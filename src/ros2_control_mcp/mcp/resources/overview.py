"""MCP resource for the ros2_control system overview."""

import json
from dataclasses import asdict

from mcp.server import MCPServer

from ros2_control_mcp.application.control.service import Ros2ControlService


def register_overview_resource(
    server: MCPServer,
    service: Ros2ControlService,
) -> None:
    """Register the ros2_control overview resource."""

    @server.resource(
        "ros2control://overview",
        name="ros2_control_overview",
        description="Current ros2_control controllers, hardware, and interfaces.",
        mime_type="application/json",
    )
    def overview() -> str:
        """Return a structured overview of the ros2_control system."""
        controllers = service.list_controllers()
        hardware = service.list_hardware_components()
        command_interfaces, state_interfaces = service.list_hardware_interfaces()

        payload = {
            "controllers": [asdict(item) for item in controllers],
            "hardware_components": [asdict(item) for item in hardware],
            "command_interfaces": [
                asdict(item) for item in command_interfaces
            ],
            "state_interfaces": [
                asdict(item) for item in state_interfaces
            ],
        }

        return json.dumps(payload, indent=2)
