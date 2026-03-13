import subprocess
import json
import os
import platform
from src.logger import log
import shutil
import streamlit as st # type: ignore

#Queries JSON file path. Set as global variable for easy access across functions.
global osquery_json_path 
osquery_json_path = "src/queries.json"

def get_osquery_path():
    """
    Locates the osqueryi dynamically across differnt platforms and installation methods.
    """
    path = shutil.which("osqueryi")
    if path:
        log(f"Found osqueryi at: {path}", level="info")
        return path
    fallbacks = [
        "/usr/local/bin/osqueryi", 
        "/opt/homebrew/bin/osqueryi", 
        "/bin/osqueryi",
        "C:\\Program Files\\osquery\\osqueryi.exe"#for windows. 
    ]
    for f in fallbacks:
        if os.path.exists(f):
            log(f"Found osqueryi at: {f}", level="info")
            return f
        
    return "osqueryi"    

def load_queries(osquery_json_path):
    """
    Loads osquery queries from a JSON file. Allows for easy managment and addition/removal of queries. 
    """
    log(f"Attempting to load queries from: {osquery_json_path}")
    try:
        if not os.path.exists(osquery_json_path):
            log(f"IO Error: {osquery_json_path} not found", level="error")
            return None
        with open(osquery_json_path, "r") as f:
            log("Queries loaded successfully.", level="success")
            return json.load(f)
    except json.JSONDecodeError as e:
        log(f"JSON Syntax Error in {osquery_json_path}: {str(e)}", level="error")
        return None 

def get_current_os_key():
    """Maps platform.system() to JSON keys."""
    os_map = {
        "Windows": "windows",
        "Darwin": "macos",
        "Linux": "linux"
        }
    os_name = platform.system()
    key = os_map.get(os_name, "unknown")
    log(f"Detected OS: {os_name} (mapped to key: {key})", level="info")
    return key

    
def run_selected_osquery_scans(selected_names, osquery_json_path):
    """
    Exectues only the user-selected scans from the JSON file containing the queries. 
    selected_names: a list of strings e.g [installed_apps]

    The 3-Step Execution Pipeline:
    1. Detect OS
    2. Load and Filter for OS section
    3. Execute only the user-selected scans
    """

    if "osquery_cache" not in st.session_state:
        st.session_state.osquery_cache = {}
        log("Initialized osquery cache in session state.", level="info")

    osquery_bin = get_osquery_path()
    log(f"Using binary at: {osquery_bin}")

    log("running osquery", level="info")
    os_key = get_current_os_key() 
    
    all_queries = load_queries(osquery_json_path)
    log(f"Loaded queries: {all_queries}", level="debug")
    if all_queries is None:
        return {"error": "Failed to load queries."}

    if os_key not in all_queries:
        log(f"No audit policy defined for OS: {os_key}", level="error")
        return {"error": f"No audit policy defined for OS: {os_key}"}
        
    os_scans = all_queries[os_key]["scans"]
    log(f"Available scans for {os_key}: {[scan['name'] for scan in os_scans]}", level="debug")
    results = {}
    
    for scan in os_scans:
        if scan["name"] in selected_names:

            # Check cache first
            cache_key = f"{os_key}_{scan['name']}"
            if cache_key in st.session_state.osquery_cache:
                log(f"Cache Hit: {scan['name']}", level="success")
                results[scan["name"]] = st.session_state.osquery_cache[cache_key]
                continue

            sql_query = scan["sql"]
            
            if sql_query.lower().startswith("elect"):
                sql_query = "S" + sql_query
            
            log(f"Initializing scan: {scan['name']}, SQL: {sql_query}", level="info")
            
            try:
                process = subprocess.run(
                [
                    'osqueryi', 
                    '--S',                        #Use a "Silent" temporary database
                    '--config_path', '/dev/null', #Ignore broken /var/osquery/osquery.conf
                    '--logger_min_status', '3',   #Only show fatal errors
                    '--json', 
                    sql_query
                ],
                capture_output=True, 
                text=True, 
                shell=False,
                timeout=30 #Prevent hanging if osqueryi encounters an issue
            )
                
                if process.returncode == 0:
                    raw_data = json.loads(process.stdout)
                    
                    #Only take the top 50 results to keep the AI context clean
                    processed_data = raw_data[:50] if isinstance(raw_data, list) else raw_data
                    
                    results[scan["name"]] = processed_data
                    st.session_state.osquery_cache[cache_key] = processed_data # Save to cache
                    log(f"✅ Data captured: {scan['name']} ({len(processed_data)} rows)", level="success")
                else:
                    log(f"Execution failed for {scan['name']}: {process.stderr}", level="error")
                    results[scan["name"]] = {"error": "Binary execution failed"}

            except subprocess.TimeoutExpired:
                log(f"Scan {scan['name']} timed out.", level="warning")
                results[scan["name"]] = {"error": "Timeout"}        
            except Exception as e:
                results[scan["name"]] = {"error": str(e)}
                log(f"Exception in {scan['name']}: {str(e)}", level="error")
                
    log(f"Total modules in final results: {list(results.keys())}")
    return results

  