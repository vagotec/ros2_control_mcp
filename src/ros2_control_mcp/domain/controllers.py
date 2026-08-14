"""Domain models for ros2_control controllers."""

from dataclasses import dataclass, field


@dataclass(frozen=True)
class ChainConnection:
    """Represent a connection to another controller in a chain."""

    name: str
    reference_interfaces: tuple[str, ...] = field(default_factory=tuple)


@dataclass(frozen=True)
class ControllerType:
    """Represent an available ros2_control controller type."""

    name: str
    base_class: str


@dataclass(frozen=True)
class Controller:
    """Represent a ros2_control controller."""

    name: str
    controller_type: str
    state: str
    is_async: bool = False
    update_rate: int = 0
    claimed_interfaces: tuple[str, ...] = field(default_factory=tuple)
    required_command_interfaces: tuple[str, ...] = field(default_factory=tuple)
    required_state_interfaces: tuple[str, ...] = field(default_factory=tuple)
    is_chainable: bool = False
    is_chained: bool = False
    exported_state_interfaces: tuple[str, ...] = field(default_factory=tuple)
    reference_interfaces: tuple[str, ...] = field(default_factory=tuple)
    chain_connections: tuple[ChainConnection, ...] = field(default_factory=tuple)
