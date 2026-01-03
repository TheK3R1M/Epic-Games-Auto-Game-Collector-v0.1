import json
import os
from datetime import datetime
from typing import List, Dict
from src.utils.paths import get_data_dir


class ClaimedHistory:
    """Persist and query claimed free games per account."""

    def __init__(self, path: str = None):
        if path is None:
            path = os.path.join(get_data_dir(), "claimed_history.json")
        self.path = path
        os.makedirs(os.path.dirname(self.path), exist_ok=True)
        # Initialize with the new structure
        self._data = {
            "global_claims": {},  # Deduped by game_id
            "account_claims": {}, # game_ids claimed per account
            "recent_logs": []     # For UI display
        }
        self._load()

    def _load(self) -> None:
        if os.path.exists(self.path):
            try:
                with open(self.path, "r", encoding="utf-8") as f:
                    loaded_data = json.load(f)
                    # Merge loaded data with default structure to handle schema evolution
                    self._data.update(loaded_data)
            except Exception:
                # If loading fails, keep the default empty structure
                pass

    def _save(self) -> None:
        with open(self.path, "w", encoding="utf-8") as f:
            json.dump(self._data, f, indent=2, ensure_ascii=False)

    def is_claimed(self, game_id: str, account_email: str) -> bool:
        # Check if the game_id is in the account's claimed list
        return game_id in self._data.get("account_claims", {}).get(account_email, [])

    def add_claim(self, game_id: str, game_name: str, account_email: str, image_url: str = "", price: str = "Unknown", status: str = "Success"):
        """Add a successful claim to history."""
        # 1. Update Global List (Deduped by game_id)
        # Find if game exists, if not add it
        if game_id not in self._data["global_claims"]:
            self._data["global_claims"][game_id] = {
                "name": game_name,
                "first_claimed_at": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                "image_url": image_url,
                "price": price
            }
        
        # 2. Update Account Record
        if account_email not in self._data["account_claims"]:
            self._data["account_claims"][account_email] = []
        
        # check if already in account list
        if game_id not in self._data["account_claims"][account_email]:
            self._data["account_claims"][account_email].append(game_id)
        
        # 3. Add to Recent Log (for UI)
        log_entry = {
            "game_name": game_name,
            "game_id": game_id,
            "account": account_email,
            "date": datetime.now().strftime("%Y-%m-%d %H:%M"),
            "timestamp": datetime.now().timestamp(),
            "image_url": image_url,
            "price": price,
            "status": status,
            "source": "Epic Games Store"
        }
        self._data["recent_logs"].insert(0, log_entry)
        # Keep only last 1000 logs
        if len(self._data["recent_logs"]) > 1000:
            self._data["recent_logs"] = self._data["recent_logs"][:1000]
        
        self._save()

    def list_claims(self) -> List[Dict]:
        # This method's behavior needs to be redefined based on the new data structure.
        # For now, returning a simplified list of all globally claimed games.
        # If the intent was to list claims per account, a parameter would be needed.
        return list(self._data.get("global_claims", {}).values())

    def get_account_claims(self, account_email: str) -> List[str]:
        """Returns a list of game_ids claimed by a specific account."""
        return self._data.get("account_claims", {}).get(account_email, [])

    def get_recent_logs(self) -> List[Dict]:
        """Returns the list of recent claim logs."""
        return self._data.get("recent_logs", [])
