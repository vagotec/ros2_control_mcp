"""Abstract adapter for ros2_control access."""

from abc import ABC, abstractmethod

from ros2_control_mcp.domain.controllers import Controller, ControllerType
from ros2_control_mcp.domain.hardware import HardwareComponent
from ros2_control_mcp.domain.interfaces import HardwareInterface


class Ros2ControlAdapter(ABC):
    """Define the interface for ros2_control implementations."""

    @abstractmethod
    def list_controllers(self) -> tuple[Controller, ...]:
        """Return the controllers known to the controller manager."""
        raise NotImplementedError

    @abstractmethod
    def list_controller_types(self) -> tuple[ControllerType, ...]:
        """Return the controller types known to the controller manager."""
        raise NotImplementedError

    @abstractmethod
    def list_hardware_components(self) -> tuple[HardwareComponent, ...]:
        """Return hardware components known to the resource manager."""
        raise NotImplementedError

    @abstractmethod
    def list_hardware_interfaces(
        self,
    ) -> tuple[tuple[HardwareInterface, ...], tuple[HardwareInterface, ...]]:
        """Return command and state interfaces from the resource manager."""
        raise NotImplementedError
