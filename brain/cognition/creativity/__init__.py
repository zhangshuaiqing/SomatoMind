"""
Creativity — Exploration and novel strategy generation.

Not 'creativity' as in art, but as in: the ability to generate novel,
useful solutions when existing patterns consistently fail.
"""
from typing import Any, Dict


class CreativityModule:
    """Drives exploration and structural adaptation.
    
    Mechanisms:
      - Intrinsic motivation: reward for visiting novel states
      - Recombination: mix successful sub-strategies
      - Counterfactual: "what if I tried something completely different?"
    """
    def forward(self, inputs, state) -> tuple[Dict, Dict]:
        return {"novel_action": None, "novelty_score": 0.0}
    def reset(self): pass
