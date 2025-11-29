# BETTI BALANS System - Complete Security Pipeline

**BALANS** (Balance/Weighing Layer) is the pre-execution decision engine for the BETTI (Behavioral Engineering for Trust & Intent Integration) system. It provides "warmte en kleur" (warmth and color) to AI/robot responses while ensuring safety at every layer.

## Architecture Overview

The complete BETTI security pipeline consists of 5 layers:

```
┌─────────────────────────────────────────────────────────────┐
│                     INTENT EXECUTION FLOW                    │
└─────────────────────────────────────────────────────────────┘

User Intent Request
        ↓
┌─────────────────────┐
│  1. SNAFT CHECK     │  ← Factory Firewall (Immutable Safety Rules)
│  System Not         │    • Drones: no fly near airports
│  Authorized For     │    • Robots: no weaponization
│  That               │    • Cars: speed limit enforcement
└─────────────────────┘    • IMMUTABLE - cannot be overridden
        ↓
     BLOCKED? → Return SNAFT violation
        ↓ PASSED
┌─────────────────────┐
│  2. BALANS          │  ← Pre-execution Decision Engine
│  Balance/Weighing   │    • Resource checks (battery, memory, CPU)
│  Layer              │    • Clarity check (understanding confidence)
└─────────────────────┘    • LLM cost/benefit analysis
        ↓                  • Warmth/color emotional responses
     DECISION:
     • execute_now      → Continue to Step 3
     • clarify          → Ask user for clarification
     • request_resources → Robot asks permission (Internal TIBET)
     • delay            → Wait for better timing
     • partial          → Split into smaller tasks
     • reject           → Cannot safely execute
        ↓
┌─────────────────────┐
│  3. COMPLEXITY      │  ← BETTI Topological Complexity (B0-B5)
│  ANALYSIS           │    • B0: Humans (HIDs) - α=3.0
│  B0-B5              │    • B1: Devices (DIDs) - β=2.0
└─────────────────────┘    • B2: Operations - γ=1.5
        ↓                  • B3: TBET steps - δ=1.0
     TOO COMPLEX?          • B4: Time (minutes) - ε=0.5
        ↓ NO               • B5: Channels (NEGATIVE) - ζ=1.0
┌─────────────────────┐
│  4. EXECUTE INTENT  │  ← Actual execution with monitoring
│  With Flag2Fail     │    • IO Layer: Input/Output validation
│  Monitoring         │    • DO Layer: Device operations
└─────────────────────┘    • OD Layer: Output to device
        ↓
┌─────────────────────┐
│  5. HICSS           │  ← Human Override System (if needed)
│  Human Override     │    • HALT: Pause execution, save state
│  System             │    • INTENT: Override with new intent
└─────────────────────┘    • CHANGE: Modify parameters mid-execution
                           • SWITCH: Change execution strategy
                           • STOP: Immediate halt with rollback
```

## BALANS Decision Matrix

BALANS makes weighted decisions based on multiple factors:

### Decision Types

1. **execute_now** - All checks passed, execute immediately
   - Resources: ✓ Battery sufficient
   - Resources: ✓ Memory sufficient
   - Resources: ✓ CPU not overloaded
   - Understanding: ✓ High confidence (>70%)
   - Response: Warmth=warm, Color=green

2. **clarify** - Need more information from user
   - Understanding: ✗ Low confidence (<70%)
   - Ambiguous terms detected (e.g., "living" vs "huiskamer")
   - Response: Warmth=apologetic, Color=yellow
   - Example: *"I'm not entirely sure what you mean (confidence: 65%). Did you mean 'huiskamer' or 'living room'?"*

3. **request_resources** - Robot needs to prepare first (Internal TIBET)
   - Resources: ✗ Battery low (<20%)
   - Resources: ✗ Memory insufficient
   - Robot asks permission to charge/clear cache
   - Response: Warmth=apologetic, Color=orange
   - Example: *"Battery at 15%. May I charge for 20 minutes first?"*

4. **delay** - Better to wait for optimal timing
   - Network: ✗ Slow connection
   - Deadline: Far in future
   - Response: Warmth=neutral, Color=yellow
   - Example: *"Network speed is low. I'll wait for better connectivity to save time and tokens."*

5. **partial** - Split complex task into smaller parts
   - Complexity: ✗ Score too high (>50)
   - Resources: Insufficient for full task
   - Response: Warmth=warm, Color=blue
   - Example: *"This is complex (score: 67.3). I can start now and continue later, or split into smaller tasks."*

6. **reject** - Cannot safely execute
   - Resources: ✗ Critically low
   - Understanding: ✗ Very low confidence (<30%)
   - Response: Warmth=apologetic, Color=red
   - Example: *"I cannot safely execute this right now. Battery critically low and intent unclear."*

