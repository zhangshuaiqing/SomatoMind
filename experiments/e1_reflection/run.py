"""
E1: Reflection Loop — Structured Working Memory + Verbal Self-Reflection

Purpose:
  Compare a pure ReAct agent against a Reflective agent (with working memory
  and verbal self-reflection) in a partially observable GridWorld.

Dependencies:
  This experiment requires the navigation-agent GridWorld environment,
  included as a git submodule at env/gridworld/.
  Initialize with: git submodule update --init --recursive

Hypothesis:
  The Reflective agent will achieve higher success rates under partial
  observability, because working memory maintains task context and
  reflection learns from failures.

Metrics:
  - Success rate (goal reached within max_steps)
  - Steps to goal (for successful episodes)
  - Exploration coverage (% of grid visited)

Baseline: Pure ReAct agent (no working memory, no reflection)
"""

import sys, os, random, json, time
from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional, Tuple
from collections import deque

import numpy as np

# ── Import GridWorld from submodule ──────────────────
PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
SUBMOUDLE_PATH = os.path.join(PROJECT_ROOT, "env", "gridworld", "src")
if SUBMOUDLE_PATH not in sys.path:
    sys.path.insert(0, SUBMOUDLE_PATH)

from env.gridworld import GridWorld, CellType


# ═══════════════════════════════════════════════════════════
#  Memory
# ═══════════════════════════════════════════════════════════

@dataclass
class WorkingMemory:
    visited: set = field(default_factory=set)
    feedback: List[str] = field(default_factory=list)
    last_known_goal_dir: Optional[str] = None
    
    def update(self, pos):
        self.visited.add(pos)
    
    def clear(self):
        self.visited.clear()
        self.feedback.clear()
        self.last_known_goal_dir = None


@dataclass
class EpisodicMemory:
    """Ring buffer of recent steps for reflection."""
    buffer: deque = field(default_factory=lambda: deque(maxlen=50))
    
    def record(self, pos, action, stuck):
        self.buffer.append({"pos": pos, "action": action, "stuck": stuck})
    
    def recent(self, n=10):
        return list(self.buffer)[-n:]
    
    def clear(self):
        self.buffer.clear()


# ═══════════════════════════════════════════════════════════
#  Agents
# ═══════════════════════════════════════════════════════════

class ReActAgent:
    """Baseline: reacts to current observation only.
    
    Strategy:
      - If goal visible → direct path
      - Otherwise → random valid action
    """
    def __init__(self, seed=42):
        self.rng = random.Random(seed)
    
    def act(self, obs, env) -> str:
        pos = obs["agent_pos"]
        gv = obs["goal_visible"]
        gp = obs.get("goal_pos")
        
        if gv and gp:
            dr = gp[0] - pos[0]; dc = gp[1] - pos[1]
            if abs(dr) >= abs(dc):
                return "down" if dr > 0 else "up"
            else:
                return "right" if dc > 0 else "left"
        
        valid = [a for a in ["up","down","left","right"] if self._valid(a, pos, env)]
        return self.rng.choice(valid) if valid else "up"
    
    def _valid(self, action, pos, env):
        dr, dc = GridWorld.DIRECTIONS[action]
        nr, nc = pos[0]+dr, pos[1]+dc
        return 0 <= nr < env.size and 0 <= nc < env.size and env.grid[nr,nc] != CellType.OBSTACLE
    
    def reset(self): pass


