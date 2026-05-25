# E4: 知觉表征与决策实验

## 实验目的

论证一个核心命题：**智能体的决策以知觉表征为基础**——即，决策不是直接基于原始感官输入，而是基于对这些输入的结构化、抽象化表征（representation）。

对应到人类认知：人所做的一些决策是以知觉的表征为基础的（Barsalou, 1999; Fodor, 1975）。如果将智能体视为认知系统，同样的原理是否成立？什么条件下成立？

## 核心假设

### H0（零假设）
知觉表征对决策无显著影响。在相同任务下，有表征的智能体与无表征（端到端）的智能体性能无差异。

### H1（备择假设）
高质量的知觉表征显著提升决策质量，尤其是在需要**泛化、推理和长序列规划**的任务中。

### 细化预测

1. **简单任务中差异不大**——表征带来的计算开销可能抵消收益
2. **复杂迷宫/部分可观测中差异显著**——表征提供结构化的世界模型，弥补感知缺失
3. **分布外泛化中差异最大**——表征是可迁移的结构，而非单纯的模式匹配
4. **表征的质量决定上限**——语义表征（含任务相关概念）优于纯结构化表征

## 实验设计

### 自变量 1：感知表征的类型（三组对照）

| 条件 | 代码标识 | 智能体获取的信息 | 类比人类 | 架构 |
|------|---------|-----------------|---------|------|
| **A. 原始感知** | `raw` | 直接 sensor 值（如局部栅格 0/1 矩阵） | 婴儿/反射式 | 端到端策略网络 |
| **B. 结构化表征** | `structured` | 抽象后的结构化信息（物体列表、空间关系图、拓扑） | 普通人看地图 | 感知→显式表征→决策 |
| **C. 语义表征** | `semantic` | 带任务相关语义的结构化信息（"死胡同""已探索区域""可探索前沿"） | 专家/老手 | 感知→表征→语义标注→决策 |

### 自变量 2：任务难度（六个层级）

| 任务 | 代码 | 描述 | 预期表征效应 |
|------|------|------|------------|
| T1. 简单直线 | `straight` | 起点到终点无障碍 | 三种条件无差异 |
| T2. 有限障碍 | `simple_obstacle` | 需绕 1-2 个障碍 | Raw 稍慢，B/C 持平 |
| T3. 复杂迷宫 | `maze` | 需多次回溯，含死胡同 | B 明显优于 A，C 最优 |
| T4. 分布外泛化 | `ood_generalize` | 训练仅 L 形迷宫，测试出现 T 形、十字形 | **B/C 显著优于 A** |
| T5. 部分可观测 | `fog_of_war` | 迷雾模式，需记忆力构建环境模型 | **只有 B/C 能完成** |
| T6. 环境扰动 | `perturbation` | 运行中突然移动目标/新增障碍 | C 适应最快 |

### 因变量

| 指标 | 说明 |
|------|------|
| **任务成功率** | 到达目标的回合比例 |
| **步数效率** | 实际步数 / 最优步数比 |
| **泛化能力** | 在未见过的地图上的性能衰减比 |
| **鲁棒性** | 环境扰动后的恢复步数 |
| **表征利用率** | 表征空间的熵、维度有效利用率 |

## 核心论证逻辑

```
                ┌─────────────────────────────────────────┐
                │          核心论证逻辑                     │
                │                                         │
                │ 如果 H1 成立，应该观察到：                │
                │                                         │
                │ 1. 在简单任务中，三种表征差异不大          │
                │    → 说明决策本身不需要复杂表征            │
                │                                         │
                │ 2. 随着任务复杂度增加，差异拉大            │
                │    → 说明"需要表征"是任务条件决定的         │
                │                                         │
                │ 3. 分布外泛化中，B/C 显著优于 A           │
                │    → 说明表征提供了"可迁移的结构"，         │
                │      而非单纯的模式匹配                   │
                │                                         │
                │ 4. 部分可观测中，只有 B/C 表现好          │
                │    → 说明表征的一个重要功能是               │
                │      "补充不完整的感知"                   │
                └─────────────────────────────────────────┘
```

## 智能体实现

### Condition A: Raw Perception (端到端)

```python
# 输入: 5×5 局部栅格 (0=空地, 1=障碍, 2=目标)
# 输出: 动作 (上/下/左/右)
state = grid.get_local_view(agent_pos, radius=2)  # 25 个标量
action = policy_network(state.flatten())
# 或用规则: 如果目标可见→直线移动; 否则→随机/右手法则
```

