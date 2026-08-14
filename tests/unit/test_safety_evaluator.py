"""Tests for ros2_control safety evaluation."""

from ros2_control_mcp.domain.controllers import Controller
from ros2_control_mcp.domain.safety import SafetyStatus
from ros2_control_mcp.safety.evaluator import SafetyEvaluator


def test_activation_is_safe_without_interface_conflict() -> None:
    """Allow activation when required command interfaces are free."""
    evaluator = SafetyEvaluator()

    target = Controller(
        name="arm_controller",
        controller_type="test/ArmController",
        state="inactive",
        required_command_interfaces=("joint1/position",),
    )

    result = evaluator.validate_controller_activation(
        target=target,
        controllers=(target,),
    )

    assert result.status is SafetyStatus.SAFE
    assert result.allowed is True
    assert result.findings == ()


def test_activation_is_blocked_on_interface_conflict() -> None:
    """Block activation when another controller claims a required interface."""
    evaluator = SafetyEvaluator()

    target = Controller(
        name="arm_controller",
        controller_type="test/ArmController",
        state="inactive",
        required_command_interfaces=("joint1/position",),
    )

    active_controller = Controller(
        name="position_controller",
        controller_type="test/PositionController",
        state="active",
        claimed_interfaces=("joint1/position",),
    )

    result = evaluator.validate_controller_activation(
        target=target,
        controllers=(target, active_controller),
    )

    assert result.status is SafetyStatus.BLOCKED
    assert result.allowed is False
    assert len(result.findings) == 1
    assert result.findings[0].code == "INTERFACE_CONFLICT"


def test_activation_is_blocked_when_command_interface_is_unavailable() -> None:
    """Block activation when a required command interface is unavailable."""
    from ros2_control_mcp.domain.interfaces import HardwareInterface

    evaluator = SafetyEvaluator()

    target = Controller(
        name="arm_controller",
        controller_type="test/ArmController",
        state="inactive",
        required_command_interfaces=("joint1/position",),
    )

    command_interfaces = (
        HardwareInterface(
            name="joint1/position",
            data_type="double",
            is_available=False,
            is_claimed=False,
        ),
    )

    result = evaluator.validate_controller_activation(
        target=target,
        controllers=(target,),
        command_interfaces=command_interfaces,
    )

    assert result.status is SafetyStatus.BLOCKED
    assert result.findings[0].code == "COMMAND_INTERFACE_UNAVAILABLE"


def test_activation_is_blocked_when_state_interface_is_unavailable() -> None:
    """Block activation when a required state interface is unavailable."""
    from ros2_control_mcp.domain.interfaces import HardwareInterface

    evaluator = SafetyEvaluator()

    target = Controller(
        name="arm_controller",
        controller_type="test/ArmController",
        state="inactive",
        required_state_interfaces=("joint1/velocity",),
    )

    state_interfaces = (
        HardwareInterface(
            name="joint1/velocity",
            data_type="double",
            is_available=False,
            is_claimed=False,
        ),
    )

    result = evaluator.validate_controller_activation(
        target=target,
        controllers=(target,),
        state_interfaces=state_interfaces,
    )

    assert result.status is SafetyStatus.BLOCKED
    assert result.findings[0].code == "STATE_INTERFACE_UNAVAILABLE"


def test_activation_warns_when_controller_is_already_active() -> None:
    """Warn when the target controller is already active."""
    evaluator = SafetyEvaluator()

    target = Controller(
        name="arm_controller",
        controller_type="test/ArmController",
        state="active",
    )

    result = evaluator.validate_controller_activation(
        target=target,
        controllers=(target,),
    )

    assert result.status is SafetyStatus.WARNING
    assert result.allowed is True
    assert result.findings[0].code == "CONTROLLER_ALREADY_ACTIVE"


def test_activation_is_blocked_from_unconfigured_state() -> None:
    """Block activation when the controller is not configured."""
    evaluator = SafetyEvaluator()

    target = Controller(
        name="arm_controller",
        controller_type="test/ArmController",
        state="unconfigured",
    )

    result = evaluator.validate_controller_activation(
        target=target,
        controllers=(target,),
    )

    assert result.status is SafetyStatus.BLOCKED
    assert result.allowed is False
    assert result.findings[0].code == "INVALID_CONTROLLER_STATE"


def test_activation_warns_about_active_chain_dependency() -> None:
    """Warn when an active chained controller depends on the target."""
    from ros2_control_mcp.domain.controllers import ChainConnection

    evaluator = SafetyEvaluator()

    target = Controller(
        name="inner_controller",
        controller_type="test/InnerController",
        state="inactive",
    )

    outer = Controller(
        name="outer_controller",
        controller_type="test/OuterController",
        state="active",
        chain_connections=(
            ChainConnection(
                name="inner_controller",
                reference_interfaces=("inner_controller/joint1/position",),
            ),
        ),
    )

    result = evaluator.validate_controller_activation(
        target=target,
        controllers=(target, outer),
    )

    assert result.status is SafetyStatus.WARNING
    assert result.findings[0].code == "CHAIN_DEPENDENCY_ACTIVE"


