set -g FISH_OS linux
set -g OSTYPE linux

if test -r /proc/sys/kernel/osrelease
    set -l kernel_release (string collect </proc/sys/kernel/osrelease)
    if string match --quiet '*microsoft-standard-WSL2*' $kernel_release
        set -gx GALLIUM_DRIVER d3d12
        set -gx LIBVA_DRIVER_NAME d3d12
    end
end
