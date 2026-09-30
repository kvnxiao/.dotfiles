set -g FISH_OS windows
set -g OSTYPE cygwin
set -gx TMPDIR "$TEMP"
# This assumes that llama.cpp is installed via winget and that the D:\ drive exists
set -gx LLAMA_CACHE "D:/llama.cpp/cache/llama.exe"
