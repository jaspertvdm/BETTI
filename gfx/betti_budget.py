"""
BETTI GPU Budget - Physics-Based Resource Governance
=====================================================
E=mc² voor GPU resources: Energy = Model × Compute²

Budget enforcement met natuurkundige wetten omdat die ALTIJD werken.
Kepler's T²∝r³: Orbit time squared proportional to distance cubed.

BETTI = Budget Enforcement Through Transparent Intent
"""

from dataclasses import dataclass, field
from typing import Dict, List, Optional, Tuple
from datetime import datetime, timedelta
from enum import Enum
import math


class BudgetState(Enum):
    GREEN = "green"      # Ruim binnen budget
    YELLOW = "yellow"    # 70-90% budget
    ORANGE = "orange"    # 90-99% budget  
    RED = "red"          # Budget overschreden
    BLOCKED = "blocked"  # Harde limiet bereikt


@dataclass
class GPUBudget:
    """Budget voor een actor/service."""
    actor: str
    
    # Dagbudget
    daily_vram_seconds: float = 3600_000  # 1000 GB-seconds per dag
    daily_compute_units: float = 10000    # Abstracte compute units
    
    # Huidige verbruik
    used_vram_seconds: float = 0
    used_compute_units: float = 0
    
    # Physics parameters
    priority_orbit: int = 1  # 1=closest (highest priority), 10=furthest
    mass: float = 1.0        # Relatieve "massa" (importance)
    
    # Tracking
    last_reset: datetime = field(default_factory=datetime.now)
    last_request: Optional[datetime] = None
    request_count: int = 0
    
    def get_remaining_vram_seconds(self) -> float:
        return max(0, self.daily_vram_seconds - self.used_vram_seconds)
    
    def get_remaining_compute(self) -> float:
        return max(0, self.daily_compute_units - self.used_compute_units)
    
    def get_usage_percentage(self) -> float:
        vram_pct = (self.used_vram_seconds / self.daily_vram_seconds) * 100
        compute_pct = (self.used_compute_units / self.daily_compute_units) * 100
        return max(vram_pct, compute_pct)
    
    def get_state(self) -> BudgetState:
        pct = self.get_usage_percentage()
        if pct >= 100:
            return BudgetState.RED
        elif pct >= 90:
            return BudgetState.ORANGE
        elif pct >= 70:
            return BudgetState.YELLOW
        return BudgetState.GREEN


@dataclass
class ComputeCost:
    """Berekende kosten voor een GPU operatie."""
    vram_seconds: float      # VRAM × duration
    compute_units: float     # Model complexity × duration
    energy_cost: float       # E = m × c² (simplified)
    orbit_time: float        # Kepler T² ∝ r³
    allowed: bool
    reason: str


