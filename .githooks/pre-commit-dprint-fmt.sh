#!/bin/sh
set -e

command -v dprint >/dev/null 2>&1 || {
	echo "pre-commit: dprint not on PATH, skipping format" >&2
	exit 0
}

dprint fmt --staged --allow-no-files

git diff --cached --name-only --diff-filter=ACMR -z | xargs -0 -r git add --
