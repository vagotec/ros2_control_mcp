"""ROS 2 Jazzy implementation of the ros2_control adapter."""

from ros2_control_mcp.domain.controllers import Controller
from ros2_control_mcp.ros.adapter import Ros2ControlAdapter


class JazzyRos2ControlAdapter(Ros2ControlAdapter):
    """Provide ros2_control access for ROS 2 Jazzy."""

    def list_controllers(self) -> tuple[Controller, ...]:
        """Return controllers from the Jazzy controller manager."""

        raise NotImplementedError(
            "Controller manager access will be implemented in Phase 2."
        )
