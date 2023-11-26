## Windows config

# fzf autocompletions and keybindings setup
[[ $- == *i* ]] && source "$HOME/.fzf/shell/completion.zsh" 2>/dev/null
source "$HOME/.fzf/shell/key-bindings.zsh"

function open {
  # Replace MSYS-style unix path with Windows path
  explorer.exe "$(sed -r 's/\"//g; s/^\/([a-z])\//\U\1:\//; s/\//\\/g' <<<$1)"
}

function winget {
  # Note that MSYS2_ARG_CONV_EXCL="*" is required to prevent path conversion on "/C"
  cmd.exe /C winget $@
}

# Allow passing asterisk as raw string to winget and scoop
alias winget="noglob winget"
alias scoop="noglob scoop"

# Keybinds (Windows -- wezterm)
bindkey '^[[A' history-substring-search-up   # UP
bindkey '^[[B' history-substring-search-down # DOWN
bindkey '^H' backward-kill-word              # CTRL+BACKSPACE
bindkey '^[[1;5D' backward-word              # CTRL+LEFT
bindkey '^[[1;5C' forward-word               # CTRL+RIGHT
bindkey '^[[3;5~' kill-word                  # CTRL+DELETE
bindkey '^[[H' beginning-of-line             # HOME
bindkey '^[[F' end-of-line                   # END
bindkey '^[[3~' delete-char                  # DELETE
