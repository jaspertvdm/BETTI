"""
BETTI SNAFT Engine (System Not Authorized For That)
Factory-embedded firewall rules for devices

SNAFT is the latent, immutable safety layer that prevents devices from
executing intents that violate factory-embedded constraints.

Examples:
- Drones cannot fly near airports (FAA regulations)
- Robots cannot weaponize (ethical constraints)
- Cars cannot exceed speed limits (safety regulations)
- Phones cannot access unauthorized APIs (security)
"""

import re
import logging
from typing import Dict, List, Optional, Tuple
from datetime import datetime
import psycopg2
from psycopg2.extras import RealDictCursor
import os
from dotenv import load_dotenv

load_dotenv()

logger = logging.getLogger(__name__)

class SNAFTEngine:
    """SNAFT (System Not Authorized For That) firewall engine"""

    def __init__(self):
        self.security_db_config = {
            'host': os.getenv('SECURITY_DB_HOST', '192.168.4.76'),
            'port': int(os.getenv('SECURITY_DB_PORT', 5432)),
            'database': os.getenv('SECURITY_DB_NAME', 'jtel_security'),
            'user': os.getenv('SECURITY_DB_USER', 'jtel_security_user'),
            'password': os.getenv('SECURITY_DB_PASSWORD', 'secure_password_here')
        }

    def get_security_conn(self):
        """Get connection to security database"""
        return psycopg2.connect(**self.security_db_config)

    def check_snaft(
        self,
        did: str,
        device_type: str,
        manufacturer: str,
        intent: str,
        parameters: Optional[Dict] = None
    ) -> Tuple[bool, Optional[Dict]]:
        """
        Check if intent violates SNAFT rules

        Args:
            did: Device ID
            device_type: robot/drone/car/phone/iot
            manufacturer: Device manufacturer
            intent: Intent to execute
            parameters: Intent parameters

        Returns:
            (is_allowed, violation_info)
            - is_allowed: True if intent is allowed, False if SNAFT violation
            - violation_info: Dict with violation details if blocked, None if allowed
        """
        try:
            conn = self.get_security_conn()
            cursor = conn.cursor(cursor_factory=RealDictCursor)

            # Get all SNAFT rules for this device type and manufacturer
            cursor.execute("""
                SELECT * FROM snaft_rules
                WHERE (device_type = %s OR device_type = 'all')
                  AND (manufacturer = %s OR manufacturer = 'all')
                  AND enabled = true
                ORDER BY severity DESC, immutable DESC
            """, (device_type, manufacturer))

            rules = cursor.fetchall()

            for rule in rules:
                violated = False
                violation_detail = None

                # Check intent pattern blocking
                if rule['rule_type'] == 'intent_block' and rule['intent_pattern']:
                    pattern = rule['intent_pattern']
                    if re.match(pattern, intent, re.IGNORECASE):
                        violated = True
                        violation_detail = f"Intent '{intent}' matches blocked pattern '{pattern}'"

                # Check capability limits
                elif rule['rule_type'] == 'capability_limit' and rule['capability_limit']:
                    limits = rule['capability_limit']
                    if parameters:
                        # Check each limit against parameters
                        for param_key, param_value in parameters.items():
                            if param_key in limits:
                                limit = limits[param_key]
                                if isinstance(param_value, (int, float)) and param_value > limit:
                                    violated = True
                                    violation_detail = f"Parameter '{param_key}' ({param_value}) exceeds limit ({limit})"
                                    break

                # Check safety constraints
                elif rule['rule_type'] == 'safety_constraint' and rule['constraint_check']:
                    # Evaluate safety constraint (custom logic)
                    constraint_result = self._evaluate_constraint(
                        rule['constraint_check'],
                        intent,
                        parameters
                    )
                    if not constraint_result:
                        violated = True
                        violation_detail = f"Failed safety constraint: {rule['constraint_check']}"

                if violated:
                    # Log SNAFT violation
                    violation_info = self._log_snaft_violation(
                        cursor,
                        did=did,
                        device_type=device_type,
                        manufacturer=manufacturer,
                        intent=intent,
                        parameters=parameters,
                        rule_id=rule['id'],
                        rule_type=rule['rule_type'],
                        reason=rule['reason'],
                        severity=rule['severity'],
                        violation_detail=violation_detail,
                        immutable=rule['immutable']
                    )

                    conn.commit()
                    cursor.close()
                    conn.close()

                    return False, violation_info

            # No violations - intent is allowed
            cursor.close()
            conn.close()
            return True, None

        except Exception as e:
            logger.error(f"SNAFT check error: {e}")
            # Fail-safe: If SNAFT check fails, deny by default (security first)
            return False, {
                'error': 'SNAFT_CHECK_FAILED',
                'message': 'Unable to verify SNAFT compliance - denying by default',
                'severity': 'critical'
            }

    def _evaluate_constraint(
        self,
        constraint_check: str,
        intent: str,
        parameters: Optional[Dict]
    ) -> bool:
        """
        Evaluate custom safety constraint

        Args:
            constraint_check: Python expression to evaluate
            intent: Intent being checked
            parameters: Intent parameters

        Returns:
            True if constraint passed, False if violated
        """
        try:
            # Create safe evaluation context
            context = {
                'intent': intent,
                'parameters': parameters or {},
                're': re
            }

            # Evaluate constraint (sandboxed)
            result = eval(constraint_check, {"__builtins__": {}}, context)
            return bool(result)

        except Exception as e:
            logger.error(f"Constraint evaluation error: {e}")
            # If constraint evaluation fails, fail safe (deny)
            return False

    def _log_snaft_violation(
        self,
        cursor,
        did: str,
        device_type: str,
        manufacturer: str,
        intent: str,
        parameters: Optional[Dict],
        rule_id: int,
        rule_type: str,
        reason: str,
        severity: str,
        violation_detail: str,
        immutable: bool
    ) -> Dict:
        """Log SNAFT violation to security database"""

        cursor.execute("""
            INSERT INTO snaft_violations
            (did, device_type, manufacturer, intent, parameters, rule_id,
             rule_type, reason, severity, violation_detail, immutable, timestamp)
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, NOW())
            RETURNING id, timestamp
        """, (
            did, device_type, manufacturer, intent,
            psycopg2.extras.Json(parameters) if parameters else None,
            rule_id, rule_type, reason, severity, violation_detail, immutable
        ))

        result = cursor.fetchone()

        # Update device awareness (robot learning from violation)
        self._update_device_awareness(cursor, did, 'snaft_violation')

        # Create security flag if severity is high
        if severity in ['error', 'critical']:
            self._create_security_flag(
                cursor,
                did=did,
                flag_type='snaft_violation',
                severity=severity,
                description=f"SNAFT violation: {reason}",
                metadata={
                    'intent': intent,
                    'rule_type': rule_type,
                    'violation_detail': violation_detail,
                    'immutable': immutable
                }
            )

        return {
            'violation_id': result['id'],
            'timestamp': result['timestamp'],
            'reason': reason,
            'severity': severity,
            'violation_detail': violation_detail,
            'immutable': immutable,
            'blocked': True
        }

    def _update_device_awareness(
        self,
        cursor,
        did: str,
        awareness_event: str
    ):
        """Update device awareness from SNAFT events"""

        cursor.execute("""
            INSERT INTO device_awareness (did, snaft_violations_learned)
            VALUES (%s, 1)
            ON CONFLICT (did) DO UPDATE SET
                snaft_violations_learned = device_awareness.snaft_violations_learned + 1,
                self_awareness_level = LEAST(10, device_awareness.self_awareness_level + 1),
                threat_awareness_level = LEAST(10, device_awareness.threat_awareness_level + 1),
                updated_at = NOW()
        """, (did,))

    def _create_security_flag(
        self,
        cursor,
        did: str,
        flag_type: str,
        severity: str,
        description: str,
        metadata: Dict
    ):
        """Create security flag for SNAFT violation"""

        cursor.execute("""
            INSERT INTO security_flags
            (did, flag_type, severity, description, metadata, raised_at)
            VALUES (%s, %s, %s, %s, %s, NOW())
        """, (
            did,
            flag_type,
            severity,
            description,
            psycopg2.extras.Json(metadata)
        ))

    def get_snaft_rules(
        self,
        device_type: Optional[str] = None,
        manufacturer: Optional[str] = None
    ) -> List[Dict]:
        """Get all SNAFT rules (for admin/debugging)"""

        try:
            conn = self.get_security_conn()
            cursor = conn.cursor(cursor_factory=RealDictCursor)

            query = "SELECT * FROM snaft_rules WHERE enabled = true"
            params = []

            if device_type:
                query += " AND device_type = %s"
                params.append(device_type)

            if manufacturer:
                query += " AND manufacturer = %s"
                params.append(manufacturer)

            query += " ORDER BY severity DESC, immutable DESC"

            cursor.execute(query, params)
            rules = cursor.fetchall()

            cursor.close()
            conn.close()

            return [dict(rule) for rule in rules]

        except Exception as e:
            logger.error(f"Error fetching SNAFT rules: {e}")
            return []

    def get_snaft_violations(
        self,
        did: Optional[str] = None,
        limit: int = 100
    ) -> List[Dict]:
        """Get SNAFT violation history"""

        try:
            conn = self.get_security_conn()
            cursor = conn.cursor(cursor_factory=RealDictCursor)

            query = """
                SELECT sv.*, sr.reason as rule_reason
                FROM snaft_violations sv
                LEFT JOIN snaft_rules sr ON sv.rule_id = sr.id
                WHERE 1=1
            """
            params = []

            if did:
                query += " AND sv.did = %s"
                params.append(did)

            query += " ORDER BY sv.timestamp DESC LIMIT %s"
            params.append(limit)

            cursor.execute(query, params)
            violations = cursor.fetchall()

            cursor.close()
            conn.close()

            return [dict(v) for v in violations]

        except Exception as e:
            logger.error(f"Error fetching SNAFT violations: {e}")
            return []


# Singleton instance
_snaft_engine = None

def get_snaft_engine() -> SNAFTEngine:
    """Get singleton SNAFT engine instance"""
    global _snaft_engine
    if _snaft_engine is None:
        _snaft_engine = SNAFTEngine()
    return _snaft_engine
