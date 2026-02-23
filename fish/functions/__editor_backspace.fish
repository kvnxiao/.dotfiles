function __editor_backspace
    if set -q __fish_selection_active
        set -e __fish_selection_active
        commandline -f kill-selection end-selection
    else
        commandline -f backward-delete-char
    end
end
