## macOS environment.

# Google Cloud SDK PATH. Homebrew prefix is hardcoded to avoid `brew --prefix`
# forks, matching zsh/config/macos.zsh.
if [ -f /opt/homebrew/share/google-cloud-sdk/path.bash.inc ]; then
  . /opt/homebrew/share/google-cloud-sdk/path.bash.inc
fi
