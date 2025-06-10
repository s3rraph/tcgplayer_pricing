import tkinter as tk
from tkinter import filedialog, ttk
import pandas as pd

df_original = pd.DataFrame()
df_adjusted = pd.DataFrame()

def adjust_prices(row):
    try:
        market_price = row['TCG Market Price']
        low_price = row.get('TCG Low Price', float('nan'))
        base_price = max(market_price, low_price) if pd.notna(market_price) or pd.notna(low_price) else float('nan')

        if pd.notna(base_price):
            if market_price > low_price:
                row['Base Price Source'] = "Market"
            elif low_price > market_price:
                row['Base Price Source'] = "Low"
            elif market_price == low_price:
                row['Base Price Source'] = "Equal"
            else:
                row['Base Price Source'] = ""

            mp_percent = float(marketplace_percent.get()) / 100.0
            mp_floor = float(marketplace_floor.get())
            store_percent_val = float(store_percent.get()) / 100.0
            store_floor_val = float(store_floor.get())

            quantity = row.get('Total Quantity', 0)
            try:
                quantity = float(quantity)
            except:
                quantity = 0

            if quantity >= 8:
                scaler = float(scaler_8plus.get()) / 100.0
            elif quantity >= 4:
                scaler = float(scaler_4_7.get()) / 100.0
            elif quantity >= 2:
                scaler = float(scaler_2_3.get()) / 100.0
            else:
                scaler = 0.0

            mp_percent += scaler

            new_marketplace = round(max(base_price * (1 + mp_percent), mp_floor), 2)
            new_store = round(max(base_price * (1 - store_percent_val), store_floor_val), 2)

            if allow_lower_var.get():
                row['TCG Marketplace Price'] = new_marketplace
                row['My Store Price'] = new_store
            else:
                if pd.isna(row['TCG Marketplace Price']) or new_marketplace > row['TCG Marketplace Price']:
                    row['TCG Marketplace Price'] = new_marketplace
                if pd.isna(row['My Store Price']) or new_store > row['My Store Price']:
                    row['My Store Price'] = new_store
        else:
            row['Base Price Source'] = ""
    except Exception as e:
        print(f"Error adjusting row: {e}")
    return row

def update_table_and_totals(df):
    display_columns = ['TCGplayer Id', 'Product Name', 'TCG Market Price', 'TCG Low Price',
                       'Base Price Source', 'TCG Marketplace Price', 'My Store Price', 'Add to Quantity', 'Total Quantity']

    for item in tree.get_children():
        tree.delete(item)
    tree["columns"] = display_columns
    tree["show"] = "headings"

    for col in display_columns:
        tree.heading(col, text=col)
        tree.column(col, width=150)

    for _, row in df.iterrows():
        tree.insert("", "end", values=[row.get(col, '') for col in display_columns])

    try:
        for col in ['Add to Quantity', 'Total Quantity', 'TCG Market Price', 'TCG Low Price', 'TCG Marketplace Price', 'My Store Price']:
            df[col] = pd.to_numeric(df[col], errors='coerce').fillna(0)

        market_add = (df['Add to Quantity'] * df[['TCG Market Price', 'TCG Low Price']].max(axis=1)).sum()
        marketplace_add = (df['Add to Quantity'] * df['TCG Marketplace Price']).sum()
        store_add = (df['Add to Quantity'] * df['My Store Price']).sum()

        market_total = (df['Total Quantity'] * df[['TCG Market Price', 'TCG Low Price']].max(axis=1)).sum()
        marketplace_total = (df['Total Quantity'] * df['TCG Marketplace Price']).sum()
        store_total = (df['Total Quantity'] * df['My Store Price']).sum()
    except Exception:
        market_add = marketplace_add = store_add = 0
        market_total = marketplace_total = store_total = 0

    totals_market_add.config(text=f"Market Total: ${market_add:,.2f}")
    totals_marketplace_add.config(text=f"Marketplace Total: ${marketplace_add:,.2f}")
    totals_store_add.config(text=f"My Store Total: ${store_add:,.2f}")

    totals_market_total.config(text=f"Market Total: ${market_total:,.2f}")
    totals_marketplace_total.config(text=f"Marketplace Total: ${marketplace_total:,.2f}")
    totals_store_total.config(text=f"My Store Total: ${store_total:,.2f}")

def load_csv():
    global df_original, df_adjusted
    file_path = filedialog.askopenfilename(filetypes=[("CSV files", "*.csv")])
    if not file_path:
        return

    df = pd.read_csv(file_path)
    for col in ['Add to Quantity', 'Total Quantity', 'TCG Market Price', 'TCG Low Price', 'TCG Marketplace Price', 'My Store Price']:
        df[col] = pd.to_numeric(df.get(col, 0), errors='coerce').fillna(0)

    df_original = df.copy()
    df_adjusted = df_original.apply(adjust_prices, axis=1)
    update_table_and_totals(df_adjusted)

def recalc_prices():
    global df_adjusted
    if df_original.empty:
        return
    df_adjusted = df_original.copy().apply(adjust_prices, axis=1)
    update_table_and_totals(df_adjusted)

