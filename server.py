import asyncio
from contextlib import asynccontextmanager
from fastapi import FastAPI
from starlette.requests import Request
from starlette.responses import JSONResponse
from mcp.server import Server
from mcp.server.sse import SseServerTransport
import uvicorn

import docs_tool
import gmail_tool

mcp = Server("google-mcp")

# Google Docs Tools
@mcp.tool()
async def get_document_url(document_id: str) -> str:
    """Returns the URL of a Google Doc."""
    return docs_tool.get_document_url(document_id)

@mcp.tool()
async def get_heading_link(document_id: str, heading_id: str) -> str:
    """Returns the deep link to a specific heading in a Google Doc."""
    return docs_tool.get_heading_link(document_id, heading_id)

@mcp.tool()
async def find_heading(document_id: str, heading_text: str) -> str:
    """Fetches the doc structure and returns the internal heading_id matching heading_text."""
    return docs_tool.find_heading(document_id, heading_text)

@mcp.tool()
async def append_section(document_id: str, heading_text: str, heading_level: int, body_content: list) -> dict:
    """
    Appends a new section at the end of the document.
    body_content should be a list of dictionaries with type ('paragraph', 'heading', 'bullet_list', 'table', 'horizontal_rule')
    and optional text, level, items, or rows.
    """
    return docs_tool.append_section(document_id, heading_text, heading_level, body_content)

# Gmail Tools
@mcp.tool()
async def send_email(to: str, subject: str, html_body: str, text_body: str) -> dict:
    """Sends an email immediately."""
    return gmail_tool.send_email(to, subject, html_body, text_body)

@mcp.tool()
async def create_draft(to: str, subject: str, html_body: str, text_body: str) -> dict:
    """Creates an email draft without sending."""
    return gmail_tool.create_draft(to, subject, html_body, text_body)

app = FastAPI()
sse = SseServerTransport("/messages/")

@app.get("/sse")
async def handle_sse(request: Request):
    """MCP SSE endpoint."""
    async with sse.connect_sse(
        request.scope, 
        request.receive, 
        request._send
    ) as (read_stream, write_stream):
        await mcp.run(
            read_stream, 
            write_stream, 
            mcp.create_initialization_options()
        )

@app.post("/messages/")
async def handle_messages(request: Request):
    """MCP Messages endpoint."""
    await sse.handle_post_message(
        request.scope, 
        request.receive, 
        request._send
    )

import os

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 8000))
    uvicorn.run("server:app", host="0.0.0.0", port=port)
