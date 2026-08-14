"""MCP tools for ros2_control hardware inspection."""

from dataclasses import asdict
from typing import Any

from mcp.server import MCPServer

from ros2_control_mcp.application.control.service import Ros2ControlService


def register_hardware_tools(
    server: MCPServer,
    service: Ros2ControlService,
) -> None:
    """Register read-only hardware tools on the MCP server."""

    def list_hardware_components() -> list[dict[str, Any]]:
        """List ros2_control hardware components."""
        return [
            asdict(component)
            for component in service.list_hardware_components()
        ]

    def get_hardware_component(name: str) -> dict[str, Any] | None:
        """Return details for one ros2_control hardware component."""
        component = service.get_hardware_component(name)
        return asdict(component) if component is not None else None

    def list_hardware_interfaces() -> dict[str, list[dict[str, Any]]]:
        """List ros2_control command and state interfaces."""
        command_interfaces, state_interfaces = (
            service.list_hardware_interfaces()
        )
        return {
            "command_interfaces": [
                asdict(interface) for interface in command_interfaces
            ],
            "state_interfaces": [
                asdict(interface) for interface in state_interfaces
            ],
        }

    def list_claimed_command_interfaces() -> list[dict[str, Any]]:
        """List currently claimed ros2_control command interfaces."""
        return [
            asdict(interface)
            for interface in service.list_claimed_command_interfaces()
        ]

    def list_unclaimed_command_interfaces() -> list[dict[str, Any]]:
        """List currently unclaimed ros2_control command interfaces."""
        return [
            asdict(interface)
            for interface in service.list_unclaimed_command_interfaces()
        ]

    server.add_tool(
        list_hardware_components,
        name="list_hardware_components",
        description="List ros2_control hardware components and states.",
        structured_output=True,
    )
    server.add_tool(
        get_hardware_component,
        name="get_hardware_component",
        description="Get details for one ros2_control hardware component.",
        structured_output=True,
    )
    server.add_tool(
        list_hardware_interfaces,
        name="list_hardware_interfaces",
        description="List ros2_control command and state interfaces.",
        structured_output=True,
    )
    server.add_tool(
        list_claimed_command_interfaces,
        name="list_claimed_command_interfaces",
        description="List currently claimed ros2_control command interfaces.",
        structured_output=True,
    )
    server.add_tool(
        list_unclaimed_command_interfaces,
        name="list_unclaimed_command_interfaces",
        description="List currently unclaimed ros2_control command interfaces.",
        structured_output=True,
    )
