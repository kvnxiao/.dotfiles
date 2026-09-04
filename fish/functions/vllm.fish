function vllm
    set -l action $argv[1]
    set -l model $argv[2]
    set -l usage "Usage: vllm download <model> | vllm {doctor|start|stop|restart|remove} <model|webui>"

    if not contains -- $action doctor download start stop restart remove
        echo $usage >&2
        return 2
    end

    if test -z "$model"
        echo $usage >&2
        return 2
    end

    if test $action = download
        set -lx HF_HUB_OFFLINE 0

        if type -q hf
            hf download $model --cache-dir ~/.cache/huggingface/hub
        else if type -q uvx
            uvx --from huggingface-hub hf download $model --cache-dir ~/.cache/huggingface/hub
        else
            echo "download requires hf or uvx." >&2
            return 127
        end

        return $status
    end

    if not type -q podman
        echo "podman: not found" >&2
        return 1
    end

    set -l is_webui 0
    set -l container
    if test $model = webui
        set is_webui 1
        set container open-webui
    else
        set -l model_slug (string lower -- $model | string replace -ra '[^a-z0-9]+' '-' | string trim -c '-')
        if test -z "$model_slug"
            echo "Model must contain an ASCII letter or digit." >&2
            return 2
        end

        set container vllm-$model_slug
    end

    switch $action
        case doctor
            echo "podman: found"
            _vllm-ensure-network
            or return $status
            echo "ai-net network: ready"

            podman container exists $container
            set -l exists_status $status

            if test $exists_status -eq 0
                echo "$container: found"
            else if test $exists_status -eq 1
                echo "$container: not found" >&2
                return 1
            else
                echo "$container: check failed" >&2
                return $exists_status
            end
        case start restart
            _vllm-ensure-network
            or return $status

            podman container exists $container
            set -l exists_status $status
            if test $exists_status -ne 0 -a $exists_status -ne 1
                return $exists_status
            end

            if test $action = restart -a $exists_status -eq 1
                echo "$container: not found" >&2
                return 1
            end

            if test $is_webui -eq 0
                set -l running_containers (podman ps --filter 'name=^vllm-' --format '{{.Names}}')
                set -l list_status $status
                if test $list_status -ne 0
                    return $list_status
                end

                for running_container in $running_containers
                    if test $running_container != $container
                        podman stop $running_container
                        or return $status
                    end
                end
            end

            if test $action = restart
                podman restart $container
                return $status
            end

            if test $exists_status -eq 0
                podman start $container
                return $status
            end

            if test $is_webui -eq 1
                podman run -d \
                    --name open-webui \
                    --network ai-net \
                    -p 8080:8080 \
                    -v open-webui-data:/app/backend/data:U \
                    -e OPENAI_API_BASE_URL=http://vllm:8000/v1 \
                    -e OPENAI_API_KEY=sk-local \
                    -e WEBUI_AUTH=false \
                    ghcr.io/open-webui/open-webui:main
                return $status
            end

            set -l parser_args
            switch (string lower -- $model)
                case '*gemma-4*'
                    set parser_args \
                        --enable-auto-tool-choice \
                        --tool-call-parser gemma4 \
                        --reasoning-parser gemma4
                case '*qwen3.8*'
                    set parser_args \
                        --enable-auto-tool-choice \
                        --tool-call-parser hermes \
                        --reasoning-parser qwen3
            end

            podman run -d \
                --name $container \
                --network ai-net \
                --network-alias vllm \
                --device nvidia.com/gpu=all \
                --ipc=host \
                -p 8000:8000 \
                -v ~/.cache/huggingface:/root/.cache/huggingface \
                -v ~/.cache/vllm:/root/.cache/vllm \
                -e VLLM_CACHE_ROOT=/root/.cache/vllm \
                -e VLLM_WSL2_ENABLE_PIN_MEMORY=1 \
                -e HF_HUB_OFFLINE=1 \
                -e TORCH_CUDA_ARCH_LIST=12.0 \
                -e PYTORCH_CUDA_ALLOC_CONF=expandable_segments:True \
                -e VLLM_TEST_ENABLE_JIT_WARMUP=1 \
                docker.io/vllm/vllm-openai:latest \
                --model $model \
                --max-model-len 131072 \
                --max-num-seqs 2 \
                --max-num-batched-tokens 8192 \
                --enable-chunked-prefill \
                --enable-prefix-caching \
                --kv-cache-dtype fp8 \
                --gpu-memory-utilization 0.93 \
                $parser_args \
                --trust-remote-code
        case stop
            podman stop $container
        case remove
            podman rm --force $container
    end
end

function _vllm-ensure-network
    podman network exists ai-net
    set -l exists_status $status

    if test $exists_status -eq 0
        return 0
    else if test $exists_status -ne 1
        return $exists_status
    end

    podman network create ai-net
end
