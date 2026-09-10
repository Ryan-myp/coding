#!/usr/bin/env python3
"""
Code Quality Scoring Engine
基于三角色检查清单的质量评分
"""

import json
import sys
from dataclasses import dataclass, field
from typing import dict

# 权重配置
WEIGHTS = {
    "architecture": 0.30,
    "readability": 0.20,
    "maintainability": 0.20,
    "testability": 0.10,
    "security": 0.20,
}

# 维度满分
MAX_SCORES = {
    "architecture": 30,
    "readability": 20,
    "maintainability": 20,
    "testability": 10,
    "security": 20,
}


@dataclass
class Issue:
    severity: str  # "critical", "warning", "info"
    role: str      # "architect", "engineer", "security"
    line: int
    message: str
    suggestion: str = ""
    category: str = ""


@dataclass
class ReviewResult:
    file_path: str
    issues: list = field(default_factory=list)
    highlights: list = field(default_factory=list)

    @property
    def critical_count(self) -> int:
        return sum(1 for i in self.issues if i.severity == "critical")

    @property
    def warning_count(self) -> int:
        return sum(1 for i in self.issues if i.severity == "warning")

    @property
    def info_count(self) -> int:
        return sum(1 for i in self.issues if i.severity == "info")

    def calculate_score(self) -> dict:
        """计算各维度分数"""
        scores = {}
        for dimension, max_s in MAX_SCORES.items():
            # 简化评分逻辑：每有个 critical 扣 max/3，warning 扣 max/6
            dimension_issues = [
                i for i in self.issues
                if i.role == dimension or (dimension == "architecture" and i.role == "architect")
                or (dimension == "security" and i.role == "security")
                or (dimension in ("readability", "maintainability", "testability") and i.role == "engineer")
            ]
            penalty = sum(
                max_s / 3 if i.severity == "critical" else max_s / 6 if i.severity == "warning" else 0
                for i in dimension_issues
            )
            scores[dimension] = max(0, round(max_s - penalty, 1))
        return scores

    def get_total_score(self) -> float:
        scores = self.calculate_score()
        total = sum(scores[d] * WEIGHTS[d] / MAX_SCORES[d] * 100 for d in scores)
        return round(total, 1)

    def get_grade(self) -> tuple:
        score = self.get_total_score()
        if score >= 90:
            return "🟢", "优秀"
        elif score >= 70:
            return "🟡", "良好"
        elif score >= 50:
            return "🟠", "一般"
        else:
            return "🔴", "不合格"

    def to_report(self) -> str:
        grade_emoji, grade_name = self.get_grade()
        score = self.get_total_score()
        scores = self.calculate_score()

        report = f"""# 代码质量审查报告

## 基本信息
- 审查文件：{self.file_path}
- 综合评分：{grade_emoji} {score}/100 ({grade_name})

## 维度评分

| 维度 | 得分 | 满分 | 状态 |
|------|------|------|------|
| 架构合理性 | {scores.get('architecture', 0)} | {MAX_SCORES['architecture']} | {'✅' if scores.get('architecture', 0) >= 24 else '⚠️' if scores.get('architecture', 0) >= 15 else '❌'} |
| 可读性 | {scores.get('readability', 0)} | {MAX_SCORES['readability']} | {'✅' if scores.get('readability', 0) >= 16 else '⚠️' if scores.get('readability', 0) >= 10 else '❌'} |
| 可维护性 | {scores.get('maintainability', 0)} | {MAX_SCORES['maintainability']} | {'✅' if scores.get('maintainability', 0) >= 16 else '⚠️' if scores.get('maintainability', 0) >= 10 else '❌'} |
| 可测试性 | {scores.get('testability', 0)} | {MAX_SCORES['testability']} | {'✅' if scores.get('testability', 0) >= 8 else '⚠️' if scores.get('testability', 0) >= 5 else '❌'} |
| 安全性 | {scores.get('security', 0)} | {MAX_SCORES['security']} | {'✅' if scores.get('security', 0) >= 16 else '⚠️' if scores.get('security', 0) >= 10 else '❌'} |

## 问题汇总
- 🔴 严重问题：{self.critical_count} 个
- 🟡 警告：{self.warning_count} 个
- 🔵 建议：{self.info_count} 个

## 详细问题
"""
        if self.issues:
            for i, issue in enumerate(self.issues, 1):
                emoji = "🔴" if issue.severity == "critical" else "🟡" if issue.severity == "warning" else "🔵"
                report += f"\n### {emoji} [{issue.role.capitalize()}] {issue.message}"
                if issue.line:
                    report += f" (Line {issue.line})"
                report += f"\n- **类别**: {issue.category}"
                if issue.suggestion:
                    report += f"\n- **建议**: {issue.suggestion}"
        else:
            report += "\n✅ 未发现明显问题！"

        if self.highlights:
            report += "\n\n## 亮点\n"
            for h in self.highlights:
                report += f"- ✅ {h}\n"

        return report


def score_code(file_path: str, issues: list[dict] = None) -> ReviewResult:
    """对代码文件进行评分"""
    result = ReviewResult(file_path=file_path)

    if issues:
        for issue in issues:
            result.issues.append(Issue(
                severity=issue.get("severity", "warning"),
                role=issue.get("role", "engineer"),
                line=issue.get("line", 0),
                message=issue.get("message", ""),
                suggestion=issue.get("suggestion", ""),
                category=issue.get("category", ""),
            ))

    return result


def main():
    if len(sys.argv) < 2:
        print("Usage: python score.py <file_path> [--issues issues.json]")
        sys.exit(1)

    file_path = sys.argv[1]
    issues = None

    if "--issues" in sys.argv:
        idx = sys.argv.index("--issues")
        if idx + 1 < len(sys.argv):
            with open(sys.argv[idx + 1]) as f:
                issues = json.load(f)

    result = score_code(file_path, issues)
    print(result.to_report())


if __name__ == "__main__":
    main()
