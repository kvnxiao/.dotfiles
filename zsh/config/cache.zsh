## Cache shell init output from slow commands.
## Run `clear-cache` after upgrading fnm/zoxide/atuin/starship/fzf.

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
    if (( ${+functions[_cached_eval_post_${name}]} )); then
      "_cached_eval_post_${name}" "$tmp"
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

# Write `atuin uuid`'s 32-char simple UUIDv7 format into REPLY. A command
# substitution would fork and leave RANDOM unadvanced in this shell, so every
# call would return the same random bits.
_atuin_uuid7() {
  typeset -g REPLY
  local -i ms=$(( EPOCHREALTIME * 1000 ))
  printf -v REPLY '%012x7%03x%x%015x' $ms $(( RANDOM & 0xfff )) \
    $(( 8 + (RANDOM & 3) )) \
    $(( (RANDOM << 45) ^ (RANDOM << 30) ^ (RANDOM << 15) ^ RANDOM ))
}

# `atuin uuid` costs a ~120 ms process spawn under MSYS2. The generated cache
# outlives edits to this file, so the rewritten line guards on _atuin_uuid7
# and falls back to the spawn instead of exporting a stale REPLY.
_cached_eval_post_atuin() {
  local file="$1" tmp="$1.postsed"
  sed -E 's@^([[:space:]]*)export ATUIN_SESSION=\$\(atuin uuid\)$@\1if (( ${+functions[_atuin_uuid7]} )); then _atuin_uuid7; export ATUIN_SESSION=$REPLY; else export ATUIN_SESSION=$(atuin uuid); fi@' \
    "$file" > "$tmp" && mv -f "$tmp" "$file"
  if grep -qE '^[[:space:]]*export ATUIN_SESSION=\$\(atuin uuid\)$' "$file"; then
    print -u2 "_cached_eval_post_atuin: 'atuin uuid' spawn remains in cache"
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

clear-cache() {
  _cached_eval --clear
  cached-completions --clear
  # Compiled config files are the one artifact no cache helper owns
  # (see the auto-zcompile block in .zshrc). (N) avoids a "no matches
  # found" error when none exist.
  rm -f "${HOME}/.zsh"/*.zwc(N) "${HOME}/.zshrc.zwc"(N)
}
