"""
BETTI BALANS Complete Demo

Demonstrates all BALANS features:
1. Intent execution with BALANS pipeline
2. Handling all BALANS decision types
3. SNAFT factory firewall
4. Internal TIBET (robot permissions)
5. Clarification dialogues
6. Warmth & Color responses
7. BALANS & SNAFT analytics

Author: Jasper van der Meent (BETTI Architecture)
"""

import sys
import os

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

from tibet_betti_client import TibetBettiClient


def demo_basic_execution():
    """Demo 1: Basic Intent Execution with BALANS"""
    print("=" * 70)
    print("DEMO 1: Basic Intent Execution")
    print("=" * 70)

    client = TibetBettiClient(
        betti_url="http://192.168.4.76:8081",
        kit_url="http://192.168.4.76:8081"
    )

    # Execute simple intent
    result = client.execute_intent(
        intent="turn_on_lights",
        context={
            "location": "huiskamer",
            "device_type": "phone",
            "manufacturer": "Apple"
        },
        user_id="jasper@jtel.nl",
        urgency=5
    )

    print(f"\n✓ Status: {result['status']}")
    if result['status'] == 'executed':
        print(f"✓ Message: {result['result']['message']}")
        print(f"✓ Warmth: {result['result']['warmth']}")
        print(f"✓ Color: {result['result']['color']}")
        print(f"✓ Complexity: {result['result']['complexity']['score']}")


def demo_clarification():
    """Demo 2: BALANS Clarification Dialogue"""
    print("\n" + "=" * 70)
    print("DEMO 2: Clarification Dialogue")
    print("=" * 70)

    client = TibetBettiClient(
        betti_url="http://192.168.4.76:8081",
        kit_url="http://192.168.4.76:8081"
    )

    # Ambiguous intent - "living" could mean "huiskamer" or "living room"
    result = client.execute_intent(
        intent="turn_on_living_lights",
        context={"device_type": "phone"},
        user_id="jasper@jtel.nl"
    )

    print(f"\n✓ Status: {result['status']}")
    if result['status'] == 'clarification_needed':
        print(f"❓ Question: {result['result']['clarification_question']}")
        print(f"  Warmth: {result['result']['warmth']}")
        print(f"  Color: {result['result']['color']}")

        # User clarifies
        print("\n→ User clarifies: 'huiskamer'")
        result = client.clarify_intent(
            intent="turn_on_lights",
            clarification="huiskamer",
            context={"location": "huiskamer"},
            user_id="jasper@jtel.nl"
        )

        print(f"\n✓ After clarification: {result['status']}")
        if result['status'] == 'executed':
            print(f"✓ {result['result']['message']}")


def demo_resource_request():
    """Demo 3: Resource Request (Internal TIBET)"""
    print("\n" + "=" * 70)
    print("DEMO 3: Resource Request - Internal TIBET")
    print("=" * 70)

    client = TibetBettiClient(
        betti_url="http://192.168.4.76:8081",
        kit_url="http://192.168.4.76:8081"
    )

    # Large upload with low battery - simulated
    result = client.execute_intent(
        intent="upload_large_file",
        context={
            "file_size_mb": 500,
            "did": "phone_001",
            "device_type": "phone",
            "battery_pct": 15,  # Low battery!
            "urgency": 7
        },
        user_id="jasper@jtel.nl",
        deadline="2025-11-28T18:00:00Z"
    )

    print(f"\n✓ Status: {result['status']}")
    if result['status'] == 'awaiting_resources':
        print(f"🔋 Robot Request: {result['result']['robot_request']}")
        print(f"  Reasoning: {result['result']['robot_reasoning']}")
        print(f"  Delay: {result['result'].get('estimated_delay_minutes')} minutes")
        print(f"  Warmth: {result['result']['warmth']}")
        print(f"  Color: {result['result']['color']}")

        # User approves charging
        print("\n→ User approves charging")
        result = client.approve_resource_request(
            intent="upload_large_file",
            context={
                "file_size_mb": 500,
                "did": "phone_001",
                "device_type": "phone"
            },
            user_id="jasper@jtel.nl",
            approved=True
        )

        print(f"\n✓ After approval: {result['status']}")


