"""Integration test for a real ros2_control MockSystem runtime."""

from collections.abc import Iterator
from contextlib import contextmanager, ExitStack
import os
from pathlib import Path
import signal
import subprocess
from typing import TextIO

from ament_index_python.packages import get_package_prefix
from domain_coordinator import domain_id

from ros2_control_mcp.config.settings import Settings
from ros2_control_mcp.ros.jazzy.adapter import JazzyRos2ControlAdapter


FIXTURES = Path(__file__).parents[1] / "fixtures"


def _package_executable(package: str, executable: str) -> str:
    """Return the installed path of a ROS package executable."""
    return str(Path(get_package_prefix(package)) / "lib" / package / executable)


def _start_process(
    command: list[str],
    environment: dict[str, str],
) -> subprocess.Popen[str]:
    """Start a ROS process in its own process group."""
    return subprocess.Popen(
        command,
        env=environment,
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        text=True,
        start_new_session=True,
    )


def _stop_process(process: subprocess.Popen[str]) -> str:
    """Stop a ROS process and return its captured output."""
    if process.poll() is None:
        os.killpg(process.pid, signal.SIGINT)

        try:
            process.wait(timeout=5.0)
        except subprocess.TimeoutExpired:
            os.killpg(process.pid, signal.SIGKILL)
            process.wait(timeout=5.0)

    output: TextIO | None = process.stdout
    return output.read() if output is not None else ""


@contextmanager
def _managed_process(
    command: list[str],
    environment: dict[str, str],
) -> Iterator[subprocess.Popen[str]]:
    """Start a ROS process and guarantee an attempted cleanup."""
    process = _start_process(command, environment)

    try:
        yield process
    finally:
        _stop_process(process)


def test_list_mock_system_from_real_controller_manager(
    monkeypatch,
    tmp_path: Path,
) -> None:
    """Read MockSystem through a real controller_manager ROS service."""
    robot_description = (FIXTURES / "mock_runtime_robot.urdf").read_text()
    controller_parameters = FIXTURES / "mock_controller_manager.yaml"

    ros_log_directory = tmp_path / "ros-logs"
    ros_log_directory.mkdir()

    with domain_id() as reserved_domain_id, ExitStack() as processes:
        environment = os.environ.copy()
        environment["ROS_DOMAIN_ID"] = str(reserved_domain_id)
        environment["ROS_LOG_DIR"] = str(ros_log_directory)
        monkeypatch.setenv("ROS_DOMAIN_ID", str(reserved_domain_id))
        monkeypatch.setenv("ROS_LOG_DIR", str(ros_log_directory))

        processes.enter_context(
            _managed_process(
                [
                    _package_executable(
                        "robot_state_publisher",
                        "robot_state_publisher",
                    ),
                    "--ros-args",
                    "-p",
                    f"robot_description:={robot_description}",
                ],
                environment,
            )
        )
        processes.enter_context(
            _managed_process(
                [
                    _package_executable(
                        "controller_manager",
                        "ros2_control_node",
                    ),
                    "--ros-args",
                    "--params-file",
                    str(controller_parameters),
                ],
                environment,
            )
        )

        adapter = JazzyRos2ControlAdapter(
            Settings(service_timeout_seconds=15.0)
        )
        components = adapter.list_hardware_components()

        mock_system = next(
            component
            for component in components
            if component.name == "MockSystem"
        )

        assert mock_system.component_type == "system"
        assert mock_system.plugin_name == "mock_components/GenericSystem"
        assert mock_system.state_id == 3
        assert mock_system.state_label == "active"
        assert any(
            interface.name == "joint1/position"
            for interface in mock_system.command_interfaces
        )
        assert any(
            interface.name == "joint1/position"
            for interface in mock_system.state_interfaces
        )


