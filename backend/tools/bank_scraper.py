import json
import os
from database.db_manager import get_connection

#Config path
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
BANK_JSON_PATH = os.path.join(BASE_DIR, 'data', 'bank_rates.json')
MACRO_JSON_PATH = os.path.join(BASE_DIR, 'data', 'macro_indicators.json')

def load_json_data(file_path):
    """Generic loader for JSON knowledge base files."""
    try:
        with open(file_path, 'r') as f:
            return json.load(f)
    except FileNotFoundError:
        print(f"⚠️ Warning: File not found at {file_path}")
        return {}

def update_bank_memory():
    """Saves the JSON bank rates into DuckDB."""
    rates = load_json_data(BANK_JSON_PATH)
    if not rates: return
    
    conn = get_connection()
    
    conn.execute("DELETE FROM market_data WHERE asset_class = 'FD'")
    
    for key, products in rates.items():
        if key == "metadata":
            continue
            
        bank_name = key
        for period, rate in products.items():
            if not isinstance(rate, (int, float)):
                continue
            
            conn.execute("""
                INSERT INTO market_data (source, asset_class, ticker, rate_or_price, change_percentage)
                VALUES (?, ?, ?, ?, ?)
            """, (bank_name, 'FD', f"{bank_name} {period}", float(rate), 0.0))
            
    conn.close()
    print(f"✅ Verified bank rates synced to Agent Memory.")

def update_macro_memory():
    """Saves Inflation and Tax data from JSON into DuckDB."""
    macro = load_json_data(MACRO_JSON_PATH)
    if not macro: return
    
    conn = get_connection()
    
    # Clean old macro data to prevent duplicates
    conn.execute("DELETE FROM market_data WHERE asset_class IN ('Inflation', 'Tax')")
    
    # 1. Sync Inflation (CCPI)
    if 'inflation' in macro:
        conn.execute("""
            INSERT INTO market_data (source, asset_class, ticker, rate_or_price, change_percentage)
            VALUES (?, ?, ?, ?, ?)
        """, ('CBSL', 'Inflation', 'CCPI', float(macro['inflation']['value']), 0.0))
        
    # 2. Sync Tax (WHT)
    if 'tax_rates' in macro:
        conn.execute("""
            INSERT INTO market_data (source, asset_class, ticker, rate_or_price, change_percentage)
            VALUES (?, ?, ?, ?, ?)
        """, ('Gov', 'Tax', 'WHT', float(macro['tax_rates']['WHT']), 0.0))
        
    conn.close()
    print(f"✅ Macro indicators (Inflation & Tax) synced to Agent Memory.")

if __name__ == "__main__":
    print("--- Starting Manual Data Sync ---")
    update_bank_memory()
    update_macro_memory()
    print("--- Sync Complete ---")