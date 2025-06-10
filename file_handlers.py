# file_handlers.py
from tkinter import filedialog
import pandas as pd
from price_logic import adjust_prices
from table_update import update_table_and_totals

def load_csv(state):
    file_path = filedialog.askopenfilename(filetypes=[("CSV files", "*.csv")])
    if not file_path:
        return

    df = pd.read_csv(file_path)
    for col in ['Add to Quantity', 'Total Quantity', 'TCG Market Price', 'TCG Low Price', 'TCG Marketplace Price', 'My Store Price']:
        df[col] = pd.to_numeric(df.get(col, 0), errors='coerce').fillna(0)

    state['df_original'] = df.copy()
    state['df_adjusted'] = state['df_original'].apply(lambda row: adjust_prices(row, state), axis=1)
    update_table_and_totals(state)

def export_csv(state):
    if state['df_adjusted'].empty:
        return

    export_df = state['df_adjusted'][['TCGplayer Id', 'TCG Marketplace Price', 'My Store Price', 'Add to Quantity', 'Base Price Source']].copy()
    if state['reprice_only_var'].get():
        export_df['Add to Quantity'] = 0

    file_path = filedialog.asksaveasfilename(defaultextension=".csv", filetypes=[("CSV files", "*.csv")])
    if file_path:
        export_df.to_csv(file_path, index=False)
