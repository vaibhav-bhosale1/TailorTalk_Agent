# test_gemini.py
import os
from dotenv import load_dotenv
import google.generativeai as genai

# Load environment variables from .env file
load_dotenv()

# Configure the Gemini API key
GOOGLE_API_KEY = os.getenv("GOOGLE_API_KEY")

if not GOOGLE_API_KEY:
    print("Error: GOOGLE_API_KEY environment variable not set. Please set it in your .env file.")
    exit()

genai.configure(api_key=GOOGLE_API_KEY)

try:
    # Test a simple prompt with the Gemini Pro model
    model = genai.GenerativeModel('gemini-1.5-flash')
    print("Gemini model loaded successfully. Sending a test prompt...")

    prompt = "What is the capital of France?"
    response = model.generate_content(prompt)

    print(f"\nUser: {prompt}")
    print(f"Gemini: {response.text}")

    # Test another prompt to confirm conversational ability (if applicable to model)
    prompt2 = "And what is its main river?"
    response2 = model.generate_content(prompt2) # Note: For true conversational memory, you'd use chat sessions.
                                               # This is just a basic sequential test.
    print(f"\nUser: {prompt2}")
    print(f"Gemini: {response2.text}")

except Exception as e:
    print(f"An error occurred while interacting with Gemini: {e}")
    print("Please check your GOOGLE_API_KEY and network connection.")