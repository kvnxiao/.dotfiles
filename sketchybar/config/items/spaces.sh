#!/bin/bash

source "$CONFIG_DIR/workspaces.sh"

SPACE_ICONS=("一" "二" "三" "四" "五" "六" "七" "八" "九" "十" "十一" "十二" "十三" "十四" "十五")

# Focus a space on left click.

# Aerospace creates and destroys workspaces as windows move, so the chip for
# every id exists up front and plugins/aerospace.sh decides which ones draw.
for sid in "${WORKSPACE_IDS[@]}"; do
  space=(
    icon="${SPACE_ICONS[$sid - 1]}"
    icon.padding_left=10
    icon.padding_right=10
    padding_left=2
    padding_right=2
    label.padding_right=20
    icon.highlight_color=$RED
    label.color=$GREY
    label.highlight_color=$WHITE
    label.font="sketchybar-app-font:Regular:16.0"
    label.y_offset=-1
    background.color=$BACKGROUND_1
    background.border_color=$BACKGROUND_2
    background.drawing=off
    label.drawing=off
    label="$sid"
    drawing=off
    click_script="aerospace workspace $sid"
  )

  sketchybar --add item space."$sid" left \
    --set space."$sid" "${space[@]}"
done

spaces_bracket=(
  background.color=$BACKGROUND_1
  background.border_color=$BACKGROUND_2
)

# Hidden driver for the chips above. updates=on keeps it running while it is
# invisible, so it still redraws them on every aerospace event.
spaces_observer=(
  drawing=off
  updates=on
  script="$PLUGIN_DIR/aerospace.sh"
)

sketchybar --add bracket spaces_bracket '/space\..*/' \
  --set spaces_bracket "${spaces_bracket[@]}" \
  \
  --add item spaces_observer left \
  --set spaces_observer "${spaces_observer[@]}" \
  --subscribe spaces_observer aerospace_workspace_change
