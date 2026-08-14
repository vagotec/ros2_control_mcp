"""Domain models for ros2_control safety evaluation."""

from dataclasses import dataclass, field


@dataclass(frozen=True)
class SafetyAssessment:
    """Represent the result of a safety validation."""

    allowed: bool
    warnings: tuple[str, ...] = field(default_factory=tuple)
    conflicts: tuple[str, ...] = field(default_factory=tuple)
