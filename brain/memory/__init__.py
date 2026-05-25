"""
Memory — Multi-Timescale Memory System

Architecture:
  Sensory Buffer (ms) → Working Memory (s) → Episodic Memory (min) → Procedural Memory (permanent)
"""

from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional


@dataclass
class MemorySystem:
    """Coordinates all memory subsystems."""
    sensory_buffer: 'SensoryBuffer' = None
    working_memory: 'WorkingMemory' = None
    episodic_memory: 'EpisodicMemory' = None
    procedural_memory: 'ProceduralMemory' = None
    
    def reset(self):
        for m in [self.sensory_buffer, self.working_memory, self.episodic_memory]:
            if m:
                m.reset()


class SensoryBuffer:
    """Ultra-short-term buffer holding raw sensory data."""
    def __init__(self, capacity: int = 1):
        self.capacity = capacity
        self.buffer: List[Dict] = []
    
    def write(self, percept: Dict):
        self.buffer.append(percept)
        if len(self.buffer) > self.capacity:
            self.buffer.pop(0)
    
    def read(self) -> Optional[Dict]:
        return self.buffer[-1] if self.buffer else None
    
    def reset(self):
        self.buffer.clear()


class WorkingMemory:
    """Structured scratchpad for current task context.
    
    Contains: current goal, suspicion about obstacles, last error, plan stack.
    """
    def __init__(self, size: int = 2048):
        self.size = size
        self.goal: Any = None
        self.suspicions: List[str] = []
        self.last_error: Optional[str] = None
        self.plan_stack: List[Any] = []
        self.internal_state: Dict = {}
    
    def update(self, percept: Dict):
        """Update working memory with new perception."""
        self.internal_state.update(percept)
    
    def inject_feedback(self, feedback: str):
        """Integrate reflective feedback (e.g., 'I should not go left')."""
        self.suspicions.append(feedback)
    
    def read(self) -> Dict:
        return {
            "goal": self.goal,
            "suspicions": self.suspicions,
            "last_error": self.last_error,
            "plan_stack": self.plan_stack,
            "internal_state": self.internal_state,
        }
    
    def reset(self):
        self.goal = None
        self.suspicions.clear()
        self.last_error = None
        self.plan_stack.clear()
        self.internal_state.clear()


class EpisodicMemory:
    """Trajectory memory — stores experience sequences.
    
    Each episode is stored with: observations, actions, outcomes, and reflection tags.
    """
    def __init__(self, capacity: int = 100):
        self.capacity = capacity
        self.episodes: List[Dict] = []
    
    def store_episode(self, episode: Dict):
        self.episodes.append(episode)
        if len(self.episodes) > self.capacity:
            self.episodes.pop(0)
    
    def recall_recent(self, n: int = 10) -> List[Dict]:
        return self.episodes[-n:] if self.episodes else []
    
    def recall_by_tag(self, tag: str) -> List[Dict]:
        return [e for e in self.episodes if e.get("tag") == tag]
    
    def reset(self):
        self.episodes.clear()


class ProceduralMemory:
    """Long-term skills — encoded as trained weights or structured sub-policies.
    
    This is the 'muscle memory' of the Brain.
    """
    def __init__(self):
        self.skills: Dict[str, Any] = {}
    
    def store_skill(self, name: str, skill: Any):
        self.skills[name] = skill
    
    def retrieve_skill(self, name: str) -> Optional[Any]:
        return self.skills.get(name)
    
    def list_skills(self) -> List[str]:
        return list(self.skills.keys())
    
    def reset(self):
        pass  # Procedural memory persists across episodes
