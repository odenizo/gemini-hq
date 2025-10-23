#!/bin/bash

# Gemini HQ Setup Script
# Installs Gemini CLI, copies base configuration, and applies environment overrides.

# --- Configuration ---
# Specify the desired Gemini CLI version (e.g., "latest", "0.4.0")
GEMINI_CLI_VERSION="latest"

# Target environment (dev, prod, etc.). Defaults to 'dev' if no argument provided.
TARGET_ENV="${1:-dev}"

# Exit immediately if a command exits with a non-zero status.
set -e

echo "Starting Gemini CLI Setup for environment: $TARGET_ENV"

# --- Configuration Variables ---
GEMINI_CONFIG_DIR="$HOME/.gemini"
REPO_CONFIG_BASE_DIR="$(pwd)/config/gemini"
REPO_CONFIG_ENV_DIR="$REPO_CONFIG_BASE_DIR/env/$TARGET_ENV"
REPO_COMMANDS_DIR="$(pwd)/commands"

# --- Prerequisites Check ---
echo "Checking prerequisites..."
command -v npm >/dev/null 2>&1 || { echo >&2 "ERROR: npm is required but not installed. Aborting."; exit 1; }
command -v node >/dev/null 2>&1 || { echo >&2 "ERROR: node is required but not installed. Aborting."; exit 1; }
echo "Prerequisites met."

# --- Install/Update Gemini CLI ---
echo "Installing/Updating @google/gemini-cli@${GEMINI_CLI_VERSION} globally via npm..."
npm install -g "@google/gemini-cli@${GEMINI_CLI_VERSION}"
echo "Gemini CLI installed."

# --- Create Gemini Config Directories ---
echo "Ensuring Gemini configuration directories exist..."
mkdir -p "$GEMINI_CONFIG_DIR"
mkdir -p "$GEMINI_CONFIG_DIR/commands/custom"
mkdir -p "$GEMINI_CONFIG_DIR/extensions"
mkdir -p "$GEMINI_CONFIG_DIR/logs"
mkdir -p "$GEMINI_CONFIG_DIR/tmp"
echo "Configuration directories checked/created in $GEMINI_CONFIG_DIR."

# --- Copy Configuration Files ---
echo "Copying base configuration files..."

# Check if base credentials file exists in the repo config
if [ ! -f "$REPO_CONFIG_BASE_DIR/credentials.yaml" ]; then
    echo >&2 "ERROR: Base configuration file '$REPO_CONFIG_BASE_DIR/credentials.yaml' not found."
    echo >&2 "Please copy 'credentials.yaml.template' to 'credentials.yaml' and add your API key or ensure ADC is configured."
    exit 1
fi

cp "$REPO_CONFIG_BASE_DIR/config.yaml" "$GEMINI_CONFIG_DIR/"
cp "$REPO_CONFIG_BASE_DIR/profiles.yaml" "$GEMINI_CONFIG_DIR/"
cp "$REPO_CONFIG_BASE_DIR/credentials.yaml" "$GEMINI_CONFIG_DIR/" # Copy the user-configured base credentials

echo "Base configuration files copied."

# --- Apply Environment Overrides (config.yaml only for simplicity, extend as needed) ---
if [ -d "$REPO_CONFIG_ENV_DIR" ]; then
    echo "Applying overrides for environment '$TARGET_ENV'..."
    if [ -f "$REPO_CONFIG_ENV_DIR/config.yaml" ]; then
        # This is a simple overwrite. A merge strategy could be implemented with tools like yq if needed.
        echo "Overwriting config.yaml with $TARGET_ENV version."
        cp "$REPO_CONFIG_ENV_DIR/config.yaml" "$GEMINI_CONFIG_DIR/"
    else
        echo "No config.yaml override found for '$TARGET_ENV'."
    fi
    # Add logic here to copy/merge other env-specific files like profiles.yaml if required
else
    echo "No override directory found for environment '$TARGET_ENV'."
fi

# --- Copy Custom Commands ---
echo "Copying custom commands..."
find "$REPO_COMMANDS_DIR/custom" -maxdepth 1 -name "*.toml" -exec cp {} "$GEMINI_CONFIG_DIR/commands/custom/" \;
echo "Custom commands copied."

# --- Final Verification ---
echo "Verifying Gemini CLI installation..."
if command -v gemini >/dev/null 2>&1; then
    GEMINI_VERSION=$(gemini --version)
    echo "Gemini CLI version $GEMINI_VERSION found."
    echo "Setup complete for environment '$TARGET_ENV'!"
    echo "Next steps:"
    echo " - Register MCP servers (optional): ./scripts/register_mcp_servers.sh $TARGET_ENV"
    echo " - Set trusted folders (optional): ./scripts/manage_trusted_folders.sh add"
    echo " - Run Gemini: gemini"
else
    echo >&2 "ERROR: Gemini CLI command not found in PATH after installation."
    exit 1
fi

exit 0
