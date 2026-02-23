function cached-completions --description "Cache tool-generated fish completions"
    set -l manifest "$HOME/.local/share/fish/completions-cache.manifest"

    if test "$argv[1]" = --rebuild
        if test -f "$manifest"
            while read -l path
                rm -f "$path"
            end <"$manifest"
            rm -f "$manifest"
        end
        echo "Cached completions removed. Run your cached-completions calls to regenerate."
        return
    end

    set -l name $argv[1]
    set -l cmd $argv[2]
    set -l completions_dir "$HOME/.config/fish/completions"
    set -l completions_file "$completions_dir/$name.fish"

    if not test -f "$completions_file"
        mkdir -p "$completions_dir"
        eval $cmd >"$completions_file"

        mkdir -p (dirname "$manifest")
        if not test -f "$manifest"; or not grep -qxF "$completions_file" "$manifest"
            echo "$completions_file" >>"$manifest"
        end
    end
end