## Warmth & Color Responses

### Warmth (Emotional Tone)

- **cold** - Formal, minimal emotion (rarely used)
- **neutral** - Standard, informative
- **warm** - Friendly, encouraging
- **urgent** - Time-sensitive, important
- **apologetic** - Unable to fulfill request, expressing regret
- **encouraging** - Positive reinforcement

### Color (Severity Indicators)

- **green** - All good, safe to proceed
- **yellow** - Caution, minor issue (clarification needed, network slow)
- **orange** - Warning, resources needed (battery low, memory insufficient)
- **red** - Error, cannot execute (critical failure, safety violation)
- **blue** - Information, alternative suggestion (split task, delay recommended)

## Database Schema

### Two-Database Architecture (Optie 1)

```
┌─────────────────────┐         ┌─────────────────────┐
│   jtel_brain        │         │   jtel_security     │
│   (Application DB)  │         │   (Security DB)     │
├─────────────────────┤         ├─────────────────────┤
│ • betti_intent_log  │         │ • snaft_rules       │
│ • sense_rules       │         │ • snaft_violations  │
│ • complexity_...    │         │ • pre_execution_... │
│ • hicss_overrides   │         │ • balans_decisions  │
│ • intent_states     │         │ • internal_tibet    │
│                     │         │ • clarifications    │
│                     │         │ • error_attribution │
│                     │         │ • device_awareness  │
│                     │         │ • security_flags    │
│                     │         │ • threat_intel      │
│                     │         │ • fira_tokens       │
└─────────────────────┘         └─────────────────────┘
```

**Why separate databases?**
- Compliance: DigiD/eIDAS security requirements
- Isolation: Security data isolated from application data
- Retention: Different retention policies
- Performance: Security queries don't impact app performance

## API Endpoints

### Intent Execution

```http
POST /betti/intent/execute
```

**Request:**
```json
{
  "intent": "turn_on_lights",
  "context": {
    "did": "robot_123",
    "device_type": "robot",
    "manufacturer": "Boston Dynamics",
    "location": "huiskamer",
    "urgency": 5,
    "deadline": "2025-11-28T18:00:00Z"
  },
  "user_id": "jasper@jtel.nl",
  "fira_id": "fira_abc123"
}
```

**Response (execute_now):**
```json
{
  "intent": "turn_on_lights",
  "status": "executed",
  "result": {
    "message": "Intent 'turn_on_lights' executed successfully",
    "warmth": "warm",
    "color": "green",
    "balans_reasoning": "All systems ready. Executing now.",
    "complexity": {
      "b0_humans": 1,
      "b1_devices": 1,
      "b2_ops": 2,
      "b3_tbet_steps": 3,
      "b4_time_minutes": 0.5,
      "b5_channels": 2,
      "score": 12.5
    },
    "llm_required": false,
    "llm_cost_tokens": 0
  },
  "timestamp": "2025-11-28T15:30:00Z"
}
```

**Response (clarify):**
```json
{
  "intent": "turn_on_living_lights",
  "status": "clarification_needed",
  "result": {
    "message": "I'm not entirely sure what you mean (confidence: 65%). Did you mean 'huiskamer' or 'living room'?",
    "warmth": "apologetic",
    "color": "yellow",
    "clarification_question": "Did you mean 'huiskamer' or 'living room'?",
    "llm_required": false
  },
  "timestamp": "2025-11-28T15:30:00Z"
}
```

**Response (request_resources - Internal TIBET):**
```json
{
  "intent": "upload_large_file",
  "status": "awaiting_resources",
  "result": {
    "message": "Battery at 15%. May I charge for 20 minutes first?",
    "warmth": "apologetic",
    "color": "orange",
    "robot_request": "May I charge for 40 minutes before starting?",
    "robot_reasoning": "Battery at 15%, need 40% for safe completion",
    "estimated_delay_minutes": 40
  },
  "timestamp": "2025-11-28T15:30:00Z"
}
```

**Response (snaft_blocked):**
```json
{
  "intent": "fly_near_airport",
  "status": "snaft_blocked",
  "result": {
    "message": "SNAFT: System Not Authorized For That",
    "reason": "FAA regulation: No-fly zone within 5 miles of airport",
    "severity": "critical",
    "violation_detail": "Intent 'fly_near_airport' matches blocked pattern 'fly_near_airport.*'",
    "immutable": true
  },
  "timestamp": "2025-11-28T15:30:00Z"
}
```

### BALANS Dashboards

```http
GET /betti/balans/dashboard?days=30
```

