"""
Reasoning — Symbolic and probabilistic reasoning.

- Symbolic: rule-based deduction (if wall left and goal right → don't go left)
- Probabilistic: Bayesian inference under uncertainty
- Chain-of-thought: structured multi-step reasoning for LLM-based agents
"""


class SymbolicReasoner:
    """Rule-based deduction engine."""
    def forward(self, percept, context) -> dict:
        return {"conclusion": ""}
    def reset(self): pass


class ProbabilisticReasoner:
    """Bayesian inference under uncertainty."""
    def forward(self, percept, context) -> dict:
        return {"beliefs": {}}
    def reset(self): pass
