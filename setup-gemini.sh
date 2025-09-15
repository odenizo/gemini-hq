#!/bin/bash

# Gemini HQ Setup Script
# Deploys Gemini CLI configurations and sets up MCP servers

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

echo "🚀 Gemini HQ Setup Script"
echo "=========================="

# --- Configuration Paths ---
GEMINI_DIR="$HOME/.gemini"
CONFIG_SOURCE_DIR="$(pwd)/config"
CONFIG_DEST_DIR="$GEMINI_DIR"
CREDENTIALS_TEMPLATE="credentials.yaml.template"
CREDENTIALS_FILE="credentials.yaml"

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
while IFS= read -r line; do
    if [[ $line =~ ^[[:space:]]*([a-zA-Z0-9_]+): ]]; then
        server_name=${BASH_REMATCH[1]}
        enabled=$(grep -A 2 "$server_name:" "$CONFIG_SOURCE_DIR/mcp/mcp-config.yaml" | grep "enabled:" | awk '{print $2}')
        command=$(grep -A 3 "$server_name:" "$CONFIG_SOURCE_DIR/mcp/mcp-config.yaml" | grep "command:" | awk '{print $2}')
        args=$(grep -A 4 "$server_name:" "$CONFIG_SOURCE_DIR/mcp/mcp-config.yaml" | grep "args:" | cut -d'[' -f2 | cut -d']' -f1)

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
    fi
done < <(grep -E "^[[:space:]]{2}[a-zA-Z0-9_]+:" "$CONFIG_SOURCE_DIR/mcp/mcp-config.yaml")


echo ""
echo "🎉 Gemini CLI setup complete!"
echo "Please review and edit your credentials at $CONFIG_DEST_DIR/$CREDENTIALS_FILE"
