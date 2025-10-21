#!/bin/bash

# Gemini HQ Setup Script
# Deploys Gemini CLI configurations and sets up MCP servers

set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

echo "🚀 Gemini HQ Setup Script"
echo "=========================="

# --- Configuration Paths ---
GEMINI_DIR="$HOME/.gemini"
CONFIG_SOURCE_DIR="$SCRIPT_DIR/config"
CONFIG_DEST_DIR="$GEMINI_DIR"
CREDENTIALS_TEMPLATE="credentials.yaml.template"
CREDENTIALS_FILE="credentials.yaml"

if [ ! -d "$CONFIG_SOURCE_DIR/gemini" ] || [ ! -d "$CONFIG_SOURCE_DIR/mcp" ]; then
    echo -e "${RED}✗ Configuration source directories not found in $CONFIG_SOURCE_DIR.${NC}"
    echo "Please run this script from the repository where the config directory resides."
    exit 1
fi

# --- Create Gemini Directory ---
echo -n "Creating Gemini configuration directory... "
mkdir -p "$CONFIG_DEST_DIR"
echo -e "${GREEN}✓ Done${NC}"

# --- Deploy Configuration Files ---
echo "Deploying configuration files:"

# Copy config.yaml
echo -n "  - config.yaml... "
cp "$CONFIG_SOURCE_DIR/gemini/config.yaml" "$CONFIG_DEST_DIR/config.yaml"
echo -e "${GREEN}✓ Copied${NC}"

# Copy profiles.yaml
echo -n "  - profiles.yaml... "
cp "$CONFIG_SOURCE_DIR/gemini/profiles.yaml" "$CONFIG_DEST_DIR/profiles.yaml"
echo -e "${GREEN}✓ Copied${NC}"

# Copy mcp-config.yaml
echo -n "  - mcp-config.yaml... "
cp "$CONFIG_SOURCE_DIR/mcp/mcp-config.yaml" "$CONFIG_DEST_DIR/mcp-config.yaml"
echo -e "${GREEN}✓ Copied${NC}"

# --- Handle Credentials ---
echo -n "Handling credentials... "
if [ ! -f "$CONFIG_DEST_DIR/$CREDENTIALS_FILE" ]; then
    cp "$CONFIG_SOURCE_DIR/gemini/$CREDENTIALS_TEMPLATE" "$CONFIG_DEST_DIR/$CREDENTIALS_FILE"
    echo -e "${YELLOW}✓ Created from template${NC}"
    echo -e "${YELLOW}IMPORTANT: Edit $CONFIG_DEST_DIR/$CREDENTIALS_FILE to add your API keys.${NC}"
else
    echo -e "${GREEN}✓ Already exists${NC}"
fi

# --- Setup MCP Servers ---
echo ""
echo "Setting up MCP servers..."

# Note: This is a simplified parser for the YAML file.
# A more robust solution would use a proper YAML parser.
SERVER_CONFIG="$CONFIG_SOURCE_DIR/mcp/mcp-config.yaml"

mapfile -t SERVER_NAMES < <(
    awk '
        /^[[:space:]]*#/ { next }
        /^[[:space:]]*servers:[[:space:]]*$/ { section="servers"; next }
        /^[[:space:]]*custom_servers:[[:space:]]*$/ { section="custom_servers"; next }
        /^[[:space:]]*[A-Za-z0-9_]+:[[:space:]]*$/ && $0 !~ /^[[:space:]]/ { section="" }
        section != "" && /^[[:space:]]{2}([A-Za-z0-9_]+):[[:space:]]*$/ {
            key=$0
            sub(/^[[:space:]]*/, "", key)
            sub(/:.*/, "", key)
            if (key != "") { print key }
        }
    ' "$SERVER_CONFIG"
)

if [ ${#SERVER_NAMES[@]} -eq 0 ]; then
    echo -e "${YELLOW}⚠ No MCP servers found to process.${NC}"
else
    echo "Discovered MCP servers: ${SERVER_NAMES[*]}"
fi

get_server_field() {
    local server_name="$1"
    local field_name="$2"
    awk -v srv="$server_name" -v fld="$field_name" '
        $0 ~ "^[[:space:]]*" srv ":" { found=1; next }
        found && /^[[:space:]]{2}[A-Za-z0-9_]+:[[:space:]]*$/ && $0 !~ "^[[:space:]]*" srv ":" { exit }
        found && $0 ~ "^[[:space:]]{4}" fld ":" {
            line=$0
            sub(/^[[:space:]]*/, "", line)
            sub(fld ":", "", line)
            sub(/^[[:space:]]*/, "", line)
            sub(/[[:space:]]*$/, "", line)
            print line
            exit
        }
    ' "$SERVER_CONFIG"
}

for server_name in "${SERVER_NAMES[@]}"; do
    enabled=$(get_server_field "$server_name" "enabled")
    command=$(get_server_field "$server_name" "command")
    args=$(get_server_field "$server_name" "args")

    if [ "$enabled" == "true" ]; then
        echo -n "  - Installing $server_name... "
        if [ -n "$command" ] && [ -n "$args" ]; then
            # This is a placeholder for the actual installation command.
            # In a real scenario, you might run "npm install -g" or similar.
            echo "($command $args)"
            # Example of what might be run:
            # npm install -g ${args//,/ }
            echo -e "${GREEN}✓ (Simulated installation)${NC}"
        else
            echo -e "${RED}✗ Invalid config${NC}"
        fi
    else
        echo -e "  - Skipping $server_name (disabled)"
    fi
done


echo ""
echo "🎉 Gemini CLI setup complete!"
echo "Please review and edit your credentials at $CONFIG_DEST_DIR/$CREDENTIALS_FILE"