- 无显式内部表征
- 决策直接基于 sensor 值
- 类比：反射弧

### Condition B: Structured Representation

```python
# 表征构建: 感知 → 结构化
representation = {
    "ego_position": (x, y),
    "goal_direction": (dx, dy),            # 目标相对方向向量
    "frontier_nodes": [(x1,y1), ...],      # 可探索前沿（未知区域边界）
    "walls": [((x1,y1), (x2,y2)), ...],    # 障碍物线段
    "topology": adjacency_matrix,           # 连通图（可达性）
    "explored_mask": np.array(...),         # 已探索区域掩码
}
# 决策基于结构化表征，而非原始像素
action = planner(representation)
```

- 感知先转换为结构化数据
- 决策基于这些结构化信息
- 类比：人在看地图

### Condition C: Semantic Representation

```python
# 表征构建: 感知 → 结构化 → 语义标注
representation = {
    "situation_type": "dead_end",           # 情境类型归类
    "goal_direction": "northeast",
    "exploration_status": "explored_75%",   # 对环境的认知状态
    "recent_trajectory": [cell_types],      # 历史轨迹的语义化
    "uncertainty": 0.3,                     # 对环境的认知不确定性
    "abstract_goal": "go_to_region_B",      # 抽象化的子目标
    "frontier_quality": {"region_A": 0.8},  # 各区域的探索价值估计
}
# 决策基于语义化表征
action = reasoner(representation)
```

- 在结构化基础上加语义标签
- 引入"情境理解"——识别当前环境类型
- 类比：专家下棋，不是看棋子位置而是看"局面"

## 拓展方向

### 1. 表征的可干预性

在决策前人为扰动表征（引入噪声、删除某些维度），观察决策是否相应变化→更直接证明"决策依赖表征"。

```python
# 干预条件
def intervene(representation, intervention_type="drop_goal"):
    if intervention_type == "drop_goal":
        del representation["goal_direction"]
    elif intervention_type == "noise_topology":
        representation["topology"] += noise
    return representation
```

### 2. 表征涌现的可视化

对 Condition B/C 的智能体，在训练过程中可视化表征空间的变化（t-SNE / PCA），观察是否逐渐收敛到有意义的结构。

### 3. System 1 + System 2 双系统

实现双系统架构：
- **System 1（快）**：基于原始感知的直觉反应
- **System 2（慢）**：基于表征的推理决策
- 观察何时触发 System 2，以及触发条件是否随训练变化

## 实验映射到 SomatoMind Brain

| Brain 模块 | E4 实现 |
|-----------|---------|
| Perception | GridWorld 观测适配器（局部栅格 + 全局坐标） |
| Sensory Buffer | 原始感知暂存（Condition A 用） |
| Working Memory | 表征存储（Condition B/C 用） |
| Attention | 选择表征中的哪些维度参与决策 |
| Spatial | 拓扑图构建 + 空间关系推理 |
| Reasoning | 语义标注 + 情境分类（Condition C） |
| Fast Loop | 每步：感知→表征→决策→动作 |
| Meta-Cognition | 表征质量监控——是否需要更新或修正 |

## 实验计划

### Phase 1: 基线搭建
- [ ] 实现 GridWorld 任务集（T1-T6）
- [ ] 实现 Condition A（原始感知基线）
- [ ] 实现 Condition B（结构化表征）
- [ ] 实现评估指标计算

### Phase 2: 核心实验
- [ ] 在 T1-T6 上跑完三组对照
- [ ] 收集统计显著的对比数据
- [ ] 可视化表征空间

### Phase 3: 深入分析
- [ ] 表征干预实验
- [ ] 双系统架构探索
- [ ] 抽象层级与决策质量的关系曲线

## 参考文献

- Barsalou, L. W. (1999). *Perceptual symbol systems.* Behavioral and Brain Sciences, 22(4), 577-660.
- Fodor, J. A. (1975). *The Language of Thought.* Harvard University Press.
- Marr, D. (1982). *Vision: A Computational Investigation into the Human Representation and Processing of Visual Information.* MIT Press.
- Kahneman, D. (2011). *Thinking, Fast and Slow.* Farrar, Straus and Giroux.
- McClelland, J. L., et al. (2010). *Letting structure emerge: connectionist and dynamical systems approaches to cognition.* Trends in Cognitive Sciences.
- Lake, B. M., et al. (2017). *Building machines that learn and think like people.* Behavioral and Brain Sciences.
