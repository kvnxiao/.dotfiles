# Minimal bash config. Bash is treated as a debugging shell for running .sh
# scripts, so most interactive frills (completions, keybindings, history
# plugins, abbreviations) live in the zsh/fish setups instead. This carries the
# environment (PATH, env vars) needed to run things consistently across macOS,
# Linux, and MSYS2 Windows, plus a starship prompt and zoxide for interactive
# shells.

# Shared environment
[ -f "$HOME/.bash/shared.bash" ] && . "$HOME/.bash/shared.bash"

# Platform-specific environment, selected at deploy time by patina
[ -f "$HOME/.bash/os.bash" ] && . "$HOME/.bash/os.bash"

# Interactive-only init: prompt and directory jumping. Skipped for
# non-interactive shells (running .sh scripts) and inside Claude Code, matching
# the zsh/fish setups.
case $- in
  *i*)
    if [ "$CLAUDECODE" != "1" ]; then
      if command -v starship >/dev/null 2>&1; then
        # MSYS2 emits a Windows-style starship path (e.g. C:\...\starship.exe)
        # the shell cannot exec; rewrite it to a bare `starship`. Same fix as
        # zsh/config/cache.zsh's _cached_eval_post_starship.
        eval "$(starship init bash --print-full-init | sed -E "s@'?([A-Za-z]:)?[A-Za-z0-9_./\\\\ :-]*[/\\\\]starship(\.exe)?'?@starship@g")"
      fi
      # zoxide defines `z`/`zi`; `cd` is left as the builtin on purpose.
      command -v zoxide >/dev/null 2>&1 && eval "$(zoxide init bash)"
    fi
    ;;
esac
