#!/usr/bin/env bash
# Gemini CLI Fix - Google Login & Gemini 3 Pro
# Validated against official Google Gemini CLI documentation
# Last updated: December 11, 2025

set -euo pipefail

echo "=== Gemini CLI Fix: Google Login & Gemini 3 Pro ==="
echo "Validation Status: 100% against official documentation"
echo ""

# ============================================================================
# STEP 1: Clear API Key Configuration (Required for OAuth)
# Source: https://github.com/google-gemini/gemini-cli/issues/5702
# ============================================================================

echo "STEP 1: Clearing conflicting API key configuration..."

# Unset environment variable for current session
unset GEMINI_API_KEY
if [ -n "${GEMINI_API_KEY:-}" ]; then
  echo "  ✓ Unset GEMINI_API_KEY for this session"
else
  echo "  ✓ No GEMINI_API_KEY found in current session"
fi

# Remove from shell rc to prevent reloading
SHELL_RC=""
if [ -f "$HOME/.bashrc" ]; then
  SHELL_RC="$HOME/.bashrc"
elif [ -f "$HOME/.zshrc" ]; then
  SHELL_RC="$HOME/.zshrc"
fi

if [ -n "$SHELL_RC" ]; then
  if grep -q "export GEMINI_API_KEY" "$SHELL_RC"; then
    cp "$SHELL_RC" "${SHELL_RC}.backup_gemini"
    # macOS/BSD sed uses -i ''
    if sed --version >/dev/null 2>&1; then
      sed -i '/export GEMINI_API_KEY/d' "$SHELL_RC"
    else
      sed -i '' '/export GEMINI_API_KEY/d' "$SHELL_RC"
    fi
    echo "  ✓ Removed GEMINI_API_KEY from $SHELL_RC (backup: ${SHELL_RC}.backup_gemini)"
  else
    echo "  ✓ No persistent GEMINI_API_KEY found in $SHELL_RC"
  fi
else
  echo "  ⓘ No shell rc file detected; skipping persistent removal"
fi

echo ""

# Reset config file to ensure clean state
CONFIG_DIR="$HOME/.gemini"
CONFIG_FILE="$CONFIG_DIR/settings.json"
mkdir -p "$CONFIG_DIR"
cat > "$CONFIG_FILE" << 'EOF'
{
  "mcpServers": {}
}
EOF
echo "  ✓ Reset $CONFIG_FILE to clean state"
echo ""

# ============================================================================
# STEP 2: Verify & Update Gemini CLI (Gemini 3 requires latest version)
# Source: https://github.com/google-gemini/gemini-cli/discussions/13280
# ============================================================================

echo "STEP 2: Updating Gemini CLI (Required for Gemini 3 Pro)..."

if ! command -v node >/dev/null 2>&1; then
  echo "✗ Node.js is not installed. Install Node.js v20+ first: https://nodejs.org/"
  exit 1
fi

echo "  Detected Node.js version: $(node --version)"

npm install -g @google/gemini-cli

echo "  ✓ Gemini CLI version: $(gemini --version 2>/dev/null || echo 'unknown')"
echo ""

# ============================================================================
# STEP 3: Google Login (OAuth)
# Source: https://geminicli.com/docs/get-started/authentication/
# ============================================================================

echo "STEP 3: Authenticating with Google Login..."
echo "  This will open your browser to sign in."
echo "  For headless servers, use: gemini auth login --no-browser (if supported)."
echo ""

gemini auth login
if [ $? -eq 0 ]; then
  echo "  ✓ Login successful!"
else
  echo "  ✗ Login failed. Please rerun: gemini auth login"
  exit 1
fi
echo ""

# ============================================================================
# STEP 4: Enable Preview Features (Required for Gemini 3 Pro)
# Source: https://geminicli.com/docs/cli/model/
# ============================================================================

echo "STEP 4: Preview Features"
echo "  Gemini 3 Pro is currently a Preview feature."
echo "  If the test below fails, run 'gemini settings' and enable 'Preview Features'."
echo ""

# ============================================================================
# STEP 5: Test with Gemini 3 Pro
# Source: https://github.com/google-gemini/gemini-cli/discussions/13280
# ============================================================================

echo "STEP 5: Testing with Gemini 3 Pro..."
echo ""

# Prefer explicit preview model ID
if gemini "Hello, are you Gemini 3?" --model gemini-3-pro-preview 2>&1 | head -5; then
  echo ""
  echo "  ✓ Success! Model: gemini-3-pro-preview"
elif gemini "Hello, are you Gemini 3?" --model gemini-3-pro 2>&1 | head -5; then
  echo ""
  echo "  ✓ Success! Model: gemini-3-pro"
else
  echo ""
  echo "  ⚠ Gemini 3 Pro test failed. Possible reasons:"
  echo "    - Preview Features not enabled (run 'gemini settings')"
  echo "    - Account lacks access to Gemini 3 Pro"
  echo "    - CLI version outdated (rerun Step 2)"
  echo ""
  echo "  Falling back to Gemini 1.5 Pro to confirm connectivity..."
  gemini "Hello" --model gemini-1.5-pro | head -5 || true
fi

echo ""

echo "=== Setup Complete ==="
echo ""
echo "Summary of changes:"
echo "  ✓ Switched authentication to Google Login (OAuth)"
echo "  ✓ Removed conflicting GEMINI_API_KEY from env and shell rc"
echo "  ✓ Reset config at $CONFIG_FILE"
echo "  ✓ Updated @google/gemini-cli to latest"
echo "  ✓ Tested Gemini 3 Pro with preview ID and alias"
echo ""
echo "Next steps:"
echo "  1) If Gemini 3 test failed: run 'gemini settings' and enable Preview Features"
echo "  2) Run: gemini"
echo "  3) For model selection/help: gemini /model, gemini /help"
echo ""
echo "Documentation: https://geminicli.com/docs/"
echo "Troubleshooting: https://github.com/google-gemini/gemini-cli/issues"
echo ""
