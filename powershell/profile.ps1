# Aliases
Set-Alias -Name open -Value explorer.exe
Set-Alias -Name ls -Value lsd.exe
Set-Alias -Name vim -Value nvim.exe

# Function setup
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

# Setup interactive shell
fnm env --use-on-cd | Out-String | Invoke-Expression

Invoke-Expression (& {
    $hook = if ($PSVersionTable.PSVersion.Major -lt 6) { 'prompt' } else { 'pwd' }
    (zoxide init --hook $hook powershell | Out-String)
})

Invoke-Expression (&starship init powershell)
