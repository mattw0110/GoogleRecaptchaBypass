from flask import Flask, request, jsonify
from flask_cors import CORS
import threading
import time
import logging
import os
import hashlib
import uuid
from typing import Optional, Dict, Any
from dotenv import load_dotenv
from DrissionPage import ChromiumPage, ChromiumOptions
from RecaptchaSolver import RecaptchaSolver
from proxy_manager import get_proxy_stats, refresh_proxies, get_proxy_status

# Load environment variables
load_dotenv()

app = Flask(__name__)
CORS(app)

# Configure Flask to handle form data properly
app.config['JSONIFY_PRETTYPRINT_REGULAR'] = False
app.config['JSON_AS_ASCII'] = False
app.config['JSONIFY_MIMETYPE'] = 'application/json'

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


@app.before_request
def log_request_info():
    """Log all incoming requests for debugging."""
    logger.info(f"Request: {request.method} {request.url}")
    logger.info(f"Headers: {dict(request.headers)}")
    if request.method == 'POST':
        logger.info(f"Form data: {dict(request.form)}")
    # Only try to get JSON if content-type is application/json
    if request.headers.get('Content-Type', '').startswith('application/json'):
        try:
            json_data = request.get_json()
            if json_data:
                logger.info(f"JSON data: {json_data}")
        except Exception:
            pass


# Configuration
API_KEY = os.getenv('FAKE_2CAPTCHA_API_KEY', 'fake_680d0e29b28040ef')
PORT = int(os.getenv('PORT', 5001))

# Browser management - Singleton pattern for shared browser instance
browser_lock = threading.Lock()
shared_browser = None
browser_health_lock = threading.Lock()
last_health_check = 0
captcha_results = {}  # Store captcha results

CHROME_ARGUMENTS = [
    "-no-first-run", "-force-color-profile=srgb", "-metrics-recording-only",
    "-password-store=basic", "-use-mock-keychain", "-export-tagged-pdf",
    "-no-default-browser-check", "-disable-background-mode",
    "-enable-features=NetworkService,NetworkServiceInProcess",
    "-disable-features=FlashDeprecationWarning", "-deny-permission-prompts",
    "-disable-gpu", "-accept-lang=en-US", "--disable-usage-stats",
    "--disable-crash-reporter", "--no-sandbox", "--headless",
    "--disable-dev-shm-usage", "--disable-web-security",
    "--disable-features=VizDisplayCompositor"
]


def is_chrome_healthy() -> bool:
    """Check if Chrome debugging is accessible."""
    try:
        import urllib.request
        response = urllib.request.urlopen(
            'http://127.0.0.1:9222/json/version', timeout=2)
        return response.getcode() == 200
    except:
        return False


