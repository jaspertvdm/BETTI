"""
BETTI Lazy GPU Loader - Intent-Based Layer Streaming
=====================================================

CPU <RAM<>RAM<>RAM<>RAM> GPU BOEM!

Geen "dump alles in VRAM" maar intelligent layer-by-layer laden.
Quad-channel RAM als staging area voor GPU streaming.

Jasper's visie: Kwalisatie niet kwantisatie!
"""

from dataclasses import dataclass, field
from typing import Dict, List, Optional, Callable, Any
from enum import Enum
from datetime import datetime
import threading
import time


class LayerState(Enum):
    DISK = "disk"          # Op NVMe, niet geladen
    RAM_STAGING = "ram"    # In RAM staging buffer
    GPU_LOADING = "loading" # Bezig met GPU transfer
    GPU_READY = "ready"     # In VRAM, klaar voor inference
    GPU_ACTIVE = "active"   # Actief in gebruik
    EVICTING = "evicting"   # Wordt verwijderd uit VRAM


@dataclass
class ModelLayer:
    """Een laag van een model (attention, FFN, embedding, etc)."""
    name: str
    size_mb: float
    layer_type: str  # "attention", "ffn", "embedding", "lm_head"
    state: LayerState = LayerState.DISK
    priority: int = 5  # 1=highest, 10=lowest
    last_used: Optional[datetime] = None
    load_time_ms: float = 0
    
    def is_in_vram(self) -> bool:
        return self.state in [LayerState.GPU_READY, LayerState.GPU_ACTIVE]


@dataclass
class StreamingBuffer:
    """Quad-channel RAM buffer voor GPU streaming."""
    channel_count: int = 4
    channel_size_mb: int = 16000  # 64GB / 4 = 16GB per channel
    used_per_channel: List[float] = field(default_factory=lambda: [0, 0, 0, 0])
    
    def get_free_channel(self) -> Optional[int]:
        """Vind vrij kanaal voor streaming."""
        for i, used in enumerate(self.used_per_channel):
            if used < self.channel_size_mb * 0.8:  # 80% threshold
                return i
        return None
    
    def total_used(self) -> float:
        return sum(self.used_per_channel)
    
    def total_capacity(self) -> float:
        return self.channel_count * self.channel_size_mb


