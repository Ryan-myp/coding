# Code Quality Guard — Auto-Trigger Guide

## 各 Agent 自动触发机制

### 1. Pi (当前环境) ✅ 已配置

**安装位置**: `~/.pi/agent/extensions/code-quality-guard.ts`

**触发方式**:
- **自动注入**: 当用户 prompt 包含 `code/implement/write/function/class/api/review/check` 时，自动注入质量规则到系统提示
- **文件写入提醒**: 写入 `.py/.ts/.go/.java` 等代码文件时，自动弹出质量提醒
- **Git commit 拦截**: commit 前自动运行质量门禁
- **自定义命令**:
  - `/quality-check` — 运行质量门禁
  - `/quality-review` — 五轴评分审查
  - `/threat-model` — STRIDE 威胁建模

**验证**:
```bash
# 在 pi 中直接输入
/quality-check
/quality-review src/
```

---

### 2. Claude Code ✅ 已配置

**安装位置**: `~/.claude/skills/code-quality-guard/`

**触发方式**:
- Claude Code 会自动扫描 `~/.claude/skills/` 目录
- 当任务匹配 skill 描述时自动加载
- 可通过 `/skill:code-quality-guard` 手动调用

**验证**:
```bash
# 在 Claude Code 中
/skill:code-quality-guard review src/
```

---

### 3. OpenAI Codex ✅ 已配置

**安装位置**: `~/.codex/skills/code-quality-guard/` + `AGENTS.md`

**触发方式**:
- Codex 自动扫描 `~/.codex/skills/` 目录
- `AGENTS.md` 在项目根目录时自动加载为上下文
- 当写入代码文件时，Agent 会参考质量规则

**验证**:
```bash
# 在 Codex 中
python3 ~/.codex/skills/code-quality-guard/scripts/qguard.py review src/
```

---

### 4. Cursor ✅ 已配置

**安装位置**: `~/.cursor/rules/code-quality-guard.md` + `.cursorrules`

**触发方式**:
- Cursor 自动加载 `~/.cursor/rules/*.md` 作为全局规则
- 项目级 `.cursorrules` 自动加载
- 编写代码时自动遵循规则

**验证**:
- 在 Cursor 编辑器中编写代码，规则会自动生效
- 可查看 `~/.cursor/rules/code-quality-guard.md` 确认规则

---

### 5. GitHub Copilot ✅ 已配置

**触发方式**:
- 在项目根目录创建 `.github/copilot-instructions.md`
- Copilot 会自动读取并遵循指令

**安装**:
```bash
mkdir -p .github
cat > .github/copilot-instructions.md << 'EOF'
# Code Quality Rules

When generating code:
1. Never hardcode secrets (use env vars)
2. Use parameterized queries (no SQL injection)
3. Handle all errors
4. Keep functions < 50 lines
5. Nesting depth ≤ 3 levels

Run quality gate before commit:
python3 ~/.agents/skills/code-quality-guard/scripts/qguard.py gate . --min-score 70
EOF
```

---

### 6. Gemini CLI ✅ 待配置

**安装位置**: `~/.gemini/skills/code-quality-guard/`（需创建）

**触发方式**:
- Gemini CLI 支持自定义 skills
- 需手动添加到配置

---

## 自动化触发流程图

```
用户输入 "实现支付功能"
        │
        ▼
┌─────────────────────┐
│  Agent 检测关键词    │──── code/implement/write/function/class
└─────────┬───────────┘
          │
          ▼
┌─────────────────────┐
│  自动注入质量规则    │  ← 五轴标准 + 安全规则 + 架构规范
└─────────┬───────────┘
          │
          ▼
┌─────────────────────┐
│  Agent 生成代码      │  ← 遵循质量规则
└─────────┬───────────┘
          │
          ▼
┌─────────────────────┐
│  写入代码文件        │  ← 触发文件写入提醒
└─────────┬───────────┘
          │
          ▼
┌─────────────────────┐
│  Git commit        │  ← 自动运行质量门禁
└─────────┬───────────┘
          │
    ┌─────┴─────┐
    │           │
   Pass        Fail
    │           │
    ▼           ▼
  允许       要求修复
```

---

## 手动触发命令

### Pi
```
/quality-check          # 质量门禁
/quality-review src/    # 五轴评分
/threat-model           # STRIDE 威胁建模
```

### Claude Code
```bash
/skill:code-quality-guard review src/
/skill:code-quality-guard threats src/
/skill:code-quality-guard distill src/
```

### Codex
```bash
python3 ~/.codex/skills/code-quality-guard/scripts/qguard.py review src/
python3 ~/.codex/skills/code-quality-guard/scripts/qguard.py gate . --min-score 70
```

### Cursor
- 规则自动生效，无需手动触发
- 可用快捷键 `Ctrl+Shift+P` → 搜索 "Code Quality"

### GitHub Copilot
- 规则自动生效（通过 `.github/copilot-instructions.md`）

---

## CI/CD 集成

### GitHub Actions
已在 `ci/quality-check.yml` 配置：
- PR 触发五轴评分 + 评论
- 每周凌晨全量扫描
- 合并前门禁检查

### Pre-commit Hook
```bash
# 安装到项目
cp code-quality-guard/hooks/pre-commit.sh .git/hooks/pre-commit
chmod +x .git/hooks/pre-commit
```

---

## 验证安装

```bash
# 1. 检查各 Agent skill 目录
ls ~/.claude/skills/code-quality-guard/
ls ~/.codex/skills/code-quality-guard/
ls ~/.cursor/rules/code-quality-guard.md

# 2. 测试 CLI
python3 ~/.agents/skills/code-quality-guard/scripts/qguard.py --help

# 3. 测试质量门禁
python3 ~/.agents/skills/code-quality-guard/scripts/qguard.py gate . --min-score 70

# 4. 测试威胁建模
python3 ~/.agents/skills/code-quality-guard/scripts/qguard.py threats src/ --json
```

---

## 问题排查

### Q: Agent 没有自动加载 skill？
A: 检查以下路径是否存在：
- Pi: `~/.agents/skills/code-quality-guard/SKILL.md`
- Claude: `~/.claude/skills/code-quality-guard/SKILL.md`
- Codex: `~/.codex/skills/code-quality-guard/SKILL.md`

### Q: 质量门禁总是失败？
A: 检查具体 findings：
```bash
python3 ~/.agents/skills/code-quality-guard/scripts/qguard.py review . --json
```

### Q: 如何调整门禁阈值？
A: 修改 `policies/gate.json`：
```json
{
  "quality_gate": {
    "min_composite_score": 70,
    "min_axis_scores": {
      "security": 15
    }
  }
}
```
