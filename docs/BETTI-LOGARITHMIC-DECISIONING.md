# BETTI Logarithmic Decision Framework

**Mathematical Foundation for Temporal & Resource-Based Intent Execution**

## Abstract

BALANS currently uses linear scoring for decision-making. This document introduces **logarithmic functions** to model:
1. **Time-based urgency decay** (now vs later decisions)
2. **Resource sufficiency curves** (battery, memory, CPU)
3. **Learning rate diminishment** (device awareness)
4. **Complexity impact scaling** (task difficulty vs capability)

## Core Principle: Logarithmic Scaling

### Why Logarithms?

Logarithms model **diminishing returns** - the natural behavior of:
- **Urgency**: First minute matters more than 60th minute
- **Battery**: 10%→30% bigger impact than 60%→80%
- **Learning**: First violation teaches more than 100th
- **Complexity**: Doubling complexity doesn't double difficulty

### Mathematical Foundation

```
log₁₀(x + 1)  - Base 10 logarithm with offset
ln(x + 1)     - Natural logarithm with offset
log₂(x + 1)   - Binary logarithm (doubling scale)
```

The `+1` offset prevents `log(0) = -∞` for zero values.

## Part 1: Temporal Decision Power

### The Core Formula

```
Execute_Now_Power = (Urgency × Resource_Score) / Time_Penalty

Where:
  Resource_Score = log₁₀(Battery_pct + 1) × log₁₀(Memory_MB + 1)
  Time_Penalty = log₁₀(Delay_Minutes + 2)
```

### Example Calculations

#### Scenario 1: Urgent + Good Resources + No Delay
```python
urgency = 10          # Critical
battery_pct = 80      # Good
memory_mb = 2000      # Good
delay_minutes = 0     # Now

resource_score = log₁₀(80+1) × log₁₀(2000+1)
               = 1.908 × 3.301
               = 6.30

time_penalty = log₁₀(0+2) = 0.301

execute_now_power = (10 × 6.30) / 0.301
                  = 63.0 / 0.301
                  = 209.3  ← Very high! Execute now!
```

#### Scenario 2: Same Intent, 30 Minute Delay
```python
urgency = 10
battery_pct = 80
memory_mb = 2000
delay_minutes = 30    # ← Changed

resource_score = 6.30  (same)
time_penalty = log₁₀(30+2) = 1.505

execute_now_power = (10 × 6.30) / 1.505
                  = 63.0 / 1.505
                  = 41.9  ← Much lower! Consider delaying.
```

#### Scenario 3: Low Battery, Must Charge
```python
urgency = 10
battery_pct = 12      # ← Low!
memory_mb = 2000
delay_minutes = 20    # Charge time

resource_score = log₁₀(12+1) × log₁₀(2000+1)
               = 1.114 × 3.301
               = 3.68

time_penalty = log₁₀(20+2) = 1.342

execute_now_power = (10 × 3.68) / 1.342
                  = 36.8 / 1.342
                  = 27.4  ← Lower than scenario 2!
                          → Better to delay and charge first
```

### Decay Curves

```
Minutes Delay | Time Penalty | Urgency Factor (10/penalty)
──────────────┼──────────────┼──────────────────────────────
0             | 0.301        | 33.2  (NOW!)
1             | 0.477        | 21.0
5             | 0.845        | 11.8
10            | 1.079        | 9.3
30            | 1.505        | 6.6
60            | 1.792        | 5.6
120           | 2.086        | 4.8
```

**Insight**: First minute costs 33.2→21.0 = -37% urgency
             Next 59 minutes cost 21.0→5.6 = -73% urgency
             → Logarithmic decay models reality!

## Part 2: Resource Sufficiency Scoring

### Battery Power Curve

```python
def battery_score(battery_pct: float) -> float:
    """
    Logarithmic battery sufficiency

    Returns score from 0.0 (empty) to 2.0 (full)
    """
    if battery_pct <= 0:
        return 0.0

    # log₁₀(100+1) = 2.004 (max score)
    return math.log10(battery_pct + 1)

# Examples:
battery_score(0)   = 0.0    # Empty → Cannot execute
battery_score(10)  = 1.041  # Low → Risky
battery_score(30)  = 1.491  # OK → Can execute simple tasks
battery_score(50)  = 1.708  # Good → Can execute most tasks
battery_score(80)  = 1.908  # Excellent → Execute anything
battery_score(100) = 2.004  # Full → Maximum capability
```

