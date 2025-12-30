# ==============================================================================
# Epic Games Auto Game Collector
# Copyright (c) 2024 TheK3R1M
#
# DISCLAIMER: This software is for educational purposes only. 
# The author is not responsible for any misuse, account restrictions, or damages.
# Use at your own risk.
# ==============================================================================

import os
import time
import json
import random
from typing import List, Dict, Optional
from DrissionPage import ChromiumPage, ChromiumOptions
from src.security.cookie_manager import CookieManager

class EpicDrissionConnector:
    def __init__(self, account_email: str = None):
        self.account_email = account_email
        self.page = None
        self.cookie_manager = CookieManager()
        self.last_real_account_key = None

    def initialize(self):
        """Initialize the DrissionPage Chromium instance with absolute stability."""
        try:
            print(f"🛠️ Opening browser window (Stable Mode)...")
            co = ChromiumOptions()
            
            # Let DrissionPage find a free port automatically for maximum reliability
            co.auto_port() 
            co.headless(False) 
            co.set_argument('--no-sandbox')
            co.set_argument('--disable-gpu')
            co.set_argument('--disable-dev-shm-usage')
            co.set_argument('--window-size=1280,1024')
            
            # STABILITY: Disable profiles as they cause 'unpack' errors in this specific environment.
            # We strictly use JSON cookie injection for session persistence across all domains.
            
            # Create page
            self.page = ChromiumPage(co)
            
            # Set window size
            try:
                 self.page.set.window.size(850, 950)
            except: pass
            
            print(f"✅ Browser open and stable on port: {self.page.address.split(':')[-1]}")
            return True
        except Exception as e:
            print(f"❌ Initialization failed: {e}")
            return False

    def close(self):
        if self.page:
            try:
                self.page.quit()
            except:
                pass

    def login(self, email: str, password: str = "") -> bool:
        """Log in to Epic Games using DrissionPage."""
        print(f"🔐 Signing in: {email}")
        
        if not self.page:
            print("❌ Browser not initialized. Cannot login.")
            return False

        # 1. Check for valid cookies
        has_cookies = self.cookie_manager.cookies_exist(email)
        if has_cookies:
            print(f"   💾 Vaulted cookies found for {email}, attempting re-entry...")
            cookies = self.cookie_manager.load_cookies(email)
            if cookies:
                try:
                    print(f"   🍪 Cleaning and injecting {len(cookies)} cookies...")
                    
                    # CLEAN COOKIES: CDP is strict, only keep essential keys
                    clean_cookies = []
                    for c in cookies:
                        if not isinstance(c, dict): continue
                        clean_c = {
                            'name': c.get('name'),
                            'value': c.get('value'),
                            'domain': c.get('domain'),
                            'path': c.get('path', '/'),
                            'secure': c.get('secure', True)
                        }
                        # Remove None values
                        clean_c = {k: v for k, v in clean_c.items() if v is not None}
                        clean_cookies.append(clean_c)

                    # 1. Start with the login page to establish domain context
                    print("   🌐 Establishing domain context...")
                    self.page.get("https://www.epicgames.com/id/login", timeout=20)
                    time.sleep(2)
                    
                    # 2. Inject
                    self.page.set.cookies(clean_cookies)
                    
                    # 3. CRITICAL: Sync on Account page
                    print(f"   🔄 Syncing session...")
                    self.page.get("https://www.epicgames.com/account/personal", timeout=15)
                    time.sleep(3)

                    if self._check_login_success():
                        print(f"✅ SESSION RESTORED: {email}")
                        self._save_cookies(email) 
                        return True
                    else:
                        print(f"   ❌ Session re-entry failed. Cookies might be expired.")
                        # HOTFIX: Delete invalid cookies to prevent loop
                        self.cookie_manager.delete_cookies(email)
                        return False
                except Exception as e:
                    print(f"⚠️ Error during secure cookie injection for {email}: {e}")
                    return False

        # 2. Manual Login
        print("📝 Manual login required.")
        print("   Please complete login in the browser window.")
        
        try:
            try:
                self.page.get("https://www.epicgames.com/id/login?lang=en-US&redirectUrl=https%3A%2F%2Fstore.epicgames.com%2Fen-US%2F")
            except Exception as e:
                # DrissionPage sometimes raises "提示: ..." errors for connection issues
                # We suppress them and print a generic English message
                err_str = str(e)
                if "提示" in err_str or "Hint" in err_str:
                     print(f"⚠️ Connection hint received (suppressed): Retrying...")
                else:
                     print(f"⚠️ Navigation warning: {e}")

            # Wait for redirect to store
            print("   ⏳ Waiting for login completion...")
            max_wait = 120 # Reduced from 300
            start = time.time()
            while time.time() - start < max_wait:
                if self._check_login_success():
                    print("   ✅ Login detected via element check!")
                    break
                    
                current_url = self.page.url
                if "store.epicgames.com" in current_url and "/id/login" not in current_url:
                    print("   ✅ Login detected via URL!")
                    break
                time.sleep(0.5) # Check every 0.5s instead of 1s
            
            if self._check_login_success():
                self._save_cookies(email)
                self.last_real_account_key = email
                print(f"✅ Manual login successful")
                return True
            else:
                print("❌ Manual login failed or timed out.")
                return False
                
        except Exception as e:
            print(f"❌ Login error: {e}")
            return False



    def login_new_account(self) -> Optional[str]:
        """
        Interactive login for adding a new account.
        Opens browser, waits for user login, detects email, saves cookies.
        Returns the detected email or None if failed.
        """
        print("➕ Starting new account login flow...")
        try:
            # Ensure page is focused and ready
            time.sleep(0.5)
            
            # Direct login URL with minimal extras
            login_url = "https://www.epicgames.com/id/login?lang=en-US"
            print(f"   🌐 Step 1: Navigating to {login_url}")
            
            nav_success = False
            for attempt in range(1, 3):
                try:
                    print(f"   🔄 Attempt {attempt}...")
                    self.page.get(login_url, timeout=12)
                    
                    # Short wait to let the page start rendering
                    time.sleep(2)
                    
                    current_url = self.page.url
                    if "epicgames" in current_url:
                        nav_success = True
                        print(f"   ✅ At domain: {current_url}")
                        break
                except Exception as e:
                    print(f"   ⚠️ Attempt {attempt} failed: {e}")
                    time.sleep(1)
            
            if not nav_success:
                 print("   ⚠️ Try fallback to store first...")
                 self.page.get("https://store.epicgames.com/en-US/", timeout=15)
                 time.sleep(3)
                 self.page.get(login_url, timeout=15)

            print("\n" + "!"*40)
            print("   PLEASE SIGN IN IN THE SMALL BROWSER WINDOW")
            print("!"*40 + "\n")
            
            print("   ⏳ Monitoring login state (Max 5 mins)...")
            
            # Wait loop
            max_wait = 300 
            start = time.time()
            logged_in = False
            
            # Proactive email capture while waiting
            captured_email = None
            
            while time.time() - start < max_wait:
                # 1. Peek at email input if visible
                if not captured_email:
                    try:
                        email_el = self.page.ele('@name=email', timeout=0.1) or self.page.ele('#email', timeout=0.1)
                        if email_el:
                            val = email_el.value
                            if val and "@" in val and "." in val:
                                captured_email = val
                    except: pass

                # 2. Check by markers
                if self._check_login_success():
                    logged_in = True
                    break
                
                # 3. Check if we hit the redirect or confirmation
                curr_url = self.page.url.lower()
                if "epicgames.com" in curr_url:
                    if "/id/login" not in curr_url:
                         time.sleep(1.5)
                         if self._check_login_success():
                             logged_in = True
                             break
                
                time.sleep(1.5)
            
            if not logged_in:
                print("❌ Login timed out or cancelled by user.")
                return None
            
            print(f"   ✅ Login detected! Using email hint: {captured_email}")
            time.sleep(2)
            
            # Auto-detect real Email and Name from Personal Info
            print("   🕵️ Fetching account details from personal info page...")
            account_email = captured_email
            display_name = "User"
            
            try:
                self.page.get("https://www.epicgames.com/account/personal", timeout=15)
                time.sleep(3)
                
                # Use strict selectors provided by user
                email_input = self.page.ele('@name=email', timeout=5) or self.page.ele('#email', timeout=2)
                if email_input and email_input.value:
                    account_email = email_input.value
                
                name_input = self.page.ele('#displayName', timeout=5) or self.page.ele('@name=displayName', timeout=2)
                if name_input and name_input.value:
                    display_name = name_input.value
                    print(f"   👤 Account Name: {display_name}")

            except Exception as e:
                print(f"   ⚠️ Metadata fetch error: {e}")
            
            # Prioritize the unmasked email we captured during typing
            primary_email = captured_email
            if not primary_email or "*" in primary_email:
                primary_email = account_email
            
            final_identifier = primary_email or f"USER_{display_name.replace(' ', '_')}"
            
            if final_identifier:
                print(f"   📧 Final Account ID: {final_identifier}")
                # IMPORTANT: Save cookies using the unmasked email we captured
                self._save_cookies(final_identifier)
                return final_identifier
            else:
                 print("   ⚠️ No user identity established.")
                 return "UNKNOWN_USER"
            
        except Exception as e:
            print(f"❌ Error in new account flow: {e}")
            return None

    def _check_login_success(self) -> bool:
        """Check if we are actually logged in with multiple markers."""
        try:
            url = self.page.url.lower()
            
            # 1. Store page markers
            if "store.epicgames.com" in url:
                # Common data-testids for the user menu button
                if self.page.ele('@data-testid=user-account-icon', timeout=2) or \
                   self.page.ele('@data-testid=nav-user-menu-button', timeout=1):
                    # Extra check: ensure we don't see "Sign In" text
                    if not self.page.ele('text:Sign In') and not self.page.ele('text:Giriş Yap'):
                        return True
                
                # user-initials often used in the nav
                if self.page.ele('.user-name-label', timeout=1) or \
                   self.page.ele('.user-initials', timeout=1):
                    return True

            # 2. Account page markers
            if "account.epicgames.com" in url or "epicgames.com/account" in url:
                if self.page.ele('text:Sign Out', timeout=2) or \
                   self.page.ele('text:Çıkış Yap', timeout=1) or \
                   self.page.ele('text:Personal Details', timeout=1) or \
                   self.page.ele('text:Account ID', timeout=1):
                    return True
            
            # 3. Global markers
            if self.page.ele('@data-testid=user-account-icon', timeout=1) or \
               self.page.ele('text:Sign Out', timeout=1) or \
               self.page.ele('text:Çıkış Yap', timeout=1) or \
               self.page.ele('.user-initials', timeout=1):
               return True

            return ('account/personal' in url and '/id/login' not in url)
        except:
            return False

    def _save_cookies(self, email: str):
        """Save current session cookies."""
        try:
            # EXTRA: Navigate to personal details to ensure we are fully in and have all cookies
            self.page.get("https://www.epicgames.com/account/personal", timeout=15)
            time.sleep(3)
            
            # Capture ALL cookies without filtering (except domain)
            raw_cookies = self.page.cookies() 
            if not isinstance(raw_cookies, list):
                try: raw_cookies = list(raw_cookies)
                except: raw_cookies = []
            
            final_list = []
            for c in raw_cookies:
                if not isinstance(c, dict): continue
                
                domain = c.get('domain', '').lower()
                if 'epicgames.com' in domain or domain == '':
                    # Standardize fields for our CookieManager
                    final_list.append({
                        'name': c.get('name'), 
                        'value': c.get('value'), 
                        'domain': c.get('domain', '.epicgames.com'), 
                        'path': c.get('path', '/'),
                        'secure': c.get('secure', True)
                    })
            
            if final_list:
                # Deduplicate
                unique = {}
                for cookie in final_list:
                    key = (cookie['name'], cookie['domain'])
                    unique[key] = cookie
                
                self.cookie_manager.save_cookies(email, list(unique.values()))
                print(f"   💾 Vault updated: {len(unique)} cookies saved for {email}.")
            else:
                print(f"   ⚠️ No cookies captured for {email}.")
                
        except Exception as e:
            print(f"   ⚠️ Vault save error: {e}")

    def check_claimed_games(self) -> List[str]:
        """Check owned games - Skipped for DrissionPage, relies on button check."""
        return []

    def get_free_games(self) -> List[Dict]:
        """Scrape free games using robust DOM method first, API fallback."""
        print("🎮 Checking free games (DOM Method)...")
        self.page.get("https://store.epicgames.com/en-US/free-games")
        time.sleep(5)
        
        games = []
        try:
            # HOTFIX: Scrape href directly to avoid 404s
            # Find the 'Free Now' badges
            badges = self.page.eles('text:Free Now')
            
            for badge in badges:
                try:
                    # We need to find the parent <a> tag.
                    # Usually it's up 3-5 levels or so.
                    # Safer: Find the closest 'a' ancestor with an href
                    card_link = badge.parent('tag:a') 
                    if not card_link:
                         # Try going up a few levels manually if direct parent search fails
                         curr = badge
                         for _ in range(6):
                             curr = curr.parent()
                             if curr.tag == 'a':
                                 card_link = curr
                                 break
                    
                    if card_link and card_link.attr('href'):
                        raw_url = card_link.attr('href')
                        title = card_link.attr('aria-label') or "Free Game"
                        title = title.replace("Free Game, ", "").replace(", Free Game", "")
                        
                        if not raw_url.startswith("http"):
                             game_url = f"https://store.epicgames.com{raw_url}"
                        else:
                             game_url = raw_url
                        
                        # Filter out non-game links
                        if "/p/" in game_url or "/bundles/" in game_url:
                             print(f"   found: {title} -> {game_url}")
                             games.append({'name': title, 'url': game_url})

                except Exception as e:
                    print(f"   ⚠️ extraction error: {e}")
                    pass
            
            if not games:
                print("   ⚠️ DOM scrape yielded 0 games. Using strict API fallback.")
                return self._get_free_games_api_fallback()
                
            return games
            
        except Exception as e:
            print(f"❌ Error getting games: {e}")
            return []

    def _get_free_games_api_fallback(self):
        """Original API method as fallback."""
        games = []
        try:
            api_url = 'https://store-site-backend-static-ipv4.ak.epicgames.com/freeGamesPromotions?locale=en-US&country=US&allowCountries=US'
            self.page.get(api_url)
            content = self.page.ele('tag:body').text
            data = json.loads(content)
            elements = data.get('data', {}).get('Catalog', {}).get('searchStore', {}).get('elements', [])
            for el in elements:
                promos = el.get('promotions')
                if not promos: continue
                offers = promos.get('promotionalOffers', [])
                if offers and offers[0].get('promotionalOffers'):
                    title = el.get('title')
                    slug = el.get('productSlug') or el.get('urlSlug')
                    if not slug: continue
                    price = el.get('price', {}).get('totalPrice', {}).get('discountPrice', -1)
                    if price == 0:
                        url = f"https://store.epicgames.com/en-US/p/{slug}"
                        games.append({'name': title, 'url': url})
        except: pass
        return games

    def claim_game(self, url: str, name: str) -> bool:
        """Claim a specific game with robust login enforcement."""
        print(f"🎁 Claiming game: {name}")
        try:
            self.page.get(url)
            time.sleep(4)
            
            # 1. ENFORCE LOGIN CHECK
            if not self._check_login_success():
                print("   ⚠️ Not logged in at start of claim. Attempting re-login...")
                if not self.login(self.account_email or "", ""):
                    print("   ❌ Failed to restore session. Aborting claim.")
                    return False
                self.page.get(url)
                time.sleep(3)

            # 2. Find the Primary CTA Button (Purchase/Get/Owned)
            print("   🔎 Analyzing CTA button state...")
            cta_btn = self.page.ele('@data-testid=purchase-cta-button', timeout=5)
            
            if not cta_btn:
                 # Fallback to general selectors if data-testid fails
                 selectors = ['text:Get', 'text:Free', 'text:Install', 'text:Yükle', 'text:Ücretsiz', 'button:Get']
                 for s in selectors:
                     cta_btn = self.page.ele(selector=s, timeout=2) # Named argument to be safe
                     if cta_btn: break

            if cta_btn:
                btn_text = cta_btn.text.strip().lower()
                print(f"   ℹ️ Button Text Detected: '{cta_btn.text}'")
                
                # If it's already in library, we are done
                if any(x in btn_text for x in ["library", "owned", "kütüphane", "sahip"]):
                    print(f"   ✅ Already in library. No action needed.")
                    return True
                
                # If it's NOT owned, it MUST be "Get" or similar
                if any(x in btn_text for x in ["get", "free", "yükle", "al", "ücretsiz", "install"]):
                    # Handle possible overlays (Age verification etc) before clicking
                    try:
                        overlay = self.page.ele('.eds_1v3qmn', timeout=1) or self.page.ele('@data-testid=slate-overlay', timeout=1)
                        if overlay:
                            print("   🛡️ Clearing overlay/age verification...")
                            overlay.click(by_js=True)
                            time.sleep(1)
                    except: pass

                    print(f"   🖱️ Clicking '{cta_btn.text}' to open checkout...")
                    cta_btn.scroll.to_see()
                    time.sleep(0.5)
                    cta_btn.click() # Try normal click first
                    time.sleep(1.5)
                    
                    # 3. Wait for Checkout URL, Modal, or Specific Heading
                    print("   ⏳ Waiting for checkout redirection or modal...")
                    checkout_reached = False
                    for i in range(20):
                        time.sleep(1)
                        curr_url = self.page.url.lower()
                        
                        # 3.1. URL check
                        if "checkout" in curr_url or "purchase" in curr_url:
                            checkout_reached = True
                            break
                        
                        # 3.2. Modal/Heading check (using user-provided markers)
                        if self.page.ele('.payment') or self.page.ele('text:Checkout') or self.page.ele('text:Siparişi Gözden Geçir'):
                            print("   ✅ Checkout modal/heading detected via DOM.")
                            checkout_reached = True
                            break

                        # 3.3. Check for age verification specifically
                        age_gate = self.page.ele('@data-testid=adult-content-age-gate') or self.page.ele('.eds_1v3qmn')
                        if age_gate:
                             age_btn = age_gate.ele('text:Continue') or age_gate.ele('text:Devam Et') or age_gate.ele('tag:button')
                             if age_btn:
                                 print(f"   🛡️ Resolving age gate... ({age_btn.text})")
                                 age_btn.click(by_js=True)
                                 time.sleep(2)
                                 continue
                        
                        # 3.4. Re-click fallback
                        if i > 0 and i % 5 == 0:
                            print(f"   🔄 Re-clicking '{cta_btn.text}' (Attempt {i//5 + 1})...")
                            cta_btn.click(by_js=True)
                    
                    if not checkout_reached:
                         print("   ❌ Failed to reach checkout. Still on PDP?")
                         self.page.get_screenshot(path=f"fail_checkout_reach_{name}.png")
                         return False

                    print("   ✅ Checkout reached. Syncing session context...")
                    time.sleep(6) 
                    
                    # Check for login prompt within checkout
                    is_login_needed = False
                    if "/id/login" in self.page.url:
                        is_login_needed = True
                    else:
                        login_btn = self.page.ele('text:Sign In') or self.page.ele('text:Log In')
                        if login_btn:
                             checkout_box = self.page.ele('.payment-confirm-container') or self.page.ele('.payment-summaries') or self.page.ele('.payment')
                             if checkout_box and (checkout_box.ele('text:Sign In') or checkout_box.ele('text:Log In')):
                                 is_login_needed = True

                    if is_login_needed:
                        print("   ⚠️ Checkout requires login sync. Re-injecting...")
                        cookies = self.cookie_manager.load_cookies(self.account_email)
                        if cookies:
                            self.page.set.cookies(cookies)
                            time.sleep(2)
                            self.page.refresh()
                            time.sleep(10)

                    # --- PRICE VERIFICATION ---
                    try:
                        price_valid = False
                        # Wait for price element
                        total_price_ele = self.page.ele('.payment-price__value--YOUPAY', timeout=10) or \
                                         self.page.ele('.payment-offer-summary__current-price', timeout=2) or \
                                         self.page.ele('.payment-price__value', timeout=1)
                        
                        if total_price_ele:
                            price_text = total_price_ele.text.strip().replace('\xa0', ' ')
                            print(f"   💰 Verified Price: {price_text}")
                            if any(x in price_text for x in ["0.00", "Free", "0,00", "Ücretsiz", "0", "Gratis", "TRY 0"]):
                                 price_valid = True
                        else:
                            # User provided HTML context: payment-offer-summary__current-price
                            offer_price_ele = self.page.ele('.payment-offer-summary__current-price', timeout=1)
                            if offer_price_ele:
                                price_text = offer_price_ele.text.strip().replace('\xa0', ' ')
                                if any(x in price_text for x in ["0.00", "Free", "0,00", "Ücretsiz", "0", "Gratis", "TRY 0"]):
                                     price_valid = True
                                     print(f"   💰 Price verified via offer summary: {price_text}")

                        if not price_valid:
                            # Full text check as last resort
                            body_text = self.page.ele('tag:body').text.lower()
                            if "0.00" in body_text or "free" in body_text or "ücretsiz" in body_text or "0,00" in body_text:
                                price_valid = True
                                print("   💰 Price verified via page text.")

                        if not price_valid:
                            print("   ⛔ SAFETY STOP: Price not verified as free.")
                            self.page.get_screenshot(name=f"price_error_{name}.png")
                            return False
                    except Exception as e:
                        print(f"   ⚠️ Price check error: {e}")
                        # Assume valid if -100% is visible
                        if self.page.ele('text:-100%'): price_valid = True

                    # --- DEBUG: DUMP HTML ---
                    except: pass

                    # --- DEEP DEBUGGING: DUMP IFRAME & BUTTON ANALYSIS ---
                    try:
                        # Find the checkout iframe specifically
                        checkout_frame = None
                        for f in self.page.frames:
                            if any(x in f.url for x in ['/purchase', '/checkout']) or 'payment' in f.url:
                                checkout_frame = f
                                break
                        
                        if checkout_frame:
                            with open(f"debug_iframe_checkout_{name}.html", "w", encoding="utf-8") as f:
                                f.write(checkout_frame.html)
                            print(f"   🐞 DEBUG: Checkout iframe HTML dumped to debug_iframe_checkout_{name}.html")
                        else:
                             print("   🐞 DEBUG: No specific checkout iframe found for dumping.")
                    except Exception as e:
                        print(f"   🐞 DEBUG ERROR: {e}")

                    # --- PLACE ORDER ---
                    print("   🔎 Looking for 'Place Order' button (Standardizing detection)...")
                    
                    def find_order_btn():
                        # Priority 1: Search in common checkout iframes
                        for f_selector in ['@src*=/purchase', '@title=Checkout', '@title=Ödeme']:
                            try:
                                frame = self.page.get_frame(f_selector, timeout=1)
                                if frame:
                                    # Target the specific button class from user's HTML
                                    btn = frame.ele('.payment-order-confirm__btn') or \
                                          frame.ele('@data-testid=purchase-order-button')
                                    
                                    if btn: return btn
                                    
                                    # Try by exact text match inside the specific button area
                                    # Multilingual support (Turkish/English)
                                    btn_text_el = frame.ele('text=SİPARİŞ VER') or \
                                                  frame.ele('text=Place Order') or \
                                                  frame.ele('text=Siparişi Ver')
                                    
                                    if btn_text_el:
                                        if btn_text_el.tag != 'button':
                                            parent_btn = btn_text_el.parent('tag:button')
                                            if parent_btn: return parent_btn
                                        return btn_text_el
                            except: pass

                        # Priority 2: Search main page
                        btn = self.page.ele('.payment-order-confirm__btn') or \
                              self.page.ele('@data-testid=purchase-order-button')
                        if btn: return btn

                        btn_text_el = self.page.ele('text=SİPARİŞ VER') or \
                                      self.page.ele('text=Place Order')
                        if btn_text_el:
                            if btn_text_el.tag != 'button':
                                parent_btn = btn_text_el.parent('tag:button')
                                if parent_btn: return parent_btn
                            return btn_text_el
                        
                        return None

                    place_btn = find_order_btn()

                    # DEBUG: Analyze found button
                    if place_btn:
                         try:
                             print(f"   🐞 DEBUG: Found Button Info:")
                             print(f"      - Tag: {place_btn.tag}")
                             print(f"      - Text: {place_btn.text}")
                             print(f"      - Classes: {place_btn.attr('class')}")
                             print(f"      - ID: {place_btn.attr('id')}")
                             print(f"      - Data-TestID: {place_btn.attr('data-testid')}")
                         except: pass

                    if place_btn:
                        print(f"   🖱️ Preparing to click 'Place Order' ({place_btn.text})...")
                        
                        # 4. Handle "I Agree" checkbox
                        # We MUST avoid the newsletter checkbox (payment-developer-privacy)
                        # The real agreement box is usually inside 'payment-order-confirm'
                        def find_agree_box():
                             # Try to find the container first
                             container = self.page.ele('.payment-order-confirm') or \
                                         self.page.ele('.payment-confirm-container')
                             if container:
                                 box = container.ele('.payment-check-box__input') or \
                                       container.ele('.payment-check-box__inner')
                                 if box: return box
                             
                             # Search in frames but be specific about the parent
                             for f_selector in ['@src*=/purchase', '@title=Checkout']:
                                 try:
                                     frame = self.page.get_frame(f_selector, timeout=1)
                                     if frame:
                                         # Look for the agreement text nearby
                                         agree_text = frame.ele('text:yönetteminin yetkin kullanıcısı') or \
                                                      frame.ele('text:18 yaşından büyük')
                                         if agree_text:
                                             # Finding the checkbox via parent/sibling from the text
                                             container = agree_text.parent('.payment-order-confirm')
                                             if container:
                                                 box = container.ele('.payment-check-box__input')
                                                 if box: return box
                                             # Fallback to any checkbox in THAT frame
                                             return frame.ele('.payment-check-box__input')
                                 except: pass
                             return None

                        agree_box = find_agree_box()

                        if agree_box:
                            print("   🖱️ Checking agreement checkbox...")
                            try:
                                # JS click is safer for hidden/stylized checkboxes to avoid "no size" errors
                                agree_box.click(by_js=True)
                            except Exception as e:
                                print(f"      ⚠️ Agreement box click error: {e}")
                            time.sleep(1)

                        # Final Click on Place Order
                        print("   🎯 Initiating final click...")
                        try:
                            # Try JS click directly since the "no size" error happened on normal interaction
                            # This bypasses the need for the element to be "interactable" in the classic sense (visible/sized)
                            place_btn.click(by_js=True)
                        except Exception as e:
                            print(f"      ❌ Final click failed: {e}")
                            # Last report: dump HTML
                            with open(f"debug_checkout_{name}.html", "w", encoding="utf-8") as f:
                                f.write(self.page.html)
                            return False
                        
                        print("   🏁 Place Order clicked. Waiting for confirmation...")
                        time.sleep(12) 
                        
                        # Success Detection
                        success_markers = [
                            'text:Thank you', 'text:Teşekkürler', 'text:Siparişin için teşekkürler',
                            'text:Confirmed', 'text:Onaylandı', 'text:Library', 'text:Kütüphane',
                            '@data-testid=order-status-logo'
                        ]
                        for sm in success_markers:
                            if self.page.ele(sm, timeout=3):
                                 print("   ✅ Claim successful!")
                                 return True
                        
                        # Check body text as fallback
                        body_low = self.page.ele('tag:body').text.lower()
                        if any(x in body_low for x in ["thank you", "teşekkürler", "library", "kütüphane"]):
                            print("   ✅ Claim successful (verified via text)!")
                            return True

                        print("   ⚠️ Claim process finished but success status could not be verified.")
                        # Take final screenshot for debug
                        self.page.get_screenshot(path=f"uncertain_success_{name}.png")
                        return False # Be strict: if we don't see the success screen, it's a fail.
                    else:
                        print("   ❌ 'Place Order' button not found.")
                        # Dump what we see for debugging
                        with open(f"fail_no_btn_{name}.html", "w", encoding="utf-8") as f:
                            f.write(self.page.html)
                        self.page.get_screenshot(path=f"fail_no_place_order_{name}.png")
                        return False
                else:
                    print(f"   ⚠️ Unexpected button state: '{btn_text}'")
                    return False
            else:
                 print("   ❌ CTA Button not found.")
                 try:
                    self.page.get_screenshot(path=f"debug_no_get_btn_{name}.png")
                 except: pass
                 return False
            
        except Exception as e:
            print(f"❌ Claim error: {e}")
            try:
                self.page.get_screenshot(path=f"error_claim_{name}.png")
            except: pass
            return False
