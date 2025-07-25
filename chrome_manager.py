#!/usr/bin/env python3
"""
Chrome Manager for Standalone Chrome Instance

This module provides programmatic control over a standalone Chrome instance
for the GoogleRecaptchaBypass project. It handles Chrome startup, shutdown,
and status checking.
"""

import os
import sys
import time
import json
import subprocess
import requests
from pathlib import Path
from typing import Optional, Dict, Any
import logging

# Configure logging
logging.basicConfig(level=logging.INFO,
                    format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)


class ChromeManager:
    """Manages a standalone Chrome instance for the project."""

    def __init__(self, project_dir: Optional[str] = None):
        """
        Initialize the Chrome manager.

        Args:
            project_dir: Path to the project directory. Defaults to current directory.
        """
        self.project_dir = Path(project_dir) if project_dir else Path.cwd()
        self.chrome_dir = self.project_dir / "chrome"
        self.chrome_exec = self.chrome_dir / "chrome"
        self.user_data_dir = self.project_dir / "chrome_user_data"
        self.debug_port = 9222
        self.process = None

    def is_chrome_installed(self) -> bool:
        """
        Check if standalone Chrome is installed.

        Returns:
            True if Chrome executable exists, False otherwise.
        """
        return self.chrome_exec.exists() or self.chrome_exec.is_symlink()

    def get_chrome_path(self) -> Optional[str]:
        """
        Get the path to the Chrome executable.

        Returns:
            Path to Chrome executable or None if not found.
        """
        if self.is_chrome_installed():
            if self.chrome_exec.is_symlink():
                return str(self.chrome_exec.resolve())
            return str(self.chrome_exec)
        return None

    def is_chrome_running(self) -> bool:
        """
        Check if Chrome is running on the debug port.

        Returns:
            True if Chrome is running, False otherwise.
        """
        try:
            response = requests.get(
                f"http://localhost:{self.debug_port}/json/version", timeout=2)
            return response.status_code == 200
        except (requests.RequestException, requests.Timeout):
            return False

    def get_chrome_info(self) -> Optional[Dict[str, Any]]:
        """
        Get Chrome version and debugging information.

        Returns:
            Chrome info dictionary or None if Chrome is not running.
        """
        try:
            response = requests.get(
                f"http://localhost:{self.debug_port}/json/version", timeout=2)
            if response.status_code == 200:
                return response.json()
        except (requests.RequestException, requests.Timeout, json.JSONDecodeError):
            pass
        return None

    def kill_existing_chrome(self) -> bool:
        """
        Kill any existing Chrome processes on the debug port.

        Returns:
            True if successful, False otherwise.
        """
        try:
            # Kill processes on the debug port
            subprocess.run([
                "lsof", "-ti", f":{self.debug_port}"
            ], capture_output=True, text=True, check=False)

            # Kill Chrome processes
            subprocess.run([
                "pkill", "-f", f"chrome.*{self.debug_port}"
            ], capture_output=True, text=True, check=False)

            # Wait for processes to terminate
            time.sleep(2)
            return True
        except Exception as e:
            logger.error(f"Failed to kill existing Chrome: {e}")
            return False

    def start_chrome(self, headless: bool = True, wait_timeout: int = 30) -> bool:
        """
        Start the standalone Chrome instance.

        Args:
            headless: Whether to start Chrome in headless mode.
            wait_timeout: Timeout in seconds to wait for Chrome to start.

        Returns:
            True if Chrome started successfully, False otherwise.
        """
        if not self.is_chrome_installed():
            logger.error(
                "Chrome is not installed. Run setup_standalone_chrome.sh first.")
            return False

        if self.is_chrome_running():
            logger.info("Chrome is already running.")
            return True

        # Kill any existing Chrome processes
        self.kill_existing_chrome()

        # Create user data directory
        self.user_data_dir.mkdir(exist_ok=True)

        # Build Chrome command
        cmd = [
            str(self.chrome_exec),
            f"--remote-debugging-port={self.debug_port}",
            "--no-first-run",
            "--no-default-browser-check",
            "--disable-default-apps",
            "--disable-popup-blocking",
            "--disable-web-security",
            "--disable-features=VizDisplayCompositor",
            "--disable-dev-shm-usage",
            "--disable-gpu",
            "--no-sandbox",
            "--disable-setuid-sandbox",
            "--disable-background-timer-throttling",
            "--disable-backgrounding-occluded-windows",
            "--disable-renderer-backgrounding",
            "--disable-features=TranslateUI",
            "--disable-ipc-flooding-protection",
            "--disable-blink-features=AutomationControlled",
            "--disable-extensions-except=",
            "--disable-plugins-discovery",
            "--disable-sync",
            "--disable-translate",
            "--disable-background-networking",
            "--disable-client-side-phishing-detection",
            "--disable-component-extensions-with-background-pages",
            "--disable-domain-reliability",
            "--disable-features=AudioServiceOutOfProcess,TranslateUI",
            "--disable-hang-monitor",
            "--disable-prompt-on-repost",
            "--disable-sync-preferences",
            "--metrics-recording-only",
            "--safebrowsing-disable-auto-update",
            f"--user-data-dir={self.user_data_dir}",
            "--window-size=1920,1080",
            "--user-agent=Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/138.0.0.0 Safari/537.36",
            "--disable-logging",
            "--log-level=3",
            "--silent-launch"
        ]

        if headless:
            cmd.append("--headless=new")

        try:
            logger.info("Starting Chrome...")
            self.process = subprocess.Popen(
                cmd,
                stdout=subprocess.DEVNULL,
                stderr=subprocess.DEVNULL,
                start_new_session=True
            )

            # Wait for Chrome to start
            start_time = time.time()
            while time.time() - start_time < wait_timeout:
                if self.is_chrome_running():
                    logger.info(
                        f"✅ Chrome started successfully on port {self.debug_port}")
                    return True
                time.sleep(1)

            logger.error("❌ Chrome failed to start within timeout")
            return False

        except Exception as e:
            logger.error(f"Failed to start Chrome: {e}")
            return False

    def stop_chrome(self) -> bool:
        """
        Stop the Chrome instance.

        Returns:
            True if Chrome was stopped successfully, False otherwise.
        """
        try:
            if self.process:
                self.process.terminate()
                self.process.wait(timeout=5)
                self.process = None

            # Kill any remaining Chrome processes
            self.kill_existing_chrome()

            logger.info("✅ Chrome stopped successfully")
            return True

        except Exception as e:
            logger.error(f"Failed to stop Chrome: {e}")
            return False

    def restart_chrome(self, headless: bool = True) -> bool:
        """
        Restart the Chrome instance.

        Args:
            headless: Whether to start Chrome in headless mode.

        Returns:
            True if Chrome restarted successfully, False otherwise.
        """
        logger.info("Restarting Chrome...")
        self.stop_chrome()
        time.sleep(2)
        return self.start_chrome(headless=headless)

    def get_status(self) -> Dict[str, Any]:
        """
        Get the current status of Chrome.

        Returns:
            Dictionary with Chrome status information.
        """
        status = {
            "installed": self.is_chrome_installed(),
            "running": self.is_chrome_running(),
            "debug_port": self.debug_port,
            "chrome_path": self.get_chrome_path(),
            "user_data_dir": str(self.user_data_dir)
        }

        if status["running"]:
            chrome_info = self.get_chrome_info()
            if chrome_info:
                status["version"] = chrome_info.get("Browser", "Unknown")
                status["debug_url"] = f"http://localhost:{self.debug_port}"

        return status

    def print_status(self):
        """Print the current Chrome status to console."""
        status = self.get_status()

        print("=" * 50)
        print("Chrome Status")
        print("=" * 50)
        print(f"Installed: {'✅' if status['installed'] else '❌'}")
        print(f"Running: {'✅' if status['running'] else '❌'}")
        print(f"Debug Port: {status['debug_port']}")
        print(f"Chrome Path: {status['chrome_path'] or 'Not found'}")
        print(f"User Data: {status['user_data_dir']}")

        if status['running']:
            print(f"Version: {status.get('version', 'Unknown')}")
            print(f"Debug URL: {status.get('debug_url', 'N/A')}")

        print("=" * 50)


def main():
    """Main function for command-line usage."""
    import argparse

    parser = argparse.ArgumentParser(
        description="Manage standalone Chrome instance")
    parser.add_argument("action", choices=["start", "stop", "restart", "status", "info"],
                        help="Action to perform")
    parser.add_argument("--no-headless", action="store_true",
                        help="Start Chrome in non-headless mode")
    parser.add_argument("--project-dir", type=str,
                        help="Project directory path")

    args = parser.parse_args()

    manager = ChromeManager(args.project_dir)

    if args.action == "start":
        success = manager.start_chrome(headless=not args.no_headless)
        sys.exit(0 if success else 1)

    elif args.action == "stop":
        success = manager.stop_chrome()
        sys.exit(0 if success else 1)

    elif args.action == "restart":
        success = manager.restart_chrome(headless=not args.no_headless)
        sys.exit(0 if success else 1)

    elif args.action == "status":
        manager.print_status()

    elif args.action == "info":
        info = manager.get_chrome_info()
        if info:
            print(json.dumps(info, indent=2))
        else:
            print("Chrome is not running or not accessible")


if __name__ == "__main__":
    main()
