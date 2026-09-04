set -g FISH_OS linux
set -g OSTYPE linux

if test -r /proc/sys/kernel/osrelease
    set -l kernel_release (string collect </proc/sys/kernel/osrelease)
    if string match --quiet '*microsoft-standard-WSL2*' $kernel_release
        test -f "$HOME/.config/fish/wsl2.fish"; and source "$HOME/.config/fish/wsl2.fish"
    end
end
