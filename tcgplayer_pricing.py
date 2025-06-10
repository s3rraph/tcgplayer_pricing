# tcgplayer_pricing.py
import tkinter as tk
from ui_elements import build_ui

if __name__ == "__main__":
    root = tk.Tk()
    root.title("TCG Price Adjuster")
    root.geometry("1200x900")
    build_ui(root)
    root.mainloop()
