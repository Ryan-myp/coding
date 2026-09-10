#!/usr/bin/env python3
"""
Enhanced Pattern Library
支持人工维护和 AI 辅助的模式库
"""

import json
import hashlib
from pathlib import Path
from typing import List, Dict, Any, Optional
from datetime import datetime
from dataclasses import dataclass, field


@dataclass
class Pattern:
    """代码模式"""
    id: str
    name: str
    category: str  # error-handling, architecture, security, performance, testing
    language: str
    description: str
    code_example: str
    anti_pattern: str = ""
    tags: List[str] = field(default_factory=list)
    quality_score: float = 0.0
    source: str = ""  # manual, ai, github
    created_at: str = ""
    updated_at: str = ""
    usage_count: int = 0
    success_rate: float = 0.0
    
    def to_dict(self) -> dict:
        return {
            "id": self.id,
            "name": self.name,
            "category": self.category,
            "language": self.language,
            "description": self.description,
            "code_example": self.code_example[:300],
            "anti_pattern": self.anti_pattern,
            "tags": self.tags,
            "quality_score": self.quality_score,
            "source": self.source,
            "created_at": self.created_at,
            "updated_at": self.updated_at,
            "usage_count": self.usage_count,
            "success_rate": self.success_rate
        }
    
    @classmethod
    def from_dict(cls, data: dict) -> 'Pattern':
        return cls(**data)


class EnhancedPatternLibrary:
    """增强模式库"""
    
    def __init__(self, project_dir: str = "."):
        self.project_dir = Path(project_dir)
        self.library_dir = self.project_dir / ".qguard" / "patterns"
        self.library_dir.mkdir(parents=True, exist_ok=True)
        self.library_file = self.library_dir / "library.json"
        self.history_file = self.library_dir / "history.jsonl"
        
        self.patterns = self._load_library()
        self.history = self._load_history()
    
    def _load_library(self) -> List[Dict]:
        """加载模式库"""
        if self.library_file.exists():
            with open(self.library_file) as f:
                return json.load(f)
        return []
    
    def _save_library(self):
        """保存模式库"""
        with open(self.library_file, 'w') as f:
            json.dump(self.patterns, f, indent=2)
    
    def _load_history(self) -> List[Dict]:
        """加载使用历史"""
        if self.history_file.exists():
            return [json.loads(line) for line in self.history_file.read_text().split('\n') if line.strip()]
        return []
    
    def _save_history(self):
        """保存使用历史"""
        with open(self.history_file, 'w') as f:
            f.write('\n'.join(json.dumps(h) for h in self.history))
    
    def add_pattern(self, pattern: Pattern, source: str = "manual") -> str:
        """添加模式"""
        # 生成 ID
        if not pattern.id:
            pattern.id = hashlib.md5(f"{pattern.name}_{pattern.language}".encode()).hexdigest()[:12]
        
        now = datetime.now().isoformat()
        pattern.created_at = now
        pattern.updated_at = now
        pattern.source = source
        
        # 检查是否已存在
        existing = self._find_pattern(pattern.id)
        if existing:
            # 更新而非添加
            for i, p in enumerate(self.patterns):
                if p.get("id") == pattern.id:
                    self.patterns[i] = pattern.to_dict()
                    break
        else:
            self.patterns.append(pattern.to_dict())
        
        self._save_library()
        return pattern.id
    
    def _find_pattern(self, pattern_id: str) -> Optional[Dict]:
        """查找模式"""
        for p in self.patterns:
            if p.get("id") == pattern_id:
                return p
        return None
    
    def record_usage(self, pattern_id: str, success: bool) -> Dict:
        """记录模式使用"""
        now = datetime.now().isoformat()
        
        # 更新统计
        for p in self.patterns:
            if p.get("id") == pattern_id:
                p["usage_count"] = p.get("usage_count", 0) + 1
                success_count = p.get("success_count", 0) + (1 if success else 0)
                total = p["usage_count"]
                p["success_rate"] = success_count / total
                p["updated_at"] = now
                self._save_library()
                break
        
        # 记录历史
        self.history.append({
            "pattern_id": pattern_id,
            "timestamp": now,
            "success": success,
            "action": "used"
        })
        self._save_history()
        
        return {"pattern_id": pattern_id, "usage_count": 1, "success_rate": 1.0 if success else 0.0}
    
    def get_similar_patterns(self, code: str, language: str, limit: int = 5) -> List[Dict]:
        """查找相似模式"""
        # 提取关键词
        keywords = self._extract_keywords(code, language)
        
        # 计算相似度
        similar = []
        for p in self.patterns:
            if p.get("language") != language and language != "all":
                continue
            
            pattern_keywords = set(p.get("tags", []) + p.get("name", "").lower().split())
            match = len(keywords & pattern_keywords)
            
            if match > 0:
                similar.append({
                    "pattern": p,
                    "match_score": match / max(len(keywords), 1),
                    "usage_count": p.get("usage_count", 0),
                    "success_rate": p.get("success_rate", 0)
                })
        
        # 按匹配度和成功率排序
        similar.sort(key=lambda x: (x["match_score"], x["success_rate"]), reverse=True)
        return similar[:limit]
    
    def _extract_keywords(self, code: str, language: str) -> set:
        """提取关键词"""
        keywords = set()
        
        # 通用关键词
        generic_keywords = {
            "error", "exception", "handling", "logging",
            "async", "await", "concurrent", "parallel",
            "type", "interface", "abstract", "generic",
            "security", "auth", "encrypt", "hash",
            "test", "mock", "stub", "fixture"
        }
        
        # 语言特定关键词
        if language == "python":
            lang_keywords = {"def", "class", "try", "except", "with", "yield", "async", "await"}
        elif language == "typescript":
            lang_keywords = {"interface", "type", "async", "await", "Promise", "Observable"}
        elif language == "go":
            lang_keywords = {"go func", "chan", "defer", "interface", "error"}
        elif language == "java":
            lang_keywords = {"class", "interface", "extends", "implements", "try", "catch"}
        elif language == "rust":
            lang_keywords = {"fn", "impl", "trait", "match", "unwrap", "expect"}
        else:
            lang_keywords = set()
        
        # 从代码中提取
        words = code.lower().split()
        for word in words:
            # 清理标点
            clean_word = word.strip('.,;:(){}[]"\'')
            if len(clean_word) > 3:
                keywords.add(clean_word)
        
        # 添加预定义关键词
        keywords.update(generic_keywords)
        keywords.update(lang_keywords)
        
        return keywords
    
    def get_statistics(self) -> Dict:
        """获取统计信息"""
        total = len(self.patterns)
        by_category = {}
        by_language = {}
        by_source = {}
        
        for p in self.patterns:
            cat = p.get("category", "unknown")
            lang = p.get("language", "unknown")
            source = p.get("source", "unknown")
            
            by_category[cat] = by_category.get(cat, 0) + 1
            by_language[lang] = by_language.get(lang, 0) + 1
            by_source[source] = by_source.get(source, 0) + 1
        
        # 成功率统计
        avg_success_rate = 0
        if self.patterns:
            avg_success_rate = sum(p.get("success_rate", 0) for p in self.patterns) / total
        
        return {
            "total_patterns": total,
            "by_category": by_category,
            "by_language": by_language,
            "by_source": by_source,
            "average_success_rate": avg_success_rate,
            "total_usages": sum(p.get("usage_count", 0) for p in self.patterns),
            "history_count": len(self.history)
        }
    
    def generate_report(self) -> str:
        """生成模式库报告"""
        stats = self.get_statistics()
        
        report = f"""# Pattern Library Report

## Statistics
- Total Patterns: {stats['total_patterns']}
- Total Usages: {stats['total_usages']}
- History Records: {stats['history_count']}
- Average Success Rate: {stats['average_success_rate']:.1%}

## By Category
"""
        for cat, count in sorted(stats['by_category'].items()):
            report += f"- {cat}: {count}\n"
        
        report += "\n## By Language\n"
        for lang, count in sorted(stats['by_language'].items()):
            report += f"- {lang}: {count}\n"
        
        report += "\n## By Source\n"
        for source, count in sorted(stats['by_source'].items()):
            report += f"- {source}: {count}\n"
        
        report += "\n## Top Patterns\n"
        sorted_patterns = sorted(self.patterns, key=lambda x: x.get("usage_count", 0), reverse=True)[:10]
        for i, p in enumerate(sorted_patterns, 1):
            report += f"{i}. **{p.get('name')}** - {p.get('category')} ({p.get('language')})\n"
            report += f"   Usage: {p.get('usage_count', 0)}, Success: {p.get('success_rate', 0):.0%}\n"
        
        return report


