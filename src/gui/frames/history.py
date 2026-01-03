
import customtkinter as ctk
import json
import os
import requests
from io import BytesIO
from PIL import Image, ImageTk
from datetime import datetime
from src.utils.paths import get_data_dir
from src.utils.claimed_history import ClaimedHistory

# --- Helper: Async Image Loading ---
# We can't do full async in Tkinter main thread easily without freezing.
# We will use a simple caching approach or placeholders.
# For a polished app, we would use a thread pool to fetch images, then update UI labels.

class ImageCache:
    _cache = {}

    @classmethod
    def get_image(cls, url: str, size=(40, 50)):
        if not url: return None
        if url in cls._cache:
            return cls._cache[url]
        
        try:
            response = requests.get(url, timeout=3)
            if response.status_code == 200:
                img_data = BytesIO(response.content)
                pil_img = Image.open(img_data)
                pil_img = pil_img.resize(size, Image.Resampling.LANCZOS)
                tk_img = ctk.CTkImage(light_image=pil_img, dark_image=pil_img, size=size)
                cls._cache[url] = tk_img
                return tk_img
        except:
            return None
        return None

class HistoryFrame(ctk.CTkFrame):
    def __init__(self, master):
        super().__init__(master, corner_radius=0, fg_color="transparent")
        
        self.history_manager = ClaimedHistory()
        
        # Grid Layout
        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(2, weight=1) # Table expands

        # 1. Header & Stats Section
        self._create_stats_header()
        
        # 2. Filters & Toolbar
        self._create_toolbar()

        # 3. Table Area
        self._create_table_area()

        # Initial Load
        self._load_data()

    def _create_stats_header(self):
        """Top cards showing Total Games, Value Saved."""
        self.header_frame = ctk.CTkFrame(self, fg_color="transparent")
        self.header_frame.grid(row=0, column=0, padx=20, pady=(20, 10), sticky="ew")
        
        # Title
        ctk.CTkLabel(self.header_frame, text="Claim History", font=ctk.CTkFont(size=24, weight="bold")).pack(side="left")
        
        # Right Side Stats Cards
        self.stats_container = ctk.CTkFrame(self.header_frame, fg_color="transparent")
        self.stats_container.pack(side="right")
        
        # Card 1: Games Claimed
        self.card_total = self._create_stat_card(self.stats_container, "GAMES CLAIMED", "0", "#3B8ED0") # Blue
        self.card_total.pack(side="left", padx=10)
        
        # Card 2: Value Saved
        self.card_value = self._create_stat_card(self.stats_container, "VALUE SAVED", "$0.00", "#2ECC71") # Green
        self.card_value.pack(side="left", padx=10)

    def _create_stat_card(self, parent, title, value, color):
        frame = ctk.CTkFrame(parent, fg_color=("gray80", "gray17"), corner_radius=8)
        
        inner = ctk.CTkFrame(frame, fg_color="transparent")
        inner.pack(padx=15, pady=10)
        
        ctk.CTkLabel(inner, text=title, font=ctk.CTkFont(size=10, weight="bold"), text_color="gray").pack(anchor="w")
        lbl_val = ctk.CTkLabel(inner, text=value, font=ctk.CTkFont(size=20, weight="bold"), text_color=color)
        lbl_val.pack(anchor="w")
        
        return frame

    def _update_stat_card(self, frame_widget, new_value):
        # Helper to find the label and update text
        # frame -> inner -> label 2
        try:
            inner = frame_widget.winfo_children()[0]
            lbl = inner.winfo_children()[1]
            lbl.configure(text=new_value)
        except: pass

    def _create_toolbar(self):
        self.toolbar = ctk.CTkFrame(self, fg_color="transparent", height=50)
        self.toolbar.grid(row=1, column=0, padx=20, pady=(0, 10), sticky="ew")
        
        # Search
        self.entry_search = ctk.CTkEntry(self.toolbar, placeholder_text="Search by game title...", width=300)
        self.entry_search.pack(side="left", padx=(0, 10))
        self.entry_search.bind("<Return>", lambda e: self._load_data())
        
        # Status Filter
        self.filter_status = ctk.CTkOptionMenu(
            self.toolbar, 
            values=["Status: All", "Status: Success", "Status: Failed"],
            command=lambda x: self._load_data(),
            width=140
        )
        self.filter_status.pack(side="left", padx=10)
        
        # Date Filter (Mockup for now)
        self.filter_date = ctk.CTkOptionMenu(
            self.toolbar,
            values=["Date: All Time", "Date: Last 30 Days", "Date: Today"],
            command=lambda x: self._load_data(),
            width=150
        )
        self.filter_date.pack(side="left", padx=10)
        
        # Refresh
        ctk.CTkButton(self.toolbar, text="Refresh", command=self._load_data, width=80).pack(side="right")

    def _create_table_area(self):
        # Info Header Row (Not scrollable)
        self.headers_frame = ctk.CTkFrame(self, fg_color=("gray85", "gray17"), height=40, corner_radius=6)
        self.headers_frame.grid(row=2, column=0, padx=20, pady=(0, 0), sticky="new") # Sticky top of row 2
        
        # Columns: Img(50) | Title(expand) | Date(150) | Status(100) | Price(100)
        self.headers_frame.grid_columnconfigure(1, weight=1)
        
        h_font = ctk.CTkFont(size=11, weight="bold")
        ctk.CTkLabel(self.headers_frame, text="GAME TITLE", font=h_font, text_color="gray").grid(row=0, column=1, padx=10, pady=10, sticky="w")
        ctk.CTkLabel(self.headers_frame, text="DATE CLAIMED", font=h_font, text_color="gray").grid(row=0, column=2, padx=10, pady=10, sticky="w")
        ctk.CTkLabel(self.headers_frame, text="STATUS", font=h_font, text_color="gray").grid(row=0, column=3, padx=10, pady=10, sticky="w")
        ctk.CTkLabel(self.headers_frame, text="PRICE", font=h_font, text_color="gray").grid(row=0, column=4, padx=10, pady=10, sticky="ew")

        # Config fixed widths for cols 2,3,4 to match rows
        self.headers_frame.grid_columnconfigure(2, minsize=150)
        self.headers_frame.grid_columnconfigure(3, minsize=100)
        self.headers_frame.grid_columnconfigure(4, minsize=100)

        # Content (Scrollable)
        self.scroll_frame = ctk.CTkScrollableFrame(self, fg_color="transparent")
        self.scroll_frame.grid(row=3, column=0, padx=20, pady=(5, 20), sticky="nsew")
        
        self.scroll_frame.grid_columnconfigure(1, weight=1)
        self.scroll_frame.grid_columnconfigure(2, minsize=150)
        self.scroll_frame.grid_columnconfigure(3, minsize=100)
        self.scroll_frame.grid_columnconfigure(4, minsize=100)
        
        # Make row 3 expand
        self.grid_rowconfigure(3, weight=1) 
        self.grid_rowconfigure(2, weight=0) # Headers fixed

    def _load_data(self):
        # 1. Clear Table
        for widget in self.scroll_frame.winfo_children():
            widget.destroy()

        # 2. Fetch Data
        self.history_manager._load() # Reload from disk
        logs = self.history_manager.get_recent_logs()
        
        # 3. Filter
        query = self.entry_search.get().lower()
        status_filter = self.filter_status.get()
        date_filter = self.filter_date.get()
        
        filtered = []
        total_claims = 0
        total_value = 0.0
        
        for log in logs:
            name = log.get("game_name", "Unknown")
            status = log.get("status", "Success")
            price_str = log.get("price", "Unknown")
            
            # Text Search
            if query and query not in name.lower(): continue
            
            # Status Filter
            if "Success" in status_filter and status != "Success": continue
            if "Failed" in status_filter and status != "Failed": continue
            
            # Date Filter (Basic Implementation)
            # You can parse log['date'] and compare delta
            
            filtered.append(log)
            
            # Calc Stats (Naive)
            if status == "Success":
                total_claims += 1
                try:
                    # Clean price string: "$29.99" -> 29.99
                    clean = price_str.replace("$", "").replace("₺", "").replace("TRY", "").replace("Free", "0").strip()
                    val = float(clean)
                    total_value += val
                except: pass

        # 4. Render Rows
        if not filtered:
             ctk.CTkLabel(self.scroll_frame, text="No records found matching filters.", text_color="gray").pack(pady=20)
        else:
            for i, log in enumerate(filtered):
                self._draw_row(i, log)
        
        # 5. Update Top Stats
        self._update_stat_card(self.card_total, str(total_claims))
        self._update_stat_card(self.card_value, f"${total_value:.2f}")

    def _draw_row(self, index, log):
        # Row Frame (For styling background)
        # We draw directly to grid for performance, but background striping is tricky in pure grid.
        # We'll use a frame per row.
        row_color = ("gray90", "gray17") if index % 2 == 0 else "transparent"
        row_frame = ctk.CTkFrame(self.scroll_frame, fg_color=row_color, corner_radius=6, height=60)
        row_frame.grid(row=index, column=0, columnspan=5, sticky="ew", pady=2)
        
        # Configure internal grid of row_frame matches parent headers
        row_frame.grid_columnconfigure(1, weight=1)
        row_frame.grid_columnconfigure(2, minsize=150)
        row_frame.grid_columnconfigure(3, minsize=100)
        row_frame.grid_columnconfigure(4, minsize=100)

        # 1. Image (Placeholder or Cached)
        # Using a fixed placeholder color frame if no image
        img_url = log.get("image_url")
        
        try:
            # Placeholder Box
            img_box = ctk.CTkFrame(row_frame, width=40, height=50, fg_color="gray30")
            img_box.grid(row=0, column=0, padx=(10, 5), pady=5)
            
            # Ideally load image here. For now, simple icon or text
            ctk.CTkLabel(img_box, text="IMG", font=("Arial", 8)).place(relx=0.5, rely=0.5, anchor="center")
            
        except: pass

        # 2. Title & Source
        title_frame = ctk.CTkFrame(row_frame, fg_color="transparent")
        title_frame.grid(row=0, column=1, padx=10, sticky="w")
        
        ctk.CTkLabel(title_frame, text=log.get("game_name"), font=ctk.CTkFont(size=14, weight="bold")).pack(anchor="w")
        source = log.get("source", "Epic Games Store")
        ctk.CTkLabel(title_frame, text=source, font=ctk.CTkFont(size=11), text_color="gray").pack(anchor="w")

        # 3. Date
        date_str = log.get("date", "")
        # Try to make multiline: Date \n Time
        try:
            parts = date_str.split(" ")
            if len(parts) >= 2:
                final_date = f"{parts[0]}\n{parts[1]}"
            else:
                final_date = date_str
        except: final_date = date_str
        
        ctk.CTkLabel(row_frame, text=final_date, font=ctk.CTkFont(size=12), justify="left").grid(row=0, column=2, padx=10, sticky="w")

        # 4. Status Pill
        status = log.get("status", "Success")
        color = "#2ECC71" if status == "Success" else "#E74C3C" # Green / Red
        
        pill = ctk.CTkFrame(row_frame, fg_color=color, corner_radius=12, height=24)
        pill.grid(row=0, column=3, padx=10, sticky="w")
        ctk.CTkLabel(pill, text=status, font=ctk.CTkFont(size=11, weight="bold"), text_color="white").pack(padx=10, pady=2)

        # 5. Price
        price = log.get("price", "Unknown")
        ctk.CTkLabel(row_frame, text=price, font=ctk.CTkFont(size=13, weight="bold")).grid(row=0, column=4, padx=10, sticky="e")
