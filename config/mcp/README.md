# MCP Server Configuration

This directory contains configurations related to Multi-Channel Platform (MCP) servers used by the Gemini CLI.

## `servers.json`

This file lists the MCP servers that the `scripts/register_mcp_servers.sh` script will attempt to register with the Gemini CLI based on the specified environment (`dev`, `prod`, etc.).

**Format:**

The file is a JSON object with top-level keys representing environments (`dev`, `prod`, etc.) and a special key `common`.

* **`common`**: An array of server objects that should be registered regardless of the environment.
* **`<environment_name>`** (e.g., `dev`, `prod`): An array of server objects specific to that environment.

Each **server object** has the following properties:

* `name` (string, required): A unique name for the server within Gemini CLI.
* `url` (string, required): The URL or file path pointing to the OpenAPI specification. Use `http://`, `https://`, or `file:///`. You can use `$(pwd)` within double quotes to reference the `gemini-hq` repo root, e.g., "file://$(pwd)/config/mcp/my-server/openapi.yaml".
* `description` (string, optional): A brief description.
* `auth` (object, optional): Authentication details mirroring `gemini mcp add` flags. Refer to `gemini mcp add --help` for options (`type`, `credential_source`, `key_name_in_file`, `api_key_env_var`, `scopes`, etc.).

The `register_mcp_servers.sh` script will load servers from `common` **and** the specified environment key.

**Example `servers.json`:**
```json
{
  "common": [
    {
      "name": "local_calculator",
      "url": "file://$(pwd)/config/mcp/example-mcp-server/openapi.yaml",
      "description": "Example calculator server (runs locally)"
    }
  ],
  "dev": [
    { "name": "dev_api", "url": "http://dev.api.local/spec" }
  ],
  "prod": [
    { "name": "prod_api", "url": "https://prod.api.public/spec", "auth": {"type": "api_key", "credential_source": "env_var", "api_key_env_var": "PROD_API_KEY"} }
  ]
}
```

## `example-mcp-server/`

Contains a basic Node.js calculator MCP server for demonstration.

  * To run: `node config/mcp/example-mcp-server/server.js`
  * Ensure it's listed under `common` in `servers.json` to be registered.

<!-- end list -->

