# tools.py
import requests
from typing import List, Dict, Optional
from datetime import datetime, timedelta
import pytz

# Assuming your FastAPI backend runs on localhost:8000
# In deployment, this will be your deployed backend URL
FASTAPI_BASE_URL = "http://localhost:8000"

# --- Tool 1: Check Calendar Availability ---
def check_calendar_availability_tool(
    start_time_str: str,
    end_time_str: str,
    timezone: str = 'Asia/Kolkata' # Default timezone
) -> Dict:
    """
    Checks the free/busy status of the Google Calendar for a specified time range.
    This tool requires exact start and end times in ISO format (e.g., "YYYY-MM-DDTHH:MM:SS").

    Args:
        start_time_str (str): The start datetime for the availability check in ISO format (e.g., "2025-07-07T09:00:00").
        end_time_str (str): The end datetime for the availability check in ISO format (e.g., "2025-07-07T17:00:00").
        timezone (str): The timezone for the request, e.g., 'America/New_York', 'Asia/Kolkata'.
                        Defaults to 'Asia/Kolkata' (Pune time).

    Returns:
        Dict: A dictionary containing 'busy_slots' (list of dicts with start/end times) or 'error'.
    """
    print(f"Tool Call: check_calendar_availability_tool(start={start_time_str}, end={end_time_str}, tz={timezone})")
    try:
        # Validate input date format (basic check)
        try:
            datetime.fromisoformat(start_time_str)
            datetime.fromisoformat(end_time_str)
        except ValueError:
            return {"error": "Invalid time format. Please provide times in ISO format (YYYY-MM-DDTHH:MM:SS)."}

        payload = {
            "start_time": start_time_str,
            "end_time": end_time_str,
            "timezone": timezone
        }
        response = requests.post(f"{FASTAPI_BASE_URL}/check-availability", json=payload)
        response.raise_for_status() # Raise an exception for HTTP errors (4xx or 5xx)
        return response.json()
    except requests.exceptions.RequestException as e:
        print(f"Error calling check-availability API: {e}")
        return {"error": f"Failed to check availability: {e}"}
    except Exception as e:
        print(f"An unexpected error occurred in check_calendar_availability_tool: {e}")
        return {"error": f"An unexpected error occurred: {e}"}

# --- Tool 2: Create Calendar Event ---
def create_calendar_event_tool(
    summary: str,
    start_time_str: str,
    end_time_str: str,
    description: Optional[str] = None,
    location: Optional[str] = None,
    timezone: str = 'Asia/Kolkata' # Default timezone
) -> Dict:
    """
    Creates a new event on the Google Calendar.
    This tool requires the event summary, exact start and end times in ISO format.

    Args:
        summary (str): The title/summary of the event.
        start_time_str (str): The start datetime for the event in ISO format (e.g., "2025-07-07T10:00:00").
        end_time_str (str): The end datetime for the event in ISO format (e.g., "2025-07-07T11:00:00").
        description (str, optional): A detailed description for the event.
        location (str, optional): The physical or virtual location of the event.
        timezone (str): The timezone for the event, e.g., 'America/New_York', 'Asia/Kolkata'.
                        Defaults to 'Asia/Kolkata' (Pune time).

    Returns:
        Dict: A dictionary containing 'event_id', 'html_link', or 'error'.
    """
    print(f"Tool Call: create_calendar_event_tool(summary='{summary}', start={start_time_str}, end={end_time_str}, tz={timezone})")
    try:
        # Validate input date format (basic check)
        try:
            datetime.fromisoformat(start_time_str)
            datetime.fromisoformat(end_time_str)
        except ValueError:
            return {"error": "Invalid time format. Please provide times in ISO format (YYYY-MM-DDTHH:MM:SS)."}

        payload = {
            "summary": summary,
            "start_time": start_time_str,
            "end_time": end_time_str,
            "description": description,
            "location": location,
            # "attendees": [{"email": "attendee@example.com"}] # Removed as per previous step
            "timezone": timezone
        }
        response = requests.post(f"{FASTAPI_BASE_URL}/create-event", json=payload)
        response.raise_for_status() # Raise an exception for HTTP errors (4xx or 5xx)
        return response.json()
    except requests.exceptions.RequestException as e:
        print(f"Error calling create-event API: {e}")
        return {"error": f"Failed to create event: {e}"}
    except Exception as e:
        print(f"An unexpected error occurred in create_calendar_event_tool: {e}")
        return {"error": f"An unexpected error occurred: {e}"}


