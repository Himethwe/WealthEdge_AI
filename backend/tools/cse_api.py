import requests
import os
import json
from database.db_manager import get_connection

# ---------------------------------------------------------
# CONSTANTS & CONFIGURATION
# ---------------------------------------------------------
URL_ALL_SECTORS = "https://www.cse.lk/api/allSectors"
URL_ALL_SECURITY_CODES = "https://www.cse.lk/api/allSecurityCode"
URL_CHART_DATA = "https://www.cse.lk/api/chartData"
URL_TRADE_SUMMARY = "https://www.cse.lk/api/tradeSummary"

HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
    "Accept": "application/json, text/plain, */*",
    "Referer": "https://www.cse.lk/",
    "Connection": "keep-alive"
}

#5 influential companies on the CSE
BLUE_CHIPS = ["JKH.N0000", "SAMP.N0000", "COMB.N0000", "HAYL.N0000", "DIAL.N0000"]

# Path to the fundamentals JSON file (cse additional data for decisions)
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
FUNDAMENTALS_JSON_PATH = os.path.join(BASE_DIR, 'data', 'fundamentals.json')

# ---------------------------------------------------------
# AGENT PERCEPTION TOOLS
# ---------------------------------------------------------

def fetch_market_sentiment():
    """AGENT TOOL: Fetches the latest sector performance."""
    try:
        response = requests.post(URL_ALL_SECTORS, headers=HEADERS)
        response.raise_for_status() 
        
        sectors = response.json()
        processed_data = []
        for sector in sectors:
            processed_data.append({
                'name': sector.get('name'),
                'percentage_change': sector.get('percentage'),
                'turnover': sector.get('sectorTurnoverToday')
            })
        return processed_data
    except requests.exceptions.RequestException as e:
        print(f"[Error] Failed to reach CSE Sectors API: {e}")
        return None

def fetch_market_movers():
    """
    AGENT TOOL: Fetches all trade data, filters for Blue-Chips, 
    and identifies the Top Gainer for the day.
    """
    try:
        response = requests.post(URL_TRADE_SUMMARY, headers=HEADERS)
        response.raise_for_status()
        
        all_stocks = response.json().get('reqTradeSummery', [])
        extracted_data = []
        
        # 1. Filter for Blue-Chips
        for stock in all_stocks:
            symbol = stock.get('symbol')
            if symbol in BLUE_CHIPS:
                extracted_data.append({
                    "ticker": symbol,
                    "price": float(stock.get('price', 0)),
                    "change_percentage": float(stock.get('percentageChange', 0)),
                    "asset_class": "Equity"
                })
        
        # 2. Find Top Gainer
        if all_stocks:
            sorted_stocks = sorted(all_stocks, key=lambda x: x.get('percentageChange', 0), reverse=True)
            top_gainer = sorted_stocks[0]
            extracted_data.append({
                "ticker": f"TOP GAINER: {top_gainer.get('symbol')}",
                "price": float(top_gainer.get('price', 0)),
                "change_percentage": float(top_gainer.get('percentageChange', 0)),
                "asset_class": "Sentiment"
            })
            
        return extracted_data
    except Exception as e:
        print(f"[Error] Failed to fetch Market Movers: {e}")
        return []

def fetch_security_codes():
    """AGENT TOOL: Fetches company name to ticker symbol dictionary."""
    try:
        response = requests.get(URL_ALL_SECURITY_CODES, headers=HEADERS)
        response.raise_for_status()
        
        companies = response.json()
        code_map = {}
        for company in companies:
            if company.get('active') == 1: 
                name = company.get('name')
                symbol = company.get('symbol')
                code_map[name] = symbol
        return code_map
    except requests.exceptions.RequestException as e:
        print(f"[Error] Failed to reach CSE Security Codes API: {e}")
        return None

def fetch_chart_data(chart_id=1, period=1):
    """AGENT TOOL: Fetches historical trend data (Default 1 = ASPI)."""
    payload = {"chartId": str(chart_id), "period": str(period)}
    try:
        response = requests.post(URL_CHART_DATA, headers=HEADERS, data=payload)
        response.raise_for_status()
        raw_data = response.json()
        clean_trend = [{'timestamp': item.get('d'), 'price': item.get('v')} for item in raw_data]
        return clean_trend
    except requests.exceptions.RequestException as e:
        print(f"[Error] Failed to fetch chart data: {e}")
        return None

