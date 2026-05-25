"""
GridWorld — Pure Python grid navigation environment.

No external dependencies beyond numpy. Completely self-contained within SomatoMind.

Interface (backward-compatible with navigation-agent's GridWorld):
  env = GridWorld(size=10, obstacle_ratio=0.2, seed=42, random_start_goal=True,
                  observation_mode="fog_of_war", view_range=2)
  obs = env.reset()           # returns observation dict
  obs, reward, done, info = env.step("up")  # "up"|"down"|"left"|"right"
  env.render()                # returns string representation

Observation dict fields:
  agent_pos, goal_pos, goal_visible, goal_direction, surroundings,
  distance_to_goal, step_count, observation_mode, grid_size

For Web UI export:
  export_json = env.to_json()  # serializable dict for frontend rendering
"""

import random
from dataclasses import dataclass, field
from enum import IntEnum
from typing import Any, Dict, List, Optional, Tuple


class CellType(IntEnum):
    EMPTY = 0
    OBSTACLE = 1
    AGENT = 2
    GOAL = 3
    DYNAMIC_OBSTACLE = 5


@dataclass
class DynamicObstacle:
    pos: Tuple[int, int]
    direction: str = "right"
    speed: int = 1
    move_prob: float = 0.5
    boundary_mode: str = "bounce"  # bounce, wrap, random


