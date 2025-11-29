# BETTI TCP Handshake Protocol

**Three-Way Handshake for Trust Establishment Before Full Connection**

## The TCP Handshake

```
Client                    Server
  │                          │
  │────── SYN ──────────────>│  (1) Synchronize - "I want to connect"
  │                          │
  │<───── SYN-ACK ──────────│  (2) Synchronize-Acknowledge - "I'm ready"
  │                          │
  │────── ACK ──────────────>│  (3) Acknowledge - "Let's start"
  │                          │
  │═══════ DATA ═══════════>│  (Connection established!)
```

## BETTI Mapping: Trust Before Intent

```
╔═══════════════════════════════════════════════════════════════╗
║         TCP → BETTI TRUST HANDSHAKE                           ║
╚═══════════════════════════════════════════════════════════════╝

SYN         →  Initial trust request (FIR/A genesis)
SYN-ACK     →  Trust acknowledgment + capability exchange
ACK         →  Trust confirmed + ready for intents
DATA        →  Intent execution (only after handshake!)

Flags:
SYN  = Synchronize = "Let's know each other"
ACK  = Acknowledge = "I understand you"
FIN  = Finish = "We're done"
RST  = Reset = "Trust broken, restart"
```

## The Core Principle: Trust Before Action

### Problem Without Handshake

```python
# Traditional systems: Immediate action
user_sends("turn_on_lights")
# → Executed blindly without trust verification!

# Issues:
# - No identity verification
# - No capability check
# - No mutual understanding
# - Direct to intent (unsafe!)
```

### BETTI Solution: Three-Way Handshake

```python
# Step 1: SYN (User initiates)
fir_a_request = {
    "type": "SYN",
    "initiator": "user_phone",
    "responder": "smart_home",
    "did": "did:jtel:phone123",
    "hid": "hid:jtel:user456",
    "timestamp": "2025-11-28T15:00:00Z",
    "message": "I want to connect and send intents"
}

# Step 2: SYN-ACK (System responds)
fir_a_response = {
    "type": "SYN-ACK",
    "fir_a_id": "fira_789",
    "status": "acknowledged",
    "capabilities": ["lights", "heating", "security"],
    "snaft_rules": ["no_outside_access", "battery_minimum_20pct"],
    "timestamp": "2025-11-28T15:00:01Z",
    "message": "I'm ready. Here's what I can do."
}

# Step 3: ACK (User confirms)
trust_confirmation = {
    "type": "ACK",
    "fir_a_id": "fira_789",
    "understood_capabilities": True,
    "accepted_snaft_rules": True,
    "timestamp": "2025-11-28T15:00:02Z",
    "message": "Understood. Let's start."
}

# NOW: Connection established!
# Trust verified, capabilities known, rules accepted
# → Safe to send intents!

send_intent("turn_on_lights")  # ✓ Safe now!
```

## Implementation

### 1. FIR/A Genesis with Handshake

```python
def establish_trust_handshake(
    initiator: str,
    responder: str,
    did_key: DIDKey,
    hid_key: HIDKey
) -> dict:
    """
    Three-way handshake for FIR/A establishment

    Returns: Trust token only after complete handshake
    """
    # Step 1: SYN - Send trust request
    syn_request = {
        "type": "SYN",
        "initiator": initiator,
        "responder": responder,
        "did_public": did_key.export_public(),
        "hid_binding": hid_key.derive_did_binding(did_key),
        "timestamp": datetime.now(),
        "seq": 0  # Sequence number (like TCP)
    }

    response = send_to_router(syn_request)

    if response["type"] != "SYN-ACK":
        return {"error": "Handshake failed at SYN-ACK"}

    # Step 2: SYN-ACK received - Validate
    fir_a_id = response["fir_a_id"]
    capabilities = response["capabilities"]
    snaft_rules = response["snaft_rules"]

    # Check if capabilities meet requirements
    if not validate_capabilities(capabilities):
        return {"error": "Insufficient capabilities"}

    # Check if SNAFT rules are acceptable
    if not acceptable_snaft_rules(snaft_rules):
        return {"error": "SNAFT rules too restrictive"}

    # Step 3: ACK - Confirm trust
    ack_confirmation = {
        "type": "ACK",
        "fir_a_id": fir_a_id,
        "accepted_capabilities": capabilities,
        "accepted_snaft_rules": snaft_rules,
        "timestamp": datetime.now(),
        "seq": 1
    }

    final_response = send_to_router(ack_confirmation)

    if final_response["status"] != "established":
        return {"error": "Handshake failed at ACK"}

    # Handshake complete!
    return {
        "status": "established",
        "fir_a_id": fir_a_id,
        "trust_level": final_response["trust_level"],
        "capabilities": capabilities,
        "snaft_rules": snaft_rules,
        "established_at": datetime.now(),
        "ready_for_intents": True  # ✓ NOW safe!
    }
```

