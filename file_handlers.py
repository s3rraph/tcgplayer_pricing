# file_handlers.py
import os
import json
from tkinter import filedialog
import pandas as pd
from price_logic import adjust_prices
from table_update import update_table_and_totals

DB_PATH = "database"

DEFAULT_VALUES = {
    "marketplace_percent": "10",
    "marketplace_floor": "0.19",
    "store_percent": "5",
    "store_floor": "0.15",
    "scaler_2_3": "2",
    "scaler_4_7": "5",
    "scaler_8plus": "10",
    "reprice_only_var": True,
    "allow_lower_var": False,
    "include_store_price_var": True
}

def load_csv(state):
    file_path = filedialog.askopenfilename(filetypes=[("CSV files", "*.csv")])
    if not file_path:
        return

    df = pd.read_csv(file_path)
    for col in ['Add to Quantity', 'Total Quantity', 'TCG Market Price', 'TCG Low Price', 'TCG Marketplace Price', 'My Store Price']:
        if col in df.columns:
          df[col] = pd.to_numeric(df.get(col, 0), errors='coerce').fillna(0)
    else:
        df[col] = 0

    state['df_original'] = df.copy()
    state['df_adjusted'] = state['df_original'].apply(lambda row: adjust_prices(row, state), axis=1)
    update_table_and_totals(state)

def export_csv(state):
    if state['df_adjusted'].empty:
        return

    include_store_price = state.get('include_store_price_var', None)
    columns = ['TCGplayer Id', 'TCG Marketplace Price', 'Add to Quantity']
    if include_store_price and include_store_price.get():
        columns.insert(2, 'My Store Price')

    export_df = state['df_adjusted'][columns].copy()
    if state['reprice_only_var'].get():
        export_df['Add to Quantity'] = 0

    file_path = filedialog.asksaveasfilename(defaultextension=".csv", filetypes=[("CSV files", "*.csv")])
    if file_path:
        export_df.to_csv(file_path, index=False)

def save_state_to_db(state):
    data = {
        "marketplace_percent": state['marketplace_percent'].get(),
        "marketplace_floor": state['marketplace_floor'].get(),
        "store_percent": state['store_percent'].get(),
        "store_floor": state['store_floor'].get(),
        "scaler_2_3": state['scaler_2_3'].get(),
        "scaler_4_7": state['scaler_4_7'].get(),
        "scaler_8plus": state['scaler_8plus'].get(),
        "reprice_only_var": state['reprice_only_var'].get(),
        "allow_lower_var": state['allow_lower_var'].get(),
        "include_store_price_var": state['include_store_price_var'].get()
    }
    with open(DB_PATH, 'w') as f:
        json.dump(data, f)

def load_state_from_db():
    if not os.path.exists(DB_PATH):
        with open(DB_PATH, 'w') as f:
            json.dump(DEFAULT_VALUES, f)
        return DEFAULT_VALUES

    try:
        with open(DB_PATH, 'r') as f:
            data = json.load(f)
        return {**DEFAULT_VALUES, **data}  # fill any missing keys with defaults
    except:
        return DEFAULT_VALUES
