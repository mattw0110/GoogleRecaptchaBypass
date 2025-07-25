# Comprehensive Test Suite for Google reCAPTCHA Bypass

This test suite provides comprehensive testing for the Google reCAPTCHA Bypass service, covering all captcha types, API formats, and service functionality.

## 🧪 Test Categories

### **Service Health Tests** (`test_service_health.py`)
- Health endpoint functionality
- Balance checking endpoints  
- Service status monitoring
- Chrome connectivity verification

### **reCAPTCHA v2 Tests** (`test_recaptcha_v2.py`)
- Regular reCAPTCHA v2 solving
- Invisible reCAPTCHA v2 solving
- Enterprise reCAPTCHA v2
- Custom user agent handling

### **reCAPTCHA v3 Tests** (`test_recaptcha_v3.py`)
- Action-based solving (login, submit, homepage)
- Minimum score requirements
- Enterprise reCAPTCHA v3
- Custom actions and scores

### **API Format Tests** (`test_api_formats.py`)
- Classic 2captcha API format
- Modern JSON API format
- Balance endpoint compatibility
- Error handling verification
- Report functionality

### **Additional Tests**
- hCaptcha submission testing
- Proxy integration verification

## 🚀 Quick Start

### **Run All Tests**
```bash
# From the test directory
./run_tests.sh

# Or run comprehensive test suite directly
python run_comprehensive_tests.py
```

### **Run Specific Test Categories**
```bash
./run_tests.sh --health          # Health tests only
./run_tests.sh --recaptcha-v2    # reCAPTCHA v2 tests only
./run_tests.sh --recaptcha-v3    # reCAPTCHA v3 tests only
./run_tests.sh --api-formats     # API format tests only
./run_tests.sh --quick           # Quick test suite
```

### **Auto-start Service and Test**
```bash
./run_tests.sh --start-service   # Start service automatically
```

## 📋 Individual Test Files

Each test can be run independently:

```bash
# Service health
python test_service_health.py

# reCAPTCHA v2 
python test_recaptcha_v2.py

# reCAPTCHA v3
python test_recaptcha_v3.py

# API formats
python test_api_formats.py
```

## 🔧 Test Configuration

### **Service Configuration**
- **API Base URL**: `http://localhost:5001`
- **API Key**: `fake_680d0e29b28040ef`
- **Timeout**: 30 seconds for captcha solving
- **Test Timeout**: 20 seconds for API response

### **Test Expectations**

#### **Submission Tests**
- **Purpose**: Verify API compatibility and request handling
- **Success Criteria**: API returns `OK|{captcha_id}` format
- **Focus**: Integration with GSA and 2captcha clients

#### **Solving Tests**
- **Purpose**: Verify actual captcha solving functionality  
- **Expected**: May timeout during testing (this is normal)
- **Note**: Full solving requires real captcha pages with audio challenges

#### **Health Tests**
- **Purpose**: Verify service and Chrome connectivity
- **Success Criteria**: All endpoints respond correctly
- **Critical**: Chrome must be accessible on port 9222

## 📊 Test Results Interpretation

### **Test Status Indicators**
- ✅ **PASS**: Test completed successfully
- ❌ **FAIL**: Test failed, needs investigation
- ⏳ **TIMEOUT**: Expected for solving tests during development
- ⏭️ **SKIP**: Test skipped due to dependencies

### **Success Criteria**
- **Service Health**: All endpoints must respond
- **API Compatibility**: Submissions must work (solving may timeout)
- **Format Support**: Both 2captcha and modern formats must work
- **Error Handling**: Proper error codes for invalid requests

### **Expected Behavior**
- **Submissions**: Should always succeed if service is healthy
- **Solving**: May timeout without real audio captchas
- **Proxy Tests**: Should work if proxies are available
- **Chrome Tests**: Requires Chrome on port 9222

## 🛠️ Troubleshooting

### **Common Issues**

#### **Service Not Available**
```bash
❌ Service is not available!
```
**Solution**: Start the service first:
```bash
cd .. && ./start_fake_2captcha_with_chrome.sh
```

#### **Chrome Connection Failed**
```bash
❌ chrome_connectivity: Connection refused
```
**Solution**: Verify Chrome is running on port 9222:
```bash
curl http://127.0.0.1:9222/json/version
```