**Key Insight**:
- 0→30%: Gain 1.491 score (huge impact)
- 30→60%: Gain 0.217 score (diminishing)
- 60→100%: Gain 0.296 score (minimal)

This matches real battery behavior: last 40% matters less!

### Memory Availability Curve

```python
def memory_score(memory_mb: float) -> float:
    """
    Logarithmic memory sufficiency

    Returns score from 0.0 (none) to 3.3 (abundant)
    """
    if memory_mb <= 0:
        return 0.0

    # log₁₀(2000+1) ≈ 3.301 (typical max for small devices)
    return math.log10(memory_mb + 1)

# Examples:
memory_score(0)     = 0.0    # None → Cannot execute
memory_score(50)    = 1.708  # Minimal → Simple tasks only
memory_score(200)   = 2.303  # OK → Most tasks
memory_score(500)   = 2.700  # Good → Complex tasks
memory_score(2000)  = 3.301  # Excellent → Any task
```

### Combined Resource Score

```python
def resource_readiness(
    battery_pct: float,
    memory_mb: float,
    cpu_load_pct: float
) -> float:
    """
    Combined resource score using logarithmic scaling

    Returns: 0.0 (insufficient) to 10.0 (perfect)
    """
    # Individual scores
    battery = math.log10(battery_pct + 1)  # 0-2
    memory = math.log10(memory_mb + 1)     # 0-3.3
    cpu_available = 100 - cpu_load_pct
    cpu = math.log10(cpu_available + 1)    # 0-2

    # Weighted combination
    score = (battery * 2.5) + (memory * 2.0) + (cpu * 1.5)

    # Normalize to 0-10
    max_possible = (2.0 * 2.5) + (3.3 * 2.0) + (2.0 * 1.5)
    # max_possible ≈ 14.6

    return (score / max_possible) * 10.0

# Examples:
resource_readiness(80, 2000, 20)  = 9.2  # Excellent
resource_readiness(50, 1000, 50)  = 7.4  # Good
resource_readiness(30, 500, 70)   = 5.8  # Marginal
resource_readiness(12, 200, 85)   = 3.1  # Poor → Delay!
```

## Part 3: Device Learning Curve

### Awareness Growth Formula

```python
def calculate_awareness_gain(violations: int) -> float:
    """
    Logarithmic learning: first mistakes teach most

    Returns: awareness points gained
    """
    if violations == 0:
        return 0.0

    # Natural log for learning (gentler curve)
    return math.log(violations + 1) * 10

# Examples:
calculate_awareness_gain(1)    = 6.93  # First violation: big lesson!
calculate_awareness_gain(5)    = 17.9  # 5 violations: good learning
calculate_awareness_gain(10)   = 23.9  # 10 violations: solid awareness
calculate_awareness_gain(50)   = 39.3  # 50 violations: expert level
calculate_awareness_gain(100)  = 46.2  # 100 violations: diminishing returns
```

**Reality Check**:
- First mistake (0→1): Gain 6.93 points
- 100th mistake (99→100): Gain 0.07 points
- Device stops learning from repeated mistakes (logarithmic plateau)

### Self-Awareness Level

```sql
-- Update device_awareness table with logarithmic scoring
UPDATE device_awareness
SET
    self_awareness_level = LOG(snaft_violations_learned + 1) * 10,
    learning_efficiency = 1.0 / LOG(snaft_violations_learned + 2)
WHERE snaft_violations_learned > 0;
```

## Part 4: Complexity Impact Scaling

### Current Problem

```python
# Linear (current implementation):
complexity_score = 45
if complexity_score > 50:
    scores['partial'] += 0.4

# Problem: 45 vs 55 is treated as discrete jump
# Reality: Complexity impact should scale smoothly
```

### Logarithmic Solution

```python
def complexity_impact(complexity_score: float) -> float:
    """
    Logarithmic complexity impact on execution difficulty

    complexity_score: 0-100 (from B0-B5 analysis)
    Returns: impact multiplier 1.0-3.0
    """
    if complexity_score <= 0:
        return 1.0

    # log₁₀(100+1) = 2.004
    # Scale to 1.0-3.0 range (3× harder at max complexity)
    log_score = math.log10(complexity_score + 1)
    return 1.0 + (log_score / 2.004) * 2.0

# Examples:
complexity_impact(0)    = 1.0   # Trivial → no impact
complexity_impact(10)   = 1.52  # Simple → 52% harder
complexity_impact(30)   = 1.74  # Medium → 74% harder
complexity_impact(50)   = 1.85  # Complex → 85% harder
complexity_impact(100)  = 2.0   # Maximum → 100% harder (2× duration)
```

