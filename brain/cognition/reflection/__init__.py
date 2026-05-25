"""
Reflection — Meta-cognition and self-evaluation.

Core question: "Did I do well? What should I do differently?"
Implements the Reflexion pattern (Shinn et al., 2023).
"""
from typing import Any, Dict, List, Optional


class ReflectionModule:
    """Verbal self-reflection on recent trajectory.
    
    Given a trajectory segment, produces:
      - Evaluation: "I keep bumping into walls"
      - Strategy adjustment: "I should slow down near walls"
    """
    def __init__(self):
        self.last_feedback: Optional[str] = None
    
    def forward(self, inputs: Dict, state: Dict) -> tuple[Dict, Dict]:
        """Analyze trajectory and produce reflective feedback."""
        trajectory = inputs.get("trajectory", [])
        feedback = self._analyze(trajectory)
        self.last_feedback = feedback
        return {"feedback": feedback}, {}
    
    def _analyze(self, trajectory: List) -> Optional[str]:
        """Analyze trajectory for patterns and errors."""
        if not trajectory:
            return None
        # TODO: implement pattern detection
        return None
    
    def reset(self):
        self.last_feedback = None
