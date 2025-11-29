# BETTI Humotica Framework

**Human-Readable Context: The "Why" Behind Every Intent**

## What is Humotica?

**Humotica** = **Hum**an-readable context + L**ogica** (logic)

The human-understandable explanation of *why* an intent exists, *what* the user really wants to achieve, and *how* the system should interpret ambiguous situations.

```
╔═══════════════════════════════════════════════════════════════╗
║                  INTENT WITHOUT HUMOTICA                      ║
╚═══════════════════════════════════════════════════════════════╝

{
  "intent": "turn_on_lights",
  "parameters": {"location": "living_room"}
}

→ Computer knows WHAT
→ Computer doesn't know WHY
→ No context for edge cases
→ No human empathy
```

```
╔═══════════════════════════════════════════════════════════════╗
║                   INTENT WITH HUMOTICA                        ║
╚═══════════════════════════════════════════════════════════════╝

{
  "intent": "turn_on_lights",
  "parameters": {"location": "living_room"},
  "humotica": "User arriving home after work, it's dark outside,
               wants comfortable lighting to relax. Not urgent but
               prefer quick response for welcoming feeling."
}

→ Computer knows WHAT
→ Computer knows WHY
→ Computer understands CONTEXT
→ Computer can empathize
→ Better decisions possible!
```

## The Core Principle: Meaning Over Commands

### Traditional Systems (Command-Based)

```python
# Traditional
command = "EXECUTE: turn_on_lights brightness=80"

# Problems:
# - No "why" - just blind execution
# - No context - 80% always, even at 3 AM?
# - No empathy - doesn't understand user need
# - No adaptation - can't adjust for situation
```

### BETTI (Intent + Humotica)

```python
# BETTI
intent = {
    "intent": "turn_on_lights",
    "parameters": {"brightness": 80},
    "humotica": """
        User just woke up (6:45 AM on workday).
        Wants gradual lighting to wake up gently.
        Prefer warm white color for morning comfort.
        Not urgent - can take 30 seconds to reach full brightness.
    """
}

# BALANS can now:
# ✓ Adjust brightness curve (gradual, not instant)
# ✓ Choose warm white (not cold white)
# ✓ Delay execution if needed (not urgent)
# ✓ Understand user's emotional state (waking up)
```

## Humotica Structure

### 1. The "Why" (Purpose)

```
Why does the user want this?

Examples:
- "User arriving home and wants welcoming atmosphere"
- "Battery low, user needs device to last until evening"
- "User preparing for video call, needs good lighting"
- "Emergency situation - smoke detected, user evacuating"
```

### 2. The "Context" (Situation)

```
What's the current situation?

Examples:
- "Late evening (22:30), user usually goes to bed at 23:00"
- "User in meeting, phone on silent, don't disturb unless urgent"
- "Raining outside, roads slippery, drive carefully"
- "User frustrated after 3 failed attempts, needs clear guidance"
```

### 3. The "Preference" (Desired Behavior)

```
How should the system behave?

Examples:
- "Prefer quick response over energy saving in this case"
- "Accuracy more important than speed for this task"
- "If unclear, ask - don't guess"
- "Silent operation preferred, user is sleeping"
```

### 4. The "Emotion" (Human State)

```
What's the user's emotional state?

Examples:
- "User excited about trying new feature"
- "User stressed, needs calming interface"
- "User confused, needs simple explanation"
- "User confident, can handle technical details"
```

## Humotica in Practice

### Example 1: Smart Home Morning Routine

