#!/bin/bash
# Get current workspace
current_workspace=$(aerospace list-workspaces --focused)
# Move zebar windows to current workspace
aerospace list-windows --all | grep -E "(Zebar)" | awk '{print $1}' | while read window_id; do
    if [ -n "$window_id" ]; then
        aerospace move-node-to-workspace --window-id "$window_id" "$current_workspace" && true
        aerospace layout floating --window-id "$window_id" && true
    fi
done
