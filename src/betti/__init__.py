"""
BETTI - Base Event Token Time Intent

Physics-based intent coordination framework with Humotica context.
Implements JIS (JTel Identity Standard) protocol.

Installation:
    pip install betti

Usage:
    from betti import BETTIClient, Tibet, Context

    # Initialize client
    client = BETTIClient(
        betti_url="http://localhost:18081",
        secret="your_secret_here"
    )

    # Establish trust relationship (FIR/A)
    relationship = client.establish_trust("my_app", "user_device")

    # Send TIBET intent with Humotica context
    client.send_tibet(
        relationship_id=relationship.id,
        intent="turn_on_lights",
        context={"room": "living_room", "brightness": 80},
        humotica="User arriving home after work, wants comfortable lighting"
    )

Documentation: https://betti.humotica.com
JIS Protocol: https://github.com/jaspertvdm/JTel-identity-standard
"""

from .client import TibetBettiClient as BETTIClient
from .tibet import Tibet, TimeWindow, Constraints
from .context import Context, SenseRule
from .trust_token import TrustToken, FIRARelationship
from .websocket import TibetWebSocket

# Backwards compatibility
TibetBettiClient = BETTIClient

__version__ = "2.0.0"
__all__ = [
    "TibetBettiClient",
    "Tibet",
    "TimeWindow",
    "Constraints",
    "Context",
    "SenseRule",
    "TrustToken",
    "FIRARelationship",
    "TibetWebSocket"
]
