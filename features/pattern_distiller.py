#!/usr/bin/env python3
"""
Pattern Distiller
从成功代码中提取可复用的模式
"""

import json
import re
from pathlib import Path
from typing import List, Dict, Any
from dataclasses import dataclass, field


@dataclass
class Pattern:
    """代码模式"""
    id: str
    name: str
    category: str  # error-handling, architecture, security, performance
    language: str
    description: str
    code_example: str
    anti_pattern: str = ""
    tags: List[str] = field(default_factory=list)
    quality_score: float = 0.0
    
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
            "quality_score": self.quality_score
        }


class PatternDistiller:
    """模式蒸馏器"""
    
    def __init__(self, project_dir: str = "."):
        self.project_dir = Path(project_dir)
        self.library_file = self.project_dir / ".qguard" / "patterns" / "library.json"
        self.library_file.parent.mkdir(parents=True, exist_ok=True)
        self.patterns = self._load_library()
    
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
    
    def distill_from_code(self, code: str, language: str, quality_score: float = 80) -> List[Pattern]:
        """从代码中蒸馏模式"""
        patterns = []
        
        # 错误处理模式
        if re.search(r'try:\s*\n.*except\s+\w+\s+as\s+\w+', code, re.MULTILINE):
            patterns.append(Pattern(
                id=f"err-hand-{len(self.patterns)}",
                name="Proper Error Handling",
                category="error-handling",
                language=language,
                description="Using specific exception types with proper handling",
                code_example=self._extract_pattern_block(code, r'try:\s*\n.*except'),
                tags=["error", "exception", "best-practice"]
            ))
        
        # 类型注解模式
        if re.search(r'def\s+\w+\s*\([^)]*\)\s*->\s*\w+', code):
            patterns.append(Pattern(
                id=f"type-ann-{len(self.patterns)}",
                name="Type Annotations",
                category="type-safety",
                language=language,
                description="Using type hints for better code clarity",
                code_example=self._extract_pattern_block(code, r'def\s+\w+\s*\(.*\)\s*->'),
                tags=["type-hint", "typing", "clarity"]
            ))
        
        # 上下文管理模式
        if re.search(r'with\s+\w+\s+as\s+\w+', code):
            patterns.append(Pattern(
                id=f"ctx-mgr-{len(self.patterns)}",
                name="Context Manager",
                category="resource-management",
                language=language,
                description="Using context managers for resource cleanup",
                code_example=self._extract_pattern_block(code, r'with\s+\w+'),
                tags=["context", "resource", "cleanup"]
            ))
        
        # 异步模式
        if re.search(r'async\s+def', code):
            patterns.append(Pattern(
                id=f"async-{len(self.patterns)}",
                name="Async Pattern",
                category="concurrency",
                language=language,
                description="Using async/await for asynchronous operations",
                code_example=self._extract_pattern_block(code, r'async\s+def'),
                tags=["async", "await", "concurrency"]
            ))
        
        return patterns
    
    def _extract_pattern_block(self, code: str, pattern: str) -> str:
        """提取模式代码块"""
        matches = re.findall(pattern, code)
        if matches:
            # 返回第一个匹配的代码块（简化版）
            idx = code.find(matches[0])
            if idx >= 0:
                block = code[idx:idx+200]
                return block + "..." if len(block) > 200 else block
        return code[:200]
    
    def distill_directory(self, directory: str, min_score: float = 80) -> List[Pattern]:
        """从目录蒸馏模式"""
        all_patterns = []
        
        for filepath in Path(directory).rglob("*.py"):
            try:
                with open(filepath) as f:
                    code = f.read()
                
                # 简单质量评估（实际应该用分析器）
                score = self._estimate_quality(code)
                
                if score >= min_score:
                    patterns = self.distill_from_code(code, "python", score)
                    all_patterns.extend(patterns)
            except:
                pass
        
        return all_patterns
    
    def _estimate_quality(self, code: str) -> float:
        """估算代码质量"""
        score = 100
        
        # 扣分项
        if 'eval(' in code:
            score -= 30
        if 'exec(' in code:
            score -= 30
        if re.search(r'except\s*:', code):
            score -= 10
        if 'import *' in code:
            score -= 15
        if len(code) > 10000:
            score -= 10
        
        return max(0, score)
    
    def add_pattern(self, pattern: Pattern):
        """添加模式到库"""
        # 检查是否已存在
        for existing in self.patterns:
            if existing.get("name") == pattern.name and existing.get("language") == pattern.language:
                # 更新现有模式
                for i, p in enumerate(self.patterns):
                    if p.get("name") == pattern.name:
                        self.patterns[i] = pattern.to_dict()
                        break
                return
        
        self.patterns.append(pattern.to_dict())
        self._save_library()
    
    def get_patterns(self, category: str = None, language: str = None, tags: List[str] = None) -> List[Dict]:
        """获取模式"""
        results = self.patterns
        
        if category:
            results = [p for p in results if p.get("category") == category]
        if language:
            results = [p for p in results if p.get("language") == language]
        if tags:
            results = [p for p in results if any(t in p.get("tags", []) for t in tags)]
        
        return results
    
    def generate_report(self) -> str:
        """生成模式库报告"""
        report = f"""# Pattern Library Report

Total Patterns: {len(self.patterns)}

## By Category
"""
        
        categories = {}
        for p in self.patterns:
            cat = p.get("category", "unknown")
            categories[cat] = categories.get(cat, 0) + 1
        
        for cat, count in sorted(categories.items()):
            report += f"- {cat}: {count}\n"
        
        report += "\n## Recent Patterns\n"
        for p in self.patterns[-5:]:
            report += f"- **{p.get('name')}** ({p.get('language')})\n"
        
        return report


def main():
    import argparse
    parser = argparse.ArgumentParser(description="Pattern Distiller")
    parser.add_argument("command", choices=["distill", "add", "list", "report"])
    parser.add_argument("target", nargs="?", default=".")
    parser.add_argument("--language", default="python")
    parser.add_argument("--category", help="Filter by category")
    parser.add_argument("--min-score", type=float, default=80)
    args = parser.parse_args()
    
    distiller = PatternDistiller(args.target)
    
    if args.command == "distill":
        patterns = distiller.distill_directory(args.target, args.min_score)
        print(json.dumps([p.to_dict() for p in patterns], indent=2))
    
    elif args.command == "list":
        patterns = distiller.get_patterns(args.category)
        print(json.dumps(patterns, indent=2))
    
    elif args.command == "report":
        print(distiller.generate_report())


if __name__ == "__main__":
    main()
