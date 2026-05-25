<div align="center">
  <h1>🧬 SomatoMind</h1>
  <p><em>Shape shapes the mind — Morphology determines intelligence.</em></p>
  <p align="center">
    <strong>From experiments to a brain that controls machines.</strong><br />
    Exploring the structure of intelligence through computational experiments,
    building toward a deployable <strong>Brain</strong> for embodied agents.
  </p>
  <p>
    <a href="LICENSE"><img src="https://img.shields.io/badge/license-MIT-blue" alt="License: MIT"></a>
    <a href="https://github.com/zhangshuaiqing/SomatoMind/issues"><img src="https://img.shields.io/badge/contributions-welcome-brightgreen" alt="Contributions Welcome"></a>
  </p>
</div>

---

## 🌱 缘起 / Motivation

当前的 AI 系统（包括大语言模型和 Agent 框架）展现了一定程度的"智能"，但在很多实际任务中仍然"不及格"。为什么？

- **神经科学**告诉我们：果蝇的完整连接组被迁移到计算机后，其数字孪生体表现出与真实果蝇相同的行为模式——**结构决定功能**。
- **认知科学**告诉我们：人类的智能不仅仅来自前向传播，还依赖于**工作记忆、迭代反思、长程反馈、多时间尺度的动态系统**。
- **计算机科学**告诉我们：现有 Transformer + 前馈神经网络架构，缺少生物神经系统中大量存在的 **递归回路、侧向连接、可塑性机制和神经调制**。

SomatoMind 项目源于这样的信念：

> **要理解智能，不能只堆参数，而要借鉴生物的结构。**

## 🎯 终极目标 / North Star

> **构建一个真正的"大脑"（Brain）——一个具备结构化认知能力的智能体，能够操控物理世界中的设备或机器人。**

这个 Brain 不是今天的 LLM Agent 那样"一次响应定胜负"，而是：

- **有内部结构**：工作记忆、反思回路、多时间尺度的动态系统
- **能持续进化**：部署后根据与环境的交互不断调整自身连接
- **适应多模态**：从 GridWorld 的符号感知 → 仿真中的视觉/力觉 → 真实机器人的传感器
- **可移植**：同一个 Brain 架构，从实验环境稳定迁移到物理硬件

## 🧪 三阶段路线图 / Three-Phase Roadmap

### Phase 1: 单体智能的结构探索（在 GridWorld 中验证核心假设）

| 实验 | 描述 | 状态 |
|------|------|------|
| **E1 — 反思回路** | 导航 Agent + 结构化 Working Memory + Reflection 循环，对比纯 ReAct | 🔲 未开始 |
| **E2 — 可微分架构对比** | 纯前馈 vs LSTM vs 侧向连接+反馈回路的泛化能力 | 🔲 未开始 |
| **E3 — 部署后自我进化** | EWC / Differentiable Plasticity / 结构可塑性 | 🔲 未开始 |

### Phase 2: 构建 Brain 原型（将已验证的结构整合为统一大脑）

| 组件 | 描述 | 状态 |
|------|------|------|
| **B1 — Brain Core** | 整合 E1~E3 的有效结构，形成统一的"大脑"架构 | 🔲 未开始 |
| **B2 — 感知适配器** | 将环境观测映射到 Brain 的内部表征空间 | 🔲 未开始 |
| **B3 — 运动控制器** | Brain 输出的抽象决策到具体动作序列的映射 | 🔲 未开始 |
| **B4 — 认知监控器** | 元认知层——监控决策质量、自动触发反思 | 🔲 未开始 |

### Phase 3: 具身化与群体智能

| 实验 | 描述 | 状态 |
|------|------|------|
| **E4 — GridWorld 中验证 Brain** | 用 Brain 替代现有 LLM Navigator 做端到端验证 | 🔲 未开始 |
| **E5 — 仿真到实物的 Bridge** | Brain 控制 ROS2 + Gazebo 中的机器人 | 🔲 未开始 |
| **E6 — 群体涌现** | 多 Brain 通过共享隐状态环境痕迹涌现群体行为 | 🔲 未开始 |

> 🌐 项目主页：https://zhangshuaiqing.github.io/SomatoMind

## 🧰 实验平台 / Platform

- **Phase 1 实验床**：基于 [navigation-agent](https://github.com/zhangshuaiqing/navigation-agent) 的 GridWorld 环境
  - 支持 `full / local / fog_of_war` 三种观测模式
  - 支持动态障碍物、多 Agent 场景
  - 便于快速迭代和验证假设
- **Phase 3 实验床**：ROS2 + Gazebo（与 [robot](https://github.com/zhangshuaiqing/robot) 项目协作）
  - 从 GridWorld 的符号世界迁移到连续控制
  - 最终过渡到实物机器人

## 📁 项目结构

```
SomatoMind/
├── experiments/          # 核心实验代码
│   ├── e1_reflection/    # 反思回路实验
│   ├── e2_architecture/  # 网络架构对比实验
│   ├── e3_self_evolve/   # 部署后进化实验
│   └── ...
├── brain/                # 🧠 Brain 认知架构原型
│   ├── core/             # 核心引擎（快/慢回路调度）
│   ├── memory/           # 记忆系统
│   │   ├── sensory_buffer/   # 感觉缓冲（毫秒级）
│   │   ├── working_memory/   # 工作记忆（秒级）
│   │   ├── episodic_memory/  # 情景记忆（分钟级）
│   │   └── procedural_memory/# 程序记忆（长期技能）
│   ├── perception/       # 感知 + 注意力 + 世界模型
│   ├── cognition/        # 高级认知
│   │   ├── reasoning/    # 推理（符号 + 概率）
│   │   ├── planning/     # 规划（搜索 + 分解）
│   │   ├── reflection/   # 反思 / 元认知
│   │   ├── attention/    # 注意力机制
│   │   ├── spatial/      # 空间推理 + 心理模拟
│   │   └── creativity/   # 创造力 / 探索
│   ├── action/           # 动作输出 + 运动控制
│   └── plasticity/       # 可塑性系统（持续学习）
├── papers/               # 相关论文笔记与参考文献
├── docs/                 # 架构文档、实验设计思路
├── results/              # 实验结果与可视化
├── tools/                # 通用工具代码
├── notebooks/            # Jupyter 分析 notebooks
├── requirements.txt      # 依赖
└── README.md
```

## 🤝 参与贡献

这是一个开源探索项目，欢迎所有人参与讨论和贡献！

- **提建议**：在 [Issues](https://github.com/zhangshuaiqing/SomatoMind/issues) 中提出新想法或批评
- **做实验**：Fork 仓库，实现你的实验，提交 PR
- **写笔记**：如果你读过相关的论文或书籍，欢迎在 `papers/` 或 `docs/` 中添加笔记
- **讨论**：在 [Discussions](https://github.com/zhangshuaiqing/SomatoMind/discussions) 中参与头脑风暴

## 📚 核心参考文献

- Winding et al. (2023). *The connectome of an insect brain.* Science
- Shinn et al. (2023). *Reflexion: Language Agents with Verbal Reinforcement Learning.* arXiv:2303.11366
- Miconi et al. (2019). *Differentiable plasticity: training plastic neural networks with backpropagation.* ICML
- Kirkpatrick et al. (2017). *Overcoming catastrophic forgetting in neural networks.* PNAS
- Foerster et al. (2016). *Learning to Communicate with Deep Distributed Recurrent Q-Networks.* arXiv:1602.02672

---

<div align="center">
  <sub>Built with curiosity by <a href="https://github.com/zhangshuaiqing">@zhangshuaiqing</a></sub>
</div>
