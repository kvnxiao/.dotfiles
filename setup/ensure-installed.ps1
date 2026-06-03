# Check MSYS2 installation
$msys2Path = "C:\msys64"
if (-not (Test-Path $msys2Path)) {
    Write-Host "WARNING: MSYS2 is not installed at $msys2Path" -ForegroundColor Yellow
} else {
    # Check nsswitch.conf db_home setting
    $nsswitchPath = "$msys2Path\etc\nsswitch.conf"
    $expectedDbHome = "db_home: windows cygwin desc"
    if (-not (Test-Path $nsswitchPath)) {
        Write-Host "WARNING: $nsswitchPath not found" -ForegroundColor Yellow
    } else {
        $dbHomeLine = Get-Content $nsswitchPath | Where-Object { $_ -match '^\s*db_home:' }
        if ($dbHomeLine -and ($dbHomeLine.Trim() -eq $expectedDbHome)) {
            Write-Host "MSYS2 nsswitch.conf db_home is correctly set." -ForegroundColor Green
        } else {
            Write-Host "MSYS2 nsswitch.conf db_home is not set to 'windows cygwin desc'." -ForegroundColor Yellow
            if ($dbHomeLine) {
                Write-Host "  Current value: $($dbHomeLine.Trim())" -ForegroundColor Yellow
            } else {
                Write-Host "  db_home entry not found in nsswitch.conf" -ForegroundColor Yellow
            }
            $response = Read-Host "Set db_home to 'windows cygwin desc'? (y/n)"
            if ($response -eq 'y') {
                $content = Get-Content $nsswitchPath
                if ($dbHomeLine) {
                    $content = $content | ForEach-Object {
                        if ($_ -match '^\s*db_home:') { $expectedDbHome } else { $_ }
                    }
                } else {
                    $content += $expectedDbHome
                }
                Set-Content -Path $nsswitchPath -Value $content
                Write-Host "Updated db_home in $nsswitchPath" -ForegroundColor Green
            }
        }
    }
}
