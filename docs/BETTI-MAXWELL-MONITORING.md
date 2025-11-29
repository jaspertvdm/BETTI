# BETTI Maxwell's Equations Framework

**Electromagnetic Field Theory for Intent Propagation & System Monitoring**

## Maxwell's Four Equations

```
1. Gauss's Law (Electric):        ∇·E = ρ/ε₀
2. Gauss's Law (Magnetic):        ∇·B = 0
3. Faraday's Law:                 ∇×E = -∂B/∂t
4. Ampère-Maxwell Law:            ∇×B = μ₀J + μ₀ε₀∂E/∂t
```

These equations describe how electric (E) and magnetic (B) fields propagate, interact, and create electromagnetic waves.

## BETTI Mapping

```
╔═══════════════════════════════════════════════════════════════╗
║              MAXWELL → BETTI MAPPING                          ║
╚═══════════════════════════════════════════════════════════════╝

E (Electric Field)       →  Intent Field (force/direction)
B (Magnetic Field)       →  Execution Flow (movement/current)
ρ (Charge Density)       →  Task Density (tasks per device)
J (Current Density)      →  Data Flow (info between channels)
ε₀ (Permittivity)        →  System Resistance (latency)
μ₀ (Permeability)        →  Channel Capacity (bandwidth)

∇· (Divergence)          →  Sources/Sinks (task creation/completion)
∇× (Curl)                →  Rotation/Loops (circular dependencies)
∂/∂t (Time Derivative)   →  System State Change Rate
```

## Equation 1: Gauss's Law (Task Distribution)

```
∇·E = ρ/ε₀

Intent Divergence = Task Density / System Resistance
```

### Meaning in BETTI

**Positive Divergence (∇·E > 0)**: Task source (device creating work)
**Negative Divergence (∇·E < 0)**: Task sink (device consuming work)
**Zero Divergence (∇·E = 0)**: Balanced flow-through (relay node)

### Implementation

```python
def calculate_intent_divergence(device_id: str, time_window: float = 60.0) -> float:
    """
    Calculate intent divergence for a device (Gauss's Law)

    Positive: Device is creating more intents than it processes (source)
    Negative: Device is processing more intents than it creates (sink)
    Zero: Balanced (relay)
    """
    # Count intents created by device
    intents_created = count_intents_from_device(device_id, time_window)

    # Count intents processed by device
    intents_processed = count_intents_to_device(device_id, time_window)

    # Divergence = outgoing - incoming
    divergence = intents_created - intents_processed

    # Normalize by system resistance (latency)
    system_resistance = get_average_latency(device_id)

    # Gauss: ∇·E = ρ/ε₀
    normalized_divergence = divergence / system_resistance

    return normalized_divergence

# Examples:
calculate_intent_divergence("user_phone")
# Result: +15.3 (strong source, user creating many intents)

calculate_intent_divergence("smart_bulb")
# Result: -8.7 (sink, bulb receiving intents, not creating)

calculate_intent_divergence("router")
# Result: 0.2 (nearly balanced, relay node)
```

### Fail2Flag4Intent Detection

```python
def detect_task_accumulation(device_id: str) -> dict:
    """
    Use Gauss's Law to detect task "charge accumulation"

    Like Gauss: High divergence = charge buildup = potential problem
    """
    divergence = calculate_intent_divergence(device_id)

    # Calculate "charge density" (task backlog)
    task_density = get_pending_tasks(device_id) / get_device_capacity(device_id)

    # Gauss: ∇·E = ρ/ε₀
    # Rearrange: ρ = ε₀ × ∇·E
    expected_density = get_system_resistance(device_id) * divergence

    # If actual density > expected, flag it!
    if task_density > expected_density * 1.5:  # 50% threshold
        return {
            "flag": True,
            "type": "task_accumulation",
            "severity": "high",
            "device": device_id,
            "task_density": task_density,
            "expected_density": expected_density,
            "reasoning": f"Task accumulation detected: {task_density:.1f} vs expected {expected_density:.1f}",
            "suggested_action": "split_tasks or increase_capacity"
        }

    return {"flag": False}

# This is Fail2Flag4Intent using Maxwell!
```