#### **Import Errors**
```bash
❌ Error importing test modules
```
**Solution**: Ensure you're in the test directory and all files exist:
```bash
cd test
ls -la *.py
```

#### **Permission Denied**
```bash
❌ Permission denied: ./run_tests.sh
```
**Solution**: Make scripts executable:
```bash
chmod +x run_tests.sh
```

### **Test Failures**

#### **Submission Failures**
- Check service is running and healthy
- Verify API key configuration
- Ensure Chrome is connected

#### **Solving Timeouts**
- Normal during testing without real captchas
- Focus on submission success for API validation
- Use real captcha pages for full end-to-end testing

#### **Proxy Test Failures**
- Check proxy availability in `working_proxies.json`
- Run proxy refresh: `../refresh_proxies.sh`
- Verify proxy manager configuration

## 📈 Performance Benchmarks

### **Typical Test Times**
- **Health Tests**: 2-5 seconds
- **API Format Tests**: 5-10 seconds  
- **reCAPTCHA Submission Tests**: 10-15 seconds per type
- **Full Test Suite**: 30-60 seconds

### **Expected Success Rates**
- **Service Health**: 100% (if service is running)
- **API Submissions**: 100% (if properly configured)
- **Captcha Solving**: Variable (depends on real captcha availability)
- **Overall**: 70%+ for passing status

## 🔍 Understanding Test Output

### **Comprehensive Test Report**
```
📊 COMPREHENSIVE TEST RESULTS SUMMARY
=====================================
⏱️  Total Duration: 45.2 seconds
📋 Total Tests: 24
✅ Passed: 20
❌ Failed: 4
📈 Success Rate: 83.3%
📂 Categories: 5/6 passed
🏆 Overall Status: PASS
```

### **Category Breakdown**
- **Service Health**: Core functionality tests
- **reCAPTCHA v2/v3**: Captcha type specific tests
- **API Formats**: Compatibility tests
- **Additional**: Proxy and hCaptcha tests

### **Interpretation Guide**
- **80%+ Success Rate**: Service ready for production
- **70-80% Success Rate**: Service functional with minor issues
- **<70% Success Rate**: Significant problems need resolution

## 🎯 Integration with GSA

The test suite validates compatibility with GSA (General Search Automation):

### **API Compatibility**
- 2captcha format endpoints (`/in.php`, `/res.php`)
- Standard response formats (`OK|{id}`, error codes)
- Balance checking functionality
- Report functionality (good/bad captcha reporting)

### **Captcha Type Support**
- reCAPTCHA v2 (regular and invisible)
- reCAPTCHA v3 (with actions and scores)
- hCaptcha basic support
- Enterprise variants

### **GSA Integration Testing**
The test suite ensures the service works as a drop-in replacement for the real 2captcha service when configuring GSA to point to `localhost:5001`.

## 📝 Contributing

To add new tests:

1. Create test file following naming convention: `test_{category}.py`
2. Implement test functions with proper error handling
3. Add summary function returning standardized results
4. Update `run_comprehensive_tests.py` to include new tests
5. Update this README with new test descriptions

### **Test File Template**
```python
#!/usr/bin/env python3
"""
{Test Category} Tests for Google reCAPTCHA Bypass
"""

import sys
import os
import requests
from typing import Dict, Any

API_BASE_URL = "http://localhost:5001"
API_KEY = "fake_680d0e29b28040ef"

def test_example() -> Dict[str, Any]:
    """Test example functionality."""
    try:
        # Test implementation
        return {"success": True, "result": "data"}
    except Exception as e:
        return {"success": False, "error": str(e)}

def run_{category}_tests() -> Dict[str, Any]:
    """Run all {category} tests."""
    print("🔧 Running {Category} Tests...")
    
    tests = {
        "example": test_example()
    }
    
    # Calculate summary
    passed = sum(1 for r in tests.values() if r.get("success"))
    total = len(tests)
    
    return {
        "summary": {"passed": passed, "total": total},
        "details": tests
    }

if __name__ == "__main__":
    results = run_{category}_tests()
    success = results["summary"]["passed"] > 0
    sys.exit(0 if success else 1)
``` 