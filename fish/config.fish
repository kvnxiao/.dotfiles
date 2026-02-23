# Set up PATH
fish_add_path -g ~/.local/bin ~/.cargo/bin
if string match -q 'darwin*' "$OSTYPE"
  fish_add_path -g /opt/homebrew/bin /opt/homebrew/sbin
end

if status is-interactive
  # Bootstrap fisher and fish plugins
  cached-eval fisher "gh-raw jorgebucaran/fisher main functions/fisher.fish"
  # Touching a marker file to track when plugins were last updated
  set -l _fisher_marker ~/.local/share/fish/fisher-bootstrapped
  if not test -f $_fisher_marker; or test $__fish_config_dir/fish_plugins -nt $_fisher_marker
    fisher update
    mkdir -p (dirname $_fisher_marker)
    touch $_fisher_marker
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
  set -gx ANTHROPIC_MODEL claude-opus-4-6
  set -gx CLAUDE_CODE_ENABLE_TASKS true
  set -gx CLAUDE_CODE_EXPERIMENTAL_AGENT_TEAMS 1
end
