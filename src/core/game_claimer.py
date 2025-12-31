# ==============================================================================
# Epic Games Auto Game Collector
# Copyright (c) 2024 TheK3R1M
#
# DISCLAIMER: This software is for educational purposes only. 
# The author is not responsible for any misuse, account restrictions, or damages.
# Use at your own risk.
# ==============================================================================

# Game Claimer - claim flow
import asyncio
from typing import List, Dict
from .account_manager import AccountManager

from .epic_drission_connector import EpicDrissionConnector
from src.utils.claimed_history import ClaimedHistory


class GameClaimer:
    """Automatically claim games."""
    
    def __init__(self, account_manager: AccountManager = None):
        if account_manager:
            self.account_manager = account_manager
        else:
            self.account_manager = AccountManager()
        self.results = []
        self.history = ClaimedHistory()
        self.active_connectors = [] # Removed type hint to allow mixed types
    
    async def claim_free_games_for_account(self, email: str) -> Dict:
        """Claim free games for a single account."""
        result = {
            "email": email,
            "status": "pending",
            "free_games": [],
            "claimed_games": [],
            "already_owned": [],
            "errors": [],
            "cookies_saved": False,
            "real_account_key": email
        }
        
        connector = None
        try:
            # USE DRISSION CONNECTOR BY DEFAULT due to Playwright detection
            connector = EpicDrissionConnector(account_email=email)
            self.active_connectors.append(connector)
            
            # Wrap synchronous DrissionPage calls in to_thread
            await asyncio.to_thread(connector.initialize)
            
            # fetch account
            account = self.account_manager.get_account(email)
            if not account:
                result["status"] = "error"
                result["errors"].append("Account not found")
                return result
            
            # decrypt password
            password = self.account_manager.decrypt_password(account["password"])
            
            # login
            print(f"\n📧 Signing in for {email}...")
            login_success = await asyncio.to_thread(connector.login, email, password)
            if not login_success:
                result["status"] = "login_failed"
                result["errors"].append("Login failed or 2FA failed")
                return result
            
            # capture real account key detected during login for dedupe
            if connector.last_real_account_key:
                result["real_account_key"] = connector.last_real_account_key
                print(f"ℹ️ Using real account key: {connector.last_real_account_key}")

            result["cookies_saved"] = True
            print(f"✅ Cookies saved successfully")
            
            # fetch free games
            print(f"🎮 Checking free games...")
            free_games = await asyncio.to_thread(connector.get_free_games)
            result["free_games"] = free_games
            
            if not free_games:
                print(f"⚠️ No games found")
                result["status"] = "success"
                result["errors"].append("Game list empty")
                return result
            
            # check already claimed (site + local history)
            print(f"📚 Checking previously claimed games...")
            claimed_games = await asyncio.to_thread(connector.check_claimed_games)
            result["already_owned"] = claimed_games
            
            # Sort genericly or keep original order
            free_games_sorted = free_games
            
            # claim new games
            print(f"🎁 Claiming new games...")
            for i, game in enumerate(free_games_sorted, 1):
                game_name = game.get("name", "Unknown")
                game_url = game.get("url", "")
                game_id = self._normalize_game_id(game_url, game_name)

                # check both Epic library and local history
                is_already_owned_site = any(game_name.lower() in owned.lower() for owned in claimed_games)
                is_already_owned_local = self.history.is_claimed(game_id, email)

                if not is_already_owned_site and not is_already_owned_local and game_url:
                    print(f"\n   [{i}/{len(free_games)}] {game_name}")
                    print(f"🎁 Claiming game: {game_name}")
                    try:
                        claim_success = await asyncio.to_thread(connector.claim_game, game_url, game_name)
                        if claim_success:
                            result["claimed_games"].append(game_name)
                            self.history.add_claim(game_id, game_name, email)
                            print(f"   ✅ Claimed successfully")
                        else:
                            result["errors"].append(f"Failed to claim {game_name}")
                    except Exception as e:
                        result["errors"].append(f"Error claiming {game_name}: {e}")
                    await asyncio.sleep(1)  # small pause between games
                else:
                    if is_already_owned_site or is_already_owned_local:
                        print(f"   ℹ️ Already owned/processed: {game_name}")
                    else:
                        print(f"   ⚠️ Invalid URL: {game_name}")
            
            result["status"] = "success"
            
            # update account status
            self.account_manager.update_account_status(
                email, 
                "active", 
                claimed_games=result["claimed_games"]
            )
            
        except Exception as e:
            result["status"] = "error"
            result["errors"].append(str(e))
            print(f"❌ Error occurred: {str(e)}")
        
        finally:
            if connector:
                try:
                    connector.close()
                    if connector in self.active_connectors:
                        self.active_connectors.remove(connector)
                except Exception as e:
                    print(f"⚠️ Cleanup error for {email}: {e}")
        
        return result
    
    async def claim_free_games_for_all_accounts(self) -> List[Dict]:
        """Claim free games for all accounts."""
        print("=" * 50)
        print("🚀 Epic Games - Auto Claim Started")
        print("=" * 50)
        
        accounts = self.account_manager.get_all_accounts()
        
        # Run accounts concurrently with Semaphore
        print(f"\n🚀 Starting {len(accounts)} account(s) using Parallel Processing (Limit: 3)...\n")
        
        # Filter only active
        active_accounts = [acc for acc in accounts if acc.get("status") == "active"]
        skipped_count = len(accounts) - len(active_accounts)
        if skipped_count > 0:
            print(f"⏩ Skipped {skipped_count} disabled account(s).")
            
        all_results = []
        sem = asyncio.Semaphore(3) # Max 3 browsers

        async def limited_claim(account):
            async with sem:
                try:
                    res = await self.claim_free_games_for_account(account["email"])
                    return res
                except Exception as e:
                    print(f"❌ Worker error: {e}")
                    return Exception(f"Worker failed: {e}")

        tasks = [limited_claim(acc) for acc in active_accounts]
        if tasks:
             all_results = await asyncio.gather(*tasks)
        else:
             print("⚠️ No active accounts to process.")
        
        # Original sequential logic removed
        
        # Deduplicate by real account key
        processed_keys = set()
        results = []
        for result in all_results:
            if isinstance(result, Exception):
                print(f"❌ Account processing error: {result}")
                continue
            connector_key = result.get("real_account_key") or result.get("email")
            if connector_key in processed_keys:
                print(f"ℹ️ Skipping duplicate account session for {connector_key}")
                continue
            processed_keys.add(connector_key)
            results.append(result)
        
        # show summary
        self._print_results(results)
        self.results = results
        return results
    
    def _print_results(self, results: List[Dict]):
        """Print summary results."""
        print("\n" + "=" * 50)
        print("📊 Results")
        print("=" * 50)
        
        total_claimed = 0
        total_errors = 0
        
        for result in results:
            print(f"\n📧 {result['email']}")
            print(f"   Status: {result['status']}")
            print(f"   Claimed: {len(result['claimed_games'])}")
            print(f"   Already owned: {len(result['already_owned'])}")
            print(f"   Errors: {len(result['errors'])}")
            
            if result['claimed_games']:
                print(f"   ✅ Claimed games:")
                for game in result['claimed_games']:
                    print(f"      - {game}")
            
            if result['errors']:
                print(f"   ❌ Errors:")
                for error in result['errors']:
                    print(f"      - {error}")
            
            total_claimed += len(result['claimed_games'])
            total_errors += len(result['errors'])
        
        print("\n" + "=" * 50)
        print(f"📈 Total Claimed: {total_claimed}")
        print(f"⚠️ Total Errors: {total_errors}")
        print("=" * 50)

    def _normalize_game_id(self, game_url: str, game_name: str) -> str:
        """Generate a stable game identifier from URL or name."""
        if game_url:
            # Use last path segment as ID if possible
            parts = game_url.split("/")
            slug = parts[-1] or (len(parts) > 1 and parts[-2]) or ""
            slug = slug.split("?")[0]
            if slug:
                return slug.lower()
        return game_name.strip().lower()

    async def _cleanup_all(self):
        """Force-close all active connectors."""
        for connector in list(self.active_connectors):
            try:
                connector.close()
            except Exception:
                pass
            self.active_connectors.remove(connector)
