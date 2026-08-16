"""MCP tools for ros2_control controller operations."""

from dataclasses import asdict
from typing import Any

from mcp.server import MCPServer

from ros2_control_mcp.application.control.service import Ros2ControlService


def register_controller_tools(
    server: MCPServer,
    service: Ros2ControlService,
) -> None:
    """Register ros2_control controller tools."""

    def list_controllers() -> list[dict[str, Any]]:
        """List controllers known to the ros2_control controller manager."""
        return [
            asdict(controller)
            for controller in service.list_controllers()
        ]

    def get_controller(name: str) -> dict[str, Any] | None:
        """Return details for one ros2_control controller by name."""
        controller = service.get_controller(name)

        if controller is None:
            return None

        return asdict(controller)

    def list_controller_types() -> list[dict[str, Any]]:
        """List controller types available to the controller manager."""
        return [
            asdict(controller_type)
            for controller_type in service.list_controller_types()
        ]

    def load_controller(name: str) -> dict[str, Any]:
        """Load one ros2_control controller."""
        result = service.load_controller(name)
        return asdict(result)

    def configure_controller(name: str) -> dict[str, Any]:
        """Configure one ros2_control controller."""
        result = service.configure_controller(name)
        return asdict(result)

    def deactivate_controller(name: str) -> dict[str, Any]:
        """Deactivate one ros2_control controller."""
        result = service.deactivate_controller(name)
        return asdict(result)

    def cleanup_controller(name: str) -> dict[str, Any]:
        """Cleanup one ros2_control controller."""
        result = service.cleanup_controller(name)
        return asdict(result)

    def unload_controller(name: str) -> dict[str, Any]:
        """Unload one ros2_control controller."""
        result = service.unload_controller(name)
        return asdict(result)

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

    server.add_tool(
        load_controller,
        name="load_controller",
        description="Load one ros2_control controller.",
        structured_output=True,
    )

    server.add_tool(
        configure_controller,
        name="configure_controller",
        description="Configure one ros2_control controller.",
        structured_output=True,
    )

    server.add_tool(
        deactivate_controller,
        name="deactivate_controller",
        description="Deactivate one ros2_control controller.",
        structured_output=True,
    )

    server.add_tool(
        cleanup_controller,
        name="cleanup_controller",
        description="Cleanup one ros2_control controller.",
        structured_output=True,
    )

    server.add_tool(
        unload_controller,
        name="unload_controller",
        description="Unload one ros2_control controller.",
        structured_output=True,
    )