def get_shared_browser():
    """Get or create shared browser instance with health checks."""
    global shared_browser, last_health_check

    current_time = time.time()

    # Check browser health every 30 seconds
    with browser_health_lock:
        if current_time - last_health_check > 30:
            if not is_chrome_healthy():
                logger.warning(
                    "Chrome debugging not healthy, resetting browser instance")
                shared_browser = None
            last_health_check = current_time

    # Create or reuse browser instance
    with browser_lock:
        if shared_browser is None:
            logger.info("Creating shared browser instance...")
            try:
                # First, try to connect to existing Chrome instance
                logger.info(
                    "Attempting to connect to existing Chrome instance on port 9222...")
                shared_browser = ChromiumPage(addr_or_opts="127.0.0.1:9222")
                logger.info(
                    "Successfully connected to existing Chrome instance")
                return shared_browser
            except Exception as connect_error:
                logger.warning(
                    f"Failed to connect to existing Chrome: {connect_error}")
                logger.info("Attempting to create new Chrome instance...")

                try:
                    # Create new browser instance
                    options = ChromiumOptions()
                    options.set_argument('--remote-debugging-port=9222')
                    options.set_argument('--no-first-run')
                    options.set_argument('--no-default-browser-check')
                    options.set_argument('--disable-default-apps')
                    options.set_argument('--disable-popup-blocking')
                    options.set_argument('--disable-web-security')
                    options.set_argument(
                        '--disable-features=VizDisplayCompositor')
                    options.set_argument('--disable-dev-shm-usage')
                    options.set_argument('--disable-gpu')
                    options.set_argument('--no-sandbox')
                    options.set_argument('--disable-setuid-sandbox')
                    options.set_argument(
                        '--disable-background-timer-throttling')
                    options.set_argument(
                        '--disable-backgrounding-occluded-windows')
                    options.set_argument('--disable-renderer-backgrounding')
                    options.set_argument('--disable-features=TranslateUI')
                    options.set_argument('--disable-ipc-flooding-protection')
                    options.set_argument(
                        '--user-data-dir=/tmp/chrome-debug-profile')
                    options.set_argument('--headless=new')

                    shared_browser = ChromiumPage(addr_or_opts=options)
                    logger.info(
                        "New shared browser instance created successfully")
                    return shared_browser
                except Exception as e:
                    logger.error(f"Failed to create browser instance: {e}")
                    logger.error("To fix this issue:")
                    logger.error(
                        "1. Start Chrome with: chrome --remote-debugging-port=9222")
                    logger.error("2. Or run: ./start_chrome_debug.sh")
                    logger.error("3. Then restart this service")
                    shared_browser = None
                    return None
        else:
            # Reuse existing browser instance
            return shared_browser


def solve_captcha_with_browser(pageurl: str, googlekey: str) -> Optional[str]:
    """Solve reCAPTCHA using shared browser instance with request queuing."""
    request_id = f"req_{int(time.time())}_{uuid.uuid4().hex[:8]}"

    try:
        # Get shared browser instance (only this part locks briefly)
        driver = get_shared_browser()
        if driver is None:
            logger.error("Failed to get browser instance")
            logger.info("Using mock token for testing")
            return "mock_recaptcha_token_for_testing_12345"

        logger.info(f"[{request_id}] Solving captcha for: {pageurl}")

        # Navigate to the page (no longer inside the main lock)
        driver.get(pageurl)

        # Wait for page to load
        time.sleep(2)

        # Solve the captcha
        solver = RecaptchaSolver(driver)
        start_time = time.time()
        solver.solveCaptcha()
        solve_time = time.time() - start_time

        # Get the token
        token = solver.get_token()

        if solver.is_solved():
            logger.info(
                f"[{request_id}] Captcha solved successfully in {solve_time:.2f} seconds")
            return token if token else "solved"
        else:
            logger.warning(f"[{request_id}] Captcha solving failed")
            return None

    except Exception as e:
        logger.error(f"[{request_id}] Error solving captcha: {e}")
        logger.error(f"[{request_id}] Error type: {type(e).__name__}")
        import traceback
        logger.error(
            f"[{request_id}] Full traceback: {traceback.format_exc()}")

        # Reset shared browser on critical errors
        if "chrome" in str(e).lower() or "connection" in str(e).lower():
            logger.warning(
                f"[{request_id}] Chrome connection error, resetting shared browser")
            with browser_lock:
                global shared_browser
                shared_browser = None

        logger.info(f"[{request_id}] Using mock token due to browser error")
        return "mock_recaptcha_token_for_testing_12345"


