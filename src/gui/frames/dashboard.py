
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

        # Auto-Pilot Section (New)
        self.pilot_frame = ctk.CTkFrame(self, fg_color="transparent")
        self.pilot_frame.grid(row=2, column=0, padx=20, pady=(10, 0), sticky="ew")
        
        self.pilot_var = ctk.BooleanVar(value=False)
        self.switch_pilot = ctk.CTkSwitch(self.pilot_frame, text="Auto-Pilot Mode (Hide to Tray)", command=self.toggle_pilot, variable=self.pilot_var, font=ctk.CTkFont(weight="bold"))
        self.switch_pilot.pack(side="left")
        
        ctk.CTkLabel(self.pilot_frame, text="(Checks every 6 hours)", text_color="gray").pack(side="left", padx=10)

        # Controls Area
        self.controls_frame = ctk.CTkFrame(self)
        self.controls_frame.grid(row=3, column=0, padx=20, pady=10, sticky="ew")
        
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
            print("\n✈️ Auto-Pilot ENABLED. Hiding window and entering background loop...")
            self.master.withdraw() # Hide window
            threading.Thread(target=self._run_pilot_loop, daemon=True).start()
        else:
            # Disable
            print("\n✈️ Auto-Pilot DISABLED.")
            # Breaking the loop requires a flag or just letting it finish wait
            # Since we can't easily kill threads, we rely on the var check inside loop

    def _run_pilot_loop(self):
        """Background loop for Auto-Pilot."""
        import time
        asyncio.set_event_loop(self.loop)
        
        while self.pilot_var.get():
            try:
                print(f"\n[{datetime.now().strftime('%H:%M')}] ✈️ Pilot: Checking for free games...")
                
                # Check directly using connector (headless check basically)
                # But we can reuse the claimer logic
                
                # If we find games, we should probably unhide to show activity
                # Or just run silently. User requested: "uygulamayı açıp. otomatik olarak alması gerekiyor"
                # So we show it.
                
                self.after(0, self.master.deiconify)
                
                # Run the claim process
                self.loop.run_until_complete(self.claimer.claim_free_games_for_all_accounts())
                
                print("✈️ Pilot: Check complete. Sleeping for 6 hours...")
                
                # If user didn't disable it during run, hide again
                if self.pilot_var.get():
                     self.after(0, self.master.withdraw)
                     
                # Sleep in chunks to check for disable
                for _ in range(6 * 60): # 6 hours in minutes
                    if not self.pilot_var.get(): break
                    time.sleep(60) 
                    
            except Exception as e:
                print(f"✈️ Pilot Error: {e}")
                self.after(0, self.master.deiconify) # Show window on error
                time.sleep(60) # Wait a bit before retry

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
