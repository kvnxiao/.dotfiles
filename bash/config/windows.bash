## Windows (MSYS2) environment.

# Point temp at the Windows temp dir, matching zsh/config/windows.zsh.
export TEMP="$HOME/AppData/Local/Temp"
export TMP="$TEMP"

# Ensure MSYS2 coreutils are on PATH (needed when launched with a stripped env).
case ":$PATH:" in
  *":/usr/bin:"*) ;;
  *) export PATH="/usr/local/bin:/usr/bin:/bin:$PATH" ;;
esac
