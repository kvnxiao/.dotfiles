if status is-interactive
  cached-completions fnm "fnm completions --shell fish"
  cached-completions atuin "atuin gen-completions --shell fish"

  cached-eval fnm "fnm env --use-on-cd"
  cached-eval zoxide "zoxide init fish"
  cached-eval atuin "atuin init fish --disable-up-arrow"
  cached-eval starship "starship init fish --print-full-init"
end
