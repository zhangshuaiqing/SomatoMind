"""
Attention — Selective focus mechanism.

Inspired by:
  - Bottom-up attention: salient features pop out (contrast, motion, novelty)
  - Top-down attention: task-relevant features amplified (goal-driven)
  - Spotlight metaphor: only a 'window' of information is processed at full resolution
"""
from typing import Any, Dict, Optional


class AttentionModule:
    """Filters and weights perceptual input.
    
    Applies an attention mask to internal representations,
    suppressing irrelevant features and amplifying relevant ones.
    """
    def __init__(self):
        self.attention_mask: Optional[Dict] = None
    
    def forward(self, features: Dict, context: Optional[Dict] = None) -> tuple[Dict, Dict]:
        # TODO: implement spatial/feature attention
        return {"attended_features": features}, {}
    
    def reset(self):
        self.attention_mask = None
