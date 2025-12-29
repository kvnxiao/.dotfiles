#!/bin/bash

# Update sketchybar workspace number
sketchybar --trigger aerospace_workspace_change FOCUSED_WORKSPACE=$AEROSPACE_FOCUSED_WORKSPACE

# Whitelist: window titles (partial match) or app IDs (exact match)
WHITELIST_TITLES=("Versualizer")
WHITELIST_APP_IDS=()

# Get current workspace
current_workspace=$(aerospace list-workspaces --focused) || exit 1

# Get all windows across all workspaces
aerospace list-windows --all --format "%{window-id}|%{window-title}|%{app-bundle-id}" | while IFS='|' read -r window_id title app_id; do
    # Check if window matches whitelist
    for wl in "${WHITELIST_TITLES[@]}"; do
        [[ "$title" == *"$wl"* ]] && aerospace move-node-to-workspace --window-id "$window_id" "$current_workspace" < /dev/null && continue 2
    done
    
    for wl in "${WHITELIST_APP_IDS[@]}"; do
        [[ "$app_id" == "$wl" ]] && aerospace move-node-to-workspace --window-id "$window_id" "$current_workspace" < /dev/null && continue 2
    done
done
