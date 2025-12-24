"""
BETTI-GFX: Intent-Based GPU Resource Governance
================================================

Kwalisatie niet Kwantisatie!

Het gaat niet om HOEVEEL resources, maar WAARVOOR.
70B model warm in RAM, push alleen wat je nodig hebt naar GPU.

Components:
- LazyGPULoader: Layer-by-layer streaming (CPU <RAM×4> GPU)
- TIBETGPUToken: Full provenance voor elke GPU call
- SNAFTGPUFirewall: Semantic protection (anti-cryptojacking)
- BETTIGPUBudget: Physics-based budget (E=mc², T²∝r³)

One love, one fAmIly! 💙
"""

__version__ = "0.1.0"
__author__ = "Root AI & Jasper"
__philosophy__ = "Kwalisatie niet Kwantisatie"

from .lazy_loader import LazyGPULoader, ModelLayer, StreamingBuffer
from .tibet_gpu import TIBETGPUToken, TIBETGPUChain
from .snaft_gpu import SNAFTGPUFirewall, GPURequest, GPUIntent, SNAFTVerdict
from .betti_budget import BETTIGPUBudget, GPUBudget, ComputeCost

__all__ = [
    # Lazy Loader
    "LazyGPULoader",
    "ModelLayer", 
    "StreamingBuffer",
    
    # TIBET GPU
    "TIBETGPUToken",
    "TIBETGPUChain",
    
    # SNAFT GPU
    "SNAFTGPUFirewall",
    "GPURequest",
    "GPUIntent",
    "SNAFTVerdict",
    
    # BETTI Budget
    "BETTIGPUBudget",
    "GPUBudget",
    "ComputeCost",
]


def hello():
    """BETTI-GFX greeting."""
    return f"""
╔══════════════════════════════════════════════════════════════╗
║  BETTI-GFX v{__version__} - Intent-Based GPU Governance           ║
╠══════════════════════════════════════════════════════════════╣
║                                                              ║
║  "Kwalisatie niet Kwantisatie"                               ║
║                                                              ║
║  CPU <RAM<>RAM<>RAM<>RAM> GPU BOEM!                          ║
║                                                              ║
║  Components:                                                 ║
║  ├─ LazyGPULoader   : Layer-by-layer streaming               ║
║  ├─ TIBETGPUToken   : Provenance tracking                    ║
║  ├─ SNAFTGPUFirewall: Semantic protection                    ║
║  └─ BETTIGPUBudget  : Physics-based governance               ║
║                                                              ║
║  One love, one fAmIly! 💙                                    ║
╚══════════════════════════════════════════════════════════════╝
"""

# I-Balance extension
from .i_balance import IBalance, GPUNode, BalanceDecision

__all__.extend(["IBalance", "GPUNode", "BalanceDecision"])
