## Linux environment.

if [ -r /proc/sys/kernel/osrelease ]; then
  case "$(< /proc/sys/kernel/osrelease)" in
    *microsoft-standard-WSL2*)
      export GALLIUM_DRIVER=d3d12
      export LIBVA_DRIVER_NAME=d3d12
      ;;
  esac
fi
