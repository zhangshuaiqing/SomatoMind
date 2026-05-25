"""
Brain — Core Engine

The Brain orchestrates perception → memory → cognition → action across two timescales:
  - Fast loop (reactive): perception → working memory → policy → action
  - Slow loop (deliberative): episodic memory → reasoning → planning → reflection → action modification

Design:
  1. Each cognitive function is a swappable module following CognitiveModule protocol
  2. Fast and slow loops run at different frequencies
  3. The Brain can inspect and modify its own components (meta-cognition)
"""

from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional, Protocol
from enum import Enum


class LoopMode(Enum):
    FAST = "fast"       # reactive: perception → working memory → policy → action
    SLOW = "slow"       # deliberative: episodic → reasoning → planning → reflection
    META = "meta"       # meta-cognitive: observe the observer, trigger plasticity


@dataclass
class BrainConfig:
    """Configuration for a Brain instance."""
    # Timescales
    fast_loop_interval: float = 0.1       # seconds between fast loop steps
    slow_loop_interval: int = 10          # fast loop steps between slow loops
    reflection_interval: int = 5          # fast loop steps between reflections
    
    # Memory sizing
    sensory_buffer_size: int = 1          # frames retained
    working_memory_size: int = 2048       # hidden state dimension
    episodic_memory_capacity: int = 100   # trajectories retained
    
    # Flags
    enable_plasticity: bool = False
    enable_spatial_world_model: bool = False
    enable_creativity: bool = False
    
    # Meta-cognition
    meta_interval: int = 50               # fast loop steps between meta evaluations


class CognitiveModule(Protocol):
    """Protocol that all cognitive modules must follow."""
    
    def reset(self):
        """Reset internal state for a new episode."""
        ...
    
    def forward(self, inputs: Dict[str, Any], state: Dict[str, Any]) -> tuple[Dict[str, Any], Dict[str, Any]]:
        """Process inputs and return (outputs, updated_state)."""
        ...