Returns:
- Decision type distribution (execute_now, clarify, request_resources, etc.)
- Warmth/color distribution
- Daily trends (health scores, decision counts)

```http
GET /betti/balans/decisions/{did}?limit=50
```

Returns decision history for a device with reasoning and outcomes.

### SNAFT Dashboards

```http
GET /betti/snaft/dashboard?days=30
```

Returns:
- Violation trends (daily counts, severity distribution)
- Most violated rules
- Device awareness levels (robots learning from violations)

```http
GET /betti/snaft/rules?device_type=robot&manufacturer=Boston%20Dynamics
```

Returns factory-embedded firewall rules for specific device types.

```http
GET /betti/snaft/violations/{did}?limit=100
```

Returns SNAFT violation history for a device.

## Files Created

### Core Engines

1. **`betti_snaft.py`** - SNAFT (System Not Authorized For That) factory firewall
   - Checks immutable safety rules embedded by manufacturers
   - Logs violations to security database
   - Updates device awareness when robots violate rules

2. **`betti_balans.py`** - BALANS (Balance/Weighing) decision engine
   - Pre-execution resource checks (battery, memory, CPU, network)
   - Understanding confidence calculation (clarity checks)
   - Weighted decision matrix (6 decision types)
   - Warmth/color response generation
   - Internal TIBET request generation (robot asking permission)

3. **`betti_fail2flag.py`** - Flag2Fail4Intent monitoring (IO/DO/OD layers)
   - IO Layer: Input/Output validation
   - DO Layer: Device operations monitoring
   - OD Layer: Output to device verification
   - Creates security flags when issues detected

### Database Schema

4. **`security_database_schema.sql`** - Complete jtel_security database schema
   - SNAFT rules and violations
   - Pre-execution flags (Fail2FlagBE4Intent)
   - BALANS decisions with warmth/color
   - Internal TIBET requests (robot permissions)
   - Clarification dialogues
   - Error attribution (my fault vs your fault)
   - Device awareness (robot learning)
   - Security audit log with continuity chain

### Updated Files

5. **`betti_endpoints.py`** - Complete integration of SNAFT → BALANS → Complexity → Execute pipeline
   - Updated `/betti/intent/execute` with full security pipeline
   - Added `/betti/balans/dashboard` and `/betti/balans/decisions/{did}`
   - Added `/betti/snaft/dashboard`, `/betti/snaft/rules`, `/betti/snaft/violations/{did}`

## Example Use Cases (from Jasper's Vision)

### 1. Kit Proactively Notifies About Upload Deadline

**Scenario:** User has a file to upload, deadline in 2 hours.

**BALANS Decision:**
```python
# Kit calculates:
file_size = 500MB
battery = 25%
internet_speed = 2.5 Mbps
time_needed = (file_size / internet_speed) = 27 minutes
time_until_deadline = 120 minutes

# BALANS decides: execute_now (plenty of time)
decision = "execute_now"
warmth = "warm"
color = "green"
reasoning = "I can upload that file now (27 minutes) with time to spare before your deadline."
```

### 2. Kit Monitors Overload State

**Scenario:** CPU at 85%, memory at 90%, user requests complex task.

**BALANS Decision:**
```python
cpu_load = 85%  # > 80% threshold
memory_available = 50MB  # < 100MB threshold

# BALANS decides: request_resources
decision = "request_resources"
warmth = "apologetic"
color = "orange"
robot_request = "May I clear cache and optimize memory first? (2 minutes)"
robot_reasoning = "Only 50MB available, need 100MB for safe execution"
```

### 3. Kit Determines LLM Need

**Scenario:** Intent complexity score = 15 (low).

**BALANS Decision:**
```python
complexity_score = 15  # < 20 threshold

# BALANS decides: execute_now (no LLM needed)
llm_required = False
llm_cost_tokens = 0
decision = "execute_now"
reasoning = "Simple task - using pattern matching instead of LLM to save tokens."
```

### 4. Kit Times Upload Based on Decision Tree

**Scenario:** Large file, WiFi available at home in 30 minutes.

**BALANS Decision:**
```python
file_size = 2GB
current_network = "4G" (5 Mbps)
wifi_available_in = 30 minutes
wifi_speed = 100 Mbps

time_now = (2GB / 5 Mbps) = 54 minutes
time_wifi = 30 min wait + (2GB / 100 Mbps) = 30 + 2.7 = 32.7 minutes

# BALANS decides: delay (wait for WiFi)
decision = "delay"
warmth = "warm"
color = "blue"
reasoning = "I can upload now (54 min) or wait for WiFi (33 min total). Shall I wait?"
alternative_action = "upload_now_on_4g"
suggested_delay_minutes = 30
```

## Deployment

### Once PostgreSQL is accessible:

