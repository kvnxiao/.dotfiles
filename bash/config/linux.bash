## Linux environment.

if [ -r /proc/sys/kernel/osrelease ]; then
  case "$(< /proc/sys/kernel/osrelease)" in
    *microsoft-standard-WSL2*)
      [ -f "$HOME/.bash/wsl2.bash" ] && . "$HOME/.bash/wsl2.bash"
      ;;
  esac
fi
