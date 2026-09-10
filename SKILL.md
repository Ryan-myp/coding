---
name: code-quality-guard
description: "AI 代码质量守护专家 — 多语言通用的代码审查、架构评估、安全审计与持续蒸馏进化。集成 Architect/Engineer/Security/Perf 四角色联合审查，支持 Codex/Cursor/Claude/Gemini/OpenCode 等所有 AI 编码 Agent"
version: 2.0.0
author: ryan
created: 2025-09-10
platforms: [linux, macos, windows]
tags: [code-quality, architecture, security, review, maintainability, distillation, agent, multi-language, tdd]
compatibility: "Python 3.8+, Node.js 18+, 任何支持 AGENTS.md/SKILL.md 的 Agent 平台"
metadata:
  review_axes: 5
  languages_supported: 6
  roles: 4
  distillation: true
---

# Code Quality Guard v2.0 — AI 代码质量守护专家

> 让所有 AI 编码 Agent 写出统一高质量代码，无论使用什么语言

## 🎯 问题与定位

当前 AI Agent 写代码的通病：
- **功能可用但维护灾难** — 架构随意、硬编码泛滥、可读性差
- **质量千差万别** — 不同 Agent、不同提示词风格导致输出参差不齐
- **安全漏洞频出** — SQL 注入、密钥硬编码、未验证输入
- **缺乏统一标准** — 每个团队/每个人自己定义规范，难以规模化

本 Skill 提供**一套统一的、语言无关的、可进化的代码质量标准**，所有 Agent 装了这个 Skill 后，写出的代码质量趋于一致。

## 🏛️ 四角色联合审查体系

| 角色 | 职责 | 关注维度 | 审查入口 |
|------|------|---------|---------|
| **Architect** 🏗️ | 架构设计审查 | 分层、解耦、模式、扩展点、变更影响面 | `references/languages/architecture-*.md` |
| **Engineer** 👷 | 工程化审查 | 可读性、命名、DRY、注释、错误处理 | `references/languages/engineering-*.md` |
| **Security** 🔒 | 安全合规审查 | STRIDE威胁建模、OWASP Top10、依赖安全 | `references/languages/security-*.md` |
| **Performer** ⚡ | 性能审查 | N+1查询、内存泄漏、算法复杂度、缓存策略 | `references/languages/performance-*.md` |

## 🔄 完整工作流（五阶段）

```
┌─────────────────────────────────────────────────────────────────┐
│  Phase 1: 编码前 — 架构指引                                      │
│  - 需求分析 → 推荐设计模式                                       │
│  - 分层建议 → 扩展点标记                                         │
│  - 技术选型建议                                                   │
└─────────────────────────────────────────────────────────────────┘
                           │
                           ▼
┌─────────────────────────────────────────────────────────────────┐
│  Phase 2: 编码中 — 实时规范提醒                                   │
│  - 命名规范提醒                                                  │
│  - 函数职责单一检查                                              │
│  - 避免反模式                                                    │
└─────────────────────────────────────────────────────────────────┘
                           │
                           ▼
┌─────────────────────────────────────────────────────────────────┐
│  Phase 3: TDD — 测试先行                                         │
│  - RED: 先写失败测试                                             │
│  - GREEN: 最小实现让测试通过                                     │
│  - REFACTOR: 在测试保护下重构                                    │
└─────────────────────────────────────────────────────────────────┘
                           │
                           ▼
┌─────────────────────────────────────────────────────────────────┐
│  Phase 4: 完成后 — 四角色联合审查                                 │
│  - Architect: 架构合理性 + 变更影响面                            │
│  - Engineer: 可读性 + 可维护性 + 可测试性                        │
│  - Security: STRIDE威胁建模 + OWASP Top10                        │
│  - Performer: 性能瓶颈 + 资源泄漏                                │
└─────────────────────────────────────────────────────────────────┘
                           │
                           ▼
┌─────────────────────────────────────────────────────────────────┐
│  Phase 5: 蒸馏进化                                               │
│  - 优质代码 → 提取模式入库                                        │
│  - 问题代码 → 提取反模式入库                                      │
│  - 检查清单迭代更新                                               │
└─────────────────────────────────────────────────────────────────┘
```

## 🚀 快速使用

### 审查已有代码

