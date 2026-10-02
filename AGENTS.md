# Dotfiles guidelines

This repository holds the user's dotfiles. [patina](https://github.com/kvnxiao/patina), a
cross-platform dotfile manager, deploys them.

Treat shell rc files, app settings, agent skills and prompts, scripts, keymaps, and any new kind of
machine configuration as dotfiles.

## Layout

- Keep each tool in its own directory (`git/`, `zsh/`, `fish/`, `wezterm/`, `agent-configs/`, …),
  with a `patina.toml` that declares its deployment targets.
- Use the root `patina.toml` for the repository marker and third-party `[[remote]]` sources;
  `patina.lock` pins those sources.
- Use `justfile` for deployment and platform setup recipes.
- Keep platform bootstrap scripts in `setup/`.
- Keep rootless Podman configuration, the `lmserve` Compose file, and model tuning files in
  `lmserve/`; its README documents the model stack.

Patina renders sources ending in `.tmpl` through MiniJinja instead of linking them.

## Deploying

Deploy every entry except `git/.gitconfig.tmpl` as a symlink, so edits to deployed files take effect
immediately. Run `patina apply` when a `patina.toml` or that template changes.

```shell
patina apply        # prints the plan, changes nothing
patina apply --yes  # applies it
```

In a TTY, plain `apply` shows the diff and prompts. Otherwise, including agent sessions, it prints
the plan and exits without writing. Read the plan, then rerun with `--yes`.

`just deploy` runs `patina apply` and the Windows-only extras without `--yes`.

Add each new file to its directory's `patina.toml` before deploying it, unless a covering
`[[directory]]` uses `mode = "symlink-tree"`; that mode deploys every file under its source.

## Formatting

`dprint` formats JSON, Markdown, TOML, Malva, markup, YAML, and Dockerfiles. After
`just setup-hooks` wires the hooks in, `pre-commit` runs it over staged files.

## Prose guidance

Three sets of files define the prose rules. Each serves a different consumer:

- `agent-configs/shared/AGENTS.md`: every AI harness loads it upfront. Keep its prose section short
  and general to limit the tokens it reserves.
- `agent-configs/shared/output-styles/linear-prose.md`: the Claude Code output style, with the
  detailed rules. Keep it standalone: do not reference `AGENTS.md`, `audit-prose`, or any reference
  file from it.
- `agent-configs/shared/skills/audit-prose/` (`SKILL.md` and `references/`): a course-correction
  pass after a session generates code, comments, and documentation. It checks that output against
  the same rules.

When a change adds, removes, or adjusts a prose rule in any of these, update all three in the same
change. For example, changing when the 3+ rule requires a list updates the one-line summary in the
shared `AGENTS.md`, the detailed rule in `linear-prose.md`, and the matching check in `audit-prose`.
Expect some duplication; each file must work without the others.

## Post-completion checks

After completing a task, run `just check`. Run `just fix` to format every supported file.

## Benchmarking

Prefer fish builtins over external commands when modifying `.fish` files to avoid MSYS2 process
startup latency. For example, replace a literal `sed` substitution with `string replace`.

Choose the simplest behavior-preserving builtin approach. For example, iterate over a list with
`for item in $items` instead of generating indices with `seq` or maintaining a counter with `math`.

Use the following builtin replacements as a reference:

| Operation                        | External tool          | Prefer in fish                                         |
| -------------------------------- | ---------------------- | ------------------------------------------------------ |
| Iterate over list elements       | `seq` for indices      | `for item in $items`                                   |
| Replace literal text             | `sed`                  | `string replace -a -- old new "$value"`                |
| Replace text with a regex        | `sed`                  | `string replace -ar -- '[0-9]+' NUMBER "$value"`       |
| Check a regex match              | `grep -q`              | `string match -rq -- pattern "$value"`                 |
| Extract a colon-delimited field  | `cut`, simple `awk`    | `string split -f2 -- : "$value"`                       |
| Convert case                     | `tr`                   | `string lower -- "$value"`, `string upper -- "$value"` |
| Trim whitespace                  | `sed`, `awk`           | `string trim -- "$value"`                              |
| Extract a filename or directory  | `basename`, `dirname`  | `path basename -- "$file"`, `path dirname -- "$file"`  |
| Resolve an absolute path         | `realpath`             | `path resolve -- "$file"`                              |
| Count list elements              | `wc` over a pipeline   | `count $items`                                         |
| Check list membership            | `grep` over a pipeline | `contains -- "$target" $items`                         |
| Calculate a needed numeric value | `expr`, simple `bc`    | `math "$n + 1"`                                        |
| Read text into one variable      | `cat`                  | `set -l text (string collect -aN < file)`              |

Check behavior before replacing an external tool. For example, `count` counts list elements rather
than file lines or bytes, and `string collect -aN` preserves empty input and trailing newlines.

Keep external tools when a builtin replacement complicates the code or changes its behavior. For
example, retain `awk` for substantial streaming transformations instead of building a long fish
loop.

After changing bash, fish, zsh, or PowerShell dotfiles, run the corresponding `just
benchmark-*`
task and verify that interactive startup time did not increase significantly.

## Ad hoc shell scripts on Windows

A native Windows program ignores the MSYS signal sent by `timeout`. As a result,
`timeout N script -q -c '…'` does not stop a process started by `script`. Running `sk` or an
interactive shell through that pty can leave the wrapper and its child processes running. Stop them
from PowerShell with `Stop-Process -Id <pid> -Force`. Do not select processes by name; that can kill
the user's other interactive shells.

MSYS2 zsh and the Git-for-Windows bash used by agents run in separate Cygwin runtimes. Because of
that, `env VAR=x zsh …` leaves `VAR` unset in zsh. Put the test configuration in a file and source
it as the session's first command. Setting `ZDOTDIR` with `env` otherwise tests the real
configuration instead of the fixture.
