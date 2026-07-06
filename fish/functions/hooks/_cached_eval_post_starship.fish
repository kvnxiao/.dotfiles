function _cached_eval_post_starship --description "Post-process starship init cache"
  set -l file $argv[1]

  # Replace the multi-cmdsub session key generation (30-70ms in an
  # interactive startup under MSYS2/Cygwin) with a fork-free pipe.
  _cached_eval_replace_line $file 'set -gx STARSHIP_SESSION_KEY *' \
    'random 1000000000000000 9999999999999999 | read -gx STARSHIP_SESSION_KEY'

  # MSYS2: depending on the invoking environment, starship emits its own
  # binary path either as POSIX (/c/Users/...) or as a quoted Windows path
  # ('C:\Users\...\starship.exe'), which fish under MSYS2 cannot exec.
  # Convert the latter to the former. No-op when the emission is already
  # POSIX, and on macOS/Linux where the pattern cannot match.
  set -l lines
  while read -l line
    if string match -rq -- "'(?<_vol>[A-Za-z]):(?<_rest>\\\\[^']*)'" $line
      set -l unix /(string lower $_vol)(string replace -a '\\' '/' -- $_rest)
      set line (string replace -- "'$_vol:$_rest'" $unix $line)
    end
    set -a lines $line
  end <"$file"
  printf '%s\n' $lines >"$file"

  # Warn on bad post-conditions rather than on whether a rewrite happened:
  # "nothing to replace" is healthy (upstream emits either form), but these
  # patterns must never survive in a processed cache.
  if string match -q '*(random)(random)*' -- $lines
    echo "_cached_eval_post_starship: multi-cmdsub STARSHIP_SESSION_KEY generation still present (slow under MSYS2); upstream init format may have changed" >&2
  end
  if string match -rq -- "'[A-Za-z]:\\\\" $lines
    echo "_cached_eval_post_starship: quoted Windows path remains in cache; prompt may not render" >&2
  end
end
