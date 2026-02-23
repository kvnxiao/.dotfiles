function cached-eval --description "Cache command output and source it"
  if test "$argv[1]" = --rebuild
    rm -rf "$HOME/.local/share/fish/eval-cache"
    echo "Cache cleared. Restart fish to regenerate."
    return
  end

  set -l name $argv[1]
  set -l cmd $argv[2]
  set -l cache_dir "$HOME/.local/share/fish/eval-cache"
  set -l cache_file "$cache_dir/$name.fish"

  if not test -f "$cache_file"
    mkdir -p "$cache_dir"
    if test (count $argv) -ge 4
      eval $cmd | string replace -a "$argv[3]" "$argv[4]" > "$cache_file"
    else
      eval $cmd > "$cache_file"
    end
    # Run post-processing hook if defined: _cached_eval_post_<name>
    set -l hook "_cached_eval_post_$name"
    if functions -q $hook
      $hook "$cache_file"
    end
  end

  source "$cache_file"
end
