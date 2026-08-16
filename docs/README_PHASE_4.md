# Phase 4 - MCP Controller and Hardware Capabilities

This phase describes the capability inventory present in the current source tree, not an inferred commit history.

## Goal

Expose controller and hardware operations as structured MCP tools and provide reusable read-only resources and prompts.

## Architecture / Implementation

`create_server()` registers 15 tools:

```text
list_controllers
get_controller
list_controller_types
load_controller
configure_controller
deactivate_controller
cleanup_controller
unload_controller
list_hardware_components
get_hardware_component
set_hardware_component_state
list_resource_claims
list_controller_dependencies
validate_controller_switch
execute_controller_switch
```

Five read-only resources are registered:

| URI | Result |
|---|---|
| `ros2control://overview` | controllers, hardware, command interfaces, state interfaces |
| `ros2control://hardware` | hardware components and interfaces |
| `ros2control://claims` | resource claims |
| `ros2control://chains` | controller dependencies |
| `ros2control://safety` | safety-relevant claims, dependencies, and interfaces |

Four prompts are registered:

```text
inspect_ros2_control_system
diagnose_controller_conflict
diagnose_hardware_interface
review_controller_switch
```

Tools convert dataclasses to structured dictionaries. Resources return JSON snapshots. Prompts return workflow instructions and do not execute ROS operations.

## Relevant Components / Files

```text
src/ros2_control_mcp/server.py
src/ros2_control_mcp/mcp/tools/controllers.py
src/ros2_control_mcp/mcp/tools/hardware.py
src/ros2_control_mcp/mcp/tools/relationships.py
src/ros2_control_mcp/mcp/tools/safety.py
src/ros2_control_mcp/mcp/resources/
src/ros2_control_mcp/mcp/prompts/
tests/unit/test_server.py
tests/e2e/test_mcp_controller_switch.py
```

## Commands

Start the MCP stdio server for a client-owned session:

```bash
cd ~/projects/robotics/ros2_control_mcp
source .venv/bin/activate
source /opt/ros/jazzy/setup.bash
ros2-control-mcp
```

Syntax check:

```bash
uv run python -m compileall src tests
```

## MCP End-User Usage

Read-only controller inspection:

```text
Use ros2_control_mcp and list the current controllers.
```

Read-only controller-type inspection:

```text
Use ros2_control_mcp and list the controller types available to the controller manager.
```

Read-only hardware inspection:

```text
Use ros2_control_mcp and show the hardware component named MockSystem.
Report its plugin, lifecycle state, command interfaces, and state interfaces.
```

Explicit hardware lifecycle write:

```text
Use ros2_control_mcp to set MockSystem to state ID 2 with label "inactive".
Do not perform any other operation.
```

The last request uses `set_hardware_component_state`, is state-changing, and does not use `SafetyEvaluator`.

## Tests / Validation

Server construction:

```bash
uv run pytest -q tests/unit/test_server.py
```

The real MCP tool path is validated later by:

```bash
source /opt/ros/jazzy/setup.bash
uv run pytest -q tests/e2e/test_mcp_controller_switch.py -vv
```

## Expected Result

- exactly 15 tools, five resources, and four prompts are registered
- tool results are structured MCP results
- resources remain read-only
- prompts provide guidance without directly changing ROS state

## Architecture Decisions

- MCP functions call `Ros2ControlService`, not `rclpy`
- `activate_controller()` is not an MCP tool; activation uses `execute_controller_switch`
- `list_hardware_interfaces()` is not an MCP tool; interface data is exposed through hardware records and resources

## Known Limitations

- no HTTP transport
- no direct controller command-value publishing
- no MCP tool dedicated solely to listing hardware interfaces

## Result

The implemented controller, hardware, relationship, safety, resource, and prompt capabilities are available through one MCP stdio server.

## Next Phase

[Phase 5](README_PHASE_5.md) documents switch safety and controller lifecycle behavior.
