## Shared config is loaded after platform specific configs

# Aliases
alias ls="lsd -a"
alias vi="nvim"
alias vim="nvim"

# Abbreviations
abbr --quiet -S gaa="git add ."
abbr --quiet -S gst="git status"
abbr --quiet -S gsm="git switch main"
abbr --quiet -S gpu="git push"
abbr --quiet -S gpuo="git push -u origin \"\$(git branch --show-current)\""
abbr --quiet -S gpuf="git push -f"
abbr --quiet -S gcm="git commit -m"
abbr --quiet -S gcam="git commit --amend --no-edit"
abbr --quiet -S gcmnf="git commit --no-verify -m"
abbr --quiet -S gsmp="git switch main && git pull"
abbr --quiet -S gpl="git pull"
abbr --quiet -S gsn="git switch -c"
abbr --quiet -S gsw="git switch"

export FZF_DEFAULT_OPTS=" \
--color=bg+:#313244,bg:#1e1e2e,spinner:#f5e0dc,hl:#f38ba8 \
--color=fg:#cdd6f4,header:#f38ba8,info:#cba6f7,pointer:#f5e0dc \
--color=marker:#f5e0dc,fg+:#cdd6f4,prompt:#cba6f7,hl+:#f38ba8"

eval "$(zoxide init zsh)"
eval "$(fnm env --use-on-cd)"
eval "$(starship init zsh)"
