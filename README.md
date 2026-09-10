# Code Quality Guard v5.0 — 多语言 AI 代码质量守护系统

一个跨平台的代码质量守护工具，支持意图识别、五轴评分、STRIDE 威胁建模和设计模式蒸馏。

## 🚀 快速开始

### 在 Pi 中使用

```
/quality-check          # 运行质量门禁
/quality-review src/    # 五轴评分审查
/threat-model           # STRIDE 威胁建模
/learn-patterns         # 从项目学习最佳实践
/intent-detect "你的prompt"  # 测试意图检测
```

### 在终端使用

```bash
# 智能触发
bash scripts/qguard-auto.sh trigger "实现用户认证API"

# 意图检测
python3 scripts/intent_detector.py "实现用户认证API" --verbose

# 五轴评分
python3 scripts/qguard.py review src/

# 威胁建模
python3 scripts/qguard.py threats src/ --json

# 质量门禁
python3 scripts/qguard.py gate . --min-score 70

# 模式蒸馏
python3 scripts/qguard.py distill . --output patterns.json
```

## 🎯 核心特性

### 1. 智能意图识别
- 支持中英双语
- 检测 6 种意图：代码编写、代码审查、安全审查、调试修复、重构优化、测试
- 自动注入对应的质量规则

### 2. 五轴评分系统
| 维度 | 权重 | 关注点 | 最低分 |
|------|------|--------|--------|
| Correctness | 20% | 错误处理、边界条件 | 15/20 |
| Readability | 20% | 命名、函数长度 | 15/20 |
| Architecture | 25% | 分层、耦合、上帝类 | 18/25 |
| Security | 20% | 密钥、注入、认证 | 15/20 |
| Performance | 15% | N+1查询、超时 | 10/15 |

### 3. 实时质量守护
- 代码写入时弹出提醒
- Git commit 前自动运行门禁
- PR/Merge 时自动检查

### 4. 多 Agent 支持
- Pi (当前环境)
- Claude Code
- OpenAI Codex
- Cursor
- GitHub Copilot

### 5. 学习进化
- 从高质量代码中学习设计模式
- 记录蒸馏历史
- 持续优化规则

## 📦 安装

### 一键安装所有 Agent
```bash
bash scripts/install_all_agents.sh
```

### 手动安装
```bash
# Pi
cp ~/.agents/skills/code-quality-guard/scripts/qguard-auto.sh ~/.local/bin/

# Claude Code
mkdir -p ~/.claude/skills/code-quality-guard
cp ~/.agents/skills/code-quality-guard/SKILL.md ~/.claude/skills/code-quality-guard/

# Codex
mkdir -p ~/.codex/skills/code-quality-guard
cp ~/.agents/skills/code-quality-guard/SKILL.md ~/.codex/skills/code-quality-guard/

# Cursor
mkdir -p ~/.cursor/rules
cp ~/.agents/skills/code-quality-guard/references/quality-rules.md ~/.cursor/rules/code-quality-guard.md
```

## 📊 文件结构

```
code-quality-guard/
├── README.md                    # 本文件
├── v5-improvements.md           # v5 改进说明
├── AUTO_TRIGGER_GUIDE.md        # 自动触发指南
├── SKILL.md                     # 主技能文档
├── scripts/
│   ├── qguard.py                # 统一 CLI
│   ├── qguard-auto.sh           # 智能触发脚本
│   ├── intent_detector.py       # 意图检测器
│   ├── install_all_agents.sh    # 一键安装脚本
│   ├── ast_analyzer.py          # AST 分析器
│   ├── score_engine.py          # 五轴评分引擎
│   ├── threat_modeler.py        # STRIDE 威胁建模
│   ├── distiller.py             # 模式蒸馏器
│   ├── metrics_dashboard.py     # 质量趋势仪表板
│   └── badge_generator.py       # 徽章生成器
├── playbooks/                   # 操作手册
│   ├── tdd.sh                   # TDD 工作流
│   ├── review.sh                # 代码审查流程
│   ├── threat-model.sh          # 威胁建模
│   └── migrate.sh               # 迁移安全
├── ci/
│   └── quality-check.yml        # GitHub Actions
├── policies/
│   └── gate.json                # 门禁配置
├── integrations/
└── distillation/                # 蒸馏结果
    ├── patterns.json
    └── history.jsonl
```

## 🔧 配置

### 质量门禁阈值
编辑 `policies/gate.json`:
```json
{
  "quality_gate": {
    "min_composite_score": 70,
    "min_axis_scores": {
      "security": 15,
      "architecture": 18
    },
    "critical_findings": ["hardcoded_secret", "sql_injection", "eval_usage"]
  }
}
```

### 自定义规则
编辑 `scripts/intent_detector.py` 中的 `INTENT_KEYWORDS` 添加自定义意图。

## 📈 版本历史

| 版本 | 日期 | 改进 |
|------|------|------|
| v5.0 | 2025 | 意图识别、多 Agent 支持、一键安装 |
| v4.0 | 2025 | AST 分析、五轴评分、STRIDE |
| v3.0 | 2025 | 13 个操作手册、威胁建模 |
| v2.0 | 2025 | 多语言支持、4 角色框架 |
| v1.0 | 2025 | Python-only 初始版本 |

## 🔗 相关链接

- **GitHub**: https://github.com/Ryan-myp/coding
- **本地路径**: `~/.agents/skills/code-quality-guard/`
- **文档**: `v5-improvements.md`

## 🤝 贡献

欢迎提交 Issue 和 Pull Request！

## 📄 许可证

MIT License
