import PyInstaller.__main__
import os
import shutil

def build():
    print("🚀 Building Epic Games Auto Collector EXE...")
    
    # Ensure dist/build folders are clean
    if os.path.exists("dist"):
        shutil.rmtree("dist")
    if os.path.exists("build"):
        shutil.rmtree("build")

    # PyInstaller arguments
    args = [
        'src/main.py',                        # Main script
        '--name=EpicGamesCollector',          # Name of the exe
        '--onefile',                          # Single executable
        '--console',                          # Show console (needed for CLI menu & debugging)
        '--clean',                            # Clean cache
        
        # Collect CustomTkinter assets (themes, etc.)
        '--collect-all=customtkinter',
        
        # Include source code if needed by dynamic imports (safesty net)
        '--add-data=src;src',
        
        # Icon (if exists, else skip)
        # '--icon=app.ico', 
    ]
    
    print(f"🔧 Running PyInstaller with args: {args}")
    PyInstaller.__main__.run(args)
    
    print("\n✅ Build complete!")
    print(f"📂 Executable is in: {os.path.abspath('dist/EpicGamesCollector.exe')}")

if __name__ == "__main__":
    build()
