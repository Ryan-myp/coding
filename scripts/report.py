#!/usr/bin/env python3
"""
审查报告生成器 v2 — 五轴评分 + 质量门禁
"""

import json
import sys
from datetime import datetime
from pathlib import Path


def generate_report(
    file_path: str,
    issues: list[dict],
    highlights: list[str] = None,
    language: str = "unknown",
    total_lines: int = 0,
    changed_lines: int = 0,
) -> str:
    """生成五轴质量审查报告"""
    highlights = highlights or []

    # 分类
    by_severity = {"critical": [], "warning": [], "info": []}
    by_axis = {"correctness": [], "readability": [], "architecture": [], "security": [], "performance": []}

    for issue in issues:
        sev = issue.get("severity", "warning")
        axis = issue.get("axis", "readability")
        by_severity.setdefault(sev, []).append(issue)
        by_axis.setdefault(axis, []).append(issue)

    # 评分
    MAX_SCORES = {"correctness": 20, "readability": 20, "architecture": 25, "security": 20, "performance": 15}
    SEVERITY_PENALTY = {"critical": 5, "warning": 2, "info": 0.5}

    axis_scores = {}
    for axis, max_s in MAX_SCORES.items():
        penalty = sum(SEVERITY_PENALTY.get(i.get("severity", "warning"), 2) for i in by_axis.get(axis, []))
        axis_scores[axis] = max(0, round(max_s - penalty, 1))

    WEIGHTS = {"correctness": 0.20, "readability": 0.20, "architecture": 0.25, "security": 0.20, "performance": 0.15}
    total_score = sum(axis_scores[a] / MAX_SCORES[a] * WEIGHTS[a] * 100 for a in WEIGHTS)
    total_score = round(total_score, 1)

    # 分级
    if total_score >= 90:
        grade_emoji, grade_name, gate = "🟢", "Excellent", "pass"
    elif total_score >= 70:
        grade_emoji, grade_name, gate = "🟡", "Good", "conditional"
    elif total_score >= 50:
        grade_emoji, grade_name, gate = "🟠", "Fair", "fail"
    else:
        grade_emoji, grade_name, gate = "🔴", "Poor", "fail"

    critical_count = len(by_severity["critical"])
    if critical_count > 0:
        gate = "fail"

    axis_labels = {
        "correctness": ("✅ Correctness", 20),
        "readability": ("📖 Readability", 20),
        "architecture": ("🏗️ Architecture", 25),
        "security": ("🔒 Security", 20),
        "performance": ("⚡ Performance", 15),
    }

    report = f"""# Code Quality Review Report

## Overview
| Field | Value |
|-------|-------|
| File | `{file_path}` |
| Language | {language} |
| Lines | {total_lines} total / {changed_lines} changed |
| Time | {datetime.now().strftime('%Y-%m-%d %H:%M:%S')} |
| Reviewer | Code Quality Guard (4-axis) |

## Score: {grade_emoji} **{total_score}/100** — {grade_name}

### Axis Breakdown
| Axis | Score | Max | Issues |
|------|-------|-----|--------|
"""
    for axis, (emoji, max_s) in axis_labels.items():
        issues_count = len(by_axis.get(axis, []))
        report += f"| {emoji} | {axis_scores.get(axis, max_s)} | {max_s} | {issues_count} |\n"

    report += f"""
### Issue Summary
| Severity | Count |
|----------|-------|
| 🔴 Critical | {critical_count} |
| 🟡 Warning | {len(by_severity['warning'])} |
| 🔵 Info | {len(by_severity['info'])} |

---
"""

    # 详细问题
    for axis, (emoji, _) in axis_labels.items():
        axis_issues = by_axis.get(axis, [])
        if not axis_issues:
            continue
        report += f"\n## {emoji}\n\n"
        for issue in axis_issues:
            sev = issue.get("severity", "warning")
            sev_emoji = "🔴" if sev == "critical" else "🟡" if sev == "warning" else "🔵"
            report += f"### {sev_emoji} {issue.get('message', 'Unknown issue')}"
            if issue.get("line"):
                report += f" (Line {issue['line']})"
            report += "\n"
            if issue.get("category"):
                report += f"- **Category**: {issue['category']}\n"
            if issue.get("suggestion"):
                report += f"- **Fix**: {issue['suggestion']}\n"
            report += "\n"

    if highlights:
        report += "\n## ✨ Highlights\n\n"
        for h in highlights:
            report += f"- ✅ {h}\n"

    # 门禁判定
    report += "\n---\n\n## Gate Decision\n\n"
    if gate == "pass":
        report += f"🟢 **APPROVED** — Score {total_score} ≥ 70, no Critical issues\n"
    elif gate == "fail":
        report += f"🔴 **REJECTED** — {critical_count} Critical issue(s) found, score {total_score}\n"
        report += "**Action**: Fix all Critical issues and resubmit.\n"
    else:
        report += f"🟠 **CONDITIONAL** — Score {total_score}, {len(by_severity['warning'])} warning(s) remain\n"
        report += "**Action**: Address warnings before merge.\n"

    # 蒸馏建议
    if total_score >= 90:
        report += """

---

## 🧪 Distillation Candidate

This code qualifies for pattern extraction:

```bash
python3 scripts/distill.py <file_path>
```

Patterns will be extracted to `references/patterns/`.
"""

    return report


def main():
    if len(sys.argv) < 2:
        print("Usage: python report.py <file_path> [--issues issues.json] [--language lang]")
        sys.exit(1)

    file_path = sys.argv[1]
    issues = []
    language = "unknown"

    if "--issues" in sys.argv:
        idx = sys.argv.index("--issues")
        if idx + 1 < len(sys.argv):
            with open(sys.argv[idx + 1]) as f:
                issues = json.load(f)

    if "--language" in sys.argv:
        idx = sys.argv.index("--language")
        if idx + 1 < len(sys.argv):
            language = sys.argv[idx + 1]

    report = generate_report(file_path, issues, language=language)
    print(report)


if __name__ == "__main__":
    main()
