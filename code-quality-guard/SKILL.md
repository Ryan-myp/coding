---
name: code-quality-guard
description: "工业级 AI 代码质量守护专家 — 五轴审查/四角色评估/蒸馏进化。覆盖架构、安全、性能、可维护性、测试五大维度，支持 Python/TypeScript/Go/Java/Rust 全语言。集成 TDD、STRIDE 威胁建模、API 设计、重构手册、可观测性等 20+ 工业级工程实践"
version: 3.0.0
author: ryan
created: 2025-09-10
platforms: [linux, macos, windows]
tags: [code-quality, architecture, security, review, maintainability, distillation, agent, multi-language, tdd, observability, api-design, refactoring, distributed-systems]
compatibility: "Python 3.8+, Node.js 18+, 任何支持 AGENTS.md/SKILL.md 的 Agent 平台 (Codex/Cursor/Claude/Gemini/Copilot/OpenCode/Kiro)"
metadata:
  review_axes: 5
  roles: 4
  languages_supported: 6
  distillation: true
  playbooks: 12
  patterns: 30
  anti_patterns: 15
---

# Code Quality Guard v3.0 — 工业级代码质量守护体系

> 基于 addyosmani/agent-skills (⭐93k)、alirezarezvani/claude-skills (⭐25k) 及 12 个顶级开源工程实践构建

## 🎯 定位与目标

**要解决的问题：**
AI Agent 写代码时质量参差不齐——功能可用但维护灾难，不同人/不同 Agent 输出风格迥异，安全隐患频发，缺乏统一标准。

**本 Skill 提供：**
- **一套统一的质量标准** — 所有 Agent 遵循同一套规则
- **工业级的检查清单** — 覆盖从设计到部署的全生命周期
- **持续进化的知识体系** — 通过蒸馏机制从优秀代码中学习

## 🏛️ 五轴 × 四角色 审查矩阵

### 五轴评分体系（每轴独立评分，加权汇总）

```
                    ┌─────────────────────────────────────────┐
                    │           Code Quality Guard            │
                    │         五轴 × 四角色矩阵               │
                    ├──────────┬──────────┬──────────┬────────┤
                    │ Correct. │ Readable │ Architect│ Secure │ Perf. │
                    │  (20%)   │  (20%)   │  (25%)   │ (20%)  │(15%)  │
                    ├──────────┼──────────┼──────────┼────────┼───────┤
  Architect 🏗️    │          │          │    ✓     │        │       │
  Engineer 👷     │    ✓     │    ✓     │          │   ✓    │   ✓   │
  Security 🔒     │          │          │          │   ✓    │       │
  Performer ⚡    │          │          │          │        │   ✓   │
                    └──────────┴──────────┴──────────┴────────┴───────┘
                              ↓
                    综合评分 0-100，四级门禁
```

### 质量门禁

| 分数 | 等级 | Emoji | 门禁结果 | 行动 |
|------|------|-------|---------|------|
| 90-100 | Excellent | 🟢 | **自动通过** | 候选蒸馏入库 |
| 70-89 | Good | 🟡 | **条件通过** | 修复警告后合入 |
| 50-69 | Fair | 🟠 | **有条件通过** | 必须修复 Critical |
| 0-49 | Poor | 🔴 | **驳回** | 重写后重审 |

## 🔄 全生命周期工作流

```
┌──────────┐    ┌──────────┐    ┌──────────┐    ┌──────────┐    ┌──────────┐
│  0. 需求  │ →  │  1. 架构  │ →  │  2. 规范  │ →  │  3. 实现  │ →  │  4. 审查  │
│  Interview│    │  RFC/ADR │    │  Constraints│   │  TDD Loop │   │  5-Axis  │
└──────────┘    └──────────┘    └──────────┘    └──────────┘    └──────────┘
                                                      │
                                                      ▼
┌──────────┐    ┌──────────┐    ┌──────────┐    ┌──────────┐    ┌──────────┐
│  8. 进化  │ ←  │  7. 部署  │ ←  │  6. 发布  │ ←  │  5a.修复  │ ←  │  4. 审查  │
│ Distill  │    │ Strategy │    │  Review  │    │  迭代   │    │  Gate    │
└──────────┘    └──────────┘    └──────────┘    └──────────┘    └──────────┘
```

