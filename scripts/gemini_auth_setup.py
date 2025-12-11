#!/usr/bin/env python3
"""
Gemini CLI Authentication Repair Script
Cross-platform OAuth setup with automatic browser handling
Supports: macOS and Linux
Author: Generated from validated documentation
"""

import os
import sys
import platform
import subprocess
import re
import time
import json
import webbrowser
from pathlib import Path
from typing import Optional, Tuple

class Colors:
    """ANSI color codes for terminal output"""
    GREEN = '\033[92m'
    YELLOW = '\033[93m'
    RED = '\033[91m'
    BLUE = '\033[94m'
    BOLD = '\033[1m'
    END = '\033[0m'

class GeminiAuthSetup:
    """Handles Gemini CLI authentication setup with OAuth browser automation"""
    
    def __init__(self):
        self.os_name = platform.system()
        self.home_dir = Path.home()
        self.gemini_config_dir = self.home_dir / ".gemini"
        self.settings_file = self.gemini_config_dir / "settings.json"
        self.shell_rc = self._detect_shell_rc()
        
    def _detect_shell_rc(self) -> Optional[Path]:
        """Detect the user's shell configuration file"""
        candidates = [
            self.home_dir / ".zshrc",
            self.home_dir / ".bashrc",
            self.home_dir / ".bash_profile",
        ]
        for rc in candidates:
            if rc.exists():
                return rc
        return None
    
    def print_header(self, text: str):
        """Print formatted section header"""
        print(f"\n{Colors.BOLD}{'=' * 70}{Colors.END}")
        print(f"{Colors.BOLD}{text}{Colors.END}")
        print(f"{Colors.BOLD}{'=' * 70}{Colors.END}\n")
    
    def print_success(self, text: str):
        """Print success message"""
        print(f"{Colors.GREEN}✓ {text}{Colors.END}")
    
    def print_error(self, text: str):
        """Print error message"""
        print(f"{Colors.RED}✗ {text}{Colors.END}")
    
    def print_warning(self, text: str):
        """Print warning message"""
        print(f"{Colors.YELLOW}⚠ {text}{Colors.END}")
    
    def print_info(self, text: str):
        """Print info message"""
        print(f"{Colors.BLUE}ℹ {text}{Colors.END}")
    
    def run_command(self, cmd: list, capture_output=False, timeout=30) -> Tuple[bool, str]:
        """Run shell command with error handling"""
        try:
            if capture_output:
                result = subprocess.run(
                    cmd,
                    capture_output=True,
                    text=True,
                    timeout=timeout
                )
                return result.returncode == 0, result.stdout
            else:
                result = subprocess.run(cmd, timeout=timeout)
                return result.returncode == 0, ""
        except subprocess.TimeoutExpired:
            return False, "Command timed out"
        except Exception as e:
            return False, str(e)
    
    def step1_clear_api_key(self):
        """Step 1: Remove conflicting API key configuration"""
        self.print_header("STEP 1: Clearing API Key Configuration")
        
        # Unset for current session
        if "GEMINI_API_KEY" in os.environ:
            del os.environ["GEMINI_API_KEY"]
            self.print_success("Unset GEMINI_API_KEY for current session")
        
        # Remove from shell config
        if self.shell_rc and self.shell_rc.exists():
            try:
                content = self.shell_rc.read_text()
                backup_file = self.shell_rc.with_suffix('.backup_gemini')
                backup_file.write_text(content)
                new_content = re.sub(
                    r'export\s+GEMINI_API_KEY=.*\n?',
                    '',
                    content
                )
                if new_content != content:
                    self.shell_rc.write_text(new_content)
                    self.print_success(f"Removed GEMINI_API_KEY from {self.shell_rc}")
                else:
                    self.print_info(f"No GEMINI_API_KEY found in {self.shell_rc}")
            except Exception as e:
                self.print_error(f"Failed to modify {self.shell_rc}: {e}")
        
        # Reset config file
        self.gemini_config_dir.mkdir(parents=True, exist_ok=True)
        try:
            with open(self.settings_file, 'w') as f:
                json.dump({"mcpServers": {}}, f, indent=2)
            self.print_success(f"Reset {self.settings_file}")
        except Exception as e:
            self.print_error(f"Failed to reset settings: {e}")
    
    def step2_install_gemini_cli(self):
        """Step 2: Install/Update Gemini CLI"""
        self.print_header("STEP 2: Installing Gemini CLI")
        success, version = self.run_command(["node", "--version"], capture_output=True)
        if not success:
            self.print_error("Node.js not found. Please install Node.js v20+ first")
            self.print_info("Visit: https://nodejs.org/")
            return False
        self.print_info(f"Node.js version: {version.strip()}")
        self.print_info("Installing @google/gemini-cli...")
        success, _ = self.run_command(["npm", "install", "-g", "@google/gemini-cli"], timeout=120)
        if success:
            success_ver, version = self.run_command(["gemini", "--version"], capture_output=True)
            if success_ver:
                self.print_success(f"Gemini CLI installed: {version.strip()}")
            else:
                self.print_success("Gemini CLI installed")
            return True
        else:
            self.print_error("Failed to install Gemini CLI")
            return False
    
    def step3_set_term(self):
        """Step 3: Set TERM environment variable for colors"""
        self.print_header("STEP 3: Configuring Terminal")
        os.environ["TERM"] = "xterm-256color"
        self.print_success("Set TERM=xterm-256color for this session")
        if self.shell_rc:
            try:
                content = self.shell_rc.read_text()
                term_export = 'export TERM=xterm-256color\n'
                if term_export.strip() not in content:
                    with open(self.shell_rc, 'a') as f:
                        f.write(f"\n{term_export}")
                    self.print_success(f"Added to {self.shell_rc}")
                else:
                    self.print_info(f"Already configured in {self.shell_rc}")
            except Exception as e:
                self.print_warning(f"Could not modify {self.shell_rc}: {e}")
    
    def open_url_in_browser(self, url: str) -> bool:
        """Open URL in default browser (OS-specific)"""
        try:
            if self.os_name == "Darwin":
                subprocess.run(["open", url], check=True)
                self.print_success("Opened browser (macOS)")
                return True
            elif self.os_name == "Linux":
                try:
                    subprocess.run(["xdg-open", url], check=True)
                    self.print_success("Opened browser (Linux - xdg-open)")
                    return True
                except Exception:
                    webbrowser.open(url)
                    self.print_success("Opened browser (Python fallback)")
                    return True
            else:
                webbrowser.open(url)
                self.print_success("Opened browser (generic)")
                return True
        except Exception as e:
            self.print_warning(f"Could not auto-open browser: {e}")
            self.print_info(f"Please open this URL manually: {url}")
            return False
    
    def step4_oauth_login(self):
        """Step 4: Execute OAuth login with browser automation"""
        self.print_header("STEP 4: Google OAuth Login")
        self.print_info("Starting OAuth flow...")
        self.print_info("This will open your browser for authentication")
        try:
            process = subprocess.Popen(
                ["gemini", "auth", "login"],
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True,
                bufsize=1
            )
            url_found = False
            url_pattern = re.compile(r'https?://[^\s]+')
            start_time = time.time()
            timeout = 10
            while time.time() - start_time < timeout:
                line = process.stdout.readline()
                if not line:
                    break
                print(line.strip())
                match = url_pattern.search(line)
                if match and not url_found:
                    url = match.group(0)
                    self.print_info(f"Found OAuth URL: {url[:50]}...")
                    self.open_url_in_browser(url)
                    url_found = True
            if not url_found:
                self.print_warning("Could not auto-detect OAuth URL")
                self.print_info("Please follow the prompts in the terminal")
            self.print_info("Waiting for you to complete authentication in browser...")
            self.print_info("(Timeout: 120 seconds)")
            try:
                process.wait(timeout=120)
                if process.returncode == 0:
                    self.print_success("OAuth login completed!")
                    return True
                else:
                    self.print_error("OAuth login failed")
                    return False
            except subprocess.TimeoutExpired:
                self.print_error("Authentication timed out")
                process.kill()
                return False
        except Exception as e:
            self.print_error(f"OAuth login failed: {e}")
            return False
    
    def step5_test_gemini_3(self):
        """Step 5: Test with Gemini 3 Pro models"""
        self.print_header("STEP 5: Testing Gemini Models")
        models_to_try = [
            ("gemini-3-pro-preview", "Gemini 3 Pro (Preview)"),
            ("gemini-3-pro", "Gemini 3 Pro"),
            ("gemini-1.5-pro", "Gemini 1.5 Pro (Fallback)"),
        ]
        for model_id, model_name in models_to_try:
            self.print_info(f"Testing {model_name}...")
            success, output = self.run_command(
                ["gemini", "Hello, are you working?", "--model", model_id],
                capture_output=True,
                timeout=30
            )
            if success and output:
                self.print_success(f"{model_name} is working!")
                preview = output[:200] + "..." if len(output) > 200 else output
                print(f"\n{Colors.BLUE}Response preview:{Colors.END}\n{preview}\n")
                return True
            else:
                self.print_warning(f"{model_name} not available")
        self.print_error("No Gemini models responded")
        self.print_info("Try enabling 'Preview Features' with: gemini settings")
        return False
    
    def step6_validate_config(self):
        """Step 6: Validate configuration"""
        self.print_header("STEP 6: Configuration Validation")
        checks_passed = 0
        total_checks = 3
        if self.settings_file.exists():
            try:
                with open(self.settings_file) as f:
                    json.load(f)
                self.print_success(f"Config file valid: {self.settings_file}")
                checks_passed += 1
            except json.JSONDecodeError:
                self.print_error(f"Config file has JSON errors: {self.settings_file}")
        else:
            self.print_warning(f"Config file not found: {self.settings_file}")
        if os.environ.get("TERM") == "xterm-256color":
            self.print_success("TERM is set to xterm-256color")
            checks_passed += 1
        else:
            self.print_warning(f"TERM is: {os.environ.get('TERM', 'not set')}")
        success, _ = self.run_command(["gemini", "--version"], capture_output=True)
        if success:
            self.print_success("Gemini CLI is accessible")
            checks_passed += 1
        else:
            self.print_error("Gemini CLI not found in PATH")
        print(f"\n{Colors.BOLD}Validation: {checks_passed}/{total_checks} checks passed{Colors.END}")
        return checks_passed == total_checks
    
    def run_setup(self):
        """Execute all setup steps"""
        print(f"\n{Colors.BOLD}{Colors.GREEN}")
        print("=" * 70)
        print("  Gemini CLI Authentication Repair")
        print("  Cross-Platform OAuth Setup with Browser Automation")
        print(f"  Platform: {self.os_name}")
        print("=" * 70)
        print(f"{Colors.END}\n")
        try:
            self.step1_clear_api_key()
            if not self.step2_install_gemini_cli():
                return False
            self.step3_set_term()
            if not self.step4_oauth_login():
                self.print_error("Authentication failed. Please try running: gemini auth login")
                return False
            self.step5_test_gemini_3()
            self.step6_validate_config()
            self.print_header("Setup Complete!")
            self.print_success("Gemini CLI is configured with OAuth authentication")
            self.print_info("You can now use: gemini \"your prompt here\"")
            self.print_info("For settings: gemini settings")
            self.print_info("For help: gemini --help")
            return True
        except KeyboardInterrupt:
            print(f"\n\n{Colors.YELLOW}Setup interrupted by user{Colors.END}")
            return False
        except Exception as e:
            self.print_error(f"Unexpected error: {e}")
            import traceback
            traceback.print_exc()
            return False

def main():
    """Main entry point"""
    if sys.version_info < (3, 7):
        print("Error: Python 3.7 or higher is required")
        sys.exit(1)
    setup = GeminiAuthSetup()
    success = setup.run_setup()
    sys.exit(0 if success else 1)

if __name__ == "__main__":
    main()
