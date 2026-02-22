# .dotfiles

Dotfiles managed via [dotter](https://github.com/SuperCuber/dotter).

## Prerequisites

Install the following before running any setup commands:

- [git](https://git-scm.com/)
- [just](https://github.com/casey/just) — task runner
- [dotter](https://github.com/SuperCuber/dotter) — dotfile manager
- [starship](https://starship.rs/) — shell prompt
- [fnm](https://github.com/Schniz/fnm) — Node.js version manager
- [zoxide](https://github.com/ajeetdsouza/zoxide) — smarter cd
- [atuin](https://github.com/atuinsh/atuin) — shell history
- [lsd](https://github.com/lsd-rs/lsd) — ls replacement
- [fzf](https://github.com/junegunn/fzf) — fuzzy finder
- [broot](https://github.com/Canop/broot) — file navigator
- [neovim](https://neovim.io/) — editor

### Windows only

- [MSYS2](https://www.msys2.org/) — provides zsh and Unix tools
- [scoop](https://scoop.sh/) — package manager
- Enable `Developer Mode` in settings: [`ms-settings:developers`](ms-settings:developers)

## Setup

```shell
cd ~
git clone https://github.com/kvnxiao/.dotfiles
cd ~/.dotfiles
just setup
```

`just setup` handles first-time installation (symlinks, Windows Defender exclusions) and deploys all dotfiles via dotter.
