# Gemini HQ - Automated Gemini CLI Setup

This repository provides scripts and configuration templates to automate the installation, configuration, and management of the Google Gemini CLI (`@google/gemini-cli`) on a Linux-based environment.

**Features:**

* Automated installation of a specific Gemini CLI version.
* Environment support (e.g., `dev`, `prod`) for configuration overrides.
* Configuration templates for core settings, profiles, and credentials.
* Automated registration and health checks for MCP servers defined in `config/mcp/servers.json`.
* Scripts for backing up and restoring the `~/.gemini` configuration directory.
* Script for managing trusted folders.
* Example custom command included.

## Prerequisites

* A Linux environment (VM, container, etc.) with `bash`, `curl`, `node`, and `npm` installed.
* A Google AI Studio API Key or appropriate GCP Application Default Credentials (ADC) for authentication.
* (Required for MCP/Health Check scripts) `jq` installed (`sudo apt install jq` or `brew install jq`).
* (Optional for Health Check script) `curl` installed.

## Setup Steps

1.  **Clone the Repository:**
    ```bash
    git clone <repository_url> gemini-hq
    cd gemini-hq
    ```

2.  **Configure Credentials:**
    * Copy the credentials template:
        ```bash
        cp config/gemini/credentials.yaml.template config/gemini/credentials.yaml
        ```
    * Edit `config/gemini/credentials.yaml` and add your authentication details (API Key or configure ADC).
    * **Security:** Treat `credentials.yaml` securely. Add it to `.gitignore` if needed.

3.  **Configure Environment (Optional):**
    * Review/modify the base configuration in `config/gemini/config.yaml` and `profiles.yaml`.
    * Add environment-specific overrides in `config/gemini/env/dev/config.yaml` or `config/gemini/env/prod/config.yaml` if needed.

4.  **Configure MCP Servers (Optional):**
    * Edit `config/mcp/servers.json`. Define servers, optionally specifying different URLs or details per environment (`dev`/`prod`). See `config/mcp/README.md`.

5.  **Configure Trusted Folders (Optional):**
    * Edit `config/gemini/trusted_folders.json` to list absolute paths you want to mark as trusted for filesystem/shell tools.

6.  **Run Setup Script:**
    Make the setup script executable and run it, specifying the target environment (defaults to `dev`):
    ```bash
    chmod +x setup-gemini.sh
    # For development environment
    ./setup-gemini.sh dev
    # For production environment
    # ./setup-gemini.sh prod
    ```
    This script will:
    * Install/update Gemini CLI to the version specified within the script.
    * Create `~/.gemini` directories.
    * Copy base configs, applying environment overrides if found.
    * Copy your `credentials.yaml`.
    * Copy custom commands.

7.  **Register MCP Servers (Optional):**
    ```bash
    chmod +x scripts/register_mcp_servers.sh
    ./scripts/register_mcp_servers.sh dev # Or 'prod'
    ```

8.  **Set Trusted Folders (Optional):**
    ```bash
    chmod +x scripts/manage_trusted_folders.sh
    ./scripts/manage_trusted_folders.sh add # Reads from config/gemini/trusted_folders.json
    # Or ./scripts/manage_trusted_folders.sh remove
    ```

## Usage

* **Interactive Chat:** `gemini`
* **Run Headless:** Use `scripts/run_gemini.sh` (make executable) or `gemini` directly with flags.
    ```bash
    ./scripts/run_gemini.sh --profile coder --prompt "Explain..." @file.py
    ```
* **Use Custom Command:** `/custom/example Explain quantum computing.`
* **Check MCP Health:** `chmod +x scripts/health_check.sh && ./scripts/health_check.sh dev` (or `prod`)

## Management Scripts

* **Backup Config:** `chmod +x scripts/backup_config.sh && ./scripts/backup_config.sh <backup_dir_path>`
* **Restore Config:** `chmod +x scripts/restore_config.sh && ./scripts/restore_config.sh <path_to_backup.tar.gz>`

## Configuration Files

* `config/gemini/config.yaml`: Base configuration.
* `config/gemini/profiles.yaml`: Profile definitions.
* `config/gemini/credentials.yaml`: **Keep secure.**
* `config/gemini/trusted_folders.json`: List of trusted paths.
* `config/gemini/env/<env>/config.yaml`: Environment-specific overrides.
* `config/mcp/servers.json`: MCP server definitions (supports environment keys).
* `commands/custom/example-command.toml`: Example custom command.
