# 🧠 BETTI SDK Integration - Brain API

**BETTI (TIBET Behavioral Engineering for Trust & Intent Integration)** is now integrated into the JTel Brain API!

This document explains what's been added and how to use it.

---

## 🎯 What is BETTI?

BETTI implements three intelligent layers:

```
┌─────────────────────────────────────────────┐
│  📊 CONTEXT LAYER   "Wat is de situatie?"  │
│  ↓                                          │
│  🧠 SENSE LAYER     "Wat moet gebeuren?"   │
│  ↓                                          │
│  ⚡ INTENT LAYER    "Doe het!"             │
└─────────────────────────────────────────────┘
```

- **Context Layer**: Aggregates user/device state from your database
- **Sense Layer**: Pattern matching rules that trigger when conditions match
- **Intent Layer**: Executes actions based on sense triggers

---

## 📦 What's Been Added

### New Database Tables

```sql
sense_rules           -- Context-aware automation rules
user_trust_tokens     -- BETTI trust token cache (FIR/A references)
betti_intent_log      -- Intent execution audit log
user_context_cache    -- Context cache for performance
```

### New API Endpoints

All endpoints are under `/betti` prefix:

#### Context Layer
- `POST /betti/context/update` - Update user context
- `GET /betti/context/{user_id}` - Get current context

#### Sense Layer
- `POST /betti/sense/rules` - Create sense rule
- `GET /betti/sense/rules` - List all rules
- `POST /betti/sense/evaluate` - Evaluate rules against context
- `DELETE /betti/sense/rules/{id}` - Delete rule

#### Intent Layer
- `POST /betti/intent/execute` - Execute an intent
- `GET /betti/intent/history/{user_id}` - Get intent history

---

## 🚀 Quick Start

### 1. Run Database Migration

```bash
cd brain_api
./run_betti_migration.sh
```

This will:
- Create BETTI tables in your `jtel_brain` database
- Insert example sense rules
- Verify the migration was successful

### 2. Restart Brain API

```bash
# If using systemd
sudo systemctl restart brain-api

# Or manually
cd brain_api
python3 -m uvicorn main:app --host 0.0.0.0 --port 8010 --reload
```

You should see:
```
✅ BETTI SDK endpoints loaded successfully
```

### 3. Test the Endpoints

Visit: http://localhost:8010/docs

You'll see new `/betti/*` endpoints in the Swagger UI.

---

## 📖 Usage Examples

### Example 1: Update User Context

When a user comes home, update their context:

```bash
curl -X POST "http://localhost:8010/betti/context/update" \
  -H "Content-Type: application/json" \
  -d '{
    "user_id": "jasper",
    "context": {
      "location": "home",
      "ambient_light": 50
    },
    "evaluate_sense": true
  }'
```

**What happens:**
1. Brain API aggregates FULL context from database (user info, recent activities, time of day, etc.)
2. Merges it with provided context
3. Caches it for performance
4. Evaluates sense rules
5. If rules match → triggers intents (logged in `betti_intent_log`)

Response:
```json
{
  "user_id": "jasper",
  "context": {
    "user_id": "jasper",
    "user_name": "Jasper",
    "location": "home",
    "time_of_day": "evening",
    "day_type": "weekday",
    "ambient_light": 50,
    "activity_count_24h": 42
  },
  "timestamp": "2025-11-27T17:30:00"
}
```

### Example 2: Create a Sense Rule

Create a rule that suggests turning on lights in the evening:

```bash
curl -X POST "http://localhost:8010/betti/sense/rules" \
  -H "Content-Type: application/json" \
  -d '{
    "name": "Evening Lights",
    "description": "Turn on lights when arriving home in the evening",
    "conditions": {
      "location": "home",
      "time_of_day": "evening",
      "ambient_light": {"lt": 100}
    },
    "intent": "suggest_lights_on",
    "priority": 7
  }'
```

