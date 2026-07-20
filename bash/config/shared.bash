## Shared environment, loaded before platform-specific config.
## Mirrors zsh/config/shared.zsh, minus interactive-only pieces.

# pnpm
export PNPM_HOME="${HOME}/.pnpm"
case ":$PATH:" in
  *":$PNPM_HOME:"*) ;;
  *) export PATH="$PNPM_HOME:$PATH" ;;
esac

# ~/.local/bin
if [ -d "$HOME/.local/bin" ]; then
  case ":$PATH:" in
    *":$HOME/.local/bin:"*) ;;
    *) export PATH="$HOME/.local/bin:$PATH" ;;
  esac
fi

# Flutter version management
export FVM_CACHE_PATH="$HOME/.fvm"
case ":$PATH:" in
  *":$HOME/.fvm/default/bin:"*) ;;
  *) export PATH="$PATH:$HOME/.fvm/default/bin" ;;
esac

export XDG_CONFIG_HOME="$HOME/.config"
