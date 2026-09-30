# Set up PATH
set -gx VISUAL nvim
set -gx PNPM_HOME "$HOME/.pnpm"
# Mirror fish_add_path -g in one assignment: each fish_user_paths change
# rebuilds PATH.
set -l _paths $PNPM_HOME/bin
string match -q macos "$FISH_OS"; and set _paths /opt/homebrew/bin /opt/homebrew/sbin $PNPM_HOME
set -a _paths /usr/local/bin /usr/bin ~/.local/bin ~/.cargo/bin
set -l _new_paths
for p in (path normalize -- $_paths | path filter -d)
  contains -- $p $fish_user_paths; or set -a _new_paths $p
end
set -q _new_paths[1]; and set -g fish_user_paths $_new_paths $fish_user_paths

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

  # Set up init scripts from various tools required at prompt render time
  cached-eval fnm "fnm env --use-on-cd"
  cached-eval zoxide "zoxide init fish"
  cached-eval br "broot --print-shell-function fish"

  cached-eval starship "starship init fish --print-full-init"
  function fish_right_prompt
  end

  # Aliases as plain functions: each `alias` call costs 1-3ms under MSYS2
  function ls --wraps='lsd -a' --description 'alias ls=lsd -a'; lsd -a $argv; end
  function vi --wraps=nvim --description 'alias vi=nvim'; nvim $argv; end
  function vim --wraps=nvim --description 'alias vim=nvim'; nvim $argv; end
  function cd --wraps=z --description 'alias cd=z'; z $argv; end
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
end
