"""
BETTI Complexity Calculator

Implements topological complexity measurement for autonomous tasks.
Based on Betti numbers from algebraic topology, adapted for semantic autonomy.

B0 (humans)   = number of unique human actors (HIDs)
B1 (devices)  = number of unique devices (DIDs)
B2 (ops)      = number of unique operations/subsystems
B3 (tbet)     = number of micro-steps (depth of autonomy)
B4 (time)     = estimated execution time in minutes
B5 (channels) = number of available routing/communication channels

Complexity Score = α*B0 + β*B1 + γ*B2 + δ*B3 + ε*B4 - ζ*B5

Where: α > β > γ > δ > ε (humans are heaviest factor)
       ζ is NEGATIVE (more channels = LOWER complexity = safer)

Author: Jasper van der Meent
Implementation: Claude (Sonnet 4.5)
Date: November 2025
"""

from typing import Dict, List, Any, Tuple, Optional
from dataclasses import dataclass
import psycopg2
from psycopg2.extras import RealDictCursor, Json
from datetime import datetime


@dataclass
class ComplexityMetrics:
    """BETTI complexity metrics"""
    b0_humans: int = 0
    b1_devices: int = 0
    b2_ops: int = 0
    b3_tbet_steps: int = 0
    b4_time_minutes: float = 0.0
    b5_channels: int = 0
    complexity_score: float = 0.0
    split_required: bool = False
    threshold_profile: str = "default"


@dataclass
class ComplexityThreshold:
    """Complexity thresholds configuration"""
    name: str
    b0_max: int
    b1_max: int
    b2_max: int
    b3_max: int
    b4_max: float
    b5_min: int
    complexity_max: float
    alpha: float    # Weight for humans
    beta: float     # Weight for devices
    gamma: float    # Weight for operations
    delta: float    # Weight for TBET steps
    epsilon: float  # Weight for time
    zeta: float     # Weight for channels (NEGATIVE - reduces complexity)


def get_threshold_profile(conn, profile_name: str = "default") -> ComplexityThreshold:
    """Get complexity threshold configuration"""
    cur = conn.cursor(cursor_factory=RealDictCursor)

    cur.execute("""
        SELECT * FROM complexity_thresholds WHERE name = %s
    """, (profile_name,))

    row = cur.fetchone()
    cur.close()

    if not row:
        # Return default hardcoded
        return ComplexityThreshold(
            name="default",
            b0_max=2, b1_max=4, b2_max=5, b3_max=10, b4_max=10.0, b5_min=1,
            complexity_max=50.0,
            alpha=3.0, beta=2.0, gamma=1.5, delta=1.0, epsilon=0.5, zeta=1.0
        )

    return ComplexityThreshold(
        name=row["name"],
        b0_max=row["b0_max"],
        b1_max=row["b1_max"],
        b2_max=row["b2_max"],
        b3_max=row["b3_max"],
        b4_max=row.get("b4_max", 10.0),
        b5_min=row.get("b5_min", 1),
        complexity_max=row["complexity_max"],
        alpha=row["alpha"],
        beta=row["beta"],
        gamma=row["gamma"],
        delta=row["delta"],
        epsilon=row.get("epsilon", 0.5),
        zeta=row.get("zeta", 1.0)
    )