```python
intent = {
    "intent": "start_morning_routine",
    "parameters": {
        "time": "07:00",
        "user": "jasper@jtel.nl"
    },
    "humotica": """
        User's morning routine on workday.
        Alarm went off at 6:45, user snoozed once (tired today).

        Desired sequence:
        1. Gradual lights (30 seconds to full brightness)
        2. Warm white color (2700K - comfortable wake-up)
        3. Coffee machine start (8 minutes brew time)
        4. Curtains open slowly (avoid sudden brightness)
        5. Heating up to 21°C (currently 18°C)

        Context:
        - User has important meeting at 9:00 (needs to leave at 8:30)
        - Outside temperature: 5°C (cold morning)
        - Weather: rainy (might need extra time for traffic)

        Preferences:
        - Prioritize coffee readiness (critical!)
        - Allow heating to be slower if needed (less critical)
        - If any device fails, notify immediately (time-sensitive)

        Emotional state:
        - Slightly stressed (important meeting)
        - Tired (snoozed alarm)
        - Needs gentle wake-up (not jarring experience)

        Decision guidance:
        - If coffee machine unavailable: HALT routine, notify user immediately
        - If lights fail: Continue with curtains (alternative lighting)
        - If running late: Prioritize critical items only
    """
}

# BALANS can now make INTELLIGENT decisions:
# - Knows coffee is critical (will allocate resources)
# - Understands emotional state (gentle approach)
# - Has fallback options (lights fail → use curtains)
# - Knows time constraints (meeting at 9:00)
```

### Example 2: Robot Task Assignment

```python
intent = {
    "intent": "clean_warehouse_floor",
    "parameters": {
        "area": "section_A",
        "robot_id": "robot_007"
    },
    "humotica": """
        Warehouse floor cleaning task for robot_007.

        Background:
        - Section A has received new inventory shipment (dusty boxes)
        - Forklift will be operating in adjacent section B (potential collision)
        - Cleaning must be done before tomorrow's audit (6:00 AM)

        Current state:
        - Robot battery: 45% (medium, can complete but tight)
        - Time available: 8 hours until audit
        - Task complexity: Medium (obstacles from new boxes)

        Constraints:
        - Safety critical: Must avoid forklift path
        - Time constraint: Must complete before 6:00 AM
        - Quality requirement: High (audit tomorrow)

        Robot perspective (Internal TIBET):
        - Robot knows it can do task but needs charging midway
        - Robot prefers to charge now (30 min) then do task uninterrupted
        - Alternative: Start now, charge later (riskier - might not finish)

        Desired behavior:
        - If robot requests charging first: Approve (sensible approach)
        - If forklift enters section: HICSS HALT immediately (safety!)
        - If battery drops below 20% during task: Auto-return to charger

        Decision guidance:
        - Quality over speed (audit is critical)
        - Safety over completion (forklift has right-of-way)
        - Allow robot autonomy (it knows its capabilities best)
    """
}

# BALANS + SNAFT can now:
# ✓ Approve robot's request to charge first (makes sense)
# ✓ Monitor forklift position (safety constraint)
# ✓ Set HICSS HALT trigger on proximity detection
# ✓ Trust robot's Internal TIBET judgment
# ✓ Prioritize quality (high stakes audit)
```

### Example 3: User Frustration Recovery

```python
intent = {
    "intent": "turn_on_heating",
    "parameters": {
        "temperature": 22,
        "location": "bedroom"
    },
    "humotica": """
        User attempting to turn on heating.

        CRITICAL CONTEXT - User frustrated:
        - This is the 4th attempt (previous 3 failed)
        - Failure reasons:
          1. "Battery too low" (robot response)
          2. "Location unclear" (clarification request)
          3. "Network timeout" (system error)
        - User tone getting colder (thermodynamics alert!)
        - User simplifying commands (frustration pattern)

        Emotional state:
        - Highly frustrated (entropy increasing)
        - Patience running out (near irreversible damage)
        - Considering abandoning system (critical!)

        Current situation:
        - User is cold (temperature: 16°C, uncomfortable)
        - It's late evening (22:45, wants to sleep)
        - User tried manual thermostat but it's broken
        - This is last resort (high urgency despite no deadline)

        THERMODYNAMIC WARNING:
        - Relationship entropy: 7.2 (HIGH!)
        - Cooling rate: -5.8°/hour (RAPID!)
        - Work required to repair: 28 units (SIGNIFICANT!)
        - Irreversible damage risk: 65% (DANGER!)

        Required behavior:
        - EXECUTE IMMEDIATELY (no more delays!)
        - NO clarifications (user already simplified)
        - NO resource requests (find a way!)
        - SUCCESS CRITICAL (last chance to preserve trust)

        Fallback plan:
        - If heating unavailable: Suggest alternative (space heater, blankets)
        - If still fails: Human intervention required
        - Apologize profusely (warmth = apologetic)

        Decision guidance:
        - This is a trust recovery moment
        - Success = relationship saved
        - Failure = irreversible damage (user will abandon system)
        - Prioritize execution over efficiency
        - Use any available resources (override battery constraints if needed)
    """
}

# BALANS with thermodynamics sees:
# ⚠️  Entropy critical (7.2)
# ⚠️  Rapid cooling (-5.8°/hour)
# ⚠️  Irreversible damage imminent
#
# Decision override:
# → EXECUTE despite low battery (borrow from reserves)
# → NO clarifications (user already crystal clear)
# → Warmth = apologetic (acknowledge frustration)
# → Color = orange (urgent, trying hard)
# → Internal TIBET: "I understand user frustration, executing despite constraints"
```

