"""Abstract adapter for ros2_control access."""

from abc import ABC, abstractmethod

from ros2_control_mcp.domain.control import ControlResult
from ros2_control_mcp.domain.safety import ControllerSwitchPlan
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
    def load_controller(self, name: str) -> ControlResult:
        """Load a controller through ros2_control."""
        raise NotImplementedError

    @abstractmethod
    def configure_controller(self, name: str) -> ControlResult:
        """Configure a controller through ros2_control."""
        raise NotImplementedError

    @abstractmethod
    def activate_controller(self, name: str) -> ControlResult:
        """Activate a controller through ros2_control."""
        raise NotImplementedError

    @abstractmethod
    def deactivate_controller(self, name: str) -> ControlResult:
        """Deactivate a controller through ros2_control."""
        raise NotImplementedError

    @abstractmethod
    def switch_controllers(
        self,
        plan: ControllerSwitchPlan,
    ) -> ControlResult:
        """Execute a validated controller switch through ros2_control."""
        raise NotImplementedError

    @abstractmethod
    def unload_controller(self, name: str) -> ControlResult:
        """Unload a controller through ros2_control."""
        raise NotImplementedError

    @abstractmethod
    def cleanup_controller(self, name: str) -> ControlResult:
        """Cleanup a controller through ros2_control."""
        raise NotImplementedError

    @abstractmethod
    def set_hardware_component_state(
        self,
        name: str,
        state_id: int,
        state_label: str = "",
    ) -> ControlResult:
        """Change hardware component lifecycle state."""
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
