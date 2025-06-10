# price_logic.py
import pandas as pd

def safe_float(entry):
    try:
        value = entry.get()
        return float(value) if value.strip() else 0.0
    except:
        return 0.0

def adjust_prices(row, state):
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

            mp_percent = safe_float(state['marketplace_percent']) / 100.0
            mp_floor = safe_float(state['marketplace_floor'])
            store_percent_val = safe_float(state['store_percent']) / 100.0
            store_floor_val = safe_float(state['store_floor'])

            quantity = row.get('Total Quantity', 0)
            try:
                quantity = float(quantity)
            except:
                quantity = 0

            if quantity >= 8:
                scaler = safe_float(state['scaler_8plus']) / 100.0
            elif quantity >= 4:
                scaler = safe_float(state['scaler_4_7']) / 100.0
            elif quantity >= 2:
                scaler = safe_float(state['scaler_2_3']) / 100.0
            else:
                scaler = 0.0

            mp_percent += scaler
            new_marketplace = round(max(base_price * (1 + mp_percent), mp_floor), 2)
            new_store = round(max(base_price * (1 - store_percent_val), store_floor_val), 2)

            if state['allow_lower_var'].get():
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
