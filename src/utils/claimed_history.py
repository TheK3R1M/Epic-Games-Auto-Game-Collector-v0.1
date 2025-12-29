import json
import os
from datetime import datetime
from typing import List, Dict


class ClaimedHistory:
    """Persist and query claimed free games per account."""

    def __init__(self, path: str = "data/claimed_history.json"):
        self.path = path
        os.makedirs(os.path.dirname(self.path), exist_ok=True)
        self._data = {"claims": []}
        self._load()

    def _load(self) -> None:
        if os.path.exists(self.path):
            try:
                with open(self.path, "r", encoding="utf-8") as f:
                    self._data = json.load(f)
            except Exception:
                self._data = {"claims": []}

    def _save(self) -> None:
        with open(self.path, "w", encoding="utf-8") as f:
            json.dump(self._data, f, indent=2, ensure_ascii=False)

    def is_claimed(self, game_id: str, account_email: str) -> bool:
        for entry in self._data.get("claims", []):
            if entry.get("game_id") == game_id and entry.get("account_email") == account_email:
                return True
        return False

    def add_claim(self, game_id: str, game_name: str, account_email: str) -> None:
        entry = {
            "game_id": game_id,
            "game_name": game_name,
            "account_email": account_email,
            "claimed_at": datetime.utcnow().isoformat() + "Z",
        }
        self._data.setdefault("claims", []).append(entry)
        self._save()

    def list_claims(self) -> List[Dict]:
        return list(self._data.get("claims", []))
