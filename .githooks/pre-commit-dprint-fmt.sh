#!/bin/sh
set -e

command -v dprint >/dev/null 2>&1 || {
	echo "pre-commit: dprint not on PATH, skipping format" >&2
	exit 0
}

tmp=$(mktemp)
trap 'rm -f "$tmp" "$tmp.fmt" "$tmp.list"' EXIT

git -c core.quotePath=false diff --cached --name-only --diff-filter=ACMR >"$tmp.list"

# Format the staged blob, not the working copy: `git add` on the working copy
# would also stage hunks that were left unstaged.
while IFS= read -r path <&3; do
	[ -n "$(dprint file-paths "$path")" ] || continue

	unstaged=0
	git diff --quiet -- "$path" || unstaged=1

	git show ":$path" >"$tmp"
	# --stdin resolves config from the working directory, not from the path.
	(cd "$(dirname "$path")" && dprint fmt --stdin "$(basename "$path")") <"$tmp" >"$tmp.fmt"
	cmp -s "$tmp" "$tmp.fmt" && continue

	mode=$(git ls-files -s -- "$path" | cut -d' ' -f1)
	blob=$(git hash-object -w --no-filters "$tmp.fmt")
	git update-index --cacheinfo "$mode,$blob,$path"

	if [ "$unstaged" = 0 ]; then
		git checkout -- "$path"
	else
		echo "pre-commit: formatted staged $path; its working copy keeps unstaged changes and is not formatted" >&2
	fi
done 3<"$tmp.list"
