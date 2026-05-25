"""
Brain — Core Architecture

The Brain is the central coordinating module that connects:
  - Perception → Working Memory → Reflection → Action

Design principles:
  1. Modular: each cognitive function is an independent, swappable component
  2. Recursive: the Brain itself can inspect and modify its own components
  3. Time-scale separated: fast (reactive) and slow (deliberative) processing loops
"""

from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional


@dataclass
class BrainConfig:
    """Configuration for a Brain instance."""
    working_memory_size: int = 1024
    reflection_interval: int = 5  # Reflect every N steps
    enable_plasticity: bool = False
    slow_loop_frequency: float = 0.1  # Hz, relative to fast loop


class Brain:
    """The SomatoMind Brain — a structured cognitive agent architecture.
    
    This is a scaffold that will be filled in as experiments yield insights.
    """
    
    def __init__(self, config: Optional[BrainConfig] = None):
        self.config = config or BrainConfig()
        self.step_count = 0
        
    def perceive(self, observation: Any) -> Dict:
        """Process raw observation into internal representation."""
        raise NotImplementedError
        
    def decide(self, state: Dict) -> Any:
        """Produce an action from current internal state."""
        raise NotImplementedError
        
    def reflect(self, trajectory: List[Dict]) -> Optional[str]:
        """Reflect on recent experience, return verbal feedback if needed."""
        raise NotImplementedError
        
    def step(self, observation: Any) -> Any:
        """One complete perception-decision-action loop."""
        self.step_count += 1
        state = self.perceive(observation)
        action = self.decide(state)
        
        if self.step_count % self.config.reflection_interval == 0:
            feedback = self.reflect([])  # TODO: pass actual trajectory
            if feedback:
                self._incorporate_feedback(feedback)
                
        return action
        
    def _incorporate_feedback(self, feedback: str):
        """Integrate reflective feedback into internal state."""
        raise NotImplementedError
