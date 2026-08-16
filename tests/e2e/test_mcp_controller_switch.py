"""End-to-end smoke test for MCP controller switching on real ROS 2."""

import asyncio
from collections.abc import Iterator
from contextlib import contextmanager, ExitStack
import os
from pathlib import Path
import signal
import subprocess
from typing import TextIO
from typing import Any

from ament_index_python.packages import get_package_prefix
from domain_coordinator import domain_id
from mcp.client import Client
from mcp.types import CallToolResult

from ros2_control_mcp.server import create_server


FIXTURES = Path(__file__).parents[1] / "fixtures"


def _package_executable(package: str, executable: str) -> str:
    """Return the installed path of a ROS package executable."""
    return str(Path(get_package_prefix(package)) / "lib" / package / executable)


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
    process = subprocess.Popen(
        command,
        env=environment,
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        text=True,
        start_new_session=True,
    )

    try:
        yield process
    finally:
        _stop_process(process)


def _structured_result(result: CallToolResult) -> dict[str, Any]:
    """Return a successful MCP tool's structured result."""
    assert result.is_error is False
    assert isinstance(result.structured_content, dict)
    return result.structured_content


async def _run_mcp_switch_scenario() -> None:
    """Exercise controller switching entirely through an MCP client."""
    controller_name = "test_position_controller"
    server = create_server()

    async with Client(
        server,
        mode="legacy",
        raise_exceptions=True,
    ) as client:
        load_result = _structured_result(
            await client.call_tool(
                "load_controller",
                {"name": controller_name},
            )
        )
        assert load_result["ok"] is True

        configure_result = _structured_result(
            await client.call_tool(
                "configure_controller",
                {"name": controller_name},
            )
        )
        assert configure_result["ok"] is True

        activation_succeeded = False
        activation_result = _structured_result(
            await client.call_tool(
                "execute_controller_switch",
                {
                    "activate": [controller_name],
                    "deactivate": [],
                },
            )
        )
        assert activation_result["ok"] is True
        activation_succeeded = True

        try:
            controller_result = _structured_result(
                await client.call_tool(
                    "get_controller",
                    {"name": controller_name},
                )
            )
            assert controller_result["result"]["state"] == "active"

            claims_result = _structured_result(
                await client.call_tool("list_resource_claims")
            )
            assert {
                "interface_name": "joint1/position",
                "controller_name": controller_name,
            } in claims_result["result"]
        finally:
            if activation_succeeded:
                deactivation_result = _structured_result(
                    await client.call_tool(
                        "execute_controller_switch",
                        {
                            "activate": [],
                            "deactivate": [controller_name],
                        },
                    )
                )
                assert deactivation_result["ok"] is True

        controller_result = _structured_result(
            await client.call_tool(
                "get_controller",
                {"name": controller_name},
            )
        )
        assert controller_result["result"]["state"] == "inactive"

        claims_result = _structured_result(
            await client.call_tool("list_resource_claims")
        )
        assert all(
            claim["interface_name"] != "joint1/position"
            for claim in claims_result["result"]
        )


def test_mcp_controller_switch_end_to_end(
    monkeypatch,
    tmp_path: Path,
) -> None:
    """Run MCP through safety and a real Jazzy controller_manager."""
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

        asyncio.run(_run_mcp_switch_scenario())
