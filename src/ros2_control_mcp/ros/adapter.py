"""Abstract adapter for ros2_control access."""

from abc import ABC, abstractmethod

from ros2_control_mcp.domain.controllers import Controller, ControllerType


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