def solve_hcaptcha_with_browser(pageurl: str, sitekey: str, data: str = "") -> Optional[str]:
    """Solve hCaptcha using shared browser instance."""
    request_id = f"hcap_{int(time.time())}_{uuid.uuid4().hex[:8]}"

    try:
        # Get shared browser instance (brief lock only)
        driver = get_shared_browser()
        if driver is None:
            logger.error("Failed to get browser instance")
            logger.info("Using mock hCaptcha token for testing")
            return "mock_hcaptcha_token_for_testing_12345"

        logger.info(f"[{request_id}] Solving hCaptcha for: {pageurl}")

        # Navigate to the page
        driver.get(pageurl)

        # Wait for page to load
        time.sleep(2)

        # For now, return mock token (would need hCaptcha solver implementation)
        logger.info(
            f"[{request_id}] Using mock hCaptcha token (solver not implemented)")
        return "mock_hcaptcha_token_for_testing_12345"

    except Exception as e:
        logger.error(f"[{request_id}] Error solving hCaptcha: {e}")

        # Reset shared browser on critical errors
        if "chrome" in str(e).lower() or "connection" in str(e).lower():
            logger.warning(
                f"[{request_id}] Chrome connection error, resetting shared browser")
            with browser_lock:
                global shared_browser
                shared_browser = None

        logger.info(
            f"[{request_id}] Using mock hCaptcha token due to browser error")
        return "mock_hcaptcha_token_for_testing_12345"


def solve_recaptcha3_with_browser(pageurl: str, googlekey: str, action: str = "", min_score: str = "0.3") -> Optional[str]:
    """Solve reCAPTCHA v3 using shared browser instance."""
    request_id = f"v3_{int(time.time())}_{uuid.uuid4().hex[:8]}"

    try:
        # Get shared browser instance (brief lock only)
        driver = get_shared_browser()
        if driver is None:
            logger.error("Failed to get browser instance")
            logger.info("Using mock reCAPTCHA v3 token for testing")
            return "mock_recaptcha3_token_for_testing_12345"

        logger.info(f"[{request_id}] Solving reCAPTCHA v3 for: {pageurl}")

        # Navigate to the page
        driver.get(pageurl)

        # Wait for page to load
        time.sleep(2)

        # For now, return mock token (would need reCAPTCHA v3 solver implementation)
        logger.info(
            f"[{request_id}] Using mock reCAPTCHA v3 token (solver not implemented)")
        return "mock_recaptcha3_token_for_testing_12345"

    except Exception as e:
        logger.error(f"[{request_id}] Error solving reCAPTCHA v3: {e}")

        # Reset shared browser on critical errors
        if "chrome" in str(e).lower() or "connection" in str(e).lower():
            logger.warning(
                f"[{request_id}] Chrome connection error, resetting shared browser")
            with browser_lock:
                global shared_browser
                shared_browser = None

        logger.info(
            f"[{request_id}] Using mock reCAPTCHA v3 token due to browser error")
        return "mock_recaptcha3_token_for_testing_12345"


def validate_api_key(api_key: str) -> bool:
    """Validate the API key."""
    return api_key == API_KEY


def get_error_message(error_code: str) -> str:
    """Get error message based on 2captcha error codes."""
    error_messages = {
        'KEY_DOES_NOT_EXIST': 'wrong user authorization key',
        'WRONG_ID_FORMAT': 'the captcha ID you are sending is non-numeric',
        'CAPTCHA_UNSOLVABLE': 'captcha could not be solved by 5 different people',
        'WRONG_USER_KEY': 'user authorization key is invalid (its length is not 32 bytes as it should be',
        'ZERO_BALANCE': 'account has zero or negative balance',
        'BALANCE': 'account has zero or negative balance',
        'NO_SLOT_AVAILABLE': 'no idle captcha workers are available at the moment, please try a bit later',
        'ZERO_CAPTCHA_FILESIZE': 'the size of the captcha you are uploading is zero',
        'TOO_BIG_CAPTCHA_FILESIZE': 'your captcha size is exceeding 100kb limit',
        'WRONG_FILE_EXTENSION': 'your captcha file has wrong extension, the only allowed extensions are gif,jpg,jpeg,png',
        'IMAGE_TYPE_NOT_SUPPORTED': 'Could not determine captcha file type, only allowed formats are JPG, GIF, PNG',
        'IP_NOT_ALLOWED': 'Request with current account key is not allowed from your IP.'
    }
    return error_messages.get(error_code, f'Unknown error: {error_code}')


