"""Domain models for ros2_control hardware components."""

from dataclasses import dataclass


@dataclass(frozen=True)
class HardwareComponent:
    """Represent a ros2_control hardware component."""

    name: str
    component_type: str
    plugin_name: str
    state: str
