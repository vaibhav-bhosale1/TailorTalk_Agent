# streamlit_app.py
import streamlit as st
import requests # To make HTTP requests to our FastAPI backend

# --- Page Configuration ---
st.set_page_config(
    page_title="TailorTalk AI Agent",
    page_icon="✂️",
    layout="centered"
)

# --- Title and Description ---
st.title("✂️ TailorTalk Appointment Agent")
st.write("Hello! I'm your personal AI assistant for booking appointments.")

# --- Initialize Chat History ---
if "messages" not in st.session_state:
    st.session_state.messages = []
    # Initial greeting from the AI
    st.session_state.messages.append({"role": "assistant", "content": "How can I help you book an appointment today?"})

# --- Display Chat Messages ---
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

# --- Chat Input ---
if prompt := st.chat_input("Ask me anything about booking an appointment..."):
    # Add user message to chat history
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)

    # Here we'll eventually call our FastAPI backend
    # For now, let's just echo the message or simulate a simple response
    with st.chat_message("assistant"):
        with st.spinner("Thinking..."):
            # Simulating a response for now
            # In the next phase, this will be replaced by an actual API call
            response = f"You said: '{prompt}'. (This will be processed by the AI soon!)"
            st.markdown(response)
        st.session_state.messages.append({"role": "assistant", "content": response})

# Optional: A button to clear chat history
if st.button("Clear Chat"):
    st.session_state.messages = []
    st.session_state.messages.append({"role": "assistant", "content": "How can I help you book an appointment today?"})
    st.experimental_rerun() # Rerun to clear messages immediately