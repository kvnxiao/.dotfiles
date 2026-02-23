function _cached_eval_post_atuin --description "Post-process atuin init cache"
  set -l file $argv[1]

  # Remove eager ATUIN_SESSION init (deferred via function wrappers in config.fish)
  sed -i '/^if not set -q ATUIN_SESSION/,/^end$/d' "$file"
end
