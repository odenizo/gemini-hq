#!/usr/bin/env python3
"""
Gemini CLI Authentication Fix Script
Repairs broken Gemini CLI authentication with automatic OAuth browser handling
Handles common auth failures and configuration issues
Cross-platform: macOS & Linux
"""

import os
import sys
import platform
import subprocess
import re
import time
import json
import webbrowser
import select
from pathlib import Path
from typing import Optional, Tuple, List

class Colors:
    """Terminal colors for better UX"""
    GREEN = '\033[92m'
    YELLOW = '\033[93m'
    RED = '\033[91m'
    BLUE = '\033[94m'
    CYAN = '\033[96m'
    BOLD = '\033[1m'
    END = '\033[0m'

class GeminiAuthFix:
    """Fixes Gemini CLI authentication issues with OAuth automation"""
    
    def __init__(self):
        self.os_name = platform.system()
        self.home_dir = Path.home()
        
        # Gemini config locations
        self.gemini_dir = self.home_dir / ".gemini"
        self.settings_file = self.gemini_dir / "settings.json"
        self.credentials_file = self.gemini_dir / "credentials.json"
        
        # Shell config
        self.shell_rc = self._detect_shell_rc()
        
        # Track issues found
        self.issues_found: List[str] = []
        self.fixes_applied: List[str] = []
    
    def _detect_shell_rc(self) -> Optional[Path]:
        """Detect shell configuration file"""
        candidates = [
            self.home_dir / ".zshrc",
            self.home_dir / ".bashrc",
            self.home_dir / ".bash_profile",
            self.home_dir / ".profile"
        ]
        for rc in candidates:
            if rc.exists():
                return rc
        return self.home_dir / ".bashrc"  # Default fallback
    
    def log(self, msg: str, level: str = "info"):
        """Colored logging"""
        icons = {
            "success": f"{Colors.GREEN}✓{Colors.END}",
            "error": f"{Colors.RED}✗{Colors.END}",
            "warning": f"{Colors.YELLOW}⚠{Colors.END}",
            "info": f"{Colors.BLUE}ℹ{Colors.END}",
            "fix": f"{Colors.CYAN}🔧{Colors.END}"
        }
        icon = icons.get(level, "")
        print(f"{icon} {msg}")
    
    def header(self, text: str):
        """Print section header"""
        print(f"\n{Colors.BOLD}{'─' * 70}{Colors.END}")
        print(f"{Colors.BOLD}{text}{Colors.END}")
        print(f"{Colors.BOLD}{'─' * 70}{Colors.END}\n")
    
    def run_cmd(self, cmd: List[str], capture=False, timeout=30, check=False) -> Tuple[bool, str]:
        """Execute command with error handling"""
        try:
            if capture:
                result = subprocess.run(
                    cmd,
                    capture_output=True,
                    text=True,
                    timeout=timeout
                )
                return result.returncode == 0, result.stdout.strip()
            else:
                result = subprocess.run(cmd, timeout=timeout, check=check)
                return result.returncode == 0, ""
        except subprocess.TimeoutExpired:
            return False, "Timeout"
        except subprocess.CalledProcessError as e:
            return False, str(e)
        except FileNotFoundError:
            return False, "Command not found"
        except Exception as e:
            return False, str(e)
    
    def diagnose_auth_issues(self) -> bool:
        """Diagnose current authentication problems"""
        self.header("DIAGNOSING AUTHENTICATION ISSUES")
        
        # Check 1: Gemini CLI installed
        success, version = self.run_cmd(["gemini", "--version"], capture=True)
        if not success:
            self.issues_found.append("gemini_cli_missing")
            self.log("Gemini CLI not found or not in PATH", "error")
        else:
            self.log(f"Gemini CLI found: {version}", "success")
        
        # Check 2: Conflicting API key
        if "GEMINI_API_KEY" in os.environ:
            self.issues_found.append("api_key_conflict")
            self.log("Found GEMINI_API_KEY in environment (conflicts with OAuth)", "warning")
        
        # Check 3: Corrupted config files
        if self.settings_file.exists():
            try:
                with open(self.settings_file) as f:
                    json.load(f)
                self.log(f"Config file valid: {self.settings_file}", "success")
            except json.JSONDecodeError:
                self.issues_found.append("corrupted_config")
                self.log(f"Config file corrupted: {self.settings_file}", "error")
        
        # Check 4: Missing credentials
        if not self.credentials_file.exists():
            self.issues_found.append("no_credentials")
            self.log("No credentials file found (needs OAuth login)", "warning")
        
        # Check 5: TERM variable
        if os.environ.get("TERM", "").lower() in ["dumb", ""]:
            self.issues_found.append("bad_term")
            self.log(f"TERM variable problematic: {os.environ.get('TERM', 'not set')}", "warning")
        
        # Check 6: Test basic command
        success, output = self.run_cmd(
            ["gemini", "test", "--model", "gemini-1.5-flash"],
            capture=True,
            timeout=15
        )
        if not success:
            self.issues_found.append("auth_failure")
            if output:
                lower = output.lower()
                if "invalid_argument" in lower or "400" in lower:
                    self.log("API returns INVALID_ARGUMENT (auth broken)", "error")
                elif "401" in lower or "unauthorized" in lower:
                    self.log("Authentication expired or invalid", "error")
                else:
                    self.log(f"Command test failed: {output[:100]}", "error")
            else:
                self.log("Command test failed (no output)", "error")
        else:
            self.log("Basic command test passed", "success")
        
        print(f"\n{Colors.BOLD}Found {len(self.issues_found)} issue(s){Colors.END}")
        return len(self.issues_found) > 0
    
    def fix_api_key_conflict(self):
        """Remove conflicting API key configuration"""
        self.header("FIX 1: Removing API Key Conflicts")
        
        if "GEMINI_API_KEY" in os.environ:
            del os.environ["GEMINI_API_KEY"]
            self.log("Removed GEMINI_API_KEY from current session", "fix")
        
        if self.shell_rc and self.shell_rc.exists():
            try:
                content = self.shell_rc.read_text()
                backup = self.shell_rc.with_suffix(f'{self.shell_rc.suffix}.backup')
                backup.write_text(content)
                new_content = re.sub(
                    r'^\s*export\s+GEMINI_API_KEY=.*$',
                    '',
                    content,
                    flags=re.MULTILINE
                )
                if new_content != content:
                    self.shell_rc.write_text(new_content)
                    self.fixes_applied.append("api_key_removed")
                    self.log(f"Removed API key from {self.shell_rc.name}", "fix")
                    self.log(f"Backup saved to {backup.name}", "info")
            except Exception as e:
                self.log(f"Could not modify {self.shell_rc}: {e}", "error")
    
    def fix_corrupted_config(self):
        """Reset corrupted configuration files"""
        self.header("FIX 2: Resetting Configuration")
        if self.settings_file.exists():
            backup = self.settings_file.with_suffix('.json.backup')
            try:
                backup.write_text(self.settings_file.read_text())
                self.log(f"Backed up settings to {backup.name}", "info")
            except Exception:
                pass
        self.gemini_dir.mkdir(parents=True, exist_ok=True)
        minimal_config = {"mcpServers": {}}
        try:
            with open(self.settings_file, 'w') as f:
                json.dump(minimal_config, f, indent=2)
            self.fixes_applied.append("config_reset")
            self.log(f"Created fresh config: {self.settings_file}", "fix")
        except Exception as e:
            self.log(f"Failed to write config: {e}", "error")
    
    def fix_term_variable(self):
        """Set proper TERM variable for colors"""
        self.header("FIX 3: Setting Terminal Type")
        os.environ["TERM"] = "xterm-256color"
        self.log("Set TERM=xterm-256color for this session", "fix")
        if self.shell_rc:
            try:
                content = self.shell_rc.read_text()
                term_line = 'export TERM=xterm-256color'
                if term_line not in content:
                    with open(self.shell_rc, 'a') as f:
                        f.write(f"\n# Gemini CLI color support\n{term_line}\n")
                    self.fixes_applied.append("term_set")
                    self.log(f"Added TERM to {self.shell_rc.name}", "fix")
                else:
                    self.log(f"TERM already configured in {self.shell_rc.name}", "info")
            except Exception as e:
                self.log(f"Could not modify {self.shell_rc}: {e}", "warning")
    
    def install_or_update_gemini(self) -> bool:
        """Install or update Gemini CLI"""
        self.header("FIX 4: Installing/Updating Gemini CLI")
        success, _ = self.run_cmd(["npm", "--version"], capture=True)
        if not success:
            self.log("npm not found. Install Node.js from https://nodejs.org/", "error")
            return False
        self.log("Installing @google/gemini-cli (this may take a minute)...", "info")
        success, output = self.run_cmd(
            ["npm", "install", "-g", "@google/gemini-cli"],
            capture=True,
            timeout=120
        )
        if success:
            self.fixes_applied.append("cli_installed")
            success_ver, version = self.run_cmd(["gemini", "--version"], capture=True)
            if success_ver:
                self.log(f"Gemini CLI ready: {version}", "fix")
            return True
        else:
            self.log(f"Installation failed: {output[:200] if output else 'unknown error'}", "error")
            return False
    
    def open_browser(self, url: str) -> bool:
        """Open URL in default browser (OS-specific)"""
        try:
            if self.os_name == "Darwin":
                subprocess.run(["open", url], check=True, timeout=5)
                self.log("Opened browser (macOS)", "success")
                return True
            elif self.os_name == "Linux":
                try:
                    subprocess.run(["xdg-open", url], check=True, timeout=5)
                    self.log("Opened browser (Linux)", "success")
                    return True
                except Exception:
                    webbrowser.open(url)
                    self.log("Opened browser (fallback)", "success")
                    return True
            else:
                webbrowser.open(url)
                self.log("Opened browser (generic)", "success")
                return True
        except Exception as e:
            self.log(f"Could not auto-open browser: {e}", "warning")
            self.log(f"Please manually open: {url}", "info")
            return False
    
    def perform_oauth_login(self) -> bool:
        """Execute OAuth login with browser automation"""
        self.header("FIX 5: Performing OAuth Login")
        self.log("Starting OAuth authentication flow...", "info")
        self.log("Your browser will open for Google login", "info")
        try:
            process = subprocess.Popen(
                ["gemini", "auth", "login"],
                stdout=subprocess.PIPE,
                stderr=subprocess.STDOUT,
                text=True,
                bufsize=1,
                universal_newlines=True
            )
            oauth_url = None
            url_pattern = re.compile(r'https://accounts\.google\.com[^\s]+')
            self.log("Monitoring for OAuth URL...", "info")
            start_time = time.time()
            timeout = 10
            while time.time() - start_time < timeout:
                if process.poll() is not None:
                    break
                try:
                    if sys.platform != 'win32':
                        ready, _, _ = select.select([process.stdout], [], [], 0.1)
                        if ready:
                            line = process.stdout.readline()
                        else:
                            continue
                    else:
                        line = process.stdout.readline()
                    if not line:
                        continue
                    print(f"  {line.rstrip()}")
                    match = url_pattern.search(line)
                    if match and not oauth_url:
                        oauth_url = match.group(0)
                        self.log("Found OAuth URL!", "success")
                        self.open_browser(oauth_url)
                        break
                except Exception as e:
                    self.log(f"Read error: {e}", "warning")
                    break
            if not oauth_url:
                self.log("Could not detect OAuth URL automatically", "warning")
                self.log("Please follow the prompts shown above", "info")
            self.log("Waiting for authentication to complete...", "info")
            self.log("(Complete the login in your browser, then return here)", "info")
            try:
                returncode = process.wait(timeout=120)
                if returncode == 0:
                    self.fixes_applied.append("oauth_completed")
                    self.log("OAuth authentication successful!", "fix")
                    if self.credentials_file.exists():
                        self.log(f"Credentials saved to {self.credentials_file}", "success")
                    return True
                else:
                    self.log("OAuth process returned error", "error")
                    return False
            except subprocess.TimeoutExpired:
                self.log("Authentication timed out (waited 2 minutes)", "error")
                process.kill()
                return False
        except FileNotFoundError:
            self.log("'gemini' command not found. Ensure it's installed and in PATH", "error")
            return False
        except Exception as e:
            self.log(f"OAuth login failed: {e}", "error")
            return False
    
    def test_authentication(self) -> bool:
        """Test if authentication is working"""
        self.header("VERIFICATION: Testing Authentication")
        models = [
            ("gemini-1.5-flash", "Gemini 1.5 Flash"),
            ("gemini-1.5-pro", "Gemini 1.5 Pro"),
            ("gemini-2.0-flash-exp", "Gemini 2.0 Flash (Experimental)"),
        ]
        working_model = None
        for model_id, model_name in models:
            self.log(f"Testing {model_name}...", "info")
            success, output = self.run_cmd(
                ["gemini", "Say 'working' if you can see this", "--model", model_id],
                capture=True,
                timeout=30
            )
            if success and output and len(output) > 5:
                self.log(f"✓ {model_name} is working!", "success")
                working_model = model_name
                preview = output[:150] + "..." if len(output) > 150 else output
                print(f"\n{Colors.CYAN}Response:{Colors.END}\n{preview}\n")
                break
            else:
                self.log(f"  {model_name} not available or failed", "warning")
        if working_model:
            self.log(f"Authentication verified with {working_model}!", "success")
            return True
        else:
            self.log("No models responded. Authentication may still need issues", "error")
            self.log("Try: gemini settings (to enable Preview Features)", "info")
            return False
    
    def run_fix(self) -> bool:
        """Execute complete authentication fix"""
        print(f"\n{Colors.BOLD}{Colors.GREEN}")
        print("╔" + "═" * 68 + "╗")
        print("║" + " " * 68 + "║")
        print("║" + "  GEMINI CLI AUTHENTICATION FIX".center(68) + "║")
        print("║" + "  Repair OAuth & Browser Handling".center(68) + "║")
        print("║" + f"  Platform: {self.os_name}".center(68) + "║")
        print("║" + " " * 68 + "║")
        print("╚" + "═" * 68 + "╝")
        print(f"{Colors.END}\n")
        try:
            has_issues = self.diagnose_auth_issues()
            if not has_issues:
                self.log("No authentication issues detected!", "success")
                self.log("Running verification test anyway...", "info")
                self.test_authentication()
                return True
            if "api_key_conflict" in self.issues_found:
                self.fix_api_key_conflict()
            if "corrupted_config" in self.issues_found:
                self.fix_corrupted_config()
            if "bad_term" in self.issues_found:
                self.fix_term_variable()
            if "gemini_cli_missing" in self.issues_found:
                if not self.install_or_update_gemini():
                    return False
            if "no_credentials" in self.issues_found or "auth_failure" in self.issues_found:
                if not self.perform_oauth_login():
                    self.log("OAuth login failed. Try manually: gemini auth login", "error")
                    return False
            success = self.test_authentication()
            self.header("FIX SUMMARY")
            print(f"{Colors.BOLD}Issues found:{Colors.END} {len(self.issues_found)}")
            print(f"{Colors.BOLD}Fixes applied:{Colors.END} {len(self.fixes_applied)}")
            if success:
                self.log("\n🎉 Authentication is now working!", "success")
                self.log("You can use: gemini \"your prompt here\"", "info")
                self.log("For settings: gemini settings", "info")
            else:
                self.log("\n⚠ Authentication may still need attention", "warning")
                self.log("Try running: gemini auth login", "info")
                self.log("Or check: gemini settings", "info")
            return success
        except KeyboardInterrupt:
            print(f"\n\n{Colors.YELLOW}Fix interrupted by user{Colors.END}")
            return False
        except Exception as e:
            self.log(f"Unexpected error during fix: {e}", "error")
            return False

def main():
    """Main entry point"""
    if sys.version_info < (3, 7):
        print("Error: Python 3.7+ required")
        sys.exit(1)
    if platform.system() not in ["Darwin", "Linux"]:
        print(f"Warning: This script is designed for macOS/Linux. Your platform: {platform.system()}")
        response = input("Continue anyway? (y/N): ")
        if response.lower() != 'y':
            sys.exit(0)
    fixer = GeminiAuthFix()
    success = fixer.run_fix()
    sys.exit(0 if success else 1)

if __name__ == "__main__":
    main()