```
按照 code-quality-guard 标准审查以下代码：
[代码片段或文件路径]

要求：
1. 四角色联合审查
2. 按严重程度分级（Critical / Required / Optional / Nit）
3. 给出具体修复建议
4. 输出质量评分
```

### 编码前架构指引

```
准备写 [某个功能]，请先按 code-quality-guard 的 Architect 角色：
1. 分析需求关键点
2. 推荐设计模式
3. 给出分层建议
4. 标记扩展点
```

### 安全审计

```
按 code-quality-guard 的 Security 角色进行 STRIDE 威胁建模：
[代码或功能描述]
```

### TDD 指导

```
按 code-quality-guard 的 TDD 流程实现 [功能]：
1. 先写 RED 测试
2. 再写最小 GREEN 实现
3. 最后 REFACTOR
```

### 蒸馏进化

```
用 code-quality-guard 的蒸馏模式分析这个代码库：
[仓库路径]
提取最佳实践和反模式，更新模式库。
```

## 📊 五轴质量评分体系

每次审查覆盖五个维度，每个维度独立评分：

| 轴 | 权重 | 满分 | 关键检查项 |
|----|------|------|-----------|
| **Correctness** ✅ | 20% | 20 | 边界条件、错误处理、逻辑正确性 |
| **Readability** 📖 | 20% | 20 | 命名、复杂度、注释、DRY |
| **Architecture** 🏗️ | 25% | 25 | 分层、解耦、模式、扩展性 |
| **Security** 🔒 | 20% | 20 | 输入验证、认证授权、数据安全 |
| **Performance** ⚡ | 15% | 15 | 算法复杂度、资源管理、缓存 |

**综合分级**：

| 分数 | 等级 | 含义 | 行动 |
|------|------|------|------|
| 90-100 | 🟢 Excellent | 可直接合入 | 可作为模式蒸馏入库 |
| 70-89 | 🟡 Good | 小问题需修复 | 修复后合入 |
| 50-69 | 🟠 Fair | 需要较大改进 | 必须修复 Critical 后重审 |
| 0-49 | 🔴 Poor | 不合格，需要重写 | 驳回重做 |

## 🔬 蒸馏进化机制（核心创新）

### 什么是蒸馏？

从历史审查结果和优质代码中自动提取最佳实践，反馈到检查清单和模式库，使 Skill 持续进化。

### 蒸馏触发条件

1. **高分代码** — 评分 ≥ 90 的代码自动进入模式候选
2. **用户主动触发** — "用蒸馏模式分析这个代码库"
3. **定时蒸馏** — 定期扫描历史审查记录，提取新模式

### 蒸馏流程

```
优质代码样本
    │
    ▼
┌──────────────────────────────────────┐
│ Step 1: 模式识别                      │
│ - 识别设计模式                        │
│ - 提取命名约定                        │
│ - 发现安全最佳实践                    │
│ - 定位性能优化技巧                    │
└──────────────────────────────────────┘
    │
    ▼
┌──────────────────────────────────────┐
│ Step 2: 反模式识别                    │
│ - 识别硬编码                          │
│ - 发现上帝类/面条代码                 │
│ - 定位安全漏洞模式                    │
│ - 检测性能反模式                      │
└──────────────────────────────────────┘
    │
    ▼
┌──────────────────────────────────────┐
│ Step 3: 模式入库                       │
│ - 追加到 references/patterns/        │
│ - 标注语言适用性                      │
│ - 添加代码示例                        │
└──────────────────────────────────────┘
    │
    ▼
┌──────────────────────────────────────┐
│ Step 4: 检查清单迭代                  │
│ - 新增检查项                          │
│ - 调整权重                            │
│ - 版本化记录变更                      │
└──────────────────────────────────────┘
```

### 蒸馏产物

| 文件 | 说明 |
|------|------|
| `references/patterns/DESIGN_PATTERNS.md` | 设计模式库（按语言分类） |
| `references/patterns/NAME_CONVENTIONS.md` | 命名规范库 |
| `references/patterns/ERROR_HANDLING.md` | 错误处理模式库 |
| `references/anti-patterns/HARDCODE.md` | 硬编码反模式 |
| `references/anti-patterns/GOD_CLASS.md` | 上帝类反模式 |
| `references/anti-patterns/SPAGHETTI.md` | 面条代码反模式 |
| `distillation/patterns.json` | 结构化模式索引 |
| `distillation/history.jsonl` | 蒸馏历史记录 |

