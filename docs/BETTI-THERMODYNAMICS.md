# BETTI Thermodynamics Framework

**Second Law of Thermodynamics for Relationship Entropy & Irreversibility Detection**

## The Second Law of Thermodynamics

```
ΔS ≥ 0  (for isolated systems)

Entropy always increases or stays constant
Irreversible processes increase entropy
```

**Meaning**: Systems naturally move toward disorder. Reversing this requires work (energy).

## BETTI Mapping: Warmth Decay & Relationship Entropy

```
╔═══════════════════════════════════════════════════════════════╗
║         THERMODYNAMICS → BETTI RELATIONSHIP MONITORING        ║
╚═══════════════════════════════════════════════════════════════╝

S (Entropy)           →  Relationship disorder/coldness
ΔS > 0                →  Relationship degrading (colder)
ΔS = 0                →  Stable relationship (constant warmth)
ΔS < 0                →  Relationship improving (REQUIRES WORK!)
Irreversible process  →  Trust broken permanently
Heat flow Q           →  Emotional warmth exchange
Temperature T         →  Interaction warmth level
Work W                →  Effort to repair relationship
```

## The Core Principle: Warmth Naturally Decays

### Problem: Relationships Degrade Without Maintenance

```python
# Initial state: Warm relationship
initial_warmth = "warm"
initial_entropy = 0.0

# Time passes without interaction
# → Entropy increases (2nd law!)
# → Warmth decreases

after_7_days_warmth = "neutral"  # Colder!
after_7_days_entropy = 3.5       # More disorder

# This is NATURAL (thermodynamics!)
```

### BETTI Thermodynamic Monitoring

```python
def calculate_relationship_entropy(
    user_id: str,
    time_window_days: float = 7.0
) -> dict:
    """
    Calculate relationship entropy (disorder)

    High entropy = cold, disordered, failing relationship
    Low entropy = warm, ordered, healthy relationship
    """
    # Get interaction history
    interactions = get_interactions(user_id, time_window_days)

    # Calculate warmth sequence
    warmth_values = {
        "warm": 1.0,
        "neutral": 0.5,
        "cold": 0.0,
        "apologetic": 0.3
    }

    warmth_sequence = [
        warmth_values.get(interaction["warmth"], 0.5)
        for interaction in interactions
    ]

    # Entropy = measure of disorder
    # High variance in warmth = high entropy (unstable)
    # Declining warmth = increasing entropy (degrading)

    if len(warmth_sequence) == 0:
        return {"entropy": 10.0, "status": "no_interaction"}

    # Calculate entropy using Shannon entropy
    warmth_mean = np.mean(warmth_sequence)
    warmth_variance = np.var(warmth_sequence)

    # Trend: Is warmth decreasing?
    if len(warmth_sequence) >= 2:
        warmth_slope = (warmth_sequence[-1] - warmth_sequence[0]) / len(warmth_sequence)
    else:
        warmth_slope = 0.0

    # Entropy formula (simplified)
    # High when: low mean warmth, high variance, negative slope
    entropy = (
        (1.0 - warmth_mean) * 5.0 +        # Low warmth = high entropy
        warmth_variance * 3.0 +             # Unstable = high entropy
        max(0, -warmth_slope) * 2.0         # Declining = high entropy
    )

    # Interpret
    if entropy > 7.0:
        status = "critical"  # Relationship failing!
    elif entropy > 4.0:
        status = "degrading"  # Getting colder
    elif entropy > 2.0:
        status = "stable"     # Maintaining
    else:
        status = "improving"  # Getting warmer

    return {
        "entropy": entropy,
        "status": status,
        "mean_warmth": warmth_mean,
        "warmth_variance": warmth_variance,
        "warmth_trend": "declining" if warmth_slope < 0 else "improving",
        "slope": warmth_slope
    }

# Example:
entropy = calculate_relationship_entropy("user_123", time_window_days=7)
# {
#   "entropy": 6.5,           # High entropy!
#   "status": "degrading",    # Relationship getting colder
#   "mean_warmth": 0.4,       # Average warmth declining
#   "warmth_variance": 0.15,  # Unstable
#   "warmth_trend": "declining",
#   "slope": -0.08            # -8% per interaction
# }
```

## Detecting Irreversible Processes (HICSS Trigger)

