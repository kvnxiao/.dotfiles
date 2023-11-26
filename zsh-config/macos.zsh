## MacOS config
source "$HOME/.fzf.zsh"

# Keybinds (macOS -- wezterm)
bindkey '^[[A' history-substring-search-up   # UP
bindkey '^[[B' history-substring-search-down # DOWN
bindkey '^[[1;3D' backward-word              # CTRL+LEFT
bindkey '^[[1;3C' forward-word               # CTRL+RIGHT
bindkey '^[[3;3~' kill-word                  # CTRL+DELETE
bindkey '^[[H' beginning-of-line             # HOME
bindkey '^[[F' end-of-line                   # END
bindkey '^[[3~' delete-char                  # DELETE
