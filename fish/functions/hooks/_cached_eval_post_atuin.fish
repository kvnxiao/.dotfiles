function _cached_eval_post_atuin --description "Post-process atuin init cache"
  set -l file $argv[1]

  # `atuin uuid` spawns a process per shell (~115ms under MSYS2). Generate the
  # RFC 9562 v7 id from builtins instead: 48 bits of unix ms, the version
  # nibble 7, 12 random bits, the variant nibble 8-b, then 60 random bits.
  #
  # The emitted block pipes into `read` instead of assigning from a command
  # substitution: each one costs ~4-5ms in an interactive MSYS2 shell, and the
  # `set -l x (...)` form measured ~23ms slower per startup. Do not rewrite
  # these pipes as command substitutions. `set -l _ms` declares the variable
  # ahead of the branch so `read _ms` assigns that local instead of creating a
  # global. Quoting every printf argument keeps a failed read from shifting the
  # field layout and changing the id's length.
  #
  # /proc is MSYS2 and Linux only; on macOS the fallback forks `date` once at
  # second precision, where 60 random bits still keep the id unique. `btime`
  # counts whole seconds, so the derived timestamp trails `date` by a fixed
  # sub-second offset (~0.5s on this machine); v7 ids need only coarse time
  # ordering. The session id groups history rows rather than authenticating
  # them, so fish's `random` suffices.
  set -l gen (printf '%s\n' \
    '    set -l _ms' \
    '    if test -r /proc/uptime -a -r /proc/stat' \
    '        read -l _up _rest </proc/uptime' \
    '        string match -gr \'btime (\d+)\' </proc/stat | read -l _btime' \
    '        math -s0 "($_btime + $_up) * 1000" | read _ms' \
    '    else' \
    '        date +%s | read -l _sec' \
    '        set _ms $_sec"000"' \
    '    end' \
    '    random 0 4095 | read -l _ra' \
    '    random 8 11 | read -l _rv' \
    '    random 0 1152921504606846975 | read -l _rb' \
    '    printf \'%012x7%03x%x%015x\n\' "$_ms" "$_ra" "$_rv" "$_rb" | read -gx ATUIN_SESSION' \
    | string collect)

  _cached_eval_replace_line $file '*set -gx ATUIN_SESSION (atuin uuid)' $gen
  or echo "_cached_eval_post_atuin: ATUIN_SESSION assignment not found; the atuin uuid spawn remains in the cache" >&2
end