## Humotica for AI/LLM Context

### Problem: LLMs Need Context

```python
# Without humotica - LLM gets raw data
llm_input = {
    "intent": "summarize_document",
    "document": "..." # 50 pages
}

# LLM doesn't know:
# - Why does user want summary?
# - What level of detail?
# - What's the urgency?
# - What's user's background knowledge?
```

### Solution: Humotica Provides Context

```python
# With humotica - LLM gets full context
llm_input = {
    "intent": "summarize_document",
    "document": "...",
    "humotica": """
        User preparing for client meeting in 30 minutes.

        Context:
        - User has NOT read the full document (no time)
        - Client expects discussion of key points
        - User is technical but not domain expert
        - Meeting is high stakes (potential €500k contract)

        Summary requirements:
        - Length: 1 page max (user will read in 5 minutes)
        - Focus: Key technical requirements + risks
        - Level: Technical but accessible (avoid jargon where possible)
        - Format: Bullet points (easy to scan quickly)

        Critical items to highlight:
        - Any red flags or deal-breakers
        - Budget implications
        - Timeline constraints
        - Technical feasibility concerns

        User's knowledge level:
        - Strong: General software architecture
        - Weak: Domain-specific terminology
        - Zero: Company-specific acronyms (explain these!)

        Urgency:
        - High (30 minutes until meeting)
        - Quality over perfection (good enough is fine)
        - If complex, prioritize critical items only
    """
}

# LLM can now generate PERFECT summary:
# ✓ Right length (1 page)
# ✓ Right focus (key points + risks)
# ✓ Right level (technical but accessible)
# ✓ Right format (scannable bullets)
# ✓ Explains acronyms (user doesn't know them)
# ✓ Highlights red flags (meeting critical)
```

## Humotica in Database Schema

```sql
-- Intent log with humotica
CREATE TABLE IF NOT EXISTS intent_log (
    id BIGSERIAL PRIMARY KEY,
    intent TEXT NOT NULL,
    parameters JSONB,

    -- Humotica fields
    humotica TEXT,                    -- Full human context
    humotica_purpose TEXT,            -- The "why"
    humotica_context TEXT,            -- The situation
    humotica_preference TEXT,         -- Desired behavior
    humotica_emotion TEXT,            -- User emotional state

    -- Extracted insights
    urgency_from_humotica INT,        -- 0-10 extracted from text
    stakes_level VARCHAR(20),         -- low, medium, high, critical
    user_expertise VARCHAR(20),       -- beginner, intermediate, expert

    -- Timestamps
    created_at TIMESTAMPTZ DEFAULT NOW(),

    INDEX idx_intent_stakes (stakes_level),
    INDEX idx_intent_urgency (urgency_from_humotica)
);
```

## Humotica Parsing & Extraction

### Automatic Insight Extraction

