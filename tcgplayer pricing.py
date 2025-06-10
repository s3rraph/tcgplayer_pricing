import tkinter as tk
from tkinter import filedialog, ttk
import pandas as pd

df_adjusted = pd.DataFrame()

def adjust_prices(row):
    try:
        market_price = row['TCG Market Price']
        if pd.notna(market_price):
            # Get user inputs
            mp_percent = float(marketplace_percent.get()) / 100.0
            mp_floor = float(marketplace_floor.get())
            store_percent_val = float(store_percent.get()) / 100.0
            store_floor_val = float(store_floor.get())

            new_marketplace = round(max(market_price * (1 + mp_percent), mp_floor), 2)
            new_store = round(max(market_price * (1 - store_percent_val), store_floor_val), 2)

            if allow_lower_var.get():
                row['TCG Marketplace Price'] = new_marketplace
                row['My Store Price'] = new_store
            else:
                if pd.isna(row['TCG Marketplace Price']) or new_marketplace > row['TCG Marketplace Price']:
                    row['TCG Marketplace Price'] = new_marketplace
                if pd.isna(row['My Store Price']) or new_store > row['My Store Price']:
                    row['My Store Price'] = new_store
    except Exception as e:
        print(f"Error adjusting row: {e}")
    return row

def update_table_and_totals(df):
    display_columns = ['TCGplayer Id', 'Product Name', 'TCG Market Price',
                       'TCG Marketplace Price', 'My Store Price', 'Add to Quantity', 'Total Quantity']

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
        for col in ['Add to Quantity', 'Total Quantity', 'TCG Market Price', 'TCG Marketplace Price', 'My Store Price']:
            df[col] = pd.to_numeric(df[col], errors='coerce').fillna(0)

        market_add = (df['Add to Quantity'] * df['TCG Market Price']).sum()
        marketplace_add = (df['Add to Quantity'] * df['TCG Marketplace Price']).sum()
        store_add = (df['Add to Quantity'] * df['My Store Price']).sum()

        market_total = (df['Total Quantity'] * df['TCG Market Price']).sum()
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
    global df_adjusted
    file_path = filedialog.askopenfilename(filetypes=[("CSV files", "*.csv")])
    if not file_path:
        return

    df = pd.read_csv(file_path)

    for col in ['Add to Quantity', 'Total Quantity', 'TCG Market Price', 'TCG Marketplace Price', 'My Store Price']:
        df[col] = pd.to_numeric(df[col], errors='coerce').fillna(0)

    df = df.apply(adjust_prices, axis=1)
    df_adjusted = df

    update_table_and_totals(df_adjusted)

def recalc_prices():
    global df_adjusted
    if df_adjusted.empty:
        return
    df_adjusted = df_adjusted.apply(adjust_prices, axis=1)
    update_table_and_totals(df_adjusted)

def export_csv():
    if df_adjusted.empty:
        return

    export_df = df_adjusted[['TCGplayer Id', 'TCG Marketplace Price', 'My Store Price', 'Add to Quantity']].copy()
    if reprice_only_var.get():
        export_df['Add to Quantity'] = 0

    file_path = filedialog.asksaveasfilename(defaultextension=".csv", filetypes=[("CSV files", "*.csv")])
    if file_path:
        export_df.to_csv(file_path, index=False)

# GUI Setup
root = tk.Tk()
root.title("TCG Price Adjuster")
root.geometry("1020x950")

frame = tk.Frame(root)
frame.pack(fill=tk.BOTH, expand=True)

tk.Button(frame, text="Load CSV", command=load_csv).pack(pady=5)

# Checkboxes
reprice_only_var = tk.BooleanVar(value=True)
tk.Checkbutton(frame, text="Reprice Only (Set Add to Quantity to 0)", variable=reprice_only_var).pack()

allow_lower_var = tk.BooleanVar(value=False)
tk.Checkbutton(frame, text="Allow Lower Prices", variable=allow_lower_var).pack()

# Price Inputs
tk.Label(frame, text="Marketplace % Increase:").pack()
marketplace_percent = tk.Entry(frame)
marketplace_percent.insert(0, "10")
marketplace_percent.pack()

tk.Label(frame, text="Marketplace Floor Price:").pack()
marketplace_floor = tk.Entry(frame)
marketplace_floor.insert(0, "0.19")
marketplace_floor.pack()

tk.Label(frame, text="Store % Decrease:").pack()
store_percent = tk.Entry(frame)
store_percent.insert(0, "5")
store_percent.pack()

tk.Label(frame, text="Store Floor Price:").pack()
store_floor = tk.Entry(frame)
store_floor.insert(0, "0.15")
store_floor.pack()

# Recalc Button
tk.Button(frame, text="Recalculate Prices", command=recalc_prices).pack(pady=10)

# Totals Display
tk.Label(frame, text="Total Sales Value", font=('Arial', 10, 'bold')).pack(pady=(10, 0))

tk.Label(frame, text="(Based on Add to Quantity)", font=('Arial', 9, 'italic')).pack()
totals_market_add = tk.Label(frame, text="Market Total: $0.00")
totals_market_add.pack()
totals_marketplace_add = tk.Label(frame, text="Marketplace Total: $0.00")
totals_marketplace_add.pack()
totals_store_add = tk.Label(frame, text="My Store Total: $0.00")
totals_store_add.pack()

tk.Label(frame, text="(Based on Total Quantity)", font=('Arial', 9, 'italic')).pack(pady=(10, 0))
totals_market_total = tk.Label(frame, text="Market Total: $0.00")
totals_market_total.pack()
totals_marketplace_total = tk.Label(frame, text="Marketplace Total: $0.00")
totals_marketplace_total.pack()
totals_store_total = tk.Label(frame, text="My Store Total: $0.00")
totals_store_total.pack()

# Export Button
tk.Button(frame, text="Export Adjusted CSV", command=export_csv).pack(pady=10)

# Treeview
tree_frame = tk.Frame(frame)
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
