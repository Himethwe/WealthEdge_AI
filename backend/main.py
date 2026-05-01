from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from fastapi.middleware.cors import CORSMiddleware

# Import the new helper function from your agent file
from agents.investment_agent import get_agent_response

app = FastAPI(title="Sri Lankan Financial AI API")

# CORS Middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  #nedd to change in production to exact url
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Define the data structure we expect from React
class ChatRequest(BaseModel):
    message: str

# Define the endpoint
@app.post("/api/chat")
async def chat_with_agent(request: ChatRequest):
    try:
        # Call the helper function to get both the answer and the reasoning
        final_answer, reasoning_steps = get_agent_response(request.message)
        
        # Return BOTH the response and the reasoning to React as JSON
        return {
            "response": final_answer,
            "reasoning": reasoning_steps
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# A simple health check endpoint
@app.get("/")
async def root():
    return {"status": "Agent API is running perfectly!"}