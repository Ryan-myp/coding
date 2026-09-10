#!/usr/bin/env python3
"""
Self-Learning Engine
从成功和失败中学习，持续改进
"""

import json
import hashlib
from pathlib import Path
from typing import List, Dict, Any
from datetime import datetime
from dataclasses import dataclass, field


@dataclass
class LearningRecord:
    """学习记录"""
    id: str
    timestamp: str
    type: str  # success, failure, pattern
    content: str
    context: Dict[str, Any] = field(default_factory=dict)
    outcome: str = ""  # passed, failed, improved
    tags: List[str] = field(default_factory=list)
    
    def to_dict(self) -> dict:
        return {
            "id": self.id,
            "timestamp": self.timestamp,
            "type": self.type,
            "content": self.content[:200],  # 截断
            "context": self.context,
            "outcome": self.outcome,
            "tags": self.tags
        }


class SelfLearningEngine:
    """自学习引擎"""
    
    def __init__(self, project_dir: str = "."):
        self.project_dir = Path(project_dir)
        self.learnings_dir = self.project_dir / ".qguard" / "learnings"
        self.learnings_dir.mkdir(parents=True, exist_ok=True)
        self.records_file = self.learnings_dir / "records.jsonl"
        self.patterns_file = self.learnings_dir / "patterns.json"
        
        self._load_existing()
    
    def _load_existing(self):
        """加载已有学习记录"""
        if self.records_file.exists():
            self.records = [json.loads(line) for line in self.records_file.read_text().split('\n') if line.strip()]
        else:
            self.records = []
        
        if self.patterns_file.exists():
            self.patterns = json.load(open(self.patterns_file))
        else:
            self.patterns = {"success": [], "failure": [], "improvement": []}
    
    def record_success(self, code: str, intent: str, language: str, tags: List[str] = None) -> str:
        """记录成功的代码生成"""
        record = LearningRecord(
            id=hashlib.md5(code.encode()).hexdigest()[:12],
            timestamp=datetime.now().isoformat(),
            type="success",
            content=code[:500],
            context={"intent": intent, "language": language},
            outcome="passed",
            tags=tags or []
        )
        
        self.records.append(record.to_dict())
        self._save()
        
        # 提取模式
        pattern = self._extract_pattern(record)
        if pattern:
            self.patterns["success"].append(pattern)
            self._save_patterns()
        
        return record.id
    
    def record_failure(self, code: str, intent: str, language: str, error: str, tags: List[str] = None) -> str:
        """记录失败的代码生成"""
        record = LearningRecord(
            id=hashlib.md5((code + error).encode()).hexdigest()[:12],
            timestamp=datetime.now().isoformat(),
            type="failure",
            content=code[:500],
            context={"intent": intent, "language": language, "error": error},
            outcome="failed",
            tags=tags or []
        )
        
        self.records.append(record.to_dict())
        self._save()
        
        # 提取反模式
        pattern = self._extract_pattern(record)
        if pattern:
            self.patterns["failure"].append(pattern)
            self._save_patterns()
        
        return record.id
    
    def record_improvement(self, original: str, improved: str, notes: str = "") -> str:
        """记录代码改进"""
        record = LearningRecord(
            id=hashlib.md5((original + improved).encode()).hexdigest()[:12],
            timestamp=datetime.now().isoformat(),
            type="improvement",
            content=improved[:500],
            context={"original": original[:200], "notes": notes},
            outcome="improved",
            tags=["refactor", "improvement"]
        )
        
        self.records.append(record.to_dict())
        self._save()
        
        return record.id
    
    def _extract_pattern(self, record: LearningRecord) -> Dict:
        """提取模式"""
        pattern = {
            "type": record.type,
            "language": record.context.get("language", "unknown"),
            "tags": record.tags,
            "keywords": self._extract_keywords(record.content)
        }
        return pattern
    
    def _extract_keywords(self, text: str) -> List[str]:
        """提取关键词"""
        # 简单关键词提取
        words = text.lower().split()
        common = {"def", "class", "function", "async", "await", "try", "except", "if", "else", "return"}
        return [w for w in words if len(w) > 3 and w not in common][:10]
    
    def get_similar_patterns(self, code: str, limit: int = 5) -> List[Dict]:
        """查找相似模式"""
        keywords = set(self._extract_keywords(code))
        similar = []
        
        for pattern in self.patterns.get("success", []):
            pattern_keywords = set(pattern.get("keywords", []))
            match = len(keywords & pattern_keywords)
            if match > 0:
                similar.append({
                    "pattern": pattern,
                    "match_score": match / max(len(keywords), 1)
                })
        
        similar.sort(key=lambda x: x["match_score"], reverse=True)
        return similar[:limit]
    
    def get_learning_stats(self) -> Dict:
        """获取学习统计"""
        success_count = len([r for r in self.records if r["type"] == "success"])
        failure_count = len([r for r in self.records if r["type"] == "failure"])
        improvement_count = len([r for r in self.records if r["type"] == "improvement"])
        
        return {
            "total_records": len(self.records),
            "success": success_count,
            "failure": failure_count,
            "improvement": improvement_count,
            "success_rate": success_count / max(success_count + failure_count, 1),
            "patterns_count": len(self.patterns.get("success", []))
        }
    
    def generate_insight_report(self) -> str:
        """生成洞察报告"""
        stats = self.get_learning_stats()
        
        report = f"""# Self-Learning Report

## Statistics
- Total Records: {stats['total_records']}
- Success: {stats['success']}
- Failure: {stats['failure']}
- Improvements: {stats['improvement']}
- Success Rate: {stats['success_rate']:.1%}
- Patterns Extracted: {stats['patterns_count']}

## Recent Learning
"""
        
        recent = sorted(self.records, key=lambda x: x["timestamp"], reverse=True)[:5]
        for r in recent:
            report += f"- [{r['type']}] {r['timestamp'][:10]}: {r['content'][:50]}...\n"
        
        return report
    
    def _save(self):
        """保存记录"""
        with open(self.records_file, 'w') as f:
            f.write('\n'.join(json.dumps(r) for r in self.records))
    
    def _save_patterns(self):
        """保存模式"""
        with open(self.patterns_file, 'w') as f:
            json.dump(self.patterns, f, indent=2)


