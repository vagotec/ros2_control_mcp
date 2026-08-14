"""Configuration settings for ros2_control_mcp."""

from dataclasses import dataclass


@dataclass(frozen=True)
class Settings:
    """Store runtime configuration for ros2_control_mcp."""

    default_controller_manager: str = "/controller_manager"
    service_timeout_seconds: float = 5.0
