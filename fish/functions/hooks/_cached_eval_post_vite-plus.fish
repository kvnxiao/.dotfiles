function _cached_eval_post_vite-plus --description "Post-process Vite+ env cache"
  set -l file $argv[1]

  # Materialize the completion registration at cache time: the upstream line
  # spawns vp at every shell startup (~70ms under MSYS2). Invoked by explicit
  # path because the cache (which sets up PATH) has not been sourced yet.
  set -l reg (VP_COMPLETE=fish "$HOME/.vite-plus/bin/vp" | string collect)
  if test -z "$reg"
    echo "_cached_eval_post_vite-plus: vp produced no completion output; leaving env.fish unmodified" >&2
    return
  end
  _cached_eval_replace_line $file 'VP_COMPLETE=fish command vp | source' $reg
  or echo "_cached_eval_post_vite-plus: completion line not found; env.fish may have changed upstream" >&2
end
