

# ThreatAdvisor Prototype

## Overview
Prototype 4 - current changes have not been tested fully. 

## Overview
ThreatAdvisor is a scanner that supports Nmap (Network Mapper) scans and Osquery scans, these scans are then analysed by the GPT API. The API explains the scan findings for non-technical users.

The ThreatTrace prototype supports Nmap (Network Mapper) scans and Osquery scans. The UI allows a user to choose if they'd like a Telemetry (Osquery) scan or a Nmap scan or both. It also allows the user to choose what kind of Osquery scan or Nmap scan they'd like to run. This makes the process really easy for the User. 

The app is built using a Streamlit-based web interface for running live scans of both types, as well as analysing any uploaded scan data, and reviewing raw test data. A user can type the IP address of the device they'd like to scan into the scanner however this was only tested on localhost. 

The system prompt is in a external file to allow for easy changes. 
---

## Components
### 1. File Scanner 
- Allows users to upload existing Nmap XML scan results for analysis.

### 2. Live Nmap Scanner
- Runs actual Nmap scans on a target host (default: localhost).
- Extracts open TCP ports and basic service information.
- Produces structured output for AI analysis.

### 3. Live Osquery Scanner
- Runs actual Osquery scans on a target host (default: localhost).
- Gives selected info on device. 
- Produces structured output for AI analysis.

### 4. AI Client
- Communicates with the OpenAI API to analyse scan results.
- Uses system and user prompts to generate clear, non-technical explanations.
- Tracks API token usage, response time, and estimated cost.

### 5. Frontend
- Streamlit UI: A modern, reactive web interface that handles scan execution, file uploads, and data visualization.

### 6. Prompt Templates
- The prompt is in a external to allow for easy changes and manamgment.
- Ensures explanations are clear, non-alarming, and actionable.

---

## Getting Started

### Prerequisites
- Python 3.10+
- Nmap installed (for live scans)
- OpenAI API key
- Required Python packages: streamlit, openai, python-dotenv
- Osqueryi 

### Setup
1. Clone the repository:
   ```bash
   git clone <repo_url>
   cd gkz00001-project
   ```
2. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```
3. Create a `.env` file with your OpenAI API key:
   ```
   OPENAI_API_KEY=your_api_key_here
   ```

### Running the Application
```bash
streamlit run main.py
```
Open `http://127.0.0.1:5000` in your browser.

---

## Notes
- AI explanations are designed for non-technical users and do not provide actionable exploits.
- API usage is measured in tokens, and cost estimates are provided in the GUI or web frontend.
- Some scans have been included these have been changed with IP addresses and MAC addresses also being changed. All identifiying data should been have been removed from these files. 
# ThreatAdvisorTesting