def calculate_complexity(
    context: Dict[str, Any],
    intent: str,
    threshold_profile: str = "default",
    conn = None
) -> ComplexityMetrics:
    """
    Calculate BETTI complexity metrics for a task.

    Args:
        context: Intent context containing HIDs, DIDs, operations, etc.
        intent: The intent being executed
        threshold_profile: Which threshold profile to use
        conn: Database connection (optional, for threshold lookup)

    Returns:
        ComplexityMetrics with calculated values
    """

    # Get thresholds
    if conn:
        thresholds = get_threshold_profile(conn, threshold_profile)
    else:
        thresholds = get_threshold_profile(None, threshold_profile)

    # Extract unique actors from context
    b0_humans = len(set(extract_hids(context)))

    # Extract unique devices
    b1_devices = len(set(extract_dids(context)))

    # Extract unique operations/subsystems
    b2_ops = len(set(extract_operations(context, intent)))

    # Extract TBET steps (if provided in context)
    b3_tbet_steps = context.get("tbet_steps", 0)
    if not b3_tbet_steps:
        # Estimate based on complexity if not provided
        b3_tbet_steps = estimate_tbet_steps(context, intent)

    # Extract/estimate time dimension (B4)
    b4_time_minutes = context.get("estimated_duration_minutes", 0.0)
    if not b4_time_minutes:
        # Estimate based on task complexity
        b4_time_minutes = estimate_time_minutes(context, intent, b0_humans, b1_devices, b2_ops, b3_tbet_steps)

    # Extract routing channels (B5)
    b5_channels = len(set(extract_channels(context, intent)))
    if b5_channels == 0:
        # Default to at least 1 channel if none detected
        b5_channels = 1

    # Calculate complexity score with B5 (channels) - NEGATIVE contribution
    complexity_score = (
        thresholds.alpha * b0_humans +
        thresholds.beta * b1_devices +
        thresholds.gamma * b2_ops +
        thresholds.delta * b3_tbet_steps +
        thresholds.epsilon * b4_time_minutes -
        thresholds.zeta * b5_channels  # SUBTRACT channels (more = safer)
    )

    # Determine if split is required
    split_required = (
        b0_humans > thresholds.b0_max or
        b1_devices > thresholds.b1_max or
        b2_ops > thresholds.b2_max or
        b3_tbet_steps > thresholds.b3_max or
        b4_time_minutes > thresholds.b4_max or
        b5_channels < thresholds.b5_min or  # Too FEW channels = risky!
        complexity_score > thresholds.complexity_max
    )

    return ComplexityMetrics(
        b0_humans=b0_humans,
        b1_devices=b1_devices,
        b2_ops=b2_ops,
        b3_tbet_steps=b3_tbet_steps,
        b4_time_minutes=round(b4_time_minutes, 2),
        b5_channels=b5_channels,
        complexity_score=round(complexity_score, 2),
        split_required=split_required,
        threshold_profile=threshold_profile
    )


def extract_hids(context: Dict[str, Any]) -> List[str]:
    """Extract unique human identifiers from context"""
    hids = []

    # Direct HIDs
    if "hid" in context:
        hids.append(context["hid"])
    if "hids" in context:
        hids.extend(context["hids"])

    # Participants
    if "participants" in context:
        hids.extend(context["participants"])

    # User ID
    if "user_id" in context:
        hids.append(context["user_id"])

    # Caller/callee
    if "caller" in context:
        hids.append(context["caller"])
    if "callee" in context:
        hids.append(context["callee"])

    return [h for h in hids if h]  # Filter None/empty


def extract_dids(context: Dict[str, Any]) -> List[str]:
    """Extract unique device identifiers from context"""
    dids = []

    # Direct DIDs
    if "did" in context:
        dids.append(context["did"])
    if "dids" in context:
        dids.extend(context["dids"])

    # Devices
    if "devices" in context:
        if isinstance(context["devices"], list):
            dids.extend(context["devices"])
        elif isinstance(context["devices"], dict):
            dids.extend(context["devices"].keys())

    # Device ID
    if "device_id" in context:
        dids.append(context["device_id"])

    # Target device
    if "target_device" in context:
        dids.append(context["target_device"])

    return [d for d in dids if d]


def extract_operations(context: Dict[str, Any], intent: str) -> List[str]:
    """Extract unique operations/subsystems from context and intent"""
    ops = [intent]  # Intent itself is an operation

    # Explicit operations
    if "operations" in context:
        ops.extend(context["operations"])

    # Actions
    if "actions" in context:
        if isinstance(context["actions"], list):
            ops.extend(context["actions"])
        elif isinstance(context["actions"], dict):
            ops.extend(context["actions"].keys())

    # Subsystems
    if "subsystems" in context:
        ops.extend(context["subsystems"])

    # Required capabilities
    if "required_capabilities" in context:
        ops.extend(context["required_capabilities"])

    # Infer from intent type
    ops.extend(infer_operations_from_intent(intent, context))

    return list(set([o for o in ops if o]))  # Unique, non-empty


