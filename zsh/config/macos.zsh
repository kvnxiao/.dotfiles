## MacOS config

# fzf completions & keybindings, cached (`source <(fzf --zsh)` forks fzf at every startup)
_cached_eval fzf "fzf --zsh"

# Google Cloud SDK PATH. Homebrew prefix is hardcoded: two `brew --prefix`
# forks cost ~30ms per startup.
if [[ -f /opt/homebrew/share/google-cloud-sdk/path.zsh.inc ]]; then
  source /opt/homebrew/share/google-cloud-sdk/path.zsh.inc
fi

# gcloud completions, lazy-loaded on first tab-complete of gcloud/gsutil/bq
if [[ -f /opt/homebrew/share/google-cloud-sdk/completion.zsh.inc ]]; then
  _gcloud_lazy_completions() {
    unfunction _gcloud_lazy_completions
    source /opt/homebrew/share/google-cloud-sdk/completion.zsh.inc
    local real=${_comps[${words[1]}]}
    [[ -n $real && $real != _gcloud_lazy_completions ]] && $real "$@"
  }
  compdef _gcloud_lazy_completions gcloud gsutil bq
fi

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
