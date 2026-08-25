$script:CacheHooks = Join-Path $PSScriptRoot 'cache-hooks.ps1'

<#
.SYNOPSIS
    Cache a tool's shell-init output and return the cache path to dot-source.
.DESCRIPTION
    A failed generator or an unusable cache writes a warning and returns
    nothing; the caller's array omits the broken tool.
#>
function cached-eval {
    param(
        [Parameter(Position = 0)][string]$Name,
        [Parameter(Position = 1)][string]$Command,
        [switch]$Clear
    )

    $cacheDir = Join-Path $HOME '.local\share\powershell\eval-cache'

    if ($Clear) {
        Remove-Item -LiteralPath $cacheDir -Recurse -Force -ErrorAction Ignore
        Write-Host 'Eval cache cleared. Restart pwsh to regenerate.'
        return
    }
    if ($Name -like '--*') {
        Write-Warning "cached-eval: unknown flag '$Name' (did you mean -Clear?)"
        return
    }

    $cache = Join-Path $cacheDir "$Name.ps1"
    if (Test-Path -LiteralPath $cache -PathType Leaf) {
        return $cache
    }

    # Hooks load on a miss only, and a missing or broken cache-hooks.ps1 costs
    # one unprocessed cache instead of every tool's.
    try {
        . $script:CacheHooks
    } catch {
        Write-Warning "cached-eval: hooks unavailable ($_); caching '$Name' unprocessed"
    }

    $temp = $null
    $committed = $false
    $previousEncoding = [Console]::OutputEncoding
    try {
        # Generators emit UTF-8; the Windows console default is the OEM code page.
        [Console]::OutputEncoding = [System.Text.Encoding]::UTF8
        $global:LASTEXITCODE = 0
        $lines = Invoke-Expression $Command
        if ($LASTEXITCODE -ne 0) {
            Write-Warning "cached-eval: generator for '$Name' exited $LASTEXITCODE; not caching"
            return
        }
        if (-not $lines) {
            Write-Warning "cached-eval: generator for '$Name' produced nothing; not caching"
            return
        }

        New-Item -ItemType Directory -Force -Path $cacheDir | Out-Null
        # A concurrent shell racing on the same miss must never dot-source a
        # partial file.
        $temp = "$cache.$PID"
        Set-Content -LiteralPath $temp -Value (($lines -join "`n") + "`n") -NoNewline -Encoding utf8NoBOM

        $hook = "_cached_eval_post_$Name"
        if (Test-Path -LiteralPath "Function:\$hook") {
            & $hook $temp | Out-Null
        }

        $parseErrors = $null
        [System.Management.Automation.Language.Parser]::ParseFile($temp, [ref]$null, [ref]$parseErrors) | Out-Null
        if ($parseErrors) {
            Write-Warning "cached-eval: cache for '$Name' failed its syntax check; not caching"
            return
        }
        # File.Move replaces the destination in one step. Move-Item -Force
        # deletes it first, so the cache is missing until the move completes.
        [System.IO.File]::Move($temp, $cache, $true)
        $committed = $true
        return $cache
    } catch {
        Write-Warning "cached-eval: caching '$Name' failed: $_"
        return
    } finally {
        [Console]::OutputEncoding = $previousEncoding
        if ($temp -and -not $committed) {
            Remove-Item -LiteralPath $temp -Force -ErrorAction Ignore
        }
    }
}

function clear-cache {
    cached-eval -Clear
}
