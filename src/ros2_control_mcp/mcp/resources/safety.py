"""MCP resource for ros2_control safety context."""

import json
from dataclasses import asdict

from mcp.server import MCPServer

from ros2_control_mcp.application.control.service import Ros2ControlService


def register_safety_resource(
    server: MCPServer,
    service: Ros2ControlService,
) -> None:
    """Register the ros2_control safety context resource."""

    @server.resource(
        "ros2control://safety",
        name="ros2_control_safety",
        description="Current ros2_control safety-relevant system state.",
        mime_type="application/json",
    )
    def safety() -> str:
        """Return safety-relevant ros2_control state."""
        command_interfaces, state_interfaces = service.list_hardware_interfaces()

        payload = {
            "resource_claims": [
                asdict(item) for item in service.list_resource_claims()
            ],
            "controller_dependencies": [
                asdict(item)
                for item in service.list_controller_dependencies()
            ],
            "command_interfaces": [
                asdict(item) for item in command_interfaces
            ],
            "state_interfaces": [
                asdict(item) for item in state_interfaces
            ],
            "physical_safety_guarantee": False,
        }

        return json.dumps(payload, indent=2)
