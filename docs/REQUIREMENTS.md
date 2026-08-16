# ros2_control_mcp Requirements

This document separates the runtime, development, test, architecture, and release requirements for `ros2_control_mcp` 0.1.0.

# 1. Supported Environment

The validated target is:

```text
Ubuntu 24.04 LTS
ROS 2 Jazzy
Python >= 3.12
```

`pyproject.toml` does not declare an upper Python bound. Other operating systems and ROS distributions are not part of the validated 0.1.0 baseline.

# 2. Runtime Requirements

## 2.1 System software

- ROS 2 Jazzy
- Python 3.12 or newer
- `uv` for the documented source-tree workflow
- a robot or simulator bringup providing an accessible ROS 2 Control `controller_manager`

The server process itself does not start a production controller manager.

## 2.2 Python package

The only Python dependency declared by `pyproject.toml` is:

```text
mcp>=2,<3
```

The dependency graph is stored in `uv.lock`; the current locked MCP SDK baseline is:

```text
mcp 2.0.0
```

## 2.3 ROS Python and interface dependencies

Production code directly uses:

- `rclpy`
- `controller_manager_msgs.msg`
- `controller_manager_msgs.srv`
- `lifecycle_msgs.msg`

These packages are provided by the ROS 2 Jazzy installation rather than declared as PyPI dependencies.

## 2.4 ROS 2 Control runtime

Operational tools require a reachable controller manager exposing the expected services under the configured manager name. The default is:

```text
/controller_manager
```

The implementation calls services including:

```text
/controller_manager/list_controllers
/controller_manager/list_controller_types
/controller_manager/load_controller
/controller_manager/configure_controller
/controller_manager/cleanup_controller
/controller_manager/unload_controller
/controller_manager/switch_controller
/controller_manager/list_hardware_components
/controller_manager/list_hardware_interfaces
/controller_manager/set_hardware_component_state
```

The server and target ROS system must share compatible ROS middleware settings and the same intended `ROS_DOMAIN_ID`.

# 3. Development Requirements

- Git
- `uv`
- Python compatible with `requires-python = ">=3.12"`
- ROS 2 Jazzy sourced for imports or tests that use ROS modules
- `pytest>=8,<9`, declared as the compatible range in the `dev` dependency group

The current `uv.lock` resolves that range to:

```text
pytest 8.4.2
```

Create or synchronize the environment with:

```bash
cd ~/projects/robotics/ros2_control_mcp
uv sync
```

The existing development environment uses access to the ROS-provided Python packages. Sourcing `/opt/ros/jazzy/setup.bash` remains required for a complete ROS environment.

# 4. Test Requirements

## 4.1 Unit tests

Unit tests cover domain conversion, safety evaluation, application behavior, and server creation. They do not require a running ROS graph.

## 4.2 ROS integration and E2E tests

The real ROS tests additionally import or require:

- `ament_index_python`
- `domain_coordinator`
- `controller_manager`
- `controller_manager_msgs`
- `lifecycle_msgs`
- `robot_state_publisher`
- `ros2_control`
- `ros2_controllers`
- `mock_components/GenericSystem`
- `forward_command_controller/ForwardCommandController`

The exact system-package names used to install these components depend on the ROS 2 Jazzy packaging environment. The repository does not declare them as Python/PyPI dependencies.

The fixtures are:

```text
tests/fixtures/mock_runtime_robot.urdf
tests/fixtures/mock_controller_manager.yaml
```

They define `MockSystem`, `joint1/position`, and `test_position_controller`.

## 4.3 Test isolation

Integration and E2E tests:

1. reserve an isolated ROS domain through `domain_coordinator`
2. ignore the user's current `ROS_DOMAIN_ID`
3. start `robot_state_publisher` themselves
4. start the real Jazzy `ros2_control_node` themselves
5. communicate through real controller-manager services
6. terminate their process groups through bounded SIGINT/SIGKILL cleanup

No manually running ROS test processes are required.

# 5. Architecture Requirements

The stable layer boundary is:

```text
MCP
 -> Ros2ControlService
 -> Ros2ControlAdapter
 -> JazzyRos2ControlAdapter
 -> ROS 2 Jazzy services
```

Domain and application modules must not construct ROS nodes or service clients. ROS messages and services belong in the Jazzy implementation.

The MCP layer must not use shell or ROS 2 CLI commands as an implementation substitute.

# 6. MCP Requirements

The server uses MCP over `stdio` through:

```text
ros2-control-mcp = ros2_control_mcp.server:main
```

The client starts the server and communicates using standard MCP capabilities. Version 0.1.0 does not provide an HTTP entry point.

The 15 registered tools are:

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

`activate_controller()` and `list_hardware_interfaces()` exist internally but are not registered MCP tools.

# 7. Controller Lifecycle Requirements

The supported user-visible sequence is:

```text
unloaded
 -> load -> unconfigured
 -> configure -> inactive
 -> execute switch activation -> active
 -> deactivate -> inactive
 -> cleanup -> unconfigured
 -> unload -> no longer listed
```

Load and configure must not implicitly activate a controller. MCP activation must use `execute_controller_switch`.

# 8. Safety Requirements

Read-only operations must remain distinguishable from state-changing operations.

`validate_controller_switch` is read-only. `execute_controller_switch` invokes the same `SafetyEvaluator` and blocks adapter execution when validation returns `blocked`.

The following operations do not use `SafetyEvaluator` in 0.1.0 and must not be documented as if they do:

```text
load_controller
configure_controller
deactivate_controller
cleanup_controller
unload_controller
set_hardware_component_state
```

Safety findings are software-level checks. They do not guarantee physical safety.

# 9. Testing Requirements

Unit tests:

```bash
uv run pytest -q tests/unit
```

ROS 2 Jazzy integration and E2E tests:

```bash
source /opt/ros/jazzy/setup.bash
uv run pytest -q tests/integration
uv run pytest -q tests/e2e/test_mcp_controller_switch.py -vv
```

Complete suite:

```bash
source /opt/ros/jazzy/setup.bash
uv run pytest -q
```

# 10. Scope Boundaries

Version 0.1.0 does not provide command-value publishing, motion planning, production bringup management, physical safety certification, arbitrary shell access, ROS CLI execution, HTTP transport, or non-Jazzy adapters.

# 11. Release Requirements

Before release:

- all required production and test files must be tracked
- `pyproject.toml` must report version `0.1.0`
- README, installation, requirements, phases, and changelog must agree
- the package entry point and MCP registration must be valid
- the documented test baseline must pass in the Jazzy environment
- licensing must be explicitly decided by the maintainer

# 12. Current Baseline

The recorded 0.1.0 baseline is 40 passing pytest tests, including five real Jazzy integration tests and one real MCP E2E smoke test.
