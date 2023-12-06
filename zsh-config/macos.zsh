## MacOS config

# Install fzf via homebrew and run the install command for completions & keybindings
source "$HOME/.fzf.zsh"

# Flutter version management
export FVM_HOME="$HOME/.fvm"
export PATH="$PATH:$HOME/.fvm/default/bin"

# The next line updates PATH for the Google Cloud SDK.
if [ -f "$HOME/src/google-cloud-sdk/path.zsh.inc" ]; then . "$HOME/src/google-cloud-sdk/path.zsh.inc"; fi

# The next line enables shell command completion for gcloud.
if [ -f "$HOME/src/google-cloud-sdk/completion.zsh.inc" ]; then . "$HOME/src/google-cloud-sdk/completion.zsh.inc"; fi

# Keybinds (macOS -- wezterm)
bindkey '^[[A' history-substring-search-up   # UP
bindkey '^[[B' history-substring-search-down # DOWN
bindkey '^[[1;3D' backward-word              # CTRL+LEFT
bindkey '^[[1;3C' forward-word               # CTRL+RIGHT
bindkey '^[[3;3~' kill-word                  # CTRL+DELETE
bindkey '^[[H' beginning-of-line             # HOME
bindkey '^[[F' end-of-line                   # END
bindkey '^[[3~' delete-char                  # DELETE