### Irreversible = Cannot Undo Without Effort

```python
def detect_irreversible_damage(
    user_id: str,
    recent_interactions: list
) -> dict:
    """
    Detect if relationship damage is irreversible

    Like thermodynamics: Some processes can't be undone spontaneously
    Requires WORK (energy) to reverse
    """
    # Check for critical events
    critical_events = [
        "snaft_violation",       # Safety rule broken
        "intent_rejected_3x",    # Repeated rejections
        "user_frustration",      # Negative feedback
        "trust_broken"           # Explicit trust loss
    ]

    irreversible_markers = []

    for interaction in recent_interactions:
        if interaction.get("event_type") in critical_events:
            irreversible_markers.append({
                "event": interaction["event_type"],
                "timestamp": interaction["timestamp"],
                "severity": interaction.get("severity", "medium")
            })

    # Calculate "work required" to repair
    # Like thermodynamics: ΔS < 0 requires external work W
    entropy_current = calculate_relationship_entropy(user_id)["entropy"]
    entropy_baseline = 2.0  # Healthy baseline

    entropy_increase = entropy_current - entropy_baseline

    if entropy_increase > 5.0:
        # High entropy increase = significant work needed
        work_required = "high"  # Might be irreversible!
        reversible = False
    elif entropy_increase > 2.0:
        work_required = "medium"
        reversible = True  # Can repair with effort
    else:
        work_required = "low"
        reversible = True

    return {
        "irreversible": not reversible,
        "work_required": work_required,
        "entropy_increase": entropy_increase,
        "critical_events": irreversible_markers,
        "recommendation": "HICSS_HALT" if not reversible else "repair_with_effort"
    }

# Example: User getting frustrated
damage = detect_irreversible_damage("user_123", recent_interactions)
# {
#   "irreversible": False,
#   "work_required": "medium",
#   "entropy_increase": 3.2,
#   "critical_events": [
#     {"event": "intent_rejected_3x", "timestamp": "...", "severity": "medium"}
#   ],
#   "recommendation": "repair_with_effort"
# }
```

## User Tone Monitoring (Temperature Gradient)

### Detecting Coldness ("koudere toon")

```python
def monitor_user_tone_temperature(
    user_id: str,
    time_window: float = 3600.0  # 1 hour
) -> dict:
    """
    Monitor user's emotional "temperature" over time

    Like thermodynamics: Temperature drops when heat leaves system
    User tone getting colder = relationship cooling
    """
    # Get user messages/responses
    messages = get_user_messages(user_id, time_window)

    # Analyze tone per message
    tone_temperatures = []

    for msg in messages:
        # Analyze text sentiment/tone
        tone = analyze_message_tone(msg["text"])

        # Map to temperature
        temp_map = {
            "enthusiastic": 10.0,   # Hot
            "friendly": 8.0,
            "neutral": 5.0,         # Room temperature
            "short": 3.0,           # Cool
            "curt": 2.0,            # Cold
            "frustrated": 1.0       # Freezing
        }

        temperature = temp_map.get(tone, 5.0)
        tone_temperatures.append({
            "timestamp": msg["timestamp"],
            "temperature": temperature,
            "tone": tone
        })

    if len(tone_temperatures) == 0:
        return {"status": "no_data"}

    # Calculate temperature gradient (cooling rate)
    temps = [t["temperature"] for t in tone_temperatures]

    initial_temp = temps[0]
    current_temp = temps[-1]
    temp_change = current_temp - initial_temp

    # Cooling rate (degrees per hour)
    time_span = (
        tone_temperatures[-1]["timestamp"] -
        tone_temperatures[0]["timestamp"]
    ).total_seconds() / 3600.0

    cooling_rate = temp_change / time_span if time_span > 0 else 0.0

    # Interpret
    if cooling_rate < -3.0:
        status = "rapid_cooling"  # Emergency!
        action = "HICSS_HALT_immediately"
    elif cooling_rate < -1.0:
        status = "cooling"        # Warning
        action = "sense_and_adapt"
    elif cooling_rate < 0.5:
        status = "stable"         # OK
        action = "continue"
    else:
        status = "warming"        # Good!
        action = "continue_positive"

    return {
        "status": status,
        "initial_temperature": initial_temp,
        "current_temperature": current_temp,
        "temperature_change": temp_change,
        "cooling_rate": cooling_rate,  # Degrees/hour
        "tone_sequence": [t["tone"] for t in tone_temperatures],
        "recommended_action": action
    }

# Example: User getting frustrated
tone = monitor_user_tone_temperature("user_123", time_window=3600)
# {
#   "status": "rapid_cooling",
#   "initial_temperature": 8.0,  # Friendly
#   "current_temperature": 2.0,  # Curt
#   "temperature_change": -6.0,  # Dropped 6 degrees!
#   "cooling_rate": -6.0,        # -6°/hour
#   "tone_sequence": ["friendly", "neutral", "short", "curt"],
#   "recommended_action": "HICSS_HALT_immediately"
# }

# Thermodynamics detected: User is cooling rapidly!
# System should HALT and change approach!
```

