"""Application service for ros2_control operations."""

from ros2_control_mcp.domain.controllers import Controller, ControllerType
from ros2_control_mcp.ros.adapter import Ros2ControlAdapter


class Ros2ControlService:
    """Coordinate ros2_control operations through an adapter."""

    def __init__(self, adapter: Ros2ControlAdapter) -> None:
        """Initialize the service with a ros2_control adapter."""
        self._adapter = adapter

    def list_controllers(self) -> tuple[Controller, ...]:
        """Return controllers reported by ros2_control."""
        return self._adapter.list_controllers()

    def get_controller(self, name: str) -> Controller | None:
        """Return one controller by name if it exists."""
        return next(
            (
                controller
                for controller in self.list_controllers()
                if controller.name == name
            ),
            None,
        )

    def list_controller_types(self) -> tuple[ControllerType, ...]:
        """Return available controller types reported by ros2_control."""
        return self._adapter.list_controller_types()
