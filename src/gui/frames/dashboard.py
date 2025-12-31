
import customtkinter as ctk
import sys
import threading
import asyncio
from datetime import datetime

class TextRedirector(object):
    def __init__(self, widget, tag="stdout"):
        self.widget = widget
        self.tag = tag

    def write(self, str):
        self.widget.configure(state="normal")
        self.widget.insert("end", str)
        self.widget.see("end")
        self.widget.configure(state="disabled")
    
    def flush(self):
        pass

class DashboardFrame(ctk.CTkFrame):
    def __init__(self, master, claimer):
        super().__init__(master, corner_radius=0, fg_color="transparent")
        self.claimer = claimer
        self.is_running = False
        self.loop = asyncio.new_event_loop()
        
        # Grid Layout
        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(2, weight=1) # Log area expands

        # Header
        self.header = ctk.CTkLabel(self, text="Dashboard", font=ctk.CTkFont(size=24, weight="bold"))
        self.header.grid(row=0, column=0, padx=20, pady=(20, 10), sticky="w")

        # Stats Area
        self.stats_frame = ctk.CTkFrame(self, fg_color="transparent")
        self.stats_frame.grid(row=1, column=0, padx=20, pady=(0, 20), sticky="ew")
        self.stats_frame.grid_columnconfigure(0, weight=1)
        self.stats_frame.grid_columnconfigure(1, weight=1)

        # Card 1: Total Claims
        self.card_claims = ctk.CTkFrame(self.stats_frame)
        self.card_claims.grid(row=0, column=0, padx=(0, 10), sticky="ew")
        
        self.lbl_claims_title = ctk.CTkLabel(self.card_claims, text="Total Games Claimed", font=ctk.CTkFont(size=12, weight="bold")) # Bold title
        self.lbl_claims_title.pack(pady=(10, 0))
        
        self.lbl_claims_val = ctk.CTkLabel(self.card_claims, text="0", font=ctk.CTkFont(size=30, weight="bold"), text_color="#3498DB") # Consistent Blue
        self.lbl_claims_val.pack(pady=(0, 10))

        # Card 2: Active Accounts
        self.card_accounts = ctk.CTkFrame(self.stats_frame)
        self.card_accounts.grid(row=0, column=1, padx=(10, 0), sticky="ew")

        self.lbl_acc_title = ctk.CTkLabel(self.card_accounts, text="Active Accounts", font=ctk.CTkFont(size=12, weight="bold")) # Bold title
        self.lbl_acc_title.pack(pady=(10, 0))
        
        self.lbl_acc_val = ctk.CTkLabel(self.card_accounts, text="0", font=ctk.CTkFont(size=30, weight="bold"), text_color="#2ECC71") # Consistent Green
        self.lbl_acc_val.pack(pady=(0, 10))

        # Update stats initially
        self.update_stats()

        # Timer Info UI
        self.timer_frame = ctk.CTkFrame(self, fg_color="transparent")
        self.timer_frame.grid(row=2, column=0, padx=20, pady=(0, 10), sticky="ew")
        
        self.lbl_next_unlock = ctk.CTkLabel(self.timer_frame, text="Next Unlock: Calculating...", text_color="gray")
        self.lbl_next_unlock.pack(side="left")
        
        # self.lbl_current_ends = ctk.CTkLabel(self.timer_frame, text="Ends: ...", text_color="gray")
        # self.lbl_current_ends.pack(side="right")

        # Auto-Pilot Section (New)
        self.pilot_frame = ctk.CTkFrame(self, fg_color="transparent")
        self.pilot_frame.grid(row=3, column=0, padx=20, pady=(10, 0), sticky="ew")
        
        self.pilot_var = ctk.BooleanVar(value=False)
        self.switch_pilot = ctk.CTkSwitch(self.pilot_frame, text="Auto-Pilot Mode (Hide to Tray)", command=self.toggle_pilot, variable=self.pilot_var, font=ctk.CTkFont(weight="bold"))
        self.switch_pilot.pack(side="left")
        
        ctk.CTkLabel(self.pilot_frame, text="(Checks every 6 hours)", text_color="gray").pack(side="left", padx=10)

        # Controls Area
        self.controls_frame = ctk.CTkFrame(self)
        self.controls_frame.grid(row=4, column=0, padx=20, pady=10, sticky="ew")
        
        self.btn_start = ctk.CTkButton(self.controls_frame, text="Start Claiming", command=self.toggle_claim, height=40, font=ctk.CTkFont(size=14, weight="bold"))
        self.btn_start.pack(side="left", padx=20, pady=20)
        
        # Center status vertically relative to button
        self.status_label = ctk.CTkLabel(self.controls_frame, text="Status: Idle", text_color="gray", font=ctk.CTkFont(size=14))
        self.status_label.pack(side="left", padx=10, anchor="center")

        # Console Log
        self.log_label = ctk.CTkLabel(self, text="Activity Log:", font=ctk.CTkFont(size=14, weight="bold"))
        # Console Log
        self.log_label = ctk.CTkLabel(self, text="Activity Log:", font=ctk.CTkFont(size=14, weight="bold"))
        self.log_label.grid(row=4, column=0, padx=20, pady=(10, 0), sticky="w")

        self.console = ctk.CTkTextbox(self, font=ctk.CTkFont(family="Consolas", size=12))
        self.console.grid(row=5, column=0, padx=20, pady=(5, 20), sticky="nsew")
        self.console.configure(state="disabled")

        # Redirect stdout and stderr
        sys.stdout = TextRedirector(self.console, "stdout")
        sys.stderr = TextRedirector(self.console, "stderr")

    def toggle_claim(self):
        if not self.is_running:
            self.start_claiming()
        else:
            self.stop_claiming()

    def start_claiming(self):
        self.is_running = True
        self.btn_start.configure(text="Stop", fg_color="red", hover_color="darkred")
        self.status_label.configure(text="Status: Running...", text_color="green")
        
        # Run in thread
        threading.Thread(target=self._run_async_process, daemon=True).start()

    def stop_claiming(self):
        # Graceful stop not fully implemented in CLI backend yet, but we can force state
        self.is_running = False
        self.btn_start.configure(text="Start Claiming", fg_color=['#3B8ED0', '#1F6AA5'], hover_color=['#36719F', '#144870']) # Default blue
        self.status_label.configure(text="Status: Stopping...", text_color="orange")
        print("\n[GUI] Stopping safely (wait for current task)...")
        # In a real app we would cancel the asyncio task here

    def toggle_pilot(self):
        """Handle Auto-Pilot toggle."""
        if self.pilot_var.get():
            # Enable Auto-Pilot
            print("\n✈️ Auto-Pilot ENABLED. Hiding window to System Tray...")
            
            # Initialize Tray
            from src.gui.tray import SystemTrayIcon
            
            def show_callback():
                # Called when user clicks "Show" in tray
                self.master.deiconify()
                # We don't disable pilot var automatically, app just shows up
                # But tray icon should disappear? 
                # Our tray logic stops itself on show.
                
            def exit_callback():
                # Kill app
                self.master.quit()
                sys.exit(0)

            self.tray = SystemTrayIcon(self.master, show_callback, exit_callback)
            self.tray.setup()
            self.tray.run()
            
            self.master.withdraw() # Hide window
            threading.Thread(target=self._run_pilot_loop, daemon=True).start()
        else:
            # Disable
            print("\n✈️ Auto-Pilot DISABLED.")
            # If the user toggles it OFF while window is open, ensure tray is gone (it should be)
            try:
                if hasattr(self, 'tray') and self.tray:
                    self.tray.stop()
            except: pass

    def _run_pilot_loop(self):
        """Background loop for Auto-Pilot (Smart Mode)."""
        import time
        from datetime import datetime, timedelta
        asyncio.set_event_loop(self.loop)
        
        while self.pilot_var.get():
            try:
                print(f"\n[{datetime.now().strftime('%H:%M')}] ✈️ Pilot: Checking...")
                
                # Run the claim process
                results = self.loop.run_until_complete(self.claimer.claim_free_games_for_all_accounts())
                
                # --- SMART PILOT LOGIC ---
                # Find next unlock time from results
                next_unlock_iso = None
                claimed_names = []
                
                try:
                    for res in results:
                        # Collect claimed names for notification
                        if res.get("claimed_games"):
                            claimed_names.extend(res["claimed_games"])
                            
                        # Look for timer
                        if res.get("free_games"):
                            for g in res["free_games"]:
                                if g.get("next_unlock"):
                                    next_unlock_iso = g["next_unlock"]
                                    break
                        if next_unlock_iso: break
                except Exception: pass

                # Notification
                if claimed_names and hasattr(self, 'tray') and self.tray and self.tray.icon:
                    distinct_games = list(set(claimed_names))
                    msg = f"Successfully claimed: {', '.join(distinct_games)}"
                    try:
                        self.tray.icon.notify(msg, "Epic Games Collected! 🎁")
                    except: pass
                
                # Calculate sleep time
                sleep_seconds = 6 * 3600 # Default 6 hours
                if next_unlock_iso:
                    try:
                        unlock_dt = datetime.fromisoformat(next_unlock_iso)
                        now = datetime.now()
                        diff = (unlock_dt - now).total_seconds()
                        
                        if diff > 0:
                            # Sleep until unlock + 5 minutes buffer
                            sleep_seconds = int(diff) + 300 
                            print(f"⏰ Smart Pilot: Next game unlocks in {int(diff/3600)}h {int((diff%3600)/60)}m. Sleeping until then.")
                            
                            # UI Update (Thread-safe invoke)
                            self.after(0, lambda: self.lbl_next_unlock.configure(text=f"Next Unlock: {unlock_dt.strftime('%Y-%m-%d %H:%M')}", text_color="#3498DB"))
                        else:
                            print("⚠️ Timer says unlock passed, but maybe cached. Sleeping 1h default.")
                            sleep_seconds = 3600
                    except Exception as e:
                        print(f"⚠️ Timer parse error: {e}")
                
                print(f"✈️ Pilot: Sleeping for {int(sleep_seconds/60)} minutes...")
                
                # Sleep in chunks to check for disable
                chunk_size = 60
                steps = int(sleep_seconds / chunk_size)
                for _ in range(steps): 
                    if not self.pilot_var.get(): break
                    time.sleep(chunk_size) 
                    
            except Exception as e:
                print(f"✈️ Pilot Error: {e}")
                time.sleep(60)

    def _run_async_process(self):
        asyncio.set_event_loop(self.loop)
        try:
            self.loop.run_until_complete(self.claimer.claim_free_games_for_all_accounts())
        except Exception as e:
            print(f"\n[Error] {e}")
        finally:
            self.is_running = False
            # Update UI from main thread if possible, or just via callback
            # Since CustomTkinter isn't perfectly thread-safe, direct config usually works but explicit after() is better.
            # For simplicity in this demo, direct config might work or we rely on user clicking Stop.
            print("\n[GUI] Process Finished.")
            
            # If pilot mode was enabled and we just finished manual run, do NOT hide.
            # Only hide if we are in pilot loop.
            
            # Reset UI
            self.after(0, self._reset_ui)

    def update_stats(self):
        """Refreshes the stats cards."""
        try:
            # Claims
            claims = self.claimer.history.list_claims()
            self.lbl_claims_val.configure(text=str(len(claims)))
            
            # Accounts
            accounts = self.claimer.account_manager.get_all_accounts()
            self.lbl_acc_val.configure(text=str(len(accounts)))
        except Exception:
            pass

    def _reset_ui(self):
        self.btn_start.configure(text="Start Claiming", fg_color=['#3B8ED0', '#1F6AA5'], hover_color=['#36719F', '#144870'])
        self.status_label.configure(text="Status: Idle", text_color="gray")
        self.update_stats() # Refresh stats after run
