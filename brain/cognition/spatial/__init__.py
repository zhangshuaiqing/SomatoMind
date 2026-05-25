"""
Spatial — Spatial reasoning and mental simulation.
"""
from typing import Any, Dict


class SpatialReasoner:
    """Egocentric (body-centered) and allocentric (map-like) spatial reasoning.
    
    - Egocentric: "where is the wall relative to me?"
    - Allocentric: "what does the whole map look like?"
    - Path integration: tracking position without external references
    """
    def forward(self, inputs, state) -> tuple[Dict, Dict]:
        return {"spatial_representation": {}}, {}
    def reset(self): pass


class MentalSimulator:
    """Run the world model forward in 'imagination'.
    
    Enables: "if I go left now, where will I end up?"
    """
    def forward(self, inputs, state) -> tuple[Dict, Dict]:
        return {"predicted_outcomes": []}
    def reset(self): pass
