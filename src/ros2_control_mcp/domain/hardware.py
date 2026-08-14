"""Domain models for ros2_control hardware components."""

from dataclasses import dataclass, field

from ros2_control_mcp.domain.interfaces import HardwareInterface


@dataclass(frozen=True)
class HardwareComponent:
    """Represent a ros2_control hardware component."""

    name: str
    component_type: str
    is_async: bool
    rw_rate: int
    plugin_name: str
    state_id: int
    state_label: str
    command_interfaces: tuple[HardwareInterface, ...] = field(
        default_factory=tuple
    )
    state_interfaces: tuple[HardwareInterface, ...] = field(
        default_factory=tuple
    )
