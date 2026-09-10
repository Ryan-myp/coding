---
name: code-quality-guard
description: "AI 代码质量守护专家 — 集成架构师/工程师/安全专家视角，为 Codex/Cursor/Claude 等 Agent 提供代码质量门禁、架构审查、安全扫描与持续蒸馏进化能力"
version: 1.0.0
author: ryan
created: 2025-09-10
platforms: [linux, macos, windows]
tags: [code-quality, architecture, security, review, maintainability, distillation, agent]
---

# Code Quality Guard v1.0 — AI 代码质量守护专家

> 让所有 AI 编码 Agent（Codex / Cursor / Claude / GitHub Copilot）写出统一高质量代码

## 🎯 核心目标

解决 AI Agent 写代码"功能可用但维护困难"的问题：
- 架构设计随意，缺乏分层与解耦
- 硬编码泛滥，配置与逻辑混杂
- 可读性差，命名混乱，注释缺失
- 安全性漏洞，注入、权限、数据泄露
- 可测试性低，难以覆盖边界场景
- 扩展性差，每次改动都是大改

## 📐 角色体系

本 Skill 整合三个专业角色，每个角色有独立的检查清单：

| 角色 | 职责 | 关注维度 |
|------|------|---------|
| **Architect** | 架构设计审查 | 分层、解耦、模式、扩展点 |
| **Engineer** | 代码工程化审查 | 可读性、可维护性、可测试性 |
| **Security** | 安全合规审查 | 注入、权限、数据安全、依赖安全 |

使用方式：当 Agent 完成代码编写后，自动触发三角色联合审查。

## 🔄 工作流

```
Agent 写代码
    │
    ▼
┌──────────────────────────────┐
│  Phase 1: 编码前架构指引       │  ← Architect 前置建议
│  - 推荐设计模式               │
│  - 分层建议                   │
│  - 扩展点标记                 │
└──────────────────────────────┘
    │
    ▼
┌──────────────────────────────┐
│  Phase 2: 编码中实时规范       │  ← Engineer 实时提醒
│  - 命名规范                   │
│  - 函数职责单一               │
│  - 避免硬编码                 │
└──────────────────────────────┘
    │
    ▼
┌──────────────────────────────┐
│  Phase 3: 完成后全面审查       │  ← 三角色联合审查
│  - Architect: 架构合理性      │
│  - Engineer: 代码质量         │
│  - Security: 安全漏洞         │
└──────────────────────────────┘
    │
    ▼
┌──────────────────────────────┐
│  Phase 4: 蒸馏进化             │  ← 从优质代码中学习
│  - 提取优秀模式到 reference   │
│  - 积累 Bad Smell 案例库      │
│  - 持续迭代检查清单           │
└──────────────────────────────┘
```

## 🚀 快速使用

### 方式一：直接加载审查

```
请按照 code-quality-guard 的标准审查以下代码：
[粘贴代码或指定文件路径]
```

### 方式二：编码前架构指引

```
在写 [某个功能] 之前，请先按照 code-quality-guard 的架构师角色给出设计建议
```

### 方式三：完整流水线

```
使用 code-quality-guard 全流程处理：
1. 分析 PRD/需求
2. 给出架构设计建议
3. 生成代码时遵循工程规范
4. 完成后三角色联合审查
5. 蒸馏学到的模式
```

## 📋 审查维度详解

### Architect 角色检查清单

<details>
<summary>架构分层</summary>

- [ ] 是否存在清晰的分层（Controller → Service → Repository/DAO）
- [ ] 各层之间是否单向依赖
- [ ] 是否避免跨层调用
- [ ] 是否有明确的边界上下文（Bounded Context）
- [ ] 是否使用了合适的抽象层次
</details>

<details>
<summary>设计模式</summary>

- [ ] 是否使用了合适的设计模式（Strategy/Factory/Observer/Repository 等）
- [ ] 是否避免了上帝类（God Class）
- [ ] 是否符合单一职责原则（SRP）
- [ ] 是否符合依赖倒置原则（DIP）
- [ ] 扩展点是否通过接口/抽象暴露
</details>

