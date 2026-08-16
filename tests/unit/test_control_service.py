"""Tests for the ros2_control application service."""

from ros2_control_mcp.application.control.service import Ros2ControlService
from ros2_control_mcp.domain.control import ControlResult
from ros2_control_mcp.domain.safety import ControllerSwitchPlan
from ros2_control_mcp.domain.controllers import Controller, ControllerType
from ros2_control_mcp.domain.hardware import HardwareComponent
from ros2_control_mcp.domain.interfaces import HardwareInterface
from ros2_control_mcp.ros.adapter import Ros2ControlAdapter


class FakeRos2ControlAdapter(Ros2ControlAdapter):
    """Provide deterministic ros2_control data for service tests."""

    def list_controllers(self) -> tuple[Controller, ...]:
        """Return test controllers."""
        return (
            Controller(
                name="joint_state_broadcaster",
                controller_type=(
                    "joint_state_broadcaster/JointStateBroadcaster"
                ),
                state="active",
                update_rate=100,
                required_state_interfaces=(
                    "joint1/velocity",
                    "joint1/position",
                ),
            ),
        )

    def list_controller_types(self) -> tuple[ControllerType, ...]:
        """Return test controller types."""
        return (
            ControllerType(
                name="joint_state_broadcaster/JointStateBroadcaster",
                base_class="controller_interface::ControllerInterface",
            ),
        )

    def load_controller(self, name: str) -> ControlResult:
        """Return a successful test load result."""
        return ControlResult(
            ok=True,
            message=f"Loaded '{name}'.",
        )

    def configure_controller(self, name: str) -> ControlResult:
        """Return a successful test configure result."""
        return ControlResult(
            ok=True,
            message=f"Configured '{name}'.",
        )

    def activate_controller(self, name: str) -> ControlResult:
        """Return a successful test activation result."""
        return ControlResult(
            ok=True,
            message=f"Activated '{name}'.",
        )

    def deactivate_controller(self, name: str) -> ControlResult:
        """Return a successful test deactivation result."""
        return ControlResult(
            ok=True,
            message=f"Deactivated '{name}'.",
        )

    def switch_controllers(
        self,
        plan: ControllerSwitchPlan,
    ) -> ControlResult:
        """Return a successful test switch result."""
        return ControlResult(
            ok=True,
            message=(
                f"Activate={plan.activate}, "
                f"Deactivate={plan.deactivate}"
            ),
        )

    def unload_controller(self, name: str) -> ControlResult:
        """Return a successful test unload result."""
        return ControlResult(
            ok=True,
            message=f"Unloaded '{name}'.",
        )

    def cleanup_controller(self, name: str) -> ControlResult:
        """Return a successful test cleanup result."""
        return ControlResult(
            ok=True,
            message=f"Cleaned up '{name}'.",
        )

    def set_hardware_component_state(
        self,
        name: str,
        state_id: int,
        state_label: str = "",
    ) -> ControlResult:
        """Return a successful hardware state change result."""
        return ControlResult(
            ok=True,
            message=(
                f"Hardware '{name}' changed to "
                f"{state_label or state_id}."
            ),
        )

    def list_hardware_components(self) -> tuple[HardwareComponent, ...]:
        """Return test hardware components."""
        return (
            HardwareComponent(
                name="MockSystem",
                component_type="system",
                is_async=False,
                rw_rate=100,
                plugin_name="mock_components/GenericSystem",
                state_id=3,
                state_label="active",
            ),
        )

    def list_hardware_interfaces(
        self,
    ) -> tuple[tuple[HardwareInterface, ...], tuple[HardwareInterface, ...]]:
        """Return test command and state interfaces."""
        command_interfaces = (
            HardwareInterface(
                name="joint1/position",
                data_type="double",
                is_available=True,
                is_claimed=False,
            ),
        )

        state_interfaces = (
            HardwareInterface(
                name="joint1/position",
                data_type="double",
                is_available=True,
                is_claimed=False,
            ),
            HardwareInterface(
                name="joint1/velocity",
                data_type="double",
                is_available=True,
                is_claimed=False,
            ),
        )

        return command_interfaces, state_interfaces


def test_list_controllers() -> None:
    """Return controllers through the application service."""
    service = Ros2ControlService(FakeRos2ControlAdapter())

    controllers = service.list_controllers()

    assert len(controllers) == 1
    assert controllers[0].name == "joint_state_broadcaster"
    assert controllers[0].state == "active"


def test_get_controller() -> None:
    """Return a controller by name."""
    service = Ros2ControlService(FakeRos2ControlAdapter())

    controller = service.get_controller("joint_state_broadcaster")

    assert controller is not None
    assert controller.name == "joint_state_broadcaster"


def test_get_unknown_controller() -> None:
    """Return None when the requested controller does not exist."""
    service = Ros2ControlService(FakeRos2ControlAdapter())

    assert service.get_controller("missing_controller") is None


def test_list_controller_types() -> None:
    """Return controller types through the application service."""
    service = Ros2ControlService(FakeRos2ControlAdapter())

    controller_types = service.list_controller_types()

    assert len(controller_types) == 1
    assert (
        controller_types[0].name
        == "joint_state_broadcaster/JointStateBroadcaster"
    )


def test_list_hardware_components() -> None:
    """Return hardware components through the application service."""
    service = Ros2ControlService(FakeRos2ControlAdapter())

    components = service.list_hardware_components()

    assert len(components) == 1
    assert components[0].name == "MockSystem"
    assert components[0].state_label == "active"


