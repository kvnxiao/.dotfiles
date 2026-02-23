if status is-interactive
  cached-completions fnm "fnm completions --shell fish"
  cached-completions atuin "atuin gen-completions --shell fish"
  cached-completions fzf "gh-raw junegunn/fzf v(fzf --version | string split -f1 ' ') shell/completion.fish"

  cached-eval fnm "fnm env --use-on-cd"
  cached-eval fzf-keybindings "gh-raw junegunn/fzf v(fzf --version | string split -f1 ' ') shell/key-bindings.fish"
  cached-eval zoxide "zoxide init fish"
  cached-eval atuin "atuin init fish --disable-up-arrow"

  # Wrap atuin functions with lazy session init to defer atuin uuid from startup to first use
  functions -c _atuin_preexec _atuin_preexec_inner
  functions -c _atuin_search _atuin_search_inner
  function _atuin_preexec --on-event fish_preexec
    _atuin_ensure_session
    _atuin_preexec_inner $argv
  end
  function _atuin_search
    _atuin_ensure_session
    _atuin_search_inner $argv
  end

  cached-eval starship "starship init fish --print-full-init"

  # Aliases
  alias ls="lsd -a"
  alias vi="nvim"
  alias vim="nvim"

  # Claude Code environment variables
  set -gx XDG_CONFIG_HOME "$HOME/.config"
  set -gx ENABLE_LSP_TOOL 1
  set -gx ENABLE_EXPERIMENTAL_MCP_CLI true
  set -gx ANTHROPIC_MODEL claude-opus-4-6
  set -gx CLAUDE_CODE_ENABLE_TASKS true
  set -gx CLAUDE_CODE_EXPERIMENTAL_AGENT_TEAMS 1
end
