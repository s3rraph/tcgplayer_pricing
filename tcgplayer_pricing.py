# tcgplayer_pricing.py
import tkinter as tk
from ui_elements import build_ui

try:
    from _build_stamp import VERSION  # written by package.ps1
except ImportError:
    VERSION = None

if __name__ == "__main__":
    root = tk.Tk()
    root.title(f"TCG Price Adjuster v{VERSION}" if VERSION else "TCG Price Adjuster")
    root.geometry("1200x900")
    build_ui(root)
    root.mainloop()