class ReflectiveAgent:
    """Agent with working memory + episodic memory + verbal reflection.
    
    Strategy:
      1. If goal visible → direct path
      2. Use goal_direction from observation to guide exploration
      3. Working memory prevents revisiting explored areas
      4. Reflection detects loops and adjusts strategy
    """
    MAX_MEMO = 10
    
    def __init__(self, seed=42):
        self.rng = random.Random(seed)
        self.wm = WorkingMemory()
        self.em = EpisodicMemory()
        self.step = 0
        self.reflection_interval = 8
        self.reflection_count = 0
        self.last_feedback = None
        self.persistent_dir = None  # direction we're committed to
    
    def act(self, obs, env) -> str:
        self.step += 1
        pos = obs["agent_pos"]
        gv = obs["goal_visible"]
        gp = obs.get("goal_pos")
        gd = obs.get("goal_direction")
        
        self.wm.update(pos)
        
        # Phase 1: if goal visible, direct path
        if gv and gp:
            self.persistent_dir = None
            dr = gp[0]-pos[0]; dc = gp[1]-pos[1]
            if abs(dr) >= abs(dc):
                return "down" if dr > 0 else "up"
            else:
                return "right" if dc > 0 else "left"
        
        # Phase 2: reflection feedback overrides
        if self.last_feedback and "loop" in self.last_feedback:
            self.persistent_dir = None
            self.last_feedback = None  # consume feedback
            # pick least visited direction
            scores = {}
            for a in ["up","down","left","right"]:
                dr, dc = GridWorld.DIRECTIONS[a]
                nr, nc = pos[0]+dr, pos[1]+dc
                if self._valid(a, pos, env):
                    scores[a] = 1 if (nr,nc) not in self.wm.visited else 0
                else:
                    scores[a] = -100
            best = max(scores, key=scores.get)
            if scores[best] > -1:
                return best
        
        # Phase 3: use goal_direction to guide exploration
        if gd and gd != "HERE":
            self.wm.last_known_goal_dir = gd
            compass = {"N": "up", "S": "down", "W": "left", "E": "right"}
            for d in gd:
                action = compass.get(d)
                if action and self._valid(action, pos, env):
                    nr, nc = pos[0]+GridWorld.DIRECTIONS[action][0], pos[1]+GridWorld.DIRECTIONS[action][1]
                    if (nr,nc) not in self.wm.visited or self.rng.random() < 0.3:
                        return action
        
        # Phase 4: persistent exploration direction
        if self.persistent_dir and self._valid(self.persistent_dir, pos, env):
            dr, dc = GridWorld.DIRECTIONS[self.persistent_dir]
            nr, nc = pos[0]+dr, pos[1]+dc
            if (nr,nc) not in self.wm.visited or self.rng.random() < 0.4:
                return self.persistent_dir
        
        # Phase 5: pick least visited valid direction
        scores = {}
        for a in ["up","down","left","right"]:
            dr, dc = GridWorld.DIRECTIONS[a]
            nr, nc = pos[0]+dr, pos[1]+dc
            if self._valid(a, pos, env):
                scores[a] = 0 if (nr,nc) not in self.wm.visited else 1
            else:
                scores[a] = 999
        best = min(scores, key=scores.get)
        if scores[best] < 999:
            self.persistent_dir = best
            return best
        
        # Phase 6: fallback
        valid = [a for a in ["up","down","left","right"] if self._valid(a, pos, env)]
        return self.rng.choice(valid) if valid else "up"
    
    def _valid(self, action, pos, env):
        dr, dc = GridWorld.DIRECTIONS[action]
        nr, nc = pos[0]+dr, pos[1]+dc
        return 0 <= nr < env.size and 0 <= nc < env.size and env.grid[nr,nc] != CellType.OBSTACLE
    
    def reflect(self, trajectory):
        """Check for loops — if agent is stuck, produce feedback."""
        if len(trajectory) < 6: return None
        recent = trajectory[-6:]
        poses = [(t["pos"][0], t["pos"][1]) for t in recent]
        unique = len(set(poses))
        if unique <= 2:  # stuck in loop
            return "loop detected, try different direction"
        return None
    
    def __call__(self, obs, env):
        return self.act(obs, env)
    
    def reset(self):
        self.step = 0
        self.reflection_count = 0
        self.last_feedback = None
        self.persistent_dir = None
        self.wm.clear()
        self.em.clear()


# ═══════════════════════════════════════════════════════════
#  Runner
# ═══════════════════════════════════════════════════════════

@dataclass
class Result:
    agent: str; mode: str; n: int=0; ok: int=0
    steps_ok: list = field(default_factory=list)
    reflections: int=0
    
    @property
    def rate(self): return self.ok / max(self.n, 1)
    @property
    def avg_steps(self): return sum(self.steps_ok)/len(self.steps_ok) if self.steps_ok else 0


def run_episode(agent, env, max_steps=200):
    """Run one episode. Returns (success, steps, reflections)."""
    obs = env.reset()
    if hasattr(agent, 'reset'): agent.reset()
    refs = 0
    
    for step in range(max_steps):
        if isinstance(obs, dict):
            o = obs
        else:
            o = env._get_obs() if hasattr(env, '_get_obs') else obs
        
        action = agent.act(o, env) if hasattr(agent, 'act') else agent(o, env)
        
        # Periodic reflection for ReflectiveAgent
        if hasattr(agent, 'reflection_count'):
            if agent.step > 0 and agent.step % agent.reflection_interval == 0:
                recent = agent.em.recent(10)
                fb = agent.reflect(recent)
                if fb:
                    agent.last_feedback = fb
                    agent.reflection_count += 1
                    refs += 1
        
        next_obs, reward, done, info = env.step(action)
        
        # Track episodic memory
        if hasattr(agent, 'em'):
            pos = o.get("agent_pos", env.agent_pos)
            prev = o.get("agent_pos", env.agent_pos)
            stuck = (prev == pos)
            agent.em.record(pos, action, stuck)
        
        if done or reward > 0:
            return True, step+1, (agent.reflection_count if hasattr(agent, 'reflection_count') else refs)
        
        obs = next_obs
    return False, max_steps, refs


