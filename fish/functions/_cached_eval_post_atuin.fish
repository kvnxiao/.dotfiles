function _cached_eval_post_atuin --description "Post-process atuin init cache (Windows optimizations)"
  if test "$FISH_OS" != windows
    return
  end

  set -l file $argv[1]

  # Windows: replace slow "atuin uuid" subcommand with faster "atuin-uuid" binary,
  # and defer ATUIN_SESSION init from startup to first command execution
  sed -i \
    -e 's/atuin uuid/atuin-uuid/g' \
    -e '/^if not set -q ATUIN_SESSION/,/^end$/d' \
    -e 's/^function _atuin_preexec --on-event fish_preexec$/function _atuin_ensure_session\n    if not set -q ATUIN_SESSION; or test "$ATUIN_SHLVL" != "$SHLVL"\n        set -gx ATUIN_SESSION (atuin-uuid)\n        set -gx ATUIN_SHLVL $SHLVL\n    end\nend\n\nfunction _atuin_preexec --on-event fish_preexec\n    _atuin_ensure_session/' \
    "$file"
end
