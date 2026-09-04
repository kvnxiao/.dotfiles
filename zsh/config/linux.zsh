## Linux config

if [[ -r /proc/sys/kernel/osrelease && "$(< /proc/sys/kernel/osrelease)" == *microsoft-standard-WSL2* ]]; then
  export GALLIUM_DRIVER=d3d12
  export LIBVA_DRIVER_NAME=d3d12
fi

# Keybinds (Linux -- wezterm)
bindkey '^[[A' history-substring-search-up   # UP
bindkey '^[[B' history-substring-search-down # DOWN
bindkey '^H' backward-kill-word              # CTRL+BACKSPACE
bindkey '^[[1;5D' backward-word              # CTRL+LEFT
bindkey '^[[1;5C' forward-word               # CTRL+RIGHT
bindkey '^[[3;5~' kill-word                  # CTRL+DELETE
bindkey '^[[H' beginning-of-line             # HOME
bindkey '^[[F' end-of-line                   # END
bindkey '^[[3~' delete-char                  # DELETE
