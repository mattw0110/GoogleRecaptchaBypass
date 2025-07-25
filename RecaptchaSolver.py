import os
import urllib.request
import random
import pydub
import speech_recognition as sr
import time
import math
from typing import Optional
from DrissionPage import ChromiumPage
from proxy_manager import get_proxy, get_proxy_dict, mark_proxy_success, mark_proxy_failure


class RecaptchaSolver:
    """A class to solve reCAPTCHA challenges using audio recognition with anti-detection measures."""

    # Constants
    TEMP_DIR = os.getenv("TEMP") if os.name == "nt" else "/tmp"
    TIMEOUT_STANDARD = 10
    TIMEOUT_SHORT = 2
    TIMEOUT_DETECTION = 0.05

    def __init__(self, driver: ChromiumPage) -> None:
        """Initialize the solver with a ChromiumPage driver.

        Args:
            driver: ChromiumPage instance for browser interaction
        """
        self.driver = driver
        self.current_proxy = None
        self._setup_anti_detection()

    def _setup_anti_detection(self) -> None:
        """Setup anti-detection measures for the browser."""
        try:
            # Get a proxy for this session
            self.current_proxy = get_proxy()
            if self.current_proxy:
                print(f"Using proxy: {self.current_proxy}")
                # Note: DrissionPage doesn't directly support proxy configuration
                # We'll use it for other requests that support proxies

            # Set realistic user agent
            self.driver.set.user_agent(
                "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/138.0.0.0 Safari/537.36"
            )

            # Set realistic viewport
            self.driver.set.window.size(1920, 1080)

            # Add realistic browser properties
            self.driver.run_js("""
                Object.defineProperty(navigator, 'webdriver', {
                    get: () => undefined,
                });
                
                Object.defineProperty(navigator, 'plugins', {
                    get: () => [1, 2, 3, 4, 5],
                });
                
                Object.defineProperty(navigator, 'languages', {
                    get: () => ['en-US', 'en'],
                });
                
                Object.defineProperty(navigator, 'platform', {
                    get: () => 'MacIntel',
                });
                
                // Add realistic canvas fingerprint
                const originalGetContext = HTMLCanvasElement.prototype.getContext;
                HTMLCanvasElement.prototype.getContext = function(type, ...args) {
                    const context = originalGetContext.call(this, type, ...args);
                    if (type === '2d') {
                        const originalFillText = context.fillText;
                        context.fillText = function(...args) {
                            return originalFillText.apply(this, args);
                        };
                    }
                    return context;
                };
            """)

        except Exception as e:
            print(f"Warning: Could not setup all anti-detection measures: {e}")

    def _human_like_delay(self, min_seconds: float = 0.5, max_seconds: float = 2.0) -> None:
        """Add human-like random delay."""
        delay = random.uniform(min_seconds, max_seconds)
        time.sleep(delay)

    def _human_like_mouse_movement(self, element) -> None:
        """Simulate human-like mouse movement to element."""
        try:
            # Get element position - handle ElementRect object properly
            rect = element.rect

            # Access rect properties correctly for DrissionPage ElementRect
            try:
                # Try direct attribute access first (DrissionPage ElementRect)
                x = rect.x
                y = rect.y
                width = rect.width
                height = rect.height
            except AttributeError:
                # Fallback to dictionary access if it's a dict
                try:
                    x = rect.get('x', 0)
                    y = rect.get('y', 0)
                    width = rect.get('width', 0)
                    height = rect.get('height', 0)
                except AttributeError:
                    # If neither works, use default values
                    print("Warning: Could not get element position, using defaults")
                    x, y, width, height = 0, 0, 100, 100

            # Calculate center of element
            center_x = x + width / 2
            center_y = y + height / 2

            # Add some randomness to the target position
            target_x = center_x + random.uniform(-5, 5)
            target_y = center_y + random.uniform(-5, 5)

            # Simulate mouse movement with acceleration/deceleration
            current_x, current_y = 0, 0  # Assume starting from top-left

            # Calculate distance
            distance = math.sqrt((target_x - current_x) **
                                 2 + (target_y - current_y) ** 2)

            # Number of steps for smooth movement
            steps = max(10, int(distance / 10))

            for i in range(steps + 1):
                # Ease-in-out curve for natural movement
                t = i / steps
                ease_t = t * t * (3 - 2 * t)  # Smoothstep function

                x_pos = current_x + (target_x - current_x) * ease_t
                y_pos = current_y + (target_y - current_y) * ease_t

                # Move mouse (if supported by driver) - fix the coordinate handling
                try:
                    self.driver.actions.move_to((x_pos, y_pos))
                except:
                    pass  # Some drivers don't support this

                # Small delay between movements
                time.sleep(random.uniform(0.01, 0.03))

        except Exception as e:
            print(f"Warning: Could not simulate mouse movement: {e}")

    def _human_like_click(self, element) -> None:
        """Simulate human-like clicking behavior."""
        try:
            # Move mouse to element first
            self._human_like_mouse_movement(element)

            # Pre-click delay
            self._human_like_delay(0.1, 0.3)

            # Click with slight randomness
            element.click()

            # Post-click delay
            self._human_like_delay(0.2, 0.8)

        except Exception as e:
            print(f"Warning: Could not simulate human-like click: {e}")
            # Fallback to regular click
            element.click()

    def solveCaptcha(self) -> None:
        """Attempt to solve the reCAPTCHA challenge with anti-detection measures.

        Raises:
            Exception: If captcha solving fails or bot is detected
        """

        # Initial page load delay
        self._human_like_delay(1.0, 3.0)

        # Handle main reCAPTCHA iframe
        print("Looking for reCAPTCHA iframe...")
        self.driver.wait.ele_displayed(
            "@title=reCAPTCHA", timeout=self.TIMEOUT_STANDARD
        )
        self._human_like_delay(0.5, 1.5)

        iframe_inner = self.driver("@title=reCAPTCHA")
        print("Found reCAPTCHA iframe")

        # Find and click the checkbox with human-like behavior
        print("Looking for checkbox...")
        iframe_inner.wait.ele_displayed(
            ".rc-anchor-content", timeout=self.TIMEOUT_STANDARD
        )

        checkbox = iframe_inner(".rc-anchor-content",
                                timeout=self.TIMEOUT_SHORT)
        print("Found checkbox, clicking...")
        self._human_like_click(checkbox)

        # Check if solved by just clicking
        self._human_like_delay(1.0, 2.0)
        if self.is_solved():
            print("Captcha solved by checkbox click!")
            return

        # Wait longer for challenge to appear and check multiple times
        print("Checkbox click didn't solve, waiting for challenge...")

        # Check for challenge multiple times with increasing delays
        for attempt in range(5):
            print(f"Challenge check attempt {attempt + 1}/5...")
            self._human_like_delay(2.0, 3.0)

            if self._check_for_challenge():
                print("Challenge detected, trying audio challenge...")
                self._handle_audio_challenge(iframe_inner)
                return
            else:
                print(f"No challenge detected on attempt {attempt + 1}")

                # Also check if solved
                if self.is_solved():
                    print("Captcha solved during challenge wait!")
                    return

        print("No challenge detected after multiple attempts")
        if not self.is_solved():
            raise Exception("Captcha solving failed - no challenge appeared")
        else:
            print("Captcha appears to be solved!")

    def _check_for_challenge(self) -> bool:
        """Check if a challenge interface has appeared."""
        try:
            # Look for challenge indicators
            challenge_indicators = [
                "iframe[title*='challenge']",
                "iframe[title*='recaptcha']",
                ".rc-challenge",
                ".rc-imageselect",
                ".rc-audiochallenge",
                "iframe[src*='recaptcha']",
                "iframe[src*='challenge']",
                "iframe[src*='api2/anchor']",
                "iframe[src*='api2/bframe']"
            ]

            for indicator in challenge_indicators:
                try:
                    element = self.driver.ele(indicator, timeout=1)
                    if element:
                        print(
                            f"Challenge detected with indicator: {indicator}")
                        return True
                except:
                    continue

            # Also check for any iframe that might be a challenge - simplified approach
            try:
                # Just check for the first few common iframe patterns
                iframe_patterns = [
                    "iframe[title*='recaptcha']",
                    "iframe[src*='recaptcha']",
                    "iframe[src*='challenge']"
                ]

                for pattern in iframe_patterns:
                    try:
                        frame = self.driver.ele(pattern, timeout=1)
                        if frame:
                            title = frame.attrs.get("title", "")
                            src = frame.attrs.get("src", "")
                            print(
                                f"Found iframe: title='{title}', src='{src}'")
                            if "challenge" in title.lower() or "recaptcha" in title.lower():
                                print(f"Challenge iframe found: {title}")
                                return True
                    except:
                        continue

            except Exception as e:
                print(f"Error checking iframes: {e}")

            return False
        except Exception as e:
            print(f"Error checking for challenge: {e}")
            return False

    def _handle_audio_challenge(self, iframe) -> None:
        """Handle audio challenge with improved element detection based on original repository approach."""
        try:
            print("Starting audio challenge handling...")

            # Wait for challenge to appear with longer timeout
            print("Waiting for challenge to appear...")
            self._human_like_delay(3.0, 5.0)

            # Find the challenge iframe using multiple strategies (original repository approach)
            print("Looking for challenge iframe...")
            challenge_iframe = None

            # Strategy 1: Look for iframe with challenge-related titles (most reliable)
            challenge_iframe_selectors = [
                "iframe[title*='recaptcha challenge']",
                "iframe[title*='challenge']",
                "iframe[src*='recaptcha/api2/bframe']",
                "iframe[src*='recaptcha'][src*='bframe']",
                "iframe[name*='c-']",  # Common pattern for challenge iframes
                "iframe[src*='anchor']"
            ]

            for selector in challenge_iframe_selectors:
                try:
                    print(f"Trying challenge iframe selector: {selector}")
                    challenge_iframe = self.driver(selector, timeout=2)

                    if challenge_iframe:
                        print(
                            f"Found challenge iframe with selector: {selector}")
                        # Verify it's actually a challenge iframe by checking for audio elements
                        try:
                            # Try to find audio button inside this iframe
                            test_audio = challenge_iframe(
                                "#recaptcha-audio-button", timeout=1)
                            if test_audio:
                                print(
                                    "Confirmed challenge iframe contains audio button")
                                break
                        except:
                            print(
                                "Iframe found but no audio button, continuing search...")
                            challenge_iframe = None

                except Exception as e:
                    print(f"Challenge iframe selector {selector} failed: {e}")
                    continue

            # Strategy 2: If no specific challenge iframe found, use the provided iframe
            if not challenge_iframe:
                print("Using provided iframe as challenge iframe...")
                challenge_iframe = iframe

            if not challenge_iframe:
                print("WARNING: No challenge iframe found, using main page context")
                challenge_iframe = self.driver

            # Now look for the audio button with improved selectors
            print("Looking for audio button...")
            audio_button = None

            # Original repository's primary selector pattern
            audio_button_selectors = [
                "#recaptcha-audio-button",  # Primary selector from original repo
                "button[title*='Get an audio challenge']",
                "button[title*='audio challenge']",
                "button[id*='audio']",
                "button[class*='rc-button-audio']",
                ".rc-button-audio",
                "button[aria-label*='audio']",
                "button[aria-label*='Audio']",
                # XPath based selectors (more reliable for dynamic content)
                "xpath://button[contains(@id, 'audio')]",
                "xpath://button[contains(@title, 'audio')]",
                "xpath://button[contains(@aria-label, 'audio')]",
                "xpath://button[contains(@class, 'audio')]",
                # Generic button selectors as last resort
                "xpath://div[@class='rc-audiochallenge-control']//button[1]",
                "xpath://div[contains(@class, 'challenge')]//button[contains(@title, 'audio') or contains(@aria-label, 'audio')]"
            ]

            for selector in audio_button_selectors:
                try:
                    print(f"Trying audio button selector: {selector}")
                    audio_button = challenge_iframe(selector, timeout=2)

                    if audio_button:
                        print(f"Found audio button with selector: {selector}")
                        # Verify the button is visible and clickable
                        try:
                            if audio_button.states().is_displayed and audio_button.states().is_enabled:
                                print("Audio button is visible and enabled")
                                break
                            else:
                                print(
                                    "Audio button found but not clickable, continuing search...")
                                audio_button = None
                        except:
                            print("Could not verify button state, but proceeding...")
                            break

                except Exception as e:
                    print(f"Audio button selector {selector} failed: {e}")
                    continue

            # If still no audio button found, try a more aggressive search
            if not audio_button:
                print("Attempting aggressive audio button search...")
                try:
                    # Look for buttons one by one to avoid collection issues
                    button_selectors = [
                        "button:nth-child(1)",
                        "button:nth-child(2)",
                        "button:nth-child(3)",
                        "button",  # Any button as last resort
                    ]

                    for btn_sel in button_selectors:
                        try:
                            btn = challenge_iframe(btn_sel, timeout=1)
                            if btn:
                                btn_text = btn.text.lower() if btn.text else ""
                                btn_title = btn.attrs.get('title', '').lower()
                                btn_aria = btn.attrs.get(
                                    'aria-label', '').lower()

                                print(
                                    f"Button found: text='{btn_text}', title='{btn_title}', aria='{btn_aria}'")

                                if 'audio' in btn_text or 'audio' in btn_title or 'audio' in btn_aria:
                                    print(
                                        f"Found audio button by content analysis")
                                    audio_button = btn
                                    break
                        except:
                            continue

                    if audio_button:
                        print("Audio button found through aggressive search")

                except Exception as e:
                    print(f"Aggressive search failed: {e}")

            if not audio_button:
                raise Exception(
                    "Audio button not found after exhaustive search")

            # Click the audio button with human-like behavior
            print("Clicking audio button...")
            self._human_like_click(audio_button)
            self._human_like_delay(2.0, 4.0)

            # Check for bot detection
            if self.is_detected():
                raise Exception(
                    "Bot detection triggered after clicking audio button")

            # Wait for audio to load and find the audio source
            print("Waiting for audio to load...")
            self._human_like_delay(3.0, 5.0)

            # Find audio source with improved selectors
            print("Looking for audio source...")
            audio_source = None

            audio_source_selectors = [
                "#audio-source",  # Original repository selector
                "audio source",
                "source[type*='audio']",
                "audio[src]",
                "source[src*='recaptcha']",
                ".rc-audiochallenge-audio source",
                ".rc-audiochallenge-audio",
                "xpath://audio//source[@src]",
                "xpath://source[contains(@src, 'recaptcha')]",
                "xpath://audio[@src]"
            ]

            for selector in audio_source_selectors:
                try:
                    print(f"Trying audio source selector: {selector}")
                    audio_source = challenge_iframe(selector, timeout=3)

                    if audio_source:
                        print(f"Found audio source with selector: {selector}")
                        # Verify it has a src attribute
                        src = audio_source.attrs.get("src")
                        if src:
                            print(f"Audio source has valid src: {src[:50]}...")
                            break
                        else:
                            print("Audio source found but no src attribute")
                            audio_source = None

                except Exception as e:
                    print(f"Audio source selector {selector} failed: {e}")
                    continue

            if not audio_source:
                raise Exception(
                    "Audio source not found after exhaustive search")

            # Get the audio URL
            src = audio_source.attrs.get("src")
            if not src:
                raise Exception("Audio source found but no src URL available")

            print(f"Processing audio from URL: {src[:50]}...")

            # Process the audio challenge
            text_response = self._process_audio_challenge(src)
            print(f"Audio recognition result: {text_response}")

            # Find and fill the response field
            print("Looking for response input field...")
            response_field = None

            response_field_selectors = [
                "#audio-response",  # Original repository selector
                "input[id*='audio-response']",
                "input[name*='audio']",
                "input[type='text']",
                ".rc-audiochallenge-response-field",
                "input[placeholder*='audio']",
                "input[aria-label*='audio']",
                "xpath://input[@id='audio-response']",
                "xpath://input[contains(@class, 'response')]",
                "xpath://div[contains(@class, 'audiochallenge')]//input[@type='text']"
            ]

            for selector in response_field_selectors:
                try:
                    print(f"Trying response field selector: {selector}")
                    response_field = challenge_iframe(selector, timeout=2)

                    if response_field:
                        print(
                            f"Found response field with selector: {selector}")
                        break

                except Exception as e:
                    print(f"Response field selector {selector} failed: {e}")
                    continue

            if not response_field:
                raise Exception("Response field not found")

            # Type the response with human-like behavior
            print(f"Typing response: {text_response}")
            self._human_like_type(response_field, text_response.lower())
            self._human_like_delay(0.5, 1.5)

            # Find and click the verify button
            print("Looking for verify button...")
            verify_button = None

            verify_button_selectors = [
                "#recaptcha-verify-button",  # Original repository selector
                "button[id*='verify']",
                "button[type='submit']",
                ".rc-button-default",
                "button[value*='verify']",
                "input[type='submit']",
                "button:contains('Verify')",
                "button:contains('Submit')",
                "xpath://button[@id='recaptcha-verify-button']",
                "xpath://button[contains(@class, 'verify')]",
                "xpath://button[@type='submit']",
                # Often the last button
                "xpath://div[contains(@class, 'audiochallenge')]//button[last()]"
            ]

            for selector in verify_button_selectors:
                try:
                    print(f"Trying verify button selector: {selector}")
                    verify_button = challenge_iframe(selector, timeout=2)

                    if verify_button:
                        print(f"Found verify button with selector: {selector}")
                        break

                except Exception as e:
                    print(f"Verify button selector {selector} failed: {e}")
                    continue

            if not verify_button:
                # As a last resort, look for submit-type buttons
                print("Looking for any submit button as last resort...")
                try:
                    submit_selectors = [
                        "button[type='submit']", "input[type='submit']", "button"]
                    for sel in submit_selectors:
                        try:
                            verify_button = challenge_iframe(sel, timeout=1)
                            if verify_button:
                                print(
                                    f"Found fallback button with selector: {sel}")
                                break
                        except:
                            continue
                except:
                    pass

            if not verify_button:
                raise Exception("Verify button not found")

            # Click the verify button
            print("Clicking verify button...")
            self._human_like_click(verify_button)
            self._human_like_delay(2.0, 4.0)

            # Check if the captcha was solved
            print("Checking if captcha was solved...")
            self._human_like_delay(3.0, 5.0)

            if not self.is_solved():
                print("Captcha not solved, checking for errors...")
                # Check if we need to try again or if there was an error
                raise Exception(
                    "Failed to solve the captcha - verification unsuccessful")
            else:
                print("✅ Audio challenge completed successfully!")

        except Exception as e:
            print(f"❌ Audio challenge failed: {str(e)}")
            raise Exception(f"Audio challenge failed: {str(e)}")

    def _human_like_type(self, element, text: str) -> None:
        """Simulate human-like typing behavior."""
        try:
            # Clear field first
            element.clear()
            self._human_like_delay(0.1, 0.3)

            # Type character by character with random delays
            for char in text:
                element.input(char)
                # Random delay between characters
                time.sleep(random.uniform(0.05, 0.15))

        except Exception as e:
            print(f"Warning: Could not simulate human-like typing: {e}")
            # Fallback to regular input
            element.input(text)

    def _process_audio_challenge(self, audio_url: str) -> str:
        """Process the audio challenge and return the recognized text.

        Args:
            audio_url: URL of the audio file to process

        Returns:
            str: Recognized text from the audio file
        """
        mp3_path = os.path.join(
            self.TEMP_DIR, f"{random.randrange(1, 1000)}.mp3")
        wav_path = os.path.join(
            self.TEMP_DIR, f"{random.randrange(1, 1000)}.wav")

        try:
            # Use proxy for downloading audio if available
            if self.current_proxy:
                import requests
                proxy_dict = get_proxy_dict(self.current_proxy)
                response = requests.get(
                    audio_url, proxies=proxy_dict, timeout=30)
                response.raise_for_status()

                with open(mp3_path, 'wb') as f:
                    f.write(response.content)

                # Mark proxy as successful
                mark_proxy_success(self.current_proxy)
            else:
                # Fallback to direct download
                urllib.request.urlretrieve(audio_url, mp3_path)

            sound = pydub.AudioSegment.from_mp3(mp3_path)
            sound.export(wav_path, format="wav")

            recognizer = sr.Recognizer()
            with sr.AudioFile(wav_path) as source:
                audio = recognizer.record(source)

            # Use the correct speech recognition method - fix the method name
            try:
                return recognizer.recognize_google(audio)
            except sr.UnknownValueError:
                raise Exception("Could not understand audio")
            except sr.RequestError as e:
                raise Exception(
                    f"Could not request results from Google Speech Recognition service; {e}")

        except Exception as e:
            # Mark proxy as failed if we used one
            if self.current_proxy:
                mark_proxy_failure(self.current_proxy)
            raise e
        finally:
            for path in (mp3_path, wav_path):
                if os.path.exists(path):
                    try:
                        os.remove(path)
                    except OSError:
                        pass

    def is_solved(self) -> bool:
        """Check if the captcha has been solved successfully."""
        try:
            # Check multiple indicators of success
            indicators = [
                ".recaptcha-checkbox-checkmark",
                ".recaptcha-checkbox-checked",
                "[aria-checked='true']",
                ".rc-anchor-checked"
            ]

            for indicator in indicators:
                try:
                    element = self.driver.ele(
                        indicator, timeout=self.TIMEOUT_SHORT)
                    if element and element.states().is_displayed:
                        return True
                except:
                    continue

            return False
        except Exception:
            return False

    def is_detected(self) -> bool:
        """Check if the bot has been detected."""
        try:
            detection_indicators = [
                "Try again later",
                "unusual traffic",
                "automated",
                "robot",
                "blocked",
                "suspicious"
            ]

            for indicator in detection_indicators:
                try:
                    element = self.driver.ele(
                        indicator, timeout=self.TIMEOUT_DETECTION)
                    if element and element.states().is_displayed:
                        return True
                except:
                    continue

            return False
        except Exception:
            return False

    def get_token(self) -> Optional[str]:
        """Get the reCAPTCHA token if available."""
        try:
            # Try multiple possible token locations
            token_selectors = [
                "#recaptcha-token",
                "input[name='g-recaptcha-response']",
                "[data-sitekey]"
            ]

            for selector in token_selectors:
                try:
                    element = self.driver.ele(
                        selector, timeout=self.TIMEOUT_SHORT)
                    if element:
                        token = element.attrs.get(
                            "value") or element.attrs.get("data-token")
                        if token:
                            return token
                except:
                    continue

            return None
        except Exception:
            return None
