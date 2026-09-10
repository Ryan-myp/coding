#!/usr/bin/env python3
"""
Feedback Loop
用户反馈循环系统 - 记录 user-confirmed fixes 和 user-rejected suggestions
"""

import json
import hashlib
from pathlib import Path
from typing import List, Dict, Any
from datetime import datetime
from dataclasses import dataclass, field


@dataclass
class FeedbackRecord:
    """反馈记录"""
    id: str
    timestamp: str
    type: str  # confirmed, rejected, modified
    suggestion_id: str
    feedback: str
    user_id: str = "anonymous"
    project_context: Dict[str, Any] = field(default_factory=dict)
    
    def to_dict(self) -> dict:
        return {
            "id": self.id,
            "timestamp": self.timestamp,
            "type": self.type,
            "suggestion_id": self.suggestion_id,
            "feedback": self.feedback[:200],
            "user_id": self.user_id,
            "project_context": self.project_context
        }


class FeedbackLoop:
    """用户反馈循环"""
    
    def __init__(self, project_dir: str = "."):
        self.project_dir = Path(project_dir)
        self.feedback_dir = self.project_dir / ".qguard" / "feedback"
        self.feedback_dir.mkdir(parents=True, exist_ok=True)
        self.records_file = self.feedback_dir / "records.jsonl"
        self.stats_file = self.feedback_dir / "stats.json"
        
        self.records = self._load_records()
        self.stats = self._load_stats()
    
    def _load_records(self) -> List[Dict]:
        if self.records_file.exists():
            return [json.loads(line) for line in self.records_file.read_text().split('\n') if line.strip()]
        return []
    
    def _save_records(self):
        with open(self.records_file, 'w') as f:
            f.write('\n'.join(json.dumps(r) for r in self.records))
    
    def _load_stats(self) -> Dict:
        if self.stats_file.exists():
            with open(self.stats_file) as f:
                return json.load(f)
        return {"total": 0, "confirmed": 0, "rejected": 0, "modified": 0}
    
    def _save_stats(self):
        with open(self.stats_file, 'w') as f:
            json.dump(self.stats, f, indent=2)
    
    def record_feedback(self, suggestion_id: str, feedback_type: str, 
                        feedback_text: str, user_id: str = "anonymous",
                        project_context: Dict = None) -> str:
        """记录用户反馈"""
        record = FeedbackRecord(
            id=hashlib.md5(f"{suggestion_id}_{datetime.now().isoformat()}".encode()).hexdigest()[:12],
            timestamp=datetime.now().isoformat(),
            type=feedback_type,
            suggestion_id=suggestion_id,
            feedback=feedback_text,
            user_id=user_id,
            project_context=project_context or {}
        )
        
        self.records.append(record.to_dict())
        self._save_records()
        
        # 更新统计
        self.stats["total"] += 1
        self.stats[feedback_type] = self.stats.get(feedback_type, 0) + 1
        self._save_stats()
        
        return record.id
    
    def get_feedback_stats(self) -> Dict:
        """获取反馈统计"""
        total = len(self.records)
        if total == 0:
            return {"total": 0, "response_rate": 0, "approval_rate": 0}
        
        confirmed = len([r for r in self.records if r["type"] == "confirmed"])
        rejected = len([r for r in self.records if r["type"] == "rejected"])
        modified = len([r for r in self.records if r["type"] == "modified"])
        
        return {
            "total": total,
            "confirmed": confirmed,
            "rejected": rejected,
            "modified": modified,
            "response_rate": total / max(self.stats.get("total_suggestions", 1), 1),
            "approval_rate": confirmed / max(total, 1)
        }
    
    def get_improvement_suggestions(self) -> List[str]:
        """基于反馈生成改进建议"""
        improvements = []
        
        # 分析被拒绝的反馈
        rejected = [r for r in self.records if r["type"] == "rejected"]
        if rejected:
            improvements.append({
                "type": "reduce_false_positives",
                "count": len(rejected),
                "suggestion": "Review and refine rules causing false positives"
            })
        
        # 分析被修改的反馈
        modified = [r for r in self.records if r["type"] == "modified"]
        if modified:
            improvements.append({
                "type": "improve_suggestions",
                "count": len(modified),
                "suggestion": "Suggestions often need modification - improve precision"
            })
        
        return improvements
    
    def generate_report(self) -> str:
        """生成反馈报告"""
        stats = self.get_feedback_stats()
        
        report = f"""# Feedback Loop Report

## Statistics
- Total Feedback: {stats['total']}
- Confirmed: {stats['confirmed']}
- Rejected: {stats['rejected']}
- Modified: {stats['modified']}
- Approval Rate: {stats['approval_rate']:.1%}

## Improvement Suggestions
"""
        
        for imp in self.get_improvement_suggestions():
            report += f"- **{imp['type']}**: {imp['suggestion']} ({imp['count']} cases)\n"
        
        report += "\n## Recent Feedback\n"
        recent = sorted(self.records, key=lambda x: x["timestamp"], reverse=True)[:10]
        for r in recent:
            report += f"- [{r['type']}] {r['timestamp'][:10]}: {r['feedback'][:50]}...\n"
        
        return report


def main():
    import argparse
    parser = argparse.ArgumentParser(description="Feedback Loop")
    parser.add_argument("command", choices=["record", "stats", "report", "improve"])
    parser.add_argument("target", nargs="?", default=".")
    parser.add_argument("--type", choices=["confirmed", "rejected", "modified"], required=True)
    parser.add_argument("--suggestion-id", required=True)
    parser.add_argument("--feedback", required=True)
    parser.add_argument("--user", default="anonymous")
    parser.add_argument("--json", action="store_true")
    args = parser.parse_args()
    
    loop = FeedbackLoop(args.target)
    
    if args.command == "record":
        record_id = loop.record_feedback(
            args.suggestion_id,
            args.type,
            args.feedback,
            args.user
        )
        print(f"Recorded feedback: {record_id}")
    
    elif args.command == "stats":
        stats = loop.get_feedback_stats()
        if args.json:
            print(json.dumps(stats, indent=2))
        else:
            print(f"Total: {stats['total']}")
            print(f"Approved: {stats['confirmed']}")
            print(f"Rejected: {stats['rejected']}")
            print(f"Approval Rate: {stats['approval_rate']:.1%}")
    
    elif args.command == "report":
        print(loop.generate_report())
    
    elif args.command == "improve":
        suggestions = loop.get_improvement_suggestions()
        print(json.dumps(suggestions, indent=2))


if __name__ == "__main__":
    import sys
    main()