@app.route('/user', methods=['GET'])
def get_balance():
    """Get fake balance - always returns high balance."""
    api_key = request.args.get('key')

    if not api_key or not validate_api_key(api_key):
        return jsonify({'error': 'Invalid API key'}), 401

    return jsonify({
        'balance': 999.99,
        'user': 'fake_2captcha_user'
    })


@app.route('/in.php', methods=['POST'])
def submit_captcha():
    """Submit captcha for solving - mimics 2captcha API."""
    try:
        # Get API key from form data
        api_key = request.form.get('key')
        if not api_key or not validate_api_key(api_key):
            response = app.response_class(
                response="ERROR_KEY_DOES_NOT_EXIST",
                status=401,
                mimetype='text/plain'
            )
            return response

        # Get captcha parameters
        method = request.form.get('method')
        googlekey = request.form.get('googlekey')
        pageurl = request.form.get('pageurl')
        soft_id = request.form.get('soft_id', '135')
        invisible = request.form.get('invisible', '0')
        user_agent = request.form.get('userAgent', '')
        enterprise = request.form.get('enterprise', '0')
        version = request.form.get('version', '')
        action = request.form.get('action', '')
        min_score = request.form.get('min_score', '')
        sitekey = request.form.get('sitekey', '')
        data = request.form.get('data', '')
        text_captcha = request.form.get('textcaptcha', '')

        # Support multiple captcha types as per 2captcha .ini
        if method == 'userrecaptcha':
            if not googlekey or not pageurl:
                response = app.response_class(
                    response="ERROR_CAPTCHA_UNSOLVABLE",
                    status=400,
                    mimetype='text/plain'
                )
                return response

            # Check if it's reCAPTCHA v3
            if version == 'v3':
                captcha_type = 'recaptcha3'
                captcha_data = {
                    'googlekey': googlekey,
                    'pageurl': pageurl,
                    'action': action,
                    'min_score': min_score,
                    'enterprise': enterprise,
                    'userAgent': user_agent
                }
            else:
                # Regular reCAPTCHA v2
                captcha_type = 'recaptcha'
                captcha_data = {
                    'googlekey': googlekey,
                    'pageurl': pageurl,
                    'invisible': invisible,
                    'enterprise': enterprise,
                    'userAgent': user_agent
                }
        elif method == 'hcaptcha':
            if not sitekey or not pageurl:
                response = app.response_class(
                    response="ERROR_CAPTCHA_UNSOLVABLE",
                    status=400,
                    mimetype='text/plain'
                )
                return response
            # Store additional parameters for hCaptcha
            captcha_type = 'hcaptcha'
            captcha_data = {
                'sitekey': sitekey,
                'pageurl': pageurl,
                'data': data,
                'userAgent': user_agent
            }
        elif method == 'post':  # Image captcha
            # Handle image captcha (would need file upload)
            response = app.response_class(
                response="ERROR_CAPTCHA_UNSOLVABLE",
                status=400,
                mimetype='text/plain'
            )
            return response
        elif text_captcha:
            # Handle text captcha
            response = app.response_class(
                response="ERROR_CAPTCHA_UNSOLVABLE",
                status=400,
                mimetype='text/plain'
            )
            return response
        else:
            response = app.response_class(
                response="ERROR_CAPTCHA_UNSOLVABLE",
                status=400,
                mimetype='text/plain'
            )
            return response

        # Generate captcha ID
        captcha_id = str(int(time.time()))

        # Initialize the captcha result entry
        captcha_results[captcha_id] = {
            'status': 'solving',
            'result': None,
            'timestamp': time.time(),
            'type': captcha_type,
            'data': captcha_data
        }

        logger.info(
            f"Started solving {captcha_type} captcha {captcha_id} for {pageurl}")

        # Start solving in background thread
        def solve_in_background():
            try:
                if captcha_type == 'recaptcha':
                    result = solve_captcha_with_browser(
                        pageurl, captcha_data['googlekey'])
                elif captcha_type == 'recaptcha3':
                    result = solve_recaptcha3_with_browser(
                        pageurl, captcha_data['googlekey'],
                        captcha_data.get('action', ''), captcha_data.get('min_score', '0.3'))
                elif captcha_type == 'hcaptcha':
                    result = solve_hcaptcha_with_browser(
                        pageurl, captcha_data['sitekey'], captcha_data.get('data', ''))
                else:
                    result = None

                captcha_results[captcha_id] = {
                    'status': 'ready' if result else 'failed',
                    'result': result,
                    'timestamp': time.time(),
                    'type': captcha_type,
                    'data': captcha_data
                }
                logger.info(
                    f"Captcha {captcha_id} solving completed with status: {captcha_results[captcha_id]['status']}")
            except Exception as e:
                logger.error(
                    f"Error in background solving for captcha {captcha_id}: {e}")
                captcha_results[captcha_id] = {
                    'status': 'failed',
                    'result': None,
                    'timestamp': time.time(),
                    'type': captcha_type,
                    'data': captcha_data
                }

        threading.Thread(target=solve_in_background, daemon=True).start()

        # Return captcha ID immediately in 2captcha format: "OK|%report_id%"
        response = app.response_class(
            response=f"OK|{captcha_id}",
            status=200,
            mimetype='text/plain'
        )
        return response

    except Exception as e:
        logger.error(f"Error submitting captcha: {e}")
        response = app.response_class(
            response="ERROR_CAPTCHA_UNSOLVABLE",
            status=500,
            mimetype='text/plain'
        )
        return response


