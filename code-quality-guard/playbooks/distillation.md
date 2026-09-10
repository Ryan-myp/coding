# 蒸馏进化 Playbook

## 触发条件

- 审查评分 ≥ 90 的代码
- 用户主动请求："用蒸馏模式分析"
- 定期扫描（如每周）
- 新项目接入时初始化模式库

## 蒸馏流程

### Step 1: 扫描代码

```bash
# 扫描单个文件
python3 scripts/distill.py src/service/payment.py

# 扫描整个项目
python3 scripts/distill.py src/ --max-files 100

# 指定语言
python3 scripts/distill.py src/ --languages python typescript go
```

### Step 2: 模式识别

蒸馏引擎自动识别：

| 模式类型 | 识别规则 | 入库位置 |
|---------|---------|---------|
| Repository 模式 | `*Repository` 类 | `patterns/DESIGN_PATTERNS.md` |
| Strategy 模式 | `*Strategy` 接口 | `patterns/DESIGN_PATTERNS.md` |
| Guard Clause | 提前返回模式 | `patterns/DESIGN_PATTERNS.md` |
| Builder 模式 | 链式构建 | `patterns/DESIGN_PATTERNS.md` |
| Option Pattern | Go 函数式配置 | `patterns/DESIGN_PATTERNS.md` |
| Result Type | Rust/TS 结果类型 | `patterns/ERROR_HANDLING.md` |
| 硬编码 URL | `https://...` 字面量 | `anti-patterns/HARDCODE.md` |
| 硬编码密钥 | `api_key = "..."` | `anti-patterns/HARDCODE.md` |
| 上帝类 | > 15 方法 | `anti-patterns/GOD_CLASS.md` |
| SQL注入风险 | 字符串拼接查询 | `anti-patterns/SECURITY_SMELLS.md` |

### Step 3: 人工审核

蒸馏引擎输出 JSON 报告后，人工审核：
- 模式示例是否有价值
- 反模式描述是否准确
- 是否需要添加到检查清单

### Step 4: 更新文档

审核通过后，追加到对应文档：

```markdown
## 新增模式：[模式名称]

**来源**: `src/service/payment.py`
**语言**: Python
**识别时间**: 2025-09-10

### 示例代码
\`\`\`python
# 代码示例...
\`\`\`

### 适用场景
- ...

### 注意事项
- ...
```

### Step 5: 记录历史

```jsonl
{"timestamp":"2025-09-10T14:30:00","source":"src/service/payment.py","language":"python","patterns":["guard_clause","repository_pattern"],"anti_patterns":[],"score":92,"distiller":"v3.0"}
```

## 蒸馏质量门禁

| 条件 | 要求 |
|------|------|
| 原始代码评分 | ≥ 90（Excellent） |
| 模式示例数量 | ≥ 1 个完整示例 |
| 语言覆盖 | 至少 2 种语言 |
| 人工审核 | 必须通过 |
| 文档更新 | 必须有 |

## 定期蒸馏计划

```bash
# 每周自动蒸馏（crontab 示例）
0 2 * * 1 cd /path/to/code-quality-guard && python3 scripts/distill.py /path/to/project --max-files 200

# 每月深度蒸馏
0 3 1 * * python3 scripts/distill.py /path/to/all-projects --max-files 500 --output distillation/monthly.json
```

## 蒸馏效果追踪

每月统计：
- 新增模式数量
- 新增反模式数量
- 检查清单更新次数
- 审查命中率变化（同类型问题减少）

```json
{
  "period": "2025-09",
  "patterns_added": 3,
  "anti_patterns_added": 2,
  "checklist_updates": 5,
  "false_positive_rate": 0.05,
  "detection_coverage": 0.85
}
```
