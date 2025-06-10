# ui_elements.py
import tkinter as tk
from tkinter import filedialog, ttk
from price_logic import adjust_prices
from table_update import update_table_and_totals
from file_handlers import load_csv, export_csv
import pandas as pd

state = {
    'df_original': pd.DataFrame(),
    'df_adjusted': pd.DataFrame(),
    'marketplace_percent': None,
    'marketplace_floor': None,
    'store_percent': None,
    'store_floor': None,
    'scaler_2_3': None,
    'scaler_4_7': None,
    'scaler_8plus': None,
    'allow_lower_var': None,
    'reprice_only_var': None,
    'tree': None,
    'totals_labels': {}
}

def recalc_prices():
    if state['df_original'].empty:
        return
    state['df_adjusted'] = state['df_original'].copy().apply(
        lambda row: adjust_prices(row, state), axis=1)
    update_table_and_totals(state)

def build_ui(root):
    frame = tk.Frame(root)
    frame.pack(expand=False, anchor='n')

    top_frame = tk.Frame(frame)
    top_frame.pack(expand=False, anchor='n')
    center_frame = tk.Frame(top_frame)
    center_frame.pack(anchor='n')

    def labeled_entry(parent, label_text, default):
        tk.Label(parent, text=label_text).pack(pady=2, anchor='w')
        entry = tk.Entry(parent)
        entry.insert(0, default)
        entry.pack(pady=2, anchor='w')
        return entry

    controls_frame = tk.Frame(center_frame)
    controls_frame.pack(side=tk.LEFT, padx=20, anchor='n')
    controls_inner = tk.Frame(controls_frame)
    controls_inner.pack()
    state['marketplace_percent'] = labeled_entry(controls_inner, "Marketplace % Increase:", "10")
    state['marketplace_floor'] = labeled_entry(controls_inner, "Marketplace Floor Price:", "0.19")
    state['store_percent'] = labeled_entry(controls_inner, "Store % Decrease:", "5")
    state['store_floor'] = labeled_entry(controls_inner, "Store Floor Price:", "0.15")

    scalers_frame = tk.Frame(center_frame)
    scalers_frame.pack(side=tk.LEFT, padx=20, anchor='n')
    scalers_inner = tk.Frame(scalers_frame)
    scalers_inner.pack()
    state['scaler_2_3'] = labeled_entry(scalers_inner, "Scaler for 2-3 copies (%):", "2")
    state['scaler_4_7'] = labeled_entry(scalers_inner, "Scaler for 4-7 copies (%):", "5")
    state['scaler_8plus'] = labeled_entry(scalers_inner, "Scaler for 8+ copies (%):", "10")

    totals_frame = tk.Frame(center_frame)
    totals_frame.pack(side=tk.LEFT, padx=20, anchor='n')
    totals_inner = tk.Frame(totals_frame)
    totals_inner.pack()
    for key in [
        "totals_market_add", "totals_marketplace_add", "totals_store_add",
        "totals_market_total", "totals_marketplace_total", "totals_store_total"]:
        lbl = tk.Label(totals_inner, text="Market Total: $0.00")
        lbl.pack(pady=2, anchor='w')
        state['totals_labels'][key] = lbl

    buttons_frame = tk.Frame(center_frame)
    buttons_frame.pack(side=tk.LEFT, padx=20, anchor='n')
    buttons_inner = tk.Frame(buttons_frame)
    buttons_inner.pack()
    tk.Button(buttons_inner, text="Load CSV", command=lambda: load_csv(state)).pack(pady=4, anchor='w')
    tk.Button(buttons_inner, text="Recalculate Prices", command=recalc_prices).pack(pady=4, anchor='w')
    tk.Button(buttons_inner, text="Export Adjusted CSV", command=lambda: export_csv(state)).pack(pady=4, anchor='w')

    state['reprice_only_var'] = tk.BooleanVar(value=True)
    state['allow_lower_var'] = tk.BooleanVar(value=False)
    tk.Checkbutton(buttons_inner, text="Reprice Only (Set Add to Quantity to 0)", variable=state['reprice_only_var']).pack(pady=4, anchor='w')
    tk.Checkbutton(buttons_inner, text="Allow Lower Prices", variable=state['allow_lower_var']).pack(pady=4, anchor='w')

    tree_frame = tk.Frame(root)
    tree_frame.pack(fill=tk.BOTH, expand=True)

    tree_scroll_y = tk.Scrollbar(tree_frame, orient=tk.VERTICAL)
    tree_scroll_y.pack(side=tk.RIGHT, fill=tk.Y)
    tree_scroll_x = tk.Scrollbar(tree_frame, orient=tk.HORIZONTAL)
    tree_scroll_x.pack(side=tk.BOTTOM, fill=tk.X)

    state['tree'] = ttk.Treeview(tree_frame, yscrollcommand=tree_scroll_y.set, xscrollcommand=tree_scroll_x.set)
    state['tree'].pack(fill=tk.BOTH, expand=True)
    tree_scroll_y.config(command=state['tree'].yview)
    tree_scroll_x.config(command=state['tree'].xview)
