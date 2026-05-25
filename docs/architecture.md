# Architecture Design: SomatoMind Brain

## Overview

The SomatoMind Brain is designed as a **multi-timescale, modular cognitive architecture** inspired by biological neural systems. Each cognitive function (observation, memory, reasoning, planning, action) operates at its own timescale and communicates through well-defined interfaces.

## Guiding Principles

1. **Structure determines function** — the wiring topology matters as much as the weights
2. **Multi-timescale processing** — fast loops (reflexes) + slow loops (deliberation)
3. **Hierarchical memory** — from raw sensory buffers to abstract procedural knowledge
4. **Modular but integrated** — components are swappable but share a unified internal state
5. **Emergence over engineering** — complex behaviors should emerge from simple mechanisms, not be hand-coded

## Cognitive Architecture

```
                         ┌─────────────────────────────┐
                         │     Meta-Cognitive Layer     │
                         │  (monitors, evaluates,       │
                         │   triggers slow loop)        │
                         └──────────┬──────────────────┘
                                    │ triggers
                                    ▼
┌────────────┐    ┌────────────┐    ┌────────────┐    ┌────────────┐
│ Perception │───▶│   Memory   │───▶│ Cognition  │───▶│   Action   │
│            │    │            │    │            │    │            │
│ • Adapter  │    │ • Sensory  │    │ • Reasoning│    │ • Policy   │
│ • Attention│    │   Buffer   │    │ • Planning │    │ • Motor    │
│ • World    │    │ • Working  │    │ • Spatial  │    │   Bridge   │
│   Model    │    │   Memory   │    │ • Creativity│    │            │
│            │    │ • Episodic │    │            │    │            │
│            │    │ • Procedural│   │            │    │            │
└────────────┘    └────────────┘    └────────────┘    └────────────┘
       │                 │                │                  │
       └─────────────────┴────────────────┴──────────────────┘
                              │
                         ┌────▼────┐
                         │Plasticity│
                         │  (EWC,  │
                         │  Hebbian│
                         │  Struct)│
                         └─────────┘
```

### Fast Loop (Reactive)
```
Perception → Working Memory → Policy → Action
```
Timescale: milliseconds to seconds. Used for routine navigation, obstacle avoidance, simple pattern matching. No memory of past beyond working memory.

### Slow Loop (Deliberative)
```
Episodic Memory → Reasoning → Planning → Action (with reflection feedback)
```
Timescale: seconds to minutes. Used when fast loop fails, novel situations arise, or periodic review is triggered. Involves:
- Trajectory recall from episodic memory
- Reflection on what went wrong
- Planning alternative strategies
- Modifying fast-loop parameters

## Capability Mapping

### Observation (观察力)
- **Perception adapter** normalizes diverse input modalities into a unified internal representation
- **Attention mechanism** selects salient features from raw input (inspired by spatial/feature attention in visual cortex)
- **World model** predicts next observation given current state and action — enables counterfactual reasoning

### Memory (记忆力)
- **Sensory buffer**: milliseconds, holds raw observation
- **Working memory**: seconds to minutes, structured context (current goal, recent actions, task state). Implemented as recurrent attractor dynamics or explicit slot-based memory
- **Episodic memory**: minutes to hours, stores trajectories with timestamps and outcomes
- **Procedural memory**: long-term skills encoded as network weights or structured sub-policies

### Reasoning (推理力 + 计算力)
- **Symbolic reasoning**: rule-based deduction for well-defined problems (e.g., "if there's a wall to my left and the goal is to my right, I should not go left")
- **Probabilistic reasoning**: Bayesian inference under uncertainty (useful in fog-of-war mode)
- **Chain-of-thought**: for LLM-based agents, structured multi-step reasoning

### Spatial (空间力)
- **Spatial representation**: allocentric (map-like) + egocentric (body-centered) representations
- **Mental simulation**: run the world model forward in the "imagination" to evaluate candidate actions
- **Path integration**: track position relative to start without external references

### Planning (推理力的延展)
- **Tree search**: look ahead multiple steps, evaluate outcomes
- **Goal decomposition**: break a distant goal into sub-goals
- **Re-planning**: when the plan fails, generate alternatives

### Creativity (创造力)
- **Exploration vs exploitation**: intrinsic motivation drives exploration of novel states
- **Structural plasticity**: add/remove connections when existing patterns consistently underperform
- **Recombination**: mix successful sub-strategies from episodic memory

## Module Interfaces

Each module follows the same interface pattern:

```python
class CognitiveModule:
    def reset(self):
        """Reset internal state for a new episode."""
        pass
    
    def forward(self, inputs: dict, state: dict) -> tuple[dict, dict]:
        """Process inputs and return outputs + updated state."""
        pass
```

The Brain orchestrates modules via:

```python
class Brain:
    def step(self, observation: Any) -> Any:
        # 1. Perception
        internal_state = self.perception(observation)
        
        # 2. Memory update
        self.memory.sensory_buffer.write(internal_state)
        self.memory.working_memory.update(internal_state)
        
        # 3. Cognition (fast loop)
        action = self.policy(self.memory.working_memory.read())
        
        # 4. Periodic slow loop
        if should_reflect():
            self.slow_loop()
        
        # 5. Motor output
        return self.action(action)
```

## Experiment → Brain Feedback Pipeline

```
experiment/E1 runs ──────▶ findings.yaml ──────▶ Brain.from_findings()
                                                      │
                                                      ▼
                                              brain/core/config.py
                                              brain/memory/*.py
                                              ... etc
```

Each experiment produces a `findings.yaml` with structure:

```yaml
experiment: e1_reflection
conclusion: "Working memory + reflection improves success rate by 32%"
effective_components:
  - working_memory
  - reflection_loop
ineffective_components:
  - none
recommended_brain_config:
  memory.working_memory.size: 2048
  cognition.reflection.interval: 3
```

The Brain's `from_findings()` classmethod aggregates all findings to construct the optimal architecture.

## References

- Baddeley, A. (2000). The episodic buffer: a new component of working memory?
- Kahneman, D. (2011). Thinking, Fast and Slow
- Hawkins, J. (2021). A Thousand Brains: A New Theory of Intelligence
- Shinn et al. (2023). Reflexion: Language Agents with Verbal Reinforcement Learning
- Memory, Attention, and Decision-Making (neuroscience textbooks)
