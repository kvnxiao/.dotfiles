function vllm
    set -l action $argv[1]
    set -l model $argv[2]
    set -l usage "Usage: vllm download <model> | vllm {doctor|stop|restart|remove} <model|webui> | vllm {start|verify} <model> [--profile <name>] | vllm start webui"

    if not contains -- $action doctor download start stop restart remove verify
        echo $usage >&2
        return 2
    end

    if test -z "$model"
        echo $usage >&2
        return 2
    end

    set -l profile_override
    if test (count $argv) -gt 2
        if test (count $argv) -ne 4
            echo $usage >&2
            return 2
        end

        if test "$argv[3]" != --profile -o -z "$argv[4]"
            echo $usage >&2
            return 2
        end

        if not contains -- $action start verify
            echo "--profile is valid only with start or verify." >&2
            return 2
        end

        set profile_override $argv[4]
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

    set -l vllm_profile
    set -l vllm_image docker.io/vllm/vllm-openai:latest
    set -l vllm_config
    set -l container_config /etc/vllm/config.yaml
    set -l vllm_args
    set -l vllm_verify_log_patterns
    if contains -- $action start verify; and test $is_webui -eq 0
        set vllm_profile (_vllm-select-profile $model $profile_override)
        or return $status

        set vllm_config "$__fish_config_dir/vllm/profiles/$vllm_profile.yaml"
        if not test -r $vllm_config
            echo "$vllm_profile profile: $vllm_config is not readable." >&2
            return 1
        end

        set vllm_args $model --config $container_config
        switch $vllm_profile
            case qwen3.8
                set vllm_verify_log_patterns \
                    'Using (FLASHINFER attention backend|FLASHINFER backend\.)' \
                    'Using fp8 data type to store kv cache\.' \
                    'FlashInfer resolved query dtypes:.*kv_cache_dtype=(fp8|torch\.float8_e4m3fn)' \
                    'Using Triton/FLA GDN prefill kernel \(requested=triton,'
            case gemma4
                set vllm_verify_log_patterns \
                    'Using fp8 data type to store kv cache\.'
        end
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
        case verify
            if test $is_webui -eq 1
                echo "verify requires a model profile." >&2
                return 2
            end

            podman container exists $container
            set -l exists_status $status
            if test $exists_status -eq 1
                echo "$container: not found" >&2
                return 1
            else if test $exists_status -ne 0
                echo "$container: check failed" >&2
                return $exists_status
            end

            set -l running (podman container inspect --format '{{.State.Running}}' $container)
            or return $status
            if test "$running" != true
                echo "$container: not running" >&2
                return 1
            end
            echo "$container: running"

            set -l actual_image (podman container inspect --format '{{.ImageName}}' $container)
            or return $status
            set -l actual_image_digest (podman container inspect --format '{{.ImageDigest}}' $container)
            or return $status
            if test "$actual_image" != "$vllm_image"
                echo "$container: image differs from $vllm_image." >&2
                _vllm-print-recreate-command $model $profile_override
                return 1
            end
            echo "$container image: verified ($actual_image_digest)"

            set -l actual_arg_lines (podman container inspect --format '{{range .Config.Cmd}}{{println .}}{{end}}' $container)
            or return $status
            set -l actual_args (string join \n -- $actual_arg_lines | string collect)
            set -l expected_args (string join \n -- $vllm_args | string collect)
            if test "$actual_args" != "$expected_args"
                echo "$container: arguments differ from the $vllm_profile profile." >&2
                _vllm-print-recreate-command $model $profile_override
                return 1
            end
            echo "$container arguments: verified"

            set -l started_at (podman container inspect --format '{{.State.StartedAt}}' $container)
            or return $status
            set -l container_logs (podman logs --since $started_at $container 2>&1)
            or return $status

            for pattern in $vllm_verify_log_patterns
                if not string match --quiet --regex -- $pattern $container_logs
                    echo "$container: runtime log did not match '$pattern'." >&2
                    return 1
                end
            end
            echo "$container runtime: verified"

            if not type -q curl
                echo "curl: not found" >&2
                return 127
            end

            curl --fail --silent --show-error --max-time 5 http://127.0.0.1:8000/health >/dev/null
            or return $status
            echo "$container health: verified"
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

            podman run -d \
                --name $container \
                --network ai-net \
                --network-alias vllm \
                --device nvidia.com/gpu=all \
                --ipc=host \
                -p 8000:8000 \
                -v ~/.cache/huggingface:/root/.cache/huggingface \
                -v ~/.cache/vllm:/root/.cache/vllm \
                -v "$vllm_config:$container_config:ro" \
                -e VLLM_CACHE_ROOT=/root/.cache/vllm \
                -e HF_HUB_OFFLINE=1 \
                -e TRANSFORMERS_OFFLINE=1 \
                -e VLLM_NO_USAGE_STATS=1 \
                $vllm_image \
                $vllm_args
        case stop
            podman stop $container
        case remove
            podman rm --force $container
    end
end

function _vllm-select-profile
    set -l model $argv[1]
    set -l override $argv[2]
    set -l profiles qwen3.8 gemma4

    if test -n "$override"
        if contains -- $override $profiles
            echo $override
            return 0
        end

        echo "Unknown vLLM profile '$override'. Available profiles: "(string join ', ' $profiles) >&2
        return 2
    end

    switch (string lower -- $model)
        case '*qwen3.8*'
            echo qwen3.8
        case '*gemma-4*' '*gemma4*'
            echo gemma4
        case '*'
            echo "No vLLM profile matches '$model'. Available profiles: "(string join ', ' $profiles) >&2
            return 2
    end
end

function _vllm-print-recreate-command
    set -l model $argv[1]
    set -l profile $argv[2]

    if test -n "$profile"
        echo "Run 'vllm remove $model', then 'vllm start $model --profile $profile'." >&2
    else
        echo "Run 'vllm remove $model', then 'vllm start $model'." >&2
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
