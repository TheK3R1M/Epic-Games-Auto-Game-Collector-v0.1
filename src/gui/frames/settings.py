
import customtkinter as ctk
from tkinter import simpledialog, messagebox, filedialog
import sys
import os
import threading
from src.core.epic_drission_connector import EpicDrissionConnector
from src.utils.startup import register_startup_task, unregister_startup_task
from src.utils.config import ConfigManager
from src.utils.paths import get_data_dir

class SettingsFrame(ctk.CTkFrame):
    def __init__(self, master, account_manager):
        super().__init__(master, corner_radius=0, fg_color="transparent")
        self.account_manager = account_manager
        self.config_manager = ConfigManager()
        
        # Main Layout: 2 Columns. Left: Accounts, Right: Preferences.
        # OR: Scrollable vertical list. Given the number of settings, vertical scroll is safer.
        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(0, weight=1)
        
        self.scroll_container = ctk.CTkScrollableFrame(self, label_text="Settings & Accounts")
        self.scroll_container.grid(row=0, column=0, sticky="nsew", padx=10, pady=10)
        self.scroll_container.grid_columnconfigure(0, weight=1)
        
        # --- Section 1: Application Behavior ---
        self._create_section_header("Application Behavior", row=0)
        self.behavior_frame = ctk.CTkFrame(self.scroll_container, fg_color="transparent")
        self.behavior_frame.grid(row=1, column=0, padx=10, pady=(0, 20), sticky="ew")
        
        # Startup
        self.startup_var = ctk.BooleanVar(value=self.config_manager.get("run_on_startup", False))
        self._create_switch(self.behavior_frame, "Run on Startup", 
                            "Automatically start the claimer when you log in to Windows", 
                            self.startup_var, self.toggle_startup).pack(fill="x", pady=5)

        # Minimize to Tray
        self.tray_var = ctk.BooleanVar(value=self.config_manager.get("minimize_to_tray", True))
        self._create_switch(self.behavior_frame, "Minimize to Tray",
                            "Keep the application running in the background when window is closed",
                            self.tray_var, lambda: self.update_config("minimize_to_tray", self.tray_var.get())).pack(fill="x", pady=5)

        # Notifications
        self.notify_var = ctk.BooleanVar(value=self.config_manager.get("notifications", True))
        self._create_switch(self.behavior_frame, "Desktop Notifications",
                            "Show system notifications when a new game is successfully claimed",
                            self.notify_var, lambda: self.update_config("notifications", self.notify_var.get())).pack(fill="x", pady=5)

        # --- Section 2: Advanced ---
        self._create_section_header("Advanced", row=2)
        self.advanced_frame = ctk.CTkFrame(self.scroll_container, fg_color="transparent")
        self.advanced_frame.grid(row=3, column=0, padx=10, pady=(0, 20), sticky="ew")
        
        # Auto Update
        self.update_var = ctk.BooleanVar(value=self.config_manager.get("auto_update", False))
        self._create_switch(self.advanced_frame, "Automatic Updates",
                            "Download and install updates automatically",
                            self.update_var, lambda: self.update_config("auto_update", self.update_var.get())).pack(fill="x", pady=5)
        
        # --- Section 3: Data Location (Custom Path) ---
        self._create_section_header("Data Location", row=4)
        self.data_frame = ctk.CTkFrame(self.scroll_container)
        self.data_frame.grid(row=5, column=0, padx=10, pady=(0, 20), sticky="ew")
        
        current_path = get_data_dir()
        self.lbl_path = ctk.CTkLabel(self.data_frame, text=current_path, font=ctk.CTkFont(size=12), text_color="gray", wraplength=400)
        self.lbl_path.pack(side="left", padx=10, pady=10, fill="x", expand=True)
        
        self.btn_browse = ctk.CTkButton(self.data_frame, text="Browse", width=80, command=self.browse_data_path)
        self.btn_browse.pack(side="right", padx=10, pady=10)

        # --- Section 4: Accounts (Existing Logic) ---
        self._create_section_header("Registered Accounts", row=6)
        
        # Account Actions
        self.acc_actions = ctk.CTkFrame(self.scroll_container, fg_color="transparent")
        self.acc_actions.grid(row=7, column=0, padx=10, pady=5, sticky="ew")
        
        self.btn_add = ctk.CTkButton(self.acc_actions, text="+ Add Account", command=self.add_account, height=30)
        self.btn_add.pack(side="left", padx=(0, 10))
        
        self.btn_remove = ctk.CTkButton(self.acc_actions, text="Delete Selected", command=self.remove_account, height=30, fg_color="#C0392B", hover_color="#E74C3C")
        self.btn_remove.pack(side="left", padx=(0, 10))

        # Account List Frame within Scroll Container
        self.list_frame = ctk.CTkFrame(self.scroll_container)
        self.list_frame.grid(row=8, column=0, padx=10, pady=5, sticky="ew")
        self.check_vars = {}
        self.refresh_list()

        # --- Reset Danger Zone ---
        self.reset_frame = ctk.CTkFrame(self.scroll_container, fg_color="#2b1111", border_color="#C0392B", border_width=1)
        self.reset_frame.grid(row=9, column=0, padx=10, pady=(30, 20), sticky="ew")
        
        ctk.CTkLabel(self.reset_frame, text="Reset Configuration", text_color="#E74C3C", font=ctk.CTkFont(weight="bold")).pack(side="left", padx=15, pady=15)
        ctk.CTkLabel(self.reset_frame, text="Restore all settings to their default values.", text_color="gray").pack(side="left", padx=0, pady=15)
        
        ctk.CTkButton(self.reset_frame, text="Reset Defaults", command=self.reset_defaults, fg_color="transparent", border_color="#5c2b2b", border_width=1, hover_color="#3e1a1a").pack(side="right", padx=15, pady=15)

    def _create_section_header(self, text, row):
        container = ctk.CTkFrame(self.scroll_container, fg_color="transparent")
        container.grid(row=row, column=0, sticky="w", padx=5, pady=(10, 5))
        ctk.CTkLabel(container, text=text, font=ctk.CTkFont(size=16, weight="bold")).pack(anchor="w")

    def _create_switch(self, parent, title, desc, variable, command):
        frame = ctk.CTkFrame(parent, fg_color="transparent") # or slight contrast
        
        # Text Col
        txt_frame = ctk.CTkFrame(frame, fg_color="transparent")
        txt_frame.pack(side="left", padx=10, pady=5)
        
        ctk.CTkLabel(txt_frame, text=title, font=ctk.CTkFont(weight="bold")).pack(anchor="w")
        ctk.CTkLabel(txt_frame, text=desc, font=ctk.CTkFont(size=11), text_color="gray").pack(anchor="w")
        
        # Switch Col
        ctk.CTkSwitch(frame, text="", variable=variable, command=command, onvalue=True, offvalue=False).pack(side="right", padx=10)
        
        return frame

    def update_config(self, key, value):
        self.config_manager.set(key, value)
        print(f"⚙️ Setting updated: {key} = {value}")

    def browse_data_path(self):
        new_path = filedialog.askdirectory(title="Select Data Location")
        if new_path:
            # Confirm
            if messagebox.askyesno("Confirm Change", f"Change data location to:\n{new_path}\n\nThe application will require a restart. Existing data will NOT be moved automatically."):
                self.config_manager.set("custom_data_path", new_path)
                self.lbl_path.configure(text=new_path)
                messagebox.showinfo("Restart Required", "Please restart the application for changes to take effect.")

    def reset_defaults(self):
        if messagebox.askyesno("Reset Configuration", "Are you sure you want to reset all settings?"):
            self.config_manager.reset()
            # Reload vars
            self.tray_var.set(self.config_manager.get("minimize_to_tray"))
            self.notify_var.set(self.config_manager.get("notifications"))
            self.update_var.set(self.config_manager.get("auto_update"))
            self.lbl_path.configure(text=get_data_dir()) # Resets to default priority
            print("⚙️ Configuration reset to defaults.")

    def refresh_list(self):
        # Clear UI
        for widget in self.list_frame.winfo_children():
            widget.destroy()
            
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
            
            # Check expiry
            days_left = self.account_manager.check_cookie_expiry(email)
            expiry_text = ""
            if days_left != -1 and days_left < 3:
                expiry_text = f" (⚠️ Expires in {days_left} days)"
                
            cb = ctk.CTkCheckBox(row, text=f"{email}{expiry_text}", variable=var, onvalue=1, offvalue=0)
            if expiry_text:
                cb.configure(text_color="orange")
            cb.pack(side="left", padx=10, pady=5)
            
            # Active Switch
            is_active = (status == "active")
            switch_var = ctk.BooleanVar(value=is_active)
            
            def on_toggle(e=email, v=switch_var):
                self.account_manager.toggle_account_status(e, v.get())
                
            switch = ctk.CTkSwitch(row, text="Active", command=on_toggle, variable=switch_var, width=60)
            switch.pack(side="right", padx=10)

    # ... Include helper methods like add_account, remove_account, toggle_startup as before ...
    # (Re-implementing strictly necessary methods to minimize file size issues or lost context)
    
    def add_account(self):
        self.btn_add.configure(state="disabled", text="Opening Browser...")
        threading.Thread(target=self._run_browser_login, daemon=True).start()

    def _run_browser_login(self):
        try:
            connector = EpicDrissionConnector()
            if connector.initialize():
                email = connector.login_new_account()
                connector.close()
                if email:
                    if email == "UNKNOWN_USER":
                        self.after(0, lambda: self._prompt_email_after_login())
                    else:
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
        dialog = ctk.CTkInputDialog(text="Enter email:", title="Confirm Email")
        email = dialog.get_input()
        if email:
            self.account_manager.add_account(email, "", status="active")
            self.account_manager.cookie_manager.move_cookies("UNKNOWN_USER", email)
            self.refresh_list()

    def _finalize_add_account(self, email):
        self._reset_add_button()
        self.account_manager.add_account(email, "", status="active")
        self.refresh_list()
        
    def _reset_add_button(self):
        self.btn_add.configure(state="normal", text="+ Add Account")

    def remove_account(self):
        selected = [k for k,v in self.check_vars.items() if v.get() == 1]
        for e in selected:
            self.account_manager.remove_account(e)
        self.refresh_list()

    def toggle_startup(self):
        self.update_config("run_on_startup", self.startup_var.get())
        # Logic to actually register task
        exe_path = sys.executable
        if self.startup_var.get():
            args = "-m src.main --auto"
            ok, msg = register_startup_task("EpicAutoCollector", exe_path, args)
            print(f"[GUI] Startup Register: {msg}")
        else:
            ok, msg = unregister_startup_task("EpicAutoCollector")
            print(f"[GUI] Startup Unregister: {msg}")