# ---------------------------------------------------------
# DATABASE INTEGRATION (MEMORY)
# ---------------------------------------------------------

def save_sector_data(data):
    """Saves sector sentiment to DuckDB."""
    if not data: return
    conn = get_connection()
    conn.execute("DELETE FROM market_data WHERE source = 'CSE' AND asset_class = 'Stock'")
    for item in data:
        conn.execute("""
            INSERT INTO market_data (source, asset_class, ticker, rate_or_price, change_percentage)
            VALUES (?, ?, ?, ?, ?)
        """, ('CSE', 'Stock', item['name'], 0.0, item['percentage_change']))
    conn.close()
    print("[Success] Market sentiment saved to DuckDB.")

def save_stock_data(data):
    """Saves individual Blue-Chips and Top Gainer to DuckDB."""
    if not data: return
    conn = get_connection()
    conn.execute("DELETE FROM market_data WHERE source = 'CSE' AND asset_class IN ('Equity', 'Sentiment')")
    for item in data:
        conn.execute("""
            INSERT INTO market_data (source, asset_class, ticker, rate_or_price, change_percentage)
            VALUES (?, ?, ?, ?, ?)
        """, ('CSE', item['asset_class'], item['ticker'], item['price'], item['change_percentage']))
    conn.close()
    print("[Success] Individual stocks and sentiment saved to DuckDB.")

def update_fundamentals_memory():
    """Bypasses the CSE API Paywall by loading verified fundamentals from JSON."""
    if not os.path.exists(FUNDAMENTALS_JSON_PATH):
        print(f"[Error] Could not find fundamentals.json at {FUNDAMENTALS_JSON_PATH}")
        return
        
    try:
        with open(FUNDAMENTALS_JSON_PATH, 'r') as file:
            fundamentals = json.load(file)
    except Exception as e:
        print(f"[Error] Failed to read fundamentals.json: {e}")
        return
        
    conn = get_connection()
    conn.execute("DELETE FROM market_data WHERE asset_class = 'Fundamental'")
    
    for ticker, metrics in fundamentals.items():
        if ticker == "metadata": continue
        
        # Save Dividend Yield
        conn.execute("""
            INSERT INTO market_data (source, asset_class, ticker, rate_or_price, change_percentage)
            VALUES (?, ?, ?, ?, ?)
        """, ('Local', 'Fundamental', f"{ticker} Div Yield", metrics['dividend_yield'], 0.0))
        
        # Save P/E Ratio
        conn.execute("""
            INSERT INTO market_data (source, asset_class, ticker, rate_or_price, change_percentage)
            VALUES (?, ?, ?, ?, ?)
        """, ('Local', 'Fundamental', f"{ticker} PE Ratio", metrics['pe_ratio'], 0.0))
            
    conn.close()
    print("[Success] Verified Stock Fundamentals (Div Yield & P/E) saved to DuckDB.")

# ---------------------------------------------------------
# LOCAL TESTING BLOCK
# ---------------------------------------------------------
if __name__ == "__main__":
    print("--- 1. Testing Market Sentiment ---")
    sentiment = fetch_market_sentiment()
    if sentiment:
        save_sector_data(sentiment)
        print(f"Sample Sector: {sentiment[0]['name']} -> {sentiment[0]['percentage_change']}%")
        
    print("\n--- 2. Testing Market Movers (Blue-Chips & Top Gainer) ---")
    movers = fetch_market_movers()
    if movers:
        save_stock_data(movers)
        print(f"Sample Mover: {movers[0]['ticker']} -> {movers[0]['price']} LKR")

    print("\n--- 3. Testing Security Codes ---")
    codes = fetch_security_codes()
    if codes:
        sample_company = list(codes.keys())[0]
        print(f"Sample Code: {sample_company} -> {codes[sample_company]}")
        
    print("\n--- 4. Testing Chart Data (ASPI Macro Trend) ---")
    chart = fetch_chart_data(chart_id=1, period=1)
    if chart:
        print(f"Fetched {len(chart)} points. Latest Index: {chart[-1]['price']}")
        
    print("\n--- 5. Testing Fundamentals Injection ---")
    update_fundamentals_memory()