def test_list_hardware_interfaces() -> None:
    """Return hardware interfaces through the application service."""
    service = Ros2ControlService(FakeRos2ControlAdapter())

    command_interfaces, state_interfaces = service.list_hardware_interfaces()

    assert len(command_interfaces) == 1
    assert len(state_interfaces) == 2
    assert command_interfaces[0].name == "joint1/position"


def test_get_hardware_component() -> None:
    """Return a hardware component by name."""
    service = Ros2ControlService(FakeRos2ControlAdapter())

    component = service.get_hardware_component("MockSystem")

    assert component is not None
    assert component.name == "MockSystem"
    assert component.state_label == "active"


def test_get_unknown_hardware_component() -> None:
    """Return None when the hardware component does not exist."""
    service = Ros2ControlService(FakeRos2ControlAdapter())

    assert service.get_hardware_component("missing_hardware") is None


def test_list_claimed_command_interfaces() -> None:
    """Return only claimed command interfaces."""
    service = Ros2ControlService(FakeRos2ControlAdapter())

    claimed = service.list_claimed_command_interfaces()

    assert claimed == ()


def test_list_unclaimed_command_interfaces() -> None:
    """Return only unclaimed command interfaces."""
    service = Ros2ControlService(FakeRos2ControlAdapter())

    unclaimed = service.list_unclaimed_command_interfaces()

    assert len(unclaimed) == 1
    assert unclaimed[0].name == "joint1/position"


def test_list_resource_claims() -> None:
    """Return resource claims from claimed controller interfaces."""

    class ClaimAdapter(FakeRos2ControlAdapter):
        """Provide a controller with a claimed command interface."""

        def list_controllers(self) -> tuple[Controller, ...]:
            """Return a controller with one claimed interface."""
            return (
                Controller(
                    name="arm_controller",
                    controller_type=(
                        "joint_trajectory_controller/"
                        "JointTrajectoryController"
                    ),
                    state="active",
                    claimed_interfaces=("joint1/position",),
                ),
            )

    service = Ros2ControlService(ClaimAdapter())

    claims = service.list_resource_claims()

    assert len(claims) == 1
    assert claims[0].controller_name == "arm_controller"
    assert claims[0].interface_name == "joint1/position"


def test_list_controller_dependencies() -> None:
    """Return dependencies derived from controller chain connections."""
    from ros2_control_mcp.domain.controllers import ChainConnection

    class ChainAdapter(FakeRos2ControlAdapter):
        """Provide chained controller data."""

        def list_controllers(self) -> tuple[Controller, ...]:
            """Return a controller with one chain dependency."""
            return (
                Controller(
                    name="outer_controller",
                    controller_type="test/OuterController",
                    state="active",
                    chain_connections=(
                        ChainConnection(
                            name="inner_controller",
                            reference_interfaces=(
                                "inner_controller/joint1/position",
                            ),
                        ),
                    ),
                ),
            )

    service = Ros2ControlService(ChainAdapter())

    dependencies = service.list_controller_dependencies()

    assert len(dependencies) == 1
    assert dependencies[0].controller_name == "outer_controller"
    assert dependencies[0].depends_on == "inner_controller"


def test_load_controller() -> None:
    """Load a controller through the application service."""
    service = Ros2ControlService(FakeRos2ControlAdapter())

    result = service.load_controller("test_controller")

    assert result.ok is True
    assert result.message == "Loaded 'test_controller'."


def test_configure_controller() -> None:
    """Configure a controller through the application service."""
    service = Ros2ControlService(FakeRos2ControlAdapter())

    result = service.configure_controller("test_controller")

    assert result.ok is True
    assert result.message == "Configured 'test_controller'."


def test_activate_controller() -> None:
    """Activate a controller through the application service."""
    service = Ros2ControlService(FakeRos2ControlAdapter())

    result = service.activate_controller("test_controller")

    assert result.ok is True
    assert result.message == "Activated 'test_controller'."


def test_deactivate_controller() -> None:
    """Deactivate a controller through the application service."""
    service = Ros2ControlService(FakeRos2ControlAdapter())

    result = service.deactivate_controller("test_controller")

    assert result.ok is True
    assert result.message == "Deactivated 'test_controller'."


def test_execute_controller_switch() -> None:
    """Execute a validated controller switch."""
    service = Ros2ControlService(FakeRos2ControlAdapter())

    plan = ControllerSwitchPlan()

    result = service.execute_controller_switch(plan)

    assert result.ok is True


def test_execute_controller_switch_blocks_force_auto() -> None:
    """Block FORCE_AUTO execution in the current release."""
    from ros2_control_mcp.domain.safety import SwitchStrictness

    service = Ros2ControlService(FakeRos2ControlAdapter())

    plan = ControllerSwitchPlan(
        strictness=SwitchStrictness.FORCE_AUTO,
    )

    result = service.execute_controller_switch(plan)

    assert result.ok is False
    assert "not enabled" in result.message


def test_unload_controller() -> None:
    """Unload a controller through the application service."""
    service = Ros2ControlService(FakeRos2ControlAdapter())

    result = service.unload_controller("test_controller")

    assert result.ok is True
    assert result.message == "Unloaded 'test_controller'."


def test_cleanup_controller() -> None:
    """Cleanup a controller through the application service."""
    service = Ros2ControlService(FakeRos2ControlAdapter())

    result = service.cleanup_controller("test_controller")

    assert result.ok is True
    assert result.message == "Cleaned up 'test_controller'."


def test_set_hardware_component_state() -> None:
    """Change hardware state through the application service."""
    service = Ros2ControlService(FakeRos2ControlAdapter())

    result = service.set_hardware_component_state(
        name="MockSystem",
        state_id=3,
        state_label="active",
    )

    assert result.ok is True
    assert "MockSystem" in result.message
