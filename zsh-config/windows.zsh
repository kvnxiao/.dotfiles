## Windows config

# Set temp directory to Windows temp directory
export TEMP="$HOME/AppData/Local/Temp"
export TMP=$TEMP

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

function av1-search {
  ab-av1 crf-search --encoder av1_nvenc --preset p7 --pix-format yuv420p10le -i $1
}

# Encode video to AV1 using NVENC
function av1-encode {
  zmodload zsh/zutil
  zparseopts -D -F -K -- \
    {i,-input}:=arg_input \
    {o,-output}:=arg_output \
    {q,-quality}:=arg_cq || return 1
  if [[ -z $arg_input || -z $arg_cq ]]; then
    echo "Usage: av1-encode -i <input> -o <output> -q <cq>"
    return 1
  fi
  if [[ -z $arg_output ]]; then
    arg_output=$arg_input:r.av1.mkv
  fi
  echo ffmpeg -i $arg_input[-1] -c:v av1_nvenc -pix_fmt p010le -preset p7 -tune hq -highbitdepth true -cq:v $arg_cq[-1] -c:a libopus -b:a 128k $arg_output[-1]
  ffmpeg -i $arg_input[-1] -c:v av1_nvenc -pix_fmt p010le -preset p7 -tune hq -highbitdepth true -cq:v $arg_cq[-1] -c:a libopus -b:a 128k $arg_output[-1]
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
