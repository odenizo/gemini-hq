#!/bin/bash

# Script to register MCP servers based on environment from config/mcp/servers.json

TARGET_ENV="${1:-dev}" # Default to 'dev' if no environment is specified

set -e

MCP_SERVERS_CONFIG="$(pwd)/config/mcp/servers.json"
CREDENTIALS_FILE="$HOME/.gemini/credentials.yaml" # Default location

# --- Prerequisite Check ---
command -v jq >/dev/null 2>&1 || { echo >&2 "ERROR: jq is required. Please install jq. Aborting."; exit 1; }
command -v gemini >/dev/null 2>&1 || { echo >&2 "ERROR: gemini command not found. Run setup-gemini.sh first. Aborting."; exit 1; }

if [ ! -f "$MCP_SERVERS_CONFIG" ]; then
    echo >&2 "ERROR: MCP server configuration file not found at $MCP_SERVERS_CONFIG. Aborting."
    exit 1
fi

echo "Registering MCP servers for environment: $TARGET_ENV"
echo "Reading configurations from $MCP_SERVERS_CONFIG..."

# Function to process a single server JSON object
process_server() {
    local server_json="$1"
    name=$(echo "$server_json" | jq -r '.name')
    url_raw=$(echo "$server_json" | jq -r '.url')
    description=$(echo "$server_json" | jq -r '.description // empty')
    auth_config=$(echo "$server_json" | jq -c '.auth // null')

    if [ -z "$name" ] || [ "$name" == "null" ]; then
        echo >&2 "WARNING: Skipping server entry with missing or null name: $server_json"
        return
    fi
    if [ -z "$url_raw" ] || [ "$url_raw" == "null" ]; then
        echo >&2 "WARNING: Skipping server '$name' due to missing or null url."
        return
    fi

    # Evaluate url for shell expansions like $(pwd)
    eval "url=\"$url_raw\""

    echo "-----------------------------------------"
    echo "Processing server: $name"
    echo "  URL: $url"
    [ ! -z "$description" ] && [ "$description" != "null" ] && echo "  Description: $description"

    # Check if server is already registered and remove it first
    if gemini mcp list | grep -q "^$name "; then # Added space to avoid partial matches
        echo "  Server '$name' already registered. Removing and re-adding..."
        gemini mcp remove "$name" --force || echo "  WARNING: Could not remove existing server '$name', proceeding anyway."
    fi

    # Construct the gemini mcp add command
    cmd="gemini mcp add \"$name\" \"$url\""
    if [ ! -z "$description" ] && [ "$description" != "null" ]; then
         cmd="$cmd --description \"$description\""
    fi

    # Add authentication arguments if present
    if [ "$auth_config" != "null" ]; then
        echo "  Adding authentication config..."
        auth_type=$(echo "$auth_config" | jq -r '.type // empty')
        credential_source=$(echo "$auth_config" | jq -r '.credential_source // empty')
        key_name_in_file=$(echo "$auth_config" | jq -r '.key_name_in_file // empty')
        api_key_env_var=$(echo "$auth_config" | jq -r '.api_key_env_var // empty')
        scopes_raw=$(echo "$auth_config" | jq -r '.scopes // empty | join(" ")') # join array if present

        if [ ! -z "$auth_type" ] && [ "$auth_type" != "null" ]; then
            cmd="$cmd --auth-type \"$auth_type\""
            if [ ! -z "$credential_source" ] && [ "$credential_source" != "null" ]; then
                 cmd="$cmd --auth-credential-source \"$credential_source\""
                 if [ "$credential_source" == "credential_file" ]; then
                     if [ -z "$key_name_in_file" ] || [ "$key_name_in_file" == "null" ]; then
                        echo "  WARNING: Auth type is credential_file but 'key_name_in_file' is missing for '$name'."
                     fi
                     # Gemini CLI implies name matching for key_name_in_file within credentials.yaml mcp_auth block
                 elif [ "$credential_source" == "env_var" ]; then
                     if [ -z "$api_key_env_var" ] || [ "$api_key_env_var" == "null" ]; then
                         echo "  WARNING: Auth type is env_var but 'api_key_env_var' is missing for '$name'."
                     else
                        cmd="$cmd --auth-api-key-env-var \"$api_key_env_var\""
                     fi
                 fi
            fi
            if [ ! -z "$scopes_raw" ] && [ "$scopes_raw" != "null" ]; then
                # Scopes are space-separated, pass them directly without extra quotes
                cmd="$cmd --auth-scopes $scopes_raw"
            fi
        else
             echo "  WARNING: Auth config found for '$name' but 'type' is missing."
        fi
    fi

    cmd="$cmd --force" # Add --force to bypass prompts

    echo "  Executing: $cmd"
    if eval "$cmd"; then
        echo "  Successfully registered/updated server '$name'."
    else
        echo >&2 "  ERROR: Failed to register server '$name'."
    fi
}

# Process common servers
jq -c '.common // [] | .[]' "$MCP_SERVERS_CONFIG" | while read -r server; do
    process_server "$server"
done

# Process environment-specific servers
jq -c --arg env "$TARGET_ENV" '.[$env] // [] | .[]' "$MCP_SERVERS_CONFIG" | while read -r server; do
    process_server "$server"
done

echo "-----------------------------------------"
echo "MCP Server registration process finished for environment '$TARGET_ENV'."
echo "Verify registration with: gemini mcp list"

exit 0
