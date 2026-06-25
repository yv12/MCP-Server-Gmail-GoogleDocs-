import os
import uvicorn
from mcp.server.fastmcp import FastMCP

import docs_tool
import gmail_tool

mcp = FastMCP("google-mcp")

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

# Wrap the SSE app with health check and root routes
from starlette.applications import Starlette
from starlette.routing import Route, Mount
from starlette.responses import JSONResponse

async def health(request):
    return JSONResponse({"status": "ok", "server": "google-mcp"})

async def root(request):
    return JSONResponse({
        "status": "ok",
        "server": "google-mcp",
        "sse_endpoint": "/sse",
        "tools": ["get_document_url", "get_heading_link", "find_heading", "append_section", "send_email", "create_draft"]
    })

sse_app = mcp.sse_app()

app = Starlette(routes=[
    Route("/", root),
    Route("/health", health),
    Mount("/", app=sse_app),
])

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 8000))
    uvicorn.run("server:app", host="0.0.0.0", port=port)
