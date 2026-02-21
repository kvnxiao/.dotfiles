#!/usr/bin/env zsh
# Computes and appends HOSTNAME, LANG, and TZ to ~/.zshenv.
# These values are normally resolved via subprocess spawns in /etc/profile
# and /etc/profile.d/{lang,tzset}.sh. Pre-setting them skips those spawns.
#
# Run this once on each machine (or after changing timezone/locale):
#   zsh ~/.dotfiles/setup-zshenv.zsh

set -e

ZSHENV="$HOME/.zshenv"

# Compute current values using the same commands /etc/profile would use
_hostname="$(/usr/bin/hostname)"
_lang="$(/usr/bin/locale -uU)"
_tz="$(/usr/bin/tzset)"
_shell="$(which zsh)"

echo "Detected values:"
echo "  HOSTNAME=$_hostname"
echo "  LANG=$_lang"
echo "  TZ=$_tz"
echo "  SHELL=$_shell"

# Remove any previously generated block
if [[ -f "$ZSHENV" ]]; then
  sed -i '/^# --- setup-zshenv generated ---$/,/^# --- end setup-zshenv ---$/d' "$ZSHENV"
fi

# Append computed values
cat >> "$ZSHENV" <<EOF
# --- setup-zshenv generated ---
# Pre-set to skip subprocess spawns in /etc/profile and /etc/profile.d/*.sh
# Regenerate with: zsh ~/.dotfiles/setup-zshenv.zsh
export HOSTNAME="$_hostname"
export LANG="$_lang"
export TZ="$_tz"
export SHELL="$_shell"
# --- end setup-zshenv ---
EOF

echo ""
echo "Appended to $ZSHENV. Restart zsh for changes to take effect."
