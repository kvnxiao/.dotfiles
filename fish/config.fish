if status is-interactive
  cached_eval fnm "fnm env --use-on-cd"
  cached_eval zoxide "zoxide init fish"
  cached_eval atuin "atuin init fish --disable-up-arrow"
  cached_eval starship "starship init fish --print-full-init"
end