class GridWorld:
    """Pure Python GridWorld for navigation tasks.
    
    Coordinates: (row, col), (0,0) is top-left.
    Actions: "up", "down", "left", "right"
    """
    
    ACTIONS = ["up", "down", "left", "right"]
    DIRECTIONS = {
        "up": (-1, 0), "down": (1, 0),
        "left": (0, -1), "right": (0, 1),
    }
    
    def __init__(
        self,
        size: int = 8,
        obstacle_ratio: float = 0.2,
        seed: Optional[int] = None,
        random_start_goal: bool = False,
        observation_mode: str = "full",
        view_range: int = 1,
        num_dynamic_obstacles: int = 0,
        dynamic_obstacle_speed: int = 1,
    ):
        self.size = size
        self.obstacle_ratio = obstacle_ratio
        self.random_start_goal = random_start_goal
        self.observation_mode = observation_mode
        self.view_range = max(1, view_range)
        self.num_dynamic_obstacles = num_dynamic_obstacles
        self.dynamic_obstacle_speed = dynamic_obstacle_speed
        self.rng = random.Random(seed)
        
        self.grid = [[CellType.EMPTY] * size for _ in range(size)]
        self.agent_pos: Tuple[int, int] = (0, 0)
        self.goal_pos: Tuple[int, int] = (size - 1, size - 1)
        self.step_count: int = 0
        self.max_steps: int = size * size * 2
        self.done: bool = False
        self.visited = [[False] * size for _ in range(size)]
        self.dynamic_obstacles: List[DynamicObstacle] = []
        self._trajectory: List[Tuple[int, int]] = []
        
        self._generate_map()
    
    # ── Map Generation ──────────────────────────────
    
    def _generate_map(self):
        self.grid = [[CellType.EMPTY] * self.size for _ in range(self.size)]
        
        if self.random_start_goal:
            self._pick_start_goal()
        else:
            self.agent_pos = (0, 0)
            self.goal_pos = (self.size - 1, self.size - 1)
        
        num_obstacles = int(self.size * self.size * self.obstacle_ratio)
        candidates = [(r, c) for r in range(self.size) for c in range(self.size)
                      if (r, c) != self.agent_pos and (r, c) != self.goal_pos]
        self.rng.shuffle(candidates)
        for r, c in candidates[:num_obstacles]:
            self.grid[r][c] = CellType.OBSTACLE
        
        # Ensure a path exists
        self._clear_path_to_goal()
        
        self.grid[self.agent_pos[0]][self.agent_pos[1]] = CellType.AGENT
        self.grid[self.goal_pos[0]][self.goal_pos[1]] = CellType.GOAL
        self.visited = [[False] * self.size for _ in range(self.size)]
        self._update_visited()
        
        # Dynamic obstacles
        self.dynamic_obstacles.clear()
        self._init_dynamic_obstacles()
    
    def _pick_start_goal(self):
        cells = [(r, c) for r in range(self.size) for c in range(self.size)]
        self.rng.shuffle(cells)
        self.agent_pos = cells[0]
        self.goal_pos = cells[1]
    
    def _clear_path_to_goal(self):
        r, c = self.agent_pos
        gr, gc = self.goal_pos
        while (r, c) != (gr, gc):
            if self.rng.random() < 0.5 and r != gr:
                r += 1 if gr > r else -1
            elif c != gc:
                c += 1 if gc > c else -1
            else:
                r += 1 if gr > r else -1
            if self.grid[r][c] == CellType.OBSTACLE:
                self.grid[r][c] = CellType.EMPTY
    
    def _init_dynamic_obstacles(self):
        for _ in range(self.num_dynamic_obstacles):
            cells = [(r, c) for r in range(self.size) for c in range(self.size)
                     if self.grid[r][c] == CellType.EMPTY
                     and (r, c) != self.agent_pos
                     and (r, c) != self.goal_pos]
            if not cells:
                break
            pos = self.rng.choice(cells)
            dyn = DynamicObstacle(
                pos=pos, speed=self.dynamic_obstacle_speed,
                direction=self.rng.choice(["up", "down", "left", "right"]),
            )
            self.dynamic_obstacles.append(dyn)
            self.grid[pos[0]][pos[1]] = CellType.DYNAMIC_OBSTACLE
    
    def _update_dynamic_obstacles(self):
        for dyn in self.dynamic_obstacles:
            if self.rng.random() > dyn.move_prob:
                continue
            if self.step_count % dyn.speed != 0:
                continue
            
            r, c = dyn.pos
            dr, dc = self.DIRECTIONS[dyn.direction]
            nr, nc = r + dr, c + dc
            
            # Bounce off walls
            if not (0 <= nr < self.size and 0 <= nc < self.size):
                opposites = {"up": "down", "down": "up", "left": "right", "right": "left"}
                dyn.direction = opposites[dyn.direction]
                dr, dc = self.DIRECTIONS[dyn.direction]
                nr, nc = r + dr, c + dc
            
            target = self.grid[nr][nc] if 0 <= nr < self.size and 0 <= nc < self.size else CellType.OBSTACLE
            if target not in (CellType.OBSTACLE, CellType.AGENT, CellType.GOAL, CellType.DYNAMIC_OBSTACLE):
                self.grid[r][c] = CellType.EMPTY
                dyn.pos = (nr, nc)
                self.grid[nr][nc] = CellType.DYNAMIC_OBSTACLE
    
    # ── Public API ──────────────────────────────────
    
    def reset(self) -> Dict:
        self.step_count = 0
        self.done = False
        self._trajectory.clear()
        self._generate_map()
        return self._get_obs()
    
    def step(self, action: str) -> Tuple[Dict, float, bool, Dict]:
        if self.done:
            return self._get_obs(), 0.0, True, {"reason": "already_done"}
        
        action = action.lower().strip()
        if action not in self.ACTIONS:
            return self._get_obs(), -0.1, False, {"error": f"Invalid action: {action}"}
        
        dr, dc = self.DIRECTIONS[action]
        nr, nc = self.agent_pos[0] + dr, self.agent_pos[1] + dc
        r, c = self.agent_pos
        
        if not (0 <= nr < self.size and 0 <= nc < self.size):
            reward = -0.5
            info = {"reason": "out_of_bounds"}
        elif self.grid[nr][nc] == CellType.OBSTACLE:
            reward = -0.5
            info = {"reason": "hit_obstacle"}
        elif self.grid[nr][nc] == CellType.DYNAMIC_OBSTACLE:
            reward = -1.0
            info = {"reason": "hit_dynamic_obstacle"}
        else:
            # Move agent
            self.grid[r][c] = CellType.EMPTY
            self.agent_pos = (nr, nc)
            self.grid[nr][nc] = CellType.AGENT
            self._trajectory.append((nr, nc))
            
            if self.agent_pos == self.goal_pos:
                reward = 10.0
                self.done = True
                info = {"reason": "reached_goal"}
            else:
                old_dist = abs(r - self.goal_pos[0]) + abs(c - self.goal_pos[1])
                new_dist = abs(nr - self.goal_pos[0]) + abs(nc - self.goal_pos[1])
                reward = 0.1 if new_dist < old_dist else -0.1
                info = {"reason": "moved"}
        
        self._update_dynamic_obstacles()
        self.step_count += 1
        
        if self.step_count >= self.max_steps:
            self.done = True
            info["reason"] = info.get("reason", "") + "_max_steps"
        
        self._update_visited()
        return self._get_obs(), reward, self.done, info
    
    def _get_obs(self) -> Dict:
        ar, ac = self.agent_pos
        gr, gc = self.goal_pos
        vr = self.view_range
        
        surroundings = []
        for dr in range(-vr, vr + 1):
            for dc in range(-vr, vr + 1):
                nr, nc = ar + dr, ac + dc
                if 0 <= nr < self.size and 0 <= nc < self.size:
                    if self.observation_mode == "fog_of_war" and not self.visited[nr][nc]:
                        surroundings.append("?")
                    elif (nr, nc) == self.agent_pos:
                        surroundings.append("A")
                    elif (nr, nc) == self.goal_pos:
                        surroundings.append("G")
                    elif self.grid[nr][nc] == CellType.OBSTACLE:
                        surroundings.append("#")
                    elif self.grid[nr][nc] == CellType.DYNAMIC_OBSTACLE:
                        surroundings.append("D")
                    else:
                        surroundings.append(".")
                else:
                    surroundings.append("X")
        
        if self.observation_mode == "full":
            goal_visible = True
            distance = abs(ar - gr) + abs(ac - gc)
        else:
            goal_visible = abs(ar - gr) <= vr and abs(ac - gc) <= vr
            distance = abs(ar - gr) + abs(ac - gc) if goal_visible else None
        
        goal_direction = None
        dr = gr - ar
        dc = gc - ac
        dirs = []
        if dr < 0: dirs.append("N")
        elif dr > 0: dirs.append("S")
        if dc < 0: dirs.append("W")
        elif dc > 0: dirs.append("E")
        goal_direction = "".join(dirs) if dirs else "HERE"
        
        return {
            "agent_pos": self.agent_pos,
            "goal_pos": self.goal_pos if self.observation_mode == "full" else None,
            "goal_visible": goal_visible,
            "goal_direction": goal_direction,
            "grid_size": self.size,
            "surroundings": surroundings,
            "distance_to_goal": distance,
            "step_count": self.step_count,
            "max_steps": self.max_steps,
            "observation_mode": self.observation_mode,
            "view_range": self.view_range,
        }
    
    def _update_visited(self):
        r, c = self.agent_pos
        self.visited[r][c] = True
    
    # ── Rendering ───────────────────────────────────
    
    def render(self, show_fog: bool = False) -> str:
        lines = []
        for r in range(self.size):
            row = ""
            for c in range(self.size):
                if show_fog and self.observation_mode == "fog_of_war" and not self.visited[r][c]:
                    row += " ? "
                elif (r, c) == self.agent_pos:
                    row += " A "
                elif (r, c) == self.goal_pos:
                    row += " G "
                elif self.grid[r][c] == CellType.OBSTACLE:
                    row += "###"
                elif self.grid[r][c] == CellType.DYNAMIC_OBSTACLE:
                    row += " D "
                else:
                    row += " . "
            lines.append(row)
        return "\n".join(lines)
    
    def to_json(self) -> Dict:
        """Serialize environment state for frontend rendering."""
        # Build full grid with positions for frontend
        display_grid = [[0] * self.size for _ in range(self.size)]
        for r in range(self.size):
            for c in range(self.size):
                cell = self.grid[r][c]
                if cell == CellType.EMPTY:
                    display_grid[r][c] = 0
                elif cell == CellType.OBSTACLE:
                    display_grid[r][c] = 1
                elif cell == CellType.DYNAMIC_OBSTACLE:
                    display_grid[r][c] = 5
                # AGENT and GOAL are overlaid from positions
                elif cell == CellType.AGENT:
                    display_grid[r][c] = 0
                elif cell == CellType.GOAL:
                    display_grid[r][c] = 0
        
        return {
            "size": self.size,
            "grid": display_grid,
            "agent_pos": list(self.agent_pos),
            "goal_pos": list(self.goal_pos),
            "step_count": self.step_count,
            "max_steps": self.max_steps,
            "done": self.done,
            "observation_mode": self.observation_mode,
            "view_range": self.view_range,
            "trajectory": [[int(p[0]), int(p[1])] for p in self._trajectory],
            "visited": self.visited,
            "dynamic_obstacles": [{"row": d.pos[0], "col": d.pos[1]} for d in self.dynamic_obstacles],
        }
