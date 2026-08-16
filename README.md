# ros2_control_mcp

A Model Context Protocol (MCP) server for inspecting and deliberately managing ROS 2 Control systems.

`ros2_control_mcp` gives MCP-compatible clients structured access to a ROS 2 Jazzy `controller_manager`. It exposes controller inspection, lifecycle operations, hardware state, resource claims, dependency information, switch validation, and controlled controller switching without using an arbitrary shell or ROS 2 CLI as its internal API.

The current release targets:

- `ros2_control_mcp` 0.1.0
- Ubuntu 24.04 LTS
- ROS 2 Jazzy
- Python 3.12 or newer, as declared by `pyproject.toml`
- MCP Python SDK 2.0.0, as locked by `uv.lock`
- local MCP transport through `stdio`

## Project Status

```text
Version:                    0.1.0
ROS distribution:           ROS 2 Jazzy
Registered MCP tools:       15
MCP resources:              5
MCP prompts:                4
Unit/integration/E2E suite: 40 passed
Real ROS 2 integration:     validated with MockSystem
MCP end-to-end path:        validated
```

The result above records the completed 0.1.0 validation baseline. See [Testing](#testing) for reproducible commands.

# Why ros2_control_mcp?

ROS 2 Control already provides programmatic and command-line interfaces. MCP clients should not need unrestricted shell access to use them. This project provides a narrow, typed boundary around the supported controller-manager operations.

The server is not a motion planner, a command-value publisher, or a physical safety system. Robot-level interlocks, emergency stops, limits, and safe operating procedures remain external responsibilities.

# Design Goals

- separate MCP protocol handling from ROS-specific code
- keep domain and application logic testable without a live ROS graph
- isolate ROS 2 Jazzy APIs behind an adapter
- distinguish inspection from state-changing operations
- validate controller-switch requests before execution
- use official ROS 2 services rather than ROS 2 CLI subprocesses
- expose structured results instead of terminal output
- isolate automated ROS test graphs from the user's normal graph
- keep robot-specific motion logic out of this server

# Architecture

```text
MCP Client
    |
    | MCP / stdio
    v
MCPServer
    |
    +-- Tools
    +-- Resources
    +-- Prompts
    |
    v
Ros2ControlService
    |
    +-- Domain models
    +-- SafetyEvaluator (switch validation/execution only)
    |
    v
Ros2ControlAdapter
    |
    v
JazzyRos2ControlAdapter
    |
    v
rclpy service clients
    |
    v
ROS 2 Jazzy controller_manager
    |
    v
ros2_control hardware and controllers
```

The composition root is `ros2_control_mcp.server:create_server`. It constructs `Ros2ControlService(JazzyRos2ControlAdapter())` and registers the MCP capabilities.

Read-only calls and ordinary lifecycle calls use:

```text
MCP Tool -> Ros2ControlService -> JazzyRos2ControlAdapter -> ROS service
```

Controller-switch execution uses the additional safety boundary:

```text
execute_controller_switch
    -> Ros2ControlService
    -> SafetyEvaluator
    -> JazzyRos2ControlAdapter
    -> /controller_manager/switch_controller
```

The `SafetyEvaluator` is not invoked by every state-changing operation. Load, configure, deactivate, cleanup, unload, and hardware-state changes call the adapter directly through the application service.

# MCP Capabilities

The server registers 15 tools, five read-only resources, and four prompts.

## Resources

All five resources are static, read-only resources and take no arguments.

| URI | Resource name | Arguments | Purpose | Top-level JSON structure |
|---|---|---|---|---|
| `ros2control://overview` | `ros2_control_overview` | none | Complete controller and hardware overview | object with `controllers`, `hardware_components`, `command_interfaces`, `state_interfaces` |
| `ros2control://hardware` | `ros2_control_hardware` | none | Hardware-focused state view | object with `hardware_components`, `command_interfaces`, `state_interfaces` |
| `ros2control://claims` | `ros2_control_claims` | none | Current command-interface claims | array of resource-claim records |
| `ros2control://chains` | `ros2_control_chains` | none | Controller dependencies and chains | array of dependency records |
| `ros2control://safety` | `ros2_control_safety` | none | Safety-relevant runtime context | object with `resource_claims`, `controller_dependencies`, `command_interfaces`, `state_interfaces`, `physical_safety_guarantee` |

Controller, hardware, interface, claim, and dependency records use the same fields described by the tool results below. `physical_safety_guarantee` is always `false`; the resource does not certify a robot as physically safe.

Resources are read-only MCP context views. They do not change the controller-manager state.

## Prompts

| Prompt | Arguments | Purpose and usage |
|---|---|---|
| `inspect_ros2_control_system` | none | Guides a read-only inspection of controllers, hardware, interfaces, claims, and dependencies |
| `diagnose_controller_conflict` | none | Guides diagnosis of controller and command-interface conflicts without changing state |
| `diagnose_hardware_interface` | none | Guides diagnosis of interface availability and claims without changing hardware state |
| `review_controller_switch` | none | Guides a read-only review of a planned switch; it does not execute the switch |

Prompts return reusable workflow text for an MCP client. They do not call ROS services themselves.

# MCP Tools

| Tool | Arguments | Operation | SafetyEvaluator | Result |
|---|---|---|---|---|
| `list_controllers` | none | Read-only | No | List of controller records |
| `get_controller` | `name: str` | Read-only | No | One controller record or `null` |
| `list_controller_types` | none | Read-only | No | List of `{name, base_class}` records |
| `load_controller` | `name: str` | State-changing | No | `{ok: bool, message: str | null}` |
| `configure_controller` | `name: str` | State-changing | No | `{ok: bool, message: str | null}` |
| `deactivate_controller` | `name: str` | State-changing | No | `{ok: bool, message: str | null}` |
| `cleanup_controller` | `name: str` | State-changing | No | `{ok: bool, message: str | null}` |
| `unload_controller` | `name: str` | State-changing | No | `{ok: bool, message: str | null}` |
| `list_hardware_components` | none | Read-only | No | List of hardware components including interfaces |
| `get_hardware_component` | `name: str` | Read-only | No | One hardware component or `null` |
| `set_hardware_component_state` | `name: str`, `state_id: int`, `state_label: str` | State-changing | No | `{ok: bool, message: str | null}` |
| `list_resource_claims` | none | Read-only | No | List of `{interface_name, controller_name}` records |
| `list_controller_dependencies` | none | Read-only | No | List of dependency records |
| `validate_controller_switch` | `activate: list[str]`, `deactivate: list[str]`, optional `strictness`, optional `timeout_seconds` | Read-only | Yes | Safety status, operation, and findings |
| `execute_controller_switch` | same | State-changing | Yes | `{ok: bool, message: str | null}` |

A controller record includes its name, type, state, claimed and required interfaces, update information, and chain metadata. A hardware component includes its type, plugin, lifecycle state, and command/state interfaces. Interfaces include `name`, `data_type`, `is_available`, and `is_claimed`.

There is no MCP tool named `list_hardware_interfaces`. That method exists internally in the application and adapter layers. MCP clients can inspect interfaces through hardware component results and the hardware, overview, and safety resources.

There is no MCP tool named `activate_controller`. Controller activation through MCP uses `execute_controller_switch`.

Strictness values are `best_effort`, `strict`, `auto`, and `force_auto`. In 0.1.0, execution rejects `auto` and `force_auto`. The default is `strict`, and the default timeout is five seconds.

## MCP SDK 2.0.0 structured output

MCP SDK 2.0.0 wraps structured results for non-dictionary return annotations. The following examples show `CallToolResult.structured_content`, not merely the semantic payload.

Tools returning lists, including `list_controllers` and `list_resource_claims`, return the list under `result`:

```json
{
  "result": [
    {
      "name": "test_position_controller",
      "controller_type": "forward_command_controller/ForwardCommandController",
      "state": "inactive"
    }
  ]
}
```

```json
{
  "result": [
    {
      "interface_name": "joint1/position",
      "controller_name": "test_position_controller"
    }
  ]
}
```

Nullable object results such as `get_controller` and `get_hardware_component` are also wrapped:

```json
{
  "result": {
    "name": "test_position_controller",
    "state": "inactive"
  }
}
```

For an unknown name, the same shape contains `null`:

```json
{
  "result": null
}
```

Tools returning `dict[str, Any]` remain top-level dictionaries. For example, `execute_controller_switch` returns:

```json
{
  "ok": true,
  "message": null
}
```

`validate_controller_switch` also returns a top-level dictionary:

```json
{
  "status": "safe",
  "operation": "switch_controllers",
  "findings": []
}
```

Each validation finding contains the fields defined by `SafetyFinding`:

```json
{
  "code": "INTERFACE_CONFLICT",
  "message": "Command interface 'joint1/position' is already claimed by controller 'other_controller'.",
  "severity": "error",
  "controller_name": "test_position_controller",
  "interface_name": "joint1/position"
}
```

`controller_name` and `interface_name` may be `null` when a finding does not apply to that field.

A `list_controller_dependencies` item has this exact domain structure and is returned inside the list wrapper:

```json
{
  "result": [
    {
      "controller_name": "downstream_controller",
      "depends_on": "upstream_controller",
      "reference_interfaces": ["upstream_controller/reference"]
    }
  ]
}
```

# Controller Lifecycle

```text
unloaded
    |
    | load_controller
    v
unconfigured
    |
    | configure_controller
    v
inactive
    |
    | execute_controller_switch (activate)
    v
active
    |
    | deactivate_controller
    v
inactive
    |
    | cleanup_controller
    v
unconfigured
    |
    | unload_controller
    v
unloaded / no longer listed
```

Loading does not create a separate documented `loaded` lifecycle state. According to the Jazzy lifecycle, a successfully loaded controller is expected to be `unconfigured`; the current integration test verifies presence after load and verifies `inactive` after configure. Activation then reaches `active`, deactivation returns to `inactive`, cleanup returns to `unconfigured`, and unload removes the controller from the listing.

# Controller Switching and Safety

Switch validation is read-only. It checks that requested controllers exist, detects activation/deactivation overlap, validates activation state and interface availability, finds resource conflicts, and reports relevant active chain relationships.

Validation returns `safe`, `warning`, or `blocked`. `execute_controller_switch` performs validation and does not call the adapter when the result is `blocked`. Warnings do not block execution. This is a software consistency check, not a physical safety guarantee.

# Hardware and Resource Claims

`list_hardware_components` and `get_hardware_component` expose component metadata and nested command/state interfaces. `set_hardware_component_state` is state-changing and does not pass through `SafetyEvaluator`.

A resource claim is returned as:

```json
{
  "interface_name": "joint1/position",
  "controller_name": "test_position_controller"
}
```

The MockSystem validation establishes:

```text
inactive: joint1/position available=true, claimed=false
active:   joint1/position available=true, claimed=true
inactive: joint1/position available=true, claimed=false
```

# End-User Usage

Terminal commands install and start the server. The quoted requests below are entered in an MCP client; they are not shell or ROS 2 CLI commands.

## Inspect controllers

```text
Use ros2_control_mcp and list the current controllers.
```

Tool: `list_controllers`.

```text
Use ros2_control_mcp and show the status of test_position_controller.
```

Tool: `get_controller` with `name="test_position_controller"`.

```text
Use ros2_control_mcp and list the controller types available to the controller manager.
```

Tool: `list_controller_types`. Arguments: none. This is read-only and does not use `SafetyEvaluator`. The result is a list of records containing `name` and `base_class`.

## Load and configure

```text
Use ros2_control_mcp to load test_position_controller. Then inspect it and report its state.
```

Tools: `load_controller`, then `get_controller`. Expected state after load: `unconfigured`.

```text
Use ros2_control_mcp to configure test_position_controller. Do not activate it. Then verify its state.
```

Tools: `configure_controller`, then `get_controller`. Expected state: `inactive`.

## Inspect hardware and relationships

```text
Use ros2_control_mcp and show the available hardware components, their plugins, lifecycle states, and interfaces.
```

Tool: `list_hardware_components`.

```text
Use ros2_control_mcp and show the hardware component named MockSystem.
Report its type, plugin, lifecycle state, command interfaces, and state interfaces.
```

Tool: `get_hardware_component` with `name="MockSystem"`. This is read-only and does not use `SafetyEvaluator`. The result is one hardware component record or `null` when the name is unknown.

```text
Use ros2_control_mcp to set MockSystem to lifecycle state ID 2 with label "inactive".
Do not perform any other operation.
```

Tool: `set_hardware_component_state` with `name="MockSystem"`, `state_id=2`, and `state_label="inactive"`. This is state-changing and does not use `SafetyEvaluator`. The result is `{ok, message}`. State IDs and labels must come from the target system's intended lifecycle transition; the MockSystem values are an example, not a universal hardware instruction.

```text
Use ros2_control_mcp and show the current resource claims. Tell me which controller claims each interface.
```

Tool: `list_resource_claims`.

```text
Use ros2_control_mcp and list the current controller dependencies.
```

Tool: `list_controller_dependencies`.

## Validate and activate

```text
Use ros2_control_mcp to validate this switch without executing it:
activate: ["test_position_controller"]
deactivate: []
strictness: "strict"
```

Tool: `validate_controller_switch`. Review its status and findings before execution.

```text
Use ros2_control_mcp to activate test_position_controller through the controlled switch path. Do not publish command values. Then verify that it is active and report its resource claims.
```

Tools: `execute_controller_switch` with `activate=["test_position_controller"]` and `deactivate=[]`, then `get_controller` and `list_resource_claims`. Execution runs validation before the ROS service call.

## Deactivate, cleanup, and unload

```text
Use ros2_control_mcp to deactivate test_position_controller and verify that it is inactive.
```

Tools: `deactivate_controller`, then `get_controller`.

```text
Use ros2_control_mcp to clean up test_position_controller and verify that it is unconfigured.
```

Tools: `cleanup_controller`, then `get_controller`.

```text
Use ros2_control_mcp to unload test_position_controller and verify that it is no longer listed.
```

Tools: `unload_controller`, then `list_controllers`.

# Normal Runtime vs Test Runtime

The normal MCP server does not launch `robot_state_publisher`, `ros2_control_node`, or `controller_manager`.

For operational use:

1. Start the robot or simulator bringup that owns the intended `controller_manager`.
2. Ensure its ROS domain and middleware environment are visible to the MCP server.
3. Start the MCP server through the client.
4. Inspect current state before requesting changes.

The automated integration and E2E tests instead start an isolated `robot_state_publisher` and real Jazzy `ros2_control_node`, reserve their own `ROS_DOMAIN_ID`, use MockSystem, and terminate their process groups after the test.

# Installation

See [docs/INSTALLATION.md](docs/INSTALLATION.md) for setup and MCP-client registration.

Quick development setup from an existing checkout:

```bash
cd ~/projects/robotics/ros2_control_mcp
uv sync
source .venv/bin/activate
source /opt/ros/jazzy/setup.bash
```

Manual diagnostic start:

```bash
uv run ros2-control-mcp
```

Normally the MCP client owns this stdio process.

# Requirements

Runtime, development, and test dependencies are separated in [docs/REQUIREMENTS.md](docs/REQUIREMENTS.md).

# Testing

Unit tests do not require a running controller manager:

```bash
cd ~/projects/robotics/ros2_control_mcp
uv run pytest -q tests/unit
```

The complete suite and ROS integration/E2E tests require a sourced ROS 2 Jazzy environment, but no manually started ROS processes:

```bash
cd ~/projects/robotics/ros2_control_mcp
source /opt/ros/jazzy/setup.bash

uv run pytest -q
uv run pytest -q tests/integration
uv run pytest -q tests/e2e/test_mcp_controller_switch.py -vv
uv run pytest -vv
```

Syntax check:

```bash
uv run python -m compileall src tests
```

# MCP End-to-End Test

`tests/e2e/test_mcp_controller_switch.py` exercises:

```text
MCP Client
    -> registered MCP tools
    -> Ros2ControlService
    -> SafetyEvaluator
    -> JazzyRos2ControlAdapter
    -> /controller_manager/switch_controller
    -> real Jazzy controller_manager
    -> MockSystem
```

It activates through `execute_controller_switch`, verifies `active` and `joint1/position` claimed, deactivates through MCP, and verifies `inactive` and the interface released. It does not call the adapter directly as an MCP substitute, invoke ROS CLI, or publish a command value.

# Project Structure

```text
ros2_control_mcp/
├── docs/
│   ├── INSTALLATION.md
│   ├── README_PHASE_1.md
│   ├── README_PHASE_2.md
│   ├── README_PHASE_3.md
│   ├── README_PHASE_4.md
│   ├── README_PHASE_5.md
│   ├── README_PHASE_6.md
│   ├── README_PHASE_7.md
│   ├── README_PHASES.md
│   └── REQUIREMENTS.md
├── src/ros2_control_mcp/
│   ├── application/control/
│   ├── config/
│   ├── domain/
│   ├── mcp/{prompts,resources,tools}/
│   ├── ros/jazzy/
│   ├── safety/
│   └── server.py
├── tests/{e2e,fixtures,integration,unit}/
├── CHANGELOG.md
├── pyproject.toml
├── README.md
└── uv.lock
```

# Development Documentation

- [Requirements](docs/REQUIREMENTS.md)
- [Installation and MCP client setup](docs/INSTALLATION.md)
- [Development phases](docs/README_PHASES.md)
- [Changelog](CHANGELOG.md)

# Scope

Version 0.1.0 includes a stdio MCP server, controller and hardware inspection, controller lifecycle operations, hardware lifecycle state changes, claims and dependency inspection, switch validation/execution, Jazzy service integration, MCP resources/prompts, isolated MockSystem integration tests, and one real MCP-to-ROS E2E smoke test.

# Out of Scope

- publishing controller command values
- motion planning or trajectory generation
- physical robot safety certification
- automatically launching production robot bringup
- arbitrary shell or ROS 2 CLI execution
- generic ROS graph management
- Nav2, MoveIt 2, perception, or multi-robot orchestration
- HTTP MCP transport
- ROS distributions other than Jazzy

# Future Architecture

Future releases may add other ROS-distribution adapters or stronger controller conflict analysis while preserving the MCP -> application -> adapter boundary. Subsystem-specific servers should remain independently deployable.

# Versioning

The package version is defined in `pyproject.toml`. This documentation describes version 0.1.0.

# License

No project license has been selected or recorded. Distribution terms require a maintainer decision.

# Changelog

Release notes are maintained in [CHANGELOG.md](CHANGELOG.md).

# Current Status

The 0.1.0 implementation and its 40-test baseline are complete. Before publishing, the repository still requires a maintainer decision on licensing and the normal release workflow (final verification, commit, and tag).
