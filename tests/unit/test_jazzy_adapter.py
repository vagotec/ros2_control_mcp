"""Tests for the ROS 2 Jazzy ros2_control adapter."""

from controller_manager_msgs.msg import ChainConnection, ControllerState

from ros2_control_mcp.ros.jazzy.adapter import JazzyRos2ControlAdapter


def test_controller_state_conversion() -> None:
    """Convert a Jazzy ControllerState into the domain model."""
    message = ControllerState()
    message.name = "arm_controller"
    message.type = "joint_trajectory_controller/JointTrajectoryController"
    message.state = "active"
    message.is_async = False
    message.update_rate = 100
    message.claimed_interfaces = ["joint1/position"]
    message.required_command_interfaces = ["joint1/position"]
    message.required_state_interfaces = [
        "joint1/position",
        "joint1/velocity",
    ]
    message.is_chainable = True
    message.is_chained = True
    message.exported_state_interfaces = ["joint1/position"]
    message.reference_interfaces = ["arm_controller/joint1/position"]

    connection = ChainConnection()
    connection.name = "upstream_controller"
    connection.reference_interfaces = ["arm_controller/joint1/position"]
    message.chain_connections = [connection]

    controller = JazzyRos2ControlAdapter._to_controller(message)

    assert controller.name == "arm_controller"
    assert controller.state == "active"
    assert controller.update_rate == 100
    assert controller.claimed_interfaces == ("joint1/position",)
    assert controller.is_chainable is True
    assert controller.is_chained is True
    assert len(controller.chain_connections) == 1
    assert controller.chain_connections[0].name == "upstream_controller"
