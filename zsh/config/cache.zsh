## Cache shell init output from slow commands.
## Run `clear-cache` after upgrading fnm/zoxide/starship.

zmodload zsh/datetime

_cached_eval() {
  local cache_dir="${HOME}/.zsh/cache"
  if [[ "$1" == --clear ]]; then
    rm -rf "$cache_dir"
    echo "Eval cache cleared. Restart zsh to regenerate."
    return
  fi
  if [[ "$1" == --* ]]; then
    print -u2 "_cached_eval: unknown flag '$1' (did you mean --clear?)"
    return 1
  fi
  local name="$1" gen_cmd="$2"
  local cache="${cache_dir}/${name}.zsh"
  if [[ ! -f "$cache" ]]; then
    # Buffer output and only write the cache on success -- a redirect would
    # persist an empty file even when the command fails
    local out
    if ! out="$(${(z)gen_cmd})"; then
      print -u2 "_cached_eval: generation command for '${name}' failed; not caching"
      return 1
    fi
    mkdir -p "$cache_dir"
    # Write and post-process a private temp file, then move it into place:
    # concurrent shells racing on the same cache miss must never source a
    # half-processed shared file
    local tmp="${cache}.$$"
    print -r -- "$out" > "$tmp"
    # Run post-processing hook if defined: _cached_eval_post_<name>
    if (( ${+functions[_cached_eval_post_${name}]} )) && ! "_cached_eval_post_${name}" "$tmp"; then
      print -u2 "_cached_eval: post-processing hook for '${name}' rejected the output; discarding"
      rm -f "$tmp"
      return 1
    fi
    if ! zsh -n "$tmp"; then
      print -u2 "_cached_eval: cache for '${name}' failed syntax check; discarding"
      rm -f "$tmp"
      return 1
    fi
    mv -f "$tmp" "$cache"
    zcompile "$cache" 2>/dev/null
  fi
  source "$cache"
}

# Rewrite absolute starship paths to a bare `starship` so the cache survives
# binary relocations (e.g. homebrew -> cargo) and MSYS2's quoted Windows-style
# emissions ('C:\...\starship.exe'), which zsh under MSYS2 cannot exec. Bake in
# PROMPT2, which starship otherwise emits as a per-shell command substitution.
_cached_eval_post_starship() {
  local file="$1" tmp="$1.postsed"
  sed -E "s@'?([A-Za-z]:)?[A-Za-z0-9_./\\\\ :-]*[/\\\\]starship(\.exe)?'?@starship@g" "$file" > "$tmp" \
    && mv -f "$tmp" "$file"
  if grep -q '/starship' "$file"; then
    print -u2 "_cached_eval_post_starship: absolute starship path remains in cache; prompt may break if the binary moves"
  fi

  # STARSHIP_SHELL selects the escape dialect, and only the zsh dialect wraps
  # escapes in %{...%} for zle to count prompt width. A zsh launched from bash
  # or fish inherits their STARSHIP_SHELL. An edited `continuation_prompt` in
  # starship.toml takes effect only after `clear-cache`.
  local continuation
  if ! continuation="$(STARSHIP_SHELL=zsh starship prompt --continuation)" || [[ -z $continuation ]]; then
    print -u2 "_cached_eval_post_starship: could not render continuation prompt; PROMPT2 keeps its per-shell spawn"
    return
  fi
  sed -E '/^PROMPT2=/d' "$file" > "$tmp" && mv -f "$tmp" "$file"
  print -r -- "PROMPT2=${(qqqq)continuation}" >> "$file"
  if grep -q '^PROMPT2=.*starship' "$file"; then
    print -u2 "_cached_eval_post_starship: PROMPT2 still spawns starship in every shell"
  fi
}

# zoxide 0.10.0's Cygwin branch emits `cygpath -w "\builtin pwd -L"` with the
# command substitution missing, so every directory change feeds cygpath a
# literal string and the database records nothing. On macOS and Linux, zoxide
# does not emit a cygpath call and the pattern cannot match.
_cached_eval_post_zoxide() {
  local file="$1" tmp="$1.postzoxide"
  # Capturing the command avoids writing a literal-backslash pattern, which
  # this sed does not match. An already-substituted line ends in `pwd -L)"` and
  # cannot re-match.
  sed 's|cygpath -w "\(.*\) pwd -L"|cygpath -w "$(\1 pwd -L)"|' "$file" > "$tmp" \
    && mv -f "$tmp" "$file"
  if grep -qF 'cygpath -w "\builtin' "$file"; then
    print -u2 "_cached_eval_post_zoxide: unsubstituted pwd remains; every directory change would feed cygpath a literal string"
    return 1
  fi
}

# The reserved link does not exist until the first `fnm use`; until then node
# resolves through the default alias behind it. A cache generated before
# link_suffix existed passes three arguments, so link_suffix stays last.
_fnm_reserve() {
  local msys_prefix="$1" win_prefix="$2" default_alias="$3" link_suffix="$4"
  local -i ms=$(( EPOCHREALTIME * 1000 ))
  local name="$$_${ms}"
  export FNM_MULTISHELL_PATH="${win_prefix}${name}"
  path=( "${msys_prefix}${name}${link_suffix}" "$default_alias" $path )
}

