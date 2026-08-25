function _fnm_reserve --description "Reserve this shell's fnm link and put it on PATH"
  # Called from the generated fnm cache with prefixes that already end in a path
  # separator, and a suffix that begins with one or is empty. The reserved link
  # does not exist until the first `fnm use`; until then node resolves through
  # the default alias behind it. A cache generated before link_suffix existed
  # passes three arguments, so link_suffix stays last.
  #
  # A command substitution costs ~4-5ms in an interactive MSYS2 shell and the
  # `set -l x (...)` form measured far worse, so `random` pipes the id into
  # `read` and both paths are built by interpolation. Do not rewrite this as
  # `(random ...)` or `(string replace ...)`.
  set -l msys_prefix $argv[1]
  set -l win_prefix $argv[2]
  set -l default_alias $argv[3]
  set -l link_suffix $argv[4]

  random 100000000 999999999 | read -l rand
  set -l name "$fish_pid"_"$rand"
  set -gx FNM_MULTISHELL_PATH "$win_prefix$name"
  set -gx PATH "$msys_prefix$name$link_suffix" $default_alias $PATH
end
