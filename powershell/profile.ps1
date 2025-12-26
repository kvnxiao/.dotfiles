# Load abbreviations module
. "$HOME\.config\powershell\PSAbbreviations.ps1"

# Load custom commands
. "$HOME\.config\powershell\commands.ps1"

# Aliases
Set-Alias -Name open -Value explorer.exe
Set-Alias -Name vim -Value nvim.exe
Set-Alias -Name vi -Value nvim.exe

# Function setup
function listall {
    lsd.exe -a @args
}
Set-Alias -Name ls -Value listall

# Force remove some functions that clash with abbreviations below
Remove-Alias -Name gcm -Force
Remove-Alias -Name gp -Force
Remove-Alias -Name gsn -Force

# Abbreviations
abbr 'gaa=git add .'
abbr 'gst=git status'
abbr 'gsm=git switch main'
abbr 'gpu=git push'
abbr 'gpuo=git push -u origin "$(git branch --show-current)"'
abbr 'gpuf=git push -f'
abbr 'gcm=git commit -m "%"'
abbr 'gcam=git commit --amend'
abbr 'gcan=git commit --amend --no-edit'
abbr 'gcmn=git commit --no-verify -m "%"'
abbr 'gsmp=git switch main && git fetch --all && git pull'
abbr 'gpl=git pull'
abbr 'gsn=git switch -c'
abbr 'gsw=git switch'
abbr 'gpr=gh pr view --web || gh pr create --web'
abbr 'gr=gh repo view --web'
abbr 'gl=git l'
abbr 'gla=git la'

# Setup interactive shell
fnm env --use-on-cd | Out-String | Invoke-Expression

# PSFfzf
$env:FZF_DEFAULT_OPTS="--color=bg+:#363a4f,bg:#24273a,spinner:#f4dbd6,hl:#ed8796,fg:#cad3f5,header:#ed8796,info:#c6a0f6,pointer:#f4dbd6,marker:#f4dbd6,fg+:#cad3f5,prompt:#c6a0f6,hl+:#ed8796"
Set-PsFzfOption -PSReadlineChordProvider 'Ctrl+u' -PSReadlineChordReverseHistory 'Ctrl+r'

Invoke-Expression (&starship init powershell)
Invoke-Expression (& { (atuin init powershell | Out-String) })
Invoke-Expression (& { (zoxide init powershell | Out-String) })