def demo_snaft_violation():
    """Demo 4: SNAFT Factory Firewall Violation"""
    print("\n" + "=" * 70)
    print("DEMO 4: SNAFT Factory Firewall")
    print("=" * 70)

    client = TibetBettiClient(
        betti_url="http://192.168.4.76:8081",
        kit_url="http://192.168.4.76:8081"
    )

    # Try to fly drone near airport - BLOCKED by SNAFT
    result = client.execute_intent(
        intent="fly_near_airport_schiphol",
        context={
            "did": "drone_dji_001",
            "device_type": "drone",
            "manufacturer": "DJI",
            "latitude": 52.308056,
            "longitude": 4.764167
        },
        user_id="jasper@jtel.nl"
    )

    print(f"\n✓ Status: {result['status']}")
    if result['status'] == 'snaft_blocked':
        print(f"🚫 Blocked: {result['result']['message']}")
        print(f"  Reason: {result['result']['reason']}")
        print(f"  Severity: {result['result']['severity']}")
        print(f"  Immutable: {result['result']['immutable']}")


def demo_complexity_split():
    """Demo 5: Task Too Complex - Split Required"""
    print("\n" + "=" * 70)
    print("DEMO 5: Complexity Analysis - Split Required")
    print("=" * 70)

    client = TibetBettiClient(
        betti_url="http://192.168.4.76:8081",
        kit_url="http://192.168.4.76:8081"
    )

    # Very complex task
    result = client.execute_intent(
        intent="organize_entire_smart_home",
        context={
            "humans": 5,
            "devices": 50,
            "operations": 200,
            "device_type": "phone"
        },
        user_id="jasper@jtel.nl"
    )

    print(f"\n✓ Status: {result['status']}")
    if result['status'] == 'split_required':
        print(f"📋 Message: {result['result']['message']}")
        print(f"  Complexity Score: {result['result']['complexity']['score']}")
        print(f"  B0 (Humans): {result['result']['complexity']['b0_humans']}")
        print(f"  B1 (Devices): {result['result']['complexity']['b1_devices']}")
        print(f"  B2 (Operations): {result['result']['complexity']['b2_ops']}")
        print(f"  Warmth: {result['result']['warmth']}")
        print(f"  Color: {result['result']['color']}")

        if 'suggested_splits' in result['result']:
            print(f"\n  Suggested Splits:")
            for split in result['result']['suggested_splits']:
                print(f"    - {split}")


def demo_balans_analytics():
    """Demo 6: BALANS Analytics Dashboard"""
    print("\n" + "=" * 70)
    print("DEMO 6: BALANS Analytics Dashboard")
    print("=" * 70)

    client = TibetBettiClient(
        betti_url="http://192.168.4.76:8081",
        kit_url="http://192.168.4.76:8081"
    )

    # Get BALANS dashboard
    dashboard = client.get_balans_dashboard(days=7)

    print("\nDecision Distribution (last 7 days):")
    for decision in dashboard.get('decision_distribution', []):
        print(f"  {decision['decision']:20} {decision['count']:4} times "
              f"(confidence: {float(decision.get('avg_confidence', 0)):.2f})")

    print("\nWarmth & Color Distribution:")
    for wc in dashboard.get('warmth_color_distribution', [])[:5]:
        print(f"  {wc['response_warmth']:15} + {wc['response_color']:10} = {wc['count']:4} times")


def demo_snaft_analytics():
    """Demo 7: SNAFT Analytics Dashboard"""
    print("\n" + "=" * 70)
    print("DEMO 7: SNAFT Analytics Dashboard")
    print("=" * 70)

    client = TibetBettiClient(
        betti_url="http://192.168.4.76:8081",
        kit_url="http://192.168.4.76:8081"
    )

    # Get SNAFT rules
    print("\nSNAFT Rules for Drones:")
    drone_rules = client.get_snaft_rules(device_type="drone")
    for rule in drone_rules[:3]:
        print(f"  {rule['rule_type']:20} {rule['manufacturer']:15} - {rule['reason']}")

    # Get SNAFT dashboard
    dashboard = client.get_snaft_dashboard(days=7)

    print("\nTop SNAFT Violations (last 7 days):")
    for v in dashboard.get('top_violations', [])[:5]:
        print(f"  {v['device_type']:10} {v['reason']:50} {v['violation_count']:4} times")

    print("\nDevice Awareness Levels:")
    for d in dashboard.get('device_awareness', [])[:5]:
        print(f"  {d['did']:20} awareness: {d['self_awareness_level']}/10  "
              f"(learned {d['snaft_violations_learned']} violations)")