### Phase 0: 需求澄清（Interview Mode）

当需求模糊时，先问问题而不是直接写代码：

```
HYPOTHESIS: 你想构建 [X]，因为 [原因]
CONFIDENCE: XX% — 缺少 [关键信息]

Q: [下一个澄清问题]
GUESS: [我的假设]
```

触发条件：需求缺少 who/why/success metric/constraint 中任意一个。

### Phase 1: 架构设计（RFC/ADR）

在写任何代码之前：
1. 写 RFC（Request for Comments）文档
2. 记录 Architecture Decision Records (ADRs)
3. 明确模块边界和依赖方向
4. 定义接口契约（Contract First）

### Phase 2: 质量约束（Constraints）

定义 "三 tier 行为准则"：
- **Always Do:** 无条件遵守的规则
- **Ask First:** 需要人工确认的规则
- **Never Do:** 绝对禁止的规则

### Phase 3: TDD 实现循环

```
RED → GREEN → REFACTOR → (repeat)
```

### Phase 4: 五轴联合审查

### Phase 5: 质量门禁 + 修复迭代

### Phase 6: Code Review

### Phase 7: 部署策略

### Phase 8: 蒸馏进化

## 📐 五轴详细检查清单

### Axis 1: Correctness (20分)

| 检查项 | 关键问题 | 扣分 |
|--------|---------|------|
| 边界条件 | null/empty/边界值是否处理？ | -5/case |
| 错误路径 | 异常分支是否有处理？ | -3/path |
| 竞态条件 | 并发场景下是否安全？ | -5/slot |
| 状态一致性 | 状态变更是否原子？ | -4/inconsistent |
| 类型安全 | 是否使用了 unsafe cast？ | -2/cast |

### Axis 2: Readability (20分)

| 检查项 | 关键问题 | 扣分 |
|--------|---------|------|
| 命名质量 | 名称是否表达意图？ | -3/name |
| 函数长度 | 是否 > 50 行（Python/Go）或 > 80 行（Java/TS）？ | -4/long |
| 嵌套深度 | 是否 > 3 层？ | -3/nested |
| 注释质量 | 是否说明"为什么"而非"是什么"？ | -2/comment |
| DRY | 有无重复代码块？ | -4/dup |

### Axis 3: Architecture (25分)

| 检查项 | 关键问题 | 扣分 |
|--------|---------|------|
| 分层清晰 | 是否存在跨层调用？ | -5/cross-layer |
| 单一职责 | 类/模块是否只做一件事？ | -4/god-class |
| 依赖方向 | 是否存在循环依赖？ | -5/circular |
| 扩展点 | 新功能是否需要改大量代码？ | -3/inflexible |
| 接口设计 | 是否符合 Contract First？ | -4/bad-interface |

### Axis 4: Security (20分)

| 检查项 | 关键问题 | 扣分 |
|--------|---------|------|
| 输入验证 | 外部输入是否在边界验证？ | -5/unvalidated |
| SQL注入 | 是否使用参数化查询？ | -8/sql-inject |
| 密钥管理 | 是否有硬编码密钥？ | -8/hardcoded-secret |
| 认证授权 | 是否检查了权限？ | -5/no-authz |
| 依赖安全 | 依赖是否有已知CVE？ | -4/vulnerable-dep |

### Axis 5: Performance (15分)

| 检查项 | 关键问题 | 扣分 |
|--------|---------|------|
| N+1查询 | 有无循环中的单次查询？ | -5/n-plus-1 |
| 算法复杂度 | 有无 O(n²) 或更差？ | -4/complex |
| 内存管理 | 有无泄漏风险？ | -4/memory-leak |
| 缓存策略 | 热点数据是否缓存？ | -3/no-cache |
| 超时控制 | 外部调用是否有超时？ | -3/no-timeout |

## 🔬 蒸馏进化机制

### 蒸馏触发条件

1. **高分代码自动候选** — 评分 ≥ 90 的代码自动进入模式池
2. **用户主动触发** — "用蒸馏模式分析这个代码库"
3. **定时蒸馏** — 扫描 `distillation/history.jsonl` 提取新模式

### 蒸馏流程