### 2. Capability Exchange (SYN-ACK Phase)

```python
def generate_syn_ack_response(syn_request: dict) -> dict:
    """
    Server response to SYN: Share capabilities and rules
    """
    # Create FIR/A
    fir_a_id = create_fir_a(syn_request["initiator"], syn_request["responder"])

    # Get system capabilities
    capabilities = get_available_intents()  # ["turn_on_lights", "set_temperature", ...]

    # Get SNAFT rules for this device type
    snaft_rules = get_snaft_rules(syn_request["responder"])

    # Get BALANS preferences
    balans_preferences = get_balans_preferences(fir_a_id)

    return {
        "type": "SYN-ACK",
        "fir_a_id": fir_a_id,
        "status": "acknowledged",
        "capabilities": capabilities,
        "snaft_rules": snaft_rules,
        "balans_preferences": balans_preferences,
        "max_intents_per_minute": 60,
        "timestamp": datetime.now(),
        "seq": syn_request["seq"] + 1,
        "message": "I'm ready. Here's what I can do and my rules."
    }
```

### 3. Handshake Flags

```python
class HandshakeFlags:
    """TCP-style flags for BETTI trust handshake"""

    SYN = 0x01   # Synchronize - initiate connection
    ACK = 0x02   # Acknowledge - confirm receipt
    FIN = 0x04   # Finish - close connection
    RST = 0x08   # Reset - abort connection
    PSH = 0x10   # Push - urgent intent (after established)

def check_handshake_flag(flags: int, flag: int) -> bool:
    """Check if specific flag is set"""
    return (flags & flag) != 0

def set_handshake_flag(flags: int, flag: int) -> int:
    """Set specific flag"""
    return flags | flag

# Example:
flags = 0
flags = set_handshake_flag(flags, HandshakeFlags.SYN)  # Set SYN
flags = set_handshake_flag(flags, HandshakeFlags.ACK)  # Set ACK
# flags now = SYN-ACK (0x03)

if check_handshake_flag(flags, HandshakeFlags.SYN):
    print("SYN flag set")  # ✓

if check_handshake_flag(flags, HandshakeFlags.ACK):
    print("ACK flag set")  # ✓
```

## Trust States

```python
class TrustState(Enum):
    """FIR/A trust states (like TCP states)"""

    CLOSED = "CLOSED"                   # No connection
    SYN_SENT = "SYN_SENT"              # SYN sent, waiting for SYN-ACK
    SYN_RECEIVED = "SYN_RECEIVED"      # SYN received, SYN-ACK sent
    ESTABLISHED = "ESTABLISHED"         # Handshake complete, trust established
    FIN_WAIT = "FIN_WAIT"              # Closing connection
    TIME_WAIT = "TIME_WAIT"            # Waiting before full closure
    RESET = "RESET"                    # Trust broken, need new handshake

def get_trust_state(fir_a_id: str) -> TrustState:
    """Get current trust state of FIR/A"""
    # Query database
    state = query_fir_a_state(fir_a_id)
    return TrustState(state)

def transition_trust_state(
    fir_a_id: str,
    from_state: TrustState,
    to_state: TrustState,
    event: str
) -> bool:
    """
    Transition trust state (state machine)
    """
    valid_transitions = {
        (TrustState.CLOSED, TrustState.SYN_SENT): ["SYN"],
        (TrustState.SYN_SENT, TrustState.ESTABLISHED): ["SYN-ACK", "ACK"],
        (TrustState.SYN_RECEIVED, TrustState.ESTABLISHED): ["ACK"],
        (TrustState.ESTABLISHED, TrustState.FIN_WAIT): ["FIN"],
        (TrustState.FIN_WAIT, TrustState.CLOSED): ["ACK"],
        (TrustState.ESTABLISHED, TrustState.RESET): ["RST", "SNAFT_VIOLATION"],
    }

    transition = (from_state, to_state)

    if transition not in valid_transitions:
        return False

    if event not in valid_transitions[transition]:
        return False

    # Valid transition
    update_fir_a_state(fir_a_id, to_state)
    return True
```

