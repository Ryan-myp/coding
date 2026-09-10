# Code Quality Guard

> AI 代码质量守护专家 — 让 Codex / Cursor / Claude 等 Agent 写出统一高质量代码

## 🎯 解决什么问题

AI Agent 写代码常见的质量问题：
- **架构随意** — 缺乏分层，模块耦合严重
- **硬编码泛滥** — 配置与逻辑混杂，变更困难
- **可读性差** — 命名混乱，注释缺失
- **安全隐患** — SQL 注入、密钥硬编码、权限缺失
- **难以维护** — 上帝类、 spaghetti 代码
- **不可测试** — 全局状态、强耦合

## 🚀 快速开始

### 安装

```bash
# 克隆到 skills 目录
ln -s $(pwd)/code-quality-guard ~/.agents/skills/code-quality-guard
```

### 使用方式

**审查已有代码：**
```
请按照 code-quality-guard 的标准审查以下代码：
[粘贴代码或指定文件路径]
```

**编码前架构指引：**
```
在写 [某个功能] 之前，请先按照 code-quality-guard 的架构师角色给出设计建议
```

**完整流水线：**
```
使用 code-quality-guard 全流程：
1. 分析需求 → 2. 架构设计建议 → 3. 编码规范 → 4. 三角色联合审查 → 5. 蒸馏进化
```

## 📐 角色体系

| 角色 | 职责 | 关注维度 |
|------|------|---------|
| 🏛️ **Architect** | 架构设计审查 | 分层、解耦、模式、扩展点 |
| 👷 **Engineer** | 代码工程化审查 | 可读性、可维护性、可测试性 |
| 🔒 **Security** | 安全合规审查 | 注入、权限、数据安全、依赖安全 |

## 🔬 蒸馏进化机制

从优质代码中自动提取最佳实践，持续进化检查清单：

```bash
# 蒸馏单个文件
python3 scripts/distill.py path/to/file.py

# 蒸馏整个目录
python3 scripts/distill.py path/to/project --max-files 50
```

蒸馏产出：
- `references/patterns/` — 设计模式库
- `references/bad-smells/` — 反模式案例库
- `distillation/log.jsonl` — 蒸馏历史记录

## 📊 质量评分

每次审查输出 0-100 分：

| 分数 | 等级 | 含义 |
|------|------|------|
| 90-100 | 🟢 优秀 | 可直接合入 |
| 70-89 | 🟡 良好 | 有小问题需修复 |
| 50-69 | 🟠 一般 | 需要较大改进 |
| 0-49 | 🔴 不合格 | 需要重写 |

## 📂 目录结构

```
code-quality-guard/
├── SKILL.md                          # 主技能文件
├── references/
│   ├── architect-checklist.md        # 架构师检查清单
│   ├── engineer-checklist.md         # 工程师检查清单
│   ├── security-checklist.md         # 安全专家检查清单
│   ├── patterns/                     # 模式库（蒸馏产出）
│   │   ├── DESIGN_PATTERNS.md
│   │   └── NAME_CONVENTIONS.md
│   └── bad-smells/                   # 反模式案例库
│       └── ANTI_PATTERNS.md
├── scripts/
│   ├── score.py                      # 质量评分引擎
│   ├── distill.py                    # 蒸馏引擎
│   └── generate_report.py            # 报告生成器
└── templates/                        # 报告模板
```

## 🔗 与其他工具集成

```json
// .pi/settings.json — 让其他 Agent harness 也能使用
{
  "skills": [
    "~/.agents/skills/code-quality-guard"
  ]
}
```

## 🤝 贡献指南

1. Fork 本仓库
2. 新增模式/反模式时附实际代码示例
3. 蒸馏功能需记录来源
4. PR 需通过质量门禁（≥70分）

## 📝 License

MIT
