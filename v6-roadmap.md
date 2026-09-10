# Code Quality Guard v6.0 — 进化路线图

## 吸收的优秀设计

### 1. addyosmani/agent-skills

| 设计模式 | 应用位置 | 说明 |
|---------|---------|------|
| Skill Anatomy | SKILL.md | 标准结构：Overview → When to Use → Process → Rationalizations → Red Flags → Verification |
| Commands (TOML) | commands/*.toml | 结构化命令定义，可复用 prompt |
| Personas | personas/*.md | 角色分离：code-reviewer, security-auditor, test-engineer |
| Constraints | policies/constraints.md | 质量契约，可机械执行 |
| Six-Axis Review | qguard.py | 在原有五轴基础上增加 Accessibility |
| Common Rationalizations | SKILL.md | 识别 agent 常见的合理化借口 |
| Red Flags | SKILL.md | 可观察的违规行为模式 |

### 2. alirezarezvani/claude-skills

| 设计模式 | 应用位置 | 说明 |
|---------|---------|------|
| AST Analysis | ast_analyzer.py | 真实解析代码结构，非正则匹配 |
| STRIDE Threat Model | threat_modeler.py | 六维威胁建模 |
| Pattern Distillation | distiller.py | 从高质量代码提取模式 |

### 3. OpenCode Integration

| 设计模式 | 应用位置 | 说明 |
|---------|---------|------|
| Intent → Skill Mapping | intent_detector.py | 6 种意图自动识别 |
| Lifecycle Commands | commands/*.toml | /review, /security, /gate |

## v6 核心改进

### 1. 六维评分系统
```
Correctness (20%) + Readability (15%) + Architecture (20%) 
+ Security (20%) + Performance (10%) + Testing (10%) + Accessibility (5%)
```

### 2. 智能意图检测
- 支持 6 种意图：code-writing, code-review, security-audit, debugging, refactoring, testing
- 中英双语识别
- 置信度评分

### 3. 角色分离 (Personas)
- Code Reviewer: 综合质量审查
- Security Auditor: 安全威胁建模
- Test Engineer: 测试覆盖分析

### 4. 结构化命令 (Commands)
- `/review`: 六轴代码审查
- `/security`: STRIDE 威胁建模
- `/gate`: 质量门禁检查

### 5. 约束驱动 (Constraints)
- 明确的质量阈值
- 可机械执行的检查
- 变更历史记录

### 6. 常见借口识别
| 借口 | 现实 |
|------|------|
| "I'll add tests later" | 事后写的测试不完整 |
| "This is simple enough to skip review" | 简单代码常有微妙边界情况 |
| "The security check will catch it" | 自动化检查抓不住架构问题 |
| "It works on my machine" | 本地运行 ≠ 生产可用 |

## 架构设计

```
code-quality-guard/
├── SKILL.md                    # 主技能文档 (v6 结构)
├── scripts/
│   ├── qguard.py              # 统一 CLI (六轴 + 意图检测)
│   ├── intent_detector.py     # 意图检测器
│   ├── ast_analyzer.py        # AST 分析器
│   ├── score_engine.py        # 评分引擎
│   ├── threat_modeler.py      # 威胁建模
│   ├── distiller.py           # 模式蒸馏
│   └── metrics_dashboard.py   # 指标仪表板
├── commands/                   # 结构化命令 (TOML)
│   ├── review.toml
│   ├── security.toml
│   └── gate.toml
├── personas/                   # 角色定义 (Markdown)
│   ├── code-reviewer.md
│   ├── security-auditor.md
│   └── test-engineer.md
├── policies/
│   ├── gate.json              # 门禁配置
│   └── constraints.md         # 质量约束
├── playbooks/                  # 操作手册
│   ├── tdd.sh
│   ├── review.sh
│   └── threat-model.sh
└── distillation/              # 蒸馏结果
    ├── patterns.json
    └── history.jsonl
```

## 使用流程

### 1. 意图检测
```bash
python3 qguard.py intent "实现用户认证API"
# Output: Primary Intent: code-writing (confidence: 0.85)
```

### 2. 代码审查
```bash
python3 qguard.py review src/
# Output: Six-axis scores with findings
```

### 3. 安全审计
```bash
python3 qguard.py threats src/ --json
# Output: STRIDE threat model
```

### 4. 质量门禁
```bash
python3 qguard.py gate . --min-score 70
# Output: Pass/Fail with violations
```

## 与 v5 的对比

| 特性 | v5 | v6 |
|------|-----|-----|
| 评分维度 | 5 轴 | 6 轴 + Accessibility |
| 意图检测 | 基础关键词 | 置信度 + 多意图 |
| 角色分离 | 无 | 3 个 Persona |
| 命令定义 | Shell 脚本 | TOML 结构化 |
| 约束管理 | 无 | constraints.md |
| 常见借口 | 无 | Rationalizations 表 |
| 吸收来源 | 基础设计 | addyosmani + alirezarezvani |

## 未来方向

- [ ] 支持更多语言 AST 解析 (TypeScript, Go, Java, Rust)
- [ ] 集成 CI/CD 平台 (Jenkins, GitLab CI, Azure DevOps)
- [ ] Web 仪表板可视化
- [ ] 团队协作功能 (多人审查)
- [ ] 机器学习辅助评分
