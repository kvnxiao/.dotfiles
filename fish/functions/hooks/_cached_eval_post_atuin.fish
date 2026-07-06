function _cached_eval_post_atuin --description "Post-process atuin init cache"
  set -l file $argv[1]

  # Remove eager ATUIN_SESSION init block (session is deferred to first use
  # via the lazy wrappers appended below)
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

  # Rename the upstream handlers to *_inner and append lazy wrappers that
  # create the atuin session on first use instead of at startup (previously
  # done with two `functions -c` copies in config.fish, ~3ms per shell)
  if not string match -q 'function _atuin_preexec --on-event fish_preexec' -- $lines
     or not string match -q 'function _atuin_search' -- $lines
    echo "_cached_eval_post_atuin: expected atuin function definitions not found; lazy session wrappers not installed" >&2
    return
  end
  _cached_eval_replace_line $file 'function _atuin_preexec --on-event fish_preexec' 'function _atuin_preexec_inner'
  _cached_eval_replace_line $file 'function _atuin_search' 'function _atuin_search_inner'
  printf '%s\n' \
    'function _atuin_preexec --on-event fish_preexec' \
    '    _atuin_ensure_session' \
    '    _atuin_preexec_inner $argv' \
    'end' \
    'function _atuin_search' \
    '    _atuin_ensure_session' \
    '    _atuin_search_inner $argv' \
    'end' >>"$file"
end
