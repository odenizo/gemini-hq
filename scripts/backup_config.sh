#!/bin/bash

# Script to backup the ~/.gemini configuration directory

GEMINI_CONFIG_DIR="$HOME/.gemini"
DEFAULT_BACKUP_DIR="$(pwd)/backups" # Default to a 'backups' subdirectory in the repo
BACKUP_DIR="${1:-$DEFAULT_BACKUP_DIR}" # Use provided argument or default

set -e

TIMESTAMP=$(date +"%Y%m%d_%H%M%S")
BACKUP_FILENAME="gemini_config_backup_${TIMESTAMP}.tar.gz"
BACKUP_FILEPATH="$BACKUP_DIR/$BACKUP_FILENAME"

echo "Starting Gemini configuration backup..."

if [ ! -d "$GEMINI_CONFIG_DIR" ]; then
    echo "ERROR: Gemini configuration directory not found at $GEMINI_CONFIG_DIR. Nothing to back up."
    exit 1
fi

echo "Source: $GEMINI_CONFIG_DIR"
echo "Destination Dir: $BACKUP_DIR"

# Create backup directory if it doesn't exist
mkdir -p "$BACKUP_DIR"

echo "Creating archive: $BACKUP_FILEPATH"

# Create tar.gz archive. Exclude potentially large/temporary subdirectories.
tar --exclude="$GEMINI_CONFIG_DIR/tmp" \
    --exclude="$GEMINI_CONFIG_DIR/extensions/node_modules" \
    --exclude="$GEMINI_CONFIG_DIR/logs/*" \
    --exclude="*.log" \
    --exclude="*.bak" \
    -czvf "$BACKUP_FILEPATH" -C "$HOME" ".gemini"

if [ $? -eq 0 ]; then
    echo "Backup created successfully: $BACKUP_FILEPATH"
else
    echo "ERROR: Backup creation failed."
    # Attempt to clean up partial backup file
    [ -f "$BACKUP_FILEPATH" ] && rm "$BACKUP_FILEPATH"
    exit 1
fi

exit 0
