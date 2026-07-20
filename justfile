# Dotfiles management

set windows-shell := ["pwsh", "-NoProfile", "-Command"]

# Default: deploy dotfiles
default: deploy

# Deploy dotfiles via patina
[unix]
deploy:
    patina apply

# Deploy dotfiles via patina (also patches scoop config)
[windows]
deploy: _ensure-installed
    patina apply
    & pwsh -NoProfile -ExecutionPolicy Bypass -File setup\scoop-config.ps1

# Windows pre-deploy environment check (MSYS2 nsswitch.conf)
[windows]
_ensure-installed:
    & pwsh -NoProfile -ExecutionPolicy Bypass -File setup\ensure-installed.ps1

# Set up ~/.zshenv with computed HOSTNAME, LANG, TZ, SHELL (MSYS2 only)
[windows]
setup-msys2-zsh:
    C:\msys64\usr\bin\zsh.exe setup/setup-msys2-zsh.zsh

# Set up ~/.config/fish/conf.d/_local-env.fish with computed HOSTNAME, LANG, TZ, SHELL (MSYS2 only)
[windows]
setup-msys2-fish:
    C:\msys64\usr\bin\fish.exe setup/setup-msys2-fish.fish

# Apply Windows Defender exclusions (requires admin)
[windows]
defender-exclusions:
    Start-Process pwsh -Verb RunAs -Wait -ArgumentList '-NoProfile', '-ExecutionPolicy', 'Bypass', '-File', "$env:USERPROFILE\.dotfiles\setup\windows-defender-exclusions.ps1"

# Wire repo-tracked git hooks into local .git/config (idempotent)
setup-hooks:
    git config --local --replace-all include.path ../.githooks/config '^\.\./\.githooks/config$'

# Full setup: deploy + platform-specific setup
[windows]
setup: deploy defender-exclusions setup-msys2-zsh setup-msys2-fish setup-hooks

# Full setup: deploy + platform-specific setup
[unix]
setup: deploy setup-hooks
