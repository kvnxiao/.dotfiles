function __editor_delete
    if set -q __fish_selection_active
        set -e __fish_selection_active
        commandline -f kill-selection end-selection
    else
        commandline -f delete-char
    end
end
