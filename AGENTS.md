# Dotfiles guidelines

This repository holds the user's dotfiles. [patina](https://github.com/kvnxiao/patina),
a cross-platform dotfile manager, deploys them.

"Dotfiles" here is wider than tool config: shell rc files, app settings, agent skills and
prompts, scripts, keymaps, and anything else the user wants on their machines. Treat a
new kind of file as in scope.

## Layout

- One directory per tool (`git/`, `zsh/`, `fish/`, `wezterm/`, `agent-configs/`, …). Each
  holds the files and a `patina.toml` that says where they deploy.
- Root `patina.toml` marks the repo root and declares third-party `[[remote]]` git
  sources. `patina.lock` pins them.
- `justfile` wraps the deploy and per-platform setup steps.
- `setup/` holds the platform bootstrap scripts the justfile calls.

Patina renders a source that ends in `.tmpl` through MiniJinja instead of linking it.

## Deploying

Every entry but `git/.gitconfig.tmpl` deploys as a symlink, so an edit to a deployed file
is live at once. Run `patina apply` when the deployment itself changes: an edited
`patina.toml`, or an edit to that template.

```shell
patina apply        # prints the plan, changes nothing
patina apply --yes  # applies it
```

In a TTY, plain `apply` shows the diff and prompts. Anywhere else, an agent session
included, it prints the plan and exits without writing. Read the plan, then re-run with
`--yes`.

`just deploy` runs `patina apply` plus the Windows-only extras. It passes no `--yes`.

A new file needs an entry in that directory's `patina.toml` before it can deploy.

## Formatting

`dprint` formats JSON, Markdown, TOML, CSS, HTML, and YAML. The `pre-commit` hook runs it
over staged files once `just setup-hooks` has wired the hooks in.

## This file

`CLAUDE.md` is a symlink to `AGENTS.md`. Edit `AGENTS.md`.

## Benchmarking

Changes made to a shell's dotfiles (bash, fish, zsh, powershell) must run the appropriate `just benchmark-*` task to benchmark the time-to-interactive shell startup and ensure it is not significantly increased.
