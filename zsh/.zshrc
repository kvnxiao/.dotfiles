setopt histignorealldups sharehistory

# Use emacs keybindings even if our EDITOR is set to vi
bindkey -e

# Keep 1000 lines of history within the shell and save it to ~/.zsh_history:
HISTSIZE=1000
SAVEHIST=1000
HISTFILE=~/.zsh_history

# Use modern completion system
autoload -Uz compinit
compinit

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

# Load zgenom
if [[ ! -f "$HOME/.zgenom/zgenom.zsh" ]]; then
  git clone https://github.com/jandamm/zgenom.git "${HOME}/.zgenom"
fi
source "$HOME/.zgenom/zgenom.zsh"

# Check for plugin and zgenom updates every 7 days
# This does not increase the startup time.
zgenom autoupdate

if ! zgenom saved; then
  echo "Creating a zgenom save"
  zgenom load zsh-users/zsh-autosuggestions
  zgenom load zsh-users/zsh-history-substring-search
  zgenom load zsh-users/zsh-completions
  zgenom load Aloxaf/fzf-tab
  zgenom load olets/zsh-abbr
  zgenom load zdharma-continuum/fast-syntax-highlighting
  # save all to init script
  zgenom save
  # Compile zsh files
  zgenom compile "$HOME/.zshrc"
fi

# fzf fuzzy finder (shell completions and keybindings)
if [[ ! -d "$HOME/.fzf" ]]; then
  git clone --depth 1 https://github.com/junegunn/fzf.git ~/.fzf
  # Only install fzf if the command is not available
  if [[ ! -x "$(command -v fzf)" ]]; then
    ~/.fzf/install
  fi
fi

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

# Shared configs
source "$HOME/.zsh/shared.zsh"