def test_activation_warns_when_controller_is_already_active() -> None:
    """Warn when the target controller is already active."""
    evaluator = SafetyEvaluator()

    target = Controller(
        name="arm_controller",
        controller_type="test/ArmController",
        state="active",
    )

    result = evaluator.validate_controller_activation(
        target=target,
        controllers=(target,),
    )

    assert result.status is SafetyStatus.WARNING
    assert result.allowed is True
    assert result.findings[0].code == "CONTROLLER_ALREADY_ACTIVE"


def test_activation_is_blocked_from_unconfigured_state() -> None:
    """Block activation when the controller is not configured."""
    evaluator = SafetyEvaluator()

    target = Controller(
        name="arm_controller",
        controller_type="test/ArmController",
        state="unconfigured",
    )

    result = evaluator.validate_controller_activation(
        target=target,
        controllers=(target,),
    )

    assert result.status is SafetyStatus.BLOCKED
    assert result.allowed is False
    assert result.findings[0].code == "INVALID_CONTROLLER_STATE"


def test_activation_warns_about_active_chain_dependency() -> None:
    """Warn when an active chained controller depends on the target."""
    from ros2_control_mcp.domain.controllers import ChainConnection

    evaluator = SafetyEvaluator()

    target = Controller(
        name="inner_controller",
        controller_type="test/InnerController",
        state="inactive",
    )

    outer = Controller(
        name="outer_controller",
        controller_type="test/OuterController",
        state="active",
        chain_connections=(
            ChainConnection(
                name="inner_controller",
                reference_interfaces=("inner_controller/joint1/position",),
            ),
        ),
    )

    result = evaluator.validate_controller_activation(
        target=target,
        controllers=(target, outer),
    )

    assert result.status is SafetyStatus.WARNING
    assert result.findings[0].code == "CHAIN_DEPENDENCY_ACTIVE"


def test_switch_is_safe_when_conflicting_controller_is_deactivated() -> None:
    """Allow a switch when the current resource owner is deactivated."""
    from ros2_control_mcp.domain.safety import ControllerSwitchPlan

    evaluator = SafetyEvaluator()

    old_controller = Controller(
        name="old_controller",
        controller_type="test/OldController",
        state="active",
        claimed_interfaces=("joint1/position",),
    )

    new_controller = Controller(
        name="new_controller",
        controller_type="test/NewController",
        state="inactive",
        required_command_interfaces=("joint1/position",),
    )

    plan = ControllerSwitchPlan(
        activate=("new_controller",),
        deactivate=("old_controller",),
    )

    result = evaluator.validate_controller_switch(
        plan=plan,
        controllers=(old_controller, new_controller),
    )

    assert result.status is SafetyStatus.SAFE
    assert result.allowed is True


def test_switch_is_blocked_for_unknown_controller() -> None:
    """Block a switch that references an unknown controller."""
    from ros2_control_mcp.domain.safety import ControllerSwitchPlan

    evaluator = SafetyEvaluator()

    plan = ControllerSwitchPlan(
        activate=("missing_controller",),
    )

    result = evaluator.validate_controller_switch(
        plan=plan,
        controllers=(),
    )

    assert result.status is SafetyStatus.BLOCKED
    assert result.allowed is False
    assert result.findings[0].code == "CONTROLLER_NOT_FOUND"


def test_switch_is_blocked_for_activate_deactivate_overlap() -> None:
    """Block a switch containing the same controller in both sets."""
    from ros2_control_mcp.domain.safety import ControllerSwitchPlan

    evaluator = SafetyEvaluator()

    controller = Controller(
        name="arm_controller",
        controller_type="test/ArmController",
        state="inactive",
    )

    plan = ControllerSwitchPlan(
        activate=("arm_controller",),
        deactivate=("arm_controller",),
    )

    result = evaluator.validate_controller_switch(
        plan=plan,
        controllers=(controller,),
    )

    assert result.status is SafetyStatus.BLOCKED
    assert result.allowed is False
    assert result.findings[0].code == "CONTROLLER_SWITCH_OVERLAP"


def test_switch_is_blocked_when_resource_owner_remains_active() -> None:
    """Block a switch when another controller keeps the required resource."""
    from ros2_control_mcp.domain.safety import ControllerSwitchPlan

    evaluator = SafetyEvaluator()

    owner = Controller(
        name="position_controller",
        controller_type="test/PositionController",
        state="active",
        claimed_interfaces=("joint1/position",),
    )

    target = Controller(
        name="trajectory_controller",
        controller_type="test/TrajectoryController",
        state="inactive",
        required_command_interfaces=("joint1/position",),
    )

    plan = ControllerSwitchPlan(
        activate=("trajectory_controller",),
    )

    result = evaluator.validate_controller_switch(
        plan=plan,
        controllers=(owner, target),
    )

    assert result.status is SafetyStatus.BLOCKED
    assert result.allowed is False
    assert any(
        finding.code == "INTERFACE_CONFLICT"
        for finding in result.findings
    )
