# Aliases
alias ls="lsd -a"
alias vi="nvim"
alias vim="nvim"

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
zstyle ':completion:*' list-colors ''
zstyle ':completion:*' list-prompt %SAt %p: Hit TAB for more, or the character to insert%s
zstyle ':completion:*' matcher-list '' 'm:{a-z}={A-Z}' 'm:{a-zA-Z}={A-Za-z}' 'r:|[._-]=* r:|=* l:|=*'
zstyle ':completion:*' menu select=long
zstyle ':completion:*' select-prompt %SScrolling active: current selection at %p%s
zstyle ':completion:*' use-compctl false
zstyle ':completion:*' verbose true

zstyle ':completion:*:*:kill:*:processes' list-colors '=(#b) #([0-9]#)*=0=01;31'
zstyle ':completion:*:kill:*' command 'ps -u $USER -o pid,%cpu,tty,cputime,cmd'

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
  zgenom load olets/zsh-abbr
  zgenom load zdharma-continuum/fast-syntax-highlighting
  # save all to init script
  zgenom save
  # Compile zsh files
  zgenom compile "$HOME/.zshrc"
fi

# Abbreviations
abbr --quiet -S gaa="git add ."
abbr --quiet -S gsm="git switch master"
abbr --quiet -S gpu="git push"
abbr --quiet -S gpuo="git push -u origin $(git branch --show-current)"
abbr --quiet -S gpuf="git push -f"
abbr --quiet -S gcm="git commit -m"
abbr --quiet -S gcam="git commit --amend --no-edit"
abbr --quiet -S gcmnf="git commit --no-verify -m"
abbr --quiet -S gsmp="git switch master && git pull"
abbr --quiet -S gp="git pull"
abbr --quiet -S gsn="git switch -c"
abbr --quiet -S gsw="git switch"

# Fuzzy finder
if [[ ! -f "$HOME/.fzf.zsh" ]]; then
  git clone --depth 1 https://github.com/junegunn/fzf.git ~/.fzf
  ~/.fzf/install
fi
source "$HOME/.fzf.zsh"

eval "$(zoxide init zsh)"

# Keybinds (macOS -- wezterm)
bindkey '^[[A' history-substring-search-up      # UP
bindkey '^[[B' history-substring-search-down    # DOWN
bindkey '^[[1;3D' backward-word                 # CTRL+LEFT
bindkey '^[[1;3C' forward-word                  # CTRL+RIGHT
bindkey '^[[3;3~' kill-word                     # CTRL+DELETE
bindkey '^[[H' beginning-of-line                # HOME
bindkey '^[[F' end-of-line                      # END
bindkey '^[[3~' delete-char                     # DELETE

eval "$(fnm env --use-on-cd)"
eval "$(starship init zsh)"
