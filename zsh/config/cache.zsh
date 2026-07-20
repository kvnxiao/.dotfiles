## Cache shell init output from slow commands.
## Run `zsh-rebuild-cache` after upgrading fnm/zoxide/atuin/starship/fzf.

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
    if (( ${+functions[_cached_eval_post_${name}]} )); then
      "_cached_eval_post_${name}" "$tmp"
    fi
    if ! zsh -n "$tmp"; then
      print -u2 "_cached_eval: cache for '${name}' failed syntax check: ${cache}"
    fi
    mv -f "$tmp" "$cache"
    zcompile "$cache" 2>/dev/null
  fi
  source "$cache"
}

# Rewrite absolute starship paths to a bare `starship` so the cache survives
# binary relocations (e.g. homebrew -> cargo) and MSYS2's quoted Windows-style
# emissions ('C:\...\starship.exe'), which zsh under MSYS2 cannot exec.
_cached_eval_post_starship() {
  local file="$1" tmp="$1.postsed"
  sed -E "s@'?([A-Za-z]:)?[A-Za-z0-9_./\\\\ :-]*[/\\\\]starship(\.exe)?'?@starship@g" "$file" > "$tmp" \
    && mv -f "$tmp" "$file"
  if grep -q '/starship' "$file"; then
    print -u2 "_cached_eval_post_starship: absolute starship path remains in cache; prompt may break if the binary moves"
  fi
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

zsh-rebuild-cache() {
  _cached_eval --clear
  cached-completions --clear
  # Compiled config files are the one artifact no cache helper owns
  # (see the auto-zcompile block in .zshrc). (N) avoids a "no matches
  # found" error when none exist.
  rm -f "${HOME}/.zsh"/*.zwc(N) "${HOME}/.zshrc.zwc"(N)
}
