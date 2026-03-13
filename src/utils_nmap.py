import nmap # type: ignore
import ipaddress
import streamlit as st # type: ignore
from src.logger import log


def validate_ip(ip_str):
    """Validates the provided IP address string."""
    try:
        if "/" in ip_str:
            ipaddress.ip_network(ip_str, strict=False)
        else:
            ipaddress.ip_address(ip_str)
        return True
    except ValueError:
        return False


def run_live_scan(target_ip, scan_type="-sV"):
    """
    Runs a live Nmap scan against the specified target IP address and returns structured results.
    """
    #Nmap cache stored in session state to avoid redundant scans and improve performance.
    if "nmap_cache" not in st.session_state:
        st.session_state.nmap_cache = {}
        log("Initialized nmap cache in session state.", level="info")

    if not validate_ip(target_ip):
        log(f"Invalid IP address: {target_ip}", level="error")
        return {"error": "Invalid IP address"}

    cache_key = f"nmap_{target_ip}_{scan_type}"
    if cache_key in st.session_state.nmap_cache:
        log(f"Cache Hit: {target_ip}", level="success")
        return st.session_state.nmap_cache[cache_key]

    log(f"Running Nmap scan on {target_ip} with arguments: {scan_type}", level="info")  
    nm = nmap.PortScanner()

    try:
        nm.scan(target_ip, arguments=scan_type)

        scan_data = []
        for host in nm.all_hosts():
            log(f"Scanning host: {host}", level="info")
            host_info = {
                "ip": host,
                "hostname": nm[host].hostname(),
                "status": nm[host].state(),
                "open_ports": []
            }

            for proto in nm[host].all_protocols():
                lport = nm[host][proto].keys()
                for port in lport:
                    service = nm[host][proto][port]
                    host_info["open_ports"].append({
                        "port": port,
                        "protocol": proto,
                        "service": service.get('name'),
                        "version": service.get('version'),
                        "state": service.get('state')
                    })
            scan_data.append(host_info)
        if not scan_data:
            log(f"No active host found for {target_ip}", level="warning")
        else:
            log(f"Scan completed for {target_ip}: {len(scan_data)} host(s) found", level="success")
            st.session_state.nmap_cache[cache_key] = scan_data
        
        return scan_data
    
    except nmap.PortScannerError as e:
        log(f"Nmap Execution Error: {str(e)}", level="error")
        return {"error": f"Nmap Failure: {str(e)}"}
    except Exception as e:
        log(f"Unexpected Nmap Failure: {str(e)}", level="error")
        return {"error": "Internal Nmap Module Error"}


    


