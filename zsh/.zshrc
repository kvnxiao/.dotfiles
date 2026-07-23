setopt histignorealldups sharehistory

# Use emacs keybindings even if our EDITOR is set to vi
bindkey -e

# Keep 1000 lines of history within the shell and save it to ~/.zsh_history:
HISTSIZE=1000
SAVEHIST=1000
HISTFILE=~/.zsh_history

# Cached tool-generated completions dir; must be on fpath before compinit
# runs inside the zim completion module (see cached-completions)
fpath=("$HOME/.zsh/completions" $fpath)

# --- zimfw ---
ZIM_HOME=${ZDOTDIR:-${HOME}}/.zim
zstyle ':zim:zmodule' use 'degit'
if [[ ! -e ${ZIM_HOME}/zimfw.zsh ]]; then
  curl -fsSL --create-dirs -o ${ZIM_HOME}/zimfw.zsh \
    https://github.com/zimfw/zimfw/releases/latest/download/zimfw.zsh
fi
if [[ ! ${ZIM_HOME}/init.zsh -nt ${ZIM_CONFIG_FILE:-${ZDOTDIR:-${HOME}}/.zimrc} ]]; then
  source ${ZIM_HOME}/zimfw.zsh init -q
fi
# Debian/Ubuntu's /etc/zsh/zshrc runs a global compinit before ~/.zshrc, which
# makes zim's completion module warn and re-init. Clear the flag it checks so it
# initializes cleanly; no-op where no global compinit ran (macOS, MSYS2).
unset _comps
source ${ZIM_HOME}/init.zsh

# Completion styles
zstyle ':completion:*' auto-description 'specify: %d'
zstyle ':completion:*' completer _expand _complete _correct _approximate
zstyle ':completion:*' format 'Completing %d'
zstyle ':completion:*' group-name ''
zstyle ':completion:*' menu select=2
zstyle ':completion:*:default' list-colors ${(s.:.)LS_COLORS}
zstyle ':completion:*' list-prompt %SAt %p: Hit TAB for more, or the character to insert%s
zstyle ':completion:*' matcher-list '' 'm:{a-z}={A-Z}' 'm:{a-zA-Z}={A-Za-z}' 'r:|[._-]=* r:|=* l:|=*'
zstyle ':completion:*' menu select=long
zstyle ':completion:*' select-prompt %SScrolling active: current selection at %p%s
zstyle ':completion:*' use-compctl false
zstyle ':completion:*' verbose true
zstyle ':completion:*:*:kill:*:processes' list-colors '=(#b) #([0-9]#)*=0=01;31'
zstyle ':completion:*:kill:*' command 'ps -u $USER -o pid,%cpu,tty,cputime,cmd'
# disable sort when completing `git checkout`
zstyle ':completion:*:git-checkout:*' sort false
# set descriptions format to enable group support
zstyle ':completion:*:descriptions' format '[%d]'
# set list-colors to enable filename colorizing
zstyle ':completion:*' list-colors ${(s.:.)LS_COLORS}
# preview directory's content with lsd when completing cd
zstyle ':fzf-tab:complete:cd:*' fzf-preview 'lsd -1 --color=always $realpath'
# switch group using `,` and `.`
zstyle ':fzf-tab:*' switch-group '<' '>'

# Cache helpers (must load before configs that call _cached_eval)
source "$HOME/.zsh/cache.zsh"

# Shared configs
source "$HOME/.zsh/shared.zsh"

# Platform-specific config, selected at deploy time by patina
source "$HOME/.zsh/os.zsh"

# Cached tool-generated completions
cached-completions fnm "fnm completions --shell zsh"
cached-completions atuin "atuin gen-completions --shell zsh"

_cached_eval fnm "fnm env --use-on-cd"
if [[ "$CLAUDECODE" != "1" ]]; then
  _cached_eval zoxide "zoxide init zsh"
  _cached_eval atuin "atuin init zsh --disable-up-arrow"
  _cached_eval starship "starship init zsh"
  alias cd="z"
fi

# Auto-compile configs when stale so the next shell loads .zwc files
() {
  local f
  for f in ~/.zshrc "$HOME"/.zsh/*.zsh(N) "$HOME"/.zim/init.zsh(N); do
    if [[ ! "${f}.zwc" -nt "$f" ]]; then
      zcompile "$f" 2>/dev/null
    fi
  done
  return 0
}
