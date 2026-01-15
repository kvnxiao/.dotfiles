#!/bin/bash
TICKET_INPUT="$1"
TICKET_ID=$(echo "$TICKET_INPUT" | grep -oE '[A-Z]+-[0-9]+' | head -n 1)

if [ -z "$TICKET_ID" ]; then
  echo "Error: Invalid ticket ID or URL format"
  exit 1
fi
