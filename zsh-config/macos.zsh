## MacOS config

# Install fzf via homebrew and run the install command for completions & keybindings
source "$HOME/.fzf.zsh"

# The next line updates PATH for the Google Cloud SDK.
if [ -f "$(brew --prefix)/share/google-cloud-sdk/path.zsh.inc" ]; then source "$(brew --prefix)/share/google-cloud-sdk/path.zsh.inc"; fi

# The next line enables shell command completion for gcloud.
if [ -f "$(brew --prefix)/share/google-cloud-sdk/completion.zsh.inc" ]; then source "$(brew --prefix)/share/google-cloud-sdk/completion.zsh.inc"; fi

## [Completion]
## Completion scripts setup. Remove the following line to uninstall
[[ -f ~/.dart-cli-completion/zsh-config.zsh ]] && . ~/.dart-cli-completion/zsh-config.zsh || true
## [/Completion]

export PATH="~/.shorebird/bin:$PATH"

# Keybinds (macOS -- wezterm)
bindkey '^[[A' history-substring-search-up   # UP
bindkey '^[[B' history-substring-search-down # DOWN
bindkey '^[[1;3D' backward-word              # CTRL+LEFT
bindkey '^[[1;3C' forward-word               # CTRL+RIGHT
bindkey '^[[3;3~' kill-word                  # CTRL+DELETE
bindkey '^[[H' beginning-of-line             # HOME
bindkey '^[[F' end-of-line                   # END
bindkey '^[[3~' delete-char                  # DELETE
