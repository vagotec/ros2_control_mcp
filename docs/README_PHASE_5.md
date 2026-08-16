# Phase 5 - Safety and Controller Switching

This phase documents the implemented safety boundary and lifecycle semantics visible in the current code.

## Goal

Validate planned controller switches before MCP-driven execution and make controller activation explicit.

## Architecture / Implementation

`ControllerSwitchPlan` contains activation and deactivation lists, strictness, `activate_asap`, and timeout. `SafetyEvaluator` checks:

- unknown controllers
- activation/deactivation overlap
- invalid activation lifecycle state
- unavailable required command and state interfaces
- command-interface conflicts with controllers that remain active
- active controller-chain relationships that produce warnings

The path is:

```text
validate_controller_switch (read-only)
 -> Ros2ControlService
 -> SafetyEvaluator
 -> SafetyResult
```

```text
execute_controller_switch (state-changing)
 -> Ros2ControlService
 -> SafetyEvaluator
 -> JazzyRos2ControlAdapter
 -> /controller_manager/switch_controller
```

A `blocked` result prevents the adapter call. Warnings do not block execution. Execution rejects `auto` and `force_auto` strictness in 0.1.0.

The lifecycle is:

```text
unloaded -> load -> unconfigured
unconfigured -> configure -> inactive
inactive -> execute switch activation -> active
active -> deactivate -> inactive
inactive -> cleanup -> unconfigured
unconfigured -> unload -> not listed
```

## Relevant Components / Files

```text
src/ros2_control_mcp/domain/safety.py
src/ros2_control_mcp/safety/evaluator.py
src/ros2_control_mcp/application/control/service.py
src/ros2_control_mcp/mcp/tools/safety.py
src/ros2_control_mcp/ros/jazzy/control.py
tests/unit/test_safety_evaluator.py
tests/unit/test_control_service.py
```

## Commands

Prepare the project environment:

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

Validate without execution:

```text
Use ros2_control_mcp to validate this switch without executing it:
activate: ["test_position_controller"]
deactivate: []
strictness: "strict"
Report the status and every finding.
```

Activate only after reviewing validation:

```text
Use ros2_control_mcp to activate test_position_controller through execute_controller_switch.
Do not publish command values. Then verify its state and resource claims.
```

Deactivate through the separately registered lifecycle tool:

```text
Use ros2_control_mcp to deactivate test_position_controller and verify that it is inactive.
```

## Tests / Validation

Safety rules:

```bash
uv run pytest -q tests/unit/test_safety_evaluator.py
```

Application switch orchestration:

```bash
uv run pytest -q tests/unit/test_control_service.py
```

## Expected Result

- safe plans return `safe`
- warnings return `warning` and remain executable
- invalid or conflicting plans return `blocked`
- blocked execution does not invoke the adapter
- successful activation uses the real switch-controller path in later integration tests

## Architecture Decisions

- MCP activation uses `execute_controller_switch`, not an `activate_controller` tool
- validation and execution are separate MCP operations
- SafetyEvaluator applies to switch validation/execution only
- load, configure, deactivate, cleanup, unload, and hardware-state writes do not use SafetyEvaluator

## Known Limitations

- validation is not a physical safety guarantee
- warnings do not block execution
- `auto` and `force_auto` plans cannot be executed in 0.1.0
- safety rules use controller-manager-visible state only

## Result

Controller switching has a defined application-level validation boundary and explicit MCP activation path.

## Next Phase

[Phase 6](README_PHASE_6.md) validates lifecycle and switch behavior against a real Jazzy controller manager and through MCP E2E.
