# Code Quality Guard v2

> 多语言通用的 AI 代码质量守护专家 — 让 Codex / Cursor / Claude / Gemini 等所有 Agent 写出统一高质量代码

⭐ 基于 [addyosmani/agent-skills](https://github.com/addyosmani/agent-skills) 和 [alirezarezvani/claude-skills](https://github.com/alirezarezvani/claude-skills) 的最佳实践构建

## 🎯 解决什么问题

| 问题 | 现状 | 本 Skill 提供 |
|------|------|--------------|
| 架构随意 | 无统一标准，各写各的 | 四角色联合架构审查 |
| 硬编码泛滥 | 配置与逻辑混杂 | 自动检测 + 修复建议 |
| 安全隐患 | SQL注入、密钥泄漏 | STRIDE威胁建模+OWASP检查 |
| 质量参差 | 不同Agent输出质量不同 | 五轴评分+质量门禁 |
| 无法进化 | 规则写死，过时不变 | 蒸馏机制持续学习 |

## 🏛️ 四角色联合审查

| 角色 | 关注维度 | 权重 |
|------|---------|------|
| **Architect** 🏗️ | 分层、解耦、设计模式、扩展性 | 25% |
| **Engineer** 👷 | 可读性、命名、DRY、可测试性 | 20% |
| **Security** 🔒 | STRIDE威胁建模、OWASP Top10 | 20% |
| **Performer** ⚡ | 算法复杂度、N+1查询、内存管理 | 15% |
| **+ Correctness** ✅ | 边界条件、错误处理、逻辑正确性 | 20% |

## 📊 五轴质量评分

```
┌────────────────────────────────────────┐
│  Correctness     20%  │ 边界条件、错误处理  │
│  Readability     20%  │ 命名、复杂度、DRY   │
│  Architecture    25%  │ 分层、解耦、模式    │
│  Security        20%  │ 注入、认证、数据    │
│  Performance     15%  │ 算法、缓存、内存    │
└────────────────────────────────────────┘
         ↓
    综合评分 0-100
    🟢 90+ Excellent  🟡 70-89 Good
    🟠 50-69 Fair     🔴 <50 Poor
```

## 🚀 快速使用

### 安装

```bash
# 克隆并链接
git clone https://github.com/Ryan-myp/coding.git
ln -s $(pwd)/code-quality-guard ~/.agents/skills/code-quality-guard
```

### 审查代码

```
按照 code-quality-guard 标准审查以下代码：
[代码或文件路径]

要求：
1. 四角色联合审查（Architect + Engineer + Security + Performer）
2. 五轴评分（Correctness/Readability/Architecture/Security/Performance）
3. 按严重程度分级：Critical / Required / Optional / Nit
4. 给出具体修复建议和代码示例
5. 输出质量门禁判定
```

### 安全审计

```
按 code-quality-guard 的 Security 角色进行 STRIDE 威胁建模：
[代码或功能描述]
```

### TDD 指导

```
按 code-quality-guard 的 TDD 流程实现 [功能]：
1. RED — 先写失败测试
2. GREEN — 最小实现让测试通过
3. REFACTOR — 在测试保护下重构
```

### 蒸馏进化

```
用 code-quality-guard 的蒸馏模式分析这个代码库：
[仓库路径]

提取最佳实践和反模式，更新 references/patterns/ 和 references/anti-patterns/
```

## 🔬 蒸馏进化机制

从历史代码中自动提取模式，持续进化检查清单：

```
优质代码 (≥90分)
    │
    ├─→ 设计模式 → patterns/DESIGN_PATTERNS.md
    ├─→ 命名规范 → patterns/NAME_CONVENTIONS.md
    └─→ 错误处理 → patterns/ERROR_HANDLING.md

问题代码
    │
    ├─→ 硬编码案例 → anti-patterns/HARDCODE.md
    ├─→ 上帝类案例 → anti-patterns/GOD_CLASS.md
    └─→ 面条代码 → anti-patterns/SPAGHETTI.md

检查清单迭代更新 ← distillation/history.jsonl
```

```bash
# 蒸馏单个文件
python3 scripts/distill.py path/to/file.py

# 蒸馏整个项目
python3 scripts/distill.py path/to/project --max-files 100

# 查看蒸馏历史
cat distillation/history.jsonl | tail -20
```

## 🌐 多语言支持

| 语言 | 专项检查 | 支持程度 |
|------|---------|---------|
| Python | 类型注解、GIL、装饰器、包结构 | ✅ 完整 |
| TypeScript | 泛型约束、ESM模块、React模式 | ✅ 完整 |
| Go | 接口设计、Context传递、并发模式 | ✅ 完整 |
| Java | Spring分层、依赖注入、事务管理 | ✅ 完整 |
| Rust | 所有权、Error类型、零成本抽象 | ✅ 完整 |
| 通用 | SOLID、分层、安全、性能 | ✅ 通用 |

## 📂 目录结构

```
code-quality-guard/
├── SKILL.md                          # 主入口
├── references/
│   ├── patterns/                     # 模式库
│   │   ├── DESIGN_PATTERNS.md        # 设计模式（多语言示例）
│   │   ├── NAME_CONVENTIONS.md       # 命名规范（跨语言）
│   │   └── ERROR_HANDLING.md         # 错误处理模式
│   ├── anti-patterns/                # 反模式库
│   │   ├── HARDCODE.md               # 硬编码反模式
│   │   ├── GOD_CLASS.md              # 上帝类反模式
│   │   └── SPAGHETTI.md              # 面条代码反模式
│   ├── languages/                    # 语言专项检查清单
│   │   ├── architecture-universal.md # 通用架构
│   │   ├── architecture-python.md
│   │   ├── architecture-ts.md
│   │   ├── architecture-go.md
│   │   ├── architecture-java.md
│   │   ├── architecture-rust.md
│   │   ├── security-universal.md     # 通用安全（STRIDE+OWASP）
│   │   ├── performance-universal.md  # 通用性能
│   │   └── engineering-universal.md  # 通用工程化
│   └── schemas/
│       └── review-result.schema.json # JSON Schema
├── scripts/
│   ├── distill.py                    # 蒸馏引擎（多语言）
│   ├── score.py                      # 五轴评分引擎
│   ├── report.py                     # 报告生成器
│   └── threat_model.py               # STRIDE威胁建模
├── templates/
├── hooks/
│   └── pre-commit.sh                 # Git预提交钩子
└── distillation/                     # 蒸馏产出目录
    ├── patterns.json
    └── history.jsonl
```

## 🔗 与其他工具集成

```bash
# Cursor
# 将 skills 放到 .cursor/skills/ 目录

# Claude Code
/plugin install code-quality-guard@ryan-myp-coding

# Codex
codex plugin marketplace add Ryan-myp/coding

# GitHub Copilot
# 在 .github/copilot-instructions.md 中引用

# OpenCode
cp -r code-quality-guard/.opencode/skills/
```

## 🤝 贡献指南

1. 代码符合本 Skill 的检查清单
2. 新增模式需附多语言代码示例
3. 蒸馏功能需记录来源和提取逻辑
4. 更新蒸馏历史 `distillation/history.jsonl`

## 📝 License

MIT
