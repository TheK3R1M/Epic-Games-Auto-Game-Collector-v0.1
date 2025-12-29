"""
Epic Games Selenium Connector - Alternative browser automation approach

=============================================================================
1. POTENTIAL CHALLENGES / EDGE CASES:
=============================================================================
- Epic Games has strong anti-bot protection (Arkose Labs CAPTCHA)
- Login page layout can change (React-based dynamic content)
- Website requires specific user agent and headers to avoid detection
- Two-factor authentication (2FA) via Email/SMS/Authenticator/Manual
- Session cookies expire and need refresh
- Rate limiting if too many login attempts
- CloudFlare protection on some endpoints
- JavaScript-heavy page requires waiting for elements to load
- Browser fingerprinting detection
- User-data-dir conflicts when running multiple accounts simultaneously

=============================================================================
2. LIBRARIES & REASONING:
=============================================================================
- selenium: Core browser automation (more stable than Playwright for some sites)
- undetected-chromedriver: Bypasses Selenium detection (patches WebDriver flag)
- webdriver-manager: Automatic ChromeDriver version management
- typing: Type hints for better code quality
- time/random: Human-like delays to avoid bot detection
- os/pathlib: File/directory management for profiles and cookies

=============================================================================
3. OUTLINE OF STEPS:
=============================================================================
Step 1: Initialize undetected Chrome with isolated user profile per account
Step 2: Navigate to Epic Games login page with proper wait
Step 3: Check for existing cookies and attempt cookie-based login first
Step 4: If no cookies or invalid, locate username/email input field
Step 5: Enter email with human-like typing delays
Step 6: Locate and click "Continue" button
Step 7: Wait for password field to appear (dynamic loading)
Step 8: Enter password with human-like typing
Step 9: Locate and click "Sign In" button
Step 10: Detect if CAPTCHA appears (wait/skip approach)
Step 11: Detect 2FA requirement (email/SMS/authenticator)
Step 12: Handle 2FA code input if required
Step 13: Verify successful login by checking URL/page elements
Step 14: Save session cookies for future reuse
Step 15: Navigate to free games page
Step 16: Close browser gracefully or keep open for claiming

=============================================================================
"""

import time
import random
import os
import json
import pickle
from pathlib import Path
from typing import Optional, List, Dict
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.keys import Keys
from selenium.common.exceptions import TimeoutException, NoSuchElementException

try:
    import undetected_chromedriver as uc
    UNDETECTED_AVAILABLE = True
except ImportError:
    UNDETECTED_AVAILABLE = False
    print("⚠️ undetected-chromedriver not available, using standard Chrome")


