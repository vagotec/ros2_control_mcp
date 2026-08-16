# ros2_control_mcp Installation

This guide installs `ros2_control_mcp` 0.1.0 from source and connects it to a local MCP client such as OpenAI Codex. It assumes Ubuntu 24.04 and ROS 2 Jazzy are already installed.

The server supports local MCP through `stdio`. It does not provide HTTP transport in version 0.1.0.

# 1. Prerequisites

Required software:

- Ubuntu 24.04 LTS
- ROS 2 Jazzy
- Python 3.12 or newer
- Git
- `uv`
- the ROS packages listed in [REQUIREMENTS.md](REQUIREMENTS.md)
- Codex CLI only when following the Codex example

Verify the prepared ROS environment:

```bash
source /opt/ros/jazzy/setup.bash
echo "$ROS_DISTRO"
```

Expected:

```text
jazzy
```

Verify local tools:

```bash
python3 --version
git --version
uv --version
```

This guide does not install Ubuntu or ROS 2 itself. Follow the official ROS 2 Jazzy installation procedure before continuing.

# 2. Download and Install

Clone the repository and synchronize its Python environment:

```bash
mkdir -p ~/projects/robotics
cd ~/projects/robotics
git clone https://github.com/vagotec/ros2_control_mcp.git

cd ~/projects/robotics/ros2_control_mcp
uv sync
```

For an existing checkout, use only:

```bash
cd ~/projects/robotics/ros2_control_mcp
uv sync
```

# 3. Activate the Environment

```bash
cd ~/projects/robotics/ros2_control_mcp
source .venv/bin/activate
source /opt/ros/jazzy/setup.bash
```

Sourcing ROS is important: setting `ROS_DISTRO=jazzy` by itself does not provide the complete Python, package-index, and middleware environment.

# 4. Verify the Installation

Verify the MCP SDK without relying on a non-existent `mcp.__version__` attribute:

```bash
cd ~/projects/robotics/ros2_control_mcp
source .venv/bin/activate

python - <<'PY'
from importlib.metadata import version

print("mcp:", version("mcp"))
PY
```

The version locked by the current `uv.lock` is:

```text
mcp 2.0.0
```

Verify ROS Python support and the project package:

```bash
cd ~/projects/robotics/ros2_control_mcp
source .venv/bin/activate
source /opt/ros/jazzy/setup.bash

python - <<'PY'
import rclpy
import ros2_control_mcp
from ros2_control_mcp.server import create_server

print("rclpy:", rclpy.__file__)
print("ros2_control_mcp:", ros2_control_mcp.__file__)
print("server:", create_server().name)
PY
```

Verify the console entry point:

```bash
which ros2-control-mcp
```

It should normally resolve inside:

```text
~/projects/robotics/ros2_control_mcp/.venv/bin/
```

# 5. Understand the Runtime Requirement

There are two different runtime models.

## 5.1 Normal operation

The MCP server does not start a production `controller_manager`, `ros2_control_node`, or robot bringup.

Before using controller or hardware tools:

1. start the robot or simulator bringup
2. confirm that it provides the intended `/controller_manager`
3. use the same ROS domain and middleware settings for the MCP server
4. start the MCP server through the client

If no matching controller manager is reachable, ROS-backed tool calls time out.

## 5.2 Automated tests

Integration and E2E tests start their own real Jazzy `ros2_control_node` and `robot_state_publisher`, use MockSystem in an isolated `ROS_DOMAIN_ID`, and clean up the processes. Do not manually start those test processes.

# 6. Configure the ROS Runtime

Use the same domain as the ROS 2 system you intend to inspect:

```bash
source /opt/ros/jazzy/setup.bash
export ROS_DOMAIN_ID=30
```

`30` is an example. Replace it with the deployment's actual domain. If the deployment sets `RMW_IMPLEMENTATION`, the MCP server must use a compatible value.

The default controller-manager namespace is compiled into the current settings as:

