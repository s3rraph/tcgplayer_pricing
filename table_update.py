# table_update.py
import pandas as pd

def update_table_and_totals(state):
    df = state['df_adjusted']
    tree = state['tree']
    display_columns = ['TCGplayer Id', 'Product Name', 'TCG Market Price', 'TCG Low Price',
                       'Base Price Source', 'TCG Marketplace Price', 'My Store Price', 'Add to Quantity', 'Total Quantity']

    tree.delete(*tree.get_children())
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

    labels = state['totals_labels']
    labels['totals_market_add'].config(text=f"Market Total: ${market_add:,.2f}")
    labels['totals_marketplace_add'].config(text=f"Marketplace Total: ${marketplace_add:,.2f}")
    labels['totals_store_add'].config(text=f"My Store Total: ${store_add:,.2f}")
    labels['totals_market_total'].config(text=f"Market Total: ${market_total:,.2f}")
    labels['totals_marketplace_total'].config(text=f"Marketplace Total: ${marketplace_total:,.2f}")
    labels['totals_store_total'].config(text=f"My Store Total: ${store_total:,.2f}")
