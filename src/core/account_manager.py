# Account Manager - account management
import json
import os
from cryptography.fernet import Fernet
from typing import List, Dict, Optional
from datetime import datetime
from src.security.cookie_manager import CookieManager


class AccountManager:
    """Manage accounts: add, remove, encrypt."""
    
    def __init__(self, accounts_file: str = "data/accounts.json", key_file: str = "data/key.key"):
        self.accounts_file = accounts_file
        self.key_file = key_file
        self.cipher = self._load_or_create_key()
        self.accounts = []
        self._load_accounts()
        self.purge_masked_accounts()
        self.cookie_manager = CookieManager()
    
    def _load_or_create_key(self) -> Fernet:
        """Load or create encryption key."""
        os.makedirs("data", exist_ok=True)
        
        if os.path.exists(self.key_file):
            with open(self.key_file, 'rb') as f:
                key = f.read()
        else:
            key = Fernet.generate_key()
            with open(self.key_file, 'wb') as f:
                f.write(key)
        
        return Fernet(key)
    
    def _load_accounts(self):
        """Load accounts from disk."""
        if os.path.exists(self.accounts_file):
            try:
                with open(self.accounts_file, 'r') as f:
                    data = json.load(f)
                    if isinstance(data, list):
                        self.accounts = data
                    else:
                        self.accounts = []
            except Exception as e:
                print(f"⚠️ Error loading accounts: {e}")
                self.accounts = []
        else:
            self.accounts = []

    def purge_masked_accounts(self):
        """Remove accounts with masked or invalid emails."""
        initial_count = len(self.accounts)
        
        def is_valid(email):
            e = str(email).lower()
            if "*" in e: return False
            if "sentry.io" in e: return False
            if "epicgames.com" in e: return False
            # Ensure at least 3 chars before @
            if "@" in e:
                prefix = e.split("@")[0]
                if len(prefix) < 3: return False
            else:
                return False # No @ is invalid
            return True

        cleaned = [acc for acc in self.accounts if is_valid(acc.get("email", ""))]
        
        if len(cleaned) < initial_count:
            self.accounts = cleaned
            print(f"🧹 Purged {initial_count - len(cleaned)} invalid/masked accounts from list.")
            self._save_accounts()
    
    def _save_accounts(self):
        """Persist accounts to disk."""
        os.makedirs(os.path.dirname(self.accounts_file), exist_ok=True)
        with open(self.accounts_file, 'w') as f:
            json.dump(self.accounts, f, indent=4)
    
    def add_account(self, email: str, password: str = "", status: str = "pending") -> bool:
        """Add or update an account."""
        email = email.lower().strip()
        # encrypt password (or empty string)
        encrypted_password = self.cipher.encrypt(password.encode()).decode()
        
        # Check if exists
        for acc in self.accounts:
            if acc["email"].lower() == email:
                acc["password"] = encrypted_password
                acc["status"] = status
                acc["last_login"] = datetime.now().isoformat()
                self._save_accounts()
                print(f"🔄 Account updated: {email}")
                return True

        account = {
            "id": datetime.now().timestamp(),
            "email": email,
            "password": encrypted_password,
            "cookies": self.cookie_manager._get_cookie_file(email),
            "last_login": datetime.now().isoformat(),
            "status": status,
            "claimed_games": []
        }
        
        self.accounts.append(account)
        self._save_accounts()
        print(f"✅ Account added: {email}")
        return True
    
    def remove_account(self, email: str) -> bool:
        """Remove an account."""
        email = email.lower()
        self.accounts = [acc for acc in self.accounts if acc["email"].lower() != email]
        self._save_accounts()
        # Also delete cookies
        self.cookie_manager.delete_cookies(email)
        print(f"✅ Account removed: {email}")
        return True
    
    def get_account(self, email: str) -> Optional[Dict]:
        """Get an account by email."""
        email = email.lower()
        for acc in self.accounts:
            if acc["email"].lower() == email:
                return acc
        return None
    
    def decrypt_password(self, encrypted_password: str) -> str:
        """Decrypt stored password."""
        return self.cipher.decrypt(encrypted_password.encode()).decode()
    
    def get_all_accounts(self) -> List[Dict]:
        """Return all accounts."""
        return self.accounts
    
    def update_account_status(self, email: str, status: str, claimed_games: List[str] = None):
        """Update account status and claimed games."""
        for acc in self.accounts:
            if acc["email"] == email:
                acc["status"] = status
                acc["last_login"] = datetime.now().isoformat()
                if claimed_games is not None:
                    # merge with previously claimed games
                    existing = set(acc.get("claimed_games", []))
                    new_games = set(claimed_games)
                    acc["claimed_games"] = list(existing.union(new_games))
                break
        self._save_accounts()
        print(f"💾 Account status updated: {email} -> {status}")
