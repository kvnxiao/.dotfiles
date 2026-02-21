# Ensures use_external_7zip is set in scoop config.
# Patches the existing config in-place so scoop's own fields (last_update, etc.) are preserved.

$configPath = "$env:USERPROFILE\.config\scoop\config.json"

if (-not (Test-Path $configPath)) {
    New-Item -ItemType Directory -Path (Split-Path $configPath) -Force | Out-Null
    '{ "use_external_7zip": true }' | Set-Content $configPath -Encoding UTF8
    Write-Host "Created scoop config with use_external_7zip=true"
    return
}

$config = Get-Content $configPath -Raw | ConvertFrom-Json

if ($config.use_external_7zip -ne $true) {
    $config | Add-Member -NotePropertyName "use_external_7zip" -NotePropertyValue $true -Force
    $config | ConvertTo-Json -Depth 10 | Set-Content $configPath -Encoding UTF8
    Write-Host "Set use_external_7zip=true in scoop config"
} else {
    Write-Host "scoop config already has use_external_7zip=true"
}
