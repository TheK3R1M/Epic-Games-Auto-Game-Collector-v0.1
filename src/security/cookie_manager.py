# Cookie Manager - cookie management
import json
import os
from datetime import datetime, timedelta
from pathlib import Path
from src.utils.paths import get_data_dir


class CookieManager:
    """Store and manage cookies."""
    
    def __init__(self, cookies_dir: str = None):
        if cookies_dir is None:
            cookies_dir = os.path.join(get_data_dir(), "cookies")
        self.cookies_dir = cookies_dir
        os.makedirs(self.cookies_dir, exist_ok=True)
        print(f"📁 Cookie storage: {self.cookies_dir}")
    
    def _get_cookie_file(self, email: str) -> str:
        """Return cookie file path for email."""
        import re
        safe_email = re.sub(r'[^a-zA-Z0-9]', '_', email)
        path = os.path.join(self.cookies_dir, f"{safe_email}_cookies.json")
        return path
    
    def save_cookies(self, email: str, cookies: list) -> bool:
        """Persist cookies to disk."""
        try:
            cookie_file = self._get_cookie_file(email)
            cookie_data = {
                "email": email,
                "cookies": cookies,
                "saved_at": datetime.now().isoformat(),
                "expires_at": (datetime.now() + timedelta(days=30)).isoformat()
            }
            
            with open(cookie_file, 'w') as f:
                json.dump(cookie_data, f, indent=4)
            
            print(f"✅ Cookies saved for {email} to: {cookie_file}")
            return True
        except Exception as e:
            print(f"❌ Cookies save failed: {str(e)}")
            return False
    
    def load_cookies(self, email: str) -> list | None:
        """Load cookies from disk. Returns list or None if missing/expired.
        Supports both direct email match and epic_ prefixed remapped files."""
        cookie_file = self._get_cookie_file(email)
        
        # If file doesn't exist with email, it might be an epic_ key already
        if not os.path.exists(cookie_file):
            # Check if this is already an epic_ key
            if email.startswith("epic_"):
                alt_file = os.path.join(self.cookies_dir, f"{email}_cookies.json")
                if os.path.exists(alt_file):
                    cookie_file = alt_file
                else:
                    print(f"ℹ️ Cookies file not found: {email}")
                    return None
            else:
                print(f"ℹ️ Cookies file not found: {email}")
                return None
        try:
            print(f"📂 Loading cookies from: {cookie_file}")
            with open(cookie_file, 'r') as f:
                cookie_data = json.load(f)
            
            # check expiry
            expires_at = datetime.fromisoformat(cookie_data["expires_at"])
            if datetime.now() > expires_at:
                print(f"⚠️ Cookies expired: {email}")
                os.remove(cookie_file)
                return None
            
            print(f"✅ Cookies loaded: {email}")
            return cookie_data["cookies"]
        
        except Exception as e:
            print(f"❌ Error loading cookies: {str(e)}")
            return None
    
    def delete_cookies(self, email: str) -> bool:
        """Delete stored cookies."""
        try:
            cookie_file = self._get_cookie_file(email)
            if os.path.exists(cookie_file):
                os.remove(cookie_file)
                print(f"✅ Cookies deleted: {email}")
                return True
            return False
        except Exception as e:
            print(f"❌ Error deleting cookies: {str(e)}")
            return False
    
    def cookies_exist(self, email: str) -> bool:
        """Check if valid cookies exist for this specific email."""
        cookie_file = self._get_cookie_file(email)
        if os.path.exists(cookie_file):
            try:
                with open(cookie_file, 'r') as f:
                    cookie_data = json.load(f)
                
                # Check if it actually belongs to this email (case insensitive)
                stored_email = cookie_data.get("email", "").lower()
                target_email = email.lower()
                
                if stored_email != target_email and not email.startswith("epic_"):
                    print(f"   ℹ️ Cookie email mismatch: {stored_email} != {target_email}")
                    return False

                expires_at = datetime.fromisoformat(cookie_data["expires_at"])
                if datetime.now() > expires_at:
                    print(f"   ℹ️ Cookie expired: {email}")
                    return False
                
                return True
            except Exception as e:
                print(f"   ℹ️ Error checking cookie: {e}")
                return False
        
        print(f"   ℹ️ Cookie file not found for: {email}")
        return False

    def move_cookies(self, old_email: str, new_email: str) -> bool:
        """Rename/move cookie file from old key to new key.
        Useful when the actually logged-in account differs from the user-provided email.
        """
        try:
            old_path = self._get_cookie_file(old_email)
            new_path = self._get_cookie_file(new_email)
            if os.path.exists(old_path):
                # If destination exists, overwrite to ensure correctness
                os.makedirs(os.path.dirname(new_path), exist_ok=True)
                # Read and re-write to keep JSON intact and update stored email field
                with open(old_path, 'r') as f:
                    data = json.load(f)
                data["email"] = new_email
                with open(new_path, 'w') as f:
                    json.dump(data, f, indent=4)
                # Remove old file
                try:
                    os.remove(old_path)
                except Exception:
                    pass
                print(f"🔁 Cookies remapped: {old_email} -> {new_email}")
                return True
            return False
        except Exception as e:
            print(f"❌ Error moving cookies: {str(e)}")
            return False

    def get_expiry_days(self, email: str) -> int:
        """Return number of days until cookie expiration. Returns -1 if invalid/expired."""
        try:
            cookie_file = self._get_cookie_file(email)
            if not os.path.exists(cookie_file):
                # Try epic_ prefix fallback
                if email.startswith("epic_"):
                     cookie_file = os.path.join(self.cookies_dir, f"{email}_cookies.json")
                
                if not os.path.exists(cookie_file):
                    return -1

            with open(cookie_file, 'r') as f:
                data = json.load(f)
            
            expires_at = datetime.fromisoformat(data["expires_at"])
            delta = expires_at - datetime.now()
            return delta.days
        except Exception:
            return -1
