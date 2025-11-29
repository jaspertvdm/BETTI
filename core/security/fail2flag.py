"""
BETTI Flag2Fail4Intent Monitoring
Post-execution monitoring across IO/DO/OD layers

Flag2Fail monitors intent execution and flags issues:
- IO (Input/Output): Intent input validation, output verification
- DO (Device Operations): Device response, availability, correctness
- OD (Output to Device): Command delivery, device acknowledgment

When issues are detected, flags are raised and can trigger:
- split: Split complex intent into smaller parts
- retry: Retry with adjusted parameters
- halt: HALT execution via HICSS
- switch: Switch to alternative routing channel

This combines with Fail2FlagBE4Intent (BALANS pre-checks) to create
complete monitoring: before AND during execution.
"""

import logging
from typing import Dict, List, Optional, Any
from datetime import datetime
from enum import Enum
import psycopg2
from psycopg2.extras import RealDictCursor
import os
from dotenv import load_dotenv

load_dotenv()

logger = logging.getLogger(__name__)


class MonitoringLayer(Enum):
    """Flag2Fail monitoring layers"""
    IO = "IO"  # Input/Output layer
    DO = "DO"  # Device Operations layer
    OD = "OD"  # Output to Device layer


class Flag2FailEngine:
    """Flag2Fail4Intent monitoring engine"""

    def __init__(self):
        # Connect to brain database for intent logs
        self.brain_db_config = {
            'host': os.getenv('POSTGRES_HOST', '192.168.4.76'),
            'port': int(os.getenv('POSTGRES_PORT', 5432)),
            'database': os.getenv('POSTGRES_DB', 'jtel_brain'),
            'user': os.getenv('POSTGRES_USER', 'jtel_brain_user'),
            'password': os.getenv('POSTGRES_PASSWORD', 'secure_password')
        }

        # Connect to security database for flags
        self.security_db_config = {
            'host': os.getenv('SECURITY_DB_HOST', '192.168.4.76'),
            'port': int(os.getenv('SECURITY_DB_PORT', 5432)),
            'database': os.getenv('SECURITY_DB_NAME', 'jtel_security'),
            'user': os.getenv('SECURITY_DB_USER', 'jtel_security_user'),
            'password': os.getenv('SECURITY_DB_PASSWORD', 'secure_password_here')
        }

    def get_brain_conn(self):
        """Get connection to brain database"""
        return psycopg2.connect(**self.brain_db_config)

    def get_security_conn(self):
        """Get connection to security database"""
        return psycopg2.connect(**self.security_db_config)

    def monitor_io_layer(
        self,
        intent_log_id: int,
        intent: str,
        parameters: Dict,
        expected_output: Any,
        actual_output: Any
    ) -> bool:
        """
        Monitor IO (Input/Output) layer

        Checks:
        - Intent input is valid and complete
        - Output matches expected format/content
        - No unexpected errors in processing

        Returns True if passed, False if flagged
        """
        passed = True
        flags = []

        try:
            # Check 1: Input validation
            if not intent or intent.strip() == "":
                passed = False
                flags.append({
                    'check_type': 'input_validation',
                    'expected': 'non-empty intent',
                    'actual': intent,
                    'suggested_action': 'clarify'
                })

            # Check 2: Required parameters
            if not parameters:
                passed = False
                flags.append({
                    'check_type': 'input_parameters',
                    'expected': 'valid parameters',
                    'actual': 'null or empty',
                    'suggested_action': 'clarify'
                })

            # Check 3: Output validation
            if expected_output is not None and actual_output is None:
                passed = False
                flags.append({
                    'check_type': 'output_validation',
                    'expected': str(expected_output),
                    'actual': 'null',
                    'suggested_action': 'retry'
                })

            # Check 4: Output type mismatch
            if expected_output is not None and actual_output is not None:
                if type(expected_output) != type(actual_output):
                    passed = False
                    flags.append({
                        'check_type': 'output_type',
                        'expected': type(expected_output).__name__,
                        'actual': type(actual_output).__name__,
                        'suggested_action': 'split'
                    })

            # Log all checks
            self._log_monitor(
                intent_log_id=intent_log_id,
                layer=MonitoringLayer.IO,
                checks=flags if flags else [{'check_type': 'io_complete', 'passed': True}],
                passed=passed
            )

        except Exception as e:
            logger.error(f"IO monitoring error: {e}")
            passed = False

        return passed

    def monitor_do_layer(
        self,
        intent_log_id: int,
        did: str,
        command: str,
        expected_response: Optional[str],
        actual_response: Optional[str],
        device_available: bool
    ) -> bool:
        """
        Monitor DO (Device Operations) layer

        Checks:
        - Device is available and responsive
        - Device response matches expected
        - Device acknowledges command correctly

        Returns True if passed, False if flagged
        """
        passed = True
        flags = []

        try:
            # Check 1: Device availability
            if not device_available:
                passed = False
                flags.append({
                    'check_type': 'device_availability',
                    'expected': 'device online',
                    'actual': 'device offline',
                    'suggested_action': 'switch'  # Switch to alternative channel
                })

            # Check 2: Device response received
            if device_available and not actual_response:
                passed = False
                flags.append({
                    'check_type': 'device_response',
                    'expected': 'acknowledgment',
                    'actual': 'no response',
                    'suggested_action': 'retry'
                })

            # Check 3: Response correctness
            if expected_response and actual_response:
                if expected_response.lower() not in actual_response.lower():
                    passed = False
                    flags.append({
                        'check_type': 'device_response_content',
                        'expected': expected_response,
                        'actual': actual_response,
                        'suggested_action': 'retry'
                    })

            # Log all checks
            self._log_monitor(
                intent_log_id=intent_log_id,
                layer=MonitoringLayer.DO,
                checks=flags if flags else [{'check_type': 'do_complete', 'passed': True}],
                passed=passed
            )

        except Exception as e:
            logger.error(f"DO monitoring error: {e}")
            passed = False

        return passed

    def monitor_od_layer(
        self,
        intent_log_id: int,
        did: str,
        command_sent: bool,
        command_acknowledged: bool,
        execution_started: bool,
        execution_completed: bool
    ) -> bool:
        """
        Monitor OD (Output to Device) layer

        Checks:
        - Command successfully sent to device
        - Device acknowledged receipt
        - Execution started
        - Execution completed

        Returns True if passed, False if flagged
        """
        passed = True
        flags = []

        try:
            # Check 1: Command delivery
            if not command_sent:
                passed = False
                flags.append({
                    'check_type': 'command_delivery',
                    'expected': 'command sent',
                    'actual': 'send failed',
                    'suggested_action': 'switch'  # Switch channel (HTTP -> MQTT, etc.)
                })

            # Check 2: Device acknowledgment
            if command_sent and not command_acknowledged:
                passed = False
                flags.append({
                    'check_type': 'device_acknowledgment',
                    'expected': 'ACK received',
                    'actual': 'no ACK',
                    'suggested_action': 'retry'
                })

            # Check 3: Execution started
            if command_acknowledged and not execution_started:
                passed = False
                flags.append({
                    'check_type': 'execution_start',
                    'expected': 'execution started',
                    'actual': 'no execution',
                    'suggested_action': 'halt'  # Something wrong, halt and investigate
                })

            # Check 4: Execution completed
            if execution_started and not execution_completed:
                passed = False
                flags.append({
                    'check_type': 'execution_completion',
                    'expected': 'execution completed',
                    'actual': 'incomplete',
                    'suggested_action': 'split'  # May be too complex, split into parts
                })

            # Log all checks
            self._log_monitor(
                intent_log_id=intent_log_id,
                layer=MonitoringLayer.OD,
                checks=flags if flags else [{'check_type': 'od_complete', 'passed': True}],
                passed=passed
            )

        except Exception as e:
            logger.error(f"OD monitoring error: {e}")
            passed = False

        return passed

    def _log_monitor(
        self,
        intent_log_id: int,
        layer: MonitoringLayer,
        checks: List[Dict],
        passed: bool
    ):
        """Log monitoring results to security database"""

        try:
            conn = self.get_security_conn()
            cursor = conn.cursor()

            for check in checks:
                check_type = check.get('check_type', 'unknown')
                expected = check.get('expected', '')
                actual = check.get('actual', '')
                check_passed = check.get('passed', passed)
                suggested_action = check.get('suggested_action', '')

                # Determine if this should be flagged
                flagged = not check_passed and suggested_action in ['halt', 'switch']

                cursor.execute("""
                    INSERT INTO flag2fail_monitors
                    (intent_log_id, layer, check_type, expected_value, actual_value,
                     passed, flagged, suggested_action, timestamp)
                    VALUES (%s, %s, %s, %s, %s, %s, %s, %s, NOW())
                """, (
                    intent_log_id,
                    layer.value,
                    check_type,
                    expected,
                    actual,
                    check_passed,
                    flagged,
                    suggested_action
                ))

                # If flagged, also create security flag
                if flagged:
                    self._create_security_flag(
                        cursor,
                        intent_log_id=intent_log_id,
                        layer=layer.value,
                        check_type=check_type,
                        suggested_action=suggested_action
                    )

            conn.commit()
            cursor.close()
            conn.close()

        except Exception as e:
            logger.error(f"Error logging monitor results: {e}")

    def _create_security_flag(
        self,
        cursor,
        intent_log_id: int,
        layer: str,
        check_type: str,
        suggested_action: str
    ):
        """Create security flag for failed monitor check"""

        # Get DID from intent log
        cursor.execute("""
            SELECT hid FROM betti_intent_log WHERE id = %s
        """, (intent_log_id,))
        result = cursor.fetchone()
        did = result[0] if result else 'unknown'

        severity = 'warning'
        if suggested_action == 'halt':
            severity = 'error'
        elif suggested_action == 'switch':
            severity = 'warning'

        cursor.execute("""
            INSERT INTO security_flags
            (did, flag_type, severity, description, metadata, raised_at)
            VALUES (%s, %s, %s, %s, %s, NOW())
        """, (
            did,
            'flag2fail_monitor',
            severity,
            f"Flag2Fail {layer} layer: {check_type} failed",
            psycopg2.extras.Json({
                'intent_log_id': intent_log_id,
                'layer': layer,
                'check_type': check_type,
                'suggested_action': suggested_action
            })
        ))

    def get_flagged_intents(
        self,
        did: Optional[str] = None,
        layer: Optional[str] = None,
        limit: int = 100
    ) -> List[Dict]:
        """Get all flagged intents for review"""

        try:
            conn = self.get_security_conn()
            cursor = conn.cursor(cursor_factory=RealDictCursor)

            query = """
                SELECT
                    ffm.*,
                    bil.intent,
                    bil.hid as did
                FROM flag2fail_monitors ffm
                LEFT JOIN betti_intent_log bil ON ffm.intent_log_id = bil.id
                WHERE ffm.flagged = true
            """
            params = []

            if did:
                query += " AND bil.hid = %s"
                params.append(did)

            if layer:
                query += " AND ffm.layer = %s"
                params.append(layer)

            query += " ORDER BY ffm.timestamp DESC LIMIT %s"
            params.append(limit)

            cursor.execute(query, params)
            flagged = cursor.fetchall()

            cursor.close()
            conn.close()

            return [dict(f) for f in flagged]

        except Exception as e:
            logger.error(f"Error fetching flagged intents: {e}")
            return []

    def get_monitor_stats(self, days: int = 30) -> Dict:
        """Get monitoring statistics (for dashboard)"""

        try:
            conn = self.get_security_conn()
            cursor = conn.cursor(cursor_factory=RealDictCursor)

            cursor.execute("""
                SELECT
                    layer,
                    COUNT(*) as total_checks,
                    COUNT(*) FILTER (WHERE passed = true) as passed_checks,
                    COUNT(*) FILTER (WHERE passed = false) as failed_checks,
                    COUNT(*) FILTER (WHERE flagged = true) as flagged_checks,
                    ROUND(100.0 * COUNT(*) FILTER (WHERE passed = true) / COUNT(*), 2) as pass_rate
                FROM flag2fail_monitors
                WHERE timestamp > NOW() - INTERVAL '%s days'
                GROUP BY layer
                ORDER BY layer
            """, (days,))

            stats = cursor.fetchall()

            cursor.close()
            conn.close()

            return {
                'layers': [dict(s) for s in stats],
                'period_days': days
            }

        except Exception as e:
            logger.error(f"Error fetching monitor stats: {e}")
            return {'layers': [], 'period_days': days}


# Singleton instance
_flag2fail_engine = None

def get_flag2fail_engine() -> Flag2FailEngine:
    """Get singleton Flag2Fail engine instance"""
    global _flag2fail_engine
    if _flag2fail_engine is None:
        _flag2fail_engine = Flag2FailEngine()
    return _flag2fail_engine
