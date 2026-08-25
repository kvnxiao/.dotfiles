function _cached_eval_post_fnm --description "Post-process fnm env cache"
  set -l file $argv[1]

  # `fnm env` mints a symlink per call and writes it into PATH as a literal, so
  # a cached copy pins every shell to one link: `fnm use` in one shell switches
  # node in all of them, and the entry dangles for good once that version is
  # uninstalled. Keep fnm's static exports and reserve the link instead.
  set -l lines
  while read -l line
    set -a lines "$line"
  end <"$file"

  set -l msys_link (string match -rg '^set -gx PATH "([^"]*)"' -- $lines)
  set -l win_link (string match -rg '^set -gx FNM_MULTISHELL_PATH "([^"]*)"' -- $lines)
  set -l win_dir (string match -rg '^set -gx FNM_DIR "([^"]*)"' -- $lines)
  if test -z "$msys_link" -o -z "$win_link" -o -z "$win_dir"
    echo "_cached_eval_post_fnm: fnm env output shape changed; caching it would pin one symlink across every shell" >&2
    return 1
  end

  # fnm's fish dialect formats paths through Rust's {:?}, which doubles every
  # backslash.
  set win_link (string replace -a '\\\\' '\\' -- $win_link)
  set win_dir (string replace -a '\\\\' '\\' -- $win_dir)
  set -l name (string replace -r '^.*[/\\\\]' '' -- $win_link)
  set -l win_prefix (string replace -r '[^/\\\\]*$' '' -- $win_link)
  if test -z "$name" -o -z "$win_prefix"
    echo "_cached_eval_post_fnm: FNM_MULTISHELL_PATH '$win_link' does not split into a prefix and a link name; not caching" >&2
    return 1
  end
  # fnm puts node in <link>/bin on Unix and node.exe in <link> on Windows.
  set -l parts (string split -r -m1 -- $name $msys_link)
  if test (count $parts) -ne 2
    echo "_cached_eval_post_fnm: PATH entry '$msys_link' does not contain link name '$name'; not caching" >&2
    return 1
  end
  set -l msys_prefix $parts[1]
  set -l link_suffix $parts[2]
  if not string match -q '*/' -- $msys_prefix
    echo "_cached_eval_post_fnm: PATH entry '$msys_link' is not a POSIX path; not caching" >&2
    return 1
  end

  set -l native_dir $win_dir
  if string match -qr '^([A-Za-z]:|\\\\\\\\)' -- $win_dir
    set native_dir (cygpath -u "$win_dir")
    or begin
      echo "_cached_eval_post_fnm: could not convert FNM_DIR '$win_dir' to a native path; not caching" >&2
      return 1
    end
  end
  set -l default_alias (string replace -r '/$' '' -- $native_dir)/aliases/default$link_suffix

  set -l out
  for line in $lines
    string match -q 'set -gx PATH *' -- $line; and continue
    string match -q 'set -gx FNM_MULTISHELL_PATH *' -- $line; and continue
    set -a out "$line"
  end
  set -l args (string escape -- $msys_prefix $win_prefix $default_alias $link_suffix)
  set -a out "_fnm_reserve $args"

  if string match -q -- "*$name*" $out
    echo "_cached_eval_post_fnm: the minted link name survives the rewrite; every shell would share one node version" >&2
    return 1
  end
  printf '%s\n' $out >"$file"
end
