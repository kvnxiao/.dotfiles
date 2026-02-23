## Windows config

# Set temp directory to Windows temp directory
export TEMP="$HOME/AppData/Local/Temp"
export TMP=$TEMP

# fzf autocompletions and keybindings setup
[[ $- == *i* ]] && source "$HOME/.fzf/shell/completion.zsh" 2>/dev/null
if [[ -f "$HOME/.fzf/shell/key-bindings.zsh" ]]; then
  source "$HOME/.fzf/shell/key-bindings.zsh"
fi

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

function mpv {
  mpv.exe $@
}

# Upscale image 2x using CuNNY denoise preset
function mpv-upscale-ds {
  local size_str=$(ffprobe -v error -select_streams v:0 -show_entries stream=width,height -of csv=p=0 $1)
  local wh=(${(@s:,:)size_str//[!0-9,]/})
  local w=${wh[@]:0:1}
  local h=${wh[@]:1:1}
  local w2=$(($w * 2))
  local h2=$(($h * 2))
  mkdir -p upscaled
  mpv --vo=gpu-next --gpu-api=vulkan --vf=gpu="w=${w2}:h=${h2}" $1 --glsl-shaders="~~/shaders/CuNNy-8x32-DS-Q.glsl" --image-display-duration=0 --no-hidpi-window-scale --screenshot-format=webp --sigmoid-upscaling --deband=no --dither-depth=no --screenshot-high-bit-depth=no --osc=no -o="upscaled/${1:t:r}.webp"
}

# Upscale image 2x using CuNNY NVL preset
function mpv-upscale-nvl {
  local size_str=$(ffprobe -v error -select_streams v:0 -show_entries stream=width,height -of csv=p=0 $1)
  local wh=(${(@s:,:)size_str//[!0-9,]/})
  local w=${wh[@]:0:1}
  local h=${wh[@]:1:1}
  local w2=$(($w * 2))
  local h2=$(($h * 2))
  mkdir -p upscaled
  mpv --vo=gpu-next --gpu-api=vulkan --vf=gpu="w=${w2}:h=${h2}" $1 --glsl-shaders="~~/shaders/CuNNy-8x32-NVL.glsl" --image-display-duration=0 --no-hidpi-window-scale --screenshot-format=webp --sigmoid-upscaling --deband=no --dither-depth=no --screenshot-high-bit-depth=no --osc=no -o="upscaled/${1:t:r}.webp"
}

function cbz {
  7z a -tzip ${1}.cbz *.webp -i\!details.json
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