def test_list_hardware_interfaces_from_real_controller_manager(
    monkeypatch,
    tmp_path: Path,
) -> None:
    """Read hardware interfaces through a real controller_manager service."""
    robot_description = (FIXTURES / "mock_runtime_robot.urdf").read_text()
    controller_parameters = FIXTURES / "mock_controller_manager.yaml"

    ros_log_directory = tmp_path / "ros-logs"
    ros_log_directory.mkdir()

    with domain_id() as reserved_domain_id, ExitStack() as processes:
        environment = os.environ.copy()
        environment["ROS_DOMAIN_ID"] = str(reserved_domain_id)
        environment["ROS_LOG_DIR"] = str(ros_log_directory)
        monkeypatch.setenv("ROS_DOMAIN_ID", str(reserved_domain_id))
        monkeypatch.setenv("ROS_LOG_DIR", str(ros_log_directory))

        processes.enter_context(
            _managed_process(
                [
                    _package_executable(
                        "robot_state_publisher",
                        "robot_state_publisher",
                    ),
                    "--ros-args",
                    "-p",
                    f"robot_description:={robot_description}",
                ],
                environment,
            )
        )
        processes.enter_context(
            _managed_process(
                [
                    _package_executable(
                        "controller_manager",
                        "ros2_control_node",
                    ),
                    "--ros-args",
                    "--params-file",
                    str(controller_parameters),
                ],
                environment,
            )
        )

        adapter = JazzyRos2ControlAdapter(
            Settings(service_timeout_seconds=15.0)
        )
        command_interfaces, state_interfaces = (
            adapter.list_hardware_interfaces()
        )

        position_command_interface = next(
            interface
            for interface in command_interfaces
            if interface.name == "joint1/position"
        )
        position_state_interface = next(
            interface
            for interface in state_interfaces
            if interface.name == "joint1/position"
        )

        assert position_command_interface.is_available is True
        assert position_command_interface.is_claimed is False
        assert position_state_interface.is_available is True
        assert position_state_interface.is_claimed is False


def test_load_and_configure_controller_with_real_controller_manager(
    monkeypatch,
    tmp_path: Path,
) -> None:
    """Load and configure a controller through real controller_manager services."""
    robot_description = (FIXTURES / "mock_runtime_robot.urdf").read_text()
    controller_parameters = FIXTURES / "mock_controller_manager.yaml"
    controller_name = "test_position_controller"

    ros_log_directory = tmp_path / "ros-logs"
    ros_log_directory.mkdir()

    with domain_id() as reserved_domain_id, ExitStack() as processes:
        environment = os.environ.copy()
        environment["ROS_DOMAIN_ID"] = str(reserved_domain_id)
        environment["ROS_LOG_DIR"] = str(ros_log_directory)
        monkeypatch.setenv("ROS_DOMAIN_ID", str(reserved_domain_id))
        monkeypatch.setenv("ROS_LOG_DIR", str(ros_log_directory))

        processes.enter_context(
            _managed_process(
                [
                    _package_executable(
                        "robot_state_publisher",
                        "robot_state_publisher",
                    ),
                    "--ros-args",
                    "-p",
                    f"robot_description:={robot_description}",
                ],
                environment,
            )
        )
        processes.enter_context(
            _managed_process(
                [
                    _package_executable(
                        "controller_manager",
                        "ros2_control_node",
                    ),
                    "--ros-args",
                    "--params-file",
                    str(controller_parameters),
                ],
                environment,
            )
        )

        adapter = JazzyRos2ControlAdapter(
            Settings(service_timeout_seconds=15.0)
        )

        load_result = adapter.load_controller(controller_name)
        assert load_result.ok is True

        loaded_controller = next(
            controller
            for controller in adapter.list_controllers()
            if controller.name == controller_name
        )
        assert loaded_controller.name == controller_name

        configure_result = adapter.configure_controller(controller_name)
        assert configure_result.ok is True

        configured_controller = next(
            controller
            for controller in adapter.list_controllers()
            if controller.name == controller_name
        )
        assert configured_controller.name == controller_name
        assert configured_controller.state != "active"
        assert configured_controller.state == "inactive"


