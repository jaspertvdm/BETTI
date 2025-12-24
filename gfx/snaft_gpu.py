"""
SNAFT GPU Firewall - Semantic GPU Protection
============================================
Anti-cryptojacking, anti-abuse, intent-based access control.

SNAFT = Semantic Network for Autonomous Firewall & Telemetry
Kwalificeert GPU requests op basis van intent, niet alleen resources.
"""

from dataclasses import dataclass, field
from typing import List, Dict, Optional, Callable
from enum import Enum
from datetime import datetime, timedelta
import hashlib
import re


class ThreatLevel(Enum):
    SAFE = 0
    SUSPICIOUS = 1
    BLOCKED = 2
    QUARANTINE = 3


class GPUIntent(Enum):
    """Gekwalificeerde GPU intents - niet kwantiteit maar kwaliteit!"""
    INFERENCE = "inference"          # LLM inference
    TRANSCRIPTION = "transcription"  # Audio/video transcriptie
    EMBEDDING = "embedding"          # Vector embeddings
    TRAINING = "training"            # Model training (beperkt)
    VISION = "vision"                # Image/video analyse
    CRYPTO = "crypto"                # BLOCKED - cryptomining
    UNKNOWN = "unknown"              # Ongekwalificeerd


@dataclass
class GPURequest:
    """Inkomende GPU request voor SNAFT analyse."""
    intent: GPUIntent
    model_name: str
    actor: str
    vram_requested: int  # MB
    estimated_duration: float  # seconds
    tibet_token_id: Optional[str] = None
    metadata: Dict = field(default_factory=dict)
    timestamp: datetime = field(default_factory=datetime.now)


@dataclass
class SNAFTVerdict:
    """SNAFT beslissing over GPU request."""
    allowed: bool
    threat_level: ThreatLevel
    reason: str
    restrictions: Dict = field(default_factory=dict)
    expires_at: Optional[datetime] = None


