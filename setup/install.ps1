New-Item -ItemType SymbolicLink -Path "$HOME/.dotter" -Target "$HOME/.dotfiles/.dotter" -Force
New-Item -ItemType SymbolicLink -Path "$HOME/.dotfiles/.dotter/local.toml" -Target "$HOME/.dotfiles/.dotter/local/windows.toml" -Force
