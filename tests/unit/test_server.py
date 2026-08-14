"""Tests for the MCP server."""

from mcp.server import MCPServer

from ros2_control_mcp.server import SERVER_NAME, create_server


def test_create_server() -> None:
    """Verify that create_server returns the configured MCP server."""
    server = create_server()

    assert isinstance(server, MCPServer)
    assert server.name == SERVER_NAME