# Example of how Langchain defines tools from functions
# We will use this in the next step when we create the agent
from langchain_core.tools import tool

@tool
def check_calendar_availability_langchain(
    start_time_str: str,
    end_time_str: str,
    timezone: str = 'Asia/Kolkata'
) -> Dict:
    """
    Checks the free/busy status of the Google Calendar for a specified time range.
    This tool requires exact start and end times in ISO format (e.g., "YYYY-MM-DDTHH:MM:SS").
    The user wants to know if a specific time is free for an appointment.

    Args:
        start_time_str (str): The start datetime for the availability check in ISO format (e.g., "2025-07-07T09:00:00").
        end_time_str (str): The end datetime for the availability check in ISO format (e.g., "2025-07-07T17:00:00").
        timezone (str): The timezone for the request, e.g., 'America/New_York', 'Asia/Kolkata'.
                        Defaults to 'Asia/Kolkata' (Pune time).
    """
    return check_calendar_availability_tool(start_time_str, end_time_str, timezone)

@tool
def create_calendar_event_langchain(
    summary: str,
    start_time_str: str,
    end_time_str: str,
    description: Optional[str] = None,
    location: Optional[str] = None,
    timezone: str = 'Asia/Kolkata'
) -> Dict:
    """
    Creates a new event (appointment) on the Google Calendar.
    This tool is used to finalize a booking after the user has confirmed a time slot.
    It requires the event summary, and exact start and end times in ISO format.

    Args:
        summary (str): The title/summary of the event, e.g., "Haircut Appointment", "Meeting with John".
        start_time_str (str): The start datetime for the event in ISO format (e.g., "2025-07-07T10:00:00").
        end_time_str (str): The end datetime for the event in ISO format (e.g., "2025-07-07T11:00:00").
        description (str, optional): A detailed description for the event.
        location (str, optional): The physical or virtual location of the event.
        timezone (str): The timezone for the event, e.g., 'America/New_York', 'Asia/Kolkata'.
                        Defaults to 'Asia/Kolkata' (Pune time).
    """
    return create_calendar_event_tool(summary, start_time_str, end_time_str, description, location, timezone)


# List of all tools available to the agent
ALL_TOOLS = [
    check_calendar_availability_langchain,
    create_calendar_event_langchain
]

# You can test the tools directly here if the FastAPI server is running
if __name__ == "__main__":
    print("--- Testing tools.py (ensure FastAPI backend is running on http://localhost:8000) ---")
    # Ensure FastAPI is running in another terminal before running this.

    # Test check_calendar_availability_tool
    print("\nTesting check_calendar_availability_tool...")
    # Check a timeframe where you know you have an event or expect to be free
    current_date = datetime.now(pytz.timezone('Asia/Kolkata'))
    next_day = current_date + timedelta(days=1)
    test_start_time = next_day.replace(hour=9, minute=0, second=0, microsecond=0).isoformat()
    test_end_time = next_day.replace(hour=17, minute=0, second=0, microsecond=0).isoformat()

    availability_result = check_calendar_availability_tool(
        start_time_str=test_start_time,
        end_time_str=test_end_time,
        timezone='Asia/Kolkata'
    )
    print("Availability Result:", availability_result)

    # Test create_calendar_event_tool
    print("\nTesting create_calendar_event_tool...")
    event_start = next_day.replace(hour=10, minute=30, second=0, microsecond=0).isoformat()
    event_end = next_day.replace(hour=11, minute=0, second=0, microsecond=0).isoformat()
    create_result = create_calendar_event_tool(
        summary="Langchain Tool Test Event",
        start_time_str=event_start,
        end_time_str=event_end,
        description="Created via Langchain tool test script.",
        location="Virtual Meeting",
        timezone='Asia/Kolkata'
    )
    print("Create Event Result:", create_result)
    if create_result and not create_result.get("error"):
        print("Check your calendar for 'Langchain Tool Test Event' created for tomorrow.")