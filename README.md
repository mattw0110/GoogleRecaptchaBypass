# Google Recaptcha Solver API

**We love bots ❤️, but Google doesn't.** So, here is the solution to bypass Google reCAPTCHA.

Solve Google reCAPTCHA less than 5 seconds! 🚀

This project provides a **fake 2captcha API service** for solving Google reCAPTCHA challenges. The service integrates perfectly with automation tools like GSA (General Search Automation) by providing a local 2captcha-compatible API with concurrent request handling and robust browser management.

## Recent Updates

- ✅ **Concurrent Request Handling**: Fixed browser instance conflicts for multiple simultaneous requests
- ✅ **Windows Chrome Debugging**: Dedicated Windows Chrome debugging script with better error reporting
- ✅ **GSA Configuration Fix**: Resolved hostname resolution issues (use `127.0.0.1:5001`)
- ✅ **Shared Browser Architecture**: Singleton browser pattern for improved performance and stability
- ✅ **Enhanced Error Handling**: Better recovery from Chrome connection failures
- ✅ **Health Monitoring**: Automatic Chrome debugging health checks and reconnection

### Sponsors

We need your help to keep this project alive. We could put your logo/banner here. Contact me Telegram: `s4rp3r`. This repo gets +100 visitors per day.

## 🚀 Quick Start

### Simple 3-Step Process

#### **🐧 Linux/macOS:**

**1. Setup (one time):**
```bash
# Clone and setup
git clone <repository-url>
cd GoogleRecaptchaBypass
./setup_automatic.sh
```

**2. Start the service:**
```bash
# Starts Chrome + fake 2captcha API service
./start_fake_2captcha_with_chrome.sh
```

**3. Test the setup:**
```bash
# Test the API endpoints
python test_fake_2captcha.py
```

#### **🪟 Windows:**

**1. Setup (one time):**
```cmd
# Clone and setup
git clone <repository-url>
cd GoogleRecaptchaBypass
setup_automatic.bat
```

**2. Start the service:**
```cmd
# Starts Chrome + fake 2captcha API service
start_fake_2captcha_with_chrome.bat
```

**3. Test the setup:**
```cmd
# Test the API endpoints
python test_fake_2captcha.py
```

That's it! Your fake 2captcha service is running on `http://localhost:5001`

## 🌐 How It Works

### **Architecture Overview**

1. **Shared Browser Instance**: Single Chrome instance with debugging shared across all requests
2. **Concurrent Processing**: Multiple captcha requests processed simultaneously
3. **Audio Recognition**: Solves reCAPTCHA challenges using Google Speech API  
4. **2captcha API Compatibility**: Perfect mimicry of real 2captcha.com API endpoints
5. **Health Monitoring**: Automatic Chrome connection monitoring and recovery
6. **Anti-Detection**: Uses proxy rotation and realistic browser behavior

### **Technical Implementation**

- **Browser Management**: Singleton pattern with shared Chrome debugging instance
- **Request Handling**: Concurrent processing with minimal locking
- **Error Recovery**: Automatic browser reconnection on failures
- **Request Tracking**: Unique request IDs for debugging and monitoring

## 📋 API Endpoints

The service provides both 2captcha-style and modern API endpoints:

**2captcha Compatible (for GSA):**
- `POST /in.php` - Submit captcha 
- `GET /res.php` - Get results
- `GET /user` - Check balance

**Modern API:**
- `POST /captcha` - Submit captcha (JSON)
- `GET /captcha/{id}` - Get result (JSON)
- `GET /health` - Health check

**Management Endpoints:**
- `GET /status` - Service status
- `GET /config` - Configuration info
- `GET /proxies` - Proxy information
- `POST /proxies/refresh` - Refresh proxy list

**API Key:** `fake_680d0e29b28040ef`

## 🛠️ GSA Integration

### **Quick GSA Setup:**

1. **Start the service:**
   ```bash
   # Linux/macOS
   ./start_fake_2captcha_with_chrome.sh
   
   # Windows  
   start_fake_2captcha_with_chrome.bat
   ```

