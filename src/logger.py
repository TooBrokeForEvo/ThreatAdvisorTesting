import streamlit as st # type: ignore
import time

def log(message, level="info"):
    """
    Global logging function. 
    Only displays if Developer Mode is toggled on in the sidebar.

    Cant log the logger 
    """
    #Check if the user enabled debug mode in the UI
    if st.session_state.get("global_debug", False):
        timestamp = time.strftime("%H:%M:%S")
        
        if level == "error":
            st.error(f"[{timestamp}] {message}")
        elif level == "warning":
            st.warning(f"[{timestamp}] {message}")
        elif level == "success":
            st.success(f"[{timestamp}] {message}")
        else:
            st.caption(f"[{timestamp}] DEBUG: {message}")