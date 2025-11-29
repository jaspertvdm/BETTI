"""
HICSS - HALT, INTENT, CHANGE, SWITCH, STOP
Human Override System for BETTI Intents

Allows humans to override running intents with verified TIBET tokens.
Implements Flag2Fail4Intent monitoring (IO/DO/OD layers).
"""

from dataclasses import dataclass
from typing import Dict, Any, List, Optional
from datetime import datetime
import json


@dataclass
class HICSSOverride:
    """HICSS override command"""
    intent_log_id: int
    hid: str
    override_type: str  # HALT/INTENT/CHANGE/SWITCH/STOP
    original_intent: str
    new_intent: Optional[str] = None
    new_params: Optional[Dict[str, Any]] = None
    reason: Optional[str] = None
    tibet_token: str = None
    timestamp: datetime = None
    executed: bool = False
    execution_result: Optional[Dict[str, Any]] = None


@dataclass
class IntentState:
    """State of a running/halted intent"""
    intent_log_id: int
    state: str  # running/halted/stopped/completed/failed
    state_data: Optional[Dict[str, Any]] = None
    checkpoint_at: datetime = None
    resume_token: Optional[str] = None


@dataclass
class Flag2FailMonitor:
    """Flag2Fail4Intent monitoring result"""
    intent_log_id: int
    layer: str  # IO/DO/OD
    check_type: str
    expected_value: Any
    actual_value: Any
    passed: bool
    flagged: bool = False
    suggested_action: Optional[str] = None


# ============================================================================
# HICSS Override Functions
# ============================================================================

def verify_override_permission(tibet_token: str, conn) -> bool:
    """
    Verify that TIBET token has override permission

    In production, this would verify:
    - Token signature is valid
    - Token grants admin/override permission
    - Token hasn't expired
    """
    # TODO: Implement actual TIBET verification
    # For now, accept any non-empty token
    return bool(tibet_token and len(tibet_token) > 10)


def get_intent_by_id(intent_id: int, conn) -> Optional[Dict[str, Any]]:
    """Get intent from database by ID"""
    cur = conn.cursor()
    cur.execute("""
        SELECT id, user_id, intent, context, result, state, timestamp
        FROM betti_intent_log
        WHERE id = %s
    """, (intent_id,))
    row = cur.fetchone()
    cur.close()

    if not row:
        return None

    return {
        "id": row[0],
        "user_id": row[1],
        "intent": row[2],
        "context": row[3],
        "result": row[4],
        "state": row[5],
        "timestamp": row[6]
    }


def log_hicss_override(
    intent_log_id: int,
    hid: str,
    override_type: str,
    original_intent: str,
    tibet_token: str,
    conn,
    new_intent: str = None,
    new_params: Dict[str, Any] = None,
    reason: str = None,
    executed: bool = True,
    execution_result: Dict[str, Any] = None
) -> int:
    """Log HICSS override to database"""
    cur = conn.cursor()
    cur.execute("""
        INSERT INTO hicss_overrides (
            intent_log_id, hid, override_type, original_intent,
            new_intent, new_params, reason, tibet_token,
            executed, execution_result
        ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
        RETURNING id
    """, (
        intent_log_id, hid, override_type, original_intent,
        new_intent, json.dumps(new_params) if new_params else None,
        reason, tibet_token, executed,
        json.dumps(execution_result) if execution_result else None
    ))
    override_id = cur.fetchone()[0]

    # Increment override count on intent
    cur.execute("""
        UPDATE betti_intent_log
        SET override_count = COALESCE(override_count, 0) + 1
        WHERE id = %s
    """, (intent_log_id,))

    conn.commit()
    cur.close()
    return override_id


def update_intent_state(intent_log_id: int, state: str, conn, state_data: Dict[str, Any] = None) -> None:
    """Update intent state in database"""
    cur = conn.cursor()

    # Update state in intent_log
    cur.execute("""
        UPDATE betti_intent_log
        SET state = %s
        WHERE id = %s
    """, (state, intent_log_id))

    # Insert state checkpoint
    cur.execute("""
        INSERT INTO intent_states (intent_log_id, state, state_data)
        VALUES (%s, %s, %s)
    """, (intent_log_id, state, json.dumps(state_data) if state_data else None))

    conn.commit()
    cur.close()


