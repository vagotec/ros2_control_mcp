"""Domain models for ros2_control hardware interfaces."""

from dataclasses import dataclass


@dataclass(frozen=True)
class HardwareInterface:
    """Represent a ros2_control hardware interface."""

    name: str
    data_type: str
    is_available: bool
    is_claimed: bool
