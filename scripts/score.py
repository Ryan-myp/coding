#!/usr/bin/env python3
"""
Code Quality Scoring Engine v2
五轴质量评分：Correctness, Readability, Architecture, Security, Performance
支持多语言代码审查
"""

import json
import sys
from dataclasses import dataclass, field
from datetime import datetime
from pathlib import Path
from typing import Optional

SKILL_DIR = Path(__file__).parent.parent
MAX_SCORES = {
    "correctness": 20,
    "readability": 20,
    "architecture": 25,
    "security": 20,
    "performance": 15,
}
WEIGHTS = {
    "correctness": 0.20,
    "readability": 0.20,
    "architecture": 0.25,
    "security": 0.20,
    "performance": 0.15,
}

SEVERITY_WEIGHT = {
    "critical": 3,
    "warning": 2,
    "info": 1,
}


@dataclass
class Issue:
    severity: str  # "critical", "warning", "info"
    axis: str      # "correctness", "readability", "architecture", "security", "performance"
    line: int
    message: str
    suggestion: str = ""
    category: str = ""


@dataclass
class ReviewResult:
    file_path: str
    issues: list = field(default_factory=list)
    highlights: list = field(default_factory=list)
    language: str = "unknown"
    changed_lines: int = 0
    total_lines: int = 0

    @property
    def critical_count(self) -> int:
        return sum(1 for i in self.issues if i.severity == "critical")

    @property
    def warning_count(self) -> int:
        return sum(1 for i in self.issues if i.severity == "warning")

    @property
    def info_count(self) -> int:
        return sum(1 for i in self.issues if i.severity == "info")

    def axis_score(self, axis: str) -> float:
        """计算单个轴得分"""
        max_s = MAX_SCORES[axis]
        axis_issues = [i for i in self.issues if i.axis == axis]
        penalty = sum(
            max_s * SEVERITY_WEIGHT[i.severity] / 10
            for i in axis_issues
        )
        return max(0.0, round(max_s - penalty, 1))

    def get_total_score(self) -> float:
        """计算加权总分"""
        total = 0.0
        for axis, weight in WEIGHTS.items():
            axis_max = MAX_SCORES[axis]
            axis_score = self.axis_score(axis)
            total += (axis_score / axis_max) * weight * 100
        return round(total, 1)

    def get_grade(self) -> tuple:
        score = self.get_total_score()
        if score >= 90:
            return "🟢", "Excellent", "可直接合入"
        elif score >= 70:
            return "🟡", "Good", "小问题需修复"
        elif score >= 50:
            return "🟠", "Fair", "需要较大改进"
        else:
            return "🔴", "Poor", "需要重写"

    def gate_result(self) -> tuple:
        score = self.get_total_score()
        if score >= 70 and self.critical_count == 0:
            return "pass", f"✅ 通过 — 分数 {score} ≥ 70，无 Critical 问题"
        elif self.critical_count > 0:
            return "fail", f"🔴 不通过 — 存在 {self.critical_count} 个 Critical 问题"
        else:
            return "conditional", f"🟠 有条件通过 — 分数 {score}，需修复警告后复审"

    def to_report(self) -> str:
        grade_emoji, grade_name, grade_desc = self.get_grade()
        gate_status, gate_msg = self.gate_result()
        score = self.get_total_score()

        # 按轴分组
        by_axis = {"correctness": [], "readability": [], "architecture": [], "security": [], "performance": []}
        for issue in self.issues:
            by_axis[issue.axis].append(issue)

        axis_labels = {
            "correctness": ("✅ Correctness", "正确性"),
            "readability": ("📖 Readability", "可读性"),
            "architecture": ("🏗️ Architecture", "架构"),
            "security": ("🔒 Security", "安全性"),
            "performance": ("⚡ Performance", "性能"),
        }

        report = f"""# Code Quality Review Report

## Overview
- **File**: `{self.file_path}`
- **Language**: {self.language}
- **Lines**: {self.total_lines} total, {self.changed_lines} changed
- **Review Time**: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
- **Reviewer**: Code Quality Guard (Architect + Engineer + Security + Performer)

## Score: {grade_emoji} **{score}/100** — {grade_name} ({grade_desc})

---

## Axis Scores

| Axis | Score | Max | Status |
|------|-------|-----|--------|
"""
        for axis, (emoji, label) in axis_labels.items():
            s = self.axis_score(axis)
            max_s = MAX_SCORES[axis]
            status = "✅" if s >= max_s * 0.8 else "⚠️" if s >= max_s * 0.5 else "❌"
            report += f"| {emoji} {label} | {s} | {max_s} | {status} |\n"

        report += f"""
### Summary
- 🔴 Critical: {self.critical_count}
- 🟡 Warning: {self.warning_count}
- 🔵 Info: {self.info_count}

---
"""

        for axis, (emoji, label) in axis_labels.items():
            axis_issues = by_axis[axis]
            if not axis_issues:
                report += f"\n## {emoji} {label}\n\n✅ No issues found.\n"
                continue

            report += f"\n## {emoji} {label}\n\n"
            for i, issue in enumerate(axis_issues, 1):
                sev_emoji = "🔴" if issue.severity == "critical" else "🟡" if issue.severity == "warning" else "🔵"
                report += f"### {sev_emoji} {i}. {issue.message}\n"
                if issue.line:
                    report += f"- **Line**: {issue.line}\n"
                if issue.category:
                    report += f"- **Category**: {issue.category}\n"
                if issue.suggestion:
                    report += f"- **Fix**: {issue.suggestion}\n"
                report += "\n"

        if self.highlights:
            report += "\n## ✨ Highlights\n\n"
            for h in self.highlights:
                report += f"- ✅ {h}\n"

        report += f"\n---\n\n## Gate Decision: {gate_msg}\n"

        if self.critical_count > 0 or score < 50:
            report += "\n**Action Required**: Fix all Critical issues before merging.\n"
        elif score < 70:
            report += "\n**Action Required**: Address warnings and resubmit for review.\n"
        else:
            report += "\n**Approved**: Code meets quality standards.\n"

        # 蒸馏建议
        if score >= 90:
            report += "\n---\n\n## 🧪 Distillation Candidate\n\n"
            report += "This code qualifies for pattern extraction. Run distillation to add to the knowledge base.\n"

        return report


def score_code(file_path: str, issues: list[dict] = None, language: str = None) -> ReviewResult:
    """对代码文件进行评分"""
    result = ReviewResult(file_path=file_path, language=language or "unknown")

    # 统计行数
    try:
        with open(file_path) as f:
            lines = f.readlines()
        result.total_lines = len(lines)
    except:
        pass

    if issues:
        for issue in issues:
            result.issues.append(Issue(
                severity=issue.get("severity", "warning"),
                axis=issue.get("axis", "readability"),
                line=issue.get("line", 0),
                message=issue.get("message", ""),
                suggestion=issue.get("suggestion", ""),
                category=issue.get("category", ""),
            ))

    return result


def main():
    if len(sys.argv) < 2:
        print("Usage: python score.py <file_path> [--issues issues.json] [--language lang]")
        sys.exit(1)

    file_path = sys.argv[1]
    issues = []
    language = None

    if "--issues" in sys.argv:
        idx = sys.argv.index("--issues")
        if idx + 1 < len(sys.argv):
            with open(sys.argv[idx + 1]) as f:
                issues = json.load(f)

    if "--language" in sys.argv:
        idx = sys.argv.index("--language")
        if idx + 1 < len(sys.argv):
            language = sys.argv[idx + 1]

    result = score_code(file_path, issues, language)
    print(result.to_report())


if __name__ == "__main__":
    main()