# ============================================================================
# HICSS Override Handlers
# ============================================================================

def hicss_halt(intent_id: int, hid: str, tibet_token: str, reason: str, conn) -> Dict[str, Any]:
    """
    HALT: Pause execution, save state for resume
    """
    intent = get_intent_by_id(intent_id, conn)
    if not intent:
        return {"status": "error", "error": "Intent not found"}

    if intent["state"] != "running":
        return {"status": "error", "error": f"Cannot halt intent in state: {intent['state']}"}

    # Save state
    state_data = {
        "halted_at": datetime.now().isoformat(),
        "context": intent["context"],
        "partial_result": intent.get("result"),
        "reason": reason
    }

    # Generate resume token (in production, this would be cryptographically secure)
    resume_token = f"RESUME:{intent_id}:{datetime.now().timestamp()}"

    # Update state
    update_intent_state(intent_id, "halted", conn, state_data)

    cur = conn.cursor()
    cur.execute("""
        UPDATE betti_intent_log
        SET halted_at = NOW()
        WHERE id = %s
    """, (intent_id,))
    conn.commit()
    cur.close()

    # Log override
    log_hicss_override(
        intent_id, hid, "HALT", intent["intent"], tibet_token, conn,
        reason=reason,
        execution_result={"resume_token": resume_token, "state_saved": True}
    )

    return {
        "status": "halted",
        "intent_id": intent_id,
        "resume_token": resume_token,
        "message": f"Intent halted. Use resume_token to continue."
    }


def hicss_intent(
    intent_id: int,
    hid: str,
    new_intent: str,
    new_context: Dict[str, Any],
    tibet_token: str,
    reason: str,
    conn
) -> Dict[str, Any]:
    """
    INTENT: Override with completely new intent
    """
    intent = get_intent_by_id(intent_id, conn)
    if not intent:
        return {"status": "error", "error": "Intent not found"}

    # Cancel old intent
    update_intent_state(intent_id, "stopped", conn, {"reason": "INTENT override", "cancelled_by": hid})

    # Log override
    log_hicss_override(
        intent_id, hid, "INTENT", intent["intent"], tibet_token, conn,
        new_intent=new_intent,
        new_params=new_context,
        reason=reason,
        execution_result={"old_intent_cancelled": True}
    )

    # Return indication to execute new intent
    # (Actual execution happens in endpoint layer)
    return {
        "status": "overridden",
        "old_intent_id": intent_id,
        "new_intent": new_intent,
        "new_context": new_context,
        "message": "Old intent cancelled. Execute new intent with provided context."
    }


def hicss_change(
    intent_id: int,
    hid: str,
    new_params: Dict[str, Any],
    tibet_token: str,
    reason: str,
    conn
) -> Dict[str, Any]:
    """
    CHANGE: Modify parameters mid-execution
    """
    intent = get_intent_by_id(intent_id, conn)
    if not intent:
        return {"status": "error", "error": "Intent not found"}

    if intent["state"] not in ["running", "halted"]:
        return {"status": "error", "error": f"Cannot change intent in state: {intent['state']}"}

    # Merge new params with existing context
    current_context = intent.get("context", {})
    updated_context = {**current_context, **new_params}

    # Update context in database
    cur = conn.cursor()
    cur.execute("""
        UPDATE betti_intent_log
        SET context = %s
        WHERE id = %s
    """, (json.dumps(updated_context), intent_id))
    conn.commit()
    cur.close()

    # Log override
    log_hicss_override(
        intent_id, hid, "CHANGE", intent["intent"], tibet_token, conn,
        new_params=new_params,
        reason=reason,
        execution_result={"params_updated": True, "updated_context": updated_context}
    )

    return {
        "status": "changed",
        "intent_id": intent_id,
        "updated_context": updated_context,
        "message": "Intent parameters updated. Execution continues with new params."
    }


