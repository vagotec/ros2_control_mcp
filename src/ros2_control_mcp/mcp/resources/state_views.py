"""MCP resources for focused ros2_control state views."""

import json
from dataclasses import asdict

from mcp.server import MCPServer

from ros2_control_mcp.application.control.service import Ros2ControlService


def register_state_resources(
    server: MCPServer,
    service: Ros2ControlService,
) -> None:
    """Register focused read-only ros2_control resources."""

    @server.resource(
        "ros2control://hardware",
        name="ros2_control_hardware",
        description="Current ros2_control hardware components and interfaces.",
        mime_type="application/json",
    )
    def hardware() -> str:
        """Return hardware components and interfaces."""
        components = service.list_hardware_components()
        command_interfaces, state_interfaces = service.list_hardware_interfaces()

        return json.dumps(
            {
                "hardware_components": [asdict(item) for item in components],
                "command_interfaces": [
                    asdict(item) for item in command_interfaces
                ],
                "state_interfaces": [
                    asdict(item) for item in state_interfaces
                ],
            },
            indent=2,
        )

    @server.resource(
        "ros2control://claims",
        name="ros2_control_claims",
        description="Current ros2_control command interface claims.",
        mime_type="application/json",
    )
    def claims() -> str:
        """Return current resource claims."""
        return json.dumps(
            [asdict(item) for item in service.list_resource_claims()],
            indent=2,
        )

    @server.resource(
        "ros2control://chains",
        name="ros2_control_chains",
        description="Current ros2_control controller dependencies and chains.",
        mime_type="application/json",
    )
    def chains() -> str:
        """Return current controller dependencies."""
        return json.dumps(
            [
                asdict(item)
                for item in service.list_controller_dependencies()
            ],
            indent=2,
        )
