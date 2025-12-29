# ==============================================================================
# Epic Games Auto Game Collector
# Copyright (c) 2024 TheK3R1M
#
# DISCLAIMER: This software is for educational purposes only. 
# The author is not responsible for any misuse, account restrictions, or damages.
# Use at your own risk.
# ==============================================================================

"""CLI entry point for EpicAuto Collector."""

import asyncio
import sys
import argparse
import signal
from src.core import AccountManager, GameClaimer
from src.utils.startup import register_startup_task, unregister_startup_task

# Global claimer instance for cleanup on CTRL+C
_current_claimer = None

def _cleanup_on_interrupt(signum, frame):
    """Handle CTRL+C gracefully."""
    print("\n\n⚠️ Bot interrupted by user (CTRL+C)...")
    print("🔒 Closing browsers...")
    try:
        import subprocess
        subprocess.run(["taskkill", "/F", "/IM", "chrome.exe"], 
                      capture_output=True, timeout=5)
    except Exception:
        pass
    print("👋 Goodbye!")
    sys.exit(0)

signal.signal(signal.SIGINT, _cleanup_on_interrupt)


def main_menu():
    """Display main menu and return user choice."""
    print("\n" + "=" * 50)
    print("🎮 EpicAuto Collector")
    print("=" * 50)
    print("1. Add new account")
    print("2. List accounts")
    print("3. Delete account")
    print("4. Claim games")
    print("5. Open GUI")
    print("6. Exit")
    print("=" * 50)

    choice = input("Choose (1-6): ").strip()
    return choice


def add_account():
    """Add a new account."""
    manager = AccountManager()

    email = input("Enter email: ").strip()
    password = input("Enter password: ").strip()

    if email and password:
        manager.add_account(email, password)
        print("✅ Account added successfully!")
    else:
        print("❌ Email and password are required.")


def list_accounts():
    """List stored accounts."""
    manager = AccountManager()
    accounts = manager.get_all_accounts()

    if not accounts:
        print("❌ No accounts added.")
        return

    print("\n" + "=" * 50)
    print("📧 Saved Accounts:")
    print("=" * 50)
    for i, acc in enumerate(accounts, 1):
        print(f"{i}. {acc['email']} - Status: {acc['status']}")
        if acc['claimed_games']:
            print(f"   Claimed games: {len(acc['claimed_games'])}")
    print("=" * 50)


def remove_account():
    """Remove an account by email."""
    manager = AccountManager()

    email = input("Enter email to delete: ").strip()

    account = manager.get_account(email)
    if account:
        confirm = input(
            f"Are you sure you want to delete '{email}'? (yes/no): "
        ).lower()
        if confirm == "yes":
            manager.remove_account(email)
            print("✅ Account deleted!")
        else:
            print("❌ Operation cancelled.")
    else:
        print(f"❌ Account not found: {email}")


async def claim_games():
    """Claim free games for all accounts."""
    manager = AccountManager()
    accounts = manager.get_all_accounts()

    if not accounts:
        print("❌ No accounts added. Please add accounts first.")
        return

    print(f"\n✨ Will claim games for {len(accounts)} account(s)...")
    print("⚠️ NOTE: First login may require 2FA.")
    print("    After cookies are saved, 2FA should not be needed later.\n")

    claimer = GameClaimer()
    await claimer.claim_free_games_for_all_accounts()


def open_gui():
    """Launch the GUI interface."""
    try:
        # Check specific dependency first
        import customtkinter
        from src.gui.app import GameClaimerApp

        app = GameClaimerApp()
        app.run()
    except ImportError as e:
        print("\n❌ Missing dependencies for GUI.")
        print("Please install CustomTkinter first:")
        print("   pip install customtkinter pillow")
        print(f"\nError details: {e}")
        input("Press Enter to return to menu...")
    except ImportError:
        print("❌ PySimpleGUI is not installed. Please use console mode.")
    except Exception as exc:  # pragma: no cover - best effort reporting
        print(f"❌ GUI error: {exc}")


def main():
    """Entry point with optional auto/registration flags."""
    parser = argparse.ArgumentParser(description="EpicAuto Collector CLI")
    parser.add_argument("--auto", action="store_true", help="Silent mode: claim and exit")
    parser.add_argument("--register-auto", action="store_true", help="Add startup Task Scheduler job")
    parser.add_argument("--unregister-auto", action="store_true", help="Remove startup Task Scheduler job")
    parser.add_argument("--task-name", default="EpicAutoCollector", help="Task Scheduler task name")
    args, unknown = parser.parse_known_args()

    # Auto-run mode: directly claim and exit
    if args.auto:
        asyncio.run(claim_games())
        return

    # Register/unregister startup tasks
    exe_path = sys.executable
    script_cmd = f"{exe_path} -m src.main --auto"
    if args.register_auto:
        ok, msg = register_startup_task(args.task_name, script_cmd)
        print(msg)
        return
    if args.unregister_auto:
        ok, msg = unregister_startup_task(args.task_name)
        print(msg)
        return

    # Interactive menu
    while True:
        choice = main_menu()

        try:
            if choice == "1":
                add_account()
            elif choice == "2":
                list_accounts()
            elif choice == "3":
                remove_account()
            elif choice == "4":
                asyncio.run(claim_games())
            elif choice == "5":
                open_gui()
            elif choice == "6":
                print("👋 Goodbye!")
                sys.exit(0)
            else:
                print("❌ Invalid choice. Please pick 1-6.")

        except KeyboardInterrupt:
            print("\n⚠️ Program interrupted by user.")
            sys.exit(0)
        except Exception as exc:
            print(f"❌ Error occurred: {exc}")
            import traceback

            traceback.print_exc()
            input("Press Enter to continue...")


if __name__ == "__main__":
    main()
