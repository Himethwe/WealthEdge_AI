# WealthEdge AI - Autonomous Financial Advisor

WealthEdge AI is a full-stack, autonomous AI agent designed to provide data-driven financial insights for the Sri Lankan market. It leverages live data from the Colombo Stock Exchange (CSE) and the Central Bank of Sri Lanka (CBSL) to calculate real net yields and perform equity risk analysis.

## Agentic Architecture

Unlike standard LLM chatbots, WealthEdge operates as a true Agent using the ReAct (Reasoning and Acting) framework:

- **Autonomy:** The agent determines which tools to call based on the user's prompt.
- **System Interaction:** It autonomously queries a DuckDB database using custom Python tools.
- **Chain of Thought:** The UI exposes the agent's internal reasoning loop, proving its step-by-step logic (e.g., fetching inflation -> calculating risk-free rates -> comparing equity dividend yields).

## Tech Stack

- **Frontend:** React, TypeScript, Vite, Tailwind CSS v4 (Generative UI & Floating Phone Layout)
- **Backend:** Python, FastAPI, Uvicorn
- **AI Engine:** LangChain v1.0, Groq (Llama 3.3 70B Versatile)
- **Database:** DuckDB (In-memory analytical processing)

## Repository Structure

- `/backend` - Contains the FastAPI server, LangChain agent logic (`investment_agent.py`), and tool definitions.
- `/frontend` - Contains the Vite/React application, custom Tailwind styling, and Markdown parsers.

## Setup Instructions

### 1. Backend Setup

Navigate to the backend directory:
`cd backend`

Create and activate the virtual environment:
`python -m venv venv`
`.\venv\Scripts\activate` # Windows

Install dependencies:
`pip install -r requirements.txt`

Set up your environment variables:
Create a `.env` file in the backend directory and add your Groq API key:
`GROQ_API_KEY=your_key_here`

Start the server:
`uvicorn main:app --reload`

### 2. Frontend Setup

Open a new terminal and navigate to the frontend directory:
`cd frontend`

Install dependencies:
`npm install`

Start the development server:
`npm run dev`

Navigate to `http://localhost:5173` to interact with WealthEdge AI.