```
高质量代码
    │
    ├─→ 模式识别 → design patterns / name conventions / error handling
    ├─→ 反模式识别 → hardcode / god-class / spaghetti / security-smells
    └─→ 语言特异性 → 按语言分类归档
         │
         ▼
    自动追加到 references/
         │
         ▼
    更新 distillation/patterns.json 索引
         │
         ▼
    提示用户确认是否纳入检查清单
```

### 蒸馏产物

| 产物 | 位置 | 用途 |
|------|------|------|
| 设计模式库 | `references/patterns/` | 审查时参考优秀实践 |
| 反模式库 | `references/anti-patterns/` | 识别常见问题 |
| 语言检查清单 | `references/languages/` | 按语言定制审查 |
| 蒸馏历史 | `distillation/history.jsonl` | 追踪进化过程 |
| 模式索引 | `distillation/patterns.json` | 快速检索模式 |

## 🌐 多语言支持矩阵

| 语言 | 专项检查文件 | 特有关注点 |
|------|------------|-----------|
| Python | `architecture-python.md` | 类型注解、GIL、装饰器、包结构 |
| TypeScript | `architecture-ts.md` | 泛型约束、ESM/CJS、React模式、类型守卫 |
| Go | `architecture-go.md` | 接口设计、Context、goroutine泄漏、error sentinel |
| Java | `architecture-java.md` | Spring分层、DI、事务、检查型异常 |
| Rust | `architecture-rust.md` | 所有权、Error枚举、零成本抽象、Send/Sync |
| 通用 | `*-universal.md` | SOLID、分层、STRIDE、性能 |

## 📋 内置 Playbook（12个）

| # | Playbook | 触发场景 |
|---|----------|---------|
| 1 | `tdd-workflow` | 实现新逻辑/修复bug |
| 2 | `threat-modeling` | 安全审计/新API设计 |
| 3 | `api-design` | 设计REST/GraphQL接口 |
| 4 | `refactoring` | 重构现有代码 |
| 5 | `migration` | 数据库迁移/依赖升级 |
| 6 | `performance-profile` | 性能问题排查 |
| 7 | `observability` | 添加日志/监控/追踪 |
| 8 | `legacy-code` | 处理遗留代码 |
| 9 | `deployment-strategy` | 制定发布策略 |
| 10 | `incident-response` | 线上事故响应 |
| 11 | `code-review` | PR Review |
| 12 | `distillation` | 从代码库提取最佳实践 |

每个 playbook 包含：触发条件、检查清单、具体操作步骤、输出物、常见陷阱。

## 🚀 快速使用

### 审查代码

```
按照 code-quality-guard v3 标准审查以下代码：
[代码或文件路径]

要求：
1. 五轴评分（Correctness/Readability/Architecture/Security/Performance）
2. 四角色联合评估
3. 严重程度分级：Critical / Required / Optional / Nit
4. 结构性修复建议（不只是指出问题，给出重构方案）
5. 质量门禁判定
6. 如 ≥90 分，提示可蒸馏入库
```

### 安全威胁建模

```
对以下功能进行 STRIDE 威胁建模：
[功能描述或代码]
输出：威胁列表 + 缓解措施 + 信任边界图
```

### TDD 实现

```
按 TDD 流程实现 [功能]：
1. 先写 RED 测试（失败测试）
2. 写最小 GREEN 实现
3. REFACTOR 在测试保护下清理
4. 运行五轴审查确认质量
```

### API 设计

```
按 code-quality-guard 的 API Design 规范设计 [接口]：
1. Contract First（先定义接口）
2. 一致的错误语义
3. 边界验证
4. 幂等性设计
5. 版本兼容策略
```

### 蒸馏进化

```
用 code-quality-guard 蒸馏模式分析：
[仓库路径]

任务：
1. 识别设计模式和反模式
2. 提取多语言代码示例
3. 更新 patterns/ 和 anti-patterns/
4. 记录到 distillation/history.jsonl
```

### RFC/ADR 撰写

```
为 [架构决策] 撰写 ADR：
1. 上下文（为什么需要这个决策）
2. 决策内容
3. 替代方案及权衡
4. 后果（好/坏）
5. 状态（proposed/accepted/deprecated）
```

## 📂 目录结构

