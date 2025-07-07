# main.py
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
import uvicorn
from datetime import datetime, timedelta
from typing import Optional, List
import os
from dotenv import load_dotenv

# Import our calendar utility functions
from calendar_utils import check_calendar_availability, create_calendar_event, CALENDAR_SERVICE

# Load environment variables from .env file
load_dotenv()

app = FastAPI(
    title="TailorTalk Calendar Agent Backend",
    description="Backend for the conversational AI agent for Google Calendar bookings.",
    version="0.1.0",
)

# Retrieve Google Calendar ID from environment variables
# This ID will be used for all calendar operations.
GOOGLE_CALENDAR_ID = os.getenv('GOOGLE_CALENDAR_ID')
if not GOOGLE_CALENDAR_ID:
    raise ValueError("GOOGLE_CALENDAR_ID environment variable not set. Please set it in your .env file.")

# --- Pydantic Models for Request Body Validation ---
class AvailabilityCheckRequest(BaseModel):
    start_time: str # ISO format, e.g., "2025-07-07T09:00:00"
    end_time: str   # ISO format, e.g., "2025-07-07T17:00:00"
    timezone: str = 'Asia/Kolkata' # Default timezone

class Attendee(BaseModel):
    email: str

class CreateEventRequest(BaseModel):
    summary: str
    start_time: str # ISO format
    end_time: str   # ISO format
    description: Optional[str] = None
    location: Optional[str] = None
   # attendees: Optional[List[Attendee]] = None
    timezone: str = 'Asia/Kolkata' # Default timezone

# --- Root Endpoint (already existing) ---
@app.get("/")
async def read_root():
    """
    Root endpoint for the TailorTalk Calendar Agent backend.
    Returns a simple greeting to confirm the server is running.
    """
    return {"message": "Hello TailorTalk! Backend is running."}

# --- New Endpoint: Check Calendar Availability ---
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

# --- New Endpoint: Create Calendar Event ---
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

    # Convert Pydantic Attendee objects to the dictionary format expected by googleapiclient
    #attendees_data = [a.dict() for a in request.attendees] if request.attendees else None

    result = create_calendar_event(
        calendar_id=GOOGLE_CALENDAR_ID,
        summary=request.summary,
        start_time_str=request.start_time,
        end_time_str=request.end_time,
        description=request.description,
        location=request.location,
     #   attendees=attendees_data,
        timezone=request.timezone
    )

    if result["error"]:
        raise HTTPException(status_code=500, detail=result["error"])
    return {
        "message": "Event created successfully!",
        "event_id": result["event_id"],
        "html_link": result["html_link"]
    }

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)