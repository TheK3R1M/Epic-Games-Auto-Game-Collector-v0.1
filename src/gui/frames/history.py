
import customtkinter as ctk
import json
import os
from datetime import datetime
from src.utils.paths import get_data_dir

class HistoryFrame(ctk.CTkFrame):
    def __init__(self, master):
        super().__init__(master, corner_radius=0, fg_color="transparent")
        
        # Layout
        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(2, weight=1)

        # Header
        self.header = ctk.CTkLabel(self, text="Claim History", font=ctk.CTkFont(size=24, weight="bold"))
        self.header.grid(row=0, column=0, padx=20, pady=(20, 10), sticky="w")
        
        # Search Bar
        self.search_frame = ctk.CTkFrame(self, fg_color="transparent")
        self.search_frame.grid(row=1, column=0, padx=20, pady=(0, 10), sticky="ew")
        
        self.entry_search = ctk.CTkEntry(self.search_frame, placeholder_text="Search games or email...")
        self.entry_search.pack(side="left", fill="x", expand=True, padx=(0, 10))
        self.entry_search.bind("<KeyRelease>", lambda event: self.load_data())
        
        # Refresh Button
        self.btn_refresh = ctk.CTkButton(self.search_frame, text="Refresh", command=self.load_data, width=100)
        self.btn_refresh.pack(side="right")

        # Table Container (Scrollable)
        self.table_frame = ctk.CTkScrollableFrame(self, label_text="Recent Claims")
        self.table_frame.grid(row=2, column=0, padx=20, pady=(0, 20), sticky="nsew")
        self.table_frame.grid_columnconfigure(0, weight=1) # Game
        self.table_frame.grid_columnconfigure(1, weight=1) # Account
        self.table_frame.grid_columnconfigure(2, weight=1) # Date

        # Initial Load
        self.load_data()

    def load_data(self):
        # Clear existing
        for widget in self.table_frame.winfo_children():
            widget.destroy()

        # Headers
        ctk.CTkLabel(self.table_frame, text="Game Name", font=ctk.CTkFont(weight="bold")).grid(row=0, column=0, padx=10, pady=5, sticky="w")
        ctk.CTkLabel(self.table_frame, text="Account", font=ctk.CTkFont(weight="bold")).grid(row=0, column=1, padx=10, pady=5, sticky="w")
        ctk.CTkLabel(self.table_frame, text="Date", font=ctk.CTkFont(weight="bold")).grid(row=0, column=2, padx=10, pady=5, sticky="w")

        # Load from JSON
        data_dir = get_data_dir()
        history_path = os.path.join(data_dir, "claimed_history.json")
        search_query = self.entry_search.get().lower()
        
        if not os.path.exists(history_path):
            ctk.CTkLabel(self.table_frame, text="No history found.").grid(row=1, column=0, columnspan=3, pady=20)
            return

        try:
            with open(history_path, 'r', encoding='utf-8') as f:
                data = json.load(f)
            
            # Correct parsing: claims list
            claims_list = data.get("claims", [])
            
            rows = []
            for claim in claims_list:
                game_name = claim.get("game_name", "Unknown")
                email = claim.get("account_email", "Unknown")
                date = claim.get("claimed_at", "")
                
                # Filter
                if search_query in game_name.lower() or search_query in email.lower():
                    # Format date nicely if possible
                    try:
                        dt = datetime.fromisoformat(date.replace("Z", "+00:00"))
                        date_str = dt.strftime("%Y-%m-%d %H:%M")
                    except:
                        date_str = date
                        
                    rows.append((game_name, email, date_str))
            
            # Sort by date desc
            rows.sort(key=lambda x: x[2], reverse=True)

            for i, (game, email, date) in enumerate(rows, start=1):
                bg_color = "transparent" if i % 2 == 0 else ("gray85", "gray15") # Simple striping if frame supported it, but labels are clear
                
                ctk.CTkLabel(self.table_frame, text=game.title()).grid(row=i, column=0, padx=10, pady=2, sticky="w")
                ctk.CTkLabel(self.table_frame, text=email).grid(row=i, column=1, padx=10, pady=2, sticky="w")
                ctk.CTkLabel(self.table_frame, text=date).grid(row=i, column=2, padx=10, pady=2, sticky="w")

        except Exception as e:
            ctk.CTkLabel(self.table_frame, text=f"Error loading: {e}").grid(row=1, column=0, columnspan=3)
