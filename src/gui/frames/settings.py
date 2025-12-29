
import customtkinter as ctk
from tkinter import simpledialog, messagebox
import sys
import threading
from src.core.epic_drission_connector import EpicDrissionConnector
from src.utils.startup import register_startup_task, unregister_startup_task

class SettingsFrame(ctk.CTkFrame):
    def __init__(self, master, account_manager):
        super().__init__(master, corner_radius=0, fg_color="transparent")
        self.account_manager = account_manager
        
        # Grid
        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(2, weight=1)

        # Header
        self.header = ctk.CTkLabel(self, text="Settings", font=ctk.CTkFont(size=24, weight="bold"))
        self.header.grid(row=0, column=0, padx=20, pady=(20, 10), sticky="w")

        # Actions
        self.actions_frame = ctk.CTkFrame(self, fg_color="transparent")
        self.actions_frame.grid(row=1, column=0, padx=20, pady=10, sticky="ew")
        
        # Use consistent height and styling
        btn_height = 36
        self.btn_add = ctk.CTkButton(self.actions_frame, text="+ Add Account", command=self.add_account, height=btn_height)
        self.btn_add.pack(side="left", padx=(0, 10))
        
        self.btn_select_all = ctk.CTkButton(self.actions_frame, text="Select All", command=self.toggle_select_all, height=btn_height, fg_color="gray", hover_color="gray30")
        self.btn_select_all.pack(side="left", padx=(0, 10))
        
        self.btn_remove = ctk.CTkButton(self.actions_frame, text="Delete Selected", command=self.remove_account, height=btn_height, fg_color="#C0392B", hover_color="#E74C3C")
        self.btn_remove.pack(side="left", padx=(0, 10))

        # App Behavior Section
        self.behavior_frame = ctk.CTkFrame(self, fg_color="transparent")
        self.behavior_frame.grid(row=2, column=0, padx=20, pady=(10, 20), sticky="ew")
        
        self.lbl_behavior = ctk.CTkLabel(self.behavior_frame, text="Preferences", font=ctk.CTkFont(size=18, weight="bold"))
        self.lbl_behavior.pack(anchor="w", pady=(0, 10))
        
        # Run on Startup Toggle
        self.startup_var = ctk.BooleanVar(value=False)
        self.switch_startup = ctk.CTkSwitch(self.behavior_frame, text="Run on Startup", command=self.toggle_startup, variable=self.startup_var)
        self.switch_startup.pack(anchor="w", padx=10)
        
        # Account List
        self.list_frame = ctk.CTkScrollableFrame(self, label_text="Registered Accounts")
        self.list_frame.grid(row=3, column=0, padx=20, pady=10, sticky="nsew")
        
        # Variables
        # Mapping: email -> IntVar (1=selected, 0=not)
        self.check_vars = {}
        
        self.refresh_list()

    def refresh_list(self):
        # Clear UI
        for widget in self.list_frame.winfo_children():
            widget.destroy()
            
        # Re-init vars
        self.check_vars = {}
            
        accounts = self.account_manager.get_all_accounts()
        if not accounts:
            ctk.CTkLabel(self.list_frame, text="No accounts added.").pack(pady=20)
            return

        for acc in accounts:
            email = acc.get('email', 'Unknown')
            status = acc.get('status', 'Unknown')
            
            row = ctk.CTkFrame(self.list_frame)
            row.pack(fill="x", pady=2, padx=5)
            
            var = ctk.IntVar(value=0)
            self.check_vars[email] = var
            
            # Use CheckBox for multi-select
            cb = ctk.CTkCheckBox(row, text=f"{email} ({status})", variable=var, onvalue=1, offvalue=0)
            cb.pack(side="left", padx=10, pady=5)

    def toggle_select_all(self):
        """Toggle all checkboxes."""
        # Check if any are currently unselected -> Select All
        # If all selected -> Deselect All
        all_selected = all(v.get() == 1 for v in self.check_vars.values())
        
        new_val = 0 if all_selected else 1
        for var in self.check_vars.values():
            var.set(new_val)
            
        # Update button text
        self.btn_select_all.configure(text="Deselect All" if new_val == 1 else "Select All")

    def add_account(self):
        """Start the interactive browser login flow."""
        # Disable button to prevent double clicks
        self.btn_add.configure(state="disabled", text="Browser Opening...")
        
        # Run in thread to keep GUI responsive
        threading.Thread(target=self._run_browser_login, daemon=True).start()

    def _run_browser_login(self):
        try:
            connector = EpicDrissionConnector()
            if connector.initialize():
                # Bring window to front usually happens by OS, but we can't force it easily from here
                # just hope user sees it.
                
                email = connector.login_new_account()
                connector.close()
                
                if email:
                    if email == "UNKNOWN_USER":
                        # Login successful but email not scraped
                        # Ask user for email
                        self.after(0, lambda: self._prompt_email_after_login())
                    else:
                        # Success
                        self.after(0, lambda: self._finalize_add_account(email))
                else:
                    self.after(0, self._reset_add_button)
            else:
                 self.after(0, self._reset_add_button)
        except Exception as e:
            print(f"Error in browser login: {e}")
            self.after(0, self._reset_add_button)

    def _prompt_email_after_login(self):
        self._reset_add_button()
        
        # Ask user for the email they just used
        dialog = ctk.CTkInputDialog(text="Login detected, but email could not be read.\nPlease enter the email you just logged in with:", title="Confirm Email")
        email = dialog.get_input()
        
        if email:
            # We need to rename the cookies from 'UNKNOWN_USER' to this email
            # We need access to cookie manager for this.
            # AccountManager has it.
            
            # First adding the account will init the entry
            self.account_manager.add_account(email, "", status="active")
            
            # Now move cookies
            # Note: EpicDrissionConnector saved it as "UNKNOWN_USER"
            if self.account_manager.cookie_manager.move_cookies("UNKNOWN_USER", email):
                print(f"✅ Cookies assigned to {email}")
            else:
                print("❌ Failed to move cookies.")
                
            self.refresh_list()

    def _finalize_add_account(self, email):
        self._reset_add_button()
        self.account_manager.add_account(email, "", status="active")
        self.refresh_list()
        
    def _reset_add_button(self):
        self.btn_add.configure(state="normal", text="+ Add Account")

    def remove_account(self):
        # Identify selected
        selected_emails = [email for email, var in self.check_vars.items() if var.get() == 1]
        
        if not selected_emails:
            return
            
        # Confirm action (optional but good for UX, though user wants speed so maybe skip?)
        # User said "hesapları siliyim dedim... yapamadım", implies they want it to WORK.
        # Let's just do it.
        
        # Remove all selected
        for email in selected_emails:
            self.account_manager.remove_account(email)
        
        self.refresh_list()
        # Reset Select All button text
        self.btn_select_all.configure(text="Select All")

    def toggle_startup(self):
        """Handle startup toggle."""
        state = self.startup_var.get()
        exe_path = sys.executable
        if state:
            # Pass components separately: name, exe, args
            args = "-m src.main --auto"
            ok, msg = register_startup_task("EpicAutoCollector", exe_path, args)
            if ok:
                print(f"[GUI] Startup task registered: {msg}")
            else:
                print(f"[GUI] Failed to register task: {msg}")
                self.startup_var.set(False) # Revert
        else:
            ok, msg = unregister_startup_task("EpicAutoCollector")
            if ok:
                print(f"[GUI] Startup task removed: {msg}")
            else:
                print(f"[GUI] Failed to remove task: {msg}")
