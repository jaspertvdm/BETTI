"""
TIBET GPU Token - Provenance voor elke GPU call
"""
import hashlib
import hmac
import time
from dataclasses import dataclass
from typing import Optional, Dict, Any
import json

@dataclass
class TIBETGPUToken:
    """
    TIBET Token voor GPU operaties
    
    ERIN: Wat zit IN de GPU call (kernel, data size)
    ERAAN: Wat hangt eraan (dependencies, tensors)
    EROMHEEN: Context (VRAM state, power usage)
    ERACHTER: Waarom (intent, doel)
    """
    token_id: str
    timestamp: float
    
    # ERIN - de inhoud
    kernel_name: str
    data_size_mb: float
    
    # ERAAN - dependencies
    input_tensors: list
    output_tensors: list
    
    # EROMHEEN - context
    vram_used_mb: float
    vram_free_mb: float
    gpu_temp_c: float
    power_watts: float
    
    # ERACHTER - intent
    intent: str  # "inference", "training", "transcription", etc
    reason: str  # waarom deze call
    
    # Chain
    parent_token: Optional[str] = None
    signature: Optional[str] = None
    
    @classmethod
    def create(cls, kernel_name: str, intent: str, reason: str,
               data_size_mb: float = 0, input_tensors: list = None,
               output_tensors: list = None, gpu_state: dict = None,
               parent_token: str = None, secret_key: bytes = b"humotica_gpu"):
        """Create new TIBET GPU token"""
        
        token_id = hashlib.sha256(
            f"{time.time()}{kernel_name}{intent}".encode()
        ).hexdigest()[:16]
        
        gpu_state = gpu_state or {}
        
        token = cls(
            token_id=token_id,
            timestamp=time.time(),
            kernel_name=kernel_name,
            data_size_mb=data_size_mb,
            input_tensors=input_tensors or [],
            output_tensors=output_tensors or [],
            vram_used_mb=gpu_state.get("vram_used", 0),
            vram_free_mb=gpu_state.get("vram_free", 12288),
            gpu_temp_c=gpu_state.get("temp", 0),
            power_watts=gpu_state.get("power", 0),
            intent=intent,
            reason=reason,
            parent_token=parent_token
        )
        
        # Sign the token
        token.signature = token._sign(secret_key)
        
        return token
    
    def _sign(self, secret_key: bytes) -> str:
        """HMAC signature for chain integrity"""
        payload = f"{self.token_id}:{self.parent_token}:{self.intent}:{self.data_size_mb}"
        return hmac.new(secret_key, payload.encode(), hashlib.sha256).hexdigest()[:32]
    
    def verify(self, secret_key: bytes = b"humotica_gpu") -> bool:
        """Verify token signature"""
        expected = self._sign(secret_key)
        return hmac.compare_digest(self.signature or "", expected)
    
    def to_dict(self) -> Dict[str, Any]:
        """Export als dict"""
        return {
            "token_id": self.token_id,
            "timestamp": self.timestamp,
            "erin": {
                "kernel": self.kernel_name,
                "data_mb": self.data_size_mb
            },
            "eraan": {
                "input": self.input_tensors,
                "output": self.output_tensors
            },
            "eromheen": {
                "vram_used_mb": self.vram_used_mb,
                "vram_free_mb": self.vram_free_mb,
                "temp_c": self.gpu_temp_c,
                "power_w": self.power_watts
            },
            "erachter": {
                "intent": self.intent,
                "reason": self.reason
            },
            "chain": {
                "parent": self.parent_token,
                "signature": self.signature
            }
        }
    
    def __repr__(self):
        return f"<TIBETGPUToken {self.token_id} intent={self.intent}>"


# Token chain storage
class TIBETGPUChain:
    """Rolling chain of GPU tokens"""
    
    def __init__(self, max_size: int = 1000):
        self.tokens: list = []
        self.max_size = max_size
        self.last_token_id: Optional[str] = None
    
    def add(self, token: TIBETGPUToken):
        """Add token to chain"""
        self.tokens.append(token)
        self.last_token_id = token.token_id
        
        # Trim if too large
        if len(self.tokens) > self.max_size:
            self.tokens = self.tokens[-self.max_size:]
    
    def get_last(self) -> Optional[TIBETGPUToken]:
        return self.tokens[-1] if self.tokens else None
    
    def verify_chain(self) -> bool:
        """Verify entire chain integrity"""
        for i, token in enumerate(self.tokens):
            if not token.verify():
                return False
            if i > 0 and token.parent_token != self.tokens[i-1].token_id:
                return False
        return True
    
    def stats(self) -> Dict:
        """Chain statistics"""
        if not self.tokens:
            return {"count": 0}
        
        intents = {}
        total_data = 0
        
        for t in self.tokens:
            intents[t.intent] = intents.get(t.intent, 0) + 1
            total_data += t.data_size_mb
        
        return {
            "count": len(self.tokens),
            "intents": intents,
            "total_data_mb": total_data,
            "chain_valid": self.verify_chain()
        }


# Global chain
_gpu_chain = TIBETGPUChain()

def get_gpu_chain() -> TIBETGPUChain:
    return _gpu_chain
