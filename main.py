# main.py
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware # Required for Streamlit to talk to FastAPI
from pydantic import BaseModel
import uvicorn
from datetime import datetime, timedelta
from typing import Optional, List, Dict
import os
from dotenv import load_dotenv

# Import our calendar utility functions
from calendar_utils import check_calendar_availability, create_calendar_event, CALENDAR_SERVICE

# Import the agent invocation function
from agent import invoke_agent

# Load environment variables from .env file
load_dotenv()

app = FastAPI(
    title="TailorTalk Calendar Agent Backend",
    description="Backend for the conversational AI agent for Google Calendar bookings.",
    version="0.1.0",
)

# --- CORS Middleware ---
# This is essential for allowing your Streamlit frontend (running on a different port/origin)
# to make requests to your FastAPI backend.
origins = [
    "http://localhost",
    "http://localhost:8501", # Default Streamlit port
    # Add your deployed Streamlit URL here when deploying
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"], # Allows all HTTP methods (GET, POST, etc.)
    allow_headers=["*"], # Allows all headers
)


# Retrieve Google Calendar ID from environment variables
GOOGLE_CALENDAR_ID = os.getenv('GOOGLE_CALENDAR_ID')
if not GOOGLE_CALENDAR_ID:
    raise ValueError("GOOGLE_CALENDAR_ID environment variable not set. Please set it in your .env file.")

# --- Pydantic Models for Request Body Validation ---
class AvailabilityCheckRequest(BaseModel):
    start_time: str # ISO format, e.g., "2025-07-07T09:00:00"
    end_time: str   # ISO format, e.g., "2025-07-07T17:00:00"
    timezone: str = 'Asia/Kolkata' # Default timezone

# Removed Attendee model and attendees from CreateEventRequest as per previous fix
class CreateEventRequest(BaseModel):
    summary: str
    start_time: str # ISO format
    end_time: str   # ISO format
    description: Optional[str] = None
    location: Optional[str] = None
    timezone: str = 'Asia/Kolkata' # Default timezone

# New Pydantic model for chat interactions
class ChatRequest(BaseModel):
    user_message: str
    # chat_history will be a list of dictionaries like [{"role": "user", "content": "..."}, {"role": "assistant", "content": "..."}]
    chat_history: List[Dict[str, str]] = []

# --- Root Endpoint ---
@app.get("/")
async def read_root():
    """
    Root endpoint for the TailorTalk Calendar Agent backend.
    Returns a simple greeting to confirm the server is running.
    """
    return {"message": "Hello TailorTalk! Backend is running."}

# --- Endpoint: Check Calendar Availability ---
@app.post("/check-availability")
async def get_availability(request: AvailabilityCheckRequest):
    """
    Checks the free/busy status of the configured Google Calendar
    for a given time range.
    """
    if not CALENDAR_SERVICE:
        raise HTTPException(
            status_code=503,
            detail="Google Calendar service not initialized. Check server logs for details (e.g., missing service account key)."
        )

    print(f"Checking availability from {request.start_time} to {request.end_time} in {request.timezone}")
    result = check_calendar_availability(
        calendar_id=GOOGLE_CALENDAR_ID,
        start_time_str=request.start_time,
        end_time_str=request.end_time,
        timezone=request.timezone
    )

    if result["error"]:
        raise HTTPException(status_code=500, detail=result["error"])
    return {"busy_slots": result["busy_slots"]}

# --- Endpoint: Create Calendar Event ---
@app.post("/create-event")
async def create_event(request: CreateEventRequest):
    """
    Creates a new event on the configured Google Calendar.
    """
    if not CALENDAR_SERVICE:
        raise HTTPException(
            status_code=503,
            detail="Google Calendar service not initialized. Check server logs for details (e.g., missing service account key)."
        )

    print(f"Attempting to create event: {request.summary} from {request.start_time} to {request.end_time}")

    # Removed attendees_data conversion and passing to create_calendar_event as per previous fix
    result = create_calendar_event(
        calendar_id=GOOGLE_CALENDAR_ID,
        summary=request.summary,
        start_time_str=request.start_time,
        end_time_str=request.end_time,
        description=request.description,
        location=request.location,
        # attendees=attendees_data, # This line was commented/removed
        timezone=request.timezone
    )

    if result["error"]:
        raise HTTPException(status_code=500, detail=result["error"])
    return {
        "message": "Event created successfully!",
        "event_id": result["event_id"],
        "html_link": result["html_link"]
    }

# --- NEW Endpoint: Handle Chat Messages ---
@app.post("/chat")
async def chat_with_agent(request: ChatRequest):
    """
    Receives a user message and chat history, processes it with the AI agent,
    and returns the agent's response.
    """
    print(f"Received message from frontend: {request.user_message}")
    print(f"Chat History: {request.chat_history}")

    try:
        # Invoke the Langchain agent
        agent_response = invoke_agent(
            user_message=request.user_message,
            chat_history=request.chat_history
        )
        print(f"Agent response: {agent_response}")
        return {"response": agent_response}
    except Exception as e:
        print(f"Error processing chat message: {e}")
        raise HTTPException(status_code=500, detail=f"Error processing message: {e}")


if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)