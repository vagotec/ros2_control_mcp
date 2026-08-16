# Phase 2 - Domain and Application Layer

This phase describes logical components visible in the current repository; it does not assert an unverified commit sequence.

## Goal

Represent ROS 2 Control state independently of ROS message classes and coordinate supported use cases through one application service.

## Architecture / Implementation

The domain layer defines immutable dataclasses for:

- controllers, controller types, and chain connections
- hardware components and interfaces
- resource claims and controller dependencies
- controller-switch plans and safety results
- control-operation results

`Ros2ControlService` delegates ROS access through `Ros2ControlAdapter`. It also derives individual controllers, hardware components, claimed/unclaimed interfaces, resource claims, and controller dependencies from adapter results.

```text
MCP layer
 -> Ros2ControlService
 -> domain models
 -> Ros2ControlAdapter
```

## Relevant Components / Files

```text
src/ros2_control_mcp/domain/chains.py
src/ros2_control_mcp/domain/claims.py
src/ros2_control_mcp/domain/control.py
src/ros2_control_mcp/domain/controllers.py
src/ros2_control_mcp/domain/hardware.py
src/ros2_control_mcp/domain/interfaces.py
src/ros2_control_mcp/domain/safety.py
src/ros2_control_mcp/application/control/service.py
src/ros2_control_mcp/ros/adapter.py
tests/unit/test_control_service.py
```

## Commands

Inspect the package layout:

```bash
cd ~/projects/robotics/ros2_control_mcp
find src/ros2_control_mcp/domain src/ros2_control_mcp/application -type f | sort
```

Syntax check:

```bash
uv run python -m compileall src tests
```

## MCP End-User Usage

The application service is not called directly by an end user. The MCP tools introduced in Phase 4 expose its operations. A later client request such as the following ultimately uses `Ros2ControlService.get_controller()`:

```text
Use ros2_control_mcp and show the status of test_position_controller.
```

## Tests / Validation

Existing application-service tests:

```bash
uv run pytest -q tests/unit/test_control_service.py
```

## Expected Result

- domain values are returned without exposing ROS message objects
- service methods delegate lifecycle and hardware writes to the adapter
- claims and dependencies are derived into structured domain records
- switch execution is blocked before adapter invocation when validation is blocked

## Architecture Decisions

- domain models do not import `rclpy` or controller-manager message types
- application code depends on the abstract adapter
- `ControlResult` provides a common `{ok, message}` result for writes

## Known Limitations

- the application layer does not persist controller-manager state
- controller and hardware state always comes from the adapter
- physical robot safety cannot be represented by these domain models alone

## Result

The application and domain layers provide a ROS-independent boundary for controller, hardware, relationship, and switch operations.

## Next Phase

[Phase 3](README_PHASE_3.md) documents the ROS 2 Jazzy implementation of the adapter.