def infer_operations_from_intent(intent: str, context: Dict[str, Any]) -> List[str]:
    """Infer operations based on intent type"""
    ops = []

    # Meeting intents
    if "meeting" in intent or "schedule" in intent:
        ops.extend(["calendar", "notification"])
        if context.get("participants"):
            ops.append("multi_user_coordination")

    # Call intents
    if "call" in intent:
        ops.extend(["voip", "signaling"])
        if context.get("video"):
            ops.append("video_processing")

    # Message intents
    if "message" in intent or "send" in intent:
        ops.append("messaging")
        if context.get("encryption"):
            ops.append("encryption")

    # Smart home intents
    if any(word in intent for word in ["lights", "thermostat", "lock", "camera"]):
        ops.append("smart_home")
        ops.append("iot_control")

    # Navigation intents
    if "navigate" in intent or "route" in intent:
        ops.extend(["navigation", "mapping"])

    return ops


def extract_channels(context: Dict[str, Any], intent: str) -> List[str]:
    """
    Extract available communication/routing channels from context

    Master Routing Channels:
    - webrtc: Real-time communication (video/audio/data)
    - cellular: Mobile network (calls/SMS)
    - wifi: WiFi network
    - ethernet: Wired network
    - bluetooth: Short-range wireless
    - lora: Long-range low-power (IoT)
    - websocket: Persistent connection
    - http: REST API fallback
    - push: Push notifications
    - sms: SMS fallback
    - email: Email fallback (last resort)
    - emergency: Emergency broadcast channel

    More channels = safer (fallback options)
    B5 has NEGATIVE weight in complexity (reduces risk)
    """
    channels = set()

    # Explicit channels from context
    if "channels" in context:
        if isinstance(context["channels"], list):
            channels.update(context["channels"])
        elif isinstance(context["channels"], str):
            channels.add(context["channels"])

    # Infer from devices
    if "devices" in context or "dids" in context:
        devices = context.get("devices", []) + context.get("dids", [])
        for device in devices:
            device_lower = str(device).lower()

            # Mobile phone = multiple channels
            if any(word in device_lower for word in ["phone", "mobile", "smartphone"]):
                channels.update(["cellular", "wifi", "bluetooth", "push", "sms"])

            # Tablet
            elif "tablet" in device_lower:
                channels.update(["wifi", "bluetooth", "push"])

            # Laptop/Desktop
            elif any(word in device_lower for word in ["laptop", "desktop", "computer", "pc"]):
                channels.update(["wifi", "ethernet", "bluetooth"])

            # Robot
            elif "robot" in device_lower:
                channels.update(["wifi", "bluetooth", "lora"])

            # IoT device
            elif any(word in device_lower for word in ["iot", "sensor", "smart", "camera"]):
                channels.update(["wifi", "lora", "bluetooth"])

            # Car (autonomous vehicle)
            elif any(word in device_lower for word in ["car", "vehicle", "auto"]):
                channels.update(["cellular", "wifi", "bluetooth", "lora"])

            # Drone
            elif "drone" in device_lower:
                channels.update(["cellular", "wifi", "lora", "emergency"])

    # Infer from intent type
    intent_lower = intent.lower()

    # Call intents = real-time channels
    if "call" in intent_lower:
        channels.update(["webrtc", "cellular"])
        if context.get("video"):
            channels.add("webrtc")

    # Message intents = async channels
    if "message" in intent_lower or "send" in intent_lower:
        channels.update(["websocket", "push", "sms", "email"])

    # Navigation/routing intents
    if "navigate" in intent_lower or "route" in intent_lower:
        channels.update(["cellular", "wifi"])  # GPS needs data connection

    # Emergency intents = all channels including emergency
    if context.get("emergency") or "emergency" in intent_lower or "urgent" in intent_lower:
        channels.update(["emergency", "sms", "cellular", "push"])

    # Smart home = local + cloud channels
    if any(word in intent_lower for word in ["lights", "thermostat", "lock", "camera"]):
        channels.update(["wifi", "bluetooth", "websocket"])

    # Infer from network context
    if "network" in context:
        network = context["network"]
        if isinstance(network, str):
            channels.add(network)
        elif isinstance(network, dict):
            if network.get("type"):
                channels.add(network["type"])
            if network.get("fallbacks"):
                channels.update(network["fallbacks"])

    # Always have HTTP as ultimate fallback (if any network available)
    if any(ch in channels for ch in ["wifi", "ethernet", "cellular"]):
        channels.add("http")

    # Return unique channels as list
    return list(channels)