```text
/controller_manager
```

Version 0.1.0 does not expose a command-line option for changing it.

# 7. Manual stdio Start

For a diagnostic start:

```bash
cd ~/projects/robotics/ros2_control_mcp
source .venv/bin/activate
source /opt/ros/jazzy/setup.bash

ros2-control-mcp
```

The process waits for MCP messages on standard input. It is not an interactive shell. Stop a manual diagnostic process with `Ctrl+C`.

Normally an MCP client starts and owns this process.

# 8. Register with Codex

The following concrete example registers the source checkout as a local stdio MCP server. Replace domain `30` with the domain used by the target robot or simulator.

```bash
cd ~/projects/robotics/ros2_control_mcp
source .venv/bin/activate
source /opt/ros/jazzy/setup.bash

codex mcp add ros2_control_mcp \
  --env ROS_DOMAIN_ID=30 \
  -- \
  bash -lc 'source /opt/ros/jazzy/setup.bash && cd ~/projects/robotics/ros2_control_mcp && source .venv/bin/activate && exec ros2-control-mcp'
```

If the deployment requires a particular middleware implementation, add the corresponding environment option, for example:

```text
--env RMW_IMPLEMENTATION=rmw_cyclonedds_cpp
```

Do not copy that example value unless the target ROS system uses it.

Inspect the registration:

```bash
codex mcp get ros2_control_mcp
```

Start Codex:

```bash
cd ~/projects/robotics/ros2_control_mcp
source /opt/ros/jazzy/setup.bash
codex
```

Inside Codex, `/mcp` should show `ros2_control_mcp`. Other MCP clients can use the same executable and stdio transport, but their configuration syntax is client-specific.

# 9. First End-User Requests

The following text belongs in the MCP client, not in a terminal.

Read-only connection check:

```text
Use ros2_control_mcp only. Do not use shell commands.
List the current ROS 2 Control controllers.
```

Inspect hardware:

```text
Use ros2_control_mcp only. Show the available hardware components, their lifecycle states, plugins, and interfaces.
```

Inspect one controller:

```text
Use ros2_control_mcp only. Show the status and interface requirements of test_position_controller.
```

The name `test_position_controller` belongs to the repository's MockSystem fixtures. A real deployment must use controller names from its own configuration.

# 10. Controlled Controller Workflow

Use this sequence only after confirming that the target controller configuration is appropriate for the connected system.

## 10.1 Load

```text
Use ros2_control_mcp to load test_position_controller. Then inspect it and confirm that its state is unconfigured.
```

## 10.2 Configure

```text
Configure test_position_controller without activating it. Then confirm that it is inactive.
```

## 10.3 Validate activation

```text
Validate activating test_position_controller without executing the switch.
Use activate=["test_position_controller"], deactivate=[], and strictness="strict".
Report every safety finding.
```

## 10.4 Activate through the switch path

```text
Activate test_position_controller through execute_controller_switch.
Do not publish command values.
Then verify the controller state and resource claims.
```

## 10.5 Deactivate

```text
Deactivate test_position_controller. Then confirm it is inactive and report its remaining resource claims.
```

## 10.6 Cleanup and unload

```text
Clean up test_position_controller and confirm it is unconfigured.
Then unload it and confirm it is no longer listed.
```

# 11. Build and Inspect the Package

Build the wheel and source distribution from the current checkout:

```bash
cd ~/projects/robotics/ros2_control_mcp
uv build --clear
```

`--clear` removes stale artifacts from earlier development versions before writing the current build.

Verify the exact 0.1.0 artifacts generated from the current `pyproject.toml`:

```bash
test -f dist/ros2_control_mcp-0.1.0-py3-none-any.whl
test -f dist/ros2_control_mcp-0.1.0.tar.gz
ls -l \
  dist/ros2_control_mcp-0.1.0-py3-none-any.whl \
  dist/ros2_control_mcp-0.1.0.tar.gz
```