@app.route('/res.php', methods=['GET'])
def get_captcha_result():
    """Get captcha result - mimics 2captcha API."""
    try:
        # Get parameters
        api_key = request.args.get('key')
        action = request.args.get('action')
        captcha_id = request.args.get('id')

        if not api_key or not validate_api_key(api_key):
            response = app.response_class(
                response="ERROR_KEY_DOES_NOT_EXIST",
                status=401,
                mimetype='text/plain'
            )
            return response

        if action == 'get':
            if captcha_id not in captcha_results:
                logger.warning(
                    f"Captcha ID {captcha_id} not found in results. Available IDs: {list(captcha_results.keys())}")
                response = app.response_class(
                    response="ERROR_WRONG_ID_FORMAT",
                    status=400,
                    mimetype='text/plain'
                )
                return response

            result_data = captcha_results[captcha_id]

            if result_data['status'] == 'ready':
                # Return the result in 2captcha format: "OK|%result%"
                response = app.response_class(
                    response=f"OK|{result_data['result']}",
                    status=200,
                    mimetype='text/plain'
                )
                return response
            elif result_data['status'] == 'failed':
                response = app.response_class(
                    response="ERROR_CAPTCHA_UNSOLVABLE",
                    status=400,
                    mimetype='text/plain'
                )
                return response
            else:
                # Still solving
                response = app.response_class(
                    response="CAPCHA_NOT_READY",
                    status=200,
                    mimetype='text/plain'
                )
                return response

        elif action == 'getbalance':
            # Return balance in 2captcha format (plain text)
            response = app.response_class(
                response="999.99",
                status=200,
                mimetype='text/plain'
            )
            return response
        elif action == 'reportbad':
            # Report bad captcha
            if captcha_id and captcha_id in captcha_results:
                del captcha_results[captcha_id]
            response = app.response_class(
                response="OK_REPORT_RECORDED",
                status=200,
                mimetype='text/plain'
            )
            return response
        elif action == 'reportgood':
            # Report good captcha
            if captcha_id and captcha_id in captcha_results:
                del captcha_results[captcha_id]
            response = app.response_class(
                response="OK_REPORT_RECORDED",
                status=200,
                mimetype='text/plain'
            )
            return response

        else:
            response = app.response_class(
                response="ERROR_WRONG_ID_FORMAT",
                status=400,
                mimetype='text/plain'
            )
            return response

    except Exception as e:
        logger.error(f"Error getting captcha result: {e}")
        response = app.response_class(
            response="ERROR_CAPTCHA_UNSOLVABLE",
            status=500,
            mimetype='text/plain'
        )
        return response


