"""Domain models for ros2_control resource claims."""

from dataclasses import dataclass


@dataclass(frozen=True)
class ResourceClaim:
    """Represent a command interface claimed by a controller."""

    interface_name: str
    controller_name: str
