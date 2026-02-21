if (-not (Test-Path "$env:USERPROFILE\.dotter")) {
    Write-Host "First-time install detected, running install.ps1..." -ForegroundColor Cyan
    & pwsh -NoProfile -ExecutionPolicy Bypass -File "$PSScriptRoot\install.ps1"
    Write-Host "Applying Windows Defender exclusions (requires admin)..." -ForegroundColor Cyan
    Start-Process pwsh -Verb RunAs -Wait -ArgumentList '-NoProfile', '-ExecutionPolicy', 'Bypass', '-File', "$PSScriptRoot\windows-defender-exclusions.ps1"
}
