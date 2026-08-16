"""ROS 2 Jazzy controller_manager control operations."""

import rclpy
from controller_manager_msgs.srv import CleanupController, ConfigureController, LoadController, UnloadController
from rclpy.node import Node

from ros2_control_mcp.config.settings import Settings
from ros2_control_mcp.domain.control import ControlResult


class JazzyControllerManagerControl:
    """Provide state-changing controller_manager operations for ROS 2 Jazzy."""

    def __init__(self, settings: Settings | None = None) -> None:
        """Initialize controller_manager control operations."""
        self._settings = settings or Settings()

    def load_controller(self, name: str) -> ControlResult:
        """Load a controller through the official Jazzy service."""
        return self._call_named_service(
            service_type=LoadController,
            service_suffix="load_controller",
            name=name,
            failure_message=f"Failed to load '{name}'.",
        )

    def configure_controller(self, name: str) -> ControlResult:
        """Configure a controller through the official Jazzy service."""
        return self._call_named_service(
            service_type=ConfigureController,
            service_suffix="configure_controller",
            name=name,
            failure_message=f"Failed to configure '{name}'.",
        )

    def unload_controller(self, name: str) -> ControlResult:
        """Unload a controller through the official Jazzy service."""
        return self._call_named_service(
            service_type=UnloadController,
            service_suffix="unload_controller",
            name=name,
            failure_message=f"Failed to unload '{name}'.",
        )

    def cleanup_controller(self, name: str) -> ControlResult:
        """Cleanup a controller through the official Jazzy service."""
        return self._call_named_service(
            service_type=CleanupController,
            service_suffix="cleanup_controller",
            name=name,
            failure_message=f"Failed to cleanup '{name}'.",
        )

    def _call_named_service(
        self,
        *,
        service_type: type,
        service_suffix: str,
        name: str,
        failure_message: str,
    ) -> ControlResult:
        """Call a controller_manager service that accepts a controller name."""
        initialized_here = False

        if not rclpy.ok():
            rclpy.init()
            initialized_here = True

        node = Node("ros2_control_mcp_control_client")

        try:
            service_name = (
                f"{self._settings.default_controller_manager}/{service_suffix}"
            )
            client = node.create_client(service_type, service_name)

            if not client.wait_for_service(
                timeout_sec=self._settings.service_timeout_seconds
            ):
                raise TimeoutError(
                    f"Service '{service_name}' is not available."
                )

            request = service_type.Request()
            request.name = name

            future = client.call_async(request)
            rclpy.spin_until_future_complete(
                node,
                future,
                timeout_sec=self._settings.service_timeout_seconds,
            )

            if not future.done():
                raise TimeoutError(
                    f"Service call to '{service_name}' timed out."
                )

            response = future.result()
            if response is None:
                raise RuntimeError(
                    f"Service call to '{service_name}' failed."
                )

            return ControlResult(
                ok=response.ok,
                message=None if response.ok else failure_message,
            )
        finally:
            node.destroy_node()

            if initialized_here:
                rclpy.shutdown()


    def switch_controllers(
        self,
        *,
        activate: tuple[str, ...] = (),
        deactivate: tuple[str, ...] = (),
        strictness: int = 2,
        activate_asap: bool = False,
        timeout_seconds: float = 5.0,
    ) -> ControlResult:
        """Switch controllers through the official Jazzy service."""
        from controller_manager_msgs.srv import SwitchController

        initialized_here = False

        if not rclpy.ok():
            rclpy.init()
            initialized_here = True

        node = Node("ros2_control_mcp_control_client")

        try:
            service_name = (
                f"{self._settings.default_controller_manager}/switch_controller"
            )
            client = node.create_client(SwitchController, service_name)

            if not client.wait_for_service(
                timeout_sec=self._settings.service_timeout_seconds
            ):
                raise TimeoutError(
                    f"Service '{service_name}' is not available."
                )

            request = SwitchController.Request()
            request.activate_controllers = list(activate)
            request.deactivate_controllers = list(deactivate)
            request.strictness = strictness
            request.activate_asap = activate_asap

            seconds = int(timeout_seconds)
            nanoseconds = int((timeout_seconds - seconds) * 1_000_000_000)

            request.timeout.sec = seconds
            request.timeout.nanosec = nanoseconds

            future = client.call_async(request)
            rclpy.spin_until_future_complete(
                node,
                future,
                timeout_sec=self._settings.service_timeout_seconds,
            )

            if not future.done():
                raise TimeoutError(
                    f"Service call to '{service_name}' timed out."
                )

            response = future.result()
            if response is None:
                raise RuntimeError(
                    f"Service call to '{service_name}' failed."
                )

            return ControlResult(
                ok=response.ok,
                message=response.message or None,
            )
        finally:
            node.destroy_node()

            if initialized_here:
                rclpy.shutdown()


    def set_hardware_component_state(
        self,
        name: str,
        state_id: int,
        state_label: str = "",
    ) -> ControlResult:
        """Change hardware component lifecycle state."""
        from controller_manager_msgs.srv import SetHardwareComponentState
        from lifecycle_msgs.msg import State

        initialized_here = False

        if not rclpy.ok():
            rclpy.init()
            initialized_here = True

        node = Node("ros2_control_mcp_hardware_control_client")

        try:
            service_name = (
                f"{self._settings.default_controller_manager}/"
                "set_hardware_component_state"
            )

            client = node.create_client(
                SetHardwareComponentState,
                service_name,
            )

            if not client.wait_for_service(
                timeout_sec=self._settings.service_timeout_seconds
            ):
                raise TimeoutError(
                    f"Service '{service_name}' is not available."
                )

            request = SetHardwareComponentState.Request()
            request.name = name

            request.target_state.id = state_id
            request.target_state.label = state_label

            future = client.call_async(request)

            rclpy.spin_until_future_complete(
                node,
                future,
                timeout_sec=self._settings.service_timeout_seconds,
            )

            if not future.done():
                raise TimeoutError(
                    f"Service call to '{service_name}' timed out."
                )

            response = future.result()

            if response is None:
                raise RuntimeError(
                    f"Service call to '{service_name}' failed."
                )

            return ControlResult(
                ok=response.ok,
                message=None if response.ok else (
                    f"Failed to change hardware '{name}'."
                ),
            )

        finally:
            node.destroy_node()

            if initialized_here:
                rclpy.shutdown()