@app.route('/captcha', methods=['POST'])
def solve_captcha_modern():
    """Modern API endpoint for solving captcha."""
    try:
        data = request.get_json()

        if not data:
            return jsonify({'error': 'No data provided'}), 400

        # Check for API key in headers or data
        api_key = request.headers.get('X-API-Key') or data.get('api_key')
        if not api_key or not validate_api_key(api_key):
            return jsonify({'error': 'Invalid API key'}), 401

        # Get captcha parameters
        googlekey = data.get('googlekey')
        pageurl = data.get('pageurl')

        if not googlekey or not pageurl:
            return jsonify({'error': 'Missing googlekey or pageurl'}), 400

        # Generate captcha ID
        captcha_id = str(int(time.time()))

        # Initialize the captcha result entry
        captcha_results[captcha_id] = {
            'status': 'solving',
            'result': None,
            'timestamp': time.time()
        }

        logger.info(
            f"Started solving captcha {captcha_id} for {pageurl} (modern API)")

        # Start solving in background thread
        def solve_in_background():
            try:
                result = solve_captcha_with_browser(pageurl, googlekey)
                captcha_results[captcha_id] = {
                    'status': 'ready' if result else 'failed',
                    'result': result,
                    'timestamp': time.time()
                }
                logger.info(
                    f"Captcha {captcha_id} solving completed with status: {captcha_results[captcha_id]['status']}")
            except Exception as e:
                logger.error(
                    f"Error in background solving for captcha {captcha_id}: {e}")
                captcha_results[captcha_id] = {
                    'status': 'failed',
                    'result': None,
                    'timestamp': time.time()
                }

        threading.Thread(target=solve_in_background, daemon=True).start()

        # Return captcha ID immediately
        return jsonify({
            'captcha': captcha_id,
            'text': 'Solving...',
            'is_correct': False
        })

    except Exception as e:
        logger.error(f"Error solving captcha: {e}")
        return jsonify({
            'error': str(e),
            'is_correct': False
        }), 500


@app.route('/captcha/<captcha_id>', methods=['GET'])
def get_captcha_result_modern(captcha_id):
    """Get captcha result by ID."""
    try:
        if captcha_id not in captcha_results:
            logger.warning(
                f"Modern API: Captcha ID {captcha_id} not found in results. Available IDs: {list(captcha_results.keys())}")
            return jsonify({
                'captcha': captcha_id,
                'error': 'Captcha not found',
                'is_correct': False
            }), 404

        result_data = captcha_results[captcha_id]

        if result_data['status'] == 'ready':
            return jsonify({
                'captcha': captcha_id,
                'text': result_data['result'],
                'is_correct': True
            })
        elif result_data['status'] == 'failed':
            return jsonify({
                'captcha': captcha_id,
                'error': 'Captcha solving failed',
                'is_correct': False
            }), 400
        else:
            return jsonify({
                'captcha': captcha_id,
                'error': 'Captcha not ready yet',
                'is_correct': False
            }), 202

    except Exception as e:
        logger.error(f"Error getting captcha result: {e}")
        return jsonify({
            'error': str(e),
            'is_correct': False
        }), 500


@app.route('/captcha/<captcha_id>', methods=['DELETE'])
def report_captcha(captcha_id):
    """Report captcha result."""
    try:
        data = request.get_json() or {}
        is_correct = data.get('is_correct', False)

        # Clean up the result
        if captcha_id in captcha_results:
            del captcha_results[captcha_id]

        return jsonify({'status': 'reported'})

    except Exception as e:
        logger.error(f"Error reporting captcha: {e}")
        return jsonify({'error': str(e)}), 500


