# Changelog

All notable changes to `ros2_control_mcp` are documented in this file.

The format follows Keep a Changelog conventions. The project does not yet declare a license.

## [0.1.0] - 2026-08-16

### Added

- MCP stdio server and `ros2-control-mcp` console entry point.
- Layered MCP, application, domain, safety, adapter, and ROS 2 Jazzy architecture.
- Fifteen MCP tools for controller inspection, controller lifecycle, hardware inspection/state changes, resource claims, dependencies, switch validation, and switch execution.
- Five read-only MCP resources for overview, hardware, claims, chains, and safety context.
- Four MCP prompts for system inspection, controller-conflict diagnosis, hardware-interface diagnosis, and switch review.
- Domain models for controllers, hardware components, interfaces, claims, dependencies, control results, and safety findings.
- Jazzy service integration for controller, hardware, interface, lifecycle, and switch operations.
- Explicit controller-switch validation through `SafetyEvaluator`.
- MockSystem fixtures using `joint1/position` and `test_position_controller`.

### Changed

- Promoted the package version from `0.1.0-dev` to `0.1.0`.
- Documented the controller lifecycle as load to `unconfigured`, configure to `inactive`, activate to `active`, deactivate to `inactive`, cleanup to `unconfigured`, and unload to not listed.
- Clarified that MCP activation uses `execute_controller_switch`; `activate_controller()` is an internal method, not an MCP tool.
- Clarified that `list_hardware_interfaces()` is internal and not a registered MCP tool.
- Clarified that switch execution uses `SafetyEvaluator`, while other lifecycle and hardware-state writes call the adapter directly.

### Testing

- Unit coverage for application behavior, safety evaluation, Jazzy message conversion, and server creation.
- Five real ROS 2 Jazzy integration tests using an isolated domain, real controller manager, and MockSystem.
- One MCP E2E smoke test covering MCP client to controller manager activation/deactivation and interface claim/release.
- Recorded release baseline: 40 passing pytest tests.

### Documentation

- Added complete runtime, development, and test requirements.
- Added source installation and concrete Codex stdio registration instructions.
- Added end-user MCP workflows with tool names, arguments, expected states, and response shapes.
- Added consolidated development phases and explicit normal-runtime versus test-runtime guidance.

[0.1.0]: https://github.com/vagotec/ros2_control_mcp/releases/tag/v0.1.0
