"""
E1 Visualization — Render agent trajectories and experiment results.

Usage:
  python experiments/e1_reflection/visualize.py [--results results/e1_reflection_*.json]
  python experiments/e1_reflection/visualize.py --demo   # run a fresh demo episode with render
"""

import sys, os, argparse, json, random
from typing import List, Tuple
import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.patches import Rectangle, Circle, FancyArrowPatch
import matplotlib.patches as mpatches

# ── Import built-in GridWorld ──────────────────
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))), "env"))
from gridworld import GridWorld, CellType

PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
RESULTS_DIR = os.path.join(PROJECT_ROOT, "results")
PLOTS_DIR = os.path.join(PROJECT_ROOT, "results", "plots")
os.makedirs(PLOTS_DIR, exist_ok=True)


# ═══════════════════════════════════════════════════════════════
#  Utility
# ═══════════════════════════════════════════════════════════════

def _load_results(path=None):
    """Load experiment results from JSON."""
    if path and os.path.exists(path):
        return json.load(open(path))
    # Find latest
    files = sorted(f for f in os.listdir(RESULTS_DIR) if f.startswith("e1_reflection_") and f.endswith(".json"))
    if not files:
        print("No result files found. Run the experiment first.")
        return None
    return json.load(open(os.path.join(RESULTS_DIR, files[-1])))


# ═══════════════════════════════════════════════════════════════
#  Plot 1: Comparison Bar Chart
# ═══════════════════════════════════════════════════════════════

def plot_comparison_bars(results_data, save=True):
    """Bar chart comparing success rate and avg steps by agent type."""
    agents = [r["agent"] for r in results_data["results"]]
    rates = [r["rate"] * 100 for r in results_data["results"]]
    steps = [r["avg_steps"] for r in results_data["results"]]
    ok = [r["ok"] for r in results_data["results"]]
    n = [r["n"] for r in results_data["results"]]
    refs = [r["reflections"] for r in results_data["results"]]
    
    fig, axes = plt.subplots(1, 3, figsize=(14, 4.5))
    fig.patch.set_facecolor("#0d1117")
    colors = ["#58a6ff", "#3fb950"]
    
    # 1. Success rate
    ax = axes[0]
    bars = ax.bar(agents, rates, color=colors, edgecolor="none", width=0.5)
    for bar, r in zip(bars, rates):
        ax.text(bar.get_x() + bar.get_width()/2, bar.get_height() + 1,
                f"{r:.0f}%", ha="center", va="bottom", color="#c9d1d9", fontsize=11, fontweight="bold")
    ax.set_ylim(0, 110)
    ax.set_ylabel("Success Rate (%)", color="#8b949e")
    ax.set_title("Success Rate", color="#c9d1d9", fontweight="bold")
    ax.tick_params(colors="#8b949e")
    for spine in ax.spines.values(): spine.set_color("#30363d")
    ax.set_facecolor("#161b22")
    
    # 2. Avg steps
    ax = axes[1]
    bars = ax.bar(agents, steps, color=colors, edgecolor="none", width=0.5)
    for bar, s in zip(bars, steps):
        ax.text(bar.get_x() + bar.get_width()/2, bar.get_height() + 0.3,
                f"{s:.1f}", ha="center", va="bottom", color="#c9d1d9", fontsize=11, fontweight="bold")
    ax.set_ylabel("Avg Steps to Goal", color="#8b949e")
    ax.set_title("Average Steps (successful only)", color="#c9d1d9", fontweight="bold")
    ax.tick_params(colors="#8b949e")
    for spine in ax.spines.values(): spine.set_color("#30363d")
    ax.set_facecolor("#161b22")
    
    # 3. Reflections triggered
    ax = axes[2]
    bars = ax.bar(agents, refs, color=colors, edgecolor="none", width=0.5)
    for bar, r in zip(bars, refs):
        ax.text(bar.get_x() + bar.get_width()/2, bar.get_height() + 1,
                str(r), ha="center", va="bottom", color="#c9d1d9", fontsize=11, fontweight="bold")
    ax.set_ylabel("Reflections Triggered", color="#8b949e")
    ax.set_title("Reflection Count", color="#c9d1d9", fontweight="bold")
    ax.tick_params(colors="#8b949e")
    for spine in ax.spines.values(): spine.set_color("#30363d")
    ax.set_facecolor("#161b22")
    
    fig.suptitle("E1: ReAct vs Reflective Agent — Fog of War",
                 color="#c9d1d9", fontsize=14, fontweight="bold", y=1.02)
    fig.tight_layout()
    
    if save:
        path = os.path.join(PLOTS_DIR, "e1_comparison_bars.png")
        fig.savefig(path, dpi=150, bbox_inches="tight", facecolor="#0d1117")
        print(f"Saved: {path}")
    plt.close(fig)


# ═══════════════════════════════════════════════════════════════
#  Plot 2: Trajectory Map (single episode)
# ═══════════════════════════════════════════════════════════════