## Part 5: Updated BALANS Scoring Function

### Improved Implementation

```python
import math
from typing import Dict
from datetime import datetime, timedelta

def calculate_decision_scores_logarithmic(
    resources: ResourceStatus,
    understanding: UnderstandingStatus,
    user_urgency: int,
    robot_urgency: int,
    complexity_score: float,
    deadline: Optional[datetime],
    estimated_duration: float
) -> Dict[str, float]:
    """
    Calculate weighted scores using LOGARITHMIC functions

    Returns dict: {decision_type: confidence_score}
    """
    scores = {
        'execute_now': 0.0,
        'delay': 0.0,
        'clarify': 0.0,
        'partial': 0.0,
        'reject': 0.0,
        'request_resources': 0.0
    }

    # ========== RESOURCE SCORING (Logarithmic) ==========
    battery_score = math.log10(resources.battery_pct + 1) if resources.battery_pct > 0 else 0.0
    memory_score = math.log10(resources.memory_available_mb + 1) if resources.memory_available_mb > 0 else 0.0
    cpu_available = 100 - resources.cpu_load_pct
    cpu_score = math.log10(cpu_available + 1)

    # Combined resource readiness: 0-10 scale
    resource_readiness = (
        (battery_score / 2.0) * 0.4 +  # Battery 40% weight
        (memory_score / 3.3) * 0.3 +   # Memory 30% weight
        (cpu_score / 2.0) * 0.3        # CPU 30% weight
    ) * 10.0

    # ========== TIME-BASED URGENCY (Logarithmic Decay) ==========
    # If deadline exists, calculate time pressure
    if deadline:
        time_until_deadline_mins = (deadline - datetime.now()).total_seconds() / 60
        time_pressure = user_urgency / math.log10(max(time_until_deadline_mins, 1) + 2)
    else:
        # No deadline: use base urgency
        time_pressure = user_urgency / 10.0

    # ========== COMPLEXITY IMPACT (Logarithmic) ==========
    complexity_multiplier = 1.0 + (math.log10(complexity_score + 1) / 2.0)

    # Adjust estimated duration with complexity
    adjusted_duration = estimated_duration * complexity_multiplier

    # ========== EXECUTE_NOW SCORING ==========
    # Base score from resource readiness
    scores['execute_now'] = resource_readiness / 10.0  # 0-1 scale

    # Boost if high urgency
    scores['execute_now'] += time_pressure * 0.3

    # Boost if understanding is clear
    if understanding.clarity_sufficient:
        scores['execute_now'] += understanding.confidence * 0.3
    else:
        scores['execute_now'] -= 0.5  # Penalty for unclear intent

    # Penalty if resources critically low
    if resources.battery_pct < 15:
        scores['execute_now'] -= 0.6

    # ========== DELAY SCORING ==========
    if deadline:
        # Can we afford to delay?
        time_until_deadline_mins = (deadline - datetime.now()).total_seconds() / 60
        if time_until_deadline_mins > adjusted_duration * 3:
            # Plenty of time
            scores['delay'] += 0.5

            # Logarithmic bonus for more time available
            time_buffer_score = math.log10(time_until_deadline_mins / adjusted_duration) / 2.0
            scores['delay'] += min(0.3, time_buffer_score)
        else:
            # Tight deadline
            scores['delay'] -= 0.4

    if not resources.network_sufficient:
        scores['delay'] += 0.3  # Wait for better network

    if robot_urgency < 5:
        scores['delay'] += 0.2  # Robot not urgent

    # ========== CLARIFY SCORING ==========
    if not understanding.clarity_sufficient:
        # Strong logarithmic preference based on confusion level
        confusion = 1.0 - understanding.confidence
        scores['clarify'] = 0.5 + (confusion * 0.5)

    # ========== REQUEST_RESOURCES SCORING ==========
    if not resources.battery_sufficient:
        # Logarithmic urgency based on how low battery is
        battery_deficit = 30 - resources.battery_pct  # Assume 30% minimum
        if battery_deficit > 0:
            scores['request_resources'] += math.log10(battery_deficit + 1) / 3.0

    if not resources.memory_sufficient:
        scores['request_resources'] += 0.3

    if robot_urgency > 7:
        scores['request_resources'] += 0.2  # Robot needs help urgently

    # ========== PARTIAL SCORING ==========
    if complexity_score > 50:
        # Logarithmic scoring for splitting complex tasks
        complexity_excess = complexity_score - 50
        scores['partial'] += math.log10(complexity_excess + 1) / 3.0

    if not resources.battery_sufficient and complexity_score > 20:
        scores['partial'] += 0.3  # Split to do part now, part later

    # ========== REJECT SCORING ==========
    if resource_readiness < 3.0:  # Very low resources
        scores['reject'] += 0.4

    if understanding.confidence < 0.3:
        scores['reject'] += 0.4

    # ========== NORMALIZATION ==========
    # Ensure all scores are in valid range [0.0, 1.0]
    for key in scores:
        scores[key] = max(0.0, min(1.0, scores[key]))

    return scores
```

