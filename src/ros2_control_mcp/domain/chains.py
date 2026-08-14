"""Domain models for chained ros2_control controllers."""

from dataclasses import dataclass


@dataclass(frozen=True)
class ControllerDependency:
    """Represent a dependency between two controllers."""

    controller_name: str
    depends_on: str
