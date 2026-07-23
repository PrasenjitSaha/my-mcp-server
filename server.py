#!/usr/bin/env python3
"""
Minimal MCP server built with FastMCP, using the Streamable HTTP transport.

This is designed to run as a normal long-lived web process, which is what
Azure App Service expects. App Service injects a PORT environment variable
that the app must bind to.
"""

import os
import uvicorn
from mcp.server.fastmcp import FastMCP
from mcp.server.transport_security import TransportSecuritySettings

# stateless_http=True avoids needing session/state persistence across
# requests, which keeps things simple for a first deployment.
#
# transport_security allowlists the Host/Origin headers that are allowed
# to reach this server. Without this, the MCP SDK's DNS-rebinding
# protection rejects requests whose Host header isn't localhost, which is
# what causes the "Invalid Host header" error when running on Render/Azure.
mcp = FastMCP(
    "my-mcp-server",
    stateless_http=True,
    transport_security=TransportSecuritySettings(
        allowed_hosts=["my-mcp-server-100.onrender.com","my-mcp-server-app-001.azurewebsites.net", "localhost", "127.0.0.1"],
        allowed_origins=[
            "https://my-mcp-server-100.onrender.com",
            "https://my-mcp-server-app-001.azurewebsites.net"
            "http://localhost:*",
        ],
    ),
)


@mcp.tool()
def add(a: float, b: float) -> float:
    """Add two numbers together.

    Args:
        a: first number
        b: second number
    """
    return a + b


@mcp.tool()
def get_weather(city: str) -> str:
    """Get a mock weather report for a city.

    Args:
        city: name of the city to check
    """
    return f"The weather in {city} is sunny and 25°C."


@mcp.tool()
def reverse_text(text: str) -> str:
    """Reverse a string of text.

    Args:
        text: the text to reverse
    """
    return text[::-1]


def main():
    host = os.getenv("HOST", "0.0.0.0")
    port = int(os.getenv("PORT", "8000"))

    print("Starting MCP server...")
    print(f"HOST: {host}")
    print(f"PORT: {port}")
    print("MCP endpoint will be available at: <server URL>/mcp")

    # Get the underlying Starlette/ASGI app from FastMCP and run it
    # directly with uvicorn so we control host/port explicitly.
    app = mcp.streamable_http_app()
    uvicorn.run(app, host=host, port=port, log_level="info")


if __name__ == "__main__":
    main()