def plot_trajectory(env, trajectory: List[Tuple[int, int]], title: str, filename: str):
    """Render a static GridWorld with agent trajectory overlaid."""
    grid = env.grid.copy()
    size = env.size
    
    fig, ax = plt.subplots(figsize=(size * 0.7, size * 0.7))
    fig.patch.set_facecolor("#0d1117")
    ax.set_facecolor("#161b22")
    
    # Draw grid cells
    for r in range(size):
        for c in range(size):
            cell = grid[r, c]
            color = "#161b22"  # empty
            if cell == CellType.OBSTACLE:
                color = "#30363d"
            elif cell == CellType.GOAL:
                color = "#d29922"
            elif cell == CellType.DYNAMIC_OBSTACLE:
                color = "#f85149"
            rect = Rectangle((c - 0.5, size - 1 - r + 0.5), 1, 1,
                             facecolor=color, edgecolor="#21262d", linewidth=0.5)
            ax.add_patch(rect)
    
    # Draw trajectory as arrow path
    if len(trajectory) > 1:
        xs = [p[1] for p in trajectory]
        ys = [size - 1 - p[0] for p in trajectory]
        # Fade from blue to green
        cmap = plt.cm.Blues
        for i in range(len(trajectory) - 1):
            alpha = 0.3 + 0.7 * (i / len(trajectory))
            ax.annotate("", xy=(xs[i+1], ys[i+1]), xytext=(xs[i], ys[i]),
                        arrowprops=dict(arrowstyle="->", color="#58a6ff",
                                        alpha=alpha, lw=1.5 + alpha))
    
    # Mark start and end
    if trajectory:
        sx, sy = trajectory[0][1], size - 1 - trajectory[0][0]
        ax.scatter(sx, sy, s=180, c="#3fb950", marker="o", edgecolors="#7ee787",
                   linewidths=2, zorder=5, label="Start")
    if len(trajectory) > 1:
        ex, ey = trajectory[-1][1], size - 1 - trajectory[-1][0]
        ax.scatter(ex, ey, s=180, c="#d29922", marker="*", edgecolors="#ffd8a8",
                   linewidths=2, zorder=5, label="Goal")
    
    ax.set_xlim(-0.6, size - 0.4)
    ax.set_ylim(-0.6, size - 0.4)
    ax.set_aspect("equal")
    ax.set_title(title, color="#c9d1d9", fontsize=12, fontweight="bold", pad=10)
    ax.legend(loc="upper right", facecolor="#161b22", edgecolor="#30363d",
              labelcolor="#c9d1d9", fontsize=9)
    ax.tick_params(colors="#8b949e", labelsize=8)
    for spine in ax.spines.values(): spine.set_color("#30363d")
    ax.set_xticks(range(size))
    ax.set_yticks(range(size))
    ax.grid(True, color="#21262d", linewidth=0.5)
    
    path = os.path.join(PLOTS_DIR, filename)
    fig.savefig(path, dpi=150, bbox_inches="tight", facecolor="#0d1117")
    print(f"Saved: {path}")
    plt.close(fig)


# ═══════════════════════════════════════════════════════════════
#  Demo: run a single episode and render both agents
# ═══════════════════════════════════════════════════════════════

def run_demo(seed=42):
    """Run one episode for each agent on the same map and render both trajectories."""
    size = 12
    obstacle_ratio = 0.3
    
    # Inline agent imports to avoid module path issues
    sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
    from experiments.e1_reflection.run import ReActAgent, ReflectiveAgent
    
    for agent_type, AgentClass in [("react", ReActAgent), ("reflective", ReflectiveAgent)]:
        env = GridWorld(
            size=size, obstacle_ratio=obstacle_ratio, seed=seed,
            random_start_goal=True, observation_mode="fog_of_war",
            view_range=2, num_dynamic_obstacles=3, dynamic_obstacle_speed=2,
        )
        agent = AgentClass(seed=seed)
        
        # Collect trajectory
        trajectory = []
        obs = env.reset()
        agent.reset()
        
        for step in range(200):
            o = obs if isinstance(obs, dict) else env._get_obs()
            action = agent.act(o, env) if hasattr(agent, 'act') else agent(o, env)
            trajectory.append(o.get("agent_pos", env.agent_pos))
            
            if hasattr(agent, 'reflection_count') and hasattr(agent, 'em'):
                if agent.step > 0 and agent.step % agent.reflection_interval == 0:
                    fb = agent.reflect(agent.em.recent(10))
                    if fb:
                        agent.last_feedback = fb
                        agent.reflection_count += 1
                pos = o.get("agent_pos", env.agent_pos)
                agent.em.record(pos, action, False)
            
            next_obs, reward, done, info = env.step(action)
            if done or reward > 0:
                trajectory.append(env.agent_pos)
                break
            obs = next_obs
        
        title = f"ReAct Agent — fog_of_war ({len(trajectory)} steps)" if agent_type == "react" else \
                f"Reflective Agent — fog_of_war ({len(trajectory)} steps, {agent.reflection_count} reflections)"
        plot_trajectory(env, trajectory, title, f"e1_trajectory_{agent_type}.png")


# ═══════════════════════════════════════════════════════════════
#  Main
# ═══════════════════════════════════════════════════════════════

def main():
    parser = argparse.ArgumentParser(description="Visualize E1 experiment results")
    parser.add_argument("--results", help="Path to results JSON file")
    parser.add_argument("--demo", action="store_true", help="Run a fresh demo episode with trajectory render")
    args = parser.parse_args()
    
    if args.demo:
        print("Running demo episode...")
        run_demo(seed=42)
        print("Done!")
        return
    
    data = _load_results(args.results)
    if data is None:
        return
    
    print(f"Loaded results: {data['config']}")
    print()
    
    # Plot 1: Comparison bars
    print("Generating comparison bar chart...")
    plot_comparison_bars(data)
    
    # Plot 2: Trajectory (if enough detail in results)
    print("\nTo render trajectory maps, run:")
    print("  python experiments/e1_reflection/visualize.py --demo")


if __name__ == "__main__":
    main()
