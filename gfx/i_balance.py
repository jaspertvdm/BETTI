"""
I-Balance: GPU Load Balancing via I-Poll
=========================================

Geen hardware SLI bridge nodig - software load balancing via RABEL I-Poll!

GPU nodes communiceren via I-Poll:
- JTel-brain (P2000): Security validation, light inference
- OomLlama (RTX 3060): Heavy inference, transcription, 70B warm
- Future: raspBETTI, more nodes...

"Je hoeft niet één 4090 te kopen als je 4x 3060 hebt" - Jasper
"""

from dataclasses import dataclass, field
from typing import Dict, List, Optional, Tuple
from datetime import datetime
from enum import Enum
import json


class GPUNodeStatus(Enum):
    IDLE = "idle"            # Geen actieve taken
    BUSY = "busy"            # Bezig maar kan meer
    OVERLOADED = "overloaded" # Te druk, geen nieuwe taken
    OFFLINE = "offline"       # Niet bereikbaar


@dataclass
class GPUNode:
    """Een GPU node in het netwerk."""
    name: str
    host: str
    port: int = 11434
    
    # Hardware specs
    gpu_model: str = ""
    vram_mb: int = 0
    ram_mb: int = 0
    
    # Current state
    status: GPUNodeStatus = GPUNodeStatus.OFFLINE
    vram_used_mb: int = 0
    current_tasks: int = 0
    
    # Capabilities
    capabilities: List[str] = field(default_factory=list)
    warm_models: List[str] = field(default_factory=list)
    
    # I-Poll address
    ipoll_actor: str = ""
    
    # Stats
    last_heartbeat: Optional[datetime] = None
    tasks_completed: int = 0
    avg_latency_ms: float = 0
    
    def load_factor(self) -> float:
        """Return load factor 0.0-1.0."""
        if self.vram_mb == 0:
            return 1.0
        return self.vram_used_mb / self.vram_mb
    
    def can_accept(self, vram_needed: int) -> bool:
        """Kan deze node de taak accepteren?"""
        if self.status in [GPUNodeStatus.OVERLOADED, GPUNodeStatus.OFFLINE]:
            return False
        return (self.vram_mb - self.vram_used_mb) >= vram_needed


@dataclass
class BalanceDecision:
    """I-Balance routing beslissing."""
    target_node: str
    reason: str
    estimated_wait_ms: float
    fallback_node: Optional[str] = None


