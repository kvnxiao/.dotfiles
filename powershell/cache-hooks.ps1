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

    $text = Get-Content -Raw -LiteralPath $File

    # fnm assigns a full PATH snapshot. Caching that assignment would pin PATH
    # to its value at generation time.
    if ($text -match '(?im)^\$env:PATH\s*=\s*"(?<paths>[^"]*)"$') {
        $assignment = $Matches[0]
        $multishell = ($Matches.paths -split ';')[0]
        $text = $text.Replace($assignment, '$env:PATH = "' + $multishell + ';$env:PATH"')
    } else {
        Write-Warning '_cached_eval_post_fnm: no PATH assignment found; fnm may no longer put node on PATH'
    }
    if ($text -match '(?im)^\$env:PATH\s*=\s*"[^"]*;[^"]*;') {
        throw 'a PATH snapshot survives the rewrite; caching it would freeze PATH at generation time'
    }

    Set-Content -LiteralPath $File -Value $text -NoNewline -Encoding utf8NoBOM
}