def estimate_tbet_steps(context: Dict[str, Any], intent: str) -> int:
    """Estimate TBET steps based on complexity if not provided"""
    # Simple heuristic: more complex = more steps

    steps = 1  # Base step

    # Add steps for each device
    steps += len(extract_dids(context))

    # Add steps for each operation
    steps += len(extract_operations(context, intent))

    # Add steps for multi-user
    if len(extract_hids(context)) > 1:
        steps += 2

    # Add steps for conditional logic
    if "conditions" in context or "if" in context:
        steps += 3

    # Add steps for loops/iterations
    if "iterate" in context or "repeat" in context:
        steps += context.get("iterations", 5)

    return min(steps, 20)  # Cap at 20


def estimate_time_minutes(
    context: Dict[str, Any],
    intent: str,
    b0_humans: int,
    b1_devices: int,
    b2_ops: int,
    b3_tbet_steps: int
) -> float:
    """
    Estimate execution time in minutes based on task complexity

    Time estimation formula:
    - Base time per TBET step: 0.5 minutes
    - +1 minute per human (coordination overhead)
    - +0.5 minutes per device (I/O latency)
    - +0.3 minutes per operation (processing time)
    - Additional time from context (e.g., explicit wait times)
    """

    # Base time: ~30 seconds per TBET step
    base_time = b3_tbet_steps * 0.5

    # Human coordination overhead (meeting time, approvals, etc.)
    human_time = b0_humans * 1.0

    # Device I/O latency (network requests, state changes)
    device_time = b1_devices * 0.5

    # Operation processing time
    operation_time = b2_ops * 0.3

    # Explicit wait/delay times from context
    wait_time = 0.0
    if "wait_seconds" in context:
        wait_time = context["wait_seconds"] / 60.0
    if "delay_minutes" in context:
        wait_time += context["delay_minutes"]

    # Intent-specific adjustments
    intent_multiplier = 1.0

    # Long-running intents
    if "backup" in intent or "scan" in intent or "download" in intent:
        intent_multiplier = 3.0

    # Quick intents
    elif "read" in intent or "get" in intent or "check" in intent:
        intent_multiplier = 0.5

    # File operations
    elif "upload" in intent or "process" in intent or "analyze" in intent:
        intent_multiplier = 2.0
        # Add time based on file size
        if "file_size_mb" in context:
            # ~1 minute per 100MB (adjust for your network/CPU)
            wait_time += context["file_size_mb"] / 100.0

    # Total estimated time
    total_time = (base_time + human_time + device_time + operation_time + wait_time) * intent_multiplier

    # Apply limits
    total_time = max(0.1, total_time)  # Minimum 6 seconds
    total_time = min(total_time, 120.0)  # Cap at 2 hours (longer tasks should be split)

    return round(total_time, 2)