def demo_complexity_analysis():
    """Demo 8: Complexity Analysis Without Execution"""
    print("\n" + "=" * 70)
    print("DEMO 8: Complexity Analysis (What-If)")
    print("=" * 70)

    client = TibetBettiClient(
        betti_url="http://192.168.4.76:8081",
        kit_url="http://192.168.4.76:8081"
    )

    # Analyze without executing
    analysis = client.analyze_complexity(
        intent="multi_device_coordination",
        context={
            "humans": 3,
            "devices": 10,
            "operations": 25,
            "time_minutes": 15
        },
        threshold_profile="default"
    )

    print("\nComplexity Analysis:")
    comp = analysis['complexity']
    print(f"  B0 (Humans):       {comp['b0_humans']}")
    print(f"  B1 (Devices):      {comp['b1_devices']}")
    print(f"  B2 (Operations):   {comp['b2_ops']}")
    print(f"  B3 (TBET Steps):   {comp['b3_tbet_steps']}")
    print(f"  B4 (Time Minutes): {comp['b4_time_minutes']}")
    print(f"  B5 (Channels):     {comp['b5_channels']}")
    print(f"\n  Total Score:       {comp['score']}")
    print(f"  Split Required:    {comp['split_required']}")


def demo_kit_travel_scenario():
    """Demo 9: Real Kit Travel Scenario - Battery Management"""
    print("\n" + "=" * 70)
    print("DEMO 9: Kit Travel Scenario - Krakow Trip")
    print("=" * 70)
    print("Scenario: User wants to drive to Krakow, but battery is 25%")
    print("=" * 70)

    client = TibetBettiClient(
        betti_url="http://192.168.4.76:8081",
        kit_url="http://192.168.4.76:8081"
    )

    result = client.execute_intent(
        intent="navigate_to_krakow",
        context={
            "did": "tesla_model_3_001",
            "device_type": "car",
            "manufacturer": "Tesla",
            "battery_pct": 25,
            "destination": "Krakow, Poland",
            "distance_km": 450,
            "current_location": "Utrecht, Netherlands",
            "urgency": 6
        },
        user_id="jasper@jtel.nl"
    )

    print(f"\n✓ BALANS Decision: {result['status']}")
    print(f"  Message: {result['result']['message']}")
    print(f"  Warmth: {result['result']['warmth']}")
    print(f"  Color: {result['result']['color']}")

    if result['status'] == 'delayed':
        print(f"\n  Alternative: {result['result'].get('alternative_action')}")
        print(f"  Suggested Delay: {result['result'].get('suggested_delay_minutes')} minutes")


def main():
    """Run all demos"""
    print("""
╔═══════════════════════════════════════════════════════════════════════╗
║                                                                       ║
║              BETTI BALANS - Complete Feature Demo                    ║
║                                                                       ║
║  Demonstrates:                                                        ║
║  • SNAFT factory firewall (immutable safety rules)                   ║
║  • BALANS pre-execution decisions (resource checks)                  ║
║  • Internal TIBET (robot permission requests)                        ║
║  • Clarification dialogues (ambiguity resolution)                    ║
║  • Warmth & Color emotional responses                                ║
║  • Complexity analysis (B0-B5 topological dimensions)                ║
║  • Analytics dashboards                                              ║
║                                                                       ║
║  Author: Jasper van der Meent (BETTI Architecture)                   ║
║                                                                       ║
╚═══════════════════════════════════════════════════════════════════════╝
    """)

    try:
        # Run all demos
        demo_basic_execution()
        demo_clarification()
        demo_resource_request()
        demo_snaft_violation()
        demo_complexity_split()
        demo_balans_analytics()
        demo_snaft_analytics()
        demo_complexity_analysis()
        demo_kit_travel_scenario()

        print("\n" + "=" * 70)
        print("✓ All demos completed successfully!")
        print("=" * 70)

    except Exception as e:
        print(f"\n❌ Error: {e}")
        print("\nNote: Make sure brain-api server is running on 192.168.4.76:8081")
        print("      and jtel_security database has been created.")
        return 1

    return 0


if __name__ == "__main__":
    exit(main())
