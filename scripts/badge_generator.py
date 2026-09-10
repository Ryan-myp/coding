#!/usr/bin/env python3
"""
Badge Generator — 生成质量徽章 SVG
用于 README 或 CI 状态显示
"""

from pathlib import Path
from metrics_dashboard import MetricsDashboard


def make_badge(score: float, label: str = "quality", min_score: int = 70) -> str:
    """生成质量徽章 SVG"""
    if score >= 90:
        color = "#4CAF50"  # green
        status = "excellent"
    elif score >= 70:
        color = "#FF9800"  # orange
        status = "good"
    elif score >= 50:
        color = "#FF5722"  # deep orange
        status = "fair"
    else:
        color = "#F44336"  # red
        status = "poor"

    width = 140
    height = 28
    left_width = 90
    right_width = 50

    svg = f'''<svg xmlns="http://www.w3.org/2000/svg" width="{width}" height="{height}">
  <rect width="{width}" height="{height}" rx="4" fill="#555"/>
  <rect x="{left_width}" width="{right_width}" height="{height}" rx="4" fill="{color}"/>
  <text x="8" y="19" font-family="Roboto,Helvetica,sans-serif" font-size="13"
        fill="#fff" font-weight="bold">{label}</text>
  <text x="{left_width + 7}" y="19" font-family="Roboto,Helvetica,sans-serif" font-size="13"
        fill="#fff" font-weight="bold">{score:.0f}</text>
</svg>'''
    return svg


class BadgeGenerator:
    def __init__(self):
        self.dashboard = MetricsDashboard()

    def generate(self, path: str, min_score: int = 70) -> str:
        """为指定路径生成质量徽章"""
        records = self.dashboard.get_all()
        quality = self.dashboard.compute_quality_scores(records)
        score = quality.get("latest", quality.get("avg", 0))
        return make_badge(score, min_score=min_score)

    def generate_for_repo(self, repo_path: str = None) -> dict:
        """为整个仓库生成完整徽章报告"""
        path = Path(repo_path or ".")
        records = self.dashboard.get_all()
        quality = self.dashboard.compute_quality_scores(records)

        return {
            "badge_svg": make_badge(quality.get("avg", 0)),
            "score": quality.get("avg", 0),
            "trend": self.dashboard.compute_trend(records).get("trend", "unknown"),
            "total_records": len(records),
        }