## Handshake Timeout & Retries

```python
def handshake_with_timeout(
    initiator: str,
    responder: str,
    timeout: float = 5.0,
    max_retries: int = 3
) -> dict:
    """
    Handshake with timeout and retries (like TCP)
    """
    for attempt in range(max_retries):
        try:
            # Start handshake
            result = establish_trust_handshake(initiator, responder)

            if result.get("status") == "established":
                return result

        except TimeoutError:
            # SYN-ACK not received in time
            if attempt < max_retries - 1:
                # Exponential backoff
                wait_time = (2 ** attempt) * 1.0  # 1s, 2s, 4s
                time.sleep(wait_time)
                continue
            else:
                return {
                    "error": "Handshake timeout",
                    "attempts": max_retries,
                    "reason": "No SYN-ACK received"
                }

    return {"error": "Handshake failed after retries"}
```

## Connection Termination (FIN)

```python
def close_trust_connection(fir_a_id: str) -> dict:
    """
    Gracefully close FIR/A connection (FIN handshake)
    """
    # Step 1: Send FIN
    fin_request = {
        "type": "FIN",
        "fir_a_id": fir_a_id,
        "reason": "Session complete",
        "timestamp": datetime.now()
    }

    response = send_to_router(fin_request)

    # Step 2: Receive ACK
    if response["type"] != "ACK":
        return {"error": "FIN not acknowledged"}

    # Step 3: Wait for other side's FIN
    other_fin = wait_for_fin(fir_a_id, timeout=5.0)

    # Step 4: Send final ACK
    final_ack = {
        "type": "ACK",
        "fir_a_id": fir_a_id,
        "timestamp": datetime.now()
    }

    send_to_router(final_ack)

    # Connection closed
    return {
        "status": "closed",
        "fir_a_id": fir_a_id,
        "closed_at": datetime.now()
    }
```

## Database Schema

```sql
-- FIR/A handshake log
CREATE TABLE IF NOT EXISTS fira_handshake_log (
    id BIGSERIAL PRIMARY KEY,
    fir_a_id TEXT NOT NULL,
    timestamp TIMESTAMPTZ DEFAULT NOW(),

    -- Handshake state
    state VARCHAR(20) NOT NULL,  -- SYN_SENT, SYN_RECEIVED, ESTABLISHED, etc.
    flags INT NOT NULL,          -- SYN=1, ACK=2, FIN=4, RST=8

    -- Message type
    message_type VARCHAR(20),    -- SYN, SYN-ACK, ACK, FIN, RST

    -- Capabilities exchanged
    capabilities_sent JSONB,
    capabilities_received JSONB,
    snaft_rules_sent JSONB,
    snaft_rules_received JSONB,

    -- Timing
    rtt_milliseconds INT,        -- Round-trip time

    INDEX idx_fira_handshake_fira (fir_a_id),
    INDEX idx_fira_handshake_state (state),
    INDEX idx_fira_handshake_time (timestamp DESC)
);
```

## Integration with JIS

```python
# JIS client with handshake
from jis_client import JISClient

client = JISClient(router_url="http://localhost:18081", secret="secret")

# Establish trust with handshake
fir_a = client.establish_trust_handshake(
    initiator="my_app",
    responder="api_server",
    did_key=my_did,
    hid_key=my_hid
)

if fir_a["status"] == "established":
    # Handshake complete! Now safe to send intents
    client.send_intent(fir_a["fir_a_id"], "turn_on_lights", {})
else:
    print(f"Handshake failed: {fir_a['error']}")
```

## Benefits

1. **Trust Verification**: Identity and capabilities confirmed before action
2. **Capability Discovery**: Know what system can do before sending intents
3. **Rule Awareness**: SNAFT rules communicated upfront
4. **Graceful Failure**: Handshake fails → no blind intent execution
5. **State Tracking**: Clear connection lifecycle (SYN → ESTABLISHED → FIN)

## Connection to BETTI Principles

- **Before intents**: Trust must be established (handshake)
- **SNAFT integration**: Rules shared in SYN-ACK phase
- **BALANS awareness**: Preferences exchanged during handshake
- **Intent safety**: No execution without established trust

---

**Author**: Jasper van der Meent (BETTI Architecture)
**Date**: November 28, 2025
**Status**: Specification Complete
