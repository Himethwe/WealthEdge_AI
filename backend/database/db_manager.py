import duckdb
import os

DB_PATH = os.path.join(os.path.dirname(__file__), "..", "investment_data.db")

def get_connection():
    """Returns a connection to the DuckDB database."""
    return duckdb.connect(DB_PATH)

def initialize_db():
    """Sets up the initial tables for the agent's memory and data."""
    conn = get_connection()
    
    # 1. Table for Market Trends
    conn.execute("""
        CREATE TABLE IF NOT EXISTS market_data (
            source TEXT,            -- 'CSE', 'CBSL', or 'Bank'
            asset_class TEXT,       -- 'Stock', 'T-Bill', 'FD'
            ticker TEXT,            -- e.g., 'JKH.N0000'
            rate_or_price DOUBLE,
            change_percentage DOUBLE,
            collected_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    """)
    
    # 2. Table for User Memory
    conn.execute("""
        CREATE TABLE IF NOT EXISTS user_profiles (
            user_id TEXT PRIMARY KEY,
            risk_tolerance TEXT, 
            investment_goal DOUBLE,
            time_horizon_months INTEGER,
            last_interaction TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    """)
    
    conn.close()
    print(f"✅ DuckDB initialized at {DB_PATH}")

if __name__ == "__main__":
    initialize_db()