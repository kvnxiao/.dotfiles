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

# Time-to-interactive benchmark. `.bashrc` and `.zshrc` gate starship and
# zoxide on CLAUDECODE, so `_benchmark` blanks the variable before invoking
# hyperfine. A gated bash measures 104ms against its real 344ms. fish and
# powershell have no such gate.
[windows]
_benchmark cmd:
    $env:CLAUDECODE=$null; hyperfine "{{ cmd }}" -N -w 5 -r 20

[unix]
_benchmark cmd:
    CLAUDECODE= hyperfine "{{ cmd }}" -N -w 5 -r 20

# Benchmark bash startup [-N, 5 warmup runs, 20 repetitions]
[windows]
benchmark-bash: (_benchmark "C:/msys64/usr/bin/bash.exe -i -c 'exit 0'")

# Benchmark bash startup [-N, 5 warmup runs, 20 repetitions]
[unix]
benchmark-bash: (_benchmark "bash -i -c 'exit 0'")

# Benchmark fish startup [-N, 5 warmup runs, 20 repetitions]
benchmark-fish: (_benchmark "fish -i -c 'exit 0'")

# Benchmark zsh startup [-N, 5 warmup runs, 20 repetitions]
benchmark-zsh: (_benchmark "zsh -i -c 'exit 0'")

# Benchmark pwsh startup [-N, 5 warmup runs, 20 repetitions]
[windows]
benchmark-pwsh: (_benchmark "pwsh -Command 'exit 0'")
