#Requires -RunAsAdministrator

# Windows Defender exclusions for MSYS2, WezTerm, shell dotfiles, and related
# processes / tools required by the shell configs.
# Prevents real-time scanning of MSYS2 binaries and config files,
# which significantly speeds up shell startup and general MSYS2 operations.
#
# Usage: Run from an elevated PowerShell prompt:
#   powershell -ExecutionPolicy Bypass -File windows-defender-exclusions.ps1

$ErrorActionPreference = "Stop"

# MSYS2 installation
$msys2Path = "C:\msys64"

# WezTerm installation
$weztermPath = "C:\Program Files\WezTerm"

# Dotfiles and shell config
$dotfilesPath = "$env:USERPROFILE\.dotfiles"
$configPath = "$env:USERPROFILE\.config"
$zshConfigPath = "$env:USERPROFILE\.zsh"
$zshrcPath = "$env:USERPROFILE\.zshrc"
$zshenvPath = "$env:USERPROFILE\.zshenv"
$zcompdumpPath = "$env:USERPROFILE\.zcompdump"
$zgenomPath = "$env:USERPROFILE\.zgenom"
$fishConfigPath = "$env:USERPROFILE\.config\fish\config.fish"
$fishVariablesPath = "$env:USERPROFILE\.config\fish\fish_variables"
$fishLocalSharePath = "$env:USERPROFILE\.local\share\fish"

$pathExclusions = @(
    $msys2Path
    $weztermPath
    $dotfilesPath
    $configPath
    $zshConfigPath
    $zgenomPath
    "$env:USERPROFILE\.cargo\bin"
    $fishLocalSharePath
)

$fileExclusions = @(
    $zshrcPath
    $zshenvPath
    $zcompdumpPath
    $fishConfigPath
    $fishVariablesPath
)

# Process exclusions (avoid scanning on every fork/exec during shell startup)
$cargoPath = "$env:USERPROFILE\.cargo\bin"
$processExclusions = @(
    # MSYS2 core
    "$msys2Path\usr\bin\zsh.exe"
    "$msys2Path\usr\bin\bash.exe"
    "$msys2Path\usr\bin\sh.exe"
    "$msys2Path\usr\bin\msys-2.0.dll"
    "$msys2Path\usr\bin\cygpath.exe"
    "$msys2Path\usr\bin\hostname.exe"
    "$msys2Path\usr\bin\locale.exe"
    "$msys2Path\usr\bin\tzset.exe"
    "$msys2Path\usr\bin\git.exe"
    "$msys2Path\mingw64\bin\git.exe"

    # WezTerm
    "$weztermPath\wezterm.exe"
    "$weztermPath\wezterm-gui.exe"
    "$weztermPath\wezterm-mux-server.exe"

    # Fish
    "$msys2Path\usr\bin\fish.exe"

    # Tools forked during shell startup (cached-eval, etc.)
    "$cargoPath\fnm.exe"
    "$cargoPath\zoxide.exe"
    "$cargoPath\atuin.exe"
    "$cargoPath\starship.exe"
    "$cargoPath\lsd.exe"
)

Write-Host "Adding Windows Defender path exclusions..." -ForegroundColor Cyan
foreach ($path in $pathExclusions) {
    if (Test-Path $path) {
        Add-MpPreference -ExclusionPath $path
        Write-Host "  + $path" -ForegroundColor Green
    } else {
        Write-Host "  ~ $path (not found, skipping)" -ForegroundColor Yellow
    }
}

Write-Host "`nAdding Windows Defender file exclusions..." -ForegroundColor Cyan
foreach ($file in $fileExclusions) {
    if (Test-Path $file) {
        Add-MpPreference -ExclusionPath $file
        Write-Host "  + $file" -ForegroundColor Green
    } else {
        Write-Host "  ~ $file (not found, skipping)" -ForegroundColor Yellow
    }
}

Write-Host "`nAdding Windows Defender process exclusions..." -ForegroundColor Cyan
foreach ($proc in $processExclusions) {
    if (Test-Path $proc) {
        Add-MpPreference -ExclusionProcess $proc
        Write-Host "  + $proc" -ForegroundColor Green
    } else {
        Write-Host "  ~ $proc (not found, skipping)" -ForegroundColor Yellow
    }
}

Write-Host "`nDone. Current Defender exclusions:" -ForegroundColor Cyan
$prefs = Get-MpPreference
Write-Host "`nPath exclusions:" -ForegroundColor White
$prefs.ExclusionPath | ForEach-Object { Write-Host "  $_" }
Write-Host "`nProcess exclusions:" -ForegroundColor White
$prefs.ExclusionProcess | ForEach-Object { Write-Host "  $_" }
