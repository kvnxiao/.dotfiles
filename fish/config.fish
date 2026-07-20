# Set up PATH
set -gx PNPM_HOME "$HOME/.pnpm"
fish_add_path -g /usr/local/bin /usr/bin ~/.local/bin ~/.cargo/bin
if string match -q 'macos' "$FISH_OS"
  fish_add_path -g /opt/homebrew/bin /opt/homebrew/sbin $PNPM_HOME
else if string match -q 'linux' "$FISH_OS"
  fish_add_path -g $PNPM_HOME
else if string match -q 'windows' "$FISH_OS"
  fish_add_path -g $PNPM_HOME/bin
end

# Vite+ (https://viteplus.dev): source a cached copy of env.fish — sourcing
# the vendor file directly spawns vp at every startup (~70ms under MSYS2).
# Must run after PATH setup above: cache regeneration needs cat/mkdir/fish,
# which are not on PATH during conf.d under MSYS2.
# After a Vite+ update, refresh with: cached-eval --clear
if test -f "$HOME/.vite-plus/env.fish"
  cached-eval vite-plus "cat $HOME/.vite-plus/env.fish"
end

if status is-interactive
  # Bootstrap fisher and fish plugins
  cached-eval fisher "gh-raw jorgebucaran/fisher main functions/fisher.fish"
  # Touching a marker file to track when plugins were last updated
  set -l _fisher_snapshot ~/.local/share/fish/fisher-plugins-snapshot
  set -l _dotfiles_dir (path resolve (status filename) | path dirname)
  set -l _plugins_current (string collect < $_dotfiles_dir/fish_plugins 2>/dev/null)
  set -l _plugins_snapshot (string collect < $_fisher_snapshot 2>/dev/null)
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
  command -q zoxide; and alias cd="z"
  # Lazy atuin session wrappers are baked into the cache by _cached_eval_post_atuin
  cached-eval atuin "atuin init fish --disable-up-arrow"
  cached-eval br "broot --print-shell-function fish"

  cached-eval starship "starship init fish --print-full-init"

  # Aliases
  alias ls="lsd -a"
  alias vi="nvim"
  alias vim="nvim"
  if test "$FISH_OS" = windows
    # Defer the powersession PATH scan (~7ms under MSYS2) to first call
    function asciinema --wraps powersession
      if command -q powersession
        powersession $argv
      else
        command asciinema $argv
      end
    end
  end

  # Claude Code environment variables
  set -gx XDG_CONFIG_HOME "$HOME/.config"
  set -gx ENABLE_LSP_TOOL 1
  set -gx ENABLE_EXPERIMENTAL_MCP_CLI true
  set -gx ANTHROPIC_MODEL "opus[1m]"
  set -gx CLAUDE_CODE_ENABLE_TASKS true
  set -gx CLAUDE_CODE_EXPERIMENTAL_AGENT_TEAMS 1
  # Don't set global CLAUDE_CODE_EFFORT_LEVEL, instead provide aliases for different effort levels
  alias cllow='claude --effort="low"'
  alias clmed='claude --effort="medium"'
  alias cl='claude --effort="xhigh"'
  alias clf='claude --model="fable" --effort="xhigh"'
  alias clmax='claude --effort="max"'
end
