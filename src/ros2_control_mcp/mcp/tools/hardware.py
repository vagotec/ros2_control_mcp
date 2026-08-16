"""MCP tools for ros2_control hardware operations."""

from dataclasses import asdict
from typing import Any

from mcp.server import MCPServer

from ros2_control_mcp.application.control.service import Ros2ControlService


def register_hardware_tools(
    server: MCPServer,
    service: Ros2ControlService,
) -> None:
    """Register ros2_control hardware tools."""

    def list_hardware_components() -> list[dict[str, Any]]:
        """List hardware components."""
        return [
            asdict(component)
            for component in service.list_hardware_components()
        ]

    def get_hardware_component(
        name: str,
    ) -> dict[str, Any] | None:
        """Get one hardware component."""
        component = service.get_hardware_component(name)

        if component is None:
            return None

        return asdict(component)

    def set_hardware_component_state(
        name: str,
        state_id: int,
        state_label: str,
    ) -> dict[str, Any]:
        """Change hardware component lifecycle state."""

        result = service.set_hardware_component_state(
            name=name,
            state_id=state_id,
            state_label=state_label,
        )

        return asdict(result)

    server.add_tool(
        list_hardware_components,
        name="list_hardware_components",
        description=(
            "List ros2_control hardware components."
        ),
        structured_output=True,
    )

    server.add_tool(
        get_hardware_component,
        name="get_hardware_component",
        description=(
            "Get details about one ros2_control hardware component."
        ),
        structured_output=True,
    )

    server.add_tool(
        set_hardware_component_state,
        name="set_hardware_component_state",
        description=(
            "Change ros2_control hardware component lifecycle state."
        ),
        structured_output=True,
    )
