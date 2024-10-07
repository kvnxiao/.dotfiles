#!/bin/zsh

if [[ "$OSTYPE" == "msys"* ]]; then
  echo "Detected Windows OS under msys. Please use the install.ps1 PowerShell script instead."
  exit 1
fi

if [[ "$OSTYPE" == "darwin"* ]]; then
  local_os="macos"
else
  local_os="linux"
fi

ln -snf "$HOME/.dotfiles/.dotter" "$HOME/.dotter"
ln -snf "$HOME/.dotfiles/.dotter/local/$local_os.toml" "$HOME/.dotfiles/.dotter/local.toml"
