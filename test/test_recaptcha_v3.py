#!/usr/bin/env python3
"""
reCAPTCHA v3 Tests for Google reCAPTCHA Bypass

Tests reCAPTCHA v3 solving with different actions and minimum scores.
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
TIMEOUT = 30


def wait_for_result(captcha_id: str, max_wait: int = TIMEOUT) -> Tuple[bool, str]:
    """Wait for captcha result."""
    start_time = time.time()

    while time.time() - start_time < max_wait:
        try:
            response = requests.get(
                f"{API_BASE_URL}/res.php",
                params={"key": API_KEY, "action": "get", "id": captcha_id},
                timeout=10
            )

            if response.status_code == 200:
                result = response.text.strip()
                if result.startswith("OK|"):
                    return True, result.split("|", 1)[1]
                elif "ERROR_" in result:
                    return False, result

        except Exception:
            pass

        time.sleep(3)

    return False, "TIMEOUT"


def test_recaptcha_v3_login() -> Dict[str, Any]:
    """Test reCAPTCHA v3 with login action."""
    try:
        response = requests.post(
            f"{API_BASE_URL}/in.php",
            data={
                "key": API_KEY,
                "method": "userrecaptcha",
                "googlekey": "6Le-wvkSAAAAAPBMRTvw0Q4Muexq9bi0DJwx_mJ-",
                "pageurl": "https://example.com/login",
                "version": "v3",
                "action": "login",
                "min_score": "0.3",
                "soft_id": "135"
            },
            timeout=15
        )

        if response.status_code == 200 and response.text.startswith("OK|"):
            captcha_id = response.text.split("|")[1]
            success, result = wait_for_result(captcha_id)

            return {
                "success": True,
                "submission": "OK",
                "captcha_id": captcha_id,
                "solving_success": success,
                "result": result[:50] + "..." if len(result) > 50 else result
            }
        else:
            return {"success": False, "error": f"Submission failed: {response.text}"}

    except Exception as e:
        return {"success": False, "error": str(e)}


def test_recaptcha_v3_submit() -> Dict[str, Any]:
    """Test reCAPTCHA v3 with submit action and high score."""
    try:
        response = requests.post(
            f"{API_BASE_URL}/in.php",
            data={
                "key": API_KEY,
                "method": "userrecaptcha",
                "googlekey": "6LcH_0IUAAAAAO_Xqjrtj9wWufUpYRnK6BW8hnfn",
                "pageurl": "https://example.com/submit",
                "version": "v3",
                "action": "submit",
                "min_score": "0.7",
                "soft_id": "135"
            },
            timeout=15
        )

        if response.status_code == 200 and response.text.startswith("OK|"):
            captcha_id = response.text.split("|")[1]
            success, result = wait_for_result(captcha_id)

            return {
                "success": True,
                "submission": "OK",
                "captcha_id": captcha_id,
                "solving_success": success,
                "result": result[:50] + "..." if len(result) > 50 else result
            }
        else:
            return {"success": False, "error": f"Submission failed: {response.text}"}

    except Exception as e:
        return {"success": False, "error": str(e)}


def test_recaptcha_v3_homepage() -> Dict[str, Any]:
    """Test reCAPTCHA v3 with homepage action."""
    try:
        response = requests.post(
            f"{API_BASE_URL}/in.php",
            data={
                "key": API_KEY,
                "method": "userrecaptcha",
                "googlekey": "6Le-wvkSAAAAAPBMRTvw0Q4Muexq9bi0DJwx_mJ-",
                "pageurl": "https://example.com/",
                "version": "v3",
                "action": "homepage",
                "min_score": "0.5",
                "soft_id": "135"
            },
            timeout=15
        )

        if response.status_code == 200 and response.text.startswith("OK|"):
            captcha_id = response.text.split("|")[1]
            success, result = wait_for_result(captcha_id, 20)

            return {
                "success": True,
                "submission": "OK",
                "captcha_id": captcha_id,
                "solving_success": success,
                "result": result[:50] + "..." if len(result) > 50 else result
            }
        else:
            return {"success": False, "error": f"Submission failed: {response.text}"}

    except Exception as e:
        return {"success": False, "error": str(e)}


def test_recaptcha_v3_enterprise() -> Dict[str, Any]:
    """Test reCAPTCHA v3 Enterprise."""
    try:
        response = requests.post(
            f"{API_BASE_URL}/in.php",
            data={
                "key": API_KEY,
                "method": "userrecaptcha",
                "googlekey": "6Le-wvkSAAAAAPBMRTvw0Q4Muexq9bi0DJwx_mJ-",
                "pageurl": "https://example.com/enterprise",
                "version": "v3",
                "action": "verify",
                "min_score": "0.9",
                "enterprise": "1",
                "soft_id": "135"
            },
            timeout=15
        )

        if response.status_code == 200 and response.text.startswith("OK|"):
            captcha_id = response.text.split("|")[1]
            success, result = wait_for_result(captcha_id, 20)

            return {
                "success": True,
                "submission": "OK",
                "captcha_id": captcha_id,
                "solving_success": success,
                "result": result[:50] + "..." if len(result) > 50 else result
            }
        else:
            return {"success": False, "error": f"Submission failed: {response.text}"}

    except Exception as e:
        return {"success": False, "error": str(e)}


def test_recaptcha_v3_with_useragent() -> Dict[str, Any]:
    """Test reCAPTCHA v3 with custom user agent."""
    try:
        response = requests.post(
            f"{API_BASE_URL}/in.php",
            data={
                "key": API_KEY,
                "method": "userrecaptcha",
                "googlekey": "6LcH_0IUAAAAAO_Xqjrtj9wWufUpYRnK6BW8hnfn",
                "pageurl": "https://example.com/custom",
                "version": "v3",
                "action": "custom",
                "min_score": "0.4",
                "userAgent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36",
                "soft_id": "135"
            },
            timeout=15
        )

        if response.status_code == 200 and response.text.startswith("OK|"):
            captcha_id = response.text.split("|")[1]
            success, result = wait_for_result(captcha_id, 20)

            return {
                "success": True,
                "submission": "OK",
                "captcha_id": captcha_id,
                "solving_success": success,
                "result": result[:50] + "..." if len(result) > 50 else result
            }
        else:
            return {"success": False, "error": f"Submission failed: {response.text}"}

    except Exception as e:
        return {"success": False, "error": str(e)}


def run_recaptcha_v3_tests() -> Dict[str, Any]:
    """Run all reCAPTCHA v3 tests."""
    print("🎯 Running reCAPTCHA v3 Tests...")

    tests = {
        "recaptcha_v3_login": test_recaptcha_v3_login(),
        "recaptcha_v3_submit": test_recaptcha_v3_submit(),
        "recaptcha_v3_homepage": test_recaptcha_v3_homepage(),
        "recaptcha_v3_enterprise": test_recaptcha_v3_enterprise(),
        "recaptcha_v3_with_useragent": test_recaptcha_v3_with_useragent()
    }

    # Summary
    submission_success = sum(1 for r in tests.values() if r.get("success"))
    solving_success = sum(1 for r in tests.values()
                          if r.get("solving_success"))
    total = len(tests)

    print(f"📊 reCAPTCHA v3 Tests:")
    print(f"   Submissions: {submission_success}/{total} successful")
    print(f"   Solving: {solving_success}/{total} successful")

    for test_name, result in tests.items():
        if result.get("success"):
            status = "✅" if result.get("solving_success") else "⏳"
            print(f"{status} {test_name}: Submitted OK")
            if result.get("solving_success"):
                print(f"   └─ Solved: {result.get('result', 'N/A')}")
            elif result.get("result") == "TIMEOUT":
                print(f"   └─ Timeout (expected for testing)")
            else:
                print(f"   └─ Status: {result.get('result', 'N/A')}")
        else:
            print(f"❌ {test_name}: {result.get('error', 'Unknown error')}")

    return {
        "summary": {
            "total": total,
            "submission_success": submission_success,
            "solving_success": solving_success,
            "submission_rate": submission_success/total*100,
            "solving_rate": solving_success/total*100 if total > 0 else 0
        },
        "details": tests
    }


if __name__ == "__main__":
    results = run_recaptcha_v3_tests()
    success = results["summary"]["submission_success"] > 0
    sys.exit(0 if success else 1)
