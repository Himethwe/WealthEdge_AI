import os
from dotenv import load_dotenv
from langchain_groq import ChatGroq
from langchain.tools import tool

from langchain.agents import create_agent

import sys
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from database.db_manager import get_connection

load_dotenv()

#Initialize llama
llm = ChatGroq(
    model="llama-3.3-70b-versatile",
    temperature=0.1, 
    max_retries=2
)

# ---------------------------------------------------------
# AGENT TOOLS
# ---------------------------------------------------------

@tool
def get_macro_data() -> str:
    """Use this tool to get the current Inflation (CCPI) and Withholding Tax (WHT) rates in Sri Lanka. Always check this before recommending fixed income."""
    conn = get_connection()
    cursor = conn.execute("SELECT ticker, rate_or_price FROM market_data WHERE asset_class IN ('Inflation', 'Tax')")
    results = cursor.fetchall()
    conn.close()
    
    if not results: return "Macro data not available."
    return "\n".join([f"{row[0]}: {row[1]}%" for row in results])

@tool
def get_risk_free_rates() -> str:
    """Use this tool to get the current safe investment rates: CBSL Treasury Bills and Bank Fixed Deposits (FD)."""
    conn = get_connection()
    cursor = conn.execute("SELECT source, ticker, rate_or_price FROM market_data WHERE asset_class IN ('T-Bill', 'FD') ORDER BY rate_or_price DESC")
    results = cursor.fetchall()
    conn.close()
    
    if not results: return "Risk-free rates not available."
    return "\n".join([f"{row[0]} - {row[1]}: {row[2]}%" for row in results])

@tool
def get_stock_market_data() -> str:
    """Use this tool to get the live prices of Sri Lankan Blue-Chip stocks, Top Gainers, and Sector performance."""
    conn = get_connection()
    cursor = conn.execute("SELECT asset_class, ticker, rate_or_price, change_percentage FROM market_data WHERE source = 'CSE'")
    results = cursor.fetchall()
    conn.close()
    
    if not results: return "Stock market data not available."
    output = []
    for row in results:
        asset, ticker, price, change = row
        if asset == 'Sentiment':
            output.append(f"{ticker} | Change: {change}%")
        elif asset == 'Equity':
            output.append(f"Stock: {ticker} | Price: {price} LKR | Change: {change}%")
        elif asset == 'Stock':
            output.append(f"Sector: {ticker} | Change: {change}%")
    return "\n".join(output)

@tool
def get_stock_fundamentals() -> str:
    """Use this tool to get the P/E Ratio (valuation) and Dividend Yield (annual return) for stocks. REQUIRED for making stock recommendations."""
    conn = get_connection()
    cursor = conn.execute("SELECT ticker, rate_or_price FROM market_data WHERE asset_class = 'Fundamental'")
    results = cursor.fetchall()
    conn.close()
    
    if not results: return "Fundamental data not available."
    return "\n".join([f"{row[0]}: {row[1]}" for row in results])

tools = [get_macro_data, get_risk_free_rates, get_stock_market_data, get_stock_fundamentals]

# ---------------------------------------------------------
# THE AGENT BRAIN
# ---------------------------------------------------------

system_prompt = """You are an elite, analytical Sri Lankan Financial Advisor AI named WealthEdge.
Your goal is to provide data-driven investment advice based ONLY on the tools provided to you.

CRITICAL RULES FOR ANALYSIS:
1. ALWAYS check 'get_macro_data' to factor in CCPI Inflation and WHT (Tax) for real net returns.
   - VERY IMPORTANT: If WHT is returned as 0.05, it means 5%. Use 0.05 as the decimal in your math.
   - If Inflation is 2.2, it means 2.2%. Use 0.022 as the decimal in your math.
2. ALWAYS check 'get_risk_free_rates' for safe benchmarks (T-Bills, FDs).
3. ALWAYS check 'get_stock_market_data' and 'get_stock_fundamentals' for equity analysis.
4. Calculate the REAL return of a T-Bill/FD: (Nominal Rate * (1 - WHT)) - Inflation.

CRITICAL RULES FOR FORMATTING YOUR RESPONSE:
You MUST format your final response using strict Markdown. Never output a paragraph wall of text. You must use the exact structure and headers below:

### Macro Environment
* Briefly state the current inflation and tax rates used for calculations.

### Risk-Free Yield Analysis
* Show the step-by-step math for the T-Bill Real Return using this format:
  `Real Return = (Nominal * (1 - WHT)) - Inflation = Result%`

### Equity Comparison
* Use bullet points to list the stocks analyzed.
* **Bold** the stock ticker.
* Compare their Dividend Yield to the T-Bill Real Return.
* State the P/E ratio and note it as a risk indicator (lower is safer).

### Strategic Recommendation
* Based on the user's specific capital (e.g., 30,000 LKR), provide a clear, conclusive recommendation.
* Show the projected annual return in LKR. Always format LKR amounts with commas (e.g., 30,000 LKR).
* Add a 1-sentence disclaimer that this is data-driven analysis, not personalized financial advice.
"""

# Compile the Agent
agent = create_agent(
    llm,
    tools=tools,
    system_prompt=system_prompt
)

# ---------------------------------------------------------
# AGENT EXECUTION & REASONING EXTRACTION
# ---------------------------------------------------------

def get_agent_response(user_query: str):
    """
    Executes the agent and extracts both the final response and the internal chain of thought.
    """
    result = agent.invoke({
        "messages": [{"role": "user", "content": user_query}]
    })
    
    messages = result.get("messages", [])
    reasoning_steps = []
    
    # Extract the internal ReAct logic
    for msg in messages:
        # Check if the AI decided to use a tool
        if hasattr(msg, 'tool_calls') and msg.tool_calls:
            for call in msg.tool_calls:
                tool_name = call.get('name', 'database')
                reasoning_steps.append(f"[Action] Requesting live data from {tool_name}...")
        
        # Check if the tool returned an observation
        elif hasattr(msg, 'type') and msg.type == 'tool':
            tool_name = msg.name
            reasoning_steps.append(f"[Observation] Successfully loaded market constraints from {tool_name}.")

    final_answer = messages[-1].content
    
    # Fallback if no tools were needed
    if not reasoning_steps:
        reasoning_steps = ["[Action] Analyzing query...", "[Observation] Formulating response based on internal logic."]
        
    return final_answer, reasoning_steps

# ---------------------------------------------------------
# LOCAL TESTING BLOCK
# ---------------------------------------------------------
if __name__ == "__main__":
    print("[System] Sri Lankan Investment Agent Online (LangChain v1.0)!\n")
    test_query = "Compare the 364-day T-Bill against COMB."
    print(f"User: {test_query}\n")
    
    answer, steps = get_agent_response(test_query)
    
    print("--- CHAIN OF THOUGHT ---")
    for step in steps:
        print(step)
        
    print("\n================ FINAL ANSWER ================\n")
    print(answer)