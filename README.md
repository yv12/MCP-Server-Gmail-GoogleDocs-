# Google Docs and Gmail MCP Server

This is a Model Context Protocol (MCP) server that exposes Google Docs and Gmail capabilities to LLMs via the official `mcp` SDK using an SSE transport over FastAPI.

## Setup Instructions

### 1. Google Cloud Setup
1. Go to the [Google Cloud Console](https://console.cloud.google.com/).
2. Create a new project.
3. Enable the **Google Docs API** and **Gmail API**.
4. Go to **APIs & Services > Credentials** and create an **OAuth client ID** (Desktop app).
5. Download the JSON file and save it as `credentials.json` in the root of this project.

### 2. Installation
Install the dependencies:
```bash
pip install -r requirements.txt
```

### 3. Authentication
Before running the server in a cloud environment, you must run it locally once to authenticate and generate the `token.json` file.
The server will print an authorization URL if `token.json` is missing. Complete the OAuth flow to generate `token.json`.

### 4. Running the Server
Start the server using uvicorn:
```bash
uvicorn server:app --host 0.0.0.0 --port 8000
```

The MCP SSE endpoints will be available at:
- `/sse` (for connecting)
- `/messages/` (for posting messages)
