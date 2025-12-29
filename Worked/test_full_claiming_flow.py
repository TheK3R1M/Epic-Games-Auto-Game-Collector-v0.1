
import os
import json
import time
from src.core.epic_drission_connector import EpicDrissionConnector

def test_full_claim_all_accounts():
    print("🚀 --- MULTI-ACCOUNT CLAIMING FLOW TEST ---")
    
    cookie_dir = "data/cookies"
    if not os.path.exists(cookie_dir):
        print(f"❌ No cookie directory found at {cookie_dir}")
        return

    cookie_files = [f for f in os.listdir(cookie_dir) if f.endswith("_cookies.json")]
    if not cookie_files:
        print("❌ No cookie files found in the vault.")
        return

    print(f"📋 Found {len(cookie_files)} account session(s).")

    for i, cookie_file in enumerate(cookie_files, 1):
        file_path = os.path.join(cookie_dir, cookie_file)
        try:
            with open(file_path, 'r') as f:
                data = json.load(f)
                email = data.get("email", "USER")
        except Exception as e:
            print(f"   ❌ Error reading {cookie_file}: {e}")
            continue

        print(f"\n🚀 [{i}/{len(cookie_files)}] Starting test for: {email}")
        
        connector = EpicDrissionConnector(account_email=email)
        if not connector.initialize():
            print(f"   ❌ Failed to Open Browser for {email}.")
            continue

        try:
            # 1. Login with cookies
            print(f"🔐 Phase 1: Cookie Injection for {email}")
            if not connector.login(email, ""):
                print(f"   ❌ Failed to restore session for {email}.")
                continue

            # 2. Get Free Games
            print(f"\n🎁 Phase 2: Finding Free Games")
            free_games = connector.get_free_games()
            if not free_games:
                print("   ℹ️ No free games found or API error.")
                continue

            # 3. Try Claiming all found games
            for target in free_games:
                print(f"\n🎮 Phase 3: Claiming '{target['name']}'")
                success = connector.claim_game(target['url'], target['name'])
                
                if success:
                    print(f"   🏆 SUCCESS: Game '{target['name']}' processed!")
                else:
                    print(f"   ❌ FAILED: Could not complete claim for '{target['name']}'.")

        except Exception as e:
            print(f"   ❌ Unexpected error for {email}: {e}")
        finally:
            time.sleep(2)
            connector.close()
            print(f"🔌 Browser closed for {email}.")

if __name__ == "__main__":
    test_full_claim_all_accounts()
