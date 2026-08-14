"""Tests for the ros2_control application service."""

from ros2_control_mcp.application.control.service import Ros2ControlService
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
