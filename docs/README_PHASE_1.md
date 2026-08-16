# Phase 1 - Project Foundation

This is a technical phase description based on the current repository, not a claim about exact historical commit order.

## Goal

Establish a small Python project with an MCP stdio server, central composition root, runtime settings, and a replaceable ROS adapter boundary.

## Architecture / Implementation

The package uses a `src/` layout and `uv` dependency management. `create_server()` creates the MCP server and composes `Ros2ControlService` with `JazzyRos2ControlAdapter`. `main()` runs the server using MCP `stdio` transport.

```text
MCP client
 -> ros2-control-mcp
 -> create_server()
 -> Ros2ControlService
 -> Ros2ControlAdapter
```

`Settings` currently defines `/controller_manager` and a five-second service timeout. The abstract adapter separates application code from the Jazzy implementation.

## Relevant Components / Files

```text
pyproject.toml
uv.lock
src/ros2_control_mcp/server.py
src/ros2_control_mcp/config/settings.py
src/ros2_control_mcp/ros/adapter.py
tests/unit/test_server.py
```

## Commands

Terminal setup:

```bash
cd ~/projects/robotics/ros2_control_mcp
uv sync
source .venv/bin/activate
source /opt/ros/jazzy/setup.bash
```

Start the stdio server manually for diagnostics:

```bash
uv run ros2-control-mcp
```

The process expects MCP messages on standard input. A normal MCP client starts it automatically.

Syntax check:

```bash
uv run python -m compileall src tests
```

## MCP End-User Usage

This phase establishes transport and composition but does not add a standalone end-user ROS operation. After later capability registration, an MCP client starts the same `ros2-control-mcp` entry point.

## Tests / Validation

Existing server unit test:

```bash
uv run pytest -q tests/unit/test_server.py
```

## Expected Result

- `create_server()` returns an `MCPServer` named `ros2-control-mcp`.
- the console entry point resolves to `ros2_control_mcp.server:main`
- the transport is `stdio`
- application code depends on the adapter abstraction rather than constructing ROS clients

## Architecture Decisions

- MCP server creation is centralized in one composition root.
- ROS-distribution-specific behavior stays behind `Ros2ControlAdapter`.
- no arbitrary shell or ROS 2 CLI execution is exposed.

## Known Limitations

- version 0.1.0 provides no HTTP transport
- the default controller-manager name is not exposed as a CLI option
- ROS-backed operations require an externally available controller manager

## Result

The package, entry point, stdio server, settings, and adapter boundary form the foundation for domain and application behavior.

## Next Phase

[Phase 2](README_PHASE_2.md) documents domain models and `Ros2ControlService`.
