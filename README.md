# .dotfiles

Dotfiles managed via [patina](https://github.com/kvnxiao/patina).

## Prerequisites

Install the following before running any setup commands:

- [git](https://git-scm.com/)
- [just](https://github.com/casey/just) — task runner
- [patina](https://github.com/kvnxiao/patina) — dotfile manager. With a Rust
  toolchain present, install with:
  `cargo install --git https://github.com/kvnxiao/patina.git patina-cli`
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

Patina creates symbolic links, which on Windows require either Developer Mode or
an elevated session. You no longer need to enable Developer Mode by hand: when
`patina apply` needs the privilege it offers a one-time UAC prompt that toggles
Developer Mode on via the bundled `patina-elevate` helper. You can also run
`patina doctor --fix` to remediate it ahead of time.

## Setup

```shell
cd ~
git clone https://github.com/kvnxiao/.dotfiles
cd ~/.dotfiles
just setup
```

`just setup` deploys all dotfiles via patina and, on Windows, applies Windows
Defender exclusions.
