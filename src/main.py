# ==============================================================================
# Epic Games Auto Game Collector
# Copyright (c) 2024 TheK3R1M
#
# DISCLAIMER: This software is for educational purposes only. 
# The author is not responsible for any misuse, account restrictions, or damages.
# Use at your own risk.
# ==============================================================================

"""Entry point for EpicAuto Collector (GUI Default)."""

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


async def claim_games_console():
    """Claim free games for all accounts (Headless/Auto Mode)."""
    manager = AccountManager()
    accounts = manager.get_all_accounts()

    if not accounts:
        print("❌ No accounts added. Please use the GUI to add accounts first.")
        return

    print(f"\n✨ Will claim games for {len(accounts)} account(s)...")
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
        input("Press Enter to exit...")
    except Exception as exc: 
        print(f"❌ GUI error: {exc}")
        import traceback
        traceback.print_exc()
        input("Press Enter to exit...")


def main():
    """Entry point with optional auto/registration flags."""
    parser = argparse.ArgumentParser(description="EpicAuto Collector")
    parser.add_argument("--auto", action="store_true", help="Silent mode: claim and exit")
    parser.add_argument("--register-auto", action="store_true", help="Add startup Task Scheduler job")
    parser.add_argument("--unregister-auto", action="store_true", help="Remove startup Task Scheduler job")
    parser.add_argument("--task-name", default="EpicAutoCollector", help="Task Scheduler task name")
    args, unknown = parser.parse_known_args()

    # Auto-run mode: directly claim and exit (for Task Scheduler)
    if args.auto:
        asyncio.run(claim_games_console())
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

    # DEFAULT: Launch GUI
    open_gui()


if __name__ == "__main__":
    main()