## 🌐 多语言支持

本 Skill 语言无关，但针对以下语言提供专项检查清单：

| 语言 | 文件 | 关键差异 |
|------|------|---------|
| Python | `references/languages/architecture-python.md` | 动态类型、GIL、装饰器模式 |
| TypeScript/JS | `references/languages/architecture-ts.md` | 类型系统、ESM/CJS、框架约束 |
| Go | `references/languages/architecture-go.md` | 并发模型、error handling、接口设计 |
| Java | `references/languages/architecture-java.md` | Spring生态、泛型、ORM |
| Rust | `references/languages/architecture-rust.md` | 所有权、零成本抽象、模式匹配 |
| 通用 | `references/languages/architecture-universal.md` | 所有语言通用的架构原则 |

## 📐 代码变更规模控制

| 变更大小 | 建议 | 处理方式 |
|---------|------|---------|
| ≤100 行 | 理想大小 | 一次 Review |
| 100-300 行 | 可接受（单一逻辑变更） | 一次 Review |
| 300-1000 行 | 偏大 | 建议拆分 |
| >1000 行 | 过大 | 必须拆分 |

**拆分策略**：

| 策略 | 适用场景 |
|------|---------|
| Stack | 有顺序依赖的变更 |
| Horizontal | 需要先建共享层 |
| Vertical | 按功能模块拆分 |
| By file group | 跨领域关注点 |

## 🔗 与其他 Skill 的集成

本 Skill 可与以下 Skill 协同工作：

| 集成 Skill | 协作方式 |
|-----------|---------|
| `biz-delivery` | TD 阶段 Architect 审查技术方案，实现阶段四角色联合审查 |
| `ryan-expert-skills` | 利用架构专家知识增强审查深度 |
| `dv360-expert` / `google-ads-api-expert` | 对 API 集成代码进行安全和性能审查 |
| 自建项目 Skill | 根据项目特点定制检查清单权重 |

## 📂 目录结构

```
code-quality-guard/
├── SKILL.md                          # 本文件（主入口）
├── references/
│   ├── patterns/                     # 模式库（蒸馏产出）
│   │   ├── DESIGN_PATTERNS.md
│   │   ├── NAME_CONVENTIONS.md
│   │   └── ERROR_HANDLING.md
│   ├── anti-patterns/                # 反模式库
│   │   ├── HARDCODE.md
│   │   ├── GOD_CLASS.md
│   │   └── SPAGHETTI.md
│   ├── languages/                    # 语言专项检查清单
│   │   ├── architecture-universal.md
│   │   ├── architecture-python.md
│   │   ├── architecture-ts.md
│   │   ├── architecture-go.md
│   │   ├── architecture-java.md
│   │   ├── architecture-rust.md
│   │   ├── security-universal.md
│   │   ├── performance-universal.md
│   │   └── engineering-universal.md
│   └── schemas/                      # JSON Schema 定义
│       └── review-result.schema.json
├── scripts/
│   ├── distill.py                    # 蒸馏引擎
│   ├── score.py                      # 五轴评分引擎
│   ├── report.py                     # 报告生成器
│   ├── threat_model.py               # STRIDE 威胁建模
│   └── diff_analyzer.py              # 变更影响面分析
├── templates/
│   ├── review-report.md              # 审查报告模板
│   └── distillation-log.md           # 蒸馏日志模板
└── hooks/
    └── pre-commit.sh                 # Git hooks 示例
```

## 🚢 部署与发布

```bash
# 克隆仓库
git clone https://github.com/Ryan-myp/coding.git
cd coding/code-quality-guard

# 安装到 pi
ln -s $(pwd) ~/.agents/skills/code-quality-guard

# 验证安装
ls ~/.agents/skills/ | grep code-quality-guard
```

## 🤝 贡献指南

1. 代码符合本 Skill 的检查清单
2. 新增模式/反模式需附多语言代码示例
3. 蒸馏功能需记录来源和提取逻辑
4. 语言专项检查清单需覆盖至少 2 种语言示例
