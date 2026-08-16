"""Domain models for ros2_control control operations."""

from dataclasses import dataclass


@dataclass(frozen=True)
class ControlResult:
    """Represent the result of a ros2_control control operation."""

    ok: bool
    message: str | None = None
