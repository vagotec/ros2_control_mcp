"""ROS 2 Jazzy implementation of the ros2_control adapter."""

import rclpy
from controller_manager_msgs.msg import (
    ControllerState,
    HardwareComponentState,
    HardwareInterface as RosHardwareInterface,
)
from controller_manager_msgs.srv import (
    ListControllers,
    ListControllerTypes,
    ListHardwareComponents,
    ListHardwareInterfaces,
)
from rclpy.node import Node

from ros2_control_mcp.config.settings import Settings
from ros2_control_mcp.domain.controllers import (
    ChainConnection,
    Controller,
    ControllerType,
)
from ros2_control_mcp.domain.hardware import HardwareComponent
from ros2_control_mcp.domain.interfaces import HardwareInterface
from ros2_control_mcp.ros.adapter import Ros2ControlAdapter


class JazzyRos2ControlAdapter(Ros2ControlAdapter):
    """Provide ros2_control access for ROS 2 Jazzy."""

    def __init__(self, settings: Settings | None = None) -> None:
        """Initialize the adapter with runtime settings."""
        self._settings = settings or Settings()

    def list_controllers(self) -> tuple[Controller, ...]:
        """Return controllers from the Jazzy controller manager."""
        initialized_here = False

        if not rclpy.ok():
            rclpy.init()
            initialized_here = True

        node = Node("ros2_control_mcp_client")

        try:
            service_name = (
                f"{self._settings.default_controller_manager}/list_controllers"
            )
            client = node.create_client(ListControllers, service_name)

            if not client.wait_for_service(
                timeout_sec=self._settings.service_timeout_seconds
            ):
                raise TimeoutError(
                    f"Service '{service_name}' is not available."
                )

            future = client.call_async(ListControllers.Request())
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

            return tuple(
                self._to_controller(controller)
                for controller in response.controller
            )
        finally:
            node.destroy_node()

            if initialized_here:
                rclpy.shutdown()

    def list_controller_types(self) -> tuple[ControllerType, ...]:
        """Return controller types from the Jazzy controller manager."""
        initialized_here = False

        if not rclpy.ok():
            rclpy.init()
            initialized_here = True

        node = Node("ros2_control_mcp_client")

        try:
            service_name = (
                f"{self._settings.default_controller_manager}/list_controller_types"
            )
            client = node.create_client(ListControllerTypes, service_name)

            if not client.wait_for_service(
                timeout_sec=self._settings.service_timeout_seconds
            ):
                raise TimeoutError(
                    f"Service '{service_name}' is not available."
                )

            future = client.call_async(ListControllerTypes.Request())
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

            return tuple(
                ControllerType(name=name, base_class=base_class)
                for name, base_class in zip(
                    response.types,
                    response.base_classes,
                    strict=True,
                )
            )
        finally:
            node.destroy_node()

            if initialized_here:
                rclpy.shutdown()

    def list_hardware_components(self) -> tuple[HardwareComponent, ...]:
        """Return hardware components from the Jazzy resource manager."""
        initialized_here = False

        if not rclpy.ok():
            rclpy.init()
            initialized_here = True

        node = Node("ros2_control_mcp_client")

        try:
            service_name = (
                f"{self._settings.default_controller_manager}/"
                "list_hardware_components"
            )
            client = node.create_client(ListHardwareComponents, service_name)

            if not client.wait_for_service(
                timeout_sec=self._settings.service_timeout_seconds
            ):
                raise TimeoutError(
                    f"Service '{service_name}' is not available."
                )

            future = client.call_async(ListHardwareComponents.Request())
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

            return tuple(
                self._to_hardware_component(component)
                for component in response.component
            )
        finally:
            node.destroy_node()

            if initialized_here:
                rclpy.shutdown()

    def list_hardware_interfaces(
        self,
    ) -> tuple[tuple[HardwareInterface, ...], tuple[HardwareInterface, ...]]:
        """Return command and state interfaces from the Jazzy resource manager."""
        initialized_here = False

        if not rclpy.ok():
            rclpy.init()
            initialized_here = True

        node = Node("ros2_control_mcp_client")

        try:
            service_name = (
                f"{self._settings.default_controller_manager}/"
                "list_hardware_interfaces"
            )
            client = node.create_client(ListHardwareInterfaces, service_name)

            if not client.wait_for_service(
                timeout_sec=self._settings.service_timeout_seconds
            ):
                raise TimeoutError(
                    f"Service '{service_name}' is not available."
                )

            future = client.call_async(ListHardwareInterfaces.Request())
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

            command_interfaces = tuple(
                self._to_hardware_interface(interface)
                for interface in response.command_interfaces
            )
            state_interfaces = tuple(
                self._to_hardware_interface(interface)
                for interface in response.state_interfaces
            )

            return command_interfaces, state_interfaces
        finally:
            node.destroy_node()

            if initialized_here:
                rclpy.shutdown()

    @staticmethod
    def _to_controller(controller: ControllerState) -> Controller:
        """Convert a Jazzy ControllerState message to a domain model."""
        return Controller(
            name=controller.name,
            controller_type=controller.type,
            state=controller.state,
            is_async=controller.is_async,
            update_rate=controller.update_rate,
            claimed_interfaces=tuple(controller.claimed_interfaces),
            required_command_interfaces=tuple(
                controller.required_command_interfaces
            ),
            required_state_interfaces=tuple(
                controller.required_state_interfaces
            ),
            is_chainable=controller.is_chainable,
            is_chained=controller.is_chained,
            exported_state_interfaces=tuple(
                controller.exported_state_interfaces
            ),
            reference_interfaces=tuple(controller.reference_interfaces),
            chain_connections=tuple(
                ChainConnection(
                    name=connection.name,
                    reference_interfaces=tuple(
                        connection.reference_interfaces
                    ),
                )
                for connection in controller.chain_connections
            ),
        )

    @classmethod
    def _to_hardware_component(
        cls,
        component: HardwareComponentState,
    ) -> HardwareComponent:
        """Convert a Jazzy HardwareComponentState to a domain model."""
        return HardwareComponent(
            name=component.name,
            component_type=component.type,
            is_async=component.is_async,
            rw_rate=component.rw_rate,
            plugin_name=component.plugin_name,
            state_id=component.state.id,
            state_label=component.state.label,
            command_interfaces=tuple(
                cls._to_hardware_interface(interface)
                for interface in component.command_interfaces
            ),
            state_interfaces=tuple(
                cls._to_hardware_interface(interface)
                for interface in component.state_interfaces
            ),
        )

    @staticmethod
    def _to_hardware_interface(
        interface: RosHardwareInterface,
    ) -> HardwareInterface:
        """Convert a Jazzy HardwareInterface to a domain model."""
        return HardwareInterface(
            name=interface.name,
            data_type=interface.data_type,
            is_available=interface.is_available,
            is_claimed=interface.is_claimed,
        )
