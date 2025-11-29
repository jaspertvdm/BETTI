"""
BETTI BALANS Engine (Balance/Weighing Layer)
Pre-execution decision-making with warmth and color

BALANS is the "afwegingslaag" - the layer that weighs decisions before execution:
- Resource availability (battery, memory, CPU, network)
- Understanding confidence (clarity check)
- Time estimation (will we meet deadline?)
- LLM cost/benefit analysis
- User preferences vs robot needs
- Internal TIBET requests (robot asking permission)
- Emotional tone (warmth/color) for responses

Examples:
- Kit: "I'd love to upload that, but my battery is at 15%. May I charge for 20 minutes first?"
  (Warmth: apologetic, Color: orange, Decision: request_resources)

- Kit: "I understand you want the lights on, but I'm not sure if you mean 'huiskamer' or 'living'. Which one?"
  (Warmth: neutral, Color: yellow, Decision: clarify)

- Kit: "I can upload that file now (5 minutes) or wait until you're on WiFi (saves 200 tokens)."
  (Warmth: warm, Color: green, Decision: execute_now with alternative)
"""

import logging
import re
import psutil
import time
from typing import Dict, List, Optional, Tuple
from datetime import datetime, timedelta
from dataclasses import dataclass
import psycopg2
from psycopg2.extras import RealDictCursor
import os
from dotenv import load_dotenv

load_dotenv()

logger = logging.getLogger(__name__)

@dataclass
class ResourceStatus:
    """Device resource status"""
    battery_pct: Optional[int] = None
    battery_sufficient: bool = True
    memory_available_mb: int = 0
    memory_sufficient: bool = True
    cpu_load_pct: float = 0.0
    cpu_sufficient: bool = True
    storage_available_mb: int = 0
    storage_sufficient: bool = True
    network_speed_mbps: float = 0.0
    network_sufficient: bool = True

@dataclass
class UnderstandingStatus:
    """Intent understanding status"""
    confidence: float = 0.0  # 0.0-1.0
    clarity_sufficient: bool = True
    ambiguous_terms: List[str] = None
    clarification_question: Optional[str] = None
    clarification_options: Optional[List[str]] = None

@dataclass
class DecisionResult:
    """BALANS decision result"""
    decision: str  # execute_now/delay/clarify/partial/reject/request_resources
    decision_confidence: float  # 0.0-1.0
    reasoning: str
    warmth: str  # cold/neutral/warm/urgent/apologetic/encouraging
    color: str  # green/yellow/orange/red/blue
    estimated_duration_minutes: float
    llm_required: bool
    llm_cost_tokens: int
    robot_request: Optional[str] = None  # Internal TIBET request
    robot_reasoning: Optional[str] = None
    suggested_delay_minutes: Optional[int] = None
    alternative_action: Optional[str] = None


