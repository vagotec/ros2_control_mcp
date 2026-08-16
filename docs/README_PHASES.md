# ros2_control_mcp Development Phases

This index links the seven technical documentation phases represented by the current `ros2_control_mcp` 0.1.0 repository.

The phases describe logical areas of the implemented system. They do not claim a historical commit order that cannot be established from the current source tree.

| Phase | Documentation | Status |
|---|---|---|
| 1 - Project Foundation | [README_PHASE_1.md](README_PHASE_1.md) | Complete |
| 2 - Domain and Application Layer | [README_PHASE_2.md](README_PHASE_2.md) | Complete |
| 3 - ROS 2 Jazzy Adapter | [README_PHASE_3.md](README_PHASE_3.md) | Complete |
| 4 - MCP Controller and Hardware Capabilities | [README_PHASE_4.md](README_PHASE_4.md) | Complete |
| 5 - Safety and Controller Switching | [README_PHASE_5.md](README_PHASE_5.md) | Complete |
| 6 - Real ROS 2 Integration and MCP E2E Validation | [README_PHASE_6.md](README_PHASE_6.md) | Complete; recorded baseline 40 tests |
| 7 - Release Preparation | [README_PHASE_7.md](README_PHASE_7.md) | Documentation prepared; license decision open |

The current architecture is:

```text
MCP Client
 -> MCPServer (stdio)
 -> Tools / Resources / Prompts
 -> Ros2ControlService
 -> Domain and switch safety
 -> Ros2ControlAdapter
 -> JazzyRos2ControlAdapter
 -> controller_manager
 -> ros2_control
```

Start with [Phase 1](README_PHASE_1.md) for the package foundation or [Phase 6](README_PHASE_6.md) for the real ROS integration and MCP E2E baseline.