class LazyGPULoader:
    """
    Lazy GPU Loader - Layer-by-layer intelligent loading.
    
    Principe: Laad alleen wat je NODIG hebt, wanneer je het nodig hebt.
    
    Flow:
    1. Intent komt binnen (TIBET token)
    2. Bepaal welke layers nodig zijn
    3. Stream layers via RAM buffer naar GPU
    4. Voer inference uit
    5. Evict unused layers (LRU)
    
    Jasper's quad-channel concept:
    CPU <RAM<>RAM<>RAM<>RAM> GPU
    
    Elke RAM channel kan parallel streamen naar GPU!
    """
    
    def __init__(self,
                 gpu_vram_mb: int = 12000,
                 ram_buffer: Optional[StreamingBuffer] = None,
                 prefetch_next_n: int = 2):
        self.gpu_vram_mb = gpu_vram_mb
        self.ram_buffer = ram_buffer or StreamingBuffer()
        self.prefetch_n = prefetch_next_n
        
        self.models: Dict[str, List[ModelLayer]] = {}
        self.vram_used: float = 0
        self.load_queue: List[ModelLayer] = []
        self.eviction_lock = threading.Lock()
        
        # Stats
        self.stats = {
            "layers_loaded": 0,
            "layers_evicted": 0,
            "cache_hits": 0,
            "cache_misses": 0,
            "prefetch_hits": 0
        }
    
    def register_model(self, model_name: str, layers: List[Dict]) -> bool:
        """
        Registreer model met zijn layers.
        
        layers = [
            {"name": "embed", "size_mb": 256, "type": "embedding"},
            {"name": "layer.0.attn", "size_mb": 512, "type": "attention"},
            ...
        ]
        """
        model_layers = []
        for i, layer in enumerate(layers):
            model_layers.append(ModelLayer(
                name=layer["name"],
                size_mb=layer["size_mb"],
                layer_type=layer.get("type", "unknown"),
                priority=i + 1  # Earlier layers = higher priority
            ))
        self.models[model_name] = model_layers
        return True
    
    def prepare_for_intent(self, model_name: str, intent: str) -> Dict:
        """
        Bereid model voor op basis van intent.
        
        Different intents need different layers:
        - "inference": All layers sequentially
        - "embedding": Only embedding layer
        - "completion": Focus on attention + lm_head
        """
        if model_name not in self.models:
            return {"error": f"Model '{model_name}' niet geregistreerd"}
        
        layers = self.models[model_name]
        layers_needed = []
        
        if intent == "embedding":
            # Alleen embedding layer
            layers_needed = [l for l in layers if l.layer_type == "embedding"]
        elif intent == "completion":
            # Attention en lm_head prioriteit
            layers_needed = [l for l in layers 
                           if l.layer_type in ["attention", "lm_head", "embedding"]]
        else:
            # Full inference - all layers
            layers_needed = layers
        
        # Load strategy
        result = {
            "model": model_name,
            "intent": intent,
            "layers_needed": len(layers_needed),
            "total_size_mb": sum(l.size_mb for l in layers_needed),
            "already_loaded": 0,
            "to_load": 0,
            "estimated_load_time_ms": 0
        }
        
        for layer in layers_needed:
            if layer.is_in_vram():
                result["already_loaded"] += 1
                self.stats["cache_hits"] += 1
            else:
                result["to_load"] += 1
                self.stats["cache_misses"] += 1
                # Estimate: ~2GB/s PCIe transfer
                result["estimated_load_time_ms"] += (layer.size_mb / 2000) * 1000
        
        return result
    
    def load_layer(self, model_name: str, layer_name: str) -> bool:
        """Load specifieke layer naar VRAM."""
        if model_name not in self.models:
            return False
        
        layer = next((l for l in self.models[model_name] if l.name == layer_name), None)
        if not layer:
            return False
        
        if layer.is_in_vram():
            layer.last_used = datetime.now()
            return True  # Already loaded
        
        # Check VRAM space
        if self.vram_used + layer.size_mb > self.gpu_vram_mb:
            # Need to evict
            self._evict_lru(layer.size_mb)
        
        # Simulate loading via RAM buffer
        channel = self.ram_buffer.get_free_channel()
        if channel is not None:
            self.ram_buffer.used_per_channel[channel] += layer.size_mb
        
        # Transfer to GPU
        layer.state = LayerState.GPU_LOADING
        # Simulate transfer time
        time.sleep(layer.size_mb / 5000)  # ~5GB/s simulated
        
        layer.state = LayerState.GPU_READY
        layer.last_used = datetime.now()
        self.vram_used += layer.size_mb
        self.stats["layers_loaded"] += 1
        
        # Clean RAM buffer
        if channel is not None:
            self.ram_buffer.used_per_channel[channel] -= layer.size_mb
        
        return True
    
    def _evict_lru(self, need_mb: float):
        """Evict least-recently-used layers tot er genoeg ruimte is."""
        with self.eviction_lock:
            # Collect all loaded layers across all models
            all_loaded = []
            for model_name, layers in self.models.items():
                for layer in layers:
                    if layer.is_in_vram():
                        all_loaded.append((model_name, layer))
            
            # Sort by last_used (oldest first)
            all_loaded.sort(key=lambda x: x[1].last_used or datetime.min)
            
            freed = 0
            for model_name, layer in all_loaded:
                if freed >= need_mb:
                    break
                
                layer.state = LayerState.EVICTING
                self.vram_used -= layer.size_mb
                freed += layer.size_mb
                layer.state = LayerState.DISK
                self.stats["layers_evicted"] += 1
    
    def prefetch(self, model_name: str, current_layer_idx: int):
        """Prefetch volgende N layers in achtergrond."""
        if model_name not in self.models:
            return
        
        layers = self.models[model_name]
        for i in range(self.prefetch_n):
            next_idx = current_layer_idx + i + 1
            if next_idx < len(layers):
                layer = layers[next_idx]
                if not layer.is_in_vram():
                    # Queue for background load
                    self.load_queue.append(layer)
    
    def get_vram_status(self) -> Dict:
        """Return current VRAM status."""
        layers_in_vram = []
        for model_name, layers in self.models.items():
            for layer in layers:
                if layer.is_in_vram():
                    layers_in_vram.append({
                        "model": model_name,
                        "layer": layer.name,
                        "size_mb": layer.size_mb,
                        "state": layer.state.value,
                        "last_used": layer.last_used.isoformat() if layer.last_used else None
                    })
        
        return {
            "total_vram_mb": self.gpu_vram_mb,
            "used_vram_mb": round(self.vram_used, 1),
            "free_vram_mb": round(self.gpu_vram_mb - self.vram_used, 1),
            "usage_pct": round((self.vram_used / self.gpu_vram_mb) * 100, 1),
            "layers_in_vram": len(layers_in_vram),
            "layers": layers_in_vram,
            "ram_buffer_used_mb": round(self.ram_buffer.total_used(), 1),
            "stats": self.stats
        }