<details>
<summary>解耦与内聚</summary>

- [ ] 模块内高内聚，模块间低耦合
- [ ] 是否存在循环依赖
- [ ] 是否使用了依赖注入
- [ ] 硬编码的业务逻辑是否提取为配置
</details>

### Engineer 角色检查清单

<details>
<summary>可读性</summary>

- [ ] 变量/函数命名是否语义清晰
- [ ] 函数长度是否合理（建议 < 50 行）
- [ ] 是否有必要的注释说明"为什么"而非"是什么"
- [ ] 是否存在魔法数字/字符串
- [ ] 代码格式化是否一致
</details>

<details>
<summary>可维护性</summary>

- [ ] 错误处理是否完善
- [ ] 日志是否合理（不泄露敏感信息）
- [ ] 配置是否参数化/外部化
- [ ] 是否存在重复代码（DRY 原则）
- [ ] 是否遵循了已有的代码风格
</details>

<details>
<summary>可测试性</summary>

- [ ] 函数是否有明确的输入输出
- [ ] 是否避免了全局状态
- [ ] 依赖是否可 Mock
- [ ] 边界条件是否覆盖
- [ ] 是否存在难以测试的耦合
</details>

### Security 角色检查清单

<details>
<summary>输入验证</summary>

- [ ] 所有外部输入是否经过验证/ sanitization
- [ ] SQL 注入防护（参数化查询）
- [ ] XSS 防护
- [ ] 命令注入防护
</details>

<details>
<summary>权限与安全</summary>

- [ ] 是否做了鉴权检查
- [ ] 敏感数据是否加密存储/传输
- [ ] 是否有权限校验（RBAC/ABAC）
- [ ] API 是否有限流/防重放
</details>

<details>
<summary>数据安全</summary>

- [ ] 日志中是否包含敏感信息
- [ ] 密钥是否硬编码
- [ ] 是否有数据泄露风险
- [ ] 依赖包是否存在已知漏洞
</details>

## 🧪 质量评分

每次审查输出一个综合评分（0-100）：

| 维度 | 权重 | 评分标准 |
|------|------|---------|
| 架构合理性 | 30% | 分层清晰=10, 基本合理=6, 混乱=2 |
| 可读性 | 20% | 命名清晰+注释完善=10, 一般=5, 混乱=2 |
| 可维护性 | 20% | 配置外化+错误处理完善=10, 一般=5, 差=2 |
| 可测试性 | 10% | 无全局状态+依赖可Mock=10, 一般=5, 差=2 |
| 安全性 | 20% | 无漏洞=10, 有低风险=5, 有高危=0 |

**分级标准**：
- 🟢 90-100：优秀，可直接合入
- 🟡 70-89：良好，有小问题需修复
- 🟠 50-69：一般，需要较大改进
- 🔴 0-49：不合格，需要重写

## 🔬 蒸馏进化机制

### 什么是蒸馏？

从已有的优质代码中自动提取最佳实践，反馈到检查清单和模式库，使 Skill 持续进化。

### 蒸馏触发条件

1. **用户主动触发**：`请用蒸馏模式分析这个代码库`
2. **审查通过后**：高分代码自动进入模式库
3. **定时蒸馏**：定期扫描历史审查结果，提取新模式

### 蒸馏流程

```
优质代码样本
    │
    ▼
┌─────────────────┐
│ 模式提取        │  ← LLM 分析代码中的优秀实践
│ - 设计模式      │
│ - 命名规范      │
│ - 错误处理模式  │
│ - 安全模式      │
└─────────────────┘
    │
    ▼
┌─────────────────┐
│ 模式入库        │  ← 追加到 references/patterns/
│ - 更新 patterns │
│ - 更新 bad-smells│
│ - 版本化记录    │
└─────────────────┘
    │
    ▼
┌─────────────────┐
│ 检查清单迭代    │  ← 根据新模式更新审查规则
│ - 新增检查项    │
│ - 调整权重      │
│ - A/B 验证效果  │
└─────────────────┘
```

