"""MCP prompts for ros2_control inspection workflows."""

from mcp.server import MCPServer


def register_inspection_prompts(server: MCPServer) -> None:
    """Register ros2_control inspection prompts."""

    @server.prompt(
        name="inspect_ros2_control_system",
        title="Inspect ros2_control system",
        description="Guide a structured inspection of a ros2_control system.",
    )
    def inspect_ros2_control_system() -> str:
        """Inspect the current ros2_control system before recommending actions."""
        return (
            "Inspect the current ros2_control system. "
            "Review controllers, controller states, hardware components, "
            "command and state interfaces, resource claims, and controller "
            "dependencies. Identify inconsistencies or unavailable resources. "
            "Do not perform any state-changing operation."
        )