class SNAFTGPUFirewall:
    """
    SNAFT GPU Firewall - Semantic protection layer.
    
    Principes:
    1. Intent-first: Wat wil je doen, niet hoeveel?
    2. Actor trust: TIBET-gevalideerde actors krijgen meer ruimte
    3. Pattern detection: Herken misbruik patronen
    4. Budget awareness: Respecteer BETTI budgetten
    """
    
    # Bekende cryptomining patterns
    CRYPTO_PATTERNS = [
        r"xmrig", r"ethminer", r"phoenixminer", r"trex",
        r"nicehash", r"kawpow", r"randomx", r"ethash",
        r"cryptonight", r"equihash", r"beam", r"grin"
    ]
    
    # Verdachte model namen
    SUSPICIOUS_MODELS = [
        r".*miner.*", r".*hash.*", r".*coin.*",
        r".*benchmark.*loop.*"
    ]
    
    # Toegestane intents met VRAM limieten (MB)
    INTENT_LIMITS = {
        GPUIntent.INFERENCE: 8000,      # 8GB max per inference
        GPUIntent.TRANSCRIPTION: 4000,  # 4GB voor whisper
        GPUIntent.EMBEDDING: 2000,      # 2GB voor embeddings
        GPUIntent.VISION: 6000,         # 6GB voor vision models
        GPUIntent.TRAINING: 10000,      # 10GB voor training (special permission)
        GPUIntent.CRYPTO: 0,            # ZERO - altijd blocked
        GPUIntent.UNKNOWN: 1000,        # 1GB voor unknown (restrictief)
    }
    
    def __init__(self, 
                 trust_threshold: float = 0.5,
                 max_duration: float = 3600.0,  # 1 hour max
                 rate_limit_per_minute: int = 10):
        self.trust_threshold = trust_threshold
        self.max_duration = max_duration
        self.rate_limit = rate_limit_per_minute
        self.request_history: List[GPURequest] = []
        self.blocked_actors: Dict[str, datetime] = {}
        self.trust_scores: Dict[str, float] = {}
    
    def analyze(self, request: GPURequest) -> SNAFTVerdict:
        """
        Analyseer GPU request en geef verdict.
        
        Returns:
            SNAFTVerdict met allowed/blocked en reden
        """
        # Check 1: Actor blocked?
        if request.actor in self.blocked_actors:
            if datetime.now() < self.blocked_actors[request.actor]:
                return SNAFTVerdict(
                    allowed=False,
                    threat_level=ThreatLevel.BLOCKED,
                    reason=f"Actor '{request.actor}' is geblokkeerd tot {self.blocked_actors[request.actor]}"
                )
            else:
                del self.blocked_actors[request.actor]
        
        # Check 2: Crypto intent = instant block
        if request.intent == GPUIntent.CRYPTO:
            self._block_actor(request.actor, hours=24)
            return SNAFTVerdict(
                allowed=False,
                threat_level=ThreatLevel.BLOCKED,
                reason="Cryptomining intent gedetecteerd - BLOCKED"
            )
        
        # Check 3: Model naam crypto patterns
        for pattern in self.CRYPTO_PATTERNS:
            if re.search(pattern, request.model_name.lower()):
                self._block_actor(request.actor, hours=24)
                return SNAFTVerdict(
                    allowed=False,
                    threat_level=ThreatLevel.BLOCKED,
                    reason=f"Crypto pattern '{pattern}' in model naam - BLOCKED"
                )
        
        # Check 4: Verdachte model namen
        for pattern in self.SUSPICIOUS_MODELS:
            if re.match(pattern, request.model_name.lower()):
                return SNAFTVerdict(
                    allowed=False,
                    threat_level=ThreatLevel.SUSPICIOUS,
                    reason=f"Verdacht model pattern '{pattern}' - DENIED"
                )
        
        # Check 5: VRAM limiet per intent
        vram_limit = self.INTENT_LIMITS.get(request.intent, 1000)
        if request.vram_requested > vram_limit:
            return SNAFTVerdict(
                allowed=False,
                threat_level=ThreatLevel.SUSPICIOUS,
                reason=f"VRAM request ({request.vram_requested}MB) overschrijdt limiet ({vram_limit}MB) voor {request.intent.value}"
            )
        
        # Check 6: Duration limiet
        if request.estimated_duration > self.max_duration:
            return SNAFTVerdict(
                allowed=True,  # Toegestaan maar met restrictie
                threat_level=ThreatLevel.SUSPICIOUS,
                reason=f"Duration beperkt tot {self.max_duration}s",
                restrictions={"max_duration": self.max_duration},
                expires_at=datetime.now() + timedelta(seconds=self.max_duration)
            )
        
        # Check 7: Rate limiting
        recent_requests = [r for r in self.request_history 
                         if r.actor == request.actor 
                         and (datetime.now() - r.timestamp).seconds < 60]
        if len(recent_requests) >= self.rate_limit:
            return SNAFTVerdict(
                allowed=False,
                threat_level=ThreatLevel.SUSPICIOUS,
                reason=f"Rate limit bereikt ({self.rate_limit}/min) voor actor '{request.actor}'"
            )
        
        # Check 8: Trust score (TIBET integration)
        trust = self.trust_scores.get(request.actor, 0.5)
        if trust < self.trust_threshold:
            return SNAFTVerdict(
                allowed=True,
                threat_level=ThreatLevel.SUSPICIOUS,
                reason=f"Low trust ({trust:.2f}) - beperkte resources",
                restrictions={
                    "vram_limit": min(request.vram_requested, 2000),
                    "duration_limit": min(request.estimated_duration, 300)
                }
            )
        
        # All checks passed!
        self.request_history.append(request)
        return SNAFTVerdict(
            allowed=True,
            threat_level=ThreatLevel.SAFE,
            reason="Request goedgekeurd",
            expires_at=datetime.now() + timedelta(seconds=request.estimated_duration)
        )
    
    def _block_actor(self, actor: str, hours: int = 24):
        """Blokkeer actor voor X uur."""
        self.blocked_actors[actor] = datetime.now() + timedelta(hours=hours)
    
    def set_trust(self, actor: str, score: float):
        """Set trust score voor actor (0.0 - 1.0)."""
        self.trust_scores[actor] = max(0.0, min(1.0, score))
    
    def get_stats(self) -> Dict:
        """Return firewall statistieken."""
        return {
            "total_requests": len(self.request_history),
            "blocked_actors": len(self.blocked_actors),
            "trust_scores": dict(self.trust_scores),
            "recent_requests": len([r for r in self.request_history 
                                    if (datetime.now() - r.timestamp).seconds < 3600])
        }


# Quick test
if __name__ == "__main__":
    firewall = SNAFTGPUFirewall()
    
    # Good request
    good = GPURequest(
        intent=GPUIntent.INFERENCE,
        model_name="phi3:security",
        actor="brain_api",
        vram_requested=3500,
        estimated_duration=30.0
    )
    print(f"Good: {firewall.analyze(good)}")
    
    # Crypto attempt
    crypto = GPURequest(
        intent=GPUIntent.CRYPTO,
        model_name="xmrig-cuda",
        actor="malicious_actor",
        vram_requested=8000,
        estimated_duration=86400.0
    )
    print(f"Crypto: {firewall.analyze(crypto)}")
    
    # Whisper transcription
    whisper = GPURequest(
        intent=GPUIntent.TRANSCRIPTION,
        model_name="faster-whisper-large-v3",
        actor="oomllama",
        vram_requested=3800,
        estimated_duration=120.0
    )
    print(f"Whisper: {firewall.analyze(whisper)}")
