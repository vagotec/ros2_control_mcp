"""Domain models for ros2_control safety validation."""

from dataclasses import dataclass, field
from enum import StrEnum


class SafetyStatus(StrEnum):
    """Represent the result of a ros2_control safety validation."""

    SAFE = "safe"
    WARNING = "warning"
    BLOCKED = "blocked"


class SafetySeverity(StrEnum):
    """Represent the severity of a validation finding."""

    INFO = "info"
    WARNING = "warning"
    ERROR = "error"


class SwitchStrictness(StrEnum):
    """Represent ros2_control controller switch strictness."""

    BEST_EFFORT = "best_effort"
    STRICT = "strict"
    AUTO = "auto"
    FORCE_AUTO = "force_auto"


@dataclass(frozen=True)
class ControllerSwitchPlan:
    """Represent a controller switch request before execution."""

    activate: tuple[str, ...] = field(default_factory=tuple)
    deactivate: tuple[str, ...] = field(default_factory=tuple)
    strictness: SwitchStrictness = SwitchStrictness.STRICT
    activate_asap: bool = False
    timeout_seconds: float = 5.0


@dataclass(frozen=True)
class SafetyFinding:
    """Represent one finding produced by a safety validation."""

    code: str
    message: str
    severity: SafetySeverity
    controller_name: str | None = None
    interface_name: str | None = None


@dataclass(frozen=True)
class SafetyResult:
    """Represent the complete result of a safety validation."""

    status: SafetyStatus
    operation: str
    findings: tuple[SafetyFinding, ...] = field(default_factory=tuple)

    @property
    def allowed(self) -> bool:
        """Return whether the validated operation may proceed."""
        return self.status is not SafetyStatus.BLOCKED
