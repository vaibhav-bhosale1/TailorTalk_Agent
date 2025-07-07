# calendar_utils.py
from google.oauth2 import service_account
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError
from datetime import datetime, timedelta
import os
from dotenv import load_dotenv
import pytz # For handling timezones

# Load environment variables (especially GOOGLE_SERVICE_ACCOUNT_KEY_PATH)
load_dotenv()

# --- Configuration ---
# Scopes define the level of access your application has to a user's data.
# For creating and managing events, calendar.events is sufficient.
# For checking free/busy, calendar.readonly or calendar are fine.
SCOPES = ['https://www.googleapis.com/auth/calendar.events', 'https://www.googleapis.com/auth/calendar.readonly']

# Get the path to the service account key from environment variable
SERVICE_ACCOUNT_FILE = os.getenv('GOOGLE_SERVICE_ACCOUNT_KEY_PATH')
CALENDAR_ID = os.getenv('GOOGLE_CALENDAR_ID', 'primary')  # Default to 'primary' if not set

if not SERVICE_ACCOUNT_FILE or not os.path.exists(SERVICE_ACCOUNT_FILE):
    raise FileNotFoundError(
        f"Service account key file not found at {SERVICE_ACCOUNT_FILE}. "
        "Please ensure GOOGLE_SERVICE_ACCOUNT_KEY_PATH is set correctly in your .env file "
        "and the file exists."
    )

# --- Google Calendar Service Initialization ---
def get_calendar_service():
    """
    Initializes and returns an authorized Google Calendar API service object
    using the service account credentials.
    """
    try:
        # Create credentials object from the service account key file
        credentials = service_account.Credentials.from_service_account_file(
            SERVICE_ACCOUNT_FILE, scopes=SCOPES
        )
        # Build the Google Calendar API service
        service = build('calendar', 'v3', credentials=credentials)
        print("Google Calendar service initialized successfully.")
        return service
    except Exception as e:
        print(f"Error initializing Google Calendar service: {e}")
        raise

# Initialize service globally or pass it around
# For simplicity, we'll initialize it here. In a larger app, you might
# want to manage this more explicitly (e.g., dependency injection in FastAPI).
try:
    CALENDAR_SERVICE = get_calendar_service()
except FileNotFoundError as e:
    print(f"FATAL ERROR: {e}")
    CALENDAR_SERVICE = None # Service won't be available if key is missing

# --- Utility Functions for Calendar Operations ---

def check_calendar_availability(
    calendar_id: str,
    start_time_str: str,
    end_time_str: str,
    timezone: str = 'Asia/Kolkata' # Default to Indian Standard Time as requested location is Pune
) -> dict:
    """
    Checks the free/busy schedule for a given calendar within a specified time range.

    Args:
        calendar_id (str): The ID of the calendar to check (e.g., 'primary' or the service account's calendar ID).
        start_time_str (str): Start time in ISO format (e.g., "2025-07-07T09:00:00").
        end_time_str (str): End time in ISO format (e.g., "2025-07-07T17:00:00").
        timezone (str): The timezone for the request, e.g., 'America/New_York', 'Asia/Kolkata'.

    Returns:
        dict: A dictionary containing 'busy_slots' (list of dicts with start/end times)
              and 'error' (if any).
    """
    if not CALENDAR_SERVICE:
        return {"busy_slots": [], "error": "Calendar service not initialized. Check service account key path."}

    try:
        # Convert string times to timezone-aware datetime objects
        # Ensure the input strings are parsed correctly, assuming they are naive for now
        # and we'll apply the target timezone
        start_dt = datetime.fromisoformat(start_time_str).astimezone(pytz.timezone(timezone))
        end_dt = datetime.fromisoformat(end_time_str).astimezone(pytz.timezone(timezone))

        body = {
            "timeMin": start_dt.isoformat(),
            "timeMax": end_dt.isoformat(),
            "timeZone": timezone,
            "items": [{"id": calendar_id}]
        }

        events_result = CALENDAR_SERVICE.freebusy().query(body=body).execute()
        calendars = events_result.get('calendars', {})
        busy_slots = calendars.get(calendar_id, {}).get('busy', [])

        # Format busy slots for easier consumption
        formatted_busy_slots = []
        for slot in busy_slots:
            # Parse to datetime, then convert to specified timezone for consistent output
            slot_start = datetime.fromisoformat(slot['start'].replace('Z', '+00:00')).astimezone(pytz.timezone(timezone))
            slot_end = datetime.fromisoformat(slot['end'].replace('Z', '+00:00')).astimezone(pytz.timezone(timezone))
            formatted_busy_slots.append({
                "start": slot_start.isoformat(),
                "end": slot_end.isoformat()
            })
        return {"busy_slots": formatted_busy_slots, "error": None}

    except HttpError as error:
        print(f'An HTTP error occurred: {error}')
        return {"busy_slots": [], "error": f"Google Calendar API error: {error.resp.status} - {error.content.decode()}"}
    except Exception as e:
        print(f'An unexpected error occurred during availability check: {e}')
        return {"busy_slots": [], "error": f"An unexpected error occurred: {e}"}


