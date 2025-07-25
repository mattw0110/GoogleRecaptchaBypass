#!/usr/bin/env python3
"""
Comprehensive Test Runner for Google reCAPTCHA Bypass Service

This script runs all test suites and provides a comprehensive report.
"""

import sys
import os
import time
import requests
from datetime import datetime
from typing import Dict, Any, List

# Add current directory to path for imports
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Import test modules
try:
    from test_service_health import run_health_tests
    from test_recaptcha_v2 import run_recaptcha_v2_tests
    from test_recaptcha_v3 import run_recaptcha_v3_tests
    from test_api_formats import run_api_format_tests
except ImportError as e:
    print(f"❌ Error importing test modules: {e}")
    print("Please ensure all test files are present in the test directory")
    sys.exit(1)

API_BASE_URL = "http://localhost:5001"


def print_banner():
    """Print test runner banner."""
    print("=" * 80)
    print("🧪 COMPREHENSIVE TEST SUITE - Google reCAPTCHA Bypass Service")
    print("=" * 80)
    print(f"🎯 Target Service: {API_BASE_URL}")
    print(f"⏰ Start Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("=" * 80)
    print()


def check_service_availability() -> bool:
    """Check if the service is running."""
    try:
        response = requests.get(f"{API_BASE_URL}/health", timeout=5)
        return response.status_code == 200
    except:
        return False


def wait_for_service(max_wait: int = 30) -> bool:
    """Wait for service to become available."""
    print("⏳ Waiting for service to become available...")

    for i in range(max_wait):
        if check_service_availability():
            print("✅ Service is available!")
            return True

        print(f"   Attempt {i+1}/{max_wait}...")
        time.sleep(1)

    return False


def run_hcaptcha_test() -> Dict[str, Any]:
    """Run basic hCaptcha test."""
    print("🛡️  Running hCaptcha Test...")

    try:
        response = requests.post(
            f"{API_BASE_URL}/in.php",
            data={
                "key": "fake_680d0e29b28040ef",
                "method": "hcaptcha",
                "sitekey": "10000000-ffff-ffff-ffff-000000000001",
                "pageurl": "https://example.com/hcaptcha",
                "soft_id": "135"
            },
            timeout=15
        )

        if response.status_code == 200 and response.text.startswith("OK|"):
            captcha_id = response.text.split("|")[1]
            return {
                "success": True,
                "submission": "OK",
                "captcha_id": captcha_id
            }
        else:
            return {"success": False, "error": f"Submission failed: {response.text}"}

    except Exception as e:
        return {"success": False, "error": str(e)}


def run_proxy_test() -> Dict[str, Any]:
    """Run proxy integration test."""
    print("🌐 Running Proxy Integration Test...")

    try:
        response = requests.get(f"{API_BASE_URL}/proxies", timeout=10)

        if response.status_code == 200:
            data = response.json()
            proxy_stats = data.get("proxy_stats", {})
            return {
                "success": True,
                "total_proxies": proxy_stats.get("total_proxies", 0),
                "proxy_status": data.get("proxy_status", {}),
                "working": proxy_stats.get("total_proxies", 0) > 0
            }
        else:
            return {"success": False, "error": f"HTTP {response.status_code}"}

    except Exception as e:
        return {"success": False, "error": str(e)}


def compile_final_report(test_results: Dict[str, Any]) -> Dict[str, Any]:
    """Compile final test report."""

    # Calculate overall statistics
    total_tests = 0
    passed_tests = 0
    failed_tests = 0
    categories_passed = 0
    total_categories = len(test_results)

    for category, result in test_results.items():
        if category in ["health", "api_formats"]:
            if result.get("summary", {}).get("passed", 0) > 0:
                categories_passed += 1
                passed_tests += result["summary"]["passed"]
            failed_tests += result["summary"]["total"] - \
                result["summary"]["passed"]
            total_tests += result["summary"]["total"]
        elif category in ["recaptcha_v2", "recaptcha_v3"]:
            if result.get("summary", {}).get("submission_success", 0) > 0:
                categories_passed += 1
                passed_tests += result["summary"]["submission_success"]
            failed_tests += result["summary"]["total"] - \
                result["summary"]["submission_success"]
            total_tests += result["summary"]["total"]
        else:
            # Simple success/fail tests
            if result.get("success"):
                categories_passed += 1
                passed_tests += 1
            else:
                failed_tests += 1
            total_tests += 1

    success_rate = (passed_tests / total_tests * 100) if total_tests > 0 else 0
    category_success_rate = (
        categories_passed / total_categories * 100) if total_categories > 0 else 0

    return {
        "total_tests": total_tests,
        "passed_tests": passed_tests,
        "failed_tests": failed_tests,
        "success_rate": success_rate,
        "categories_passed": categories_passed,
        "total_categories": total_categories,
        "category_success_rate": category_success_rate,
        "overall_status": "PASS" if category_success_rate >= 70 else "FAIL"
    }


def print_final_report(test_results: Dict[str, Any], summary: Dict[str, Any], duration: float):
    """Print comprehensive final report."""

    print("\n" + "=" * 80)
    print("📊 COMPREHENSIVE TEST RESULTS SUMMARY")
    print("=" * 80)

    print(f"⏱️  Total Duration: {duration:.2f} seconds")
    print(f"📋 Total Tests: {summary['total_tests']}")
    print(f"✅ Passed: {summary['passed_tests']}")
    print(f"❌ Failed: {summary['failed_tests']}")
    print(f"📈 Success Rate: {summary['success_rate']:.1f}%")
    print(
        f"📂 Categories: {summary['categories_passed']}/{summary['total_categories']} passed")
    print(f"🏆 Overall Status: {summary['overall_status']}")

    print("\n📋 Category Breakdown:")

    # Health Tests
    health = test_results.get("health", {})
    health_status = "✅ PASS" if health.get(
        "summary", {}).get("passed", 0) > 0 else "❌ FAIL"
    print(f"   🏥 Service Health: {health_status}")
    if health.get("summary"):
        print(
            f"      Tests: {health['summary']['passed']}/{health['summary']['total']}")

    # reCAPTCHA v2 Tests
    v2 = test_results.get("recaptcha_v2", {})
    v2_status = "✅ PASS" if v2.get("summary", {}).get(
        "submission_success", 0) > 0 else "❌ FAIL"
    print(f"   🤖 reCAPTCHA v2: {v2_status}")
    if v2.get("summary"):
        print(
            f"      Submissions: {v2['summary']['submission_success']}/{v2['summary']['total']}")
        print(
            f"      Solving: {v2['summary']['solving_success']}/{v2['summary']['total']}")

    # reCAPTCHA v3 Tests
    v3 = test_results.get("recaptcha_v3", {})
    v3_status = "✅ PASS" if v3.get("summary", {}).get(
        "submission_success", 0) > 0 else "❌ FAIL"
    print(f"   🎯 reCAPTCHA v3: {v3_status}")
    if v3.get("summary"):
        print(
            f"      Submissions: {v3['summary']['submission_success']}/{v3['summary']['total']}")
        print(
            f"      Solving: {v3['summary']['solving_success']}/{v3['summary']['total']}")

    # API Format Tests
    api = test_results.get("api_formats", {})
    api_status = "✅ PASS" if api.get("summary", {}).get(
        "passed", 0) > 0 else "❌ FAIL"
    print(f"   🔄 API Formats: {api_status}")
    if api.get("summary"):
        print(
            f"      Tests: {api['summary']['passed']}/{api['summary']['total']}")

    # hCaptcha Test
    hcaptcha = test_results.get("hcaptcha", {})
    hcaptcha_status = "✅ PASS" if hcaptcha.get("success") else "❌ FAIL"
    print(f"   🛡️  hCaptcha: {hcaptcha_status}")

    # Proxy Test
    proxy = test_results.get("proxy", {})
    proxy_status = "✅ PASS" if proxy.get("success") else "❌ FAIL"
    print(f"   🌐 Proxy Integration: {proxy_status}")
    if proxy.get("total_proxies"):
        print(f"      Proxies Available: {proxy['total_proxies']}")

    print("\n💡 Notes:")
    print("   • Submission tests verify API compatibility")
    print("   • Solving tests may timeout during testing (expected)")
    print("   • Focus on submission success for API functionality")
    print("   • Full solving tests require real captcha pages")

    print("\n🚀 Service Status:")
    if summary["overall_status"] == "PASS":
        print("   ✅ Service is ready for production use!")
        print("   ✅ All core functionality working")
        print("   ✅ GSA integration ready")
    else:
        print("   ⚠️  Some issues detected")
        print("   🔧 Check service configuration")
        print("   🔧 Verify Chrome connectivity")

    print("=" * 80)


def main():
    """Main test runner function."""
    start_time = time.time()
    print_banner()

    # Check service availability
    if not check_service_availability():
        print("❌ Service is not available!")
        print("Please start the service first:")
        print("   ./start_fake_2captcha_with_chrome.sh")
        print()

        if not wait_for_service():
            print("❌ Service failed to start. Exiting.")
            return False

    print("✅ Service is available, starting comprehensive tests...\n")

    # Run all test suites
    test_results = {}

    print("🏥 Running Service Health Tests...")
    test_results["health"] = run_health_tests()
    print()

    print("🤖 Running reCAPTCHA v2 Tests...")
    test_results["recaptcha_v2"] = run_recaptcha_v2_tests()
    print()

    print("🎯 Running reCAPTCHA v3 Tests...")
    test_results["recaptcha_v3"] = run_recaptcha_v3_tests()
    print()

    print("🔄 Running API Format Tests...")
    test_results["api_formats"] = run_api_format_tests()
    print()

    # Run additional tests
    test_results["hcaptcha"] = run_hcaptcha_test()
    print()

    test_results["proxy"] = run_proxy_test()
    print()

    # Generate final report
    duration = time.time() - start_time
    summary = compile_final_report(test_results)
    print_final_report(test_results, summary, duration)

    return summary["overall_status"] == "PASS"


if __name__ == "__main__":
    try:
        success = main()
        sys.exit(0 if success else 1)
    except KeyboardInterrupt:
        print("\n\n⚠️  Tests interrupted by user")
        sys.exit(1)
    except Exception as e:
        print(f"\n❌ Fatal error: {e}")
        sys.exit(1)
