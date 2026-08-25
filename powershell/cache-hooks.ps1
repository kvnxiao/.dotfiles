# cached-eval post-processing hooks, applied once at cache-generation time to
# the temp file that becomes <name>.ps1. A hook that throws drops the cache.

function _cached_eval_post_starship {
    param([string]$File)

    $text = Get-Content -Raw -LiteralPath $File

    # Loading the init spawns starship again for the continuation prompt.
    $continuation = (& starship prompt --continuation) -join "`n"
    if ($continuation) {
        $call = '(?s)Set-PSReadLineOption -ContinuationPrompt \(\s*Invoke-Native[\s\S]*?"--continuation"\s*\)\s*\)'
        $literal = "Set-PSReadLineOption -ContinuationPrompt '" + $continuation.Replace("'", "''") + "'"
        $text = $text -replace $call, $literal.Replace('$', '$$')
    } else {
        Write-Warning '_cached_eval_post_starship: starship emitted no continuation prompt; the init keeps spawning it'
    }
    if ($text -match '--continuation') {
        Write-Warning '_cached_eval_post_starship: continuation call not rewritten; the init format may have changed'
    }

    # A bare name survives the binary moving between cargo, scoop, and winget.
    # CreateProcess resolves it from PATH at no measurable cost per render.
    $text = $text -replace "-Executable '[^']*starship(\.exe)?'", "-Executable 'starship'"
    if ($text -match "'[A-Za-z]:") {
        Write-Warning '_cached_eval_post_starship: an absolute path remains; the prompt breaks if starship moves'
    }

    Set-Content -LiteralPath $File -Value $text -NoNewline -Encoding utf8NoBOM
}

function _cached_eval_post_atuin {
    param([string]$File)

    # Loading the module spawns `atuin uuid` (~120ms). .NET emits the same
    # UUIDv7 simple format in-process. CreateVersion7 requires .NET 9, so
    # pwsh 7.4 and older keep the spawn.
    if (-not [Guid].GetMethod('CreateVersion7', [Type]::EmptyTypes)) {
        Write-Warning '_cached_eval_post_atuin: Guid.CreateVersion7 needs .NET 9; `atuin uuid` still spawns at startup'
        return
    }

    $spawn = '        $env:ATUIN_SESSION = atuin uuid'
    $inProcess = "        `$env:ATUIN_SESSION = [Guid]::CreateVersion7().ToString('N')"

    $text = Get-Content -Raw -LiteralPath $File
    if (-not $text.Contains($spawn)) {
        Write-Warning '_cached_eval_post_atuin: session assignment not found; `atuin uuid` still spawns at startup'
        return
    }
    Set-Content -LiteralPath $File -Value $text.Replace($spawn, $inProcess) -NoNewline -Encoding utf8NoBOM
}

function _cached_eval_post_fnm {
    param([string]$File)

    $lines = @(Get-Content -LiteralPath $File)

    # fnm assigns a full PATH snapshot whose first entry is a symlink it mints
    # per call, so a cached copy both freezes PATH at generation time and pins
    # every shell to one link: `fnm use` in one shell switches node in all of
    # them, and the entry dangles for good once that version is uninstalled.
    # Keep fnm's static assignments and reserve the link instead.
    $sep = [System.IO.Path]::PathSeparator
    $link = $null
    $dir = $null
    switch -regex ($lines) {
        '^\$env:PATH\s*=\s*"([^"]*)"$'    { $link = ($Matches[1] -split $sep)[0] }
        '^\$env:FNM_DIR\s*=\s*"([^"]*)"$' { $dir = $Matches[1] }
    }
    if (-not $link) { throw 'no PATH assignment found; fnm may no longer put node on PATH' }
    if (-not $dir) { throw 'no FNM_DIR assignment found; the default-alias entry cannot be derived' }

    $name = [System.IO.Path]::GetFileName($link)
    if (-not $name -or -not $link.EndsWith($name)) {
        throw "link name '$name' is not the tail of the PATH entry; the prefix would be mis-sliced"
    }
    $prefix = $link.Substring(0, $link.Length - $name.Length)
    $defaultAlias = [System.IO.Path]::Combine($dir, 'aliases', 'default')

    # The reserved link does not exist until the first `fnm use`; until then node
    # resolves through the default alias behind it. FNM_MULTISHELL_PATH doubles
    # as the only temporary, so the reserve lines do not leak a variable into
    # the dot-source scope. The reserved link is already an absent PATH entry, so
    # guarding the alias on Test-Path buys nothing and would load
    # Microsoft.PowerShell.Management for ~16ms of startup.
    $quote = { param([string]$s) "'" + $s.Replace("'", "''") + "'" }
    $reserve = @(
        ('$env:FNM_MULTISHELL_PATH = ' + (& $quote $prefix) + ' + $PID + "_" + [DateTimeOffset]::UtcNow.ToUnixTimeMilliseconds()')
        ('$env:PATH = $env:FNM_MULTISHELL_PATH + ' + (& $quote "$sep$defaultAlias$sep") + ' + $env:PATH')
    )

    $out = @($lines | Where-Object {
        $_ -notmatch '^\$env:(PATH|FNM_MULTISHELL_PATH)\s*='
    }) + $reserve

    if ($out | Where-Object { $_ -like "*$name*" }) {
        throw 'the minted link name survives the rewrite; every shell would share one node version'
    }

    Set-Content -LiteralPath $File -Value (($out -join "`n") + "`n") -NoNewline -Encoding utf8NoBOM
}
