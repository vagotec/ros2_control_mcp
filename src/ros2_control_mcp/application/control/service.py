"""Application service for ros2_control operations."""

from ros2_control_mcp.domain.controllers import Controller, ControllerType
from ros2_control_mcp.domain.hardware import HardwareComponent
from ros2_control_mcp.domain.interfaces import HardwareInterface
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

    def list_hardware_components(self) -> tuple[HardwareComponent, ...]:
        """Return hardware components reported by ros2_control."""
        return self._adapter.list_hardware_components()

    def get_hardware_component(self, name: str) -> HardwareComponent | None:
        """Return one hardware component by name if it exists."""
        return next(
            (
                component
                for component in self.list_hardware_components()
                if component.name == name
            ),
            None,
        )

    def list_hardware_interfaces(
        self,
    ) -> tuple[tuple[HardwareInterface, ...], tuple[HardwareInterface, ...]]:
        """Return command and state interfaces reported by ros2_control."""
        return self._adapter.list_hardware_interfaces()

    def list_claimed_command_interfaces(self) -> tuple[HardwareInterface, ...]:
        """Return currently claimed command interfaces."""
        command_interfaces, _ = self.list_hardware_interfaces()
        return tuple(
            interface
            for interface in command_interfaces
            if interface.is_claimed
        )

    def list_unclaimed_command_interfaces(self) -> tuple[HardwareInterface, ...]:
        """Return currently unclaimed command interfaces."""
        command_interfaces, _ = self.list_hardware_interfaces()
        return tuple(
            interface
            for interface in command_interfaces
            if not interface.is_claimed
        )