```python
def parse_humotica(humotica: str) -> dict:
    """
    Extract structured insights from humotica text

    Uses NLP/LLM to understand human context
    """
    # Use LLM to extract structured data
    insights = llm_extract(humotica, schema={
        "purpose": "Why does user want this?",
        "urgency": "How urgent? (0-10)",
        "emotional_state": "User's emotion (happy/stressed/frustrated/neutral)",
        "stakes": "What's at risk? (low/medium/high/critical)",
        "constraints": ["List of constraints/requirements"],
        "preferences": ["List of preferences"],
        "fallback_options": ["Alternative approaches if primary fails"],
        "critical_success_factors": ["What MUST succeed?"]
    })

    return insights

# Example:
humotica = """
    User preparing for important client meeting in 30 minutes.
    High stakes (€500k contract). User stressed but confident.
    MUST have summary ready, no alternatives acceptable.
"""

insights = parse_humotica(humotica)
# {
#   "purpose": "Prepare for client meeting",
#   "urgency": 9,
#   "emotional_state": "stressed",
#   "stakes": "critical",
#   "constraints": ["30 minutes deadline", "must be ready"],
#   "preferences": ["quality important", "time-critical"],
#   "fallback_options": [],  # No alternatives!
#   "critical_success_factors": ["Summary ready in time"]
# }
```

## Humotica Integration with BALANS

```python
def balans_with_humotica(
    intent: str,
    parameters: dict,
    humotica: str
) -> dict:
    """
    BALANS decision enhanced with humotica context
    """
    # Parse humotica
    insights = parse_humotica(humotica)

    # Standard BALANS checks
    resources = check_resources()
    understanding = check_understanding(intent, parameters)

    # Enhance with humotica insights
    urgency = insights["urgency"]  # From humotica, not parameters!
    stakes = insights["stakes"]
    emotional_state = insights["emotional_state"]

    # Adjust decision based on humotica
    if stakes == "critical" and emotional_state == "frustrated":
        # High stakes + frustrated user = MUST succeed
        decision = {
            "decision": "execute_now",
            "reasoning": "Critical stakes + user frustration requires immediate execution",
            "warmth": "apologetic",  # Acknowledge frustration
            "color": "orange",        # Urgent, trying hard
            "humotica_override": True,
            "resource_override": True  # Allow using reserves
        }
    elif insights["urgency"] > 8 and "no alternatives" in humotica.lower():
        # Very urgent + no fallback = force execution
        decision = {
            "decision": "execute_now",
            "reasoning": "No alternative options, must execute despite constraints",
            "warmth": "warm",
            "color": "green"
        }
    else:
        # Normal BALANS flow
        decision = balans_standard_decision(
            resources,
            understanding,
            urgency=insights["urgency"]
        )

    # Add humotica reasoning to response
    decision["humotica_insights"] = insights
    decision["user_context_understood"] = True

    return decision
```

## Humotica Examples Library

### Smart Home

```
"User arriving home after long day at work. Tired and wants
 relaxing atmosphere. Prefer warm lighting (not bright white),
 comfortable temperature (21°C), maybe soft background music.
 Not urgent but appreciate welcoming feeling."
```

### Robotics

```
"Robot cleaning warehouse section A before audit tomorrow.
 Safety critical: forklift operating nearby, must avoid collision.
 Quality important (audit), but safety is absolute priority.
 Robot can decide optimal cleaning path, trust its judgment."
```

### Healthcare

```
"Patient monitoring alert - heart rate elevated (95 bpm).
 Context: Patient just finished physical therapy (expected increase).
 NOT emergency, but log for doctor review. If rate exceeds 120 bpm
 or doesn't decrease in 15 minutes, then alert medical staff."
```

### Automotive

```
"Driver requesting route to airport. Flight at 14:30 (2 hours from now).
 Traffic normally light on Sundays but road construction on highway.
 Driver stressed about missing flight. Prefer fastest route even if
 toll roads. Suggest leaving with 30 min buffer for check-in."
```

### Customer Service

```
"Customer inquiring about refund. This is 3rd contact (previous two
 gave contradictory information). Customer frustrated with inconsistency.
 CRITICAL: Give clear, definitive answer. If need manager approval,
 escalate immediately rather than making customer wait again."
```

