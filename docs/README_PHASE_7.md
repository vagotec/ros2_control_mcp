# Phase 7 - Release Preparation

This phase describes the current release-preparation state. It does not claim that a commit or release tag already exists.

## Goal

Align package metadata and documentation with the implemented and previously validated 0.1.0 scope.

## Architecture / Implementation

Release preparation includes:

- package version `0.1.0`
- current README and end-user workflow
- separated runtime, development, and test requirements
- source installation, stdio/Codex registration, and package-build instructions
- individual technical phase documents
- changelog for 0.1.0
- explicit Apache License 2.0 decision

The locked MCP SDK baseline is `mcp 2.0.0`. The runtime entry point remains:

```text
ros2-control-mcp = ros2_control_mcp.server:main
```

## Relevant Components / Files

```text
README.md
CHANGELOG.md
docs/REQUIREMENTS.md
docs/INSTALLATION.md
docs/README_PHASES.md
docs/README_PHASE_1.md ... docs/README_PHASE_7.md
pyproject.toml
uv.lock
```

## Commands

Inspect the release metadata and working tree:

```bash
cd ~/projects/robotics/ros2_control_mcp
git status --short
git diff --stat
```

Build the documented artifacts:

```bash
uv build
ls -l dist/*.whl dist/*.tar.gz
```

Syntax check:

```bash
uv run python -m compileall src tests
```

No commit or tag is created by the documentation phase itself.

## MCP End-User Usage

Release documentation enables a first read-only client check:

```text
Use ros2_control_mcp only. Do not use shell commands.
List the current ROS 2 Control controllers and hardware components.
```

The robot or simulator bringup must already provide the intended controller manager during normal operation.

## Tests / Validation

The already recorded release baseline can be reproduced in a sourced Jazzy environment with:

```bash
source /opt/ros/jazzy/setup.bash
uv run pytest -q
```

The documented baseline is 40 passing pytest tests, including five real Jazzy integration tests and one MCP E2E smoke test. This documentation phase does not add or alter tests.

## Expected Result

- all documents report version `0.1.0`
- ROS target remains Jazzy and Python requirement remains `>=3.12`
- capability inventories match 15 tools, five resources, and four prompts
- package build produces `dist/*.whl` and `dist/*.tar.gz`
- final publication remains separate from documentation preparation

## Architecture Decisions

- documentation follows the phase-file pattern used by the `ros2_mcp` reference project
- technical content remains specific to `ros2_control_mcp`
- no external project implementation is copied
- Apache License 2.0 is recorded following maintainer approval

## Known Limitations

- Apache License 2.0 has been selected
- no release commit or `v0.1.0` tag is created by this phase
- test results are the recorded baseline until explicitly rerun during final verification

## Result

The project has release-oriented README, requirements, installation, phase documentation, and changelog aligned with the current code.

## Next Phase

There is no invented Phase 8. The release owner must decide the license, run the authorized final verification, commit the intended files, and create the release tag when appropriate.