def export_csv():
    if df_adjusted.empty:
        return
    export_df = df_adjusted[['TCGplayer Id', 'TCG Marketplace Price', 'My Store Price', 'Add to Quantity', 'Base Price Source']].copy()
    if reprice_only_var.get():
        export_df['Add to Quantity'] = 0

    file_path = filedialog.asksaveasfilename(defaultextension=".csv", filetypes=[("CSV files", "*.csv")])
    if file_path:
        export_df.to_csv(file_path, index=False)

root = tk.Tk()
root.title("TCG Price Adjuster")
root.geometry("1200x900")

frame = tk.Frame(root)
frame.pack(expand=False, anchor='n')

top_frame = tk.Frame(frame)
top_frame.pack(expand=False, anchor='n')

center_frame = tk.Frame(top_frame)
center_frame.pack(anchor='n')

controls_frame = tk.Frame(center_frame)
controls_frame.pack(side=tk.LEFT, padx=20, anchor='n')
controls_inner = tk.Frame(controls_frame)
controls_inner.pack()

for widget in [
    tk.Label(controls_inner, text="Marketplace % Increase:"),
    (marketplace_percent := tk.Entry(controls_inner)),
    tk.Label(controls_inner, text="Marketplace Floor Price:"),
    (marketplace_floor := tk.Entry(controls_inner)),
    tk.Label(controls_inner, text="Store % Decrease:"),
    (store_percent := tk.Entry(controls_inner)),
    tk.Label(controls_inner, text="Store Floor Price:"),
    (store_floor := tk.Entry(controls_inner))
]:
    widget.pack(pady=2, anchor='w')

marketplace_percent.insert(0, "10")
marketplace_floor.insert(0, "0.19")
store_percent.insert(0, "5")
store_floor.insert(0, "0.15")

scalers_frame = tk.Frame(center_frame)
scalers_frame.pack(side=tk.LEFT, padx=20, anchor='n')
scalers_inner = tk.Frame(scalers_frame)
scalers_inner.pack()

for widget in [
    tk.Label(scalers_inner, text="Scaler for 2-3 copies (%):"),
    (scaler_2_3 := tk.Entry(scalers_inner)),
    tk.Label(scalers_inner, text="Scaler for 4-7 copies (%):"),
    (scaler_4_7 := tk.Entry(scalers_inner)),
    tk.Label(scalers_inner, text="Scaler for 8+ copies (%):"),
    (scaler_8plus := tk.Entry(scalers_inner))
]:
    widget.pack(pady=2, anchor='w')

scaler_2_3.insert(0, "2")
scaler_4_7.insert(0, "5")
scaler_8plus.insert(0, "10")

totals_frame = tk.Frame(center_frame)
totals_frame.pack(side=tk.LEFT, padx=20, anchor='n')
totals_inner = tk.Frame(totals_frame)
totals_inner.pack()

for widget in [
    tk.Label(totals_inner, text="Total Sales Value", font=('Arial', 10, 'bold')),
    tk.Label(totals_inner, text="(Based on Add to Quantity)", font=('Arial', 9, 'italic')),
    (totals_market_add := tk.Label(totals_inner, text="Market Total: $0.00")),
    (totals_marketplace_add := tk.Label(totals_inner, text="Marketplace Total: $0.00")),
    (totals_store_add := tk.Label(totals_inner, text="My Store Total: $0.00")),
    tk.Label(totals_inner, text="(Based on Total Quantity)", font=('Arial', 9, 'italic')),
    (totals_market_total := tk.Label(totals_inner, text="Market Total: $0.00")),
    (totals_marketplace_total := tk.Label(totals_inner, text="Marketplace Total: $0.00")),
    (totals_store_total := tk.Label(totals_inner, text="My Store Total: $0.00"))
]:
    widget.pack(pady=2, anchor='w')

buttons_frame = tk.Frame(center_frame)
buttons_frame.pack(side=tk.LEFT, padx=20, anchor='n')
buttons_inner = tk.Frame(buttons_frame)
buttons_inner.pack()

for widget in [
    tk.Button(buttons_inner, text="Load CSV", command=load_csv),
    tk.Button(buttons_inner, text="Recalculate Prices", command=recalc_prices),
    tk.Button(buttons_inner, text="Export Adjusted CSV", command=export_csv),
    tk.Checkbutton(buttons_inner, text="Reprice Only (Set Add to Quantity to 0)", variable=(reprice_only_var := tk.BooleanVar(value=True))),
    tk.Checkbutton(buttons_inner, text="Allow Lower Prices", variable=(allow_lower_var := tk.BooleanVar(value=False)))
]:
    widget.pack(pady=4, anchor='w')

tree_frame = tk.Frame(root)
tree_frame.pack(fill=tk.BOTH, expand=True)

tree_scroll_y = tk.Scrollbar(tree_frame, orient=tk.VERTICAL)
tree_scroll_y.pack(side=tk.RIGHT, fill=tk.Y)
tree_scroll_x = tk.Scrollbar(tree_frame, orient=tk.HORIZONTAL)
tree_scroll_x.pack(side=tk.BOTTOM, fill=tk.X)

tree = ttk.Treeview(tree_frame, yscrollcommand=tree_scroll_y.set, xscrollcommand=tree_scroll_x.set)
tree.pack(fill=tk.BOTH, expand=True)

tree_scroll_y.config(command=tree.yview)
tree_scroll_x.config(command=tree.xview)

root.mainloop()
