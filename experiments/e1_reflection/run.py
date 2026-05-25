"""
E1: Reflection Loop — Agent with Working Memory and Verbal Self-Reflection

Hypothesis: 
  A navigation agent that maintains a structured working memory and can
  reflect on past failures will outperform a pure ReAct agent under 
  partial observability and dynamic obstacles.

Architecture:
  Observation + Working Memory → LLM → Action + Updated Working Memory
                                   ↓
                            Critic LLM generates verbal feedback
                                   ↓
                         Feedback stored in Episodic Memory
                                   ↓
                         Next step: Episodic Memory injected into prompt

Reference:
  - Shinn et al. (2023). Reflexion: Language Agents with Verbal Reinforcement Learning
"""

print("E1: Reflection Loop — placeholder. Implement me!")
