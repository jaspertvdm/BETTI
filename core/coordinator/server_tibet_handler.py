#!/usr/bin/env python3
"""
🖥️ Server Kant - TIBET Handler

Dit script laat zien hoe een server TIBETs ontvangt en verwerkt.
Perfect als voorbeeld voor jouw app server!
"""

import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'client-sdk/python'))

from tibet_betti_client import TibetBettiClient
from datetime import datetime
import json
import time


class ServerTibetHandler:
    """
    Server kant TIBET handler

    Ontvangt TIBETs via WebSocket en voert intents uit
    """

    def __init__(self, server_name: str = "koffie_server"):
        self.server_name = server_name
        self.client = TibetBettiClient(
            betti_url="http://localhost:18081",
            kit_url="http://localhost:8000",
            secret="example_secret_123"
        )
        self.coffee_machine_busy = False

    def handle_tibet(self, tibet_data: dict):
        """
        Main handler - ontvangt TIBET en routeert naar juiste handler
        """
        intent = tibet_data.get('intent')
        context = tibet_data.get('context', {})
        fira_id = tibet_data.get('fira_id')
        humotica = tibet_data.get('humotica', '')

        print("\n" + "=" * 70)
        print(f"📥 TIBET ONTVANGEN om {datetime.now().strftime('%H:%M:%S')}")
        print("=" * 70)
        print(f"🎯 Intent: {intent}")
        print(f"🔐 Trust Token: {fira_id}")
        print(f"📝 Humotica: {humotica}")
        print(f"\n📦 Context:")
        for key, value in context.items():
            print(f"   • {key}: {value}")

        # Route naar juiste intent handler
        if intent == "maak_koffie":
            return self.handle_coffee_intent(context, fira_id, humotica)
        elif intent == "turn_on_lights":
            return self.handle_lights_intent(context, fira_id)
        elif intent == "schedule_meeting":
            return self.handle_meeting_intent(context, fira_id)
        elif intent == "morning_briefing":
            return self.handle_briefing_intent(context, fira_id)
        else:
            return self.handle_unknown_intent(intent, context)

    def handle_coffee_intent(self, context: dict, fira_id: str, humotica: str):
        """
        Handle: maak_koffie ☕
        """
        print("\n🤖 SERVER ACTIE:")
        print("=" * 70)

        # Parse context
        coffee_type = context.get('type', 'zwart')
        size = context.get('size', 'normaal')
        melk = context.get('melk', 'gewoon')
        suiker = context.get('suiker', False)
        extra = context.get('extra')
        user = context.get('user_name', 'Guest')
        temperature = context.get('temperature', 'heet')

        # Check if busy
        if self.coffee_machine_busy:
            print("⚠️  Koffie machine is bezig...")
            return {
                'status': 'busy',
                'message': 'Koffie machine bezig, probeer over 2 minuten',
                'retry_after': 120
            }

        # Start making coffee
        self.coffee_machine_busy = True
        print(f"☕ Start maken: {coffee_type.upper()}")
        print(f"   └─ Voor: {user}")
        print(f"   └─ Size: {size}")
        print(f"   └─ Melk: {melk}")
        print(f"   └─ Suiker: {'Ja' if suiker else 'Nee'}")
        if extra:
            print(f"   └─ Extra: {extra}")
        print(f"   └─ Temperature: {temperature}")

        # Simulate making coffee
        steps = [
            "Grinding beans... ⚙️",
            "Heating water... 🔥",
            "Brewing espresso... ☕",
            f"Adding {melk}... 🥛" if melk != "geen" else "Skipping milk...",
            "Finishing up... ✨"
        ]

        for i, step in enumerate(steps, 1):
            print(f"   [{i}/{len(steps)}] {step}")
            time.sleep(0.5)  # Simulate work

        self.coffee_machine_busy = False

        # Done!
        result = {
            'status': 'completed',
            'coffee_type': coffee_type,
            'ready_for': user,
            'ready_at': datetime.now().isoformat(),
            'message': f'{coffee_type.capitalize()} klaar voor {user}! ☕',
            'location': 'koffie_machine_1'
        }

        print(f"\n✅ {result['message']}")
        print(f"📍 Location: {result['location']}")
        print(f"⏰ Ready at: {datetime.now().strftime('%H:%M:%S')}")

        # Log to database (in real app)
        self._log_to_database({
            'intent': 'maak_koffie',
            'fira_id': fira_id,
            'context': context,
            'result': result,
            'humotica': humotica,
            'timestamp': datetime.now().isoformat()
        })

        return result

    def handle_lights_intent(self, context: dict, fira_id: str):
        """
        Handle: turn_on_lights 💡
        """
        print("\n🤖 SERVER ACTIE:")
        print("=" * 70)

        room = context.get('room', 'living_room')
        brightness = context.get('brightness', 100)

        print(f"💡 Turning on lights in {room}")
        print(f"   └─ Brightness: {brightness}%")

        # Simulate turning on lights
        time.sleep(0.3)

        result = {
            'status': 'completed',
            'room': room,
            'brightness': brightness,
            'message': f'Lights in {room} turned on at {brightness}%'
        }

        print(f"✅ {result['message']}")

        return result

    def handle_meeting_intent(self, context: dict, fira_id: str):
        """
        Handle: schedule_meeting 📅
        """
        print("\n🤖 SERVER ACTIE:")
        print("=" * 70)

        attendees = context.get('attendees', 2)
        time_pref = context.get('time', 'morning')
        duration = context.get('duration', 60)

        print(f"📅 Scheduling meeting")
        print(f"   └─ Attendees: {attendees}")
        print(f"   └─ Preference: {time_pref}")
        print(f"   └─ Duration: {duration} minutes")

        # Simulate scheduling
        time.sleep(0.5)

        result = {
            'status': 'scheduled',
            'meeting_id': 'MTG-' + datetime.now().strftime('%Y%m%d-%H%M%S'),
            'attendees': attendees,
            'scheduled_for': f"Tomorrow {time_pref}",
            'duration': duration,
            'message': f'Meeting scheduled for {attendees} people'
        }

        print(f"✅ {result['message']}")
        print(f"📋 Meeting ID: {result['meeting_id']}")

        return result

    def handle_briefing_intent(self, context: dict, fira_id: str):
        """
        Handle: morning_briefing 📰
        """
        print("\n🤖 SERVER ACTIE:")
        print("=" * 70)

        print("📰 Generating morning briefing...")

        # Simulate gathering info
        briefing = {
            'weather': '☀️ Sunny, 18°C',
            'meetings': '2 meetings today',
            'emails': '5 unread emails',
            'tasks': '3 high priority tasks',
            'news': 'TIBET-BETTI SDK released! 🚀'
        }

        print("\n📊 Morning Briefing:")
        for key, value in briefing.items():
            print(f"   • {key.capitalize()}: {value}")

        result = {
            'status': 'completed',
            'briefing': briefing,
            'message': 'Morning briefing ready'
        }

        print(f"\n✅ {result['message']}")

        return result

    def handle_unknown_intent(self, intent: str, context: dict):
        """
        Handle unknown intents
        """
        print("\n⚠️  UNKNOWN INTENT")
        print("=" * 70)
        print(f"Intent '{intent}' is not recognized by this server")
        print("Available intents:")
        print("   • maak_koffie")
        print("   • turn_on_lights")
        print("   • schedule_meeting")
        print("   • morning_briefing")

        return {
            'status': 'error',
            'error': 'unknown_intent',
            'message': f"Intent '{intent}' not supported",
            'available_intents': [
                'maak_koffie',
                'turn_on_lights',
                'schedule_meeting',
                'morning_briefing'
            ]
        }

    def _log_to_database(self, log_data: dict):
        """
        Log to database (simulated)
        In real app: insert into database
        """
        print(f"\n💾 Logged to database:")
        print(f"   Intent: {log_data['intent']}")
        print(f"   FIR/A: {log_data['fira_id']}")
        print(f"   Status: {log_data['result']['status']}")

    def start_listening(self):
        """
        Start listening for TIBETs via WebSocket
        (In real app - this would be a WebSocket connection)
        """
        print("=" * 70)
        print(f"🖥️  SERVER STARTED: {self.server_name}")
        print("=" * 70)
        print("\n🎧 Listening for TIBETs...")
        print("   (In real app: WebSocket connection to BETTI Router)")
        print("\n💡 To test: Run demo_shoot_tibet.py to send a TIBET\n")


