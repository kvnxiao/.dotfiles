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
| [skell](https://github.com/kvnxiao/skell)       | shell history           |
| [eza](https://github.com/eza-community/eza)     | ls replacement          |
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

### macOS only

| Tool                                                  | Purpose                      |
| ----------------------------------------------------- | ---------------------------- |
| [pnpm](https://pnpm.io/)                              | builds the Zebar widget pack |
| [Zebar](https://glzr.io/)                             | top bar                      |
| [AeroSpace](https://github.com/nikitabobko/AeroSpace) | tiling window manager        |

`zebar/settings.json` sets `acceptFirstMouse`, so the first click on the bar presses a button
instead of only activating Zebar. Official Zebar 3.3.1 ignores the setting; it needs a build that
includes [glzr-io/zebar#315](https://github.com/glzr-io/zebar/pull/315).

Patina creates symbolic links. On Windows those require Developer Mode or an elevated session. When
`patina apply` needs the privilege, it offers a one-time UAC prompt that turns Developer Mode on
through the bundled `patina-elevate` helper. After that, `patina apply` runs without elevation. To
turn it on ahead of time, run `patina doctor --fix`.

## Setup

```shell
cd ~
git clone https://github.com/kvnxiao/.dotfiles
cd ~/.dotfiles
just setup
```

`just setup` deploys the dotfiles through patina and wires the repo's git hooks. On Windows it also
applies the Defender exclusions and sets up the MSYS2 zsh and fish environments.