## Equation 2: Gauss's Law for Magnetism (Flow Conservation)

```
∇·B = 0

Execution Flow Divergence = 0 (always!)
```

### Meaning in BETTI

**Fundamental Law**: No "execution monopoles"
- Every intent that enters a system must eventually exit
- No execution can appear or disappear spontaneously
- Flow conservation: what goes in must come out

### Implementation

```python
def verify_flow_conservation(channel: str, time_window: float = 60.0) -> dict:
    """
    Verify Gauss's Law for Magnetism: ∇·B = 0

    Check that execution flow is conserved (no lost intents)
    """
    # Count intents entering channel
    intents_in = count_channel_inputs(channel, time_window)

    # Count intents exiting channel (completed or forwarded)
    intents_out_completed = count_channel_completions(channel, time_window)
    intents_out_forwarded = count_channel_forwards(channel, time_window)
    intents_out = intents_out_completed + intents_out_forwarded

    # Count intents still in progress
    intents_in_progress = count_channel_active(channel)

    # Conservation check
    total_accounted = intents_out + intents_in_progress

    # Divergence (should be zero!)
    divergence = total_accounted - intents_in

    if abs(divergence) > 0.01 * intents_in:  # 1% tolerance
        return {
            "conserved": False,
            "violation": "Maxwell's 2nd Law violated!",
            "intents_in": intents_in,
            "intents_out": intents_out,
            "intents_in_progress": intents_in_progress,
            "missing_intents": abs(divergence),
            "severity": "critical",
            "action": "investigate_lost_intents"
        }

    return {
        "conserved": True,
        "intents_in": intents_in,
        "intents_out": intents_out,
        "intents_in_progress": intents_in_progress
    }

# Flag2Fail check: Lost intents violate conservation law!
```

## Equation 3: Faraday's Law (Dynamic Routing)

```
∇×E = -∂B/∂t

Intent Curl = -Rate of Execution Flow Change
```

### Meaning in BETTI