class SeleniumEpicConnector:
    """Epic Games automation using Selenium with anti-detection."""

    def __init__(self, email: str):
        self.email = email
        self.driver = None
        self.wait = None
        # Isolated profile per account to avoid conflicts
        safe_email = email.replace("@", "_at_").replace(".", "_")
        self.profile_dir = os.path.abspath(f"data/selenium_profiles/{safe_email}")
        os.makedirs(self.profile_dir, exist_ok=True)
        self.cookies_file = os.path.join(self.profile_dir, "cookies.pkl")

    def initialize(self, headless: bool = False):
        """Initialize Chrome browser with anti-detection."""
        print(f"🔧 Initializing browser for {self.email}...")
        # Privacy hardening: ensure strictly local operation
        # Clear any environment proxies to avoid accidental routing via external services
        for key in [
            "HTTP_PROXY", "HTTPS_PROXY", "ALL_PROXY",
            "http_proxy", "https_proxy", "all_proxy"
        ]:
            if os.environ.get(key):
                os.environ[key] = ""
        
        # Disable Play Services/metrics style background comms (Chromium flags)
        privacy_flags = [
            "--disable-background-networking",
            "--disable-sync",
            "--metrics-recording-only",
            "--disable-default-apps",
            "--no-first-run",
            "--disable-client-side-phishing-detection",
            "--disable-component-update",
            "--disable-domain-reliability",
            "--safebrowsing-disable-auto-update",
            "--disable-features=Translate,AutofillServerCommunication,OptimizationHints"
        ]
        
        options = webdriver.ChromeOptions()
        
        # User data directory for persistence
        options.add_argument(f"--user-data-dir={self.profile_dir}")
        
        # Anti-detection flags
        options.add_argument("--disable-blink-features=AutomationControlled")
        options.add_experimental_option("excludeSwitches", ["enable-automation"])
        options.add_experimental_option("useAutomationExtension", False)
        # Apply privacy flags
        for flag in privacy_flags:
            options.add_argument(flag)
        
        # Performance and stability
        options.add_argument("--disable-dev-shm-usage")
        options.add_argument("--no-sandbox")
        options.add_argument("--disable-gpu")
        
        # User agent (realistic)
        options.add_argument("user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/131.0.0.0 Safari/537.36")
        
        # Window size (visible or headless)
        if headless:
            options.add_argument("--headless=new")
        options.add_argument("--window-size=1920,1080")
        
        # Language and locale
        options.add_argument("--lang=tr-TR")
        
        try:
            if UNDETECTED_AVAILABLE:
                # Use undetected-chromedriver for better stealth
                self.driver = uc.Chrome(options=options, version_main=131)
                print("   ✅ Using undetected-chromedriver")
            else:
                # Fallback to standard Chrome
                self.driver = webdriver.Chrome(options=options)
                # Mask WebDriver property manually
                self.driver.execute_cdp_cmd("Page.addScriptToEvaluateOnNewDocument", {
                    "source": "Object.defineProperty(navigator, 'webdriver', {get: () => undefined})"
                })
                print("   ✅ Using standard Chrome with WebDriver masking")
        except Exception as e:
            print(f"   ❌ Browser init failed: {e}")
            raise
        
        # Set implicit wait and create WebDriverWait
        self.driver.implicitly_wait(3)
        self.wait = WebDriverWait(self.driver, 15)
        
        print("   ✅ Browser initialized successfully")

    def _human_delay(self, min_sec: float = 0.3, max_sec: float = 1.0):
        """Simulate human-like delay."""
        time.sleep(random.uniform(min_sec, max_sec))

    def _human_type(self, element, text: str):
        """Type text with human-like delays."""
        for char in text:
            element.send_keys(char)
            time.sleep(random.uniform(0.05, 0.15))
            if random.random() < 0.1:  # 10% chance of pause
                time.sleep(random.uniform(0.1, 0.3))

    def _save_cookies(self):
        """Save cookies to file."""
        try:
            with open(self.cookies_file, "wb") as f:
                pickle.dump(self.driver.get_cookies(), f)
            print("   💾 Cookies saved")
        except Exception as e:
            print(f"   ⚠️ Could not save cookies: {e}")

    def _load_cookies(self) -> bool:
        """Load cookies from file."""
        if not os.path.exists(self.cookies_file):
            return False
        
        try:
            with open(self.cookies_file, "rb") as f:
                cookies = pickle.load(f)
            
            # Must visit domain first before adding cookies
            self.driver.get("https://www.epicgames.com")
            self._human_delay(1, 2)
            
            for cookie in cookies:
                try:
                    self.driver.add_cookie(cookie)
                except Exception:
                    pass  # Some cookies may fail, continue
            
            print("   💾 Cookies loaded")
            return True
        except Exception as e:
            print(f"   ⚠️ Could not load cookies: {e}")
            return False

    def _detect_captcha(self) -> bool:
        """Check if CAPTCHA is present on page."""
        try:
            # Check for common CAPTCHA iframes
            captcha_selectors = [
                "iframe[src*='hcaptcha']",
                "iframe[src*='recaptcha']",
                "iframe[src*='arkose']",
                "iframe[src*='funcaptcha']",
                "[class*='captcha']",
                "[id*='captcha']"
            ]
            
            for selector in captcha_selectors:
                elements = self.driver.find_elements(By.CSS_SELECTOR, selector)
                if elements:
                    return True
            
            # Check page source for CAPTCHA-related text
            page_source = self.driver.page_source.lower()
            if any(word in page_source for word in ["captcha", "arkose", "challenge"]):
                return True
            
            return False
        except:
            return False

    def _detect_2fa(self) -> Optional[str]:
        """Detect 2FA requirement and return method type."""
        try:
            page_source = self.driver.page_source.lower()
            
            # Check URL and content for 2FA indicators
            current_url = self.driver.current_url.lower()
            
            if "mfa" in current_url or "two-factor" in current_url:
                if "email" in page_source:
                    return "email"
                elif "sms" in page_source or "phone" in page_source:
                    return "sms"
                elif "authenticator" in page_source or "totp" in page_source:
                    return "totp"
                else:
                    return "manual"
            
            return None
        except:
            return None

    def login(self, email: str, password: str) -> bool:
        """Login to Epic Games account."""
        try:
            print(f"🔐 Logging in: {email}")
            
            # Try cookie-based login first
            if self._load_cookies():
                print("   🍪 Trying cookie-based login...")
                self.driver.get("https://www.epicgames.com/store/en-US/")
                self._human_delay(2, 3)
                
                # Check if already logged in
                if self._check_login_success():
                    print("   ✅ Cookie login successful!")
                    return True
                else:
                    print("   ⚠️ Cookies invalid, proceeding with credentials...")

            # Navigate to login page
            print("   🌐 Navigating to login page...")
            self.driver.get("https://www.epicgames.com/id/login")
            self._human_delay(2, 3)

            # Wait for and enter email
            print(f"   📧 Entering email: {email}")
            try:
                email_input = self.wait.until(
                    EC.presence_of_element_located((By.CSS_SELECTOR, "input[type='email'], input[name='email']"))
                )
                email_input.click()
                self._human_delay(0.3, 0.7)
                self._human_type(email_input, email)
                self._human_delay(0.5, 1)
            except TimeoutException:
                print("   ❌ Email input not found")
                return False

            # Click Continue button
            print("   ➡️ Clicking Continue...")
            try:
                continue_btn = self.wait.until(
                    EC.element_to_be_clickable((By.XPATH, "//button[contains(., 'Continue') or contains(., 'İleri')]"))
                )
                continue_btn.click()
                self._human_delay(1.5, 2.5)
            except:
                # Try Enter key if button not found
                email_input.send_keys(Keys.RETURN)
                self._human_delay(1.5, 2.5)

            # Wait for and enter password
            print("   🔑 Entering password...")
            try:
                password_input = self.wait.until(
                    EC.presence_of_element_located((By.CSS_SELECTOR, "input[type='password'], input[name='password']"))
                )
                password_input.click()
                self._human_delay(0.3, 0.7)
                self._human_type(password_input, password)
                self._human_delay(0.5, 1)
            except TimeoutException:
                print("   ❌ Password input not found")
                return False

            # Click Sign In button
            print("   🔓 Clicking Sign In...")
            try:
                signin_btn = self.wait.until(
                    EC.element_to_be_clickable((By.XPATH, "//button[contains(., 'Sign In') or contains(., 'Log in') or contains(., 'Login')]"))
                )
                signin_btn.click()
            except:
                password_input.send_keys(Keys.RETURN)
            
            self._human_delay(3, 5)

            # Check for CAPTCHA
            if self._detect_captcha():
                print("   🤖 CAPTCHA detected - cannot proceed automatically")
                print("   ⚠️ This account will be skipped (anti-bot protection)")
                return False

            # Check for 2FA
            twofa_method = self._detect_2fa()
            if twofa_method:
                print(f"   🔐 2FA required: {twofa_method}")
                success = self._handle_2fa(twofa_method)
                if not success:
                    print("   ❌ 2FA failed")
                    return False

            # Verify login success
            self._human_delay(2, 3)
            if self._check_login_success():
                print("   ✅ Login successful!")
                self._save_cookies()
                return True
            else:
                print("   ❌ Login failed - verification unsuccessful")
                return False

        except Exception as e:
            print(f"   ❌ Login error: {e}")
            import traceback
            traceback.print_exc()
            return False

    def _handle_2fa(self, method: str) -> bool:
        """Handle 2FA code input."""
        try:
            print(f"   📱 {method.upper()} 2FA - Please enter code")
            code = input(f"   Enter {method.upper()} code: ").strip()
            
            if len(code) < 4:
                return False

            # Find code input field
            code_selectors = [
                "input[name='code']",
                "input[type='text'][placeholder*='code' i]",
                "input[data-testid*='code']",
                "input[id*='code']"
            ]
            
            code_input = None
            for selector in code_selectors:
                try:
                    code_input = self.driver.find_element(By.CSS_SELECTOR, selector)
                    break
                except:
                    continue
            
            if not code_input:
                # Try all text inputs as fallback
                text_inputs = self.driver.find_elements(By.CSS_SELECTOR, "input[type='text']")
                if text_inputs:
                    code_input = text_inputs[0]
            
            if code_input:
                code_input.click()
                self._human_delay(0.3, 0.6)
                self._human_type(code_input, code)
                self._human_delay(0.5, 1)
                
                # Find and click verify button
                try:
                    verify_btn = self.driver.find_element(By.XPATH, 
                        "//button[contains(., 'Verify') or contains(., 'Continue') or contains(., 'Submit') or contains(., 'Doğrula')]")
                    verify_btn.click()
                except:
                    code_input.send_keys(Keys.RETURN)
                
                self._human_delay(3, 5)
                return True
            
            return False
            
        except Exception as e:
            print(f"   ❌ 2FA error: {e}")
            return False

    def _check_login_success(self) -> bool:
        """Verify if login was successful."""
        try:
            current_url = self.driver.current_url.lower()
            
            # Success indicators
            success_patterns = ["store", "account", "profile", "dashboard"]
            if any(pattern in current_url for pattern in success_patterns):
                return True
            
            # Check for user menu or avatar (indicates logged in)
            try:
                self.driver.find_element(By.CSS_SELECTOR, "[data-testid='user-avatar'], [class*='UserAvatar']")
                return True
            except:
                pass
            
            return False
        except:
            return False

    def get_free_games(self) -> List[Dict]:
        """Navigate to free games and extract list."""
        try:
            print("🎮 Fetching free games...")
            self.driver.get("https://www.epicgames.com/store/en-US/free-games")
            self._human_delay(3, 5)
            
            # Scroll to load dynamic content
            self.driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
            self._human_delay(1, 2)
            
            # Find game cards
            games = []
            game_elements = self.driver.find_elements(By.CSS_SELECTOR, "a[href*='/p/']")
            
            for elem in game_elements[:10]:  # Limit to first 10
                try:
                    url = elem.get_attribute("href")
                    name = elem.text.strip() or "Unknown"
                    
                    if url and name and len(name) > 2:
                        games.append({"name": name, "url": url})
                except:
                    continue
            
            print(f"   ✅ Found {len(games)} games")
            return games
            
        except Exception as e:
            print(f"   ❌ Error fetching games: {e}")
            return []

    def claim_game(self, game_url: str, game_name: str) -> bool:
        """Claim a specific game."""
        try:
            print(f"🎁 Claiming: {game_name}")
            self.driver.get(game_url)
            self._human_delay(2, 3)
            
            # Look for "Get" button
            get_button = None
            button_selectors = [
                "//button[contains(., 'Get')]",
                "//button[contains(., 'Claim')]",
                "//button[contains(., 'Free')]"
            ]
            
            for selector in button_selectors:
                try:
                    get_button = self.driver.find_element(By.XPATH, selector)
                    break
                except:
                    continue
            
            if get_button:
                get_button.click()
                self._human_delay(1, 2)
                print(f"   ✅ Claimed: {game_name}")
                return True
            else:
                print(f"   ℹ️ Already owned or no button found")
                return False
                
        except Exception as e:
            print(f"   ❌ Error claiming game: {e}")
            return False

    def close(self):
        """Close browser gracefully."""
        if self.driver:
            try:
                self.driver.quit()
                print("   🔒 Browser closed")
            except:
                pass
