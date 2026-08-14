"""Application service for ros2_control operations."""

from ros2_control_mcp.domain.chains import ControllerDependency
from ros2_control_mcp.domain.claims import ResourceClaim
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

    def list_resource_claims(self) -> tuple[ResourceClaim, ...]:
        """Return command interface claims across all controllers."""
        return tuple(
            ResourceClaim(
                interface_name=interface_name,
                controller_name=controller.name,
            )
            for controller in self.list_controllers()
            for interface_name in controller.claimed_interfaces
        )

    def list_controller_dependencies(
        self,
    ) -> tuple[ControllerDependency, ...]:
        """Return dependencies between chained controllers."""
        return tuple(
            ControllerDependency(
                controller_name=controller.name,
                depends_on=connection.name,
                reference_interfaces=connection.reference_interfaces,
            )
            for controller in self.list_controllers()
            for connection in controller.chain_connections
        )


    def validate_controller_switch(
        self,
        plan: "ControllerSwitchPlan",
    ) -> "SafetyResult":
        """Validate a controller switch without executing it."""
        from ros2_control_mcp.domain.safety import (
            ControllerSwitchPlan,
            SafetyResult,
        )
        from ros2_control_mcp.safety.evaluator import SafetyEvaluator

        controllers = self.list_controllers()
        command_interfaces, state_interfaces = self.list_hardware_interfaces()

        evaluator = SafetyEvaluator()

        return evaluator.validate_controller_switch(
            plan=plan,
            controllers=controllers,
            command_interfaces=command_interfaces,
            state_interfaces=state_interfaces,
        )
