function cargo-update-bins
  argparse 'dry-run' -- $argv
  or return 1

  set -l outdated_crates

  for line in (cargo install-update -a --list 2>/dev/null | rg 'Yes')
    set -l crate (echo $line | awk '{print $1}')
    if test -n "$crate"
        set -a outdated_crates $crate
    end
  end

  if test (count $outdated_crates) -eq 0
    echo "All crates are up to date."
    return 0
  end

  echo "Outdated crates:"
  for crate in $outdated_crates
    echo "  - $crate"
  end

  if set -q _flag_dry_run
    echo ""
    echo "Dry run — no changes made."
    return 0
  end

  echo ""
  read -P "Update all via cargo binstall? [y/N] " confirm
  if test "$confirm" != y -a "$confirm" != Y
    echo "Aborted."
    return 0
  end

  for crate in $outdated_crates
    echo ""
    echo "→ Updating $crate..."
    cargo binstall $crate --force --no-confirm
  end

  echo ""
  echo "Done!"
end
