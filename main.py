# main.py
from fastapi import FastAPI
import uvicorn
from dotenv import load_dotenv
import os

# Load environment variables from .env file
load_dotenv()

app = FastAPI(
    title="TailorTalk Calendar Agent Backend",
    description="Backend for the conversational AI agent for Google Calendar bookings.",
    version="0.1.0",
)

@app.get("/")
async def read_root():
    """
    Root endpoint for the TailorTalk Calendar Agent backend.
    Returns a simple greeting to confirm the server is running.
    """
    return {"message": "Hello TailorTalk! Backend is running."}

# You can add more endpoints here later for calendar operations and agent interaction

if __name__ == "__main__":
    # This block is for local development using `python main.py`
    # For production, uvicorn should be run directly (e.g., `uvicorn main:app --host 0.0.0.0 --port 8000`)
    uvicorn.run(app, host="0.0.0.0", port=8000)