"""Safety evaluation for ros2_control operations."""

from ros2_control_mcp.domain.controllers import Controller
from ros2_control_mcp.domain.interfaces import HardwareInterface
from ros2_control_mcp.domain.safety import (
    SafetyFinding,
    SafetyResult,
    SafetySeverity,
    SafetyStatus,
)


class SafetyEvaluator:
    """Evaluate ros2_control operations without changing system state."""

    def validate_controller_activation(
        self,
        target: Controller,
        controllers: tuple[Controller, ...],
        command_interfaces: tuple[HardwareInterface, ...] = (),
        state_interfaces: tuple[HardwareInterface, ...] = (),
    ) -> SafetyResult:
        """Validate whether a controller can be activated."""
        findings: list[SafetyFinding] = []

        if target.state == "active":
            findings.append(
                SafetyFinding(
                    code="CONTROLLER_ALREADY_ACTIVE",
                    message=f"Controller '{target.name}' is already active.",
                    severity=SafetySeverity.WARNING,
                    controller_name=target.name,
                )
            )

        if target.state not in {"inactive", "active"}:
            findings.append(
                SafetyFinding(
                    code="INVALID_CONTROLLER_STATE",
                    message=(
                        f"Controller '{target.name}' cannot be activated "
                        f"from state '{target.state}'."
                    ),
                    severity=SafetySeverity.ERROR,
                    controller_name=target.name,
                )
            )

        claimed_by_others = {
            interface: controller.name
            for controller in controllers
            if controller.name != target.name
            for interface in controller.claimed_interfaces
        }

        for interface in target.required_command_interfaces:
            owner = claimed_by_others.get(interface)
            if owner is not None:
                findings.append(
                    SafetyFinding(
                        code="INTERFACE_CONFLICT",
                        message=(
                            f"Command interface '{interface}' is already claimed "
                            f"by controller '{owner}'."
                        ),
                        severity=SafetySeverity.ERROR,
                        controller_name=target.name,
                        interface_name=interface,
                    )
                )

        available_command_interfaces = {
            interface.name
            for interface in command_interfaces
            if interface.is_available
        }

        available_state_interfaces = {
            interface.name
            for interface in state_interfaces
            if interface.is_available
        }

        for interface in target.required_command_interfaces:
            if command_interfaces and interface not in available_command_interfaces:
                findings.append(
                    SafetyFinding(
                        code="COMMAND_INTERFACE_UNAVAILABLE",
                        message=(
                            f"Required command interface '{interface}' "
                            "is not available."
                        ),
                        severity=SafetySeverity.ERROR,
                        controller_name=target.name,
                        interface_name=interface,
                    )
                )

        for interface in target.required_state_interfaces:
            if state_interfaces and interface not in available_state_interfaces:
                findings.append(
                    SafetyFinding(
                        code="STATE_INTERFACE_UNAVAILABLE",
                        message=(
                            f"Required state interface '{interface}' "
                            "is not available."
                        ),
                        severity=SafetySeverity.ERROR,
                        controller_name=target.name,
                        interface_name=interface,
                    )
                )

        for controller in controllers:
            for connection in controller.chain_connections:
                if connection.name == target.name and controller.state == "active":
                    findings.append(
                        SafetyFinding(
                            code="CHAIN_DEPENDENCY_ACTIVE",
                            message=(
                                f"Active controller '{controller.name}' depends "
                                f"on '{target.name}'."
                            ),
                            severity=SafetySeverity.WARNING,
                            controller_name=target.name,
                        )
                    )

        has_errors = any(
            finding.severity is SafetySeverity.ERROR
            for finding in findings
        )

        has_warnings = any(
            finding.severity is SafetySeverity.WARNING
            for finding in findings
        )

        if has_errors:
            status = SafetyStatus.BLOCKED
        elif has_warnings:
            status = SafetyStatus.WARNING
        else:
            status = SafetyStatus.SAFE

        return SafetyResult(
            status=status,
            operation="activate_controller",
            findings=tuple(findings),
        )


    def validate_controller_switch(
        self,
        plan: "ControllerSwitchPlan",
        controllers: tuple[Controller, ...],
        command_interfaces: tuple[HardwareInterface, ...] = (),
        state_interfaces: tuple[HardwareInterface, ...] = (),
    ) -> SafetyResult:
        """Validate a complete controller switch without executing it."""
        from ros2_control_mcp.domain.safety import ControllerSwitchPlan

        findings: list[SafetyFinding] = []
        controllers_by_name = {
            controller.name: controller
            for controller in controllers
        }

        activate_names = set(plan.activate)
        deactivate_names = set(plan.deactivate)

        overlap = activate_names & deactivate_names
        for name in sorted(overlap):
            findings.append(
                SafetyFinding(
                    code="CONTROLLER_SWITCH_OVERLAP",
                    message=(
                        f"Controller '{name}' is requested for both "
                        "activation and deactivation."
                    ),
                    severity=SafetySeverity.ERROR,
                    controller_name=name,
                )
            )

        requested_names = activate_names | deactivate_names
        for name in sorted(requested_names):
            if name not in controllers_by_name:
                findings.append(
                    SafetyFinding(
                        code="CONTROLLER_NOT_FOUND",
                        message=f"Controller '{name}' does not exist.",
                        severity=SafetySeverity.ERROR,
                        controller_name=name,
                    )
                )

        remaining_controllers = tuple(
            controller
            for controller in controllers
            if controller.name not in deactivate_names
        )

        for name in plan.activate:
            target = controllers_by_name.get(name)
            if target is None or name in overlap:
                continue

            activation_result = self.validate_controller_activation(
                target=target,
                controllers=remaining_controllers,
                command_interfaces=command_interfaces,
                state_interfaces=state_interfaces,
            )

            findings.extend(activation_result.findings)

        has_errors = any(
            finding.severity is SafetySeverity.ERROR
            for finding in findings
        )
        has_warnings = any(
            finding.severity is SafetySeverity.WARNING
            for finding in findings
        )

        if has_errors:
            status = SafetyStatus.BLOCKED
        elif has_warnings:
            status = SafetyStatus.WARNING
        else:
            status = SafetyStatus.SAFE

        return SafetyResult(
            status=status,
            operation="switch_controllers",
            findings=tuple(findings),
        )
