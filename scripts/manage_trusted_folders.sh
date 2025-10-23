#!/bin/bash

# Script to add or remove trusted folders listed in config/gemini/trusted_folders.json

ACTION="$1" # 'add' or 'remove'
CONFIG_FILE="$(pwd)/config/gemini/trusted_folders.json"

set -e

# --- Prerequisite Check ---
command -v jq >/dev/null 2>&1 || { echo >&2 "ERROR: jq is required. Please install jq. Aborting."; exit 1; }
command -v gemini >/dev/null 2>&1 || { echo >&2 "ERROR: gemini command not found. Run setup-gemini.sh first. Aborting."; exit 1; }

if [[ "$ACTION" != "add" && "$ACTION" != "remove" ]]; then
    echo "ERROR: Invalid action. Usage: $0 [add|remove]"
    exit 1
fi

if [ ! -f "$CONFIG_FILE" ]; then
    echo "ERROR: Trusted folders configuration file not found at $CONFIG_FILE. Aborting."
    exit 1
fi

echo "Processing trusted folders from $CONFIG_FILE..."
echo "Action: $ACTION"

# Read the JSON file and loop through each folder path
jq -r '.trustedFolders[]' "$CONFIG_FILE" | while read -r folder_path; do
    if [ -z "$folder_path" ]; then
        echo "Skipping empty folder path."
        continue
    fi

    # Ensure path is absolute (basic check)
    if [[ "$folder_path" != /* ]]; then
        echo "WARNING: Skipping relative path '$folder_path'. Only absolute paths are recommended for trusted folders."
        continue
    fi

    echo "Processing folder: $folder_path"

    if [ "$ACTION" == "add" ]; then
        # Check if already trusted before adding
        if ! gemini config list trustedFolders | grep -q "$folder_path"; then
            echo "  Adding '$folder_path' to trusted folders..."
            if gemini config add trustedFolders "$folder_path"; then
                echo "  Successfully added."
            else
                echo "  ERROR: Failed to add '$folder_path'."
            fi
        else
            echo "  '$folder_path' is already trusted. Skipping."
        fi
    elif [ "$ACTION" == "remove" ]; then
         # Check if it exists before removing
         if gemini config list trustedFolders | grep -q "$folder_path"; then
            echo "  Removing '$folder_path' from trusted folders..."
             if gemini config remove trustedFolders "$folder_path"; then
                 echo "  Successfully removed."
             else
                 echo "  ERROR: Failed to remove '$folder_path'."
             fi
        else
            echo "  '$folder_path' is not in the trusted list. Skipping."
        fi
    fi
done

echo "-----------------------------------------"
echo "Trusted folder management finished."
echo "Verify current list with: gemini config list trustedFolders"

exit 0
