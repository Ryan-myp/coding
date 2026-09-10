#!/usr/bin/env python3
"""
Metrics Dashboard — 质量趋势仪表板
从 distillation/history.jsonl 读取历史数据，生成趋势报告
"""

import json
import sys
from pathlib import Path
from datetime import datetime, timedelta
from collections import defaultdict


class MetricsDashboard:
    def __init__(self, history_file: str = None):
        self.history_file = Path(history_file or str(
            Path(__file__).parent.parent / "distillation" / "history.jsonl"))

    def get_all(self) -> list:
        """读取所有历史记录"""
        if not self.history_file.exists():
            return []
        records = []
        with open(self.history_file) as f:
            for line in f:
                line = line.strip()
                if line:
                    try:
                        records.append(json.loads(line))
                    except:
                        pass
        return records

    def get_recent(self, days: int = 30) -> list:
        """获取最近 N 天的记录"""
        all_records = self.get_all()
        cutoff = datetime.utcnow() - timedelta(days=days)
        return [r for r in all_records
                if datetime.fromisoformat(r["timestamp"].replace("Z", "+00:00")).replace(tzinfo=None) >= cutoff]

    def compute_trend(self, records: list) -> dict:
        """计算趋势指标"""
        if not records:
            return {"trend": "no_data", "avg_score": 0, "change": 0}

        # 按日期分组
        by_date = defaultdict(list)
        for r in records:
            date = r["timestamp"][:10]
            by_date[date].append(r)

        dates = sorted(by_date.keys())
        if len(dates) < 2:
            return {"trend": "insufficient_data", "dates": dates, "record_count": len(records)}

        # 计算每日平均分数（模拟）
        # 实际应从 score 结果中提取
        first_half = dates[:len(dates)//2]
        second_half = dates[len(dates)//2:]

        first_avg = sum(len(by_date[d]) for d in first_half) / max(len(first_half), 1)
        second_avg = sum(len(by_date[d]) for d in second_half) / max(len(second_half), 1)

        change = second_avg - first_avg
        trend = "improving" if change > 10 else "declining" if change < -10 else "stable"

        return {
            "trend": trend,
            "first_period_avg": round(first_avg, 1),
            "second_period_avg": round(second_avg, 1),
            "change": round(change, 1),
            "total_records": len(records),
            "date_range": f"{dates[0]} ~ {dates[-1]}",
        }

    def compute_quality_scores(self, records: list) -> dict:
        """从历史记录计算质量评分趋势（简化版）"""
        if not records:
            return {"scores": [], "avg": 0, "min": 0, "max": 0}

        # 从 pattern/anti-pattern 数量推断质量
        scores = []
        for r in records:
            # 简化：分数 = 100 - (anti_patterns * 5) - (patterns > 10 ? 10 : 0)
            anti = r.get("anti_patterns_found", 0)
            pat = r.get("patterns_found", 0)
            score = max(0, 100 - anti * 5 - (10 if pat > 10 else 0))
            scores.append({"date": r["timestamp"][:10], "score": score})

        if not scores:
            return {"scores": [], "avg": 0}

        avg = sum(s["score"] for s in scores) / len(scores)
        return {
            "scores": scores[-30:],  # 最近30条
            "avg": round(avg, 1),
            "min": min(s["score"] for s in scores),
            "max": max(s["score"] for s in scores),
            "latest": scores[-1]["score"] if scores else 0,
        }

    def print_dashboard(self, records: list = None):
        """打印仪表板"""
        records = records or self.get_all()
        trend = self.compute_trend(records)
        quality = self.compute_quality_scores(records)

        print(f"\n{'='*60}")
        print(f"  Code Quality Dashboard")
        print(f"{'='*60}\n")

        print(f"  Records:      {len(records)}")
        print(f"  Trend:        {trend.get('trend', 'N/A')}")
        if 'change' in trend:
            print(f"  Change:       {trend['change']:+.1f} points")
        print(f"  Avg Score:    {quality.get('avg', 0):.1f}/100")
        print(f"  Score Range:  {quality.get('min', 0)} ~ {quality.get('max', 0)}")
        print(f"  Latest:       {quality.get('latest', 'N/A')}")
        print()

        if quality.get("scores"):
            print("  Score History (last 10):")
            for s in quality["scores"][-10:]:
                bar = "█" * int(s["score"] / 5) + "░" * (20 - int(s["score"] / 5))
                print(f"    {s['date']}  {bar} {s['score']:3.0f}")
        print()
