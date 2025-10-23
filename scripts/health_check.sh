#!/bin/bash

# Script to perform a basic health check on MCP servers defined in config/mcp/servers.json

TARGET_ENV="${1:-dev}" # Default to 'dev' if no environment is specified

set -e

MCP_SERVERS_CONFIG="$(pwd)/config/mcp/servers.json"

# --- Prerequisite Check ---
command -v jq >/dev/null 2>&1 || { echo >&2 "ERROR: jq is required. Please install jq. Aborting."; exit 1; }
command -v curl >/dev/null 2>&1 || { echo >&2 "ERROR: curl is required. Please install curl. Aborting."; exit 1; }

if [ ! -f "$MCP_SERVERS_CONFIG" ]; then
    echo >&2 "ERROR: MCP server configuration file not found at $MCP_SERVERS_CONFIG. Aborting."
    exit 1
fi

echo "Performing health check for MCP servers in environment: $TARGET_ENV"
echo "Reading configurations from $MCP_SERVERS_CONFIG..."

EXIT_CODE=0 # Assume success initially

# Function to check a server URL (expects OpenAPI spec URL)
check_server() {
    local server_name="$1"
    local spec_url_raw="$2"
    local base_url=""

    # Evaluate url for shell expansions like $(pwd)
    eval "spec_url=\"$spec_url_raw\""

    echo "-----------------------------------------"
    echo "Checking server: $server_name"
    echo "  Spec URL: $spec_url"

    # Determine base URL: If it's a file URL, try localhost:3000 (common example), otherwise parse HTTP URL
    if [[ "$spec_url" == file://* ]]; then
        # Attempt to extract base URL from OpenAPI spec if possible (using jq)
        # Or make an assumption for local files (e.g., localhost:3000 used by example)
        base_url="http://localhost:3000" # Assumption for local example
        echo "  Assuming base URL for local spec: $base_url (Adjust if needed)"
        # More robust: Parse the spec file for server URL if jq is available
        if command -v yq >/dev/null 2>&1 && [[ "$spec_url" == *.yaml || "$spec_url" == *.yml ]]; then
             parsed_url=$(yq -r '.servers[0].url' "${spec_url#file://}")
             if [ ! -z "$parsed_url" ] && [ "$parsed_url" != "null" ]; then base_url=$parsed_url; fi
        elif [[ "$spec_url" == *.json ]]; then
             parsed_url=$(jq -r '.servers[0].url' "${spec_url#file://}")
             if [ ! -z "$parsed_url" ] && [ "$parsed_url" != "null" ]; then base_url=$parsed_url; fi
        fi
         echo "  Parsed/Assumed Base URL: $base_url"

    elif [[ "$spec_url" == http://* || "$spec_url" == https://* ]]; then
        # Extract base URL (protocol + hostname + port) from the spec URL
        base_url=$(echo "$spec_url" | grep -oE '^(https?://[^/]+)')
        echo "  Extracted Base URL: $base_url"
    else
        echo "  WARNING: Cannot determine base URL from spec URL '$spec_url'. Skipping health check."
        return
    fi

    # Perform a simple GET request to the base URL
    if curl --silent --fail --connect-timeout 5 "$base_url" > /dev/null; then
        echo "  Status: OK (Responded to base URL request)"
    else
        echo "  Status: FAIL (Could not connect or received error from base URL: $base_url)"
        EXIT_CODE=1 # Mark failure
    fi
}

# Process common servers
jq -c '.common // [] | .[]' "$MCP_SERVERS_CONFIG" | while read -r server; do
    name=$(echo "$server" | jq -r '.name')
    url=$(echo "$server" | jq -r '.url')
    if [ ! -z "$name" ] && [ "$name" != "null" ] && [ ! -z "$url" ] && [ "$url" != "null" ]; then
        check_server "$name" "$url"
    fi

done

# Process environment-specific servers
jq -c --arg env "$TARGET_ENV" '.[$env] // [] | .[]' "$MCP_SERVERS_CONFIG" | while read -r server; do
     name=$(echo "$server" | jq -r '.name')
     url=$(echo "$server" | jq -r '.url')
     if [ ! -z "$name" ] && [ "$name" != "null" ] && [ ! -z "$url" ] && [ "$url" != "null" ]; then
         check_server "$name" "$url"
     fi

done

echo "-----------------------------------------"
if [ "$EXIT_CODE" -eq 0 ]; then
    echo "Health check finished: All reachable servers responded."
else
    echo "Health check finished: One or more servers failed to respond."
fi

exit $EXIT_CODE
