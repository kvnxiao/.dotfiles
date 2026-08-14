# .dotfiles

Dotfiles managed via [patina](https://github.com/kvnxiao/patina).

## Prerequisites

Install the following before running any setup commands:

| Tool                                            | Purpose                 |
| ----------------------------------------------- | ----------------------- |
| [git](https://git-scm.com/)                     | version control         |
| [just](https://github.com/casey/just)           | task runner             |
| [patina](https://github.com/kvnxiao/patina)     | dotfile manager         |
| [fish](https://fishshell.com/)                  | shell                   |
| [starship](https://starship.rs/)                | shell prompt            |
| [fnm](https://github.com/Schniz/fnm)            | Node.js version manager |
| [zoxide](https://github.com/ajeetdsouza/zoxide) | smarter cd              |
| [atuin](https://github.com/atuinsh/atuin)       | shell history           |
| [lsd](https://github.com/lsd-rs/lsd)            | ls replacement          |
| [skim](https://github.com/skim-rs/skim)         | fuzzy finder            |
| [broot](https://github.com/Canop/broot)         | file navigator          |
| [neovim](https://neovim.io/)                    | editor                  |

With a Rust toolchain, install patina with
`cargo install --git https://github.com/kvnxiao/patina.git patina-cli`.

### Windows only

| Tool                            | Purpose                   |
| ------------------------------- | ------------------------- |
| [MSYS2](https://www.msys2.org/) | fish, zsh, and Unix tools |
| [scoop](https://scoop.sh/)      | package manager           |

Patina creates symbolic links. On Windows those require Developer Mode or an
elevated session. When `patina apply` needs the privilege, it offers a one-time
UAC prompt that turns Developer Mode on through the bundled `patina-elevate`
helper. After that, `patina apply` runs without elevation. To turn it on ahead
of time, run `patina doctor --fix`.

## Setup

```shell
cd ~
git clone https://github.com/kvnxiao/.dotfiles
cd ~/.dotfiles
just setup
```

`just setup` deploys the dotfiles through patina and wires the repo's git hooks.
On Windows it also applies the Defender exclusions and sets up the MSYS2 zsh and
fish environments.