## Sense Rules with Entropy Triggers

```python
def create_entropy_sense_rule(
    name: str,
    entropy_threshold: float = 6.0
) -> dict:
    """
    Create sense rule that triggers on high entropy (disorder)

    When relationship entropy exceeds threshold → Take action!
    """
    sense_rule = {
        "name": name,
        "type": "entropy_monitor",
        "conditions": {
            "relationship_entropy": {"gte": entropy_threshold},
            "status": {"in": ["degrading", "critical"]}
        },
        "actions": [
            {
                "type": "hicss_override",
                "action": "HALT",
                "reason": "High entropy - relationship failing"
            },
            {
                "type": "notify",
                "message": "User relationship degrading - intervention needed"
            },
            {
                "type": "balans_preference_update",
                "warmth": "apologetic",
                "reasoning": "Relationship under stress"
            }
        ],
        "priority": 9  # High priority!
    }

    return sense_rule

# Install rule
rule = create_entropy_sense_rule("entropy_failsafe", threshold=6.0)
install_sense_rule(rule)

# Now: When entropy > 6.0 → Automatic HICSS HALT!
```

## Work Required to Reduce Entropy

### Thermodynamic Formula

```
ΔS = Q/T  (reversible process)
ΔS > Q/T  (irreversible process)

To reduce entropy (ΔS < 0): Must do work W
```

### BETTI Implementation

```python
def calculate_repair_work(
    current_entropy: float,
    target_entropy: float = 2.0  # Healthy baseline
) -> dict:
    """
    Calculate "work" (effort) required to repair relationship

    Like thermodynamics: Reducing entropy requires energy input
    """
    entropy_reduction_needed = current_entropy - target_entropy

    if entropy_reduction_needed <= 0:
        return {
            "work_required": 0,
            "actions": [],
            "status": "healthy"
        }

    # Work required (arbitrary units, could be time/interactions/resources)
    # More entropy = exponentially more work!
    work_units = entropy_reduction_needed ** 2  # Quadratic!

    # Translate to concrete actions
    actions = []

    if work_units > 20:
        # Very high work required
        actions = [
            {"type": "human_intervention", "priority": "critical"},
            {"type": "apologize_explicitly", "warmth": "apologetic"},
            {"type": "offer_compensation", "value": "high"},
            {"type": "reset_expectations"}
        ]
        repair_probability = 0.3  # Low chance!
    elif work_units > 10:
        actions = [
            {"type": "clarification_dialogue", "priority": "high"},
            {"type": "adjust_balans_preferences", "warmth": "warm"},
            {"type": "proactive_suggestions"}
        ]
        repair_probability = 0.6
    else:
        actions = [
            {"type": "warmer_responses", "warmth": "warm"},
            {"type": "faster_execution"}
        ]
        repair_probability = 0.9

    return {
        "work_required": work_units,
        "entropy_reduction_needed": entropy_reduction_needed,
        "actions": actions,
        "estimated_interactions_needed": int(work_units / 2),
        "repair_probability": repair_probability,
        "warning": "High work required!" if work_units > 10 else None
    }

# Example: High entropy user
repair = calculate_repair_work(current_entropy=8.5, target=2.0)
# {
#   "work_required": 42.25,  # Quadratic: (8.5-2.0)² = 6.5² = 42.25
#   "entropy_reduction_needed": 6.5,
#   "actions": [
#     {"type": "human_intervention", "priority": "critical"},
#     {"type": "apologize_explicitly", ...},
#     ...
#   ],
#   "estimated_interactions_needed": 21,
#   "repair_probability": 0.3,  # Only 30% chance to repair!
#   "warning": "High work required!"
# }
```

