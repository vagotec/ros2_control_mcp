"""Domain models for chained ros2_control controllers."""

from dataclasses import dataclass, field


@dataclass(frozen=True)
class ControllerDependency:
    """Represent a dependency between chained controllers."""

    controller_name: str
    depends_on: str
    reference_interfaces: tuple[str, ...] = field(default_factory=tuple)
