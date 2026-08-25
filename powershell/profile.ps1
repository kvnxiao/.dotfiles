. "$HOME\.config\powershell\cache.ps1"

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

$env:FZF_DEFAULT_OPTS="--color=bg+:#363a4f,bg:#24273a,spinner:#f4dbd6,hl:#ed8796,fg:#cad3f5,header:#ed8796,info:#c6a0f6,pointer:#f4dbd6,marker:#f4dbd6,fg+:#cad3f5,prompt:#c6a0f6,hl+:#ed8796"
# Importing PSFzf costs ~180ms.
Set-PSReadLineKeyHandler -Chord 'Ctrl+u' -BriefDescription 'Import PSFzf, then run its file provider' -ScriptBlock {
    Import-Module PSFzf
    Set-PSReadLineKeyHandler -Chord 'Ctrl+u' -BriefDescription 'PSFzf file provider' -ScriptBlock {
        Invoke-FzfPsReadlineHandlerProvider
    }
    Invoke-FzfPsReadlineHandlerProvider
}

# Claude Code
$env:ENABLE_LSP_TOOL=1
$env:ENABLE_EXPERIMENTAL_MCP_CLI="true"
$env:ANTHROPIC_MODEL="opus[1m]"
$env:CLAUDE_CODE_ENABLE_TASKS="true"
$env:CLAUDE_CODE_EXPERIMENTAL_AGENT_TEAMS="1"

# Run `clear-cache` after upgrading any of these tools, or after editing
# starship.toml: the continuation prompt is baked in at cache time.
# zoxide stays last: it wraps whatever `prompt` it finds, and starship replaces
# `prompt` outright, so loading zoxide first would drop zoxide's directory
# tracking. The atuin init claims Ctrl+r, overriding any earlier binding.
$initScripts = @(
    cached-eval fnm      'fnm env --use-on-cd --shell power-shell'
    cached-eval starship 'starship init powershell --print-full-init'
    cached-eval atuin    'atuin init powershell --disable-up-arrow'
    cached-eval zoxide   'zoxide init powershell'
)
foreach ($initScript in $initScripts) {
    . $initScript
}