def create_calendar_event(
    calendar_id: str,
    summary: str,
    start_time_str: str,
    end_time_str: str,
    description: str = '',
    location: str = '',
    attendees: list = None,
    timezone: str = 'Asia/Kolkata' # Default to Indian Standard Time
) -> dict:
    """
    Creates a new event on the specified Google Calendar.

    Args:
        calendar_id (str): The ID of the calendar to create the event on.
        summary (str): The title of the event.
        start_time_str (str): Start time in ISO format (e.g., "2025-07-07T10:00:00").
        end_time_str (str): End time in ISO format (e.g., "2025-07-07T11:00:00").
        description (str, optional): A description for the event. Defaults to ''.
        location (str, optional): The location of the event. Defaults to ''.
        attendees (list, optional): List of dictionaries for attendees, e.g.,
                                    [{'email': 'attendee@example.com'}]. Defaults to None.
        timezone (str): The timezone for the event, e.g., 'America/New_York', 'Asia/Kolkata'.

    Returns:
        dict: A dictionary containing 'event_id', 'html_link', and 'error' (if any).
    """
    if not CALENDAR_SERVICE:
        return {"event_id": None, "html_link": None, "error": "Calendar service not initialized. Check service account key path."}

    try:
        # Ensure attendees is a list, even if None
        if attendees is None:
            attendees = []

        # Convert string times to timezone-aware datetime objects
        start_dt = datetime.fromisoformat(start_time_str).astimezone(pytz.timezone(timezone))
        end_dt = datetime.fromisoformat(end_time_str).astimezone(pytz.timezone(timezone))

        event = {
            'summary': summary,
            'description': description,
            'location': location,
            'start': {
                'dateTime': start_dt.isoformat(),
                'timeZone': timezone,
            },
            'end': {
                'dateTime': end_dt.isoformat(),
                'timeZone': timezone,
            },
            'attendees': attendees,
            'reminders': {
                'useDefault': False,
                'overrides': [
                    {'method': 'email', 'minutes': 24 * 60},  # 24 hours prior
                    {'method': 'popup', 'minutes': 10},     # 10 minutes prior
                ],
            },
        }

        created_event = CALENDAR_SERVICE.events().insert(calendarId=calendar_id, body=event).execute()
        print(f"Event created: {created_event.get('htmlLink')}")
        return {
            "event_id": created_event.get('id'),
            "html_link": created_event.get('htmlLink'),
            "error": None
        }

    except HttpError as error:
        print(f'An HTTP error occurred: {error}')
        return {"event_id": None, "html_link": None, "error": f"Google Calendar API error: {error.resp.status} - {error.content.decode()}"}
    except Exception as e:
        print(f'An unexpected error occurred during event creation: {e}')
        return {"event_id": None, "html_link": None, "error": f"An unexpected error occurred: {e}"}

# Example Usage (for testing locally, can be removed later)
if __name__ == '__main__':
    # --- IMPORTANT: Replace with your actual calendar ID ---
    # For a service account, you typically share *your* calendar with the service account.
    # So, CALENDAR_ID will be your primary calendar email (e.g., your_email@gmail.com)
    # OR the ID of a specific test calendar you created and shared.
    CALENDAR_ID = CALENDAR_ID # <--- REPLACE THIS WITH YOUR CALENDAR ID

    if CALENDAR_SERVICE:
        print(f"\n--- Testing Calendar Utility Functions with Calendar ID: {CALENDAR_ID} ---")

        # Test Availability Check for the current date (Monday, July 7, 2025)
        print("\n--- Checking Availability (Monday, July 7, 2025, 9 AM - 5 PM IST) ---")
        current_date_str = "2025-07-07"
        start_test_time = f"{current_date_str}T09:00:00"
        end_test_time = f"{current_date_str}T17:00:00"
        availability_result = check_calendar_availability(
            calendar_id=CALENDAR_ID,
            start_time_str=start_test_time,
            end_time_str=end_test_time,
            timezone='Asia/Kolkata'
        )
        if availability_result["error"]:
            print(f"Availability Check Error: {availability_result['error']}")
        else:
            print("Busy Slots:")
            for slot in availability_result["busy_slots"]:
                print(f"  - Start: {slot['start']}, End: {slot['end']}")
            if not availability_result["busy_slots"]:
                print("  No busy slots found in the specified range.")


        # Test Event Creation
        print("\n--- Creating a Test Event ---")
        event_summary = "TailorTalk Test Appointment"
        event_description = "This is a test appointment created by TailorTalk AI Agent."
        # Set a time that is likely to be free, e.g., 1 PM to 2 PM on current date
        event_start_time = f"{current_date_str}T13:00:00"
        event_end_time = f"{current_date_str}T14:00:00"

        create_result = create_calendar_event(
            calendar_id=CALENDAR_ID,
            summary=event_summary,
            start_time_str=event_start_time,
            end_time_str=event_end_time,
            description=event_description,
            timezone='Asia/Kolkata'
        )
        if create_result["error"]:
            print(f"Event Creation Error: {create_result['error']}")
        else:
            print(f"Test Event Created! ID: {create_result['event_id']}, Link: {create_result['html_link']}")
            print(f"Please check your Google Calendar for '{event_summary}' at {event_start_time} IST.")
            # You can also add a small delay and then try to delete the event for cleanup
            # Or manually delete it after testing

    else:
        print("Skipping calendar utility tests because service was not initialized.")