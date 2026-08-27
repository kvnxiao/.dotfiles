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
    # skell must load before starship, which moves any PROMPT_COMMAND it finds
    # into STARSHIP_PROMPT_COMMAND and runs it with $? restored.
    [ -f "$HOME/github/skell/bash/skell.bash" ] && . "$HOME/github/skell/bash/skell.bash"
    if [ "$CLAUDECODE" != "1" ]; then
      if command -v starship >/dev/null 2>&1; then
        # MSYS2 emits a Windows-style starship path (e.g. C:\...\starship.exe)
        # the shell cannot exec; rewrite it to a bare `starship`. Same fix as
        # zsh/config/cache.zsh's _cached_eval_post_starship.
        eval "$(starship init bash --print-full-init | sed -E "s@'?([A-Za-z]:)?[A-Za-z0-9_./\\\\ :-]*[/\\\\]starship(\.exe)?'?@starship@g")"
      fi
      # zoxide defines `z`/`zi`; `cd` is left as the builtin on purpose.
      # zoxide 0.10.0's Cygwin branch emits `cygpath -w "\builtin pwd -L"`
      # without the command substitution, so every directory change feeds
      # cygpath a literal string. Capturing the command avoids a
      # literal-backslash pattern, which this sed does not match. Same fix as
      # zsh/config/cache.zsh's _cached_eval_post_zoxide.
      command -v zoxide >/dev/null 2>&1 && eval "$(zoxide init bash | sed 's|cygpath -w "\(.*\) pwd -L"|cygpath -w "$(\1 pwd -L)"|')"
    fi
    ;;
esac
