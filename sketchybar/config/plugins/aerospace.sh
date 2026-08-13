#!/usr/bin/env bash

# Redraws every workspace chip. Runs on aerospace_workspace_change.
# A chip draws when its workspace holds a window or has focus.

source "$CONFIG_DIR/workspaces.sh"

focused=$(aerospace list-workspaces --focused)
occupied=$(aerospace list-workspaces --monitor all --empty no)

args=()
for sid in "${WORKSPACE_IDS[@]}"; do
  if [ "$sid" = "$focused" ]; then
    args+=(--set space."$sid" drawing=on background.drawing=on)
  elif grep -qx "$sid" <<<"$occupied"; then
    args+=(--set space."$sid" drawing=on background.drawing=off)
  else
    args+=(--set space."$sid" drawing=off background.drawing=off)
  fi
done

sketchybar "${args[@]}"