# Demo
if __name__ == "__main__":
    print("=== BETTI Lazy GPU Loader Demo ===")
    print("CPU <RAM<>RAM<>RAM<>RAM> GPU BOEM!\n")
    
    loader = LazyGPULoader(gpu_vram_mb=12000)
    
    # Register phi3:security model layers (simulated)
    phi3_layers = [
        {"name": "embed_tokens", "size_mb": 256, "type": "embedding"},
        {"name": "layer.0.self_attn", "size_mb": 384, "type": "attention"},
        {"name": "layer.0.mlp", "size_mb": 512, "type": "ffn"},
        {"name": "layer.1.self_attn", "size_mb": 384, "type": "attention"},
        {"name": "layer.1.mlp", "size_mb": 512, "type": "ffn"},
        {"name": "layer.2.self_attn", "size_mb": 384, "type": "attention"},
        {"name": "layer.2.mlp", "size_mb": 512, "type": "ffn"},
        {"name": "lm_head", "size_mb": 256, "type": "lm_head"},
    ]
    loader.register_model("phi3:security", phi3_layers)
    
    # Register whisper large-v3 (simulated)
    whisper_layers = [
        {"name": "encoder.embed", "size_mb": 512, "type": "embedding"},
        {"name": "encoder.layers.0-7", "size_mb": 1024, "type": "attention"},
        {"name": "encoder.layers.8-15", "size_mb": 1024, "type": "attention"},
        {"name": "encoder.layers.16-23", "size_mb": 1024, "type": "attention"},
        {"name": "decoder.layers.0-7", "size_mb": 512, "type": "attention"},
        {"name": "decoder.layers.8-15", "size_mb": 512, "type": "attention"},
    ]
    loader.register_model("whisper-large-v3", whisper_layers)
    
    # Prepare for different intents
    print("Intent: embedding only")
    result = loader.prepare_for_intent("phi3:security", "embedding")
    print(f"  Layers needed: {result['layers_needed']}")
    print(f"  Size: {result['total_size_mb']}MB")
    
    print("\nIntent: full inference")
    result = loader.prepare_for_intent("phi3:security", "inference")
    print(f"  Layers needed: {result['layers_needed']}")
    print(f"  Size: {result['total_size_mb']}MB")
    print(f"  Est. load time: {result['estimated_load_time_ms']:.0f}ms")
    
    print("\nIntent: whisper transcription")
    result = loader.prepare_for_intent("whisper-large-v3", "inference")
    print(f"  Layers needed: {result['layers_needed']}")
    print(f"  Size: {result['total_size_mb']}MB")
    
    # VRAM status
    print("\n=== VRAM Status ===")
    import json
    status = loader.get_vram_status()
    print(f"Used: {status['used_vram_mb']}MB / {status['total_vram_mb']}MB ({status['usage_pct']}%)")
    print(f"Cache hits: {status['stats']['cache_hits']}, misses: {status['stats']['cache_misses']}")