## Database Schema

```sql
-- Relationship entropy tracking
CREATE TABLE IF NOT EXISTS relationship_entropy (
    id BIGSERIAL PRIMARY KEY,
    user_id VARCHAR(255) NOT NULL,
    timestamp TIMESTAMPTZ DEFAULT NOW(),

    -- Thermodynamic metrics
    entropy DECIMAL(8,4) NOT NULL,
    temperature DECIMAL(6,2),         -- Emotional temperature
    heat_flow DECIMAL(8,4),           -- Warmth exchange rate
    work_required DECIMAL(10,2),      -- Effort to repair

    -- Status
    status VARCHAR(20),               -- healthy, stable, degrading, critical
    irreversible BOOLEAN DEFAULT false,

    -- Trends
    entropy_change_rate DECIMAL(8,4), -- dS/dt
    temperature_gradient DECIMAL(6,2), -- dT/dt (cooling rate)

    INDEX idx_entropy_user (user_id),
    INDEX idx_entropy_time (timestamp DESC),
    INDEX idx_entropy_status (status)
);

-- Irreversible events
CREATE TABLE IF NOT EXISTS irreversible_events (
    id BIGSERIAL PRIMARY KEY,
    user_id VARCHAR(255) NOT NULL,
    timestamp TIMESTAMPTZ DEFAULT NOW(),

    event_type VARCHAR(100),          -- snaft_violation, trust_broken, etc.
    severity VARCHAR(20),             -- low, medium, high, critical
    entropy_at_event DECIMAL(8,4),
    work_to_repair DECIMAL(10,2),

    repaired BOOLEAN DEFAULT false,
    repaired_at TIMESTAMPTZ,
    repair_work_actual DECIMAL(10,2),

    INDEX idx_irreversible_user (user_id),
    INDEX idx_irreversible_repaired (repaired) WHERE repaired = false
);
```

## Integration with BALANS & HICSS

```python
def balans_with_thermodynamics(
    intent: str,
    context: dict,
    user_id: str
) -> dict:
    """
    BALANS enhanced with thermodynamic monitoring
    """
    # Standard BALANS decision
    decision = balans_pre_execution_check(intent, context)

    # Check relationship entropy
    entropy_status = calculate_relationship_entropy(user_id)

    if entropy_status["entropy"] > 6.0:
        # High entropy detected!
        # Override decision to protect relationship

        # Check if irreversible damage imminent
        damage = detect_irreversible_damage(user_id, recent_interactions)

        if damage["irreversible"]:
            # CRITICAL: Irreversible damage!
            return {
                "decision": "halt",  # HICSS HALT!
                "reasoning": "Irreversible relationship damage detected",
                "entropy": entropy_status["entropy"],
                "warmth": "apologetic",
                "color": "red",
                "hicss_override": "HALT",
                "recommended_action": "human_intervention_required"
            }

        # Moderate damage - adjust response
        decision["warmth"] = "apologetic"
        decision["reasoning"] += f" (Relationship entropy high: {entropy_status['entropy']:.1f})"
        decision["extra_care"] = True

    # Check user tone temperature
    tone = monitor_user_tone_temperature(user_id)

    if tone["status"] == "rapid_cooling":
        # User is getting frustrated FAST!
        return {
            "decision": "halt",  # HICSS HALT!
            "reasoning": f"User tone cooling rapidly ({tone['cooling_rate']:.1f}°/hour)",
            "warmth": "apologetic",
            "color": "red",
            "hicss_override": "HALT",
            "suggested_approach": "switch_strategy"
        }

    return decision
```

## Benefits

1. **Early Warning**: Detect relationship degradation before it's too late
2. **Quantitative**: Entropy gives measurable relationship health
3. **Irreversibility Detection**: Know when damage might be permanent
4. **Work Estimation**: Calculate effort needed to repair
5. **Natural Law**: Based on thermodynamics (proven, universal)

---

**Author**: Jasper van der Meent (BETTI Architecture)
**Date**: November 28, 2025
**Status**: Specification Complete
**Related**: BETTI-MAXWELL-MONITORING.md, betti_balans.py, HICSS