def test_cleanup_and_unload_controller_with_real_controller_manager(
    monkeypatch,
    tmp_path: Path,
) -> None:
    """Cleanup and unload a controller through real controller_manager services."""
    robot_description = (FIXTURES / "mock_runtime_robot.urdf").read_text()
    controller_parameters = FIXTURES / "mock_controller_manager.yaml"
    controller_name = "test_position_controller"

    ros_log_directory = tmp_path / "ros-logs"
    ros_log_directory.mkdir()

    with domain_id() as reserved_domain_id, ExitStack() as processes:
        environment = os.environ.copy()
        environment["ROS_DOMAIN_ID"] = str(reserved_domain_id)
        environment["ROS_LOG_DIR"] = str(ros_log_directory)
        monkeypatch.setenv("ROS_DOMAIN_ID", str(reserved_domain_id))
        monkeypatch.setenv("ROS_LOG_DIR", str(ros_log_directory))

        processes.enter_context(
            _managed_process(
                [
                    _package_executable(
                        "robot_state_publisher",
                        "robot_state_publisher",
                    ),
                    "--ros-args",
                    "-p",
                    f"robot_description:={robot_description}",
                ],
                environment,
            )
        )
        processes.enter_context(
            _managed_process(
                [
                    _package_executable(
                        "controller_manager",
                        "ros2_control_node",
                    ),
                    "--ros-args",
                    "--params-file",
                    str(controller_parameters),
                ],
                environment,
            )
        )

        adapter = JazzyRos2ControlAdapter(
            Settings(service_timeout_seconds=15.0)
        )

        load_result = adapter.load_controller(controller_name)
        assert load_result.ok is True
        assert any(
            controller.name == controller_name
            for controller in adapter.list_controllers()
        )

        configure_result = adapter.configure_controller(controller_name)
        assert configure_result.ok is True

        configured_controller = next(
            controller
            for controller in adapter.list_controllers()
            if controller.name == controller_name
        )
        assert configured_controller.state == "inactive"

        cleanup_result = adapter.cleanup_controller(controller_name)
        assert cleanup_result.ok is True

        cleaned_controller = next(
            controller
            for controller in adapter.list_controllers()
            if controller.name == controller_name
        )
        assert cleaned_controller.state == "unconfigured"

        unload_result = adapter.unload_controller(controller_name)
        assert unload_result.ok is True
        assert all(
            controller.name != controller_name
            for controller in adapter.list_controllers()
        )


def test_activate_and_deactivate_controller_with_real_controller_manager(
    monkeypatch,
    tmp_path: Path,
) -> None:
    """Activate and deactivate a controller while tracking its interface claim."""
    robot_description = (FIXTURES / "mock_runtime_robot.urdf").read_text()
    controller_parameters = FIXTURES / "mock_controller_manager.yaml"
    controller_name = "test_position_controller"

    ros_log_directory = tmp_path / "ros-logs"
    ros_log_directory.mkdir()

    with domain_id() as reserved_domain_id, ExitStack() as processes:
        environment = os.environ.copy()
        environment["ROS_DOMAIN_ID"] = str(reserved_domain_id)
        environment["ROS_LOG_DIR"] = str(ros_log_directory)
        monkeypatch.setenv("ROS_DOMAIN_ID", str(reserved_domain_id))
        monkeypatch.setenv("ROS_LOG_DIR", str(ros_log_directory))

        processes.enter_context(
            _managed_process(
                [
                    _package_executable(
                        "robot_state_publisher",
                        "robot_state_publisher",
                    ),
                    "--ros-args",
                    "-p",
                    f"robot_description:={robot_description}",
                ],
                environment,
            )
        )
        processes.enter_context(
            _managed_process(
                [
                    _package_executable(
                        "controller_manager",
                        "ros2_control_node",
                    ),
                    "--ros-args",
                    "--params-file",
                    str(controller_parameters),
                ],
                environment,
            )
        )

        adapter = JazzyRos2ControlAdapter(
            Settings(service_timeout_seconds=15.0)
        )

        load_result = adapter.load_controller(controller_name)
        assert load_result.ok is True

        configure_result = adapter.configure_controller(controller_name)
        assert configure_result.ok is True

        configured_controller = next(
            controller
            for controller in adapter.list_controllers()
            if controller.name == controller_name
        )
        assert configured_controller.state == "inactive"

        command_interfaces, _ = adapter.list_hardware_interfaces()
        position_interface = next(
            interface
            for interface in command_interfaces
            if interface.name == "joint1/position"
        )
        assert position_interface.is_available is True
        assert position_interface.is_claimed is False

        activation_succeeded = False
        activation_result = adapter.activate_controller(controller_name)
        assert activation_result.ok is True
        activation_succeeded = True

        try:
            active_controller = next(
                controller
                for controller in adapter.list_controllers()
                if controller.name == controller_name
            )
            assert active_controller.state == "active"

            command_interfaces, _ = adapter.list_hardware_interfaces()
            position_interface = next(
                interface
                for interface in command_interfaces
                if interface.name == "joint1/position"
            )
            assert position_interface.is_available is True
            assert position_interface.is_claimed is True
        finally:
            if activation_succeeded:
                deactivation_result = adapter.deactivate_controller(
                    controller_name
                )
                assert deactivation_result.ok is True

        deactivated_controller = next(
            controller
            for controller in adapter.list_controllers()
            if controller.name == controller_name
        )
        assert deactivated_controller.state == "inactive"

        command_interfaces, _ = adapter.list_hardware_interfaces()
        position_interface = next(
            interface
            for interface in command_interfaces
            if interface.name == "joint1/position"
        )
        assert position_interface.is_available is True
        assert position_interface.is_claimed is False