def demo_server_side():
    """
    Demo: Simulate receiving and handling a TIBET
    """
    print("=" * 70)
    print("🖥️  SERVER KANT - TIBET HANDLER DEMO")
    print("=" * 70)

    server = ServerTibetHandler("koffie_server")

    # Simulate receiving a TIBET
    print("\n📡 Simulating TIBET receipt...\n")
    time.sleep(1)

    # Example TIBET data (as received from BETTI Router)
    tibet_data = {
        'intent': 'maak_koffie',
        'context': {
            'type': 'cappuccino',
            'size': 'groot',
            'suiker': False,
            'melk': 'havermelk',
            'extra': 'extra shot',
            'temperature': 'heet',
            'user_name': 'Jasper',
            'reason': 'morning_boost'
        },
        'fira_id': 'fira-abc-123-xyz',
        'timebox_seconds': 30,
        'humotica': 'Jasper wil een cappuccino, extra shot voor de ochtend energie! ☕'
    }

    # Handle it!
    result = server.handle_tibet(tibet_data)

    # Show result
    print("\n" + "=" * 70)
    print("📤 RESULT RETURNED:")
    print("=" * 70)
    print(json.dumps(result, indent=2))

    print("\n" + "=" * 70)
    print("💡 INTEGRATION IN JOUW APP:")
    print("=" * 70)
    print("""
# In jouw app server (FastAPI / Flask / etc.)

from server_tibet_handler import ServerTibetHandler

server = ServerTibetHandler("my_app_server")

@app.websocket("/ws/tibet")
async def websocket_endpoint(websocket: WebSocket):
    await websocket.accept()

    while True:
        # Receive TIBET from BETTI Router
        data = await websocket.receive_json()

        # Handle TIBET
        result = server.handle_tibet(data)

        # Send result back
        await websocket.send_json(result)


# Of via POST endpoint:
@app.post("/intents/execute")
async def execute_intent(intent_data: dict):
    result = server.handle_tibet(intent_data)
    return result
    """)

    print("\n🎉 Server kant begrijpt nu wat te doen met TIBETs!\n")


if __name__ == "__main__":
    try:
        demo_server_side()
    except KeyboardInterrupt:
        print("\n\n🖥️  Server stopped.\n")
    except Exception as e:
        print(f"\n❌ Error: {e}\n")
        import traceback
        traceback.print_exc()