class BALANSEngine:
    """BALANS (Balance/Weighing) decision engine"""

    def __init__(self):
        self.security_db_config = {
            'host': os.getenv('SECURITY_DB_HOST', '192.168.4.76'),
            'port': int(os.getenv('SECURITY_DB_PORT', 5432)),
            'database': os.getenv('SECURITY_DB_NAME', 'jtel_security'),
            'user': os.getenv('SECURITY_DB_USER', 'jtel_security_user'),
            'password': os.getenv('SECURITY_DB_PASSWORD', 'secure_password_here')
        }

        # Decision thresholds (configurable)
        self.min_battery_pct = 20
        self.min_memory_mb = 100
        self.max_cpu_load_pct = 80.0
        self.min_network_mbps = 0.5
        self.min_understanding_confidence = 0.70  # 70%
        self.llm_complexity_threshold = 20  # Use LLM if complexity > 20

    def get_security_conn(self):
        """Get connection to security database"""
        return psycopg2.connect(**self.security_db_config)

    def check_resources(
        self,
        did: str,
        intent: str,
        parameters: Optional[Dict] = None,
        estimated_duration_minutes: float = 1.0
    ) -> ResourceStatus:
        """
        Check device resources (Fail2FlagBE4Intent)

        Returns ResourceStatus with all resource checks
        """
        status = ResourceStatus()

        try:
            # Battery check (if available - for mobile devices/robots)
            battery = self._get_battery_status(did)
            if battery is not None:
                status.battery_pct = battery
                # Check if battery sufficient for estimated duration
                # Assume 1% battery = 10 minutes of operation
                required_battery = max(self.min_battery_pct, int(estimated_duration_minutes / 10))
                status.battery_sufficient = battery >= required_battery

            # Memory check
            mem = psutil.virtual_memory()
            status.memory_available_mb = mem.available // (1024 * 1024)
            status.memory_sufficient = status.memory_available_mb >= self.min_memory_mb

            # CPU check
            status.cpu_load_pct = psutil.cpu_percent(interval=0.1)
            status.cpu_sufficient = status.cpu_load_pct < self.max_cpu_load_pct

            # Storage check
            disk = psutil.disk_usage('/')
            status.storage_available_mb = disk.free // (1024 * 1024)
            # Require at least 500MB free
            status.storage_sufficient = status.storage_available_mb >= 500

            # Network check
            network_speed = self._estimate_network_speed(did)
            status.network_speed_mbps = network_speed
            status.network_sufficient = network_speed >= self.min_network_mbps

        except Exception as e:
            logger.error(f"Resource check error: {e}")
            # If checks fail, assume resources are insufficient (fail-safe)
            status.battery_sufficient = False
            status.memory_sufficient = False
            status.cpu_sufficient = False

        return status

    def check_understanding(
        self,
        intent: str,
        parameters: Optional[Dict] = None,
        context: Optional[str] = None
    ) -> UnderstandingStatus:
        """
        Check understanding confidence and clarity

        Returns UnderstandingStatus with confidence score and clarification needs
        """
        status = UnderstandingStatus()
        status.ambiguous_terms = []

        try:
            # Calculate understanding confidence
            confidence_score = 1.0  # Start optimistic

            # Check for ambiguous terms (Dutch/English mix, synonyms)
            ambiguous_pairs = [
                (['living', 'woonkamer', 'huiskamer'], 'living room'),
                (['keuken', 'kitchen'], 'kitchen'),
                (['slaapkamer', 'bedroom'], 'bedroom'),
                (['licht', 'light', 'lamp'], 'lights'),
                (['aan', 'on', 'aanzetten'], 'turn on'),
                (['uit', 'off', 'uitzetten'], 'turn off'),
            ]

            intent_lower = intent.lower()
            for synonyms, canonical in ambiguous_pairs:
                matches = [syn for syn in synonyms if syn in intent_lower]
                if len(matches) > 1:
                    # Multiple synonyms detected - ambiguous
                    status.ambiguous_terms.append(canonical)
                    confidence_score -= 0.2

            # Check for vague terms
            vague_terms = ['dat', 'die', 'het', 'daar', 'this', 'that', 'it']
            vague_count = sum(1 for term in vague_terms if term in intent_lower.split())
            if vague_count > 0:
                confidence_score -= (0.1 * vague_count)
                status.ambiguous_terms.append('vague_reference')

            # Check for missing required parameters
            if self._requires_location(intent) and not self._has_location(parameters):
                confidence_score -= 0.3
                status.ambiguous_terms.append('missing_location')

            if self._requires_device(intent) and not self._has_device(parameters):
                confidence_score -= 0.3
                status.ambiguous_terms.append('missing_device')

            # Clamp confidence to [0.0, 1.0]
            status.confidence = max(0.0, min(1.0, confidence_score))
            status.clarity_sufficient = status.confidence >= self.min_understanding_confidence

            # Generate clarification question if needed
            if not status.clarity_sufficient and status.ambiguous_terms:
                status.clarification_question, status.clarification_options = \
                    self._generate_clarification(intent, status.ambiguous_terms)

        except Exception as e:
            logger.error(f"Understanding check error: {e}")
            status.confidence = 0.5  # Neutral confidence on error
            status.clarity_sufficient = False

        return status

    def make_decision(
        self,
        did: str,
        hid: str,
        intent: str,
        parameters: Optional[Dict] = None,
        complexity_score: float = 0.0,
        user_urgency: int = 5,  # 1-10
        deadline: Optional[datetime] = None
    ) -> DecisionResult:
        """
        Make BALANS decision with weighted scoring

        Args:
            did: Device ID
            hid: Human ID
            intent: Intent to execute
            parameters: Intent parameters
            complexity_score: BETTI complexity score
            user_urgency: User urgency (1-10)
            deadline: Optional deadline for completion

        Returns:
            DecisionResult with decision, reasoning, warmth/color
        """
        # Step 1: Check resources (Fail2FlagBE4Intent)
        resources = self.check_resources(did, intent)

        # Step 2: Check understanding
        understanding = self.check_understanding(intent, parameters)

        # Step 3: Estimate duration and LLM needs
        estimated_duration = self._estimate_duration(intent, complexity_score)
        llm_required = complexity_score > self.llm_complexity_threshold
        llm_cost = self._estimate_llm_cost(complexity_score) if llm_required else 0

        # Step 4: Calculate decision scores
        scores = self._calculate_decision_scores(
            resources=resources,
            understanding=understanding,
            user_urgency=user_urgency,
            robot_urgency=self._calculate_robot_urgency(resources),
            complexity_score=complexity_score,
            deadline=deadline,
            estimated_duration=estimated_duration
        )

        # Step 5: Choose highest-scoring decision
        decision_type = max(scores, key=scores.get)
        decision_confidence = scores[decision_type]

        # Step 6: Generate reasoning and warmth/color
        reasoning, warmth, color = self._generate_reasoning(
            decision_type=decision_type,
            resources=resources,
            understanding=understanding,
            user_urgency=user_urgency,
            complexity_score=complexity_score,
            deadline=deadline
        )

        # Step 7: Generate robot request if needed
        robot_request, robot_reasoning = self._generate_robot_request(
            decision_type=decision_type,
            resources=resources,
            estimated_duration=estimated_duration
        )

        # Step 8: Log decision to database
        decision_result = DecisionResult(
            decision=decision_type,
            decision_confidence=decision_confidence,
            reasoning=reasoning,
            warmth=warmth,
            color=color,
            estimated_duration_minutes=estimated_duration,
            llm_required=llm_required,
            llm_cost_tokens=llm_cost,
            robot_request=robot_request,
            robot_reasoning=robot_reasoning
        )

        self._log_balans_decision(
            did=did,
            hid=hid,
            intent=intent,
            parameters=parameters,
            resources=resources,
            understanding=understanding,
            decision_result=decision_result,
            scores=scores,
            user_urgency=user_urgency,
            complexity_score=complexity_score
        )

        return decision_result

    def _calculate_decision_scores(
        self,
        resources: ResourceStatus,
        understanding: UnderstandingStatus,
        user_urgency: int,
        robot_urgency: int,
        complexity_score: float,
        deadline: Optional[datetime],
        estimated_duration: float
    ) -> Dict[str, float]:
        """
        Calculate weighted scores for each decision option

        Returns dict: {decision_type: confidence_score}
        """
        scores = {
            'execute_now': 1.0,
            'delay': 0.0,
            'clarify': 0.0,
            'partial': 0.0,
            'reject': 0.0,
            'request_resources': 0.0
        }

        # EXECUTE_NOW scoring
        if resources.battery_sufficient:
            scores['execute_now'] += 0.2
        else:
            scores['execute_now'] -= 0.4

        if resources.memory_sufficient:
            scores['execute_now'] += 0.1
        else:
            scores['execute_now'] -= 0.3

        if resources.cpu_sufficient:
            scores['execute_now'] += 0.1
        else:
            scores['execute_now'] -= 0.2

        if understanding.clarity_sufficient:
            scores['execute_now'] += 0.3
        else:
            scores['execute_now'] -= 0.5

        scores['execute_now'] += (user_urgency / 100.0)  # Max +0.1

        # DELAY scoring
        if deadline:
            time_until_deadline = (deadline - datetime.now()).total_seconds() / 60
            if time_until_deadline > estimated_duration * 2:
                scores['delay'] += 0.5
            else:
                scores['delay'] -= 0.3

        if not resources.network_sufficient:
            scores['delay'] += 0.3  # Wait for better network

        if robot_urgency < 5:
            scores['delay'] += 0.2  # Robot not urgent

        # CLARIFY scoring
        if not understanding.clarity_sufficient:
            scores['clarify'] += 0.8  # Strong preference for clarification
            scores['clarify'] += (1.0 - understanding.confidence)

        # REQUEST_RESOURCES scoring
        if not resources.battery_sufficient:
            scores['request_resources'] += 0.6
        if not resources.memory_sufficient:
            scores['request_resources'] += 0.3
        if robot_urgency > 7:
            scores['request_resources'] += 0.2

        # PARTIAL scoring (for complex tasks that can be split)
        if complexity_score > 50:
            scores['partial'] += 0.4
        if not resources.battery_sufficient and complexity_score > 20:
            scores['partial'] += 0.3

        # REJECT scoring (last resort)
        if not resources.battery_sufficient and not resources.memory_sufficient:
            scores['reject'] += 0.3
        if understanding.confidence < 0.3:
            scores['reject'] += 0.4

        # Normalize scores to [0.0, 1.0]
        for key in scores:
            scores[key] = max(0.0, min(1.0, scores[key]))

        return scores

    def _generate_reasoning(
        self,
        decision_type: str,
        resources: ResourceStatus,
        understanding: UnderstandingStatus,
        user_urgency: int,
        complexity_score: float,
        deadline: Optional[datetime]
    ) -> Tuple[str, str, str]:
        """
        Generate human-readable reasoning with warmth and color

        Returns: (reasoning, warmth, color)
        """
        reasoning = ""
        warmth = "neutral"
        color = "green"

        if decision_type == 'execute_now':
            reasoning = "All systems ready. Executing now."
            warmth = "warm"
            color = "green"

        elif decision_type == 'delay':
            if not resources.network_sufficient:
                reasoning = "Network speed is low. I'll wait for better connectivity to save time and tokens."
                warmth = "neutral"
                color = "yellow"
            else:
                reasoning = "No rush detected. I'll optimize timing for best results."
                warmth = "neutral"
                color = "green"

        elif decision_type == 'clarify':
            reasoning = f"I'm not entirely sure what you mean (confidence: {understanding.confidence:.0%}). "
            if understanding.clarification_question:
                reasoning += understanding.clarification_question
            else:
                reasoning += "Could you clarify?"
            warmth = "apologetic"
            color = "yellow"

        elif decision_type == 'request_resources':
            if not resources.battery_sufficient:
                reasoning = f"Battery at {resources.battery_pct}%. May I charge first? (Estimated: 20 minutes)"
                warmth = "apologetic"
                color = "orange"
            elif not resources.memory_sufficient:
                reasoning = f"Memory low ({resources.memory_available_mb}MB free). I need to clear cache first."
                warmth = "neutral"
                color = "orange"
            else:
                reasoning = "I need additional resources to complete this safely."
                warmth = "neutral"
                color = "orange"

        elif decision_type == 'partial':
            reasoning = f"This is complex (score: {complexity_score:.1f}). I can start now and continue later, or split into smaller tasks."
            warmth = "warm"
            color = "blue"

        elif decision_type == 'reject':
            reasoning = "I cannot safely execute this right now. "
            if not resources.battery_sufficient:
                reasoning += "Battery critically low. "
            if not understanding.clarity_sufficient:
                reasoning += "Intent unclear. "
            warmth = "apologetic"
            color = "red"

        return reasoning, warmth, color

    def _generate_robot_request(
        self,
        decision_type: str,
        resources: ResourceStatus,
        estimated_duration: float
    ) -> Tuple[Optional[str], Optional[str]]:
        """
        Generate Internal TIBET request (robot asking permission)

        Returns: (request_message, reasoning)
        """
        if decision_type == 'request_resources':
            if not resources.battery_sufficient:
                return (
                    f"May I charge for {int(estimated_duration * 2)} minutes before starting?",
                    f"Battery at {resources.battery_pct}%, need {int(estimated_duration * 10)}% for safe completion"
                )
            elif not resources.memory_sufficient:
                return (
                    "May I clear cache and optimize memory first? (2 minutes)",
                    f"Only {resources.memory_available_mb}MB available, need {self.min_memory_mb}MB"
                )

        return None, None

    def _calculate_robot_urgency(self, resources: ResourceStatus) -> int:
        """
        Calculate robot's internal urgency (1-10)

        Robot urgency is HIGH when resources are critically low
        """
        urgency = 5  # Neutral

        if resources.battery_pct is not None:
            if resources.battery_pct < 10:
                urgency = 10  # Critical!
            elif resources.battery_pct < 20:
                urgency = 8
            elif resources.battery_pct < 30:
                urgency = 6

        if not resources.memory_sufficient:
            urgency = max(urgency, 7)

        if not resources.cpu_sufficient:
            urgency = max(urgency, 6)

        return urgency

    def _estimate_duration(self, intent: str, complexity_score: float) -> float:
        """Estimate duration in minutes based on complexity"""
        # Simple heuristic: duration = complexity / 10
        # Clamped to [0.5, 30] minutes
        return max(0.5, min(30.0, complexity_score / 10))

    def _estimate_llm_cost(self, complexity_score: float) -> int:
        """Estimate LLM token cost based on complexity"""
        # Simple heuristic: tokens = complexity * 100
        return int(complexity_score * 100)

    def _get_battery_status(self, did: str) -> Optional[int]:
        """Get battery percentage (if available)"""
        try:
            battery = psutil.sensors_battery()
            if battery:
                return int(battery.percent)
        except:
            pass

        # TODO: Query device-specific battery API for robots/drones
        return None

    def _estimate_network_speed(self, did: str) -> float:
        """Estimate network speed in Mbps"""
        # TODO: Implement actual network speed test
        # For now, assume 10 Mbps (decent)
        return 10.0

    def _requires_location(self, intent: str) -> bool:
        """Check if intent requires location parameter"""
        location_keywords = ['lights', 'licht', 'lampen', 'temperature', 'temperatuur']
        return any(kw in intent.lower() for kw in location_keywords)

    def _has_location(self, parameters: Optional[Dict]) -> bool:
        """Check if parameters include location"""
        if not parameters:
            return False
        return 'location' in parameters or 'room' in parameters or 'kamer' in parameters

    def _requires_device(self, intent: str) -> bool:
        """Check if intent requires device parameter"""
        device_keywords = ['call', 'bel', 'message', 'stuur']
        return any(kw in intent.lower() for kw in device_keywords)

    def _has_device(self, parameters: Optional[Dict]) -> bool:
        """Check if parameters include device"""
        if not parameters:
            return False
        return 'device' in parameters or 'did' in parameters

    def _generate_clarification(
        self,
        intent: str,
        ambiguous_terms: List[str]
    ) -> Tuple[str, List[str]]:
        """Generate clarification question and options"""

        if 'living room' in ambiguous_terms:
            return (
                "Did you mean 'huiskamer' or 'living room' (UK English)?",
                ['huiskamer_lights', 'living_lights']
            )

        if 'missing_location' in ambiguous_terms:
            return (
                "Which room do you mean?",
                ['huiskamer', 'keuken', 'slaapkamer', 'badkamer']
            )

        if 'missing_device' in ambiguous_terms:
            return (
                "Which device should I use?",
                ['phone', 'tablet', 'computer']
            )

        return (
            "I'm not sure I understood correctly. Could you rephrase?",
            []
        )

    def _log_balans_decision(
        self,
        did: str,
        hid: str,
        intent: str,
        parameters: Optional[Dict],
        resources: ResourceStatus,
        understanding: UnderstandingStatus,
        decision_result: DecisionResult,
        scores: Dict[str, float],
        user_urgency: int,
        complexity_score: float
    ):
        """Log BALANS decision to security database"""

        try:
            conn = self.get_security_conn()
            cursor = conn.cursor()

            # Log pre-execution flags
            cursor.execute("""
                INSERT INTO pre_execution_flags
                (did, intent, parameters, battery_pct, battery_sufficient,
                 memory_available_mb, memory_sufficient, cpu_load_pct,
                 network_speed_mbps, understanding_confidence, clarity_sufficient,
                 clarification_needed, estimated_duration_minutes, llm_required,
                 llm_cost_tokens, complexity_score, pre_check_passed,
                 flags_raised, timestamp)
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, NOW())
            """, (
                did, intent,
                psycopg2.extras.Json(parameters) if parameters else None,
                resources.battery_pct,
                resources.battery_sufficient,
                resources.memory_available_mb,
                resources.memory_sufficient,
                resources.cpu_load_pct,
                resources.network_speed_mbps,
                understanding.confidence,
                understanding.clarity_sufficient,
                understanding.clarification_question,
                decision_result.estimated_duration_minutes,
                decision_result.llm_required,
                decision_result.llm_cost_tokens,
                complexity_score,
                decision_result.decision == 'execute_now',
                psycopg2.extras.Json([
                    f for f in ['battery', 'memory', 'cpu', 'network', 'clarity']
                    if not getattr(resources, f'{f}_sufficient', True) or
                       (f == 'clarity' and not understanding.clarity_sufficient)
                ])
            ))

            # Log BALANS decision
            robot_urgency = self._calculate_robot_urgency(resources)

            cursor.execute("""
                INSERT INTO balans_decisions
                (did, hid, intent, parameters, user_urgency, robot_urgency,
                 system_health_score, execute_now_score, delay_score, clarify_score,
                 partial_score, reject_score, request_resources_score, decision,
                 decision_confidence, decision_reasoning, response_warmth,
                 response_color, robot_internal_tibet_request, robot_reasoning,
                 timestamp)
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, NOW())
            """, (
                did, hid, intent,
                psycopg2.extras.Json(parameters) if parameters else None,
                user_urgency, robot_urgency,
                self._calculate_system_health(resources),
                scores.get('execute_now', 0.0),
                scores.get('delay', 0.0),
                scores.get('clarify', 0.0),
                scores.get('partial', 0.0),
                scores.get('reject', 0.0),
                scores.get('request_resources', 0.0),
                decision_result.decision,
                decision_result.decision_confidence,
                decision_result.reasoning,
                decision_result.warmth,
                decision_result.color,
                decision_result.robot_request,
                decision_result.robot_reasoning
            ))

            conn.commit()
            cursor.close()
            conn.close()

        except Exception as e:
            logger.error(f"Error logging BALANS decision: {e}")

    def _calculate_system_health(self, resources: ResourceStatus) -> int:
        """Calculate overall system health score (0-100)"""
        health = 100

        if resources.battery_pct is not None:
            health = min(health, resources.battery_pct)

        if not resources.memory_sufficient:
            health -= 20

        if not resources.cpu_sufficient:
            health -= 15

        if not resources.network_sufficient:
            health -= 10

        return max(0, health)


# Singleton instance
_balans_engine = None

def get_balans_engine() -> BALANSEngine:
    """Get singleton BALANS engine instance"""
    global _balans_engine
    if _balans_engine is None:
        _balans_engine = BALANSEngine()
    return _balans_engine
