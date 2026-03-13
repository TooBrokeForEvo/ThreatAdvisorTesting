import xml.etree.ElementTree as ET
import os
import json
from src.logger import log

def parse_nmap_xml(file_path):
    """
    Parses Nmap XML output into a structured format. 
    """
    if not os.path.exists(file_path):
        log(f"File not found: {file_path}", level="error")
        return f"Error: File not found - {file_path}"

    try:
        tree = ET.parse(file_path)
        root = tree.getroot()
        scan_results = []

        for host in root.findall('host'):
            addr_elem = host.find('address')
            status_elem = host.find('status')

            if addr_elem is None or status_elem is None:
                continue

            ip_address = addr_elem.attrib.get('addr')
            status = status_elem.attrib.get('state')

            host_data = {
                "ip": ip_address,
                "status": status,
                "open_ports": []
            }

            ports_elem = host.find('ports')
            if ports_elem is not None:
                for port in ports_elem.findall('port'):
                    state_elem = port.find('state')
                    
                    # Only collect ports that are actually 'open'
                    if state_elem is not None and state_elem.attrib.get('state') == 'open':
                        port_id = port.attrib.get('portid')
                        protocol = port.attrib.get('protocol')

                        service = port.find('service')
                        if service is not None:
                            service_name = service.attrib.get('name', 'unknown')
                            product = service.attrib.get('product', '')
                            version = service.attrib.get('version', '')
                        else:
                            service_name, product, version = "unknown", "", ""

                        host_data["open_ports"].append({
                            "port": port_id,
                            "protocol": protocol,
                            "service": service_name,
                            "version": f"{product} {version}".strip()
                        })

            scan_results.append(host_data)

        log(f"Successfully parsed Nmap XML file: {file_path}", level="success")
        return scan_results

    except ET.ParseError as e:
            log(f"XML Syntax Error in {file_path}: {e}", level="error")
            return {"error": f"Invalid XML format: {e}"}
    except Exception as e:
            log(f"Unexpected Parser Error: {e}", level="error")
            return {"error": str(e)}
