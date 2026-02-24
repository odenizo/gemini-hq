#!/bin/bash

# Script to restore the ~/.gemini configuration directory from a backup archive

GEMINI_CONFIG_DIR="$HOME/.gemini"
BACKUP_FILEPATH="$1" # The .tar.gz backup file must be provided as an argument

set -e

echo "Starting Gemini configuration restore..."

if [ -z "$BACKUP_FILEPATH" ]; then
    echo "ERROR: No backup file specified. Usage: $0 <path_to_backup.tar.gz>"
    exit 1
fi

if [ ! -f "$BACKUP_FILEPATH" ]; then
    echo "ERROR: Backup file not found at $BACKUP_FILEPATH."
    exit 1
fi

echo "Source Archive: $BACKUP_FILEPATH"
echo "Target Directory: $HOME" # Will restore .gemini within $HOME

# Optional: Backup existing config before restoring
if [ -d "$GEMINI_CONFIG_DIR" ]; then
    TIMESTAMP=$(date +"%Y%m%d_%H%M%S")
    EXISTING_BACKUP_PATH="${GEMINI_CONFIG_DIR}_backup_${TIMESTAMP}"
    echo "WARNING: Existing configuration found at $GEMINI_CONFIG_DIR."
    echo "Moving existing configuration to $EXISTING_BACKUP_PATH before restoring."
    mv "$GEMINI_CONFIG_DIR" "$EXISTING_BACKUP_PATH"
    if [ $? -ne 0 ]; then
        echo "ERROR: Failed to move existing configuration. Aborting restore."
        exit 1
    fi
fi

echo "Extracting backup archive..."
# Extract the archive into the HOME directory, overwriting if necessary (though we moved existing)
tar -xzvf "$BACKUP_FILEPATH" -C "$HOME"

if [ $? -eq 0 ]; then
    echo "Restore completed successfully."
    echo "The '.gemini' directory has been restored in $HOME."
    if [ -d "$EXISTING_BACKUP_PATH" ]; then
        echo "Your previous configuration was moved to: $EXISTING_BACKUP_PATH"
    fi
else
    echo "ERROR: Restore failed during extraction."
    # Attempt to clean up potentially partially extracted files - might be risky
    echo "Please check $GEMINI_CONFIG_DIR manually."
    # Optionally try to restore the moved backup if extraction failed mid-way
    if [ -d "$EXISTING_BACKUP_PATH" ]; then
         echo "Attempting to restore previous config from $EXISTING_BACKUP_PATH..."
         rm -rf "$GEMINI_CONFIG_DIR" # Remove potentially broken extraction
         mv "$EXISTING_BACKUP_PATH" "$GEMINI_CONFIG_DIR" && echo "Previous config restored." || echo "Failed to restore previous config."
    fi
    exit 1
fi

exit 0
