"""MCP tools for ros2_control claims and controller relationships."""

from dataclasses import asdict
from typing import Any

from mcp.server import MCPServer

from ros2_control_mcp.application.control.service import Ros2ControlService


def register_relationship_tools(
    server: MCPServer,
    service: Ros2ControlService,
) -> None:
    """Register read-only relationship tools on the MCP server."""

    def list_resource_claims() -> list[dict[str, Any]]:
        """List command interface claims across controllers."""
        return [
            asdict(claim)
            for claim in service.list_resource_claims()
        ]

    def list_controller_dependencies() -> list[dict[str, Any]]:
        """List dependencies between chained controllers."""
        return [
            asdict(dependency)
            for dependency in service.list_controller_dependencies()
        ]

    server.add_tool(
        list_resource_claims,
        name="list_resource_claims",
        description="List command interface claims across ros2_control controllers.",
        structured_output=True,
    )

    server.add_tool(
        list_controller_dependencies,
        name="list_controller_dependencies",
        description="List dependencies between chained ros2_control controllers.",
        structured_output=True,
    )