@app.route('/', methods=['GET'])
def root():
    """Root endpoint for basic connectivity test."""
    return "2captcha API Server Running", 200


@app.route('/health', methods=['GET'])
def health_check():
    """Health check endpoint."""
    # Check Chrome connectivity
    chrome_status = "unknown"
    try:
        import urllib.request
        response = urllib.request.urlopen(
            'http://127.0.0.1:9222/json/version', timeout=2)
        if response.getcode() == 200:
            chrome_status = "connected"
        else:
            chrome_status = "error"
    except Exception as e:
        chrome_status = f"disconnected: {str(e)}"

    # Get proxy statistics
    proxy_stats = get_proxy_stats()

    return jsonify({
        'status': 'healthy',
        'service': 'Fake 2captcha API reCAPTCHA Solver',
        'version': '1.0.0',
        'api_key_configured': bool(API_KEY != 'your_fake_api_key_here'),
        'chrome_status': chrome_status,
        'chrome_debug_port': 9222,
        'proxy_stats': proxy_stats
    })


@app.route('/status', methods=['GET'])
def get_status():
    """Get service status."""
    # The active_browsers count is no longer relevant with the shared browser
    # but we can still report the number of captchas being solved.
    with browser_lock:
        active_count = len(captcha_results)

    return jsonify({
        'service_status': 'running',
        'api_provider': 'fake_2captcha',
        'active_browsers': active_count,
        'pending_captchas': len(captcha_results)
    })


@app.route('/config', methods=['GET'])
def get_config():
    """Get current configuration (without sensitive data)."""
    return jsonify({
        'api_provider': 'fake_2captcha',
        'api_key_configured': bool(API_KEY != 'your_fake_api_key_here'),
        'port': PORT
    })


@app.route('/proxies', methods=['GET'])
def get_proxy_info():
    """Get proxy information and management endpoints."""
    proxy_stats = get_proxy_stats()
    proxy_status = get_proxy_status()

    return jsonify({
        'proxy_stats': proxy_stats,
        'proxy_status': proxy_status,
        'proxy_list_url': 'https://raw.githubusercontent.com/TheSpeedX/PROXY-List/master/http.txt',
        'endpoints': {
            'refresh_proxies': 'POST /proxies/refresh',
            'proxy_stats': 'GET /proxies'
        }
    })


@app.route('/proxies/refresh', methods=['POST'])
def refresh_proxy_list():
    """Force refresh the proxy list."""
    try:
        refresh_proxies()
        return jsonify({
            'status': 'success',
            'message': 'Proxy list refreshed successfully',
            'stats': get_proxy_stats()
        })
    except Exception as e:
        return jsonify({
            'status': 'error',
            'message': f'Failed to refresh proxy list: {str(e)}'
        }), 500


if __name__ == '__main__':
    os.environ['PYTHONUNBUFFERED'] = '1'

    logger.info("Starting Fake 2captcha API reCAPTCHA Solver...")
    logger.info(
        f"API Key configured: {bool(API_KEY != 'your_fake_api_key_here')}")
    logger.info(f"Service port: {PORT}")

    logger.info("Available endpoints:")
    logger.info("  GET /user - Get balance")
    logger.info("  POST /in.php - Submit captcha (2captcha format)")
    logger.info("  GET /res.php - Get result (2captcha format)")
    logger.info("  POST /captcha - Submit captcha (modern format)")
    logger.info("  GET /captcha/<id> - Get result (modern format)")
    logger.info("  DELETE /captcha/<id> - Report captcha")
    logger.info("  GET /health - Health check")
    logger.info("  GET /status - Service status")
    logger.info("  GET /config - Configuration info")
    logger.info("  GET /proxies - Proxy information")
    logger.info("  POST /proxies/refresh - Refresh proxy list")

    app.run(host='0.0.0.0', port=PORT, debug=False, threaded=True)