```
code-quality-guard/
├── SKILL.md                          # 主入口（本文档）
├── references/
│   ├── patterns/                     # 模式库（蒸馏产出）
│   │   ├── DESIGN_PATTERNS.md        # 20+ 设计模式（多语言）
│   │   ├── NAME_CONVENTIONS.md       # 跨语言命名规范
│   │   ├── ERROR_HANDLING.md         # 错误处理模式
│   │   └── API_DESIGN.md             # API 设计模式
│   ├── anti-patterns/                # 反模式库
│   │   ├── HARDCODE.md               # 硬编码
│   │   ├── GOD_CLASS.md              # 上帝类
│   │   ├── SPAGHETTI.md              # 面条代码
│   │   ├── SWISS_ARMY_FUNCTION.md    # 瑞士军刀函数
│   │   ├── FEATURE_REGRESSION.md     # 功能蔓延
│   │   └── SECURITY_SMELLS.md        # 安全反模式
│   ├── languages/                    # 语言专项检查清单
│   │   ├── architecture-universal.md # 通用架构（SOLID）
│   │   ├── architecture-python.md
│   │   ├── architecture-ts.md
│   │   ├── architecture-go.md
│   │   ├── architecture-java.md
│   │   ├── architecture-rust.md
│   │   ├── security-universal.md     # STRIDE + OWASP
│   │   ├── performance-universal.md
│   │   └── engineering-universal.md
│   ├── guides/                       # 工业级指南
│   │   ├── tdd-workflow.md           # TDD 工作流
│   │   ├── api-design-guide.md       # API 设计规范
│   │   ├── threat-modeling-guide.md  # 威胁建模指南
│   │   ├── refactoring-playbook.md   # 重构手册
│   │   ├── migration-guide.md        # 迁移指南
│   │   ├── observability-guide.md    # 可观测性指南
│   │   ├── deployment-strategies.md  # 部署策略
│   │   ├── legacy-code-handling.md   # 遗留代码处理
│   │   ├── incident-response.md      # 事故响应
│   │   └── code-review-playbook.md   # Code Review 手册
│   └── schemas/
│       └── review-result.schema.json
├── playbooks/                        # 12个 Playbook
│   ├── tdd-workflow.md
│   ├── threat-modeling.md
│   ├── api-design.md
│   ├── refactoring.md
│   ├── migration.md
│   ├── performance-profile.md
│   ├── observability.md
│   ├── legacy-code.md
│   ├── deployment-strategy.md
│   ├── incident-response.md
│   ├── code-review.md
│   └── distillation.md
├── scripts/
│   ├── distill.py                    # 蒸馏引擎（多语言模式识别）
│   ├── score.py                      # 五轴评分引擎
│   ├── report.py                     # 报告生成器
│   ├── threat_model.py               # STRIDE 威胁建模
│   ├── diff_analyzer.py              # 变更影响面分析
│   └── gate_checker.py               # 质量门禁检查
├── templates/
│   ├── review-report.md
│   ├── adr-template.md
│   ├── rfc-template.md
│   └── distillation-log.md
├── hooks/
│   └── pre-commit.sh                 # Git 预提交门禁
└── distillation/                     # 运行时蒸馏产出
    ├── patterns.json
    └── history.jsonl
```

## 🔗 与其他 Skill 的集成

| 集成 Skill | 协作方式 |
|-----------|---------|
| `biz-delivery` | TD 阶段 Architect 审查方案，实现阶段五轴审查 |
| `ryan-expert-skills` | 利用领域知识增强审查深度 |
| 各平台 API Skills | 对 API 集成代码进行安全 + 性能审查 |
| 自建项目 Skill | 根据项目特点定制权重和检查项 |

## 🚢 部署

```bash
# 安装到 pi
ln -s /path/to/code-quality-guard ~/.agents/skills/code-quality-guard

# 安装到 Claude Code
npx skills add Ryan-myp/coding --skill code-quality-guard

# 安装到 Codex
codex plugin marketplace add Ryan-myp/coding
codex plugin add code-quality-guard@ryan-myp-coding

# 安装到 Cursor
# 复制到 .cursor/skills/code-quality-guard/

# 安装到 OpenCode
cp -r code-quality-guard ~/.config/opencode/skills/
```

## 🤝 贡献指南

1. 新增代码符合本 Skill 检查清单
2. 新增模式需附 ≥2 种语言的代码示例
3. 蒸馏记录需包含来源、提取逻辑、置信度
4. 更新 `distillation/history.jsonl`
5. 文档使用中英文对照
