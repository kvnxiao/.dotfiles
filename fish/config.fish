# Set up PATH
fish_add_path -g /usr/local/bin /usr/bin ~/.local/bin ~/.cargo/bin
if string match -q 'darwin*' "$OSTYPE"
  fish_add_path -g /opt/homebrew/bin /opt/homebrew/sbin
end

if status is-interactive
  # Bootstrap fisher and fish plugins
  cached-eval fisher "gh-raw jorgebucaran/fisher main functions/fisher.fish"
  # Touching a marker file to track when plugins were last updated
  set -l _fisher_snapshot ~/.local/share/fish/fisher-plugins-snapshot
  set -l _plugins_current (cat $__fish_config_dir/fish_plugins 2>/dev/null | string collect)
  set -l _plugins_snapshot (cat $_fisher_snapshot 2>/dev/null | string collect)
  if test "$_plugins_current" != "$_plugins_snapshot"
    fisher update
    mkdir -p (dirname $_fisher_snapshot)
    printf '%s' "$_plugins_current" >$_fisher_snapshot
  end

  # Set up completions
  cached-completions fnm "fnm completions --shell fish"
  cached-completions atuin "atuin gen-completions --shell fish"

  # Set up init scripts from various tools required at prompt render time
  cached-eval fnm "fnm env --use-on-cd"
  cached-eval zoxide "zoxide init fish"
  cached-eval atuin "atuin init fish --disable-up-arrow"
  cached-eval br "broot --print-shell-function fish"

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
  set -gx ANTHROPIC_MODEL "opus[1m]"
  set -gx CLAUDE_CODE_ENABLE_TASKS true
  set -gx CLAUDE_CODE_EXPERIMENTAL_AGENT_TEAMS 1
end
