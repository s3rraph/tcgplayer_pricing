# ui_elements.py
import tkinter as tk
from tkinter import filedialog, ttk
from price_logic import adjust_prices
from table_update import update_table_and_totals
from file_handlers import load_csv, export_csv, load_state_from_db, save_state_to_db
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
    'include_store_price_var': None,
    'tree': None,
    'totals_labels': {}
}

config_values = load_state_from_db()

def recalc_prices():
    if state['df_original'].empty:
        return
    state['df_adjusted'] = state['df_original'].copy().apply(
        lambda row: adjust_prices(row, state), axis=1)
    update_table_and_totals(state)
    save_state_to_db(state)

def bind_entry(entry):
    entry.bind("<KeyRelease>", lambda e: recalc_prices())

def bind_checkbox(var):
    var.trace_add("write", lambda *_: recalc_prices())

def build_ui(root):
    frame = tk.Frame(root)
    frame.pack(expand=False, anchor='n')

    top_frame = tk.Frame(frame)
    top_frame.pack(expand=False, anchor='n')
    center_frame = tk.Frame(top_frame)
    center_frame.pack(anchor='n')

    def labeled_entry(parent, label_text, key):
        tk.Label(parent, text=label_text).pack(pady=2, anchor='w')
        entry = tk.Entry(parent)
        entry.insert(0, config_values.get(key, ""))
        entry.pack(pady=2, anchor='w')
        bind_entry(entry)
        return entry

    controls_frame = tk.Frame(center_frame)
    controls_frame.pack(side=tk.LEFT, padx=20, anchor='n')
    controls_inner = tk.Frame(controls_frame)
    controls_inner.pack()
    state['marketplace_percent'] = labeled_entry(controls_inner, "Marketplace % Increase:", "marketplace_percent")
    state['marketplace_floor'] = labeled_entry(controls_inner, "Marketplace Floor Price:", "marketplace_floor")
    state['store_percent'] = labeled_entry(controls_inner, "Store % Decrease:", "store_percent")
    state['store_floor'] = labeled_entry(controls_inner, "Store Floor Price:", "store_floor")

    scalers_frame = tk.Frame(center_frame)
    scalers_frame.pack(side=tk.LEFT, padx=20, anchor='n')
    scalers_inner = tk.Frame(scalers_frame)
    scalers_inner.pack()
    state['scaler_2_3'] = labeled_entry(scalers_inner, "Scaler for 2-3 copies (%):", "scaler_2_3")
    state['scaler_4_7'] = labeled_entry(scalers_inner, "Scaler for 4-7 copies (%):", "scaler_4_7")
    state['scaler_8plus'] = labeled_entry(scalers_inner, "Scaler for 8+ copies (%):", "scaler_8plus")

    totals_frame = tk.Frame(center_frame)
    totals_frame.pack(side=tk.LEFT, padx=20, anchor='n')
    totals_inner = tk.Frame(totals_frame)
    totals_inner.pack()

    tk.Label(totals_inner, text="(Based on Add to Quantity)", font=('Arial', 9, 'italic')).pack(pady=2, anchor='w')
    for key in ["totals_market_add", "totals_marketplace_add", "totals_store_add"]:
        lbl = tk.Label(totals_inner, text="Market Total: $0.00")
        lbl.pack(pady=2, anchor='w')
        state['totals_labels'][key] = lbl

    tk.Label(totals_inner, text="(Based on Total Quantity)", font=('Arial', 9, 'italic')).pack(pady=2, anchor='w')
    for key in ["totals_market_total", "totals_marketplace_total", "totals_store_total"]:
        lbl = tk.Label(totals_inner, text="Market Total: $0.00")
        lbl.pack(pady=2, anchor='w')
        state['totals_labels'][key] = lbl

    buttons_frame = tk.Frame(center_frame)
    buttons_frame.pack(side=tk.LEFT, padx=20, anchor='n')
    buttons_inner = tk.Frame(buttons_frame)
    buttons_inner.pack()
    tk.Button(buttons_inner, text="Load CSV", command=lambda: load_csv(state)).pack(pady=4, anchor='w')
    tk.Button(buttons_inner, text="Export Adjusted CSV", command=lambda: export_csv(state)).pack(pady=4, anchor='w')

    state['reprice_only_var'] = tk.BooleanVar(value=config_values.get('reprice_only_var', True))
    state['allow_lower_var'] = tk.BooleanVar(value=config_values.get('allow_lower_var', False))
    state['include_store_price_var'] = tk.BooleanVar(value=config_values.get('include_store_price_var', True))
    bind_checkbox(state['reprice_only_var'])
    bind_checkbox(state['allow_lower_var'])
    bind_checkbox(state['include_store_price_var'])
    tk.Checkbutton(buttons_inner, text="Reprice Only (Set Add to Quantity to 0)", variable=state['reprice_only_var']).pack(pady=4, anchor='w')
    tk.Checkbutton(buttons_inner, text="Allow Lower Prices", variable=state['allow_lower_var']).pack(pady=4, anchor='w')
    tk.Checkbutton(buttons_inner, text="Include My Store Price in Export", variable=state['include_store_price_var']).pack(pady=4, anchor='w')

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