class IBalance:
    """
    I-Balance: Software SLI via I-Poll.
    
    Routes GPU tasks naar beste beschikbare node gebaseerd op:
    1. Current load (VRAM usage, active tasks)
    2. Warm models (avoid cold starts)
    3. Capabilities (transcription, security, etc)
    4. Network latency
    
    Communiceert via RABEL I-Poll:
    - BALANCE_REQUEST: Vraag om beste node
    - BALANCE_ACCEPT: Node accepteert taak
    - BALANCE_HEARTBEAT: Status update
    - BALANCE_OFFLOAD: Stuur taak naar andere node
    """
    
    def __init__(self):
        self.nodes: Dict[str, GPUNode] = {}
        self.routing_history: List[Dict] = []
        
        # Pre-configure known nodes
        self._init_known_nodes()
    
    def _init_known_nodes(self):
        """Initialize bekende GPU nodes."""
        # JTel-brain - Quadro P2000
        self.register_node(GPUNode(
            name="jtel-brain",
            host="localhost",
            port=11434,
            gpu_model="Quadro P2000",
            vram_mb=5120,
            ram_mb=32000,
            capabilities=["security", "inference", "embedding"],
            warm_models=["phi3:security"],
            ipoll_actor="brain"
        ))
        
        # OomLlama - RTX 3060 12GB
        self.register_node(GPUNode(
            name="oomllama",
            host="192.168.4.85",
            port=11434,
            gpu_model="RTX 3060",
            vram_mb=12288,
            ram_mb=64000,
            capabilities=["transcription", "inference", "heavy", "70b-staging"],
            warm_models=["qwen2.5:7b"],
            ipoll_actor="oomllama"
        ))
        
        # Future: raspBETTI
        # self.register_node(GPUNode(
        #     name="raspbetti",
        #     host="192.168.4.75",
        #     ...
        # ))
    
    def register_node(self, node: GPUNode):
        """Register GPU node."""
        self.nodes[node.name] = node
    
    def update_status(self, node_name: str, status: Dict):
        """Update node status (from I-Poll heartbeat)."""
        if node_name not in self.nodes:
            return
        
        node = self.nodes[node_name]
        node.vram_used_mb = status.get("vram_used_mb", 0)
        node.current_tasks = status.get("current_tasks", 0)
        node.last_heartbeat = datetime.now()
        
        # Determine status
        load = node.load_factor()
        if load > 0.9:
            node.status = GPUNodeStatus.OVERLOADED
        elif load > 0.5:
            node.status = GPUNodeStatus.BUSY
        else:
            node.status = GPUNodeStatus.IDLE
    
    def route(self, 
              task_type: str,
              vram_needed: int = 2000,
              preferred_model: Optional[str] = None) -> BalanceDecision:
        """
        Route taak naar beste GPU node.
        
        Strategie:
        1. Als preferred_model warm is ergens -> die node
        2. Anders: laagste load die capability heeft
        3. Fallback: queue op drukste node
        """
        candidates = []
        
        for name, node in self.nodes.items():
            if node.status == GPUNodeStatus.OFFLINE:
                continue
            
            # Check capability
            if task_type not in node.capabilities and "heavy" not in node.capabilities:
                continue
            
            # Check warm model preference
            model_warm = preferred_model in node.warm_models if preferred_model else False
            
            candidates.append({
                "name": name,
                "node": node,
                "load": node.load_factor(),
                "can_accept": node.can_accept(vram_needed),
                "model_warm": model_warm
            })
        
        if not candidates:
            return BalanceDecision(
                target_node="",
                reason="Geen beschikbare GPU nodes",
                estimated_wait_ms=float("inf")
            )
        
        # Prioritize warm models
        warm_candidates = [c for c in candidates if c["model_warm"]]
        if warm_candidates:
            best = min(warm_candidates, key=lambda x: x["load"])
            return BalanceDecision(
                target_node=best["name"],
                reason=f"Model '{preferred_model}' is warm op {best['name']}",
                estimated_wait_ms=best["load"] * 1000
            )
        
        # Otherwise lowest load that can accept
        accepting = [c for c in candidates if c["can_accept"]]
        if accepting:
            best = min(accepting, key=lambda x: x["load"])
            return BalanceDecision(
                target_node=best["name"],
                reason=f"Laagste load ({best['load']:.1%}) met capaciteit",
                estimated_wait_ms=best["load"] * 500,
                fallback_node=candidates[0]["name"] if len(candidates) > 1 else None
            )
        
        # Queue on least loaded
        best = min(candidates, key=lambda x: x["load"])
        return BalanceDecision(
            target_node=best["name"],
            reason=f"Alle nodes druk, queue op {best['name']}",
            estimated_wait_ms=(best["load"] + 0.5) * 2000
        )
    
    def create_ipoll_message(self, msg_type: str, content: Dict) -> Dict:
        """Create I-Poll message voor GPU balancing."""
        return {
            "type": f"BALANCE_{msg_type}",
            "timestamp": datetime.now().isoformat(),
            "content": content,
            "protocol": "i-balance",
            "version": "0.1.0"
        }
    
    def get_cluster_status(self) -> Dict:
        """Return cluster-wide GPU status."""
        total_vram = sum(n.vram_mb for n in self.nodes.values())
        used_vram = sum(n.vram_used_mb for n in self.nodes.values())
        
        return {
            "cluster": {
                "total_vram_gb": round(total_vram / 1024, 1),
                "used_vram_gb": round(used_vram / 1024, 1),
                "utilization": round((used_vram / total_vram * 100) if total_vram > 0 else 0, 1),
                "nodes_online": sum(1 for n in self.nodes.values() 
                                    if n.status != GPUNodeStatus.OFFLINE)
            },
            "nodes": {
                name: {
                    "gpu": node.gpu_model,
                    "status": node.status.value,
                    "load": f"{node.load_factor():.1%}",
                    "vram": f"{node.vram_used_mb}/{node.vram_mb}MB",
                    "warm_models": node.warm_models,
                    "capabilities": node.capabilities
                }
                for name, node in self.nodes.items()
            }
        }


# Demo
if __name__ == "__main__":
    print("=== I-Balance: Software SLI via I-Poll ===")
    print("\n'Je hoeft niet één 4090 te kopen als je 4x 3060 hebt' - Jasper\n")
    
    balance = IBalance()
    
    # Simulate current loads
    balance.update_status("jtel-brain", {"vram_used_mb": 4000, "current_tasks": 1})
    balance.update_status("oomllama", {"vram_used_mb": 4500, "current_tasks": 1})
    
    # Cluster status
    print("Cluster Status:")
    import json
    print(json.dumps(balance.get_cluster_status(), indent=2))
    
    # Route decisions
    print("\n--- Routing Tests ---")
    
    # Security task
    decision = balance.route("security", vram_needed=3500, preferred_model="phi3:security")
    print(f"\nSecurity validation:")
    print(f"  -> {decision.target_node}: {decision.reason}")
    
    # Transcription task  
    decision = balance.route("transcription", vram_needed=4000)
    print(f"\nTranscription:")
    print(f"  -> {decision.target_node}: {decision.reason}")
    
    # Heavy inference (70B)
    decision = balance.route("heavy", vram_needed=8000, preferred_model="llama3.1:70b")
    print(f"\n70B inference:")
    print(f"  -> {decision.target_node}: {decision.reason}")