class BETTIGPUBudget:
    """
    BETTI GPU Budget Manager - Physics-based governance.
    
    Core formules:
    1. E = m × c² → Energy = ModelSize × ComputeIntensity²
    2. T² ∝ r³ → OrbitTime² ∝ PriorityDistance³ (queue priority)
    3. Conservation: Total budget is conserved, transfers possible
    
    Jasper's insight: "kwalisatie niet kwantisatie" 
    - We kwalificeren de INTENT, niet alleen de resources
    """
    
    # Physics constants (tuned for GPU)
    VRAM_TO_MASS = 0.001          # 1GB VRAM = 1.0 mass units
    COMPUTE_SPEED_OF_LIGHT = 100  # Max compute intensity
    KEPLER_CONSTANT = 1.0         # Orbital constant
    
    def __init__(self, 
                 total_vram_mb: int = 12000,  # RTX 3060 = 12GB
                 max_concurrent: int = 3):
        self.total_vram = total_vram_mb
        self.max_concurrent = max_concurrent
        self.budgets: Dict[str, GPUBudget] = {}
        self.active_jobs: List[Dict] = []
        self.daily_stats = {
            "total_vram_seconds": 0,
            "total_compute_units": 0,
            "total_requests": 0,
            "rejected_requests": 0
        }
    
    def register_actor(self, actor: str, 
                       daily_vram_seconds: float = 3600_000,
                       priority_orbit: int = 5,
                       mass: float = 1.0) -> GPUBudget:
        """Registreer actor met budget."""
        budget = GPUBudget(
            actor=actor,
            daily_vram_seconds=daily_vram_seconds,
            priority_orbit=priority_orbit,
            mass=mass
        )
        self.budgets[actor] = budget
        return budget
    
    def calculate_cost(self, 
                       actor: str,
                       vram_mb: int,
                       duration_seconds: float,
                       model_complexity: float = 1.0) -> ComputeCost:
        """
        Bereken de kosten van een GPU operatie.
        
        Physics:
        - E = m × c²: Energy scales with model size and compute squared
        - T² ∝ r³: Wait time scales with priority orbit cubed
        """
        if actor not in self.budgets:
            # Auto-register met default budget
            self.register_actor(actor)
        
        budget = self.budgets[actor]
        
        # VRAM-seconds (primary metric)
        vram_seconds = vram_mb * duration_seconds
        
        # E = m × c² 
        # m = model size (VRAM), c = compute intensity
        mass = vram_mb * self.VRAM_TO_MASS
        compute_intensity = min(model_complexity * 10, self.COMPUTE_SPEED_OF_LIGHT)
        energy_cost = mass * (compute_intensity ** 2)
        
        # Compute units (energy-based)
        compute_units = energy_cost * duration_seconds / 1000
        
        # Kepler's law: T² ∝ r³
        # Queue priority based on orbit position
        orbit_time = math.sqrt(self.KEPLER_CONSTANT * (budget.priority_orbit ** 3))
        
        # Check budget
        can_afford_vram = budget.get_remaining_vram_seconds() >= vram_seconds
        can_afford_compute = budget.get_remaining_compute() >= compute_units
        
        if not can_afford_vram:
            return ComputeCost(
                vram_seconds=vram_seconds,
                compute_units=compute_units,
                energy_cost=energy_cost,
                orbit_time=orbit_time,
                allowed=False,
                reason=f"VRAM budget overschreden: nodig {vram_seconds:.0f}, beschikbaar {budget.get_remaining_vram_seconds():.0f}"
            )
        
        if not can_afford_compute:
            return ComputeCost(
                vram_seconds=vram_seconds,
                compute_units=compute_units,
                energy_cost=energy_cost,
                orbit_time=orbit_time,
                allowed=False,
                reason=f"Compute budget overschreden: nodig {compute_units:.0f}, beschikbaar {budget.get_remaining_compute():.0f}"
            )
        
        return ComputeCost(
            vram_seconds=vram_seconds,
            compute_units=compute_units,
            energy_cost=energy_cost,
            orbit_time=orbit_time,
            allowed=True,
            reason="Budget OK"
        )
    
    def charge(self, actor: str, cost: ComputeCost) -> bool:
        """Debit budget voor uitgevoerde operatie."""
        if actor not in self.budgets:
            return False
        
        budget = self.budgets[actor]
        budget.used_vram_seconds += cost.vram_seconds
        budget.used_compute_units += cost.compute_units
        budget.request_count += 1
        budget.last_request = datetime.now()
        
        # Global stats
        self.daily_stats["total_vram_seconds"] += cost.vram_seconds
        self.daily_stats["total_compute_units"] += cost.compute_units
        self.daily_stats["total_requests"] += 1
        
        return True
    
    def get_queue_position(self, actor: str) -> Tuple[int, float]:
        """
        Bereken queue positie gebaseerd op Kepler orbit.
        
        Returns:
            (position, estimated_wait_seconds)
        """
        if actor not in self.budgets:
            return (999, float("inf"))
        
        budget = self.budgets[actor]
        
        # T² ∝ r³ → T = √(r³)
        base_wait = math.sqrt(budget.priority_orbit ** 3)
        
        # Adjust for mass (heavier = faster in our system, like gravity)
        wait_adjusted = base_wait / budget.mass
        
        # Calculate position among all actors
        all_waits = [(a, math.sqrt(b.priority_orbit ** 3) / b.mass) 
                     for a, b in self.budgets.items()]
        all_waits.sort(key=lambda x: x[1])
        
        position = next((i for i, (a, _) in enumerate(all_waits) if a == actor), 999)
        
        return (position + 1, wait_adjusted)
    
    def reset_daily_budgets(self):
        """Reset alle dagbudgetten (run at midnight)."""
        now = datetime.now()
        for budget in self.budgets.values():
            budget.used_vram_seconds = 0
            budget.used_compute_units = 0
            budget.last_reset = now
            budget.request_count = 0
        
        # Archive and reset stats
        archived = dict(self.daily_stats)
        self.daily_stats = {
            "total_vram_seconds": 0,
            "total_compute_units": 0,
            "total_requests": 0,
            "rejected_requests": 0
        }
        return archived
    
    def get_dashboard(self) -> Dict:
        """Return budget dashboard voor alle actors."""
        dashboard = {
            "total_vram_mb": self.total_vram,
            "active_jobs": len(self.active_jobs),
            "daily_stats": self.daily_stats,
            "actors": {}
        }
        
        for actor, budget in self.budgets.items():
            pos, wait = self.get_queue_position(actor)
            dashboard["actors"][actor] = {
                "state": budget.get_state().value,
                "usage_pct": round(budget.get_usage_percentage(), 1),
                "remaining_vram_sec": round(budget.get_remaining_vram_seconds()),
                "remaining_compute": round(budget.get_remaining_compute()),
                "queue_position": pos,
                "orbit_wait_sec": round(wait, 2),
                "requests_today": budget.request_count
            }
        
        return dashboard


# Demo
if __name__ == "__main__":
    betti = BETTIGPUBudget(total_vram_mb=12000)
    
    # Register actors met verschillende orbits
    betti.register_actor("brain_api", priority_orbit=1, mass=2.0)  # Closest, heavy
    betti.register_actor("whisper", priority_orbit=2, mass=1.5)    # Close
    betti.register_actor("external", priority_orbit=5, mass=0.5)   # Far, light
    
    # Calculate costs
    print("\n=== BETTI GPU Budget Demo ===")
    
    # Brain API inference
    cost = betti.calculate_cost("brain_api", vram_mb=3500, duration_seconds=5)
    print(f"\nBrain API inference (3.5GB, 5s):")
    print(f"  VRAM-seconds: {cost.vram_seconds:,.0f}")
    print(f"  Energy (E=mc²): {cost.energy_cost:,.2f}")
    print(f"  Orbit time: {cost.orbit_time:.2f}s")
    print(f"  Allowed: {cost.allowed}")
    
    # Whisper transcription
    cost = betti.calculate_cost("whisper", vram_mb=4000, duration_seconds=120)
    print(f"\nWhisper transcription (4GB, 120s):")
    print(f"  VRAM-seconds: {cost.vram_seconds:,.0f}")
    print(f"  Energy: {cost.energy_cost:,.2f}")
    print(f"  Allowed: {cost.allowed}")
    
    # Dashboard
    print(f"\n=== Dashboard ===")
    import json
    print(json.dumps(betti.get_dashboard(), indent=2))
