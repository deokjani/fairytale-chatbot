import streamlit as st
import requests
import json
import time
import asyncio
from typing import Generator
import sseclient
import urllib.parse

# Page configuration
st.set_page_config(
    page_title="AI Book Spielraum v2",
    page_icon="Book",
    layout="wide"
)

# API Base URL - 실제 서버 주소로 변경 필요
API_BASE_URL = "http://121.78.147.172:7134/v2/book"

# Helper functions
def get_book_list():
    """책 목록 가져오기"""
    try:
        response = requests.get(f"{API_BASE_URL}/list")
        if response.status_code == 200:
            return response.json()
        return []
    except:
        return []

def get_characters(book_id: str):
    """캐릭터 목록 가져오기"""
    try:
        response = requests.get(f"{API_BASE_URL}/character", params={"book_id": book_id})
        if response.status_code == 200:
            return response.json()
        return []
    except:
        return []

def stream_response(endpoint: str, data: dict) -> Generator:
    """SSE 스트림 응답 처리"""
    headers = {
        'accept': 'application/json',
        'Content-Type': 'application/x-www-form-urlencoded',
    }
    
    # Form data encoding
    encoded_data = urllib.parse.urlencode(data)
    
    response = requests.post(
        f"{API_BASE_URL}/{endpoint}",
        headers=headers,
        data=encoded_data,
        stream=True
    )
    
    client = sseclient.SSEClient(response)
    
    for event in client.events():
        if event.data.startswith("content="):
            content = event.data[8:]  # Remove "content=" prefix
            
            # Extract session_id if present
            if "<session_id>=" in content:
                parts = content.split("<session_id>=")
                if len(parts) > 1:
                    session_parts = parts[1].split("<")
                    st.session_state.session_id = session_parts[0]
                    content = parts[0]  # Only yield the content part
            
            # Extract CEFR level if present
            if "<CEFR>=" in content:
                parts = content.split("<CEFR>=")
                if len(parts) > 1:
                    cefr_level = parts[1].strip()
                    st.session_state.last_cefr = cefr_level
                    content = parts[0]  # Only yield the content part
                    if content.strip():  # Only yield if there's actual content
                        yield content
            else:
                yield content

# Title
st.title("AI Book Spielraum v2")
st.markdown("**Features:** BERT CEFR evaluation, Bad words filtering, Natural conversation")

# Sidebar
with st.sidebar:
    st.header("Settings")
    
    # Mode selection
    mode = st.radio("Select Mode", ["Talking", "Quiz"])
    
    # Book selection
    available_books = get_book_list()
    if available_books:
        book_id = st.selectbox("Select Book", available_books)
    else:
        book_id = st.text_input("Enter Book ID", value="ACS001")
    
    # Character selection for Talking mode
    character = None
    if mode == "Talking" and book_id:
        characters = get_characters(book_id)
        if characters:
            character = st.selectbox("Select Character", characters)
        else:
            character = st.text_input("Enter Character Name", value="main")
    
    # Session controls
    if st.button("New Session"):
        st.session_state.clear()
        st.rerun()
    
    # Show current session info
    if "session_id" in st.session_state and st.session_state.session_id:
        st.info(f"Session ID: {st.session_state.session_id}")
    
    if "last_cefr" in st.session_state:
        st.success(f"Last CEFR Level: {st.session_state.last_cefr}")
    
    st.markdown("---")
    st.markdown("### About v2")
    st.markdown("""
    - BERT-based CEFR evaluation
    - Bad words filtering
    - Simplified quiz 
    - Real-time level detection
    """)

# Initialize session state
if "messages" not in st.session_state:
    st.session_state.messages = []
if "session_id" not in st.session_state:
    st.session_state.session_id = ""
if "initial_greeting_sent" not in st.session_state:
    st.session_state.initial_greeting_sent = False

# Display chat messages
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

# Auto-send initial greeting for Talking mode
if mode == "Talking" and book_id and character and not st.session_state.initial_greeting_sent:
    st.session_state.initial_greeting_sent = True
    
    # Display initial greeting
    with st.chat_message("assistant"):
        message_placeholder = st.empty()
        full_response = ""
        
        data = {
            "book_id": book_id,
            "character": character,
            "session_id": st.session_state.session_id,
            "query": "",
            "final": False,
            "initial": True
        }
        
        for chunk in stream_response("talking", data):
            full_response += chunk
            message_placeholder.markdown(full_response + "|")
        
        message_placeholder.markdown(full_response)
        st.session_state.messages.append({"role": "assistant", "content": full_response})

# Chat input
if prompt := st.chat_input("Type your message here..."):
    # Add user message to chat history
    st.session_state.messages.append({"role": "user", "content": prompt})
    
    # Display user message
    with st.chat_message("user"):
        st.markdown(prompt)
    
    # Get AI response
    with st.chat_message("assistant"):
        message_placeholder = st.empty()
        full_response = ""
        
        if mode == "Talking":
            data = {
                "book_id": book_id,
                "character": character,
                "session_id": st.session_state.session_id,
                "query": prompt,
                "final": False,
                "initial": False
            }
            endpoint = "talking"
        else:  # Quiz mode
            data = {
                "book_id": book_id,
                "session_id": st.session_state.session_id,
                "query": prompt,
                "final": False
            }
            endpoint = "quiz"
        
        for chunk in stream_response(endpoint, data):
            full_response += chunk
            message_placeholder.markdown(full_response + "|")
        
        message_placeholder.markdown(full_response)
        st.session_state.messages.append({"role": "assistant", "content": full_response})

# Final evaluation button
if st.sidebar.button("Get CEFR Evaluation", disabled=(mode != "Talking")):
    with st.chat_message("assistant"):
        message_placeholder = st.empty()
        
        data = {
            "book_id": book_id,
            "character": character,
            "session_id": st.session_state.session_id,
            "query": "final evaluation",
            "final": True,
            "initial": False
        }
        
        cefr_level = ""
        for chunk in stream_response("talking", data):
            cefr_level += chunk
            message_placeholder.markdown(f"Your CEFR Level: {cefr_level}")
        
        st.session_state.messages.append({"role": "assistant", "content": f"Your CEFR Level: {cefr_level}"})

# Quiz score button
if st.sidebar.button("Get Quiz Score", disabled=(mode != "Quiz")):
    with st.chat_message("assistant"):
        message_placeholder = st.empty()
        
        data = {
            "book_id": book_id,
            "session_id": st.session_state.session_id,
            "query": "final score",
            "final": True
        }
        
        score = ""
        for chunk in stream_response("quiz", data):
            score += chunk
            message_placeholder.markdown(f"Your Quiz Score: {score} points")
        
        st.session_state.messages.append({"role": "assistant", "content": f"Your Quiz Score: {score} points"})
