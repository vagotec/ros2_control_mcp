"""MCP server entry point for ros2_control_mcp."""

from mcp.server import MCPServer


SERVER_NAME = "ros2-control-mcp"


def create_server() -> MCPServer:
    """Create the ros2_control MCP server."""
    return MCPServer(
        SERVER_NAME,
        instructions=(
            "Inspect and manage ros2_control systems through structured "
            "controller, hardware, interface, and safety operations."
        ),
    )


def main() -> None:
    """Run the MCP server over stdio."""
    server = create_server()
    server.run(transport="stdio")


if __name__ == "__main__":
    main()
