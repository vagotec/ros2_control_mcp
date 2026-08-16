# Phase 6 - Real ROS 2 Integration and MCP E2E Validation

This phase records the real test runtime and the validated 0.1.0 baseline already present in the repository.

## Goal

Verify the Jazzy adapter and complete MCP path against a real ROS 2 controller manager using MockSystem, without requiring physical hardware or manually started ROS processes.

## Architecture / Implementation

Each real ROS test starts:

```text
robot_state_publisher
controller_manager/ros2_control_node
mock_components/GenericSystem
```

The controller fixture uses:

```text
test_position_controller
forward_command_controller/ForwardCommandController
joint1/position
```

`domain_coordinator.domain_id()` reserves an isolated ROS domain independent of the user's current `ROS_DOMAIN_ID`. Processes use `start_new_session=True`. Cleanup signals the process group with SIGINT and uses bounded SIGKILL fallback.

The E2E path is:

```text
MCP Client
 -> registered MCP Tool
 -> Ros2ControlService
 -> SafetyEvaluator
 -> JazzyRos2ControlAdapter
 -> real controller_manager service
 -> MockSystem
```

## Relevant Components / Files

```text
tests/integration/test_mock_system_runtime.py
tests/e2e/test_mcp_controller_switch.py
tests/fixtures/mock_runtime_robot.urdf
tests/fixtures/mock_controller_manager.yaml
src/ros2_control_mcp/ros/jazzy/adapter.py
src/ros2_control_mcp/ros/jazzy/control.py
```

## Commands

Prepare the real ROS test environment:

```bash
cd ~/projects/robotics/ros2_control_mcp
source .venv/bin/activate
source /opt/ros/jazzy/setup.bash
```

Do not manually start `robot_state_publisher` or `ros2_control_node`; the tests own those processes.

Syntax check:

```bash
uv run python -m compileall src tests
```

## MCP End-User Usage

The E2E scenario corresponds to this client workflow:

```text
Use ros2_control_mcp to load and configure test_position_controller.
Activate it through execute_controller_switch without publishing command values.
Verify that the controller is active and joint1/position is claimed.
Then deactivate it and verify that it is inactive and the interface is unclaimed.
```

## Tests / Validation

Five real Jazzy integration tests:

```bash
uv run pytest -q tests/integration
```

One real MCP E2E smoke test:

```bash
uv run pytest -q tests/e2e/test_mcp_controller_switch.py -vv
```

Complete recorded baseline:

```bash
uv run pytest -q
```

## Expected Result

The recorded validated result is:

```text
5 real ROS 2 Jazzy integration tests
1 real MCP E2E smoke test
40 pytest tests passed in the complete suite
```

The lifecycle/claim sequence is:

```text
inactive: joint1/position available=true, claimed=false
active:   joint1/position available=true, claimed=true
inactive: joint1/position available=true, claimed=false
```

## Architecture Decisions

- real services are used instead of ROS CLI
- integration tests call the Jazzy adapter
- the E2E test calls registered MCP tools rather than substituting direct service/adapter calls
- every test owns and cleans up its ROS processes
- no command values are published

## Known Limitations

- MockSystem does not prove physical robot safety
- only ROS 2 Jazzy is covered
- the E2E suite contains one controlled smoke scenario rather than exhaustive MCP coverage

## Result

The real adapter path, controller lifecycle, resource claim/release, process isolation, and complete MCP switch path have a validated baseline.

## Next Phase

[Phase 7](README_PHASE_7.md) documents release metadata and documentation preparation.