**Condition operators:**
- Direct match: `"location": "home"`
- Less than: `{"lt": 100}`
- Greater than: `{"gt": 50}`
- In list: `{"in": ["active", "busy"]}`

### Example 3: List Sense Rules

```bash
curl "http://localhost:8010/betti/sense/rules"
```

Response:
```json
[
  {
    "id": "550e8400-e29b-41d4-a716-446655440000",
    "name": "Evening Lights",
    "description": "Turn on lights in the evening",
    "conditions": {
      "location": "home",
      "time_of_day": "evening",
      "ambient_light": {"lt": 100}
    },
    "intent": "suggest_lights_on",
    "priority": 7,
    "enabled": true,
    "user_id": null,
    "created_at": "2025-11-27T17:00:00"
  }
]
```

### Example 4: Execute an Intent

```bash
curl -X POST "http://localhost:8010/betti/intent/execute" \
  -H "Content-Type: application/json" \
  -d '{
    "intent": "turn_on_lights",
    "context": {
      "room": "living_room",
      "brightness": 80
    },
    "user_id": "jasper"
  }'
```

Response:
```json
{
  "intent": "turn_on_lights",
  "status": "executed",
  "result": {
    "message": "Intent 'turn_on_lights' executed successfully"
  },
  "timestamp": "2025-11-27T17:35:00"
}
```

**Note:** Intent execution currently logs to database. You need to implement actual handlers for your use case (see `betti_endpoints.py` line ~580).

### Example 5: Get Intent History

```bash
curl "http://localhost:8010/betti/intent/history/jasper?limit=10"
```

---

## 🔧 How Context Aggregation Works

The Context Layer queries your existing database to build a complete picture:

```python
def get_user_context(user_id):
    # 1. Get user info from identities table
    # 2. Get recent activities from events table
    # 3. Calculate time context (morning/afternoon/evening/night)
    # 4. Calculate day type (weekday/weekend)
    # 5. Count recent activity (24h window)
    # 6. Merge user metadata

    return {
        "user_id": "jasper",
        "user_name": "Jasper",
        "time_of_day": "evening",
        "day_type": "weekday",
        "hour": 19,
        "recent_activity": "chat_message",
        "activity_count_24h": 42,
        # ... any custom metadata from user record
    }
```

**No new tables needed!** Context is aggregated from your existing:
- `identities` table
- `events` table
- `raw_items` table

---

## 🧪 Testing with cURL

### Scenario: User Arrives Home

```bash
# 1. Update context (user arrives home at 19:00)
curl -X POST "http://localhost:8010/betti/context/update" \
  -H "Content-Type: application/json" \
  -d '{
    "user_id": "jasper",
    "context": {"location": "home", "ambient_light": 45},
    "evaluate_sense": true
  }'

# 2. Check which rules matched
curl "http://localhost:8010/betti/sense/evaluate" \
  -X POST \
  -H "Content-Type: application/json" \
  -d '{
    "user_id": "jasper"
  }'

# 3. Check intent log
curl "http://localhost:8010/betti/intent/history/jasper?limit=5"
```

---

## 🔗 Integration with BETTI Router (Optional)

The **BETTI Router** is a separate service that handles:
- FIR/A trust relationships (TIBET tokens)
- Intent forwarding between devices
- Continuity chain verification
- Loop prevention

**Current setup:**
- Brain API = Context/Sense/Intent layers (✅ integrated)
- BETTI Router = Trust & routing (separate service, see `server-config/jis-test/router/`)

To connect Brain API to BETTI Router:

1. Start BETTI Router (see `server-config/jis-test/README.md`)
2. Use the BETTI Python SDK to send TIBETs:

```python
from client_sdk.python.tibet_betti_client import BettiClient

client = BettiClient(router_url="http://localhost:8080")

# Send intent via BETTI Router
client.send_tibet(
    fira_id="your-fira-id",
    intent="turn_on_lights",
    context={"room": "living_room"}
)
```

---

## 📊 Example Sense Rules

The migration includes these example rules:

### 1. Evening Lights
```json
{
  "conditions": {
    "time_of_day": "evening",
    "ambient_light": {"lt": 100}
  },
  "intent": "suggest_lights_on",
  "priority": 7
}
```

### 2. Morning Briefing
```json
{
  "conditions": {
    "time_of_day": "morning",
    "day_type": "weekday"
  },
  "intent": "morning_briefing",
  "priority": 8
}
```

### 3. Focus Mode Low Battery
```json
{
  "conditions": {
    "focus_mode": true,
    "battery_level": {"lt": 20}
  },
  "intent": "disable_focus_mode",
  "priority": 9
}
```

---

## 🛠️ Customization

### Add Your Own Intent Handlers

Edit `betti_endpoints.py` around line 580:

```python
@router.post("/intent/execute")
async def execute_intent(payload: IntentExecute):
    # Add your custom intent handlers
    if payload.intent == "turn_on_lights":
        result = turn_on_lights(payload.context)
        return IntentExecuteResponse(
            intent=payload.intent,
            status="executed",
            result=result,
            timestamp=datetime.now().isoformat()
        )

    elif payload.intent == "send_message":
        result = send_message(payload.context)
        return IntentExecuteResponse(...)
```

### Extend Context Aggregation

Edit `get_user_context()` in `betti_endpoints.py` around line 100:

```python
def get_user_context(user_id: str, conn) -> Dict[str, Any]:
    # Add queries to your custom tables
    cur.execute("SELECT battery_level FROM devices WHERE user_id = %s", (user_id,))
    device = cur.fetchone()

    context = {
        # ... existing context
        "battery_level": device["battery_level"] if device else 100,
        "custom_field": get_custom_data(user_id)
    }

    return context
```

---

## 📚 Documentation

- **BETTI Architecture**: `docs/TBET-BETTI-ARCHITECTURE.md`
- **Context/Sense/Intent Explained**: `docs/SENSE-CONTEXT-INTENT-EXPLAINED.md`
- **Database Schemas**: `docs/DATABASE-SCHEMAS.md`
- **Integration Architecture**: `docs/INTEGRATION-ARCHITECTURE.md`
- **Python SDK**: `client-sdk/python/tibet_betti_client/README.md`
- **BETTI Router**: `server-config/jis-test/router/README.md`

---

## 🎯 Next Steps

1. ✅ Run database migration
2. ✅ Test endpoints in Swagger UI
3. 🔄 Implement custom intent handlers
4. 🔄 Extend context aggregation with your app data
5. 🔄 Integrate with BETTI Router (optional)
6. 🔄 Connect to JTel app for real-time context updates

---

## 🐛 Troubleshooting

### "BETTI SDK not loaded"

Check that `betti_endpoints.py` exists in `brain_api/` directory.

### Migration fails

```bash
# Check database connection
PGPASSWORD="$BRAIN_DB_PASSWORD" psql -h localhost -U jtel_brain_user -d jtel_brain -c "\dt"

# Verify environment variables
cat .env | grep BRAIN_DB
```

### Endpoints not showing in /docs

Restart the server and check logs:
```bash
tail -f /var/log/brain-api/output.log
```

You should see: `✅ BETTI SDK endpoints loaded successfully`

---

## 💡 Tips

- **Context updates are cheap**: They aggregate from existing tables, no extra database load
- **Sense rules are fast**: Evaluated in-memory with simple comparisons
- **Intent logging is async**: Doesn't block execution
- **Cache is automatic**: Context is cached for 5 minutes, refresh happens transparently

---

## 📞 Support

Questions about BETTI integration? Check:
- `docs/SENSE-CONTEXT-INTENT-EXPLAINED.md` - Detailed explanation
- `docs/INTEGRATION-ARCHITECTURE.md` - System design
- Swagger UI at http://localhost:8010/docs - Interactive API testing

---

**BETTI: Context observeert → Sense beslist → Intent executeert! 🎯**
