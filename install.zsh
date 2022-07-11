#!/bin/zsh

if [[ `uname` == "Darwin" ]]; then
  local_os="macos"
else
  local_os="linux"
fi

ln -snf "$HOME/.dotfiles/.dotter" "$HOME/.dotter"
ln -snf "$HOME/.dotfiles/.dotter/local/$local_os.toml" "$HOME/.dotfiles/.dotter/local.toml"