2. **Configure GSA with standard 2captcha service:**
   - In GSA, select **"2captcha"** from the captcha service list
   - **Host/URL**: `127.0.0.1:5001` ⚠️ **Important: Use IP address, not localhost**
   - **API Key**: `fake_680d0e29b28040ef`
   
   **Important**: Use the existing **2captcha** service option in GSA, not a custom one. Your local service perfectly mimics the real 2captcha API, so GSA's standard 2captcha.ini configuration will work seamlessly.

### **Supported Captcha Types:**
- ✅ **reCAPTCHA v2** (invisible and checkbox)
- ✅ **reCAPTCHA v3** (with action and min_score)  
- ✅ **hCaptcha** (basic support)
- ✅ **Image Captchas** (basic support)
- ✅ **Text Captchas** (basic support)

### **Why This Works:**

Your local service is a **perfect 2captcha API clone**:
- ✅ **Identical endpoints**: `/in.php`, `/res.php` with same parameters
- ✅ **Exact response formats**: `OK|<id>`, `OK|<token>`, `CAPCHA_NOT_READY`, etc.
- ✅ **Same error codes**: `ERROR_CAPTCHA_UNSOLVABLE`, `ERROR_KEY_DOES_NOT_EXIST`, etc.
- ✅ **All captcha types**: userrecaptcha, hcaptcha, version=v3, etc.
- ✅ **Concurrent handling**: Multiple requests processed simultaneously

GSA's existing `2captcha.ini` file works perfectly because your service responds exactly like the real 2captcha.com API.

**GSA Configuration Summary:**
- **Service**: Select "2captcha" (the standard one)
- **Host**: `127.0.0.1:5001` 
- **API Key**: `fake_680d0e29b28040ef`
- **Done!** GSA will use its existing 2captcha.ini configuration

### **Troubleshooting GSA Connection:**

If GSA shows "http can not be resolved" or similar connection errors:

1. **Try IP address instead of localhost:**
   - **Host**: `127.0.0.1:5001` (instead of `localhost:5001`)

2. **Verify service is running:**
   ```bash
   curl http://127.0.0.1:5001/health
   curl "http://127.0.0.1:5001/res.php?key=fake_680d0e29b28040ef&action=getbalance"
   ```

3. **Check Windows firewall/antivirus** if connections are blocked

4. **Test Chrome debugging:**
   ```bash
   curl http://127.0.0.1:9222/json/version
   ```

## 🔧 Chrome Debugging Setup

### **Windows Users - Dedicated Chrome Debug Script**

If you're having Chrome debugging issues on Windows, use the dedicated script:

```cmd
# Run this first to test Chrome debugging
start_chrome_debug_windows.bat
```

This script provides:
- ✅ **Better error reporting** with detailed troubleshooting steps
- ✅ **Automatic Chrome path detection** across different installation locations
- ✅ **Process cleanup** to avoid conflicts
- ✅ **Connection testing** to verify debugging is working
- ✅ **Administrator guidance** for permission issues

### **Manual Chrome Debugging (All Platforms)**

**Windows:**
```cmd
# Kill existing Chrome
taskkill /IM chrome.exe /F

# Start with debugging
"C:\Program Files\Google\Chrome\Application\chrome.exe" --remote-debugging-port=9222 --headless=new --user-data-dir=%TEMP%\chrome-debug

# Test connection
curl http://127.0.0.1:9222/json/version
```

**Linux/macOS:**
```bash
# Kill existing Chrome
pkill -f chrome

# Start with debugging
google-chrome --remote-debugging-port=9222 --headless=new --user-data-dir=/tmp/chrome-debug

# Test connection
curl http://127.0.0.1:9222/json/version
```

## 📁 Project Structure

