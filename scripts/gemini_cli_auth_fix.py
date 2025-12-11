#!/usr/bin/env python3
"""
Gemini CLI Authentication Fix - CORRECTED VERSION
Repairs Gemini CLI authentication based on OFFICIAL Google Gemini CLI docs
Validated against: https://geminicli.com/docs/get-started/authentication/
https://github.com/google-gemini/gemini-cli

Handles:
- API key conflicts removal
- Configuration reset
- Interactive OAuth login with browser support
- Debug mode fallback for headless environments
"""

import os
import sys
import platform
import subprocess
import re
import time
import json
from pathlib import Path
from typing import Optional, Tuple, List

class Colors:
    GREEN = '\033[92m'
    YELLOW = '\033[93m'
    RED = '\033[91m'
    BLUE = '\033[94m'
    CYAN = '\033[96m'
    BOLD = '\033[1m'
    END = '\033[0m'

class GeminiAuthFixCorrected:
    """Corrected Gemini CLI auth fix based on official documentation"""
    
    def __init__(self):
        self.os_name = platform.system()
        self.home_dir = Path.home()
        self.gemini_dir = self.home_dir / ".gemini"
        self.settings_file = self.gemini_dir / "settings.json"
        self.shell_rc = self._detect_shell_rc()
        self.issues: List[str] = []
        self.fixes: List[str] = []
    
    def _detect_shell_rc(self) -> Path:
        """Detect shell config file"""
        for rc in [self.home_dir / ".zshrc", self.home_dir / ".bashrc"]:
            if rc.exists():
                return rc
        return self.home_dir / ".bashrc"
    
    def log(self, msg: str, level: str = "info"):
        """Colored output"""
        icons = {
            "success": f"{Colors.GREEN}✓{Colors.END}",
            "error": f"{Colors.RED}✗{Colors.END}",
            "warning": f"{Colors.YELLOW}⚠{Colors.END}",
            "info": f"{Colors.BLUE}ℹ{Colors.END}",
            "fix": f"{Colors.CYAN}🔧{Colors.END}"
        }
        print(f"{icons.get(level, '')} {msg}")
    
    def header(self, text: str):
        """Section header"""
        print(f"\n{Colors.BOLD}{'─' * 70}{Colors.END}")
        print(f"{Colors.BOLD}{text}{Colors.END}")
        print(f"{Colors.BOLD}{'─' * 70}{Colors.END}\n")
    
    def run_cmd(self, cmd: List[str], capture=False, timeout=30) -> Tuple[bool, str]:
        """Execute command"""
        try:
            if capture:
                result = subprocess.run(cmd, capture_output=True, text=True, timeout=timeout)
                return result.returncode == 0, result.stdout.strip()
            else:
                result = subprocess.run(cmd, timeout=timeout)
                return result.returncode == 0, ""
        except Exception:
            return False, ""
    
    def diagnose(self) -> bool:
        """Diagnose authentication issues"""
        self.header("DIAGNOSIS: Checking Gemini CLI Configuration")
        
        success, version = self.run_cmd(["gemini", "--version"], capture=True)
        if not success:
            self.issues.append("cli_not_found")
            self.log("Gemini CLI not installed", "error")
            return False
        else:
            self.log(f"Gemini CLI installed: {version}", "success")
        
        if "GEMINI_API_KEY" in os.environ or "GOOGLE_API_KEY" in os.environ:
            self.issues.append("api_key_conflict")
            self.log("Found conflicting API key (prevents OAuth)", "warning")
        
        if self.settings_file.exists():
            try:
                with open(self.settings_file) as f:
                    settings = json.load(f)
                    if settings.get("selectedAuthType") == "oauth-personal":
                        self.log("OAuth already configured", "success")
                    else:
                        self.issues.append("needs_oauth_login")
                        self.log(f"Auth type: {settings.get('selectedAuthType', 'not set')}", "info")
            except Exception:
                self.issues.append("corrupted_config")
                self.log("Settings file corrupted", "error")
        else:
            self.issues.append("needs_oauth_login")
            self.log("No settings file (first run)", "warning")
        
        self.log("Testing authentication...", "info")
        success, output = self.run_cmd(
            ["gemini", "test", "--model", "gemini-1.5-flash"],
            capture=True,
            timeout=15
        )
        if success and output:
            self.log("Authentication working", "success")
            return False
        else:
            self.issues.append("auth_failed")
            self.log("Authentication test failed", "error")
            return True
    
    def fix_api_key_conflict(self):
        """Remove conflicting API keys"""
        self.header("FIX 1: Removing API Key Conflicts")
        for key in ["GEMINI_API_KEY", "GOOGLE_API_KEY"]:
            if key in os.environ:
                del os.environ[key]
                self.log(f"Removed {key} from environment", "fix")
        if self.shell_rc.exists():
            try:
                content = self.shell_rc.read_text()
                new_content = re.sub(
                    r'^\s*export\s+(GEMINI_API_KEY|GOOGLE_API_KEY)=.*$',
                    '',
                    content,
                    flags=re.MULTILINE
                )
                if new_content != content:
                    backup = self.shell_rc.with_suffix('.backup')
                    backup.write_text(content)
                    self.shell_rc.write_text(new_content)
                    self.fixes.append("api_key_removed")
                    self.log(f"Removed from {self.shell_rc.name} (backed up)", "fix")
            except Exception as e:
                self.log(f"Could not modify shell config: {e}", "warning")
    
    def fix_config(self):
        """Reset configuration to minimal valid state"""
        self.header("FIX 2: Resetting Configuration")
        if self.settings_file.exists():
            backup = self.settings_file.with_suffix('.json.backup')
            try:
                backup.write_text(self.settings_file.read_text())
                self.log(f"Backed up to {backup.name}", "info")
            except Exception:
                pass
        self.gemini_dir.mkdir(parents=True, exist_ok=True)
        minimal = {"mcpServers": {}}
        try:
            with open(self.settings_file, 'w') as f:
                json.dump(minimal, f, indent=2)
            self.fixes.append("config_reset")
            self.log(f"Created fresh config: {self.settings_file}", "fix")
        except Exception as e:
            self.log(f"Could not write config: {e}", "error")
    
    def perform_oauth_login(self) -> bool:
        """Perform OAuth login - CORRECTED approach"""
        self.header("FIX 3: Performing OAuth Login")
        self.log("Starting Gemini CLI with OAuth...", "info")
        self.log("This will open an interactive menu for you to select 'Login with Google'", "info")
        print()
        try:
            process = subprocess.Popen(
                ["gemini"],
                stdin=subprocess.PIPE,
                stdout=subprocess.PIPE,
                stderr=subprocess.STDOUT,
                text=True,
                bufsize=1
            )
            for line in iter(process.stdout.readline, ''):
                if line:
                    print(f"  {line.rstrip()}")
                    if "login" in line.lower() or "google" in line.lower():
                        break
            try:
                process.stdin.write("1\n")
                process.stdin.flush()
            except Exception:
                pass
            self.log("Waiting for browser authentication (120 seconds timeout)...", "info")
            self.log("If browser doesn't open, try: gemini --debug", "info")
            try:
                returncode = process.wait(timeout=120)
                if returncode == 0:
                    self.fixes.append("oauth_completed")
                    self.log("\n✓ OAuth authentication successful!", "success")
                    time.sleep(1)
                    if self.settings_file.exists():
                        try:
                            with open(self.settings_file) as f:
                                settings = json.load(f)
                                if "selectedAuthType" in settings:
                                    self.log(f"Auth type: {settings['selectedAuthType']}", "success")
                        except Exception:
                            pass
                    return True
                else:
                    self.log(f"Process exited with code {returncode}", "error")
                    return False
            except subprocess.TimeoutExpired:
                self.log("Authentication timed out", "error")
                process.kill()
                self.log("\nManual OAuth login needed:", "warning")
                self.log("Run: gemini --debug", "info")
                self.log("Copy the URL shown to your browser", "info")
                return False
        except FileNotFoundError:
            self.log("Gemini CLI not found", "error")
            return False
        except Exception as e:
            self.log(f"Error during OAuth: {e}", "error")
            return False
    
    def test_auth(self) -> bool:
        """Test if authentication is working"""
        self.header("VERIFICATION: Testing Authentication")
        models = [
            ("gemini-1.5-flash", "Gemini 1.5 Flash"),
            ("gemini-1.5-pro", "Gemini 1.5 Pro"),
        ]
        for model_id, name in models:
            self.log(f"Testing {name}...", "info")
            success, output = self.run_cmd(
                ["gemini", "Hello from authentication test", "--model", model_id],
                capture=True,
                timeout=30
            )
            if success and output:
                self.log(f"✓ {name} working!", "success")
                print(f"\nResponse preview: {output[:100]}...\n")
                return True
            else:
                self.log(f"  {name} not available", "warning")
        self.log("No models responded", "error")
        return False
    
    def run_all_fixes(self) -> bool:
        """Execute complete fix"""
        print(f"\n{Colors.BOLD}{Colors.GREEN}")
        print("╔" + "═" * 68 + "╗")
        print("║ GEMINI CLI AUTHENTICATION FIX (OFFICIAL DOCS VALIDATED)".center(70) + "║")
        print("║" + f" Platform: {self.os_name}".ljust(69) + "║")
        print("╚" + "═" * 68 + "╝")
        print(f"{Colors.END}\n")
        try:
            has_issues = self.diagnose()
            if not has_issues:
                self.log("No issues detected! Running verification...", "info")
                self.test_auth()
                return True
            if "api_key_conflict" in self.issues:
                self.fix_api_key_conflict()
            if "corrupted_config" in self.issues:
                self.fix_config()
            if "needs_oauth_login" in self.issues or "auth_failed" in self.issues:
                if not self.perform_oauth_login():
                    self.log("OAuth login failed. Try manually: gemini --debug", "error")
                    return False
            success = self.test_auth()
            self.header("SUMMARY")
            self.log(f"Issues found: {len(self.issues)}", "info")
            self.log(f"Fixes applied: {len(self.fixes)}", "info")
            if success:
                self.log("\n✓ Authentication is working!", "success")
                self.log("Use: gemini \"your prompt here\"", "info")
            else:
                self.log("\n⚠ Authentication needs manual steps", "warning")
                self.log("Run: gemini --debug", "info")
                self.log("Then follow the URL shown in terminal", "info")
            return success
        except KeyboardInterrupt:
            self.log("\n\nInterrupted by user", "warning")
            return False
        except Exception as e:
            self.log(f"Error: {e}", "error")
            return False

def main():
    """Main entry point"""
    if sys.version_info < (3, 7):
        print("Error: Python 3.7+ required")
        sys.exit(1)
    fixer = GeminiAuthFixCorrected()
    success = fixer.run_all_fixes()
    sys.exit(0 if success else 1)

if __name__ == "__main__":
    main()