def main():
    print("╔══════════════════════════════════════════════════════════════╗")
    print("║  E1: Reflection Loop — ReAct vs Reflective Agent           ║")
    print("║  Partially observable GridWorld                            ║")
    print("╚══════════════════════════════════════════════════════════════╝")
    print()
    
    CONFIG = {
        "num_episodes": 100,
        "grid_size": 10,
        "obstacle_ratio": 0.3,
        "max_steps": 200,
        "seed": 42,
        "modes": ["fog_of_war"],
        "num_dynamic": 3,
        "dynamic_speed": 2,
    }
    
    all_results = []
    
    for mode in CONFIG["modes"]:
        print(f"\n{'─'*60}")
        print(f"  Mode: {mode}")
        print(f"{'─'*60}")
        
        for agent_type in ["react", "reflective"]:
            res = Result(agent=agent_type, mode=mode)
            
            for ep in range(CONFIG["num_episodes"]):
                env = GridWorld(
                    size=CONFIG["grid_size"],
                    obstacle_ratio=CONFIG["obstacle_ratio"],
                    seed=CONFIG["seed"] + ep * 17,
                    random_start_goal=True,
                    observation_mode=mode,
                    view_range=2,
                    num_dynamic_obstacles=CONFIG["num_dynamic"],
                    dynamic_obstacle_speed=CONFIG["dynamic_speed"],
                )
                
                if agent_type == "react":
                    agent = ReActAgent(seed=CONFIG["seed"] + ep * 13)
                else:
                    agent = ReflectiveAgent(seed=CONFIG["seed"] + ep * 13)
                
                ok, steps, refs = run_episode(agent, env, CONFIG["max_steps"])
                res.n += 1
                res.reflections += refs
                if ok:
                    res.ok += 1
                    res.steps_ok.append(steps)
                
                if (ep + 1) % 20 == 0:
                    print(f"  [{agent_type:>10}] [{mode:>12}] ep {ep+1:3d}/{CONFIG['num_episodes']} "
                          f"{'✓' if ok else '✗'} steps={steps:3d}")
            
            all_results.append(res)
    
    # Results
    print(f"\n{'═'*70}")
    print(f"  RESULTS")
    print(f"{'═'*70}")
    print(f"  {'Agent':<12} {'Mode':<12} {'Success Rate':<16} {'Avg Steps':<12} {'Reflections':<12}")
    print(f"  {'─'*60}")
    for r in all_results:
        print(f"  {r.agent:<12} {r.mode:<12} {r.rate:>6.1%} ({r.ok:3d}/{r.n:<3d})  "
              f"{r.avg_steps:>6.1f}      {r.reflections:>4d}")
    print(f"  {'─'*60}")
    
    # Key findings
    print()
    for mode in CONFIG["modes"]:
        rr = [r for r in all_results if r.agent=="react" and r.mode==mode][0]
        fr = [r for r in all_results if r.agent=="reflective" and r.mode==mode][0]
        diff = fr.rate - rr.rate
        print(f"  [{mode}] Improvement: {diff:+.1%}  "
              f"(ReAct: {rr.rate:.0%} → Reflective: {fr.rate:.0%})")
    
    # Save
    d = os.path.join(os.path.dirname(__file__), "..", "..", "results")
    os.makedirs(d, exist_ok=True)
    ts = time.strftime("%Y%m%d_%H%M%S")
    p = os.path.join(d, f"e1_reflection_{ts}.json")
    json.dump({
        "config": CONFIG,
        "results": [{"agent":r.agent, "mode":r.mode, "rate":r.rate,
                      "ok":r.ok, "n":r.n, "avg_steps":r.avg_steps,
                      "reflections":r.reflections} for r in all_results],
    }, open(p, "w"), indent=2)
    print(f"\n  Saved: {p}")


if __name__ == "__main__":
    main()