def main():
    import argparse
    parser = argparse.ArgumentParser(description="Self-Learning Engine")
    parser.add_argument("command", choices=["record-success", "record-failure", "learn", "stats", "report"])
    parser.add_argument("target", nargs="?", default=".")
    parser.add_argument("--intent", help="Intent type")
    parser.add_argument("--language", default="python")
    parser.add_argument("--tags", help="Comma-separated tags")
    parser.add_argument("--error", help="Error message (for failure)")
    parser.add_argument("--json", action="store_true")
    args = parser.parse_args()
    
    engine = SelfLearningEngine(args.target)
    
    if args.command == "record-success":
        try:
            with open(args.target) as f:
                code = f.read()
        except:
            print("Provide code via stdin or file")
            return
        tags = args.tags.split(',') if args.tags else []
        record_id = engine.record_success(code, args.intent or "feature", args.language, tags)
        print(f"Recorded success: {record_id}")
    
    elif args.command == "record-failure":
        try:
            with open(args.target) as f:
                code = f.read()
        except:
            code = ""
        tags = args.tags.split(',') if args.tags else []
        record_id = engine.record_failure(code, args.intent or "feature", args.language, args.error or "", tags)
        print(f"Recorded failure: {record_id}")
    
    elif args.command == "stats":
        stats = engine.get_learning_stats()
        print(json.dumps(stats, indent=2))
    
    elif args.command == "report":
        print(engine.generate_insight_report())
    
    elif args.command == "learn":
        # 查找相似模式
        code = sys.stdin.read() if not sys.stdin.isatty() else ""
        if code:
            patterns = engine.get_similar_patterns(code)
            print(json.dumps(patterns, indent=2))
        else:
            print("Provide code to find similar patterns")


if __name__ == "__main__":
    main()
