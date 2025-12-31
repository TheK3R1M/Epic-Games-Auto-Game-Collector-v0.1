import pystray
from PIL import Image
import threading
import sys
import os

class SystemTrayIcon:
    def __init__(self, app, on_show_callback, on_exit_callback):
        self.app = app
        self.on_show = on_show_callback
        self.on_exit = on_exit_callback
        self.icon = None

    def create_image(self):
        # Create a basic image if no icon file exists or just use a generated one
        # For simplicity/reliability, we'll try to load 'app.ico' or generate a colored square
        # In a polished app, you'd bundle a real .ico
        width = 64
        height = 64
        color1 = (52, 152, 219) # Blue
        color2 = (255, 255, 255)
        
        image = Image.new('RGB', (width, height), color1)
        # Simple pattern (white center)
        # for x in range(20, 44):
        #     for y in range(20, 44):
        #         image.putpixel((x, y), color2)
        
        # Try finding a real icon if it exists in assets or root
        possible_icons = ["app.ico", "assets/app.ico", "src/assets/app.ico"]
        for path in possible_icons:
            if os.path.exists(path):
                try:
                    return Image.open(path)
                except: pass
                
        return image

    def setup(self):
        menu = (
             pystray.MenuItem('Show Dashboard', self.show_app),
             pystray.MenuItem('Exit', self.exit_app)
        )
        self.icon = pystray.Icon("EpicCollector", self.create_image(), "Epic Games Collector", menu)

    def run(self):
        # pystray.run usually hangs the thread, so we run it in its own thread or handle carefully
        # But actually pystray.icon.run() blocks. 
        # Since we are already in a GUI loop (tkinter), we should run tray in a thread?
        # NO, tray usually needs main thread logic on some OSs, but on Windows it's flexible.
        # We will run the icon in a detached thread.
        threading.Thread(target=self.icon.run, daemon=True).start()

    def show_app(self, icon, item):
        self.on_show()
        self.stop() # Hide tray icon when app is shown? 
        # Usually desired behavior: Tray icon disappears when app is open, appears when hidden.
        # Or persists? User requested "hide tray feature used... reachable from hidden icons".
        # So it should persist OR appear on hide.
        # Let's make it appear ONLY when hidden to Auto-Pilot, as implied.
        
    def exit_app(self, icon, item):
        self.icon.stop()
        self.on_exit()

    def stop(self):
        if self.icon:
            self.icon.stop()
