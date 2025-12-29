import os
import time
import sys
from typing import List, Dict

try:
    import undetected_chromedriver as uc
    _HAS_UC = True
except Exception:
    _HAS_UC = False
    from selenium import webdriver
    from selenium.webdriver.chrome.options import Options as ChromeOptions


def _to_playwright_cookies(selenium_cookies: List[Dict]) -> List[Dict]:
    pw_cookies = []
    for c in selenium_cookies:
        pw_cookies.append({
            'name': c.get('name', ''),
            'value': c.get('value', ''),
            'domain': c.get('domain', '').lstrip('.'),
            'path': c.get('path', '/'),
            'expires': float(c.get('expiry', -1)) if c.get('expiry') else -1,
            'httpOnly': bool(c.get('httpOnly', False)),
            'secure': bool(c.get('secure', False)),
            'sameSite': 'Lax',
        })
    return pw_cookies


def capture_cookies_with_selenium(email: str) -> List[Dict]:
    """
    Launch a local Chrome with undetected-chromedriver, let the user login manually,
    then return cookies converted to Playwright format.
    """
    safe_email = email.replace('@', '_').replace('.', '_')
    profile_dir = os.path.abspath(os.path.join('data', 'selenium_profiles', safe_email))
    os.makedirs(profile_dir, exist_ok=True)

    driver = None
    try:
        if _HAS_UC:
            options = uc.ChromeOptions()
            options.add_argument(f"--user-data-dir={profile_dir}")
            options.add_argument("--no-sandbox")
            options.add_argument("--disable-dev-shm-usage")
            options.add_argument("--lang=en-US")
            driver = uc.Chrome(options=options)
        else:
            options = ChromeOptions()
            options.add_argument(f"--user-data-dir={profile_dir}")
            options.add_argument("--no-sandbox")
            options.add_argument("--disable-dev-shm-usage")
            options.add_argument("--lang=en-US")
            driver = webdriver.Chrome(options=options)

        driver.set_window_size(1280, 900)
        driver.get("https://www.epicgames.com/id/login?lang=en-US&redirectUrl=https%3A%2F%2Fstore.epicgames.com%2Fen-US%2F")
        print("\n📝 A Chrome window opened for manual login.")
        print("   Complete login (CAPTCHA/2FA if shown).")

        # Non-interactive safe wait: if stdin isn't a TTY, poll the page until store is reached
        stdin_tty = sys.stdin and hasattr(sys.stdin, "isatty") and sys.stdin.isatty()
        if stdin_tty:
            print("   Return here and press Enter when you see the store page.")
            try:
                input("   Press Enter once the store page is visible in Chrome...")
            except EOFError:
                stdin_tty = False

        if not stdin_tty:
            print("   Non-interactive mode: waiting for store page automatically...")
            for _ in range(180):  # up to ~180s
                try:
                    url = driver.current_url or ""
                    title = driver.title or ""
                    if ("store.epicgames.com" in url.lower()) or ("store" in title.lower()):
                        break
                    # also check for a signed-in user component
                    logged_in = driver.execute_script(
                        "return !!(document.querySelector('[data-component=\\'SignedInUser\\']') || document.querySelector('[data-component*=\\'Profile\\']'));"
                    )
                    if logged_in:
                        break
                except Exception:
                    pass
                time.sleep(1)

        # Small grace period
        time.sleep(1.5)
        sel_cookies = driver.get_cookies() or []
        return _to_playwright_cookies(sel_cookies)
    finally:
        try:
            if driver:
                driver.quit()
        except Exception:
            pass
