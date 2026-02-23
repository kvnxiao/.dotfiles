function _atuin_ensure_session --description "Lazily initialize ATUIN_SESSION on first use"
  if not set -q ATUIN_SESSION; or test "$ATUIN_SHLVL" != "$SHLVL"
    set -gx ATUIN_SESSION (atuin uuid)
    set -gx ATUIN_SHLVL $SHLVL
  end
end
