# agent.py

import os
from datetime import datetime
import pytz
from typing import List, Dict  # ✅ Added import

from dotenv import load_dotenv

# Langchain components
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain.agents import AgentExecutor, create_tool_calling_agent
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain_core.messages import AIMessage, HumanMessage

# Import the tools we defined
from tools import ALL_TOOLS

# Load environment variables (especially GOOGLE_API_KEY)
load_dotenv()

# --- Initialize the Gemini LLM ---
GOOGLE_API_KEY = os.getenv("GOOGLE_API_KEY")
if not GOOGLE_API_KEY:
    raise ValueError("GOOGLE_API_KEY environment variable not set. Please set it in your .env file.")

llm = ChatGoogleGenerativeAI(
    model="gemini-1.5-flash",
    temperature=0.7,
    google_api_key=GOOGLE_API_KEY
)

# --- Define the Prompt Template ---
prompt = ChatPromptTemplate.from_messages(
    [
        (
            "system",
            """
            You are TailorTalk, an AI assistant designed to help users book appointments
            on a Google Calendar. Your primary function is to understand user requests,
            check calendar availability using the 'check_calendar_availability_langchain' tool,
            and create new appointments using the 'create_calendar_event_langchain' tool.

            Here are the rules you must follow:
            1.  Be Conversational.
            2.  Clarify Ambiguity.
            3.  Confirm Details.
            4.  Suggest Availability using tools.
            5.  Use ISO Format for Tools with Asia/Kolkata timezone.
          6.  Handle Time Calculations based on the provided 'Current Date and Time' context.
                #     The default timezone for all operations should be 'Asia/Kolkata'.
            7.  Inform Success after event creation.
            8.  Handle Errors Gracefully.
            9.  Do NOT make assumptions on date/time.
            10. Appointment Summary must be confirmed.

            Current Date and Time (for context, do not explicitly state this unless relevant to query):
            {current_date_time_ist}

            Available Tools:
            - check_calendar_availability_langchain
            - create_calendar_event_langchain
            """
        ),
        MessagesPlaceholder(variable_name="chat_history"),
        ("human", "{input}"),
        MessagesPlaceholder(variable_name="agent_scratchpad"),
    ]
)

# --- Create the Langchain Agent ---
agent = create_tool_calling_agent(llm, ALL_TOOLS, prompt)

# --- Create the Agent Executor ---
agent_executor = AgentExecutor(agent=agent, tools=ALL_TOOLS, verbose=True)

# --- Function to invoke the agent (for FastAPI) ---
def invoke_agent(user_message: str, chat_history: List[Dict]) -> str:
    lc_chat_history = []
    for msg in chat_history:
        if msg["role"] == "user":
            lc_chat_history.append(HumanMessage(content=msg["content"]))
        elif msg["role"] == "assistant":
            lc_chat_history.append(AIMessage(content=msg["content"]))

    current_time_ist = datetime.now(pytz.timezone('Asia/Kolkata')).strftime(
        "%A, %B %d, %Y at %I:%M:%S %p %Z%z"
    )

    try:
        result = agent_executor.invoke(
            {
                "input": user_message,
                "chat_history": lc_chat_history,
                "current_date_time_ist": current_time_ist
            }
        )
        return result.get("output", "I'm sorry, I couldn't process that request.")
    except Exception as e:
        print(f"Error invoking agent: {e}")
        return f"I apologize, but I encountered an error: {e}. Please try again."


# --- Example Usage ---
if __name__ == "__main__":
    print("--- Testing agent.py ---")

    test_history = []

    print("\nUser: Is tomorrow afternoon free for a 1-hour appointment?")
    response = invoke_agent("Is tomorrow afternoon free for a 1-hour appointment?", test_history)
    print("Agent:", response)
    test_history.append({"role": "user", "content": "Is tomorrow afternoon free for a 1-hour appointment?"})
    test_history.append({"role": "assistant", "content": response})

    print("\nUser: Okay, what about a haircut on July 9, 2025 at 3 PM for 45 minutes?")
    response = invoke_agent("Okay, what about a haircut on July 9, 2025 at 3 PM for 45 minutes?", test_history)
    print("Agent:", response)
    test_history.append({"role": "user", "content": "Okay, what about a haircut on July 9, 2025 at 3 PM for 45 minutes?"})
    test_history.append({"role": "assistant", "content": response})

    print("\nUser: Yes, that sounds good. Please book it.")
    response = invoke_agent("Yes, that sounds good. Please book it.", test_history)
    print("Agent:", response)
    test_history.append({"role": "user", "content": "Yes, that sounds good. Please book it."})
    test_history.append({"role": "assistant", "content": response})

    print("\nUser: What's the weather like?")
    response = invoke_agent("What's the weather like?", test_history)
    print("Agent:", response)
