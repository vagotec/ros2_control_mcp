"""MCP tools for ros2_control controller inspection."""

from dataclasses import asdict
from typing import Any

from mcp.server import MCPServer

from ros2_control_mcp.application.control.service import Ros2ControlService


def register_controller_tools(
    server: MCPServer,
    service: Ros2ControlService,
) -> None:
    """Register read-only controller tools on the MCP server."""

    def list_controllers() -> list[dict[str, Any]]:
        """List controllers known to the ros2_control controller manager."""
        return [asdict(controller) for controller in service.list_controllers()]

    def get_controller(name: str) -> dict[str, Any] | None:
        """Return details for one ros2_control controller by name."""
        controller = service.get_controller(name)
        return asdict(controller) if controller is not None else None

    def list_controller_types() -> list[dict[str, Any]]:
        """List controller types available to the controller manager."""
        return [
            asdict(controller_type)
            for controller_type in service.list_controller_types()
        ]

    server.add_tool(
        list_controllers,
        name="list_controllers",
        description="List ros2_control controllers and their current states.",
        structured_output=True,
    )
    server.add_tool(
        get_controller,
        name="get_controller",
        description="Get detailed information about one ros2_control controller.",
        structured_output=True,
    )
    server.add_tool(
        list_controller_types,
        name="list_controller_types",
        description="List controller types available to ros2_control.",
        structured_output=True,
    )
