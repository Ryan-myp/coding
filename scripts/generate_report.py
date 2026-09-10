#!/usr/bin/env python3
"""
Review Report Generator
生成格式化的代码质量审查报告
"""

import json
import sys
from datetime import datetime
from pathlib import Path

SKILL_DIR = Path(__file__).parent.parent
TEMPLATE_DIR = SKILL_DIR / "templates"


def generate_report(
    file_path: str,
    issues: list[dict],
    highlights: list[str] = None,
    scorable: bool = True,
) -> str:
    """生成审查报告"""
    highlights = highlights or []

    # 分类问题
    critical = [i for i in issues if i.get("severity") == "critical"]
    warnings = [i for i in issues if i.get("severity") == "warning"]
    infos = [i for i in issues if i.get("severity") == "info"]

    # 按角色分组
    by_role = {"architect": [], "engineer": [], "security": []}
    for issue in issues:
        role = issue.get("role", "engineer")
        if role in by_role:
            by_role[role].append(issue)

    # 计算分数（简化版）
    total_score = 100
    for issue in issues:
        if issue.get("severity") == "critical":
            total_score -= 10
        elif issue.get("severity") == "warning":
            total_score -= 5
        elif issue.get("severity") == "info":
            total_score -= 2
    total_score = max(0, total_score)

    # 分级
    if total_score >= 90:
        grade_emoji, grade_name = "🟢", "优秀"
    elif total_score >= 70:
        grade_emoji, grade_name = "🟡", "良好"
    elif total_score >= 50:
        grade_emoji, grade_name = "🟠", "一般"
    else:
        grade_emoji, grade_name = "🔴", "不合格"

    report = f"""# 代码质量审查报告

## 基本信息
- 审查时间：{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
- 审查文件：`{file_path}`
- 审查者：Code Quality Guard (Architect + Engineer + Security)

## 综合评分：{grade_emoji} {total_score}/100 ({grade_name})

| 角色 | 问题数 | 警告数 |
|------|--------|--------|
| 🏛️ Architect | {len(by_role['architect'])} | {len([i for i in by_role['architect'] if i.get('severity') == 'warning'])} |
| 👷 Engineer | {len(by_role['engineer'])} | {len([i for i in by_role['engineer'] if i.get('severity') == 'warning'])} |
| 🔒 Security | {len(by_role['security'])} | {len([i for i in by_role['security'] if i.get('severity') == 'warning'])} |

---

## 🔴 严重问题（必须修复）
"""

    if critical:
        for i, issue in enumerate(critical, 1):
            report += f"""
### {i}. [{issue.get('role', 'engineer').capitalize()}] {issue.get('message')}
- **位置**：Line {issue.get('line', 'N/A')}
- **类别**：{issue.get('category', 'general')}
- **建议修复**：{issue.get('suggestion', '请人工评估')}
"""
    else:
        report += "\n✅ 无严重问题\n"

    report += "\n---\n\n## 🟡 警告（建议修复）\n"
    if warnings:
        for i, issue in enumerate(warnings, 1):
            report += f"""
- [{issue.get('role', 'engineer').capitalize()}] Line {issue.get('line', 'N/A')}：{issue.get('message')}
  - 建议：{issue.get('suggestion', '')}
"""
    else:
        report += "\n✅ 无警告\n"

    report += "\n---\n\n## 🔵 建议（可选优化）\n"
    if infos:
        for i, issue in enumerate(infos, 1):
            report += f"\n- [{issue.get('role', 'engineer').capitalize()}] {issue.get('message')}"
    else:
        report += "\n✅ 无额外建议\n"

    if highlights:
        report += "\n---\n\n## ✨ 代码亮点\n"
        for h in highlights:
            report += f"\n- ✅ {h}"

    report += f"""

---

## 📊 质量门禁判定

"""
    if total_score >= 70:
        report += f"🟢 **通过** — 分数 {total_score} ≥ 70，可以合入\n"
    elif total_score >= 50:
        report += f"🟠 **有条件通过** — 分数 {total_score}，建议修复严重问题后复审\n"
    else:
        report += f"🔴 **不通过** — 分数 {total_score} < 50，需要重写后重新审查\n"

    return report


def main():
    if len(sys.argv) < 2:
        print("Usage: python generate_report.py <file_path> [--issues issues.json]")
        sys.exit(1)

    file_path = sys.argv[1]
    issues = []

    if "--issues" in sys.argv:
        idx = sys.argv.index("--issues")
        if idx + 1 < len(sys.argv):
            with open(sys.argv[idx + 1]) as f:
                issues = json.load(f)

    report = generate_report(file_path, issues)
    print(report)


if __name__ == "__main__":
    main()