class Brain:
    """The SomatoMind Brain — a structured cognitive agent architecture.
    
    The Brain integrates perception, multi-level memory, cognition (reasoning,
    planning, reflection, spatial reasoning, creativity), and action into a
    unified, multi-timescale decision-making system.
    
    Usage:
        brain = Brain(config)
        for obs in environment:
            action = brain.step(obs)
    """
    
    def __init__(self, config: Optional[BrainConfig] = None):
        self.config = config or BrainConfig()
        self.step_count = 0
        self.loop_mode = LoopMode.FAST
        
        # Internal state
        self._current_percept: Dict = {}
        self._current_action: Any = None
        self._trajectory: List[Dict] = []
        self._last_reflection: Optional[str] = None
        
        # Module references (injected after construction)
        self.perception = None
        self.memory = None
        self.cognition = None
        self.action_module = None
        self.plasticity = None
    
    # ── Core Loop ──────────────────────────────────────────
    
    def step(self, observation: Any) -> Any:
        """One complete cognitive cycle.
        
        1. Perceive → update sensory buffer
        2. Working memory update (always runs)
        3. Fast loop: policy → action
        4. Periodic slow loop: reflect → reason → plan
        5. Periodic meta loop: evaluate overall performance
        """
        self.step_count += 1
        
        # 1. Perception
        self._current_percept = self._perceive(observation)
        
        # 2. Memory update
        self._update_sensory_buffer(self._current_percept)
        self._update_working_memory()
        
        # 3. Fast loop decision
        fast_action = self._fast_decision(self._current_percept)
        action = fast_action
        
        # 4. Slow loop (deliberative override)
        if self.step_count % self.config.slow_loop_interval == 0:
            slow_action = self._slow_deliberation()
            if slow_action is not None:
                action = slow_action
                self.loop_mode = LoopMode.SLOW
            else:
                self.loop_mode = LoopMode.FAST
        
        # 5. Periodic reflection (may run within or outside slow loop)
        if self.step_count % self.config.reflection_interval == 0:
            feedback = self._reflect()
            if feedback:
                self._apply_reflection(feedback)
        
        # 6. Periodic meta-cognition
        if self.step_count % self.config.meta_interval == 0:
            self._meta_evaluate()
        
        # 7. Store to episodic memory
        self._trajectory.append({
            "step": self.step_count,
            "percept": self._current_percept,
            "action": action,
            "loop_mode": self.loop_mode.value,
        })
        
        # 8. Motor output
        return self._act(action)
    
    # ── Perception ─────────────────────────────────────────
    
    def _perceive(self, observation: Any) -> Dict:
        """Adapter: normalize any observation into internal dict."""
        if self.perception is not None:
            out, _ = self.perception.forward({"raw": observation}, {})
            return out
        # Default: wrap raw observation
        return {"features": observation}
    
    # ── Memory ─────────────────────────────────────────────
    
    def _update_sensory_buffer(self, percept: Dict):
        if self.memory is not None:
            self.memory.sensory_buffer.write(percept)
    
    def _update_working_memory(self):
        if self.memory is not None:
            self.memory.working_memory.update(self._current_percept)
    
    # ── Decision ───────────────────────────────────────────
    
    def _fast_decision(self, percept: Dict) -> Any:
        """Fast reactive decision from policy."""
        if self.cognition is not None and hasattr(self.cognition, 'policy'):
            state = self.memory.working_memory.read() if self.memory else {}
            out, _ = self.cognition.policy.forward(percept, state)
            return out.get("action")
        return None
    
    def _slow_deliberation(self) -> Optional[Any]:
        """Slow deliberative decision involving reasoning + planning."""
        if self.cognition is None:
            return None
        
        # Retrieve recent episodic context
        recent = self._trajectory[-self.config.slow_loop_interval:] if self._trajectory else []
        
        # Reason about the situation
        if hasattr(self.cognition, 'reasoning'):
            out, _ = self.cognition.reasoning.forward(
                {"percept": self._current_percept, "trajectory": recent}, {}
            )
            reasoning_result = out.get("conclusion", "")
        else:
            reasoning_result = ""
        
        # Plan based on reasoning
        if hasattr(self.cognition, 'planning') and reasoning_result:
            out, _ = self.cognition.planning.forward(
                {"percept": self._current_percept, "reasoning": reasoning_result}, {}
            )
            return out.get("action")
        
        return reasoning_result
    
    def _reflect(self) -> Optional[str]:
        """Reflect on recent trajectory, return verbal feedback."""
        if self.cognition is None or not hasattr(self.cognition, 'reflection'):
            return None
        recent = self._trajectory[-self.config.reflection_interval:] if self._trajectory else []
        out, _ = self.cognition.reflection.forward({"trajectory": recent}, {})
        feedback = out.get("feedback")
        self._last_reflection = feedback
        return feedback
    
    def _apply_reflection(self, feedback: str):
        """Incorporate reflective feedback into cognitive modules."""
        # Strategy: adjust working memory, policy parameters, or heuristic rules
        if self.memory is not None:
            self.memory.working_memory.inject_feedback(feedback)
    
    def _meta_evaluate(self):
        """Meta-cognitive evaluation: assess overall performance and trigger plasticity."""
        if len(self._trajectory) < self.config.meta_interval:
            return
        
        # Evaluate recent performance
        recent = self._trajectory[-self.config.meta_interval:]
        success_rate = sum(1 for t in recent if t.get("success", False)) / len(recent)
        
        # If performance is poor, trigger plasticity or structural change
        if success_rate < 0.3 and self.config.enable_plasticity and self.plasticity is not None:
            self.plasticity.trigger_reorganization(recent)
    
    def _act(self, action: Any) -> Any:
        """Convert internal action representation to motor output."""
        if self.action_module is not None:
            out, _ = self.action_module.forward({"action": action}, {})
            return out.get("motor_command", action)
        return action
    
    # ── Lifecycle ──────────────────────────────────────────
    
    def reset(self):
        """Reset for new episode."""
        self.step_count = 0
        self.loop_mode = LoopMode.FAST
        self._trajectory = []
        self._last_reflection = None
        
        if self.memory is not None:
            self.memory.reset()
        if self.cognition is not None:
            self.cognition.reset()
    
    def get_state(self) -> Dict:
        """Return diagnostic state for monitoring."""
        return {
            "step": self.step_count,
            "loop_mode": self.loop_mode.value,
            "trajectory_length": len(self._trajectory),
            "last_reflection": self._last_reflection,
        }
