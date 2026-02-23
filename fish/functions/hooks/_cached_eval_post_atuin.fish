function _cached_eval_post_atuin --description "Post-process atuin init cache"
  set -l file $argv[1]

  # Remove eager ATUIN_SESSION init block (deferred via function wrappers in config.fish)
  # Block is exactly:
  #   if not set -q ATUIN_SESSION; or test "$ATUIN_SHLVL" != "$SHLVL"
  #       set -gx ATUIN_SESSION (atuin uuid)
  #       set -gx ATUIN_SHLVL $SHLVL
  #   end
  set -l skip false
  set -l lines
  while read -l line
    if string match -q 'if not set -q ATUIN_SESSION*' -- $line
      set skip true
    else if test "$skip" = true; and string match -qr '^\s*end\s*$' -- $line
      set skip false
    else if test "$skip" = false
      set -a lines $line
    end
  end <"$file"
  printf '%s\n' $lines >"$file"
end
