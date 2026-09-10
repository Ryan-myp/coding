# Coding — Ryan's Coding Excellence System

工业级编码质量守护体系，包含以下核心能力：

## 📦 核心组件

### `code-quality-guard/` — AI 代码质量守护专家
基于五轴评分 × 四角色评估的工业级代码审查系统。

**特性：**
- **五轴评分** — Correctness(20%) | Readability(20%) | Architecture(25%) | Security(20%) | Performance(15%)
- **四角色评估** — Architect + Engineer + Security + Performer
- **多语言支持** — Python / TypeScript / Go / Java / Rust
- **蒸馏进化** — 从高质量代码中提取模式，持续优化检查清单
- **12 个 Playbook** — TDD、威胁建模、API 设计、重构、迁移、可观测性等
- **Git 预提交门禁** — 自动拦截硬编码密钥、SQL 注入风险

**快速开始：**
```bash
# 审查代码
python3 scripts/distill.py src/ --max-files 50

# 五轴评分
python3 scripts/score.py src/service/payment.py

# 威胁建模
python3 scripts/threat_model.py src/api/ --output threats.md

# 质量门禁
python3 scripts/gate_checker.py review_results.json
```

## 安装

```bash
# 安装到 pi (agents)
ln -s /path/to/code-quality-guard ~/.agents/skills/code-quality-guard

# 安装到 Claude Code
npx skills add Ryan-myp/coding --skill code-quality-guard
```

## 目录结构

```
code-quality-guard/
├── SKILL.md                      # 主入口
├── playbooks/                    # 12 个操作手册
│   ├── tdd-workflow.md
│   ├── threat-modeling.md
│   ├── api-design.md
│   ├── refactoring.md
│   ├── code-review.md
│   ├── observability.md
│   ├── migration.md
│   ├── legacy-code.md
│   ├── deployment-strategy.md
│   ├── incident-response.md
│   ├── performance-profile.md
│   └── distillation.md
├── references/
│   ├── patterns/                 # 设计模式库
│   ├── anti-patterns/            # 反模式库
│   ├── languages/                # 语言专项检查清单
│   ├── guides/                   # 工业级指南
│   └── schemas/                  # JSON Schema
├── scripts/                      # Python 工具集
│   ├── distill.py                # 蒸馏引擎
│   ├── score.py                  # 五轴评分
│   ├── report.py                 # 报告生成
│   ├── threat_model.py           # STRIDE 威胁建模
│   ├── diff_analyzer.py          # Diff 影响分析
│   └── gate_checker.py           # 质量门禁
├── templates/                    # ADR / RFC 模板
└── hooks/                        # Git 预提交钩子
```

## 质量门禁

| 分数 | 等级 | 门禁结果 |
|------|------|---------|
| 90-100 | Excellent 🟢 | 自动通过 + 蒸馏候选 |
| 70-89 | Good 🟡 | 条件通过 |
| 50-69 | Fair 🟠 | 必须修复 Critical |
| 0-49 | Poor 🔴 | 驳回重写 |

## 技术栈

- Python 3.8+ (无外部依赖)
- 支持 AGENTS.md / SKILL.md 规范的 Agent 平台
- CI/CD 集成（GitHub Actions / GitLab CI）
