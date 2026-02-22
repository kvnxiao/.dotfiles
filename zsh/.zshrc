setopt histignorealldups sharehistory

# Use emacs keybindings even if our EDITOR is set to vi
bindkey -e

# Keep 1000 lines of history within the shell and save it to ~/.zsh_history:
HISTSIZE=1000
SAVEHIST=1000
HISTFILE=~/.zsh_history

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

# Shared configs
source "$HOME/.zsh/shared.zsh"

if [[ $OSTYPE == msys ]] || [[ $OSTYPE == cygwin ]]; then
  # Windows specific configs
  source "$HOME/.zsh/windows.zsh"
elif [[ $OSTYPE == linux-gnu ]]; then
  # Linux specific configs
  source "$HOME/.zsh/linux.zsh"
elif [[ $OSTYPE == darwin* ]]; then
  # macOS specific configs
  source "$HOME/.zsh/macos.zsh"
fi

# Cache shell init output from slow commands.
# Run `zsh-rebuild-cache` after upgrading fnm/zoxide/atuin/starship.
_cached_eval() {
  local name="$1" gen_cmd="$2"
  local cache="${HOME}/.zsh/cache/${name}.zsh"
  if [[ ! -f "$cache" ]]; then
    mkdir -p "${HOME}/.zsh/cache"
    ${(z)gen_cmd} > "$cache"
    zcompile "$cache" 2>/dev/null
  fi
  source "$cache"
}

zsh-rebuild-cache() {
  rm -rf "${HOME}/.zsh/cache"
  rm -f "${HOME}/.zsh"/*.zwc
  local f; for f in "$HOME/.zsh"/*.zsh; do zcompile "$f" 2>/dev/null; done
  echo "Cache cleared, configs compiled. Restart zsh to regenerate."
}

_cached_eval fnm "fnm env --use-on-cd"
if [[ "$CLAUDECODE" != "1" ]]; then
  _cached_eval zoxide "zoxide init zsh"
  _cached_eval atuin "atuin init zsh --disable-up-arrow"
  _cached_eval starship "starship init zsh"
  alias cd="z"
fi
