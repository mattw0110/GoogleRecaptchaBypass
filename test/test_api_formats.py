#!/usr/bin/env python3
"""
API Format Tests for Google reCAPTCHA Bypass

Tests both the classic 2captcha API format and the modern JSON API format.
"""

import sys
import os
import requests
import time
from typing import Dict, Any, Tuple

# Add parent directory to path for imports
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

API_BASE_URL = "http://localhost:5001"
API_KEY = "fake_680d0e29b28040ef"
TIMEOUT = 20


def test_2captcha_format_submission() -> Dict[str, Any]:
    """Test classic 2captcha format submission."""
    try:
        response = requests.post(
            f"{API_BASE_URL}/in.php",
            data={
                "key": API_KEY,
                "method": "userrecaptcha",
                "googlekey": "6Le-wvkSAAAAAPBMRTvw0Q4Muexq9bi0DJwx_mJ-",
                "pageurl": "https://www.google.com/recaptcha/api2/demo",
                "soft_id": "135"
            },
            timeout=15
        )

        if response.status_code == 200 and response.text.startswith("OK|"):
            captcha_id = response.text.split("|")[1]
            return {
                "success": True,
                "format": "2captcha",
                "captcha_id": captcha_id,
                "response": response.text
            }
        else:
            return {"success": False, "error": f"Submission failed: {response.text}"}

    except Exception as e:
        return {"success": False, "error": str(e)}


def test_2captcha_format_result_check(captcha_id: str) -> Dict[str, Any]:
    """Test classic 2captcha format result checking."""
    try:
        response = requests.get(
            f"{API_BASE_URL}/res.php",
            params={"key": API_KEY, "action": "get", "id": captcha_id},
            timeout=10
        )

        if response.status_code == 200:
            result = response.text.strip()
            return {
                "success": True,
                "format": "2captcha",
                "status": "ready" if result.startswith("OK|") else "not_ready" if "CAPCHA_NOT_READY" in result else "error",
                "response": result
            }
        else:
            return {"success": False, "error": f"HTTP {response.status_code}"}

    except Exception as e:
        return {"success": False, "error": str(e)}


def test_modern_api_submission() -> Dict[str, Any]:
    """Test modern JSON API submission."""
    try:
        response = requests.post(
            f"{API_BASE_URL}/captcha",
            json={
                "googlekey": "6Le-wvkSAAAAAPBMRTvw0Q4Muexq9bi0DJwx_mJ-",
                "pageurl": "https://www.google.com/recaptcha/api2/demo"
            },
            headers={"X-API-Key": API_KEY},
            timeout=15
        )

        if response.status_code == 200:
            data = response.json()
            captcha_id = data.get("captcha")
            if captcha_id:
                return {
                    "success": True,
                    "format": "modern",
                    "captcha_id": captcha_id,
                    "response": data
                }
            else:
                return {"success": False, "error": "No captcha ID in response"}
        else:
            return {"success": False, "error": f"HTTP {response.status_code}"}

    except Exception as e:
        return {"success": False, "error": str(e)}


def test_modern_api_result_check(captcha_id: str) -> Dict[str, Any]:
    """Test modern JSON API result checking."""
    try:
        response = requests.get(
            f"{API_BASE_URL}/captcha/{captcha_id}", timeout=10)

        if response.status_code in [200, 202]:
            data = response.json()
            return {
                "success": True,
                "format": "modern",
                "status": "ready" if data.get("is_correct") else "not_ready",
                "response": data
            }
        elif response.status_code == 404:
            return {"success": False, "error": "Captcha not found"}
        else:
            return {"success": False, "error": f"HTTP {response.status_code}"}

    except Exception as e:
        return {"success": False, "error": str(e)}


def test_balance_endpoints() -> Dict[str, Any]:
    """Test balance check in different formats."""
    results = {}

    # Test 2captcha format balance
    try:
        response = requests.get(
            f"{API_BASE_URL}/res.php",
            params={"key": API_KEY, "action": "getbalance"},
            timeout=10
        )

        if response.status_code == 200:
            results["2captcha_balance"] = {
                "success": True,
                "balance": response.text.strip(),
                "valid": "999" in response.text
            }
        else:
            results["2captcha_balance"] = {
                "success": False, "error": f"HTTP {response.status_code}"}
    except Exception as e:
        results["2captcha_balance"] = {"success": False, "error": str(e)}

    # Test modern format balance (user endpoint)
    try:
        response = requests.get(
            f"{API_BASE_URL}/user?key={API_KEY}", timeout=10)

        if response.status_code == 200:
            data = response.json()
            results["modern_balance"] = {
                "success": True,
                "balance": data.get("balance"),
                "user": data.get("user"),
                "valid": data.get("balance") == 999.99
            }
        else:
            results["modern_balance"] = {
                "success": False, "error": f"HTTP {response.status_code}"}
    except Exception as e:
        results["modern_balance"] = {"success": False, "error": str(e)}

    return results