def hicss_switch(
    intent_id: int,
    hid: str,
    new_strategy: str,
    tibet_token: str,
    reason: str,
    conn
) -> Dict[str, Any]:
    """
    SWITCH: Change execution strategy (e.g., different split strategy)
    """
    intent = get_intent_by_id(intent_id, conn)
    if not intent:
        return {"status": "error", "error": "Intent not found"}

    # Save switch strategy in context
    current_context = intent.get("context", {})
    updated_context = {
        **current_context,
        "execution_strategy": new_strategy,
        "switched_by": hid,
        "switched_at": datetime.now().isoformat()
    }

    cur = conn.cursor()
    cur.execute("""
        UPDATE betti_intent_log
        SET context = %s
        WHERE id = %s
    """, (json.dumps(updated_context), intent_id))
    conn.commit()
    cur.close()

    # Log override
    log_hicss_override(
        intent_id, hid, "SWITCH", intent["intent"], tibet_token, conn,
        new_params={"strategy": new_strategy},
        reason=reason,
        execution_result={"strategy_switched": True, "new_strategy": new_strategy}
    )

    return {
        "status": "switched",
        "intent_id": intent_id,
        "new_strategy": new_strategy,
        "message": f"Execution strategy switched to: {new_strategy}"
    }


def hicss_stop(intent_id: int, hid: str, tibet_token: str, reason: str, conn) -> Dict[str, Any]:
    """
    STOP: Immediate halt with rollback if possible
    """
    intent = get_intent_by_id(intent_id, conn)
    if not intent:
        return {"status": "error", "error": "Intent not found"}

    if intent["state"] in ["stopped", "completed"]:
        return {"status": "error", "error": f"Intent already {intent['state']}"}

    # Attempt rollback (in production, this would undo actions)
    rollback_result = {"rolled_back": False, "reason": "Rollback not implemented"}

    # Mark as stopped
    update_intent_state(intent_id, "stopped", conn, {"stopped_by": hid, "reason": reason})

    # Log override
    log_hicss_override(
        intent_id, hid, "STOP", intent["intent"], tibet_token, conn,
        reason=reason,
        execution_result={"stopped": True, "rollback": rollback_result}
    )

    return {
        "status": "stopped",
        "intent_id": intent_id,
        "rollback": rollback_result,
        "message": "Intent stopped immediately."
    }


# ============================================================================
# Flag2Fail4Intent Monitoring
# ============================================================================

def monitor_io_layer(
    intent_id: int,
    expected_input: Any,
    actual_input: Any,
    expected_output: Any,
    actual_output: Any,
    conn
) -> List[Flag2FailMonitor]:
    """
    Monitor IO (Input-Output) layer
    Checks if inputs and outputs match expectations
    """
    monitors = []

    # Check input
    input_passed = (actual_input == expected_input) if expected_input is not None else True
    monitors.append(Flag2FailMonitor(
        intent_log_id=intent_id,
        layer="IO",
        check_type="input",
        expected_value=str(expected_input),
        actual_value=str(actual_input),
        passed=input_passed,
        flagged=not input_passed,
        suggested_action="retry" if not input_passed else None
    ))

    # Check output
    output_passed = (actual_output == expected_output) if expected_output is not None else True
    monitors.append(Flag2FailMonitor(
        intent_log_id=intent_id,
        layer="IO",
        check_type="output",
        expected_value=str(expected_output),
        actual_value=str(actual_output),
        passed=output_passed,
        flagged=not output_passed,
        suggested_action="split" if not output_passed else None
    ))

    return monitors


def monitor_do_layer(intent_id: int, devices: List[str], conn) -> List[Flag2FailMonitor]:
    """
    Monitor DO (Device-Output) layer
    Checks if devices are responding correctly
    """
    monitors = []

    for device in devices:
        # Check device availability (stub - in production, ping device)
        device_available = True  # TODO: Actual device health check

        monitors.append(Flag2FailMonitor(
            intent_log_id=intent_id,
            layer="DO",
            check_type="device_availability",
            expected_value="online",
            actual_value="online" if device_available else "offline",
            passed=device_available,
            flagged=not device_available,
            suggested_action="switch" if not device_available else None
        ))

    return monitors


