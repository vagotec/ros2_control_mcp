"""Tests for the ros2_control application service."""

from ros2_control_mcp.application.control.service import Ros2ControlService
from ros2_control_mcp.domain.controllers import Controller, ControllerType
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
