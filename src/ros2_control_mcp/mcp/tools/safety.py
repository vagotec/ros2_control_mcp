"""MCP tools for ros2_control safety validation."""

from dataclasses import asdict
from typing import Any

from mcp.server import MCPServer

from ros2_control_mcp.application.control.service import Ros2ControlService
from ros2_control_mcp.domain.safety import (
    ControllerSwitchPlan,
    SwitchStrictness,
)


def register_safety_tools(
    server: MCPServer,
    service: Ros2ControlService,
) -> None:
    """Register read-only ros2_control safety tools."""

    def validate_controller_switch(
        activate: list[str],
        deactivate: list[str],
        strictness: str = "strict",
        timeout_seconds: float = 5.0,
    ) -> dict[str, Any]:
        """Validate a controller switch without executing it."""
        plan = ControllerSwitchPlan(
            activate=tuple(activate),
            deactivate=tuple(deactivate),
            strictness=SwitchStrictness(strictness),
            timeout_seconds=timeout_seconds,
        )

        result = service.validate_controller_switch(plan)

        return asdict(result)

    server.add_tool(
        validate_controller_switch,
        name="validate_controller_switch",
        description=(
            "Validate a ros2_control controller switch without executing it."
        ),
        structured_output=True,
    )