def suggest_split(metrics: ComplexityMetrics, context: Dict[str, Any], intent: str) -> List[Dict[str, Any]]:
    """
    Suggest how to split a complex task into sub-BETTIs.

    Returns list of sub-task contexts.
    """
    if not metrics.split_required:
        return []

    sub_tasks = []

    # Strategy 1: Split by operations
    if metrics.b2_ops > 5:
        ops = extract_operations(context, intent)
        for op in ops:
            sub_context = context.copy()
            sub_context["operations"] = [op]
            sub_context["parent_intent"] = intent
            sub_tasks.append({
                "intent": f"{intent}_step_{op}",
                "context": sub_context,
                "reason": f"Split by operation: {op}"
            })

    # Strategy 2: Split by devices
    elif metrics.b1_devices > 3:
        dids = extract_dids(context)
        for did in dids:
            sub_context = context.copy()
            sub_context["target_device"] = did
            sub_context["parent_intent"] = intent
            sub_tasks.append({
                "intent": f"{intent}_device_{did}",
                "context": sub_context,
                "reason": f"Split by device: {did}"
            })

    # Strategy 3: Split by participants (careful with multi-human)
    elif metrics.b0_humans > 2:
        hids = extract_hids(context)
        for hid in hids:
            sub_context = context.copy()
            sub_context["participants"] = [hid]
            sub_context["parent_intent"] = intent
            sub_tasks.append({
                "intent": f"{intent}_user_{hid}",
                "context": sub_context,
                "reason": f"Split by participant: {hid}"
            })

    # Strategy 4: Split by TBET phases
    else:
        phases = ["prepare", "execute", "verify", "complete"]
        for phase in phases:
            sub_context = context.copy()
            sub_context["phase"] = phase
            sub_context["parent_intent"] = intent
            sub_tasks.append({
                "intent": f"{intent}_{phase}",
                "context": sub_context,
                "reason": f"Split by phase: {phase}"
            })

    return sub_tasks[:5]  # Max 5 sub-tasks


def log_complexity(
    intent_log_id: int,
    metrics: ComplexityMetrics,
    conn
):
    """Log complexity metrics to database"""
    cur = conn.cursor()

    # Update intent log with metrics
    cur.execute("""
        UPDATE betti_intent_log
        SET b0_humans = %s,
            b1_devices = %s,
            b2_ops = %s,
            b3_tbet_steps = %s,
            complexity_score = %s,
            split_required = %s
        WHERE id = %s
    """, (
        metrics.b0_humans,
        metrics.b1_devices,
        metrics.b2_ops,
        metrics.b3_tbet_steps,
        metrics.complexity_score,
        metrics.split_required,
        intent_log_id
    ))

    # Log to history
    cur.execute("""
        INSERT INTO complexity_history (
            intent_log_id, b0_humans, b1_devices, b2_ops, b3_tbet_steps,
            complexity_score, threshold_profile, was_split
        ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
    """, (
        intent_log_id,
        metrics.b0_humans,
        metrics.b1_devices,
        metrics.b2_ops,
        metrics.b3_tbet_steps,
        metrics.complexity_score,
        metrics.threshold_profile,
        metrics.split_required
    ))

    conn.commit()
    cur.close()


# Example usage
if __name__ == "__main__":
    # Test case 1: Simple task
    simple_context = {
        "user_id": "jasper",
        "device_id": "phone_001",
        "action": "turn_on_lights"
    }

    metrics = calculate_complexity(simple_context, "turn_on_lights")
    print(f"Simple task complexity: {metrics.complexity_score}")
    print(f"B0={metrics.b0_humans}, B1={metrics.b1_devices}, B2={metrics.b2_ops}, B3={metrics.b3_tbet_steps}")
    print(f"Split required: {metrics.split_required}\n")

    # Test case 2: Complex multi-user multi-device task
    complex_context = {
        "participants": ["jasper", "maria", "tim"],
        "devices": ["phone_001", "phone_002", "laptop_001", "tablet_001", "smart_home_hub"],
        "operations": ["schedule_meeting", "send_invites", "book_room", "setup_video", "notify_all"],
        "tbet_steps": 15
    }

    metrics = calculate_complexity(complex_context, "coordinate_team_meeting")
    print(f"Complex task complexity: {metrics.complexity_score}")
    print(f"B0={metrics.b0_humans}, B1={metrics.b1_devices}, B2={metrics.b2_ops}, B3={metrics.b3_tbet_steps}")
    print(f"Split required: {metrics.split_required}")

    if metrics.split_required:
        splits = suggest_split(metrics, complex_context, "coordinate_team_meeting")
        print(f"\nSuggested splits ({len(splits)}):")
        for i, split in enumerate(splits, 1):
            print(f"{i}. {split['intent']} - {split['reason']}")