```
GoogleRecaptchaBypass/
├── fake_2captcha_app.py                    # Main Flask API service
├── RecaptchaSolver.py                      # Core reCAPTCHA solving logic  
├── chrome_manager.py                       # Chrome instance management
├── proxy_manager.py                        # Proxy management for anti-detection
├── start_fake_2captcha_with_chrome.sh      # Main startup script (Linux/macOS)
├── start_fake_2captcha_with_chrome.bat     # Main startup script (Windows)
├── start_chrome_debug_windows.bat          # Windows Chrome debugging script
├── setup_automatic.sh                      # One-time setup script (Linux/macOS)
├── setup_automatic.bat                     # One-time setup script (Windows)
├── refresh_proxies.py                      # Proxy refresh tool (Python)
├── refresh_proxies.sh                      # Proxy refresh script (Linux/macOS)
├── refresh_proxies.bat                     # Proxy refresh script (Windows)
├── test/                                   # Comprehensive test suite
│   ├── run_tests.sh                        # Test runner script
│   ├── run_comprehensive_tests.py          # Main test orchestrator
│   ├── test_service_health.py              # Service health tests
│   ├── test_recaptcha_v2.py                # reCAPTCHA v2 tests
│   ├── test_recaptcha_v3.py                # reCAPTCHA v3 tests
│   ├── test_api_formats.py                 # API format compatibility tests
│   └── README.md                           # Test documentation
├── test_fake_2captcha.py                   # Legacy test (kept for compatibility)
├── requirements.txt                        # Python dependencies
├── working_proxies.json                    # Proxy list
└── README.md                               # This file
```

## 🔧 Advanced Configuration

### Environment Variables

Create a `.env` file:
```env
FAKE_2CAPTCHA_API_KEY=your_custom_key_here
PORT=5001
```

### Proxy Management

The service includes automatic proxy rotation for anti-detection:

#### **Automatic Proxy Refresh:**
```bash
# Linux/macOS
./refresh_proxies.sh

# Windows  
refresh_proxies.bat
```

#### **Manual Proxy Refresh:**
```bash
# Standard refresh (50 proxies)
python refresh_proxies.py

# Force refresh with cleanup
python refresh_proxies.py --force --clean

# Quick refresh (25 proxies)
python refresh_proxies.py --test-count 25

# Full refresh (100 proxies)  
python refresh_proxies.py --test-count 100

# Show current proxy stats
python refresh_proxies.py --stats
```

#### **Proxy Configuration Options:**
- **Automatic sources**: Fetches from GitHub proxy repositories
- **Testing**: Verifies proxy response times and functionality
- **Rotation**: Uses different proxies for each request
- **Cleanup**: Removes failed proxies automatically
- **Persistence**: Saves working proxies to `working_proxies.json`

#### **Manual Proxy Configuration:**
Edit `working_proxies.json` to add custom proxies:
```json
{
  "proxies": [
    {
      "proxy": "http://proxy1:port",
      "response_time": 1.2,
      "ip": "1.2.3.4",
      "success_count": 0,
      "fail_count": 0
    }
  ]
}
```

### Chrome Configuration

The service uses these Chrome flags for optimal performance:
- `--headless=new` - New headless mode
- `--remote-debugging-port=9222` - Remote debugging
- `--no-sandbox` - Disable sandbox for server environments
- `--disable-web-security` - Bypass security restrictions

## 🧪 Testing

### **Quick Health Check:**
```bash
# Test service availability
curl http://127.0.0.1:5001/health

# Test balance endpoint (what GSA uses)
curl "http://127.0.0.1:5001/res.php?key=fake_680d0e29b28040ef&action=getbalance"

# Test Chrome debugging
curl http://127.0.0.1:9222/json/version
```

### **Full Test Suite:**
```bash
# Run comprehensive tests
python test_fake_2captcha.py

# Or run the full test suite
cd test/
./run_tests.sh
```

### **API Testing Examples:**

**Submit a captcha:**
```bash
curl -X POST http://127.0.0.1:5001/in.php \
  -d "key=fake_680d0e29b28040ef" \
  -d "method=userrecaptcha" \
  -d "googlekey=6Le-wvkSAAAAAPBMRTvw0Q4Muexq9bi0DJwx_mJ-" \
  -d "pageurl=https://www.google.com/recaptcha/api2/demo"
```

**Get results:**
```bash
curl "http://127.0.0.1:5001/res.php?key=fake_680d0e29b28040ef&action=get&id=CAPTCHA_ID"
```

## 🛠️ Troubleshooting

### **Common Issues**

