# Phase 3 - ROS 2 Jazzy Adapter

This phase documents the current Jazzy implementation without asserting historical commit ordering.

## Goal

Connect the application boundary to official ROS 2 Jazzy controller-manager services and map ROS messages into domain models.

## Architecture / Implementation

`JazzyRos2ControlAdapter` implements read operations and delegates state-changing service calls to `JazzyControllerManagerControl`.

Read services include:

```text
list_controllers
list_controller_types
list_hardware_components
list_hardware_interfaces
```

Control services include:

```text
load_controller
configure_controller
cleanup_controller
unload_controller
switch_controller
set_hardware_component_state
```

Each operation creates an `rclpy` node, waits for the configured service, performs a bounded asynchronous call, converts the response, and destroys the node. `rclpy` is shut down when the operation initialized it.

## Relevant Components / Files

```text
src/ros2_control_mcp/ros/jazzy/adapter.py
src/ros2_control_mcp/ros/jazzy/control.py
src/ros2_control_mcp/ros/adapter.py
src/ros2_control_mcp/config/settings.py
tests/unit/test_jazzy_adapter.py
tests/integration/test_mock_system_runtime.py
```

## Commands

Prepare the ROS environment:

```bash
cd ~/projects/robotics/ros2_control_mcp
source .venv/bin/activate
source /opt/ros/jazzy/setup.bash
```

Syntax check:

```bash
uv run python -m compileall src tests
```

## MCP End-User Usage

The adapter is an internal implementation detail. End users call MCP tools rather than adapter methods or ROS CLI commands.

```text
Use ros2_control_mcp and list the current controllers.
Do not use shell or ROS 2 CLI commands.
```

This request later reaches `JazzyRos2ControlAdapter.list_controllers()` through the MCP and application layers.

## Tests / Validation

ROS-message conversion:

```bash
uv run pytest -q tests/unit/test_jazzy_adapter.py
```

Real service behavior is covered in Phase 6 by:

```bash
source /opt/ros/jazzy/setup.bash
uv run pytest -q tests/integration
```

## Expected Result

- controller-manager responses are converted into domain records
- service timeouts produce explicit errors
- production code uses `rclpy`, not ROS 2 CLI subprocesses
- switch activation and deactivation use `/controller_manager/switch_controller`

## Architecture Decisions

- Jazzy-specific imports remain in `ros/jazzy`
- read mapping and control-service mechanics are separated into adapter and control classes
- `list_hardware_interfaces()` is internal and is not registered as an MCP tool

## Known Limitations

- only ROS 2 Jazzy is implemented
- default service namespace is `/controller_manager`
- synchronous tool behavior creates short-lived nodes per adapter operation

## Result

The application layer can communicate with a real Jazzy controller manager through a concrete adapter.

## Next Phase

[Phase 4](README_PHASE_4.md) documents the registered MCP tools, resources, and prompts.