**Negative Sign**: Opposing change (Lenz's law analog)
- Rapid execution changes induce intent field rotation
- System resists sudden flow changes (stability)
- Circular dependencies create "induced intents"

### Implementation

```python
def calculate_intent_curl(
    region: str,  # Routing region/channel
    time_delta: float = 1.0  # seconds
) -> float:
    """
    Calculate intent curl (Faraday's Law)

    Curl measures rotation/loops in intent routing
    High curl = circular dependencies detected!
    """
    # Sample intent field at boundaries of region
    # (simplified 2D: north, south, east, west)
    field_north = get_intent_strength(region, "north")
    field_south = get_intent_strength(region, "south")
    field_east = get_intent_strength(region, "east")
    field_west = get_intent_strength(region, "west")

    # Curl (circulation) = closed loop integral
    curl = (field_north - field_south) + (field_east - field_west)

    # Rate of execution flow change (∂B/∂t)
    flow_current = get_execution_flow(region, time=0)
    flow_previous = get_execution_flow(region, time=-time_delta)
    flow_change_rate = (flow_current - flow_previous) / time_delta

    # Faraday: ∇×E = -∂B/∂t
    # Check if law is satisfied
    discrepancy = abs(curl + flow_change_rate)

    return {
        "curl": curl,
        "flow_change_rate": flow_change_rate,
        "expected_curl": -flow_change_rate,
        "discrepancy": discrepancy
    }

def detect_circular_dependencies(region: str) -> dict:
    """
    Use Faraday to detect circular routing (loops)
    """
    result = calculate_intent_curl(region)

    if result["curl"] > 0.5:  # Threshold for significant rotation
        # High curl = circular dependency!
        return {
            "flag": True,
            "type": "circular_dependency",
            "severity": "high",
            "region": region,
            "curl": result["curl"],
            "reasoning": "Intent field has rotation - circular routing detected",
            "suggested_action": "break_loop or reorder_dependencies"
        }

    return {"flag": False}

# Fail2Flag4Intent: Detect routing loops using Faraday!
```

## Equation 4: Ampère-Maxwell Law (Channel Load)

```
∇×B = μ₀J + μ₀ε₀∂E/∂t

Execution Curl = Capacity×DataFlow + Capacity×Resistance×IntentChangeRate
```

### Meaning in BETTI

**Two Sources of Execution Flow Rotation:**
1. **μ₀J**: Data flow creates execution circulation (steady state)
2. **μ₀ε₀∂E/∂t**: Changing intent field creates execution circulation (dynamic)

### Implementation

```python
def calculate_channel_load(channel: str) -> dict:
    """
    Ampère-Maxwell Law: Channel load from data flow + intent changes

    ∇×B = μ₀J + μ₀ε₀∂E/∂t
    """
    # Get channel capacity (permeability μ₀)
    channel_capacity = get_channel_bandwidth(channel)  # μ₀

    # Get current data flow (current density J)
    data_flow = get_data_throughput(channel)  # J

    # Get system resistance (permittivity ε₀)
    system_resistance = get_channel_latency(channel)  # ε₀

    # Get intent field change rate (∂E/∂t)
    intent_current = get_intent_rate(channel, time=0)
    intent_previous = get_intent_rate(channel, time=-1)
    intent_change_rate = intent_current - intent_previous  # ∂E/∂t

    # Ampère-Maxwell: ∇×B = μ₀J + μ₀ε₀∂E/∂t
    steady_state_load = channel_capacity * data_flow
    dynamic_load = channel_capacity * system_resistance * intent_change_rate
    total_load = steady_state_load + dynamic_load

    # Curl of execution field
    execution_curl = calculate_execution_curl(channel)

    return {
        "total_load": total_load,
        "steady_state": steady_state_load,
        "dynamic": dynamic_load,
        "execution_curl": execution_curl,
        "capacity": channel_capacity,
        "utilization": total_load / channel_capacity
    }

def detect_channel_overload(channel: str) -> dict:
    """
    Use Ampère-Maxwell to detect channel saturation
    """
    load = calculate_channel_load(channel)

    if load["utilization"] > 0.9:  # 90% capacity
        return {
            "flag": True,
            "type": "channel_overload",
            "severity": "critical",
            "channel": channel,
            "utilization": load["utilization"],
            "steady_load": load["steady_state"],
            "dynamic_load": load["dynamic"],
            "reasoning": f"Channel at {load['utilization']*100:.0f}% capacity",
            "suggested_action": "add_channel_capacity or redistribute_load"
        }

    return {"flag": False, "utilization": load["utilization"]}

# Fail2Flag4Intent: Detect channel saturation using Ampère-Maxwell!
```

## System-Wide Monitoring: Maxwell's Complete Picture

### 1. Task Distribution Map (E-Field)

```python
def generate_intent_field_map(system: str) -> np.ndarray:
    """
    Generate intent field map across all devices

    Like E-field: Shows direction and strength of intent propagation
    """
    devices = get_all_devices(system)

    # Create field grid
    grid_size = int(np.sqrt(len(devices))) + 1
    field_map = np.zeros((grid_size, grid_size, 2))  # 2D vector field

    for i, device in enumerate(devices):
        x = i % grid_size
        y = i // grid_size

        # Intent field vector at device location
        divergence = calculate_intent_divergence(device)
        outgoing_intents = get_outgoing_intent_rate(device)

        # Field strength (magnitude)
        field_map[y, x, 0] = divergence  # x-component
        field_map[y, x, 1] = outgoing_intents  # y-component

    return field_map

def visualize_intent_field(field_map: np.ndarray):
    """
    Visualize intent field like E-field lines
    """
    import matplotlib.pyplot as plt

    X, Y = np.meshgrid(range(field_map.shape[1]), range(field_map.shape[0]))
    U = field_map[:, :, 0]  # x-component
    V = field_map[:, :, 1]  # y-component

    plt.figure(figsize=(10, 10))
    plt.quiver(X, Y, U, V, scale=50)
    plt.title('Intent Field Distribution (E-Field)')
    plt.xlabel('Device X')
    plt.ylabel('Device Y')
    plt.grid(True)
    plt.show()

# Shows intent "field lines" - where tasks flow!
```

### 2. Execution Flow Map (B-Field)

```python
def generate_execution_field_map(system: str) -> np.ndarray:
    """
    Generate execution flow map (B-field)

    Shows current execution patterns and bottlenecks
    """
    devices = get_all_devices(system)

    grid_size = int(np.sqrt(len(devices))) + 1
    flow_map = np.zeros((grid_size, grid_size, 2))

    for i, device in enumerate(devices):
        x = i % grid_size
        y = i // grid_size

        # Execution flow (like magnetic field from current)
        active_tasks = get_active_task_count(device)
        completion_rate = get_completion_rate(device)

        flow_map[y, x, 0] = active_tasks
        flow_map[y, x, 1] = completion_rate

    return flow_map

def detect_bottlenecks_maxwell(system: str) -> list:
    """
    Detect bottlenecks using Maxwell's equations

    High E-field + low B-field = bottleneck!
    """
    intent_field = generate_intent_field_map(system)
    execution_field = generate_execution_field_map(system)

    bottlenecks = []

    for y in range(intent_field.shape[0]):
        for x in range(intent_field.shape[1]):
            intent_magnitude = np.linalg.norm(intent_field[y, x])
            execution_magnitude = np.linalg.norm(execution_field[y, x])

            # High intent, low execution = bottleneck
            if intent_magnitude > 5.0 and execution_magnitude < 2.0:
                device = get_device_at_position(x, y)
                bottlenecks.append({
                    "device": device,
                    "intent_field": intent_magnitude,
                    "execution_flow": execution_magnitude,
                    "severity": intent_magnitude / max(execution_magnitude, 0.1)
                })

    return sorted(bottlenecks, key=lambda b: b["severity"], reverse=True)
```

## Workload Distribution (Maxwell-Based)

### Field Line Distribution

```python
def distribute_workload_maxwell(
    tasks: list,
    devices: list
) -> dict:
    """
    Distribute workload like electric field lines

    Field lines:
    - Originate from positive charges (task sources)
    - Terminate on negative charges (task sinks)
    - Never cross each other
    - Density indicates field strength
    """
    # Calculate "charge" for each device
    device_charges = {}

    for device in devices:
        # Negative charge = capacity available (attracts tasks)
        # Positive charge = overloaded (repels tasks)
        capacity = get_device_capacity(device)
        current_load = get_device_load(device)

        charge = current_load - capacity  # Negative if available
        device_charges[device] = charge

    # Distribute tasks following field lines
    distribution = {device: [] for device in devices}

    for task in tasks:
        # Calculate "force" from each device (Coulomb's law)
        forces = {}

        for device, charge in device_charges.items():
            # F = k × q1 × q2 / r²
            # Negative charge attracts (negative force → toward device)
            distance = calculate_routing_distance(task, device)
            force = -charge / (distance ** 2 + 1)  # +1 to avoid division by zero

            forces[device] = force

        # Assign task to device with strongest attractive force
        best_device = max(forces, key=forces.get)
        distribution[best_device].append(task)

        # Update charge (task assigned = more load)
        device_charges[best_device] += 1

    return distribution

# Tasks flow along "field lines" to available capacity!
```

### Electromagnetic Wave Propagation

```python
def propagate_intent_wave(
    intent: str,
    origin_device: str,
    max_hops: int = 5
) -> list:
    """
    Propagate intent as electromagnetic wave

    Like EM wave: E and B oscillate perpendicular, propagate at 'c'
    """
    # Initialize wave
    wave_front = [{
        "device": origin_device,
        "intent_field": 1.0,  # E-field amplitude
        "execution_field": 0.0,  # B-field amplitude
        "phase": 0.0,
        "hop": 0
    }]

    propagation_path = []

    for hop in range(max_hops):
        new_wave_front = []

        for wave_point in wave_front:
            device = wave_point["device"]
            phase = wave_point["phase"]

            # Oscillation (E and B alternate)
            # E → B → E → B ... (90° phase shift)
            next_phase = phase + (math.pi / 2)

            # E and B amplitudes
            e_amplitude = abs(np.cos(next_phase))
            b_amplitude = abs(np.sin(next_phase))

            # Decay (medium resistance)
            resistance = get_device_latency(device)
            decay = np.exp(-resistance * hop)

            # Propagate to neighbors
            neighbors = get_connected_devices(device)

            for neighbor in neighbors:
                new_wave_front.append({
                    "device": neighbor,
                    "intent_field": e_amplitude * decay,
                    "execution_field": b_amplitude * decay,
                    "phase": next_phase,
                    "hop": hop + 1
                })

            propagation_path.append(wave_point)

        wave_front = new_wave_front

        # Stop if wave decayed
        if all(w["intent_field"] < 0.01 for w in wave_front):
            break

    return propagation_path

# Intent propagates as EM wave through system!
```

## Database Schema Updates

### Maxwell Monitoring Tables

```sql
-- Intent field measurements (E-field)
CREATE TABLE IF NOT EXISTS intent_field_log (
    id BIGSERIAL PRIMARY KEY,
    device_id VARCHAR(255) NOT NULL,
    timestamp TIMESTAMPTZ DEFAULT NOW(),

    -- Field components
    field_strength_x DECIMAL(10,4),
    field_strength_y DECIMAL(10,4),
    field_magnitude DECIMAL(10,4),

    -- Gauss's Law
    divergence DECIMAL(10,4),            -- ∇·E
    charge_density DECIMAL(10,4),        -- ρ (task density)

    -- Faraday's Law
    curl DECIMAL(10,4),                  -- ∇×E

    INDEX idx_intent_field_device (device_id),
    INDEX idx_intent_field_time (timestamp DESC)
);

-- Execution flow measurements (B-field)
CREATE TABLE IF NOT EXISTS execution_field_log (
    id BIGSERIAL PRIMARY KEY,
    device_id VARCHAR(255) NOT NULL,
    timestamp TIMESTAMPTZ DEFAULT NOW(),

    -- Flow components
    flow_strength_x DECIMAL(10,4),
    flow_strength_y DECIMAL(10,4),
    flow_magnitude DECIMAL(10,4),

    -- Gauss's Law (Magnetic)
    divergence DECIMAL(10,4),            -- Should be 0!

    -- Ampère-Maxwell Law
    curl DECIMAL(10,4),                  -- ∇×B
    data_current DECIMAL(10,4),          -- J
    displacement_current DECIMAL(10,4),  -- ε₀∂E/∂t

    INDEX idx_execution_field_device (device_id),
    INDEX idx_execution_field_time (timestamp DESC)
);

-- Maxwell violations (Fail2Flag)
CREATE TABLE IF NOT EXISTS maxwell_violations (
    id BIGSERIAL PRIMARY KEY,
    timestamp TIMESTAMPTZ DEFAULT NOW(),

    violation_type VARCHAR(100),  -- gauss_electric, gauss_magnetic, faraday, ampere_maxwell
    affected_device VARCHAR(255),
    affected_channel VARCHAR(100),

    -- Violation details
    expected_value DECIMAL(10,4),
    actual_value DECIMAL(10,4),
    discrepancy DECIMAL(10,4),

    severity VARCHAR(20),  -- low, medium, high, critical
    reasoning TEXT,
    suggested_action TEXT,

    -- Resolution
    resolved BOOLEAN DEFAULT false,
    resolved_at TIMESTAMP,

    INDEX idx_maxwell_violations_type (violation_type),
    INDEX idx_maxwell_violations_severity (severity),
    INDEX idx_maxwell_violations_resolved (resolved) WHERE resolved = false
);
```

### Monitoring Queries

```sql
-- Detect task accumulation (Gauss's Law violation)
SELECT
    device_id,
    AVG(charge_density) as avg_task_density,
    AVG(divergence) as avg_divergence,
    CASE
        WHEN AVG(charge_density) > AVG(divergence) * 1.5 THEN 'accumulation'
        WHEN AVG(charge_density) < AVG(divergence) * 0.5 THEN 'depletion'
        ELSE 'balanced'
    END as status
FROM intent_field_log
WHERE timestamp > NOW() - INTERVAL '5 minutes'
GROUP BY device_id
HAVING AVG(charge_density) > AVG(divergence) * 1.5
ORDER BY avg_task_density DESC;

-- Detect flow conservation violations (Gauss's Magnetic Law)
SELECT
    device_id,
    AVG(ABS(divergence)) as avg_divergence_abs,
    COUNT(*) as violation_count
FROM execution_field_log
WHERE timestamp > NOW() - INTERVAL '5 minutes'
    AND ABS(divergence) > 0.01  -- Should be 0!
GROUP BY device_id
ORDER BY violation_count DESC;

-- Detect circular dependencies (Faraday's Law)
SELECT
    ifl.device_id,
    AVG(ifl.curl) as intent_curl,
    AVG(efl.flow_magnitude) as execution_flow,
    CASE
        WHEN AVG(ifl.curl) > 0.5 THEN 'circular_dependency'
        ELSE 'linear_flow'
    END as routing_pattern
FROM intent_field_log ifl
JOIN execution_field_log efl ON ifl.device_id = efl.device_id
    AND ifl.timestamp = efl.timestamp
WHERE ifl.timestamp > NOW() - INTERVAL '5 minutes'
GROUP BY ifl.device_id
HAVING AVG(ifl.curl) > 0.5
ORDER BY intent_curl DESC;
```

## Integration with Fail2Flag4Intent

### Complete Monitoring Pipeline

```python
def fail2flag_maxwell_check(device_id: str) -> list:
    """
    Run all Maxwell equation checks (Fail2Flag4Intent)

    Returns list of flags raised
    """
    flags = []

    # 1. Gauss's Law (Electric): Task accumulation
    gauss_e_result = detect_task_accumulation(device_id)
    if gauss_e_result["flag"]:
        flags.append(gauss_e_result)

    # 2. Gauss's Law (Magnetic): Flow conservation
    gauss_b_result = verify_flow_conservation(device_id)
    if not gauss_b_result["conserved"]:
        flags.append({
            "flag": True,
            "type": "flow_conservation_violation",
            "severity": gauss_b_result["severity"],
            **gauss_b_result
        })

    # 3. Faraday's Law: Circular dependencies
    faraday_result = detect_circular_dependencies(device_id)
    if faraday_result["flag"]:
        flags.append(faraday_result)

    # 4. Ampère-Maxwell Law: Channel overload
    ampere_result = detect_channel_overload(device_id)
    if ampere_result["flag"]:
        flags.append(ampere_result)

    # Log violations
    for flag in flags:
        log_maxwell_violation(flag)

    return flags

# Run on all devices periodically
def monitor_system_maxwell(system: str):
    """
    System-wide Maxwell monitoring
    """
    devices = get_all_devices(system)
    all_flags = []

    for device in devices:
        flags = fail2flag_maxwell_check(device)
        all_flags.extend(flags)

    # Generate report
    return {
        "timestamp": datetime.now(),
        "total_flags": len(all_flags),
        "by_type": categorize_flags(all_flags),
        "by_severity": severity_distribution(all_flags),
        "critical_devices": identify_critical_devices(all_flags)
    }
```

## HID/LLM/Device Workload Distribution

### Capability-Based Assignment (Maxwell Fields)

```python
def assign_work_maxwell(tasks: list) -> dict:
    """
    Assign work using Maxwell principles

    HID: High resistance (slow), low capacity → few field lines
    LLM: Medium resistance, medium capacity → moderate field lines
    Device: Low resistance (fast), high capacity → many field lines
    """
    # Define "electrical properties" of each worker type
    workers = {
        "hid": {
            "type": "human",
            "capacity": 10,      # Tasks per hour
            "resistance": 100,   # High latency
            "charge": -10        # Attractive (needs work)
        },
        "llm": {
            "type": "language_model",
            "capacity": 100,     # Tasks per hour
            "resistance": 10,    # Medium latency
            "charge": -50        # Moderate attraction
        },
        "device": {
            "type": "automated",
            "capacity": 1000,    # Tasks per hour
            "resistance": 1,     # Low latency
            "charge": -500       # High attraction
        }
    }

    distribution = {worker: [] for worker in workers}

    for task in tasks:
        # Task has "charge" (complexity/priority)
        task_charge = task["complexity"] * task["priority"]

        # Calculate field strength to each worker
        field_strengths = {}

        for worker, props in workers.items():
            # E = k × Q / (r² × resistance)
            # Negative charge attracts positive charge
            distance = 1.0  # Assume equal distance (can be routing distance)

            field_strength = abs(props["charge"]) / (
                (distance ** 2) * props["resistance"]
            )

            # Weight by capacity
            weighted_strength = field_strength * props["capacity"]

            field_strengths[worker] = weighted_strength

        # Assign to worker with strongest field
        assigned_worker = max(field_strengths, key=field_strengths.get)

        # But respect capabilities!
        task_type = task["type"]

        if task_type == "creative" and assigned_worker != "hid":
            # Creative tasks MUST go to human (even if device has stronger field)
            assigned_worker = "hid"
        elif task_type == "reasoning" and assigned_worker == "device":
            # Reasoning tasks need LLM, not device
            assigned_worker = "llm"
        elif task_type == "automation" and assigned_worker == "hid":
            # Don't burden human with automation
            assigned_worker = "device"

        distribution[assigned_worker].append(task)

        # Update charge (task assigned)
        workers[assigned_worker]["charge"] += task_charge

    return distribution

# Example:
tasks = [
    {"type": "creative", "complexity": 8, "priority": 10},     # → HID
    {"type": "reasoning", "complexity": 6, "priority": 7},     # → LLM
    {"type": "automation", "complexity": 3, "priority": 5},    # → Device
    {"type": "automation", "complexity": 2, "priority": 3},    # → Device
]

work_distribution = assign_work_maxwell(tasks)
# Result:
# {
#   "hid": [creative_task],           # 1 task (human only)
#   "llm": [reasoning_task],          # 1 task (needs thinking)
#   "device": [automation1, automation2]  # 2 tasks (can automate)
# }
```

## Conclusion

Maxwell's Equations provide the mathematical framework for system monitoring:

```
╔═══════════════════════════════════════════════════════════════╗
║           MAXWELL'S LAWS FOR BETTI                            ║
╚═══════════════════════════════════════════════════════════════╝

1. Gauss (E):     ∇·E = ρ/ε₀
   → Task distribution, accumulation detection

2. Gauss (B):     ∇·B = 0
   → Flow conservation, lost intent detection

3. Faraday:       ∇×E = -∂B/∂t
   → Circular dependencies, loop detection

4. Ampère-Maxwell: ∇×B = μ₀J + μ₀ε₀∂E/∂t
   → Channel load, bandwidth saturation

UNIFIED: Fail2Flag4Intent = Maxwell Violation Detection
```

Combined with Pythagoras, Einstein, Logarithms, Euler, and Fourier, BETTI now has a complete electromagnetic framework for intent propagation and system monitoring.

---

**Author**: Jasper van der Meent (BETTI Architecture)
**Implementation**: Claude Sonnet 4.5 + Jasper
**Date**: November 28, 2025
**Status**: Specification Complete
**Related**: BETTI-FOURIER-ROUTING.md, BETTI-EULER-IDENTITY.md, betti_fail2flag.py
