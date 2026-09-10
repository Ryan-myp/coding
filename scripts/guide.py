#!/usr/bin/env python3
"""
Agent Code Generation Guide
指导 AI agent 生成一致、高质量的代码
"""

import json
import re
import sys
from pathlib import Path
from typing import Dict, List, Optional, Any
from dataclasses import dataclass, field, asdict


@dataclass
class GenerationContext:
    """代码生成上下文"""
    intent: str = "feature"
    project_type: str = "general"
    language: str = "python"
    framework: str = ""
    team_size: str = "unknown"
    security_level: str = "standard"
    performance_required: bool = False
    conventions: Dict[str, Any] = field(default_factory=dict)
    patterns: List[str] = field(default_factory=list)


@dataclass
class GenerationGuide:
    """生成指南"""
    context: GenerationContext
    rules: List[Dict] = field(default_factory=list)
    suggestions: List[str] = field(default_factory=list)
    anti_patterns: List[str] = field(default_factory=list)
    
    def to_prompt(self) -> str:
        """生成 agent 可用的 prompt"""
        prompt = f"""# Code Generation Guide

## Intent: {self.context.intent}
## Project: {self.context.project_type} ({self.context.language})

## Conventions to Follow:
"""
        for rule in self.rules:
            prompt += f"- {rule['name']}: {rule['description']}\n"
        
        if self.suggestions:
            prompt += "\n## Suggestions:\n"
            for s in self.suggestions:
                prompt += f"- {s}\n"
        
        if self.anti_patterns:
            prompt += "\n## Anti-Patterns to Avoid:\n"
            for a in self.anti_patterns:
                prompt += f"- ❌ {a}\n"
        
        return prompt


