"""MCP server entry point for ros2_control_mcp."""

from mcp.server import MCPServer

from ros2_control_mcp.application.control.service import Ros2ControlService
from ros2_control_mcp.mcp.prompts.diagnostics import register_diagnostic_prompts
from ros2_control_mcp.mcp.prompts.inspection import register_inspection_prompts
from ros2_control_mcp.mcp.resources.overview import register_overview_resource
from ros2_control_mcp.mcp.resources.safety import register_safety_resource
from ros2_control_mcp.mcp.resources.state_views import register_state_resources
from ros2_control_mcp.mcp.tools.controllers import register_controller_tools
from ros2_control_mcp.mcp.tools.hardware import register_hardware_tools
from ros2_control_mcp.mcp.tools.relationships import register_relationship_tools
from ros2_control_mcp.mcp.tools.safety import register_safety_tools
from ros2_control_mcp.ros.jazzy.adapter import JazzyRos2ControlAdapter


SERVER_NAME = "ros2-control-mcp"


def create_server() -> MCPServer:
    """Create and configure the ros2_control MCP server."""
    server = MCPServer(
        SERVER_NAME,
        instructions=(
            "Inspect ros2_control controllers, hardware, interfaces, claims, "
            "and controller dependencies. Validate planned controller switches "
            "before execution. Do not imply physical safety guarantees."
        ),
    )

    service = Ros2ControlService(JazzyRos2ControlAdapter())

    register_controller_tools(server, service)
    register_hardware_tools(server, service)
    register_relationship_tools(server, service)
    register_safety_tools(server, service)

    register_overview_resource(server, service)
    register_state_resources(server, service)
    register_safety_resource(server, service)

    register_inspection_prompts(server)
    register_diagnostic_prompts(server)

    return server


def main() -> None:
    """Run the MCP server over stdio."""
    server = create_server()
    server.run(transport="stdio")


if __name__ == "__main__":
    main()
