import streamlit as st
import asyncio
import nest_asyncio
import subprocess
import sys
import time
import httpx

nest_asyncio.apply()

# ─── Auto-start MCP servers ───────────────────────────────────────────────────

def is_server_up(port: int) -> bool:
    """Check if a server is already listening on the given port."""
    try:
        import socket
        with socket.create_connection(("localhost", port), timeout=1):
            return True
    except OSError:
        return False

def start_servers():
    """Start both MCP servers as background subprocesses (only once)."""
    if "servers_started" not in st.session_state:
        st.session_state.servers_started = False

    if st.session_state.servers_started:
        return  # already launched in this session

    procs = []

    if not is_server_up(8000):
        p1 = subprocess.Popen(
            [sys.executable, "season_mcp_server.py"],
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL,
        )
        procs.append(("Season Server :8000", p1))

    if not is_server_up(8001):
        p2 = subprocess.Popen(
            [sys.executable, "travel_mcp_server.py"],
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL,
        )
        procs.append(("Travel Server :8001", p2))

    if procs:
        # Give servers a moment to boot
        with st.spinner("⏳ Starting MCP servers..."):
            time.sleep(3)

    st.session_state.servers_started = True

# ─── Streamlit UI ─────────────────────────────────────────────────────────────

st.set_page_config(page_title="MCP Travel Planner", layout="centered")
st.title("🌍 AI Travel Planner (MCP)")
st.markdown("Ask: *Suggest a place to travel this month*")

# Start servers before anything else
start_servers()

from main import AIService

if "service" not in st.session_state:
    st.session_state.service = AIService()

if "messages" not in st.session_state:
    st.session_state.messages = []

user_input = st.chat_input("Ask something...")

if user_input:
    st.session_state.messages.append(("user", user_input))

    loop = asyncio.get_event_loop()

    with st.spinner("Thinking... 🤖"):
        response = loop.run_until_complete(
            st.session_state.service.process_query(user_input)
        )

    st.session_state.messages.append(("assistant", response))

for role, msg in st.session_state.messages:
    with st.chat_message(role):
        st.markdown(msg)