def main():
    import argparse
    parser = argparse.ArgumentParser(description="Enhanced Pattern Library")
    parser.add_argument("command", choices=["add", "list", "search", "stats", "report"])
    parser.add_argument("target", nargs="?", default=".")
    parser.add_argument("--name", help="Pattern name")
    parser.add_argument("--category", help="Pattern category")
    parser.add_argument("--language", default="python")
    parser.add_argument("--source", default="manual", choices=["manual", "ai", "github"])
    parser.add_argument("--code", help="Code example")
    parser.add_argument("--tags", help="Comma-separated tags")
    parser.add_argument("--json", action="store_true")
    args = parser.parse_args()
    
    library = EnhancedPatternLibrary(args.target)
    
    if args.command == "add":
        # 创建新模式
        pattern = Pattern(
            name=args.name or "Unknown",
            category=args.category or "general",
            language=args.language,
            description="User-defined pattern",
            code_example=args.code or "# Add code example",
            tags=args.tags.split(',') if args.tags else [],
            source=args.source
        )
        pattern_id = library.add_pattern(pattern, args.source)
        print(f"Added pattern: {pattern_id}")
    
    elif args.command == "list":
        patterns = library.patterns
        if args.category:
            patterns = [p for p in patterns if p.get("category") == args.category]
        print(json.dumps(patterns, indent=2))
    
    elif args.command == "search":
        code = sys.stdin.read() if not sys.stdin.isatty() else ""
        if code:
            similar = library.get_similar_patterns(code, args.language)
            print(json.dumps(similar, indent=2))
        else:
            print("Provide code to search for similar patterns")
    
    elif args.command == "stats":
        stats = library.get_statistics()
        if args.json:
            print(json.dumps(stats, indent=2))
        else:
            print(f"Total patterns: {stats['total_patterns']}")
            print(f"Total usages: {stats['total_usages']}")
            print(f"Avg success rate: {stats['average_success_rate']:.1%}")
    
    elif args.command == "report":
        print(library.generate_report())


if __name__ == "__main__":
    import sys
    main()
