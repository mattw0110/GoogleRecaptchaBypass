#!/usr/bin/env python3
"""
Service Health Tests for Google reCAPTCHA Bypass

Tests basic service functionality, health endpoints, and connectivity.
"""

import sys
import os
import requests
import json
from typing import Dict, Any

# Add parent directory to path for imports
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

API_BASE_URL = "http://localhost:5001"
API_KEY = "fake_680d0e29b28040ef"


def test_health_endpoint() -> Dict[str, Any]:
    """Test the /health endpoint."""
    try:
        response = requests.get(f"{API_BASE_URL}/health", timeout=10)

        if response.status_code == 200:
            data = response.json()
            return {
                "success": True,
                "status": data.get("status"),
                "chrome_status": data.get("chrome_status"),
                "api_key_configured": data.get("api_key_configured"),
                "proxy_stats": data.get("proxy_stats", {})
            }
        else:
            return {"success": False, "error": f"HTTP {response.status_code}"}
    except Exception as e:
        return {"success": False, "error": str(e)}


def test_balance_endpoint() -> Dict[str, Any]:
    """Test the balance check endpoint."""
    try:
        response = requests.get(
            f"{API_BASE_URL}/res.php",
            params={"key": API_KEY, "action": "getbalance"},
            timeout=10
        )

        if response.status_code == 200:
            balance = response.text.strip()
            return {
                "success": True,
                "balance": balance,
                "valid_balance": "999" in balance
            }
        else:
            return {"success": False, "error": f"HTTP {response.status_code}"}
    except Exception as e:
        return {"success": False, "error": str(e)}


def test_status_endpoint() -> Dict[str, Any]:
    """Test the /status endpoint."""
    try:
        response = requests.get(f"{API_BASE_URL}/status", timeout=10)

        if response.status_code == 200:
            data = response.json()
            return {
                "success": True,
                "service_status": data.get("service_status"),
                "active_browsers": data.get("active_browsers"),
                "pending_captchas": data.get("pending_captchas")
            }
        else:
            return {"success": False, "error": f"HTTP {response.status_code}"}
    except Exception as e:
        return {"success": False, "error": str(e)}


def test_chrome_connectivity() -> Dict[str, Any]:
    """Test Chrome connectivity on port 9222."""
    try:
        response = requests.get(
            "http://127.0.0.1:9222/json/version", timeout=5)

        if response.status_code == 200:
            data = response.json()
            return {
                "success": True,
                "browser": data.get("Browser"),
                "protocol_version": data.get("Protocol-Version"),
                "user_agent": data.get("User-Agent")
            }
        else:
            return {"success": False, "error": f"HTTP {response.status_code}"}
    except Exception as e:
        return {"success": False, "error": str(e)}


def run_health_tests() -> Dict[str, Any]:
    """Run all health tests and return results."""
    print("🏥 Running Service Health Tests...")

    results = {
        "health_endpoint": test_health_endpoint(),
        "balance_endpoint": test_balance_endpoint(),
        "status_endpoint": test_status_endpoint(),
        "chrome_connectivity": test_chrome_connectivity()
    }

    # Summary
    passed = sum(1 for r in results.values() if r.get("success"))
    total = len(results)

    print(f"📊 Health Tests: {passed}/{total} passed")

    for test_name, result in results.items():
        if result.get("success"):
            print(f"✅ {test_name}: OK")
        else:
            print(f"❌ {test_name}: {result.get('error', 'Unknown error')}")

    return {
        "summary": {"passed": passed, "total": total, "success_rate": passed/total*100},
        "details": results
    }


if __name__ == "__main__":
    results = run_health_tests()
    success = results["summary"]["passed"] == results["summary"]["total"]
    sys.exit(0 if success else 1)