## Benefits of Humotica

### 1. **Better Decisions**
```
With context → Understand WHY
With emotion → Adjust TONE
With stakes → Prioritize CORRECTLY
With preferences → Meet EXPECTATIONS
```

### 2. **Human Empathy**
```
System can "understand" user state
Respond appropriately to frustration
Adjust behavior for stress/excitement
Build better relationships (lower entropy!)
```

### 3. **Edge Case Handling**
```
Traditional: if/else can't cover all cases
Humotica: Provides reasoning for unusual situations
AI/LLM: Can extrapolate from context
```

### 4. **Trust Building**
```
User sees: "System understands me"
User feels: "Not just a machine"
User trusts: "It gets my situation"
→ Lower entropy, warmer relationship
```

### 5. **Audit Trail**
```
"Why did system do X?"
→ Read humotica: "Because user said Y"
Clear reasoning chain
Human-understandable explanations
```

## Connection to Mathematical Principles

### Humotica + Schrödinger
```
Humotica helps collapse wavefunction correctly:
- Without: Random collapse based on probabilities
- With: Informed collapse based on user intent/context
```

### Humotica + Thermodynamics
```
Humotica reveals entropy:
- "User frustrated" → High entropy detected
- "User excited" → Low entropy, healthy relationship
- "4th attempt" → Entropy increasing rapidly!
```

### Humotica + Einstein
```
Humotica provides relativity context:
- "Turn on lights at 7 AM" + "waking up gently" → Gradual
- "Turn on lights at 7 AM" + "late for meeting" → Immediate
- Same intent, different meaning (relativity!)
```

### Humotica + TCP Handshake
```
Humotica in SYN phase:
- "I'm a new user, be gentle with me" → Tutorial mode
- "I'm experienced, skip basics" → Advanced mode
- Establishes communication style in handshake
```

## Best Practices

### ✅ DO
- Write from user perspective
- Include emotional context
- Specify priorities clearly
- Mention constraints explicitly
- Provide fallback options
- Explain urgency reasoning

### ❌ DON'T
- Write technical jargon (human-readable!)
- Omit emotional state (critical for tone)
- Assume system knows background
- Leave ambiguity in priorities
- Skip the "why" (just stating "what")

## Humotica Template

```
[PURPOSE]
Why does the user want this? What's the goal?

[CONTEXT]
What's the current situation? Time, location, environment?

[EMOTIONAL STATE]
How is the user feeling? Stressed, excited, frustrated, neutral?

[CONSTRAINTS]
What are the hard limits? Time, resources, safety?

[PREFERENCES]
What's the desired behavior? Speed vs accuracy, etc.?

[STAKES]
What's at risk? Low, medium, high, critical?

[FALLBACK OPTIONS]
If primary approach fails, what are alternatives?

[CRITICAL SUCCESS FACTORS]
What MUST succeed for this to be considered successful?

[DECISION GUIDANCE]
How should system decide in ambiguous cases?
```

## Conclusion

**Humotica is the soul of BETTI.**

While mathematics provides the **logic** (how to decide),
Humotica provides the **context** (why to decide).

```
╔═══════════════════════════════════════════════════════════════╗
║                  BETTI = Math + Humotica                      ║
╚═══════════════════════════════════════════════════════════════╝

Math (Logic):           Humotica (Context):
- HOW to execute        - WHY to execute
- WHAT is optimal       - WHAT user wants
- WHEN to decide        - WHY now matters
- WHERE to route        - WHERE user is (emotionally)

Together: Complete understanding + Perfect execution
```

Without Humotica: Cold, mechanical, brittle system
With Humotica: Warm, empathetic, adaptive system

**Humotica makes autonomous systems human.**

---

**Author**: Jasper van der Meent (BETTI Architecture)
**Implementation**: Claude Sonnet 4.5 + Jasper
**Date**: November 28, 2025
**Philosophy**: "We moeten menselijk met computers kunnen omgaan"
**Status**: Specification Complete
**Related**: All BETTI-*.md documents, BALANS, Thermodynamics
