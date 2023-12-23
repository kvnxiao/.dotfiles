## Windows config

export TEMP="$HOME/AppData/Local/Temp"

# fzf autocompletions and keybindings setup
[[ $- == *i* ]] && source "$HOME/.fzf/shell/completion.zsh" 2>/dev/null
source "$HOME/.fzf/shell/key-bindings.zsh"

function open {
  # Replace MSYS-style unix path with Windows path
  explorer.exe "$(cygpath -w $1)"
}

# Allow passing asterisk as raw string to winget and scoop
alias winget="noglob winget"
alias scoop="noglob scoop"

# Replace MSYS-style unix path with Windows path using forward slashes
function pwd {
  cygpath -w "$PWD" | sed 's/\\/\//g'
}

function unzipjis {
  7z.exe x $1 -mcp=932
}

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
