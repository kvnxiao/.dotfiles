#!/bin/zsh

if [[ ! -L "$HOME/.dotter" ]]; then
    echo "First-time install detected, running install.zsh..."
    zsh "${0:a:h}/install.zsh"
fi
