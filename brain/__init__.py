"""
brain — SomatoMind Core Cognition Architecture

This package is the evolving prototype of the SomatoMind "Brain":
an agent architecture inspired by biological neural systems that can:

  - Maintain structured working memory across timesteps
  - Reflect on past decisions and adjust strategies (metacognition)
  - Continue learning after deployment (plasticity mechanisms)
  - Adapt to multiple perception modalities and motor systems

The Brain is the ultimate output of SomatoMind experiments.
Each experiment in experiments/ feeds findings back into brain/.
"""

from .core.brain import Brain