# The first `fnm use` in a shell moves node from the default alias to the
# reserved link and changes which PATH entry wins. zsh keeps running the path
# it hashed, so `fnm current` and `node --version` report different versions
# until a rehash. fish and PowerShell re-resolve on their own and do not need
# the wrapper.
fnm() {
  command fnm "$@"
  local ret=$?
  rehash
  return $ret
}

# `fnm env` mints a symlink per call and writes it into PATH as a literal, so a
# cached copy pins every shell to one link: `fnm use` in one shell switches
# node in all of them, and the entry dangles for good once that version is
# uninstalled. Keep fnm's static exports and reserve the link instead.
_cached_eval_post_fnm() {
  local file="$1" tmp="$1.postfnm"
  local line msys_link='' win_link='' win_dir=''
  local -a kept=()

  for line in "${(@f)$(<$file)}"; do
    case $line in
      ('export PATH='*)
        msys_link=${${line#export PATH=\"}%%\"*}
        continue ;;
      ('export FNM_MULTISHELL_PATH='*)
        win_link=${${line#export FNM_MULTISHELL_PATH=\"}%\"}
        continue ;;
      ('export FNM_DIR='*)
        win_dir=${${line#export FNM_DIR=\"}%\"} ;;
    esac
    kept+=( "$line" )
  done
  if [[ -z $msys_link || -z $win_link || -z $win_dir ]]; then
    print -u2 "_cached_eval_post_fnm: fnm env output shape changed; caching it would pin one symlink across every shell"
    return 1
  fi

  # fnm's zsh dialect formats paths through Rust's {:?}, which doubles every
  # backslash.
  win_link=${win_link//\\\\/\\}
  win_dir=${win_dir//\\\\/\\}
  local name=${win_link##*[/\\]}
  local win_prefix=${win_link%"$name"}
  if [[ -z $name || -z $win_prefix ]]; then
    print -u2 "_cached_eval_post_fnm: FNM_MULTISHELL_PATH '${win_link}' does not split into a prefix and a link name; not caching"
    return 1
  fi
  if [[ $msys_link != *"$name"* ]]; then
    print -u2 "_cached_eval_post_fnm: PATH entry '${msys_link}' does not contain link name '${name}'; not caching"
    return 1
  fi
  # fnm puts node in <link>/bin on Unix and node.exe in <link> on Windows.
  local msys_prefix=${msys_link%"$name"*} link_suffix=${msys_link##*"$name"}
  if [[ $msys_prefix != */ ]]; then
    print -u2 "_cached_eval_post_fnm: PATH entry '${msys_link}' is not a POSIX path; not caching"
    return 1
  fi

  local native_dir=$win_dir
  if [[ $win_dir == [A-Za-z]:* || $win_dir == '\\'* ]] \
    && ! native_dir="$(cygpath -u "$win_dir")"; then
    print -u2 "_cached_eval_post_fnm: could not convert FNM_DIR '${win_dir}' to a native path; not caching"
    return 1
  fi
  local default_alias="${native_dir%/}/aliases/default${link_suffix}"

  print -rl -- "${kept[@]}" \
    "_fnm_reserve ${(qq)msys_prefix} ${(qq)win_prefix} ${(qq)default_alias} ${(qq)link_suffix}" > "$tmp" || return 1
  if grep -qF -- "$name" "$tmp"; then
    print -u2 "_cached_eval_post_fnm: the minted link name survives the rewrite; every shell would share one node version"
    rm -f "$tmp"
    return 1
  fi
  mv -f "$tmp" "$file"
}

# Cache tool-generated completion files into a directory on fpath.
# ~/.zsh/completions is prepended to fpath in .zshrc before compinit runs;
# on first generation the completion is also registered immediately.
cached-completions() {
  local dir="${HOME}/.zsh/completions"
  if [[ "$1" == --clear ]]; then
    rm -rf "$dir"
    echo "Completions cache cleared. Restart zsh to regenerate."
    return
  fi
  if [[ "$1" == --* ]]; then
    print -u2 "cached-completions: unknown flag '$1' (did you mean --clear?)"
    return 1
  fi
  local name="$1" gen_cmd="$2"
  local file="${dir}/_${name}"
  if [[ ! -f "$file" ]]; then
    local out
    if ! out="$(${(z)gen_cmd})"; then
      print -u2 "cached-completions: generation command for '${name}' failed; not caching"
      return 1
    fi
    mkdir -p "$dir"
    print -r -- "$out" > "$file"
    # Future shells pick this up from fpath at compinit
    if (( ${+functions[compdef]} )); then
      autoload -Uz "_${name}" && compdef "_${name}" "$name"
    fi
  fi
}

clear-cache() {
  _cached_eval --clear
  cached-completions --clear
  # Compiled config files are the one artifact no cache helper owns
  # (see the auto-zcompile block in .zshrc). (N) avoids a "no matches
  # found" error when none exist.
  rm -f "${HOME}/.zsh"/*.zwc(N) "${HOME}/.zshrc.zwc"(N)
}
