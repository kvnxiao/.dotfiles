function _cached_eval_replace_line --description "Replace whole lines matching a glob in a cache file"
  # Usage: _cached_eval_replace_line <file> <glob-pattern> <replacement-line>
  # Shared by _cached_eval_post_* hooks; runs only at cache-generation time.
  # Returns 1 if no line matched, so hooks can warn about upstream drift.
  set -l file $argv[1]
  set -l pattern $argv[2]
  set -l replacement $argv[3]
  set -l matched 1
  set -l lines
  while read -l line
    if string match -q -- $pattern $line
      set -a lines $replacement
      set matched 0
    else
      set -a lines $line
    end
  end <"$file"
  printf '%s\n' $lines >"$file"
  return $matched
end