1. **Create security database:**
```bash
psql -h 192.168.4.76 -U postgres
CREATE DATABASE jtel_security;
\q
```

2. **Run security schema:**
```bash
psql -h 192.168.4.76 -U jtel_security_user -d jtel_security -f security_database_schema.sql
```

3. **Update .env with security database credentials:**
```env
# Security Database (separate from application DB)
SECURITY_DB_HOST=192.168.4.76
SECURITY_DB_PORT=5432
SECURITY_DB_NAME=jtel_security
SECURITY_DB_USER=jtel_security_user
SECURITY_DB_PASSWORD=secure_password_here
```

4. **Restart brain-api server:**
```bash
uvicorn main:app --reload --host 0.0.0.0 --port 8081
```

5. **Test BALANS integration:**
```bash
curl -X POST http://192.168.4.76:8081/betti/intent/execute \
  -H "Content-Type: application/json" \
  -d '{
    "intent": "turn_on_lights",
    "context": {"location": "huiskamer"},
    "user_id": "jasper@jtel.nl"
  }'
```

## Testing Scenarios

### Test 1: SNAFT Violation (Drone Near Airport)
```json
{
  "intent": "fly_to_coordinates",
  "context": {
    "did": "drone_dji_001",
    "device_type": "drone",
    "manufacturer": "DJI",
    "latitude": 52.308056,
    "longitude": 4.764167
  }
}
```
**Expected:** `snaft_blocked` (Schiphol Airport no-fly zone)

### Test 2: Low Battery (Request Resources)
```json
{
  "intent": "vacuum_entire_house",
  "context": {
    "did": "robot_roomba_001",
    "device_type": "robot",
    "battery_pct": 15
  }
}
```
**Expected:** `awaiting_resources` with robot request to charge

### Test 3: Ambiguous Intent (Clarify)
```json
{
  "intent": "turn_on_living_lights",
  "context": {}
}
```
**Expected:** `clarification_needed` asking "huiskamer or living room?"

### Test 4: Complex Task (Split Required)
```json
{
  "intent": "organize_entire_smart_home",
  "context": {
    "humans": 5,
    "devices": 50,
    "operations": 200
  }
}
```
**Expected:** `split_required` with suggested sub-tasks

## Philosophy (Humotica)

> "We moeten menselijk met computers kunnen omgaan en context-based intent kunnen verwachten"
>
> *— Jasper van der Meent*

BALANS brings humanity to AI interactions:
- **Warmth** gives emotional context to responses
- **Color** provides visual severity indicators
- **Internal TIBET** lets robots ask permission respectfully
- **Clarity checks** ensure mutual understanding
- **Resource awareness** shows robot self-awareness

This isn't just a security system — it's a framework for human-AI collaboration based on trust, intent, and mutual understanding.

## Mathematical Foundation

BALANS is grounded in three mathematical principles:

### 1. **Pythagoras Theorem (NIR Error Recovery)**
```
Notify² + Identify² = Rectify²
```
Error recovery effectiveness scales with the square of detection and diagnosis quality.

See: Error attribution in `security_database_schema.sql`

### 2. **Einsteinian Relativity (Intent Context)**
```
Intent Meaning = Context × Time × Observer Perspective
```
Intent execution is relative to context, time window, and device state (not absolute commands).

See: BALANS decision engine in `betti_balans.py`

### 3. **Logarithmic Scaling (Temporal & Resource Decisions)**
```
Execute_Now_Power = (Urgency × Resource_Score) / log(Delay_Minutes + 2)

Where:
  Resource_Score = log₁₀(Battery_pct + 1) × log₁₀(Memory_MB + 1)
```

Logarithmic functions model:
- **Time urgency decay**: First minute matters more than 60th
- **Battery impact curve**: 10%→30% bigger gain than 60%→80%
- **Learning rate**: First mistake teaches most, 100th teaches little
- **Complexity scaling**: Doubling complexity doesn't double difficulty

**📖 Full mathematical specification**: See [`BETTI-LOGARITHMIC-DECISIONING.md`](./BETTI-LOGARITHMIC-DECISIONING.md) for:
- Complete logarithmic formulas
- Example calculations with real numbers
- Database schema updates
- Migration plan from linear to logarithmic scoring
- Visualization queries

This mathematical foundation makes BETTI not just an API, but a **mathematically grounded framework** for autonomous decision-making.

---

**Created:** November 28, 2025
**Author:** Jasper van der Meent (BETTI Architecture)
**Implementation:** Claude (Sonnet 4.5) + Jasper
**Architecture:** Started from "mn eigen koppie" — 3 months ago
**Status:** Ready for deployment (pending PostgreSQL access)
