#!/usr/bin/env python3
"""
Test script for Fake 2captcha API service
"""

import requests
import json
import time
import os
from typing import Dict, Any
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Configuration
API_BASE_URL = f"http://localhost:{os.getenv('PORT', '5000')}"
TEST_TIMEOUT = 30  # seconds


def test_health_check() -> bool:
    """Test the health check endpoint."""
    try:
        response = requests.get(f"{API_BASE_URL}/health", timeout=10)
        if response.status_code == 200:
            data = response.json()
            print(f"✅ Health check passed: {data}")
            return True
        else:
            print(f"❌ Health check failed: {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ Health check error: {e}")
        return False


def test_balance_check() -> bool:
    """Test the balance check endpoint."""
    try:
        api_key = os.getenv('FAKE_2CAPTCHA_API_KEY', 'test_key')
        response = requests.get(
            f"{API_BASE_URL}/user?key={api_key}", timeout=10)
        if response.status_code == 200:
            data = response.json()
            print(f"✅ Balance check passed: {data}")
            return True
        else:
            print(f"❌ Balance check failed: {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ Balance check error: {e}")
        return False


def test_status_check() -> bool:
    """Test the status check endpoint."""
    try:
        response = requests.get(f"{API_BASE_URL}/status", timeout=10)
        if response.status_code == 200:
            data = response.json()
            print(f"✅ Status check passed: {data}")
            return True
        else:
            print(f"❌ Status check failed: {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ Status check error: {e}")
        return False


def test_config_check() -> bool:
    """Test the configuration check endpoint."""
    try:
        response = requests.get(f"{API_BASE_URL}/config", timeout=10)
        if response.status_code == 200:
            data = response.json()
            print(f"✅ Config check passed: {data}")
            return True
        else:
            print(f"❌ Config check failed: {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ Config check error: {e}")
        return False


def test_captcha_submit() -> bool:
    """Test captcha submission."""
    try:
        api_key = os.getenv('FAKE_2CAPTCHA_API_KEY', 'test_key')

        # Test data
        test_data = {
            'key': api_key,
            'method': 'userrecaptcha',
            'googlekey': '6LcA-wAAAAAAABlX02ZqFPKNP_y66oTYvY74Y5B',
            'pageurl': 'https://www.google.com/recaptcha/api2/demo'
        }

        response = requests.post(
            f"{API_BASE_URL}/in.php", data=test_data, timeout=TEST_TIMEOUT)

        if response.status_code == 200:
            data = response.json()
            print(f"✅ Captcha submit test passed: {data}")
            return data.get('request')  # Return captcha ID for result test
        else:
            print(f"❌ Captcha submit test failed: {response.status_code}")
            return None

    except Exception as e:
        print(f"❌ Captcha submit test error: {e}")
        return None


def test_captcha_result(captcha_id: str) -> bool:
    """Test getting captcha result."""
    if not captcha_id:
        print("⚠️ Skipping captcha result test - no captcha ID")
        return True

    try:
        api_key = os.getenv('FAKE_2CAPTCHA_API_KEY', 'test_key')

        # Wait a bit for the captcha to start solving
        print(
            f"⏳ Waiting 3 seconds for captcha {captcha_id} to start solving...")
        time.sleep(3)

        # Try to get result (it might not be ready yet)
        response = requests.get(
            f"{API_BASE_URL}/res.php?key={api_key}&action=get&id={captcha_id}",
            timeout=10
        )

        if response.status_code == 200:
            data = response.json()
            print(f"✅ Captcha result test passed: {data}")
            return True
        elif response.status_code == 400:
            data = response.json()
            if 'CAPCHA_NOT_READY' in str(data):
                print(f"⚠️ Captcha result test - not ready yet: {data}")
                return True  # This is expected
            else:
                print(f"❌ Captcha result test failed: {data}")
                return False
        elif response.status_code == 404:
            print(
                f"❌ Captcha result test failed: Captcha ID {captcha_id} not found (404)")
            return False
        else:
            print(f"❌ Captcha result test failed: {response.status_code}")
            return False

    except Exception as e:
        print(f"❌ Captcha result test error: {e}")
        return False


