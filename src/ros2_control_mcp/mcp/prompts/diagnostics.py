"""MCP prompts for ros2_control diagnostic workflows."""

from mcp.server import MCPServer


def register_diagnostic_prompts(server: MCPServer) -> None:
    """Register ros2_control diagnostic prompts."""

    @server.prompt(
        name="diagnose_controller_conflict",
        title="Diagnose controller conflict",
        description="Guide analysis of ros2_control controller conflicts.",
    )
    def diagnose_controller_conflict() -> str:
        """Guide diagnosis of controller and resource conflicts."""
        return (
            "Diagnose controller conflicts in the current ros2_control system. "
            "Review controller states, claimed command interfaces, required "
            "interfaces, and controller dependencies. Identify conflicting "
            "resource claims and explain the cause. Do not change controller "
            "states."
        )

    @server.prompt(
        name="diagnose_hardware_interface",
        title="Diagnose hardware interface",
        description="Guide analysis of ros2_control hardware interfaces.",
    )
    def diagnose_hardware_interface() -> str:
        """Guide diagnosis of hardware interface availability and claims."""
        return (
            "Diagnose the ros2_control hardware interfaces. Review hardware "
            "component states, command interfaces, state interfaces, "
            "availability, and claims. Identify missing or unavailable "
            "interfaces and explain likely causes. Do not change hardware "
            "states."
        )

    @server.prompt(
        name="review_controller_switch",
        title="Review controller switch",
        description="Review a controller switch before execution.",
    )
    def review_controller_switch() -> str:
        """Guide a read-only review of a planned controller switch."""
        return (
            "Review a planned ros2_control controller switch. Check current "
            "controller states, required command and state interfaces, "
            "resource claims, controller dependencies, and controller chains. "
            "Identify conflicts and risks. Do not execute the switch."
        )