### 蒸馏输出物

| 文件 | 用途 |
|------|------|
| `references/patterns/DESIGN_PATTERNS.md` | 设计模式库 |
| `references/patterns/NAME_CONVENTIONS.md` | 命名规范库 |
| `references/bad-smells/HARDCODE.md` | 硬编码反模式案例 |
| `references/bad-smells/GOD_CLASS.md` | 上帝类反模式案例 |
| `references/security/CHECKLIST.md` | 安全漏洞模式库 |
| `distillation/log.md` | 蒸馏历史记录 |

## 📂 目录结构

```
code-quality-guard/
├── SKILL.md                          # 本文件
├── references/
│   ├── architect-checklist.md        # 架构师详细检查清单
│   ├── engineer-checklist.md         # 工程师详细检查清单
│   ├── security-checklist.md         # 安全专家详细检查清单
│   ├── patterns/                     # 模式库（蒸馏产出）
│   │   ├── DESIGN_PATTERNS.md
│   │   ├── NAME_CONVENTIONS.md
│   │   └── ANTI_PATTERNS.md
│   └── bad-smells/                   # 反模式案例库（蒸馏产出）
│       ├── HARDCODE.md
│       ├── GOD_CLASS.md
│       └── SPAGHETTI_CODE.md
├── scripts/
│   ├── score.py                      # 质量评分脚本
│   ├── distill.py                    # 蒸馏引擎
│   └── generate_report.py            # 审查报告生成
└── templates/
    ├── review-report.md              # 审查报告模板
    └── distillation-log.md           # 蒸馏日志模板
```

## 📊 审查报告格式

```markdown
# 代码质量审查报告

## 基本信息
- 审查时间：2025-09-10 14:30:00
- 审查文件：src/service/payment.py
- 审查者：Code Quality Guard (Architect + Engineer + Security)

## 综合评分：🟢 85/100

| 角色 | 分数 | 问题数 | 警告数 |
|------|------|--------|--------|
| Architect | 28/30 | 0 | 1 |
| Engineer | 16/20 | 1 | 2 |
| Security | 18/20 | 0 | 1 |

## 发现的问题

### 🔴 严重（必须修复）
1. [Architect] 第 45 行：硬编码的支付网关 URL
   ```
   GATEWAY_URL = "https://pay.example.com/api"
   ```
   **建议**：移至配置文件 `settings.yaml`

### 🟡 警告（建议修复）
2. [Engineer] 第 12 行：函数 `process_payment` 超过 50 行
   **建议**：拆分为 `validate_input` + `call_gateway` + `handle_response`

3. [Security] 第 78 行：日志中打印了 card_number
   **建议**：使用 `****1234` 脱敏

## 亮点
- ✅ 良好的异常处理结构
- ✅ 使用了 Strategy 模式处理不同支付方式

## 蒸馏建议
此代码可作为以下模式的示例入库：
- 支付网关调用模式
- 敏感数据脱敏模式
```

## 🔗 与其他 Skill 的集成

本 Skill 可与以下 Skill 协同工作：

| 集成 Skill | 协作方式 |
|-----------|---------|
| `biz-delivery` | TD 阶段由 Architect 审查技术方案，实现阶段由 Engineer 审查代码 |
| `ryan-expert-skills` | 利用已有架构知识增强审查深度 |
| 各平台 API Skills | 对生成的 API 代码进行安全审查 |

## 🚢 部署与发布

```bash
# 克隆仓库
git clone https://github.com/Ryan-myp/coding.git
cd coding/code-quality-guard

# 安装到 pi
ln -s $(pwd) ~/.agents/skills/code-quality-guard

# 验证
pi --list-skills | grep code-quality-guard
```

## 📝 贡献指南

欢迎提交 PR！审查标准：
1. 代码符合本 Skill 的检查清单
2. 新增模式/反模式需附实际代码示例
3. 蒸馏功能需记录来源和提取逻辑
4. 测试用例覆盖率 ≥ 80%