The build backend and package entry point come from `pyproject.toml`. To verify exactly the 0.1.0 wheel in a separate temporary environment, choose an unused path and run:

```bash
cd ~/projects/robotics/ros2_control_mcp
uv venv --system-site-packages /tmp/ros2-control-mcp-0.1.0
uv pip install \
  --python /tmp/ros2-control-mcp-0.1.0/bin/python \
  dist/ros2_control_mcp-0.1.0-py3-none-any.whl
```

Do not install with an unrestricted `dist/*.whl` glob: a directory containing artifacts from multiple versions could select more than one wheel. The clean build plus exact filename makes the installed version unambiguous.

Verify the installed package and entry point:

```bash
source /opt/ros/jazzy/setup.bash
/tmp/ros2-control-mcp-0.1.0/bin/python -c \
  "import ros2_control_mcp; print(ros2_control_mcp.__file__)"
test -x /tmp/ros2-control-mcp-0.1.0/bin/ros2-control-mcp
```

Start the installed stdio server for a manual diagnostic check:

```bash
source /opt/ros/jazzy/setup.bash
/tmp/ros2-control-mcp-0.1.0/bin/ros2-control-mcp
```

Stop the manual process with `Ctrl+C`. A normal MCP client should own this process instead. The installed server still requires an accessible production `controller_manager` for ROS-backed operations.

MCP SDK 2.0.0 uses `{"result": ...}` wrappers for structured non-dictionary tool results such as lists and nullable objects. Dictionary-returning tools keep their fields at the top level. See the README section "MCP SDK 2.0.0 structured output" for concrete controller, claim, switch, and validation examples.

# 12. Run Automated Tests

Syntax check:

```bash
cd ~/projects/robotics/ros2_control_mcp
uv run python -m compileall src tests
```

Unit tests:

```bash
cd ~/projects/robotics/ros2_control_mcp
uv run pytest -q tests/unit
```

Integration tests:

```bash
cd ~/projects/robotics/ros2_control_mcp
source /opt/ros/jazzy/setup.bash
uv run pytest -q tests/integration
```

MCP E2E smoke test:

```bash
cd ~/projects/robotics/ros2_control_mcp
source /opt/ros/jazzy/setup.bash
uv run pytest -q tests/e2e/test_mcp_controller_switch.py -vv
```

Complete suite:

```bash
cd ~/projects/robotics/ros2_control_mcp
source /opt/ros/jazzy/setup.bash
uv run pytest -q
```

No manually started ROS processes are required for these tests.

# 13. Troubleshooting

## Tool call times out

- confirm the robot or simulator bringup is running
- confirm `/controller_manager` is the correct namespace
- confirm the client process uses the target `ROS_DOMAIN_ID`
- confirm the full Jazzy environment is sourced
- confirm compatible middleware settings

## Python cannot import rclpy

```bash
source /opt/ros/jazzy/setup.bash
python -c "import rclpy; print(rclpy.__file__)"
```

## Entry point is missing

```bash
cd ~/projects/robotics/ros2_control_mcp
uv sync
source .venv/bin/activate
which ros2-control-mcp
```

## Codex cannot start the server

- inspect `codex mcp get ros2_control_mcp`
- verify the repository path in the registered command
- verify that the command sources Jazzy and activates `.venv`
- verify that the selected ROS domain matches the target runtime

# 14. Safety Boundary

MCP access to a live controller manager is privileged operational access. Inspect state before changing it. Switch validation checks software-visible state and resource conflicts, but cannot certify physical safety. Use the robot's hardware safety systems and operating procedures.

# 15. Installation Complete

The setup is ready when:

- `ros2-control-mcp` resolves from the environment
- the MCP client can start it over stdio
- the intended ROS domain is configured
- the robot or simulator provides a reachable `/controller_manager`
- read-only MCP inspection returns the expected controllers and hardware
