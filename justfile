# Dotfiles management

set windows-shell := ["pwsh", "-NoProfile", "-Command"]

# Default: deploy dotfiles
default: deploy

# Deploy dotfiles (runs install on first use, then dotter deploy)
[unix]
deploy: _ensure-installed
    dotter deploy

# Deploy dotfiles (runs install on first use, then dotter deploy)
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

# Set up ~/.zshenv with computed HOSTNAME, LANG, TZ, SHELL
[windows]
setup-zshenv:
    C:\msys64\usr\bin\zsh.exe setup/setup-zshenv.zsh

# Set up ~/.config/fish/conf.d/_local-env.fish with computed HOSTNAME, LANG, TZ, SHELL
[windows]
setup-fishenv:
    C:\msys64\usr\bin\fish.exe setup/setup-fishenv.fish

# Apply Windows Defender exclusions (requires admin)
[windows]
defender-exclusions:
    Start-Process pwsh -Verb RunAs -Wait -ArgumentList '-NoProfile', '-ExecutionPolicy', 'Bypass', '-File', "$env:USERPROFILE\.dotfiles\setup\windows-defender-exclusions.ps1"

# Wire repo-tracked git hooks into local .git/config (idempotent)
setup-hooks:
    git config --local --replace-all include.path ../.githooks/config '^\.\./\.githooks/config$'

# Full setup: deploy + platform-specific setup
[windows]
setup: deploy defender-exclusions setup-zshenv setup-fishenv setup-hooks

# Full setup: deploy + platform-specific setup
[unix]
setup: deploy setup-zshenv setup-hooks
