# 审查报告模板

## 基本信息
- 审查时间：{{timestamp}}
- 审查文件：{{file_path}}
- 审查者：Code Quality Guard

## 综合评分：{{grade_emoji}} {{total_score}}/100 ({{grade_name}})

## 维度评分

| 角色 | 分数 | 问题数 | 警告数 |
|------|------|--------|--------|
| 🏛️ Architect | {{arch_score}} | {{arch_issues}} | {{arch_warnings}} |
| 👷 Engineer | {{eng_score}} | {{eng_issues}} | {{eng_warnings}} |
| 🔒 Security | {{sec_score}} | {{sec_issues}} | {{sec_warnings}} |

## 发现的问题

### 🔴 严重（必须修复）
{{critical_issues}}

### 🟡 警告（建议修复）
{{warning_issues}}

### 🔵 建议
{{info_issues}}

## 亮点
{{highlights}}

## 质量门禁
{{gate_result}}

## 蒸馏建议
{{distillation_suggestions}}