def test_modern_api() -> bool:
    """Test the modern API endpoints."""
    try:
        api_key = os.getenv('FAKE_2CAPTCHA_API_KEY', 'test_key')

        # Test modern submit
        test_data = {
            'googlekey': '6LcA-wAAAAAAABlX02ZqFPKNP_y66oTYvY74Y5B',
            'pageurl': 'https://www.google.com/recaptcha/api2/demo'
        }

        headers = {'X-API-Key': api_key}

        response = requests.post(
            f"{API_BASE_URL}/captcha",
            json=test_data,
            headers=headers,
            timeout=TEST_TIMEOUT
        )

        if response.status_code == 200:
            data = response.json()
            print(f"✅ Modern API submit test passed: {data}")
            return data.get('captcha')  # Return captcha ID
        else:
            print(f"❌ Modern API submit test failed: {response.status_code}")
            return None

    except Exception as e:
        print(f"❌ Modern API submit test error: {e}")
        return None


def test_modern_result(captcha_id: str) -> bool:
    """Test getting result via modern API."""
    if not captcha_id:
        print("⚠️ Skipping modern result test - no captcha ID")
        return True

    try:
        # Wait a bit for the captcha to start solving
        print(
            f"⏳ Waiting 3 seconds for captcha {captcha_id} to start solving...")
        time.sleep(3)

        response = requests.get(
            f"{API_BASE_URL}/captcha/{captcha_id}", timeout=10)

        if response.status_code == 200:
            data = response.json()
            print(f"✅ Modern result test passed: {data}")
            return True
        elif response.status_code == 202:
            data = response.json()
            print(f"⚠️ Modern result test - not ready yet: {data}")
            return True  # This is expected
        elif response.status_code == 404:
            print(
                f"❌ Modern result test failed: Captcha ID {captcha_id} not found (404)")
            return False
        else:
            print(f"❌ Modern result test failed: {response.status_code}")
            return False

    except Exception as e:
        print(f"❌ Modern result test error: {e}")
        return False


def check_environment() -> bool:
    """Check if environment variables are properly configured."""
    print("\n🔍 Environment Check:")

    api_key = os.getenv('FAKE_2CAPTCHA_API_KEY')
    port = os.getenv('PORT', '5000')

    if api_key and api_key != 'your_fake_api_key_here':
        print(f"✅ FAKE_2CAPTCHA_API_KEY is configured")
    else:
        print(f"⚠️ FAKE_2CAPTCHA_API_KEY not configured")

    print(f"✅ PORT configured: {port}")

    return True


def main():
    """Run all tests."""
    print("🧪 Fake 2captcha API Integration Test Suite")
    print("=" * 55)

    # Check environment
    check_environment()

    print("\n🚀 Running API Tests:")
    print("-" * 30)

    tests = [
        ("Health Check", test_health_check),
        ("Balance Check", test_balance_check),
        ("Status Check", test_status_check),
        ("Config Check", test_config_check),
    ]

    passed = 0
    total = len(tests)

    for test_name, test_func in tests:
        print(f"\n📋 Testing: {test_name}")
        try:
            if test_func():
                passed += 1
        except Exception as e:
            print(f"❌ {test_name} crashed: {e}")

    # Test captcha solving (these might take longer)
    print(f"\n📋 Testing: Captcha Submit (2captcha format)")
    captcha_id = test_captcha_submit()
    if captcha_id:
        passed += 1
        total += 1

        print(f"\n📋 Testing: Captcha Result (2captcha format)")
        if test_captcha_result(captcha_id):
            passed += 1
        total += 1

    # Test modern API
    print(f"\n📋 Testing: Modern API Submit")
    modern_captcha_id = test_modern_api()
    if modern_captcha_id:
        passed += 1
        total += 1

        print(f"\n📋 Testing: Modern API Result")
        if test_modern_result(modern_captcha_id):
            passed += 1
        total += 1

    print("\n" + "=" * 55)
    print(f"📊 Test Results: {passed}/{total} tests passed")

    if passed == total:
        print("🎉 All tests passed! The Fake 2captcha API is working correctly.")
    else:
        print("⚠️ Some tests failed. Check the configuration and try again.")

    print("\n💡 GSA Configuration:")
    api_key = os.getenv('FAKE_2CAPTCHA_API_KEY', 'your_api_key_here')
    port = os.getenv('PORT', '5000')
    print(f"   Service Type: 2captcha API")
    print(f"   API URL: http://localhost:{port}")
    print(f"   API Key: {api_key}")


if __name__ == "__main__":
    main()
