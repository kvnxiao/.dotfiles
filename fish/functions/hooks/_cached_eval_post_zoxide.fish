function _cached_eval_post_zoxide --description "Post-process zoxide init cache"
  set -l file $argv[1]

  # Define z and zi directly: each `alias` call costs 1-3ms under MSYS2.
  for name in z zi
    _cached_eval_replace_line $file "alias $name=__zoxide_$name" \
      "function $name --wraps=__zoxide_$name --description 'alias $name=__zoxide_$name'; __zoxide_$name \$argv; end"
    or echo "_cached_eval_post_zoxide: 'alias $name=__zoxide_$name' not found; zoxide init may have changed upstream" >&2
  end
end
