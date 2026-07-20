function cached-eval --description "Cache command output and source it"
  if test "$argv[1]" = --clear
    rm -rf "$HOME/.local/share/fish/eval-cache"
    echo "Cache cleared. Restart fish to regenerate."
    return
  end
  if string match -q -- '--*' "$argv[1]"
    echo "cached-eval: unknown flag '$argv[1]' (did you mean --clear?)" >&2
    return 1
  end

  set -l name $argv[1]
  set -l cmd $argv[2]
  set -l cache_dir "$HOME/.local/share/fish/eval-cache"
  set -l cache_file "$cache_dir/$name.fish"

  if not test -f "$cache_file"
    # Buffer output and only write the cache on success — `eval $cmd > file`
    # would persist an empty file via the redirect even when $cmd fails
    set -l out (eval $cmd)
    if test $status -ne 0
      echo "cached-eval: generation command for '$name' failed; not caching" >&2
      return 1
    end
    if test (count $argv) -ge 4
      set out (string replace -a -- "$argv[3]" "$argv[4]" $out)
    end
    mkdir -p "$cache_dir"
    # Write and post-process a private temp file, then move it into place:
    # concurrent shells racing on the same cache miss must never read or
    # hook a half-processed shared file
    set -l tmp_file "$cache_file.$fish_pid"
    printf '%s\n' $out > "$tmp_file"
    # Run post-processing hook if defined: _cached_eval_post_<name>
    set -l hook "_cached_eval_post_$name"
    if functions -q $hook
      $hook "$tmp_file"
    end

    if not fish --no-execute "$tmp_file"
      echo "cached-eval: cache for '$name' failed syntax check: $cache_file" >&2
    end
    mv -f "$tmp_file" "$cache_file"
  end

  source "$cache_file"
end
