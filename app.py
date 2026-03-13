import streamlit as st # type: ignore
import os
import json
import time
from src.parser import parse_nmap_xml
from src.ai_engine import ThreatAI
from src.utils_nmap import run_live_scan
from src.utils_osquery import load_queries, get_current_os_key, run_selected_osquery_scans, osquery_json_path
from src.logger import log

st.set_page_config(page_title="ThreatAdvisor", layout="wide")

#Initalization 
threat_ai = ThreatAI()

#Session state init 
if "global_debug" not in st.session_state:
    st.session_state.global_debug = True
    log("Initialized global debug mode in session state.", level="info")
if "messages" not in st.session_state:
    st.session_state.messages = []
    log("Initialized messages in session state.", level="info")
if "current_data" not in st.session_state:
    st.session_state.current_data = {"nmap": None, "host": None}
    log("Initialized current_data in session state.", level="info")

#Sidebar system control
with st.sidebar:
    st.title("System Controls")

    # The Model Selector Button
    selected_model = st.selectbox(
        "Intelligence Model",
        ["gemini-2.5-flash", "gpt-5-mini", "gpt-4.1-nano"],
        help="Select the AI engine for forensic analysis."
    )

    st.session_state.global_debug = st.toggle("Developer Debug Mode", value=st.session_state.global_debug)
    log(f"Global debug mode set to: {st.session_state.global_debug}", level="debug")

    st.divider()
    st.info("Upload an existing scan or initiate a live audit.")
    uploaded_file = st.file_uploader("Upload Nmap XML Scan", type=["xml"])

    if st.button("Reset Session"):
        st.session_state.messages = []
        st.session_state.current_data = {"nmap": None, "host": None}
        st.rerun()

#Main Panel
st.title("Integrated Security Advisor")

st.subheader("Audit Configuration")
audit_layers = st.multiselect(
    "Select Intelligence Layers",
    ["Network Discovery (Nmap)", "Host Telemetry (Osquery)"],
    default=["Network Discovery (Nmap)"]
)

col1, col2 = st.columns(2)

with col1:
    if "Network Discovery (Nmap)" in audit_layers:
        st.markdown("### Network Layer")
        target_ip = st.text_input("Target IP Address", placeholder="e.g. 127.0.0.1")
        scan_mode = st.selectbox(
            "Scan Type",
            ["Service Version Detection (-sV)", "Stealth SYN Scan (-sS)", "Quick Scan (-F)"],
            index=0
        )
        scan_args = {"Service Version Detection (-sV)": "-sV", "Stealth SYN Scan (-sS)": "-sS", "Quick Scan (-F)": "-F"}[scan_mode]
    else:
        target_ip = None
     
with col2:
    if "Host Telemetry (Osquery)" in audit_layers:
        st.markdown("### Host Layer")
        all_data = load_queries(osquery_json_path)
        os_key = get_current_os_key()
        available_scan_names = [s["name"] for s in all_data[os_key]["scans"]]

        selected_os_modules = st.multiselect(
            "Select Host Audit Modules",
            options=available_scan_names,
            default=available_scan_names[:1]
        )
    else:
        selected_os_modules = []   

#The exectution  
if st.button("Initialize Security Audit"):
    st.session_state.current_data = {"nmap": None, "host": None}
    
    #Nmap
    if "Network Discovery (Nmap)" in audit_layers:
        if target_ip:
            with st.spinner(f"Scanning Network: {target_ip}..."):
                st.session_state.current_data["nmap"] = run_live_scan(target_ip, scan_args)
                log(f"Nmap scan completed for {target_ip}", level="success")
        else:
            st.error("IP Address required for Network Discovery.")

    #Osquery
    if "Host Telemetry (Osquery)" in audit_layers:
        if selected_os_modules:
            with st.spinner("Collecting Host Telemetry..."):
                st.session_state.current_data["host"] = run_selected_osquery_scans(selected_os_modules, osquery_json_path)
                log("Osquery scans completed.", level="success")
        else:
            st.warning("No Osquery modules selected.")

if any(st.session_state.current_data.values()):
        st.success("Audit Complete. Data ready for analysis.")

#File upload logic
if uploaded_file is not None and st.session_state.current_data["nmap"] is None:
    with open("temp_scan.xml", "wb") as f:
        f.write(uploaded_file.getbuffer())
    st.session_state.current_data["nmap"] = parse_nmap_xml("temp_scan.xml")
    st.success("File scan loaded.")

#AI Consulter chat
st.divider()
st.subheader("Security Consultation")

#Render chat history
for msg in st.session_state.messages:
    with st.chat_message(msg["role"]):
        st.markdown(msg["content"])

if prompt := st.chat_input("Ask about your findings..."):
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)

    with st.chat_message("assistant"):
        if any(st.session_state.current_data.values()):
            message_placeholder = st.empty()
            full_response = ""
            
            raw_response = threat_ai.get_explanation(st.session_state.current_data, prompt, model_name=selected_model)
            
            for chunk in raw_response.split(" "):
                full_response += chunk + " "
                time.sleep(0.04)
                message_placeholder.markdown(full_response + "▌")
            
            message_placeholder.markdown(full_response)
            st.session_state.messages.append({"role": "assistant", "content": full_response})
        else:
            st.warning("Forensic data required for analysis. Please initiate an audit.")