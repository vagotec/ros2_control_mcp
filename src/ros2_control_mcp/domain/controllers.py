"""Domain models for ros2_control controllers."""

from dataclasses import dataclass, field


@dataclass(frozen=True)
class Controller:
    """Represent a ros2_control controller."""

    name: str
    controller_type: str
    state: str
    claimed_interfaces: tuple[str, ...] = field(default_factory=tuple)
    required_command_interfaces: tuple[str, ...] = field(default_factory=tuple)
    required_state_interfaces: tuple[str, ...] = field(default_factory=tuple)
