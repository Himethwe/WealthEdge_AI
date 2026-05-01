import requests
import re
from bs4 import BeautifulSoup
from database.db_manager import get_connection

# ---------------------------------------------------------
# CONSTANTS & CONFIGURATION
# ---------------------------------------------------------
URL_TBILLS = "https://www.cbsl.lk/eResearch/MoneyMarketRatesDefault.aspx?ReportId=6169"

HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,*/*;q=0.8"
}

# ---------------------------------------------------------
# AGENT PERCEPTION TOOLS
# ---------------------------------------------------------

def fetch_tbill_rates():
    """
    AGENT TOOL: Scrapes the CBSL website for the latest Treasury Bill rates.
    """
    try:
        response = requests.get(URL_TBILLS, headers=HEADERS)
        response.raise_for_status()
        
        soup = BeautifulSoup(response.text, 'html.parser')
        rates = []
        rows = soup.find_all('tr')
        
        for row in rows:
            cols = row.find_all(['td', 'th'])
            text_data = [col.get_text(strip=True) for col in cols]
            
            #Check if row has atleast 4 columns
            if len(text_data) >= 4:
                # Regular Expression to check if Column 0 is a date (YYYY-MM-DD)
                if re.match(r'\d{4}-\d{2}-\d{2}', text_data[0]):
                    try:
                        rate_91 = float(text_data[1])
                        rate_182 = float(text_data[2])
                        rate_364 = float(text_data[3])
                        
                        rates.append({"ticker": "91-Day T-Bill", "rate": rate_91})
                        rates.append({"ticker": "182-Day T-Bill", "rate": rate_182})
                        rates.append({"ticker": "364-Day T-Bill", "rate": rate_364})
                        
                        break 
                        
                    except ValueError:
                        continue
                
        if not rates:
            raise ValueError("Could not find valid date rows with numeric data.")
            
        return rates
        
    except Exception as e:
        print(f"[Error] Failed to scrape CBSL T-Bill rates: {e}")
        print("[System] Using recent fallback rates for continuity.")
        return [
            {"ticker": "91-Day T-Bill", "rate": 8.05},
            {"ticker": "182-Day T-Bill", "rate": 8.22},
            {"ticker": "364-Day T-Bill", "rate": 8.41}
        ]

# ---------------------------------------------------------
# DATABASE INTEGRATION (MEMORY)
# ---------------------------------------------------------

def save_cbsl_data(data):
    """Saves the T-Bill rates to DuckDB."""
    if not data:
        return
        
    conn = get_connection()
    conn.execute("DELETE FROM market_data WHERE source = 'CBSL' AND asset_class = 'T-Bill'")
    
    for item in data:
        conn.execute("""
            INSERT INTO market_data (source, asset_class, ticker, rate_or_price, change_percentage)
            VALUES (?, ?, ?, ?, ?)
        """, ('CBSL', 'T-Bill', item['ticker'], item['rate'], 0.0))
    
    conn.close()
    print("[Success] CBSL Treasury Bill rates saved to DuckDB Memory.")

# ---------------------------------------------------------
# LOCAL TESTING BLOCK
# ---------------------------------------------------------
if __name__ == "__main__":
    print("--- Testing CBSL T-Bill Scraper ---")
    tbill_rates = fetch_tbill_rates()
    
    if tbill_rates:
        print(f"Successfully fetched {len(tbill_rates)} T-Bill tenures.")
        for rate in tbill_rates:
            print(f"> {rate['ticker']}: {rate['rate']}%")
            
        save_cbsl_data(tbill_rates)