## Part 6: Practical Examples

### Example 1: Battery-Constrained Decision

```python
# Input
resources = ResourceStatus(
    battery_pct=12,
    memory_available_mb=2000,
    cpu_load_pct=20
)
user_urgency = 8
estimated_duration = 5  # minutes

# Calculation
battery_score = log₁₀(12+1) = 1.114
memory_score = log₁₀(2000+1) = 3.301
cpu_score = log₁₀(80+1) = 1.908

resource_readiness = (1.114/2.0)*0.4 + (3.301/3.3)*0.3 + (1.908/2.0)*0.3
                   = 0.223 + 0.300 + 0.286
                   = 0.809 * 10
                   = 8.09 / 10 (NOT sufficient!)

battery_deficit = 30 - 12 = 18
request_resources_score = log₁₀(18+1) / 3.0 = 0.39

Decision: request_resources (score: 0.39 + base)
Reasoning: "Battery at 12%. May I charge first? (20 minutes)"
```

### Example 2: Time Pressure Decision

```python
# Input
urgency = 10
deadline = datetime.now() + timedelta(minutes=10)
estimated_duration = 8  # minutes (tight!)

# Calculation
time_until_deadline = 10 minutes
time_pressure = 10 / log₁₀(10+2) = 10 / 1.079 = 9.27

Time buffer = 10 / 8 = 1.25× (not much!)
delay_score = 0.0 (cannot afford delay)
execute_now_score += 9.27 * 0.3 = 2.78 (strong boost)

Decision: execute_now (high urgency, tight deadline)
Reasoning: "Deadline in 10 minutes. Executing immediately."
```

### Example 3: Complex Task Splitting

```python
# Input
complexity_score = 75
battery_pct = 40

# Calculation
complexity_multiplier = 1.0 + (log₁₀(75+1) / 2.0)
                      = 1.0 + (1.881 / 2.0)
                      = 1.94× difficulty

Battery marginal (40% < 50% ideal)
Task will take 1.94× longer than expected

partial_score = log₁₀(75-50+1) / 3.0 + 0.3 (battery consideration)
              = log₁₀(26) / 3.0 + 0.3
              = 1.415 / 3.0 + 0.3
              = 0.47 + 0.3
              = 0.77

Decision: partial (split into smaller tasks)
Reasoning: "Complex task (score: 75). Battery at 40%. I can start now and continue after charging."
```

## Part 7: Database Schema Updates

### Add Logarithmic Metrics to balans_decisions

```sql
-- Add logarithmic scoring columns
ALTER TABLE balans_decisions
ADD COLUMN resource_readiness_log DECIMAL(5,2),
ADD COLUMN time_pressure_log DECIMAL(5,2),
ADD COLUMN complexity_impact_log DECIMAL(5,2),
ADD COLUMN decision_power_score DECIMAL(8,2);

-- Update with logarithmic calculations
UPDATE balans_decisions
SET
    resource_readiness_log = (
        (LOG(battery_pct + 1) / 2.0) * 0.4 +
        (LOG(memory_available_mb + 1) / 3.3) * 0.3 +
        (LOG(100 - cpu_load_pct + 1) / 2.0) * 0.3
    ) * 10.0,
    complexity_impact_log = 1.0 + (LOG(complexity_score + 1) / 2.0),
    decision_power_score = (user_urgency * resource_readiness_log) /
                          NULLIF(LOG(estimated_duration_minutes + 2), 0);
```

### Add Learning Rate to device_awareness

```sql
-- Add logarithmic learning metrics
ALTER TABLE device_awareness
ADD COLUMN learning_rate DECIMAL(5,2),
ADD COLUMN awareness_plateau DECIMAL(5,2);

UPDATE device_awareness
SET
    learning_rate = 1.0 / LOG(snaft_violations_learned + 2),
    awareness_plateau = LOG(snaft_violations_learned + 1) * 10;
```

## Part 8: Visualization & Monitoring

### Dashboard Query: Logarithmic Decision Distribution

```sql
-- Analyze decisions by logarithmic power score
SELECT
    decision,
    COUNT(*) as count,
    AVG(decision_power_score) as avg_power,
    PERCENTILE_CONT(0.5) WITHIN GROUP (ORDER BY decision_power_score) as median_power,
    MIN(decision_power_score) as min_power,
    MAX(decision_power_score) as max_power
FROM balans_decisions
WHERE timestamp > NOW() - INTERVAL '7 days'
GROUP BY decision
ORDER BY avg_power DESC;
```

### Monitor Resource-Decision Correlation

```sql
-- How does battery level correlate with decisions?
SELECT
    FLOOR(battery_pct / 10) * 10 as battery_range,
    decision,
    COUNT(*) as count,
    AVG(resource_readiness_log) as avg_readiness,
    AVG(decision_confidence) as avg_confidence
FROM balans_decisions
WHERE timestamp > NOW() - INTERVAL '7 days'
GROUP BY battery_range, decision
ORDER BY battery_range, count DESC;
```

## Part 9: Benefits of Logarithmic Scoring

### 1. **Natural Decay**
- Urgency decreases naturally over time
- Matches human perception of urgency
- Prevents abrupt decision changes

### 2. **Realistic Resource Impact**
- First 30% of battery matters most
- Memory impact plateaus at higher amounts
- Models real hardware behavior

### 3. **Learning Efficiency**
- Devices learn faster from first mistakes
- Prevents over-learning from repeated errors
- Awareness plateaus naturally

### 4. **Smooth Scaling**
- No discrete jumps in scoring
- Complexity scales realistically
- Better decision boundaries

### 5. **Mathematical Elegance**
- Pythagoras (NIR): a² + b² = c²
- Einstein (Relativity): E=mc²
- BETTI (Decisioning): Power = (U × R) / log(T)

## Part 10: Migration Plan

### Phase 1: Add Logarithmic Columns (Non-Breaking)
```sql
-- Add new columns without removing old ones
ALTER TABLE balans_decisions
ADD COLUMN resource_readiness_log DECIMAL(5,2),
ADD COLUMN time_pressure_log DECIMAL(5,2);
```

### Phase 2: Dual Calculation (Testing)
```python
# Calculate both linear and logarithmic scores
scores_linear = _calculate_decision_scores_linear(...)
scores_log = _calculate_decision_scores_logarithmic(...)

# Use linear for decisions (current behavior)
# Log logarithmic for analysis
```

### Phase 3: A/B Testing
```python
# 50% of requests use logarithmic scoring
if hash(intent_id) % 2 == 0:
    scores = _calculate_decision_scores_logarithmic(...)
else:
    scores = _calculate_decision_scores_linear(...)
```

### Phase 4: Full Migration
```python
# Replace linear with logarithmic everywhere
scores = _calculate_decision_scores_logarithmic(...)
```

### Phase 5: Remove Linear Code
```python
# Cleanup: remove old _calculate_decision_scores function
```

## Conclusion

Logarithmic functions provide **mathematical elegance** for temporal and resource-based decision-making:

- ✅ **Pythagoras** for NIR (Notify² + Identify² = Rectify²)
- ✅ **Einstein** for relativity (Intent meaning depends on context)
- ✅ **Logarithms** for decay/growth (time urgency, battery impact, learning curves)

BETTI becomes not just an API, but a **mathematically grounded framework** for autonomous systems.

---

**Authors**: Jasper van der Meent (Architecture) + Claude Sonnet 4.5 (Implementation)
**Date**: 2025-11-28
**Status**: Specification (Ready for Implementation)
**Related**: BETTI-BALANS-README.md, BETTI-COMPLETE-CAPABILITIES.md
