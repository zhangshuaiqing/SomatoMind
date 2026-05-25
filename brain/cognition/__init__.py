"""
Cognition — High-level cognitive functions.

Contains: reasoning, planning, reflection (metacognition), attention, spatial, creativity.
"""

from typing import Any, Dict, List, Optional


class CognitionSystem:
    """Container for all cognitive modules."""
    
    def __init__(self):
        self.reasoning = None
        self.planning = None
        self.reflection = None
        self.policy = None
        self.spatial = None
        self.creativity = None
    
    def reset(self):
        for m in [self.reasoning, self.planning, self.reflection, self.policy, self.spatial, self.creativity]:
            if m is not None and hasattr(m, 'reset'):
                m.reset()
