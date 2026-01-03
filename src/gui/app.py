
import customtkinter as ctk
import os
import sys
import threading
import asyncio
from typing import Optional
from PIL import Image

# Import Frames
from .frames.dashboard import DashboardFrame
from .frames.history import HistoryFrame
from .frames.settings import SettingsFrame

# Import Backend
from src.core.game_claimer import GameClaimer
from src.core.account_manager import AccountManager

class GameClaimerApp(ctk.CTk):
    def __init__(self):
        super().__init__()

        # Window Setup
        self.title("Epic Games Auto Collector")
        self.geometry("1100x700")
        
        # Theme Setup
        ctk.set_appearance_mode("Dark")
        ctk.set_default_color_theme("dark-blue")
        
        # Data
        self.account_manager = AccountManager()
        self.claimer = GameClaimer(self.account_manager)
        self.running_task: Optional[asyncio.Task] = None
        self.loop_thread: Optional[threading.Thread] = None
        self.stop_event = threading.Event()

        # Layout Configuration
        self.grid_columnconfigure(1, weight=1)
        self.grid_rowconfigure(0, weight=1)

        # Init UI
        self._create_sidebar()
        self._create_main_frames()
        
        # Show default frame
        self._select_frame("dashboard")

    def _create_sidebar(self):
        """Create the left sidebar navigation."""
        self.sidebar_frame = ctk.CTkFrame(self, width=200, corner_radius=0)
        self.sidebar_frame.grid(row=0, column=0, sticky="nsew")
        self.sidebar_frame.grid_rowconfigure(4, weight=1)

        # Logo / Title
        self.logo_label = ctk.CTkLabel(self.sidebar_frame, text="Epic Collector", font=ctk.CTkFont(size=20, weight="bold"))
        self.logo_label.grid(row=0, column=0, padx=20, pady=(20, 10))

        # Navigation Buttons
        self.btn_dashboard = ctk.CTkButton(self.sidebar_frame, text="Dashboard", command=lambda: self._select_frame("dashboard"), fg_color="transparent", text_color=("gray10", "gray90"), hover_color=("gray70", "gray30"), anchor="w")
        self.btn_dashboard.grid(row=1, column=0, padx=20, pady=10, sticky="ew")

        self.btn_history = ctk.CTkButton(self.sidebar_frame, text="History", command=lambda: self._select_frame("history"), fg_color="transparent", text_color=("gray10", "gray90"), hover_color=("gray70", "gray30"), anchor="w")
        self.btn_history.grid(row=2, column=0, padx=20, pady=10, sticky="ew")

        self.btn_settings = ctk.CTkButton(self.sidebar_frame, text="Settings", command=lambda: self._select_frame("settings"), fg_color="transparent", text_color=("gray10", "gray90"), hover_color=("gray70", "gray30"), anchor="w")
        self.btn_settings.grid(row=3, column=0, padx=20, pady=10, sticky="ew")
        
        # Version Info
        self.version_label = ctk.CTkLabel(self.sidebar_frame, text="v2.4", font=ctk.CTkFont(size=10))
        self.version_label.grid(row=5, column=0, padx=20, pady=10)

    def _create_main_frames(self):
        """Initialize all content frames."""
        self.frames = {}
        
        # Dashboard
        self.frames["dashboard"] = DashboardFrame(self, self.claimer)
        self.frames["history"] = HistoryFrame(self)
        self.frames["settings"] = SettingsFrame(self, self.account_manager)
        
        for frame in self.frames.values():
            frame.grid(row=0, column=1, sticky="nsew")

    def _select_frame(self, name):
        """Switch visible interface."""
        # Update buttons
        self.btn_dashboard.configure(fg_color=("gray75", "gray25") if name == "dashboard" else "transparent")
        self.btn_history.configure(fg_color=("gray75", "gray25") if name == "history" else "transparent")
        self.btn_settings.configure(fg_color=("gray75", "gray25") if name == "settings" else "transparent")

        # Show frame
        frame = self.frames.get(name)
        if frame:
            # Refresh data if frame has a refresh method
            if hasattr(frame, "update_stats"):
                frame.update_stats()
            elif hasattr(frame, "load_data"):
                frame.load_data()
            elif hasattr(frame, "refresh_list"):
                frame.refresh_list()
                
            frame.lift()

        
        # Start Web Dashboard (if enabled)
        self.start_web_dashboard()

    def start_web_dashboard(self):
        if hasattr(self, 'web_dashboard') and self.web_dashboard:
            return

        from src.utils.config import ConfigManager
        config = ConfigManager()
        if config.get("web_dashboard_enabled", True):
            try:
                from src.web.server import WebDashboard
                port = config.get("web_port", 5000)
                
                # Pass self (App) as controller
                self.web_dashboard = WebDashboard(self)
                
                # Run in daemon thread
                t = threading.Thread(target=self.web_dashboard.run, args=(port,), daemon=True)
                t.start()
                print(f"🌐 Web Dashboard started at http://localhost:{port}")
            except Exception as e:
                print(f"❌ Failed to start Web Dashboard: {e}")

    def run(self):
        # Handle Close Event for Tray
        self.protocol("WM_DELETE_WINDOW", self.on_closing)
        self.mainloop()
        
    def create_tray_icon(self):
        """Create and run the system tray icon in a separate daemon thread."""
        if hasattr(self, 'tray') and self.tray:
            return # Already running
            
        from src.gui.tray import SystemTrayIcon
        
        def show_callback():
            self.after(0, self.deiconify)
            
        def exit_callback():
            self.after(0, self.quit_app)

        self.tray = SystemTrayIcon(self, show_callback, exit_callback)
        self.tray.setup()
        
        # Run pystray in a separate thread so it doesn't block tkinter
        threading.Thread(target=self.tray.run, daemon=True).start()

    def minimize_to_tray(self):
        """Standard method to hide window and ensure tray is active."""
        self.create_tray_icon()
        self.withdraw()
        
        # Optional: Notification
        from src.utils.config import ConfigManager
        if ConfigManager().get("minimize_to_tray", True):
             pass # Maybe a toast? "Minimized to tray"

    def quit_app(self):
        """Clean shutdown."""
        if hasattr(self, 'tray') and self.tray:
            self.tray.stop()
        self.quit()
        sys.exit(0)

    def on_closing(self):
        """Handle window close event."""
        from src.utils.config import ConfigManager
        config = ConfigManager()
        is_tray_enabled = config.get("minimize_to_tray", True)
        
        print(f"[GUI] Close Request. Tray Enabled in Config: {is_tray_enabled}")
        
        if is_tray_enabled:
            # Check if tray icon is actually valid/running?
            # Just try to minimize
            try:
                self.minimize_to_tray()
                print("[GUI] Window withdrawn to tray.")
            except Exception as e:
                print(f"❌ Tray minimize failed: {e}")
                self.quit_app()
        else:
            print("[GUI] Quitting app directly.")
            self.quit_app()

if __name__ == "__main__":
    app = GameClaimerApp()
    app.run()

