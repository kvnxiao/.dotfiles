function lmserve --description 'Build images, download model artifacts, and refresh the CDI spec for the ai-net Quadlet units'
    set -l action $argv[1]
    set -l usage "Usage: lmserve build ninfer | lmserve download <profile> | lmserve cdi"

    if contains -- $action build download; and test (count $argv) -ne 2
        echo $usage >&2
        return 2
    end

    if test "$action" = cdi; and test (count $argv) -ne 1
        echo $usage >&2
        return 2
    end

    switch "$action"
        case build
            _lmserve-build $argv[2]
        case download
            _lmserve-download $argv[2]
        case cdi
            _lmserve-cdi
        case '*'
            echo $usage >&2
            return 2
    end
end

function _lmserve-build
    set -l engine $argv[1]

    if test $engine != ninfer
        echo "Unknown build target '$engine'. Available targets: ninfer" >&2
        return 2
    end

    for tool in git podman
        if not type -q $tool
            echo "$tool: not found" >&2
            return 127
        end
    end

    set -l src ~/src/ninfer
    set -l overlay ~/.config/lmserve/ninfer

    if not test -r $overlay/Containerfile
        echo "$overlay/Containerfile is not readable. Run 'patina apply --yes'." >&2
        return 1
    end

    if test -d $src/.git
        if not git -C $src diff --quiet HEAD
            echo "$src has uncommitted changes. Commit, stash, or remove them before rebuilding." >&2
            return 1
        end

        git -C $src fetch --depth 1 origin master
        or return $status

        git -C $src reset --hard FETCH_HEAD
        or return $status
    else
        git clone --depth 1 https://github.com/Neroued/ninfer.git $src
        or return $status
    end

    podman build --tag ninfer:base $src
    or return $status

    podman build --tag ninfer:local --file $overlay/Containerfile $overlay
end

function _lmserve-download
    set -l repo
    set -l file
    set -l unit

    switch $argv[1]
        case qwen3.8-nvfp4
            set repo neroued/Qwen3.8-27B-nvfp4-NInfer
            set file qwen3_8_27b_nvfp4.ninfer
            set unit ninfer-qwen3.8.container
        case '*'
            echo "Unknown profile '$argv[1]'. Available profiles: qwen3.8-nvfp4" >&2
            return 2
    end

    for tool in hf systemctl
        if not type -q $tool
            echo "$tool: not found" >&2
            return 127
        end
    end

    set -l cache ~/.cache/huggingface/hub

    set -lx HF_HUB_OFFLINE 0
    hf download $repo $file --cache-dir $cache
    or return $status

    set -l snapshot (env HF_HUB_OFFLINE=1 hf download $repo $file --cache-dir $cache --quiet)
    or return $status

    set -l blob (realpath $snapshot[-1])
    or return $status

    if not test -r $blob
        echo "$blob is not readable." >&2
        return 1
    end

    set -l dropin ~/.config/containers/systemd/$unit.d
    mkdir -p $dropin
    or return $status

    printf '[Container]\nVolume=%s:/models/artifact.ninfer:ro\n' $blob >$dropin/artifact.conf
    or return $status

    echo "$unit: bound $blob"
    systemctl --user daemon-reload
end

function _lmserve-cdi
    if not type -q nvidia-ctk
        echo "nvidia-ctk: not found" >&2
        return 127
    end

    set -l spec ~/.config/cdi/nvidia.yaml

    mkdir -p (dirname $spec)
    or return $status

    nvidia-ctk cdi generate --output=$spec
    or return $status

    echo "$spec: regenerated"
end
