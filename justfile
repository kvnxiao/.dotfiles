# Dotfiles management

set windows-shell := ["pwsh", "-NoProfile", "-Command"]

# Default: deploy dotfiles
default: deploy

# Deploy dotfiles (runs install on first use, then dotter deploy)
[unix]
deploy: _ensure-installed
    dotter deploy

[windows]
deploy: _ensure-installed
    dotter deploy
    & pwsh -NoProfile -ExecutionPolicy Bypass -File setup\scoop-config.ps1

# First-time install: symlink .dotter and local.toml
[windows]
_ensure-installed:
    & pwsh -NoProfile -ExecutionPolicy Bypass -File setup\ensure-installed.ps1

[unix]
_ensure-installed:
    zsh setup/ensure-installed.zsh

# Set up ~/.zshenv with computed HOSTNAME, LANG, TZ, SHELL
[unix]
setup-zshenv:
    zsh setup/setup-zshenv.zsh

[windows]
setup-zshenv:
    C:\msys64\usr\bin\zsh.exe setup/setup-zshenv.zsh

# Apply Windows Defender exclusions (requires admin)
[windows]
defender:
    Start-Process pwsh -Verb RunAs -Wait -ArgumentList '-NoProfile', '-ExecutionPolicy', 'Bypass', '-File', "$env:USERPROFILE\.dotfiles\setup\windows-defender-exclusions.ps1"

# Full setup: deploy + platform-specific setup
[windows]
setup: deploy defender setup-zshenv

[unix]
setup: deploy setup-zshenv

# Rebuild zsh eval cache (fnm, zoxide, atuin, starship)
[unix]
rebuild-cache:
    rm -rf ~/.zsh/cache && echo "Cache cleared. Restart zsh to regenerate."

[windows]
rebuild-cache:
    C:\msys64\usr\bin\zsh.exe -c 'rm -rf ~/.zsh/cache && echo "Cache cleared. Restart zsh to regenerate."'