#### **1. GSA Connection Issues**
```
Error: "http can not be resolved"
```
**Solution**: Use `127.0.0.1:5001` instead of `localhost:5001` in GSA configuration.

#### **2. Chrome Debugging Failed**
```
Error: "Failed to connect to existing Chrome"
```
**Solutions**:
- **Windows**: Run `start_chrome_debug_windows.bat` first
- **Linux/macOS**: Check if Chrome is running with `ps aux | grep chrome`
- **All platforms**: Verify port 9222 is accessible: `curl http://127.0.0.1:9222/json/version`

#### **3. Mock Tokens Instead of Real Tokens**
```
Log: "Using mock token for testing"
```
**Cause**: Chrome debugging connection is failing
**Solutions**:
1. Ensure Chrome debugging is working (see above)
2. Check service logs for Chrome connection errors
3. Verify no antivirus is blocking Chrome debugging
4. Try running as administrator (Windows)

#### **4. Service Not Starting**
```
Error: "Port 5001 already in use"
```
**Solutions**:
```bash
# Windows
netstat -ano | findstr :5001
taskkill /PID [PID] /F

# Linux/macOS
lsof -ti:5001 | xargs kill -9
```

#### **5. High Request Volume Issues**
The service now handles concurrent requests properly with a shared browser instance. If you're still experiencing issues:
- Check Chrome memory usage
- Verify proxy rotation is working
- Monitor service logs for connection errors

### **Windows-Specific Issues**

#### **Windows Defender/Antivirus**
Add exclusions for:
- Chrome executable
- Project directory  
- Port 9222 and 5001

#### **User Permissions**
- Run Command Prompt as Administrator
- Ensure Chrome can create temporary profiles

#### **Chrome Installation Paths**
The service checks these locations automatically:
- `C:\Program Files\Google\Chrome\Application\chrome.exe`
- `C:\Program Files (x86)\Google\Chrome\Application\chrome.exe`  
- `%LOCALAPPDATA%\Google\Chrome\Application\chrome.exe`

### **Debug Mode**

Enable verbose logging by setting environment variable:
```bash
export DEBUG=1  # Linux/macOS
set DEBUG=1     # Windows
```

### **Performance Monitoring**

Check service status:
```bash
curl http://127.0.0.1:5001/status
```

Monitor Chrome debugging:
```bash
curl http://127.0.0.1:9222/json/list
```

## 📊 Performance & Scaling

### **Concurrent Request Handling**
- ✅ **Shared browser instance** - Single Chrome process for all requests
- ✅ **Minimal locking** - Brief locks only for browser access
- ✅ **Request queuing** - Multiple requests processed efficiently
- ✅ **Health monitoring** - Automatic recovery from failures

### **Expected Performance**
- **Response time**: 5-30 seconds per captcha
- **Concurrent requests**: 10+ simultaneous requests supported
- **Success rate**: 80-95% depending on captcha complexity
- **Memory usage**: ~200-500MB including Chrome

### **Scaling Considerations**
- **Chrome memory**: Monitor Chrome process memory usage
- **Proxy rotation**: Ensure sufficient working proxies
- **Request timeout**: GSA may timeout on slow captchas
- **Rate limiting**: Some sites may rate limit requests

## 🤝 Contributing

### **Development Setup**
```bash
# Clone repository
git clone <repository-url>  
cd GoogleRecaptchaBypass

# Install dependencies
pip install -r requirements.txt

# Run tests
python test_fake_2captcha.py
```

### **Adding New Features**
1. Create feature branch
2. Add tests for new functionality
3. Update README if needed
4. Submit pull request

### **Reporting Issues**
Include in bug reports:
- Operating system and version
- Chrome version
- Service logs
- GSA configuration (if applicable)

## 📄 License

This project is for educational purposes only. Use responsibly and in accordance with the terms of service of the websites you're accessing.

## 🔗 Links

- **Telegram**: `s4rp3r` (for support)
- **Issues**: Create GitHub issues for bugs and feature requests
- **Discussions**: GitHub discussions for questions and help

---

**⚠️ Disclaimer**: This tool is for educational and testing purposes only. Always respect website terms of service and use automation responsibly.