class CodeGenerationGuide:
    """代码生成引导器"""
    
    def __init__(self, project_dir: str = "."):
        self.project_dir = Path(project_dir)
        self.context = GenerationContext()
        self.patterns = self._load_patterns()
        self.conventions = self._load_conventions()
    
    def _load_patterns(self) -> Dict[str, List[Dict]]:
        """加载模式库"""
        patterns_file = self.project_dir / ".qguard" / "patterns.json"
        if patterns_file.exists():
            with open(patterns_file) as f:
                return json.load(f)
        return {}
    
    def _load_conventions(self) -> Dict[str, Any]:
        """加载团队约定"""
        conv_file = self.project_dir / "CONVENTIONS.md"
        if conv_file.exists():
            with open(conv_file) as f:
                return {"custom": f.read()}
        return {}
    
    def prepare(self, intent: str, language: str = "python") -> GenerationGuide:
        """准备生成上下文"""
        self.context.intent = intent
        self.context.language = language
        
        # 检测项目类型
        self.context.project_type = self._detect_project_type()
        self.context.framework = self._detect_framework()
        
        # 生成规则
        rules = self._generate_rules(intent, language)
        suggestions = self._generate_suggestions(intent, language)
        anti_patterns = self._get_anti_patterns(language)
        
        return GenerationGuide(
            context=self.context,
            rules=rules,
            suggestions=suggestions,
            anti_patterns=anti_patterns
        )
    
    def _detect_project_type(self) -> str:
        """检测项目类型"""
        files = list(self.project_dir.glob("*"))
        
        if any(f.name.endswith('.py') for f in files):
            if any(f.name in ['requirements.txt', 'pyproject.toml'] for f in files):
                return "backend"
        if any(f.name.endswith('.ts') or f.name.endswith('.tsx') for f in files):
            if any(f.name in ['package.json'] for f in files):
                return "frontend"
        if any(f.name.endswith('.go') for f in files):
            return "backend"
        
        return "general"
    
    def _detect_framework(self) -> str:
        """检测框架"""
        files = list(self.project_dir.glob("*"))
        
        for f in files:
            content = f.read_text()[:1000] if f.is_file() else ""
            if 'flask' in content.lower():
                return "flask"
            if 'django' in content.lower():
                return "django"
            if 'fastapi' in content.lower():
                return "fastapi"
            if 'react' in content.lower():
                return "react"
            if 'vue' in content.lower():
                return "vue"
        
        return ""
    
    def _generate_rules(self, intent: str, language: str) -> List[Dict]:
        """生成规则"""
        rules_map = {
            "python": {
                "feature": [
                    {"name": "Type Hints", "description": "Use type hints for all function parameters and returns"},
                    {"name": "Error Handling", "description": "Use specific exceptions, not bare except"},
                    {"name": "Docstrings", "description": "Add docstrings to public functions"},
                    {"name": "SOLID", "description": "Follow SOLID principles"},
                ],
                "fix": [
                    {"name": "Root Cause", "description": "Fix root cause, not symptom"},
                    {"name": "Test First", "description": "Write regression test before fix"},
                    {"name": "Minimal Change", "description": "Make minimal changes to fix"},
                ],
                "refactor": [
                    {"name": "Preserve Behavior", "description": "Don't change external behavior"},
                    {"name": "Small Steps", "description": "Refactor in small increments"},
                    {"name": "Test Coverage", "description": "Ensure tests pass after each step"},
                ],
            },
            "typescript": {
                "feature": [
                    {"name": "Strict Types", "description": "No 'any' types, use strict mode"},
                    {"name": "Error Boundaries", "description": "Handle errors in components"},
                    {"name": "Async/Await", "description": "Use async/await, not raw promises"},
                ],
                "fix": [
                    {"name": "Type Safety", "description": "Maintain type safety after fix"},
                    {"name": "Regression Test", "description": "Add test for the bug"},
                ],
            },
            "go": {
                "feature": [
                    {"name": "Error Return", "description": "Return errors, don't panic"},
                    {"name": "Context", "description": "Use context.Context for cancellation"},
                    {"name": "Interface Segregation", "description": "Small, focused interfaces"},
                ],
            },
        }
        
        lang_rules = rules_map.get(language, rules_map.get("python", []))
        intent_rules = lang_rules.get(intent, lang_rules.get("feature", []))
        
        return intent_rules
    
    def _generate_suggestions(self, intent: str, language: str) -> List[str]:
        """生成建议"""
        suggestions = {
            "python": {
                "feature": [
                    "Use dependency injection for testability",
                    "Follow PEP 8 naming conventions",
                    "Use list comprehensions over map/filter",
                    "Prefer pathlib over os.path",
                ],
                "fix": [
                    "Check existing tests before modifying",
                    "Run linter after fix",
                ],
            },
            "typescript": {
                "feature": [
                    "Use discriminated unions for state",
                    " Prefer interfaces over type aliases for objects",
                    "Use optional chaining (?.) and nullish coalescing (??)",
                ],
            },
        }
        
        return suggestions.get(language, {}).get(intent, [])
    
    def _get_anti_patterns(self, language: str) -> List[str]:
        """获取反模式"""
        anti_patterns = {
            "python": [
                "God functions (>50 lines)",
                "Global mutable state",
                "Catching broad exceptions",
                "Deeply nested conditionals",
                "Magic numbers/strings",
            ],
            "typescript": [
                "Using 'any' type",
                "Callback hell",
                "Unbounded recursion",
                "Mutating props directly",
            ],
            "go": [
                "Ignoring errors",
                "Using panic for error handling",
                "Global variables",
                "Missing context propagation",
            ],
        }
        
        return anti_patterns.get(language, anti_patterns.get("python", []))
    
    def review(self, code: str, language: str = "python") -> Dict:
        """审查生成的代码"""
        issues = []
        
        # 基本检查
        lines = code.split('\n')
        
        # 检查反模式
        for i, line in enumerate(lines, 1):
            if language == "python":
                if re.search(r'\bexcept\s*:', line):
                    issues.append({"line": i, "type": "anti-pattern", "message": "Bare except clause"})
                if re.search(r'\bimport\s+\*\s*', line):
                    issues.append({"line": i, "type": "anti-pattern", "message": "Wildcard import"})
                if len(line) > 120:
                    issues.append({"line": i, "type": "style", "message": "Line too long (>120 chars)"})
            
            if language == "typescript":
                if re.search(r':\s*any\b', line):
                    issues.append({"line": i, "type": "anti-pattern", "message": "Using 'any' type"})
                if re.search(r'\.subscribe\s*\(', line) and 'unsubscribe' not in code.lower():
                    issues.append({"line": i, "type": "warning", "message": "Missing subscription cleanup"})
        
        # 计算质量分数
        score = max(0, 100 - len(issues) * 10)
        
        return {
            "score": score,
            "issues": issues,
            "line_count": len([l for l in lines if l.strip()]),
            "recommendation": "Pass" if score >= 70 else "Needs Review"
        }
    
    def distill(self, source_code: str, label: str = "good") -> Dict:
        """蒸馏模式"""
        patterns = {
            "label": label,
            "patterns": [],
            "metrics": {}
        }
        
        # 简单模式提取
        lines = source_code.split('\n')
        
        # 统计指标
        patterns["metrics"] = {
            "lines": len([l for l in lines if l.strip()]),
            "functions": len(re.findall(r'def\s+\w+', source_code)) if self.context.language == "python" else 0,
            "classes": len(re.findall(r'class\s+\w+', source_code)),
        }
        
        # 提取常见模式
        if re.search(r'def\s+\w+\s*\([^)]*->\s*\w+', source_code):
            patterns["patterns"].append("type_hints")
        if re.search(r'try:\s*\n.*except\s+\w+', source_code, re.MULTILINE):
            patterns["patterns"].append("error_handling")
        if re.search(r'async\s+def', source_code):
            patterns["patterns"].append("async_patterns")
        
        return patterns


def main():
    import argparse
    parser = argparse.ArgumentParser(description="Agent Code Generation Guide")
    parser.add_argument("command", choices=["prepare", "review", "distill", "learn"])
    parser.add_argument("target", nargs="?", default=".")
    parser.add_argument("--intent", help="Generation intent")
    parser.add_argument("--language", default="python")
    parser.add_argument("--json", action="store_true")
    args = parser.parse_args()
    
    guide = CodeGenerationGuide(args.target)
    
    if args.command == "prepare":
        intent = args.intent or "feature"
        result = guide.prepare(intent, args.language)
        if args.json:
            print(json.dumps({
                "context": asdict(result.context),
                "rules": result.rules,
                "suggestions": result.suggestions,
                "anti_patterns": result.anti_patterns
            }, indent=2))
        else:
            print(result.to_prompt())
    
    elif args.command == "review":
        try:
            with open(args.target) as f:
                code = f.read()
        except:
            code = args.target
        result = guide.review(code, args.language)
        print(json.dumps(result, indent=2))
    
    elif args.command == "distill":
        with open(args.target) as f:
            code = f.read()
        result = guide.distill(code)
        print(json.dumps(result, indent=2))
    
    elif args.command == "learn":
        print("Learning from feedback...")
        # 实际学习逻辑在这里


if __name__ == "__main__":
    main()
