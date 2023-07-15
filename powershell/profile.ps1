# Aliases
Set-Alias -Name open -Value explorer.exe
Set-Alias -Name vim -Value nvim.exe
Set-Alias -Name vi -Value nvim.exe

# Function setup
function listall {
    lsd.exe -a @args
}
Set-Alias -Name ls -Value listall

function vid2mkv([Parameter(ValueFromPipeline = $true)][string]$file) {
    process {
        if (-not (Test-Path -Path $file -PathType Leaf)) {
            Write-Output "Please provide a valid video file"
            return
        }
        $output = [System.IO.Path]::ChangeExtension($file, ".mkv")
        ffmpeg.exe -i $file -vcodec copy -acodec copy $output
    }
}

function unzipjis {
    7z.exe x @args -mcp=932
}

# Git abbreviation functions
Remove-Alias -Name gcm -Force
Remove-Alias -Name gp -Force
Remove-Alias -Name gsn -Force
function gaa { git add . @args }
function gst { git status @args }
function gsm { git switch main @args }
function gpu { git push @args }
function gpuo { git push -u origin "$(git branch --show-current)" @args }
function gpuf { git push -f @args }
function gcm { git commit -m @args }
function gcam { git commit --amend --no-edit @args }
function gcmnf { git commit --no-verify -m @args }
function gsmp { git switch main && git pull @args }
function gp { git pull @args }
function gsn { git switch -c @args }
function gsw { git switch @args }

# Setup interactive shell
fnm env --use-on-cd | Out-String | Invoke-Expression

# PSFfzf
$env:FZF_DEFAULT_OPTS="--color=bg+:#363a4f,bg:#24273a,spinner:#f4dbd6,hl:#ed8796,fg:#cad3f5,header:#ed8796,info:#c6a0f6,pointer:#f4dbd6,marker:#f4dbd6,fg+:#cad3f5,prompt:#c6a0f6,hl+:#ed8796"
Set-PsFzfOption -PSReadlineChordProvider 'Ctrl+u' -PSReadlineChordReverseHistory 'Ctrl+r'

Invoke-Expression (&starship init powershell)

Import-Module 'C:\Users\kvnxiao\github\vcpkg\scripts\posh-vcpkg'

Invoke-Expression (& { (zoxide init powershell | Out-String) })