def test_error_handling() -> Dict[str, Any]:
    """Test error handling in both API formats."""
    results = {}

    # Test 2captcha format error handling
    try:
        response = requests.post(
            f"{API_BASE_URL}/in.php",
            data={"key": "invalid_key", "method": "userrecaptcha"},
            timeout=10
        )

        results["2captcha_error"] = {
            "success": "ERROR_KEY_DOES_NOT_EXIST" in response.text,
            "response": response.text.strip()
        }
    except Exception as e:
        results["2captcha_error"] = {"success": False, "error": str(e)}

    # Test modern format error handling
    try:
        response = requests.post(
            f"{API_BASE_URL}/captcha",
            json={"googlekey": "test"},
            headers={"X-API-Key": "invalid_key"},
            timeout=10
        )

        results["modern_error"] = {
            "success": response.status_code == 401,
            "status_code": response.status_code,
            "response": response.json() if response.headers.get('content-type', '').startswith('application/json') else response.text
        }
    except Exception as e:
        results["modern_error"] = {"success": False, "error": str(e)}

    return results


def test_report_functionality() -> Dict[str, Any]:
    """Test reporting functionality in 2captcha format."""
    # First submit a captcha to get an ID
    submission = test_2captcha_format_submission()
    if not submission.get("success"):
        return {"success": False, "error": "Could not submit captcha for testing"}

    captcha_id = submission["captcha_id"]
    results = {}

    # Test reportbad
    try:
        response = requests.get(
            f"{API_BASE_URL}/res.php",
            params={"key": API_KEY, "action": "reportbad", "id": captcha_id},
            timeout=10
        )

        results["reportbad"] = {
            "success": "OK_REPORT_RECORDED" in response.text,
            "response": response.text.strip()
        }
    except Exception as e:
        results["reportbad"] = {"success": False, "error": str(e)}

    # Test reportgood
    try:
        response = requests.get(
            f"{API_BASE_URL}/res.php",
            params={"key": API_KEY, "action": "reportgood", "id": captcha_id},
            timeout=10
        )

        results["reportgood"] = {
            "success": "OK_REPORT_RECORDED" in response.text,
            "response": response.text.strip()
        }
    except Exception as e:
        results["reportgood"] = {"success": False, "error": str(e)}

    return results


def run_api_format_tests() -> Dict[str, Any]:
    """Run all API format tests."""
    print("🔄 Running API Format Tests...")

    # Test submissions
    print("   Testing submissions...")
    captcha_2captcha = test_2captcha_format_submission()
    captcha_modern = test_modern_api_submission()

    # Test result checking
    print("   Testing result checking...")
    result_2captcha = None
    result_modern = None

    if captcha_2captcha.get("success"):
        time.sleep(2)  # Brief wait
        result_2captcha = test_2captcha_format_result_check(
            captcha_2captcha["captcha_id"])

    if captcha_modern.get("success"):
        time.sleep(2)  # Brief wait
        result_modern = test_modern_api_result_check(
            captcha_modern["captcha_id"])

    # Test other functionality
    print("   Testing balance endpoints...")
    balance_tests = test_balance_endpoints()

    print("   Testing error handling...")
    error_tests = test_error_handling()

    print("   Testing report functionality...")
    report_tests = test_report_functionality()

    # Compile results
    results = {
        "submissions": {
            "2captcha_format": captcha_2captcha,
            "modern_format": captcha_modern
        },
        "result_checking": {
            "2captcha_format": result_2captcha,
            "modern_format": result_modern
        },
        "balance_tests": balance_tests,
        "error_tests": error_tests,
        "report_tests": report_tests
    }

    # Summary
    tests_passed = 0
    tests_total = 0

    # Count successful submissions
    if captcha_2captcha.get("success"):
        tests_passed += 1
    tests_total += 1

    if captcha_modern.get("success"):
        tests_passed += 1
    tests_total += 1

    # Count successful balance tests
    for test in balance_tests.values():
        if test.get("success"):
            tests_passed += 1
        tests_total += 1

    # Count successful error tests
    for test in error_tests.values():
        if test.get("success"):
            tests_passed += 1
        tests_total += 1

    print(f"📊 API Format Tests: {tests_passed}/{tests_total} passed")

    # Print detailed results
    print("✅ 2captcha Format Submission:",
          "OK" if captcha_2captcha.get("success") else "FAILED")
    print("✅ Modern Format Submission:",
          "OK" if captcha_modern.get("success") else "FAILED")
    print("✅ 2captcha Balance:", "OK" if balance_tests.get(
        "2captcha_balance", {}).get("success") else "FAILED")
    print("✅ Modern Balance:", "OK" if balance_tests.get(
        "modern_balance", {}).get("success") else "FAILED")
    print("✅ Error Handling:", "OK" if all(t.get("success")
          for t in error_tests.values()) else "PARTIAL")

    return {
        "summary": {
            "total": tests_total,
            "passed": tests_passed,
            "success_rate": tests_passed/tests_total*100 if tests_total > 0 else 0
        },
        "details": results
    }


if __name__ == "__main__":
    results = run_api_format_tests()
    # 70% pass rate
    success = results["summary"]["passed"] >= results["summary"]["total"] * 0.7
    sys.exit(0 if success else 1)