def monitor_od_layer(
    intent_id: int,
    device: str,
    expected_response: Any,
    actual_response: Any,
    conn
) -> Flag2FailMonitor:
    """
    Monitor OD (Output-Device) layer
    Checks if device output matches expectations
    """
    response_passed = (actual_response == expected_response) if expected_response is not None else True

    return Flag2FailMonitor(
        intent_log_id=intent_id,
        layer="OD",
        check_type="device_response",
        expected_value=str(expected_response),
        actual_value=str(actual_response),
        passed=response_passed,
        flagged=not response_passed,
        suggested_action="halt" if not response_passed else None
    )


def log_flag2fail_monitor(monitor: Flag2FailMonitor, conn) -> int:
    """Log Flag2Fail monitor result to database"""
    cur = conn.cursor()
    cur.execute("""
        INSERT INTO flag2fail_monitors (
            intent_log_id, layer, check_type,
            expected_value, actual_value, passed, flagged, suggested_action
        ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
        RETURNING id
    """, (
        monitor.intent_log_id, monitor.layer, monitor.check_type,
        str(monitor.expected_value), str(monitor.actual_value),
        monitor.passed, monitor.flagged, monitor.suggested_action
    ))
    monitor_id = cur.fetchone()[0]
    conn.commit()
    cur.close()
    return monitor_id


def check_all_layers(
    intent_id: int,
    expected_input: Any,
    actual_input: Any,
    expected_output: Any,
    actual_output: Any,
    devices: List[str],
    conn
) -> Dict[str, Any]:
    """
    Run all Flag2Fail4Intent checks (IO/DO/OD)
    Returns aggregated results with flags
    """
    all_monitors = []

    # IO Layer
    io_monitors = monitor_io_layer(intent_id, expected_input, actual_input, expected_output, actual_output, conn)
    all_monitors.extend(io_monitors)

    # DO Layer
    do_monitors = monitor_do_layer(intent_id, devices, conn)
    all_monitors.extend(do_monitors)

    # Log all monitors
    for monitor in all_monitors:
        log_flag2fail_monitor(monitor, conn)

    # Aggregate results
    flagged_monitors = [m for m in all_monitors if m.flagged]
    all_passed = all(m.passed for m in all_monitors)

    return {
        "all_passed": all_passed,
        "total_checks": len(all_monitors),
        "failed_checks": len([m for m in all_monitors if not m.passed]),
        "flagged_count": len(flagged_monitors),
        "flagged_monitors": [
            {
                "layer": m.layer,
                "check_type": m.check_type,
                "expected": m.expected_value,
                "actual": m.actual_value,
                "suggested_action": m.suggested_action
            }
            for m in flagged_monitors
        ]
    }


# ============================================================================
# Test Cases
# ============================================================================

if __name__ == "__main__":
    print("HICSS - HALT, INTENT, CHANGE, SWITCH, STOP")
    print("=" * 50)

    # Test Flag2Fail monitoring
    print("\nTest: Flag2Fail4Intent Monitoring")
    print("-" * 50)

    test_monitor_io = Flag2FailMonitor(
        intent_log_id=1,
        layer="IO",
        check_type="input",
        expected_value="turn_on",
        actual_value="turn_on",
        passed=True
    )
    print(f"IO Layer Check: {test_monitor_io}")

    test_monitor_do_fail = Flag2FailMonitor(
        intent_log_id=1,
        layer="DO",
        check_type="device_availability",
        expected_value="online",
        actual_value="offline",
        passed=False,
        flagged=True,
        suggested_action="switch"
    )
    print(f"DO Layer Check (FLAGGED): {test_monitor_do_fail}")

    print("\n✓ HICSS system ready for integration")
