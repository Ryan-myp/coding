#!/usr/bin/env python3
"""
TypeScript AST Analyzer
分析 TypeScript/JavaScript 代码质量问题
"""

import ast
import json
import re
from pathlib import Path
from typing import List, Dict, Optional, Any
from dataclasses import dataclass, field, asdict


@dataclass
class Finding:
    """质量问题发现"""
    rule_id: str
    severity: str  # critical, high, medium, low, info
    message: str
    line: int = 0
    column: int = 0
    suggestion: str = ""
    category: str = "general"
    
    def to_dict(self) -> dict:
        return {
            "rule_id": self.rule_id,
            "severity": self.severity,
            "message": self.message,
            "line": self.line,
            "column": self.column,
            "suggestion": self.suggestion,
            "category": self.category
        }


@dataclass
class TSAnalysisResult:
    """TypeScript 分析结果"""
    filepath: str
    language: str = "typescript"
    findings: List[Finding] = field(default_factory=list)
    metrics: Dict[str, Any] = field(default_factory=dict)
    
    def to_dict(self) -> dict:
        return {
            "filepath": self.filepath,
            "language": self.language,
            "findings": [f.to_dict() for f in self.findings],
            "metrics": self.metrics
        }


class TypeScriptAnalyzer:
    """TypeScript 代码质量分析器"""
    
    def __init__(self):
        self.rules = self._load_rules()
    
    def _load_rules(self) -> Dict[str, Dict]:
        """加载规则定义"""
        return {
            "TS001": {
                "name": "no-any",
                "severity": "high",
                "description": "Avoid using 'any' type",
                "pattern": r"\bany\b",
                "suggestion": "Use specific types or generics instead of 'any'"
            },
            "TS002": {
                "name": "no-console",
                "severity": "medium",
                "description": "Avoid console.log in production",
                "pattern": r"console\.(log|warn|error|info)",
                "suggestion": "Use a proper logging library"
            },
            "TS003": {
                "name": "no-eval",
                "severity": "critical",
                "description": "Avoid eval() for security",
                "pattern": r"\beval\s*\(",
                "suggestion": "Use JSON.parse() or safe alternatives"
            },
            "TS004": {
                "name": "no-hardcoded-secret",
                "severity": "critical",
                "description": "No hardcoded secrets",
                "pattern": r"(password|secret|api_key|apikey|token)\s*[:=]\s*['\"][^'\"]+['\"]",
                "suggestion": "Use environment variables or secret management"
            },
            "TS005": {
                "name": "require-await",
                "severity": "medium",
                "description": "Async functions should use await",
                "pattern": r"async\s+\w+\s*\([^)]*\)\s*[^{]*\{[^}]*\}(?!\s*.*\bawait\b)",
                "suggestion": "Add await or remove async keyword"
            },
            "TS006": {
                "name": "no-unused-vars",
                "severity": "low",
                "description": "Remove unused variables",
                "pattern": r"const\s+(\w+)\s*=",
                "suggestion": "Remove unused variable or use it"
            },
            "TS007": {
                "name": "prefer-const",
                "severity": "low",
                "description": "Prefer const over let",
                "pattern": r"\blet\s+\w+\s*=",
                "suggestion": "Use const unless you need to reassign"
            },
            "TS008": {
                "name": "no-string-literal",
                "severity": "low",
                "description": "Use constants for string literals",
                "pattern": r"['\"][a-zA-Z_][a-zA-Z0-9_]*['\"]\s*[:(]",
                "suggestion": "Extract string literal to a named constant"
            }
        }
    
    def analyze(self, filepath: str) -> TSAnalysisResult:
        """分析 TypeScript/JavaScript 文件"""
        result = TSAnalysisResult(filepath=filepath)
        
        try:
            with open(filepath, 'r', encoding='utf-8') as f:
                code = f.read()
        except Exception as e:
            result.findings.append(Finding(
                rule_id="ERROR",
                severity="critical",
                message=f"Failed to read file: {e}"
            ))
            return result
        
        lines = code.split('\n')
        result.metrics = {
            "lines_of_code": len([l for l in lines if l.strip()]),
            "characters": len(code),
            "functions": len(re.findall(r'\bfunction\s+\w+\b', code)),
            "classes": len(re.findall(r'\bclass\s+\w+\b', code)),
            "imports": len(re.findall(r'\bimport\b', code))
        }
        
        # 应用规则
        for rule_id, rule in self.rules.items():
            pattern = re.compile(rule['pattern'])
            for i, line in enumerate(lines, 1):
                if pattern.search(line):
                    result.findings.append(Finding(
                        rule_id=rule_id,
                        severity=rule['severity'],
                        message=f"{rule['description']}: {line.strip()[:80]}",
                        line=i,
                        suggestion=rule['suggestion']
                    ))
        
        # 计算综合评分
        result.metrics['score'] = self._calculate_score(result.findings)
        
        return result
    
    def _calculate_score(self, findings: List[Finding]) -> float:
        """计算质量评分 (0-100)"""
        if not findings:
            return 100.0
        
        penalties = {
            "critical": 20,
            "high": 10,
            "medium": 5,
            "low": 2,
            "info": 1
        }
        
        total_penalty = sum(
            penalties.get(f.severity, 0) for f in findings
        )
        
        return max(0, 100 - total_penalty)
    
    def generate_report(self, result: TSAnalysisResult) -> str:
        """生成报告"""
        report = f"""# TypeScript Analysis Report

## File: {result.filepath}

## Metrics
- Lines of Code: {result.metrics.get('lines_of_code', 0)}
- Functions: {result.metrics.get('functions', 0)}
- Classes: {result.metrics.get('classes', 0)}
- Imports: {result.metrics.get('imports', 0)}
- **Quality Score: {result.metrics.get('score', 0):.1f}/100**

"""
        
        if result.findings:
            report += "## Findings\n\n"
            
            # 按严重程度分组
            by_severity = {}
            for finding in result.findings:
                if finding.severity not in by_severity:
                    by_severity[finding.severity] = []
                by_severity[finding.severity].append(finding)
            
            for severity in ["critical", "high", "medium", "low", "info"]:
                if severity in by_severity:
                    report += f"### {severity.upper()}\n\n"
                    for finding in by_severity[severity]:
                        report += f"- **{finding.rule_id}** (line {finding.line}): {finding.message}\n"
                        if finding.suggestion:
                            report += f"  - Suggestion: {finding.suggestion}\n"
                    report += "\n"
        else:
            report += "✅ No issues found!\n"
        
        return report


def main():
    import argparse
    parser = argparse.ArgumentParser(description="TypeScript Code Analyzer")
    parser.add_argument("filepath", help="TypeScript/JavaScript file to analyze")
    parser.add_argument("--json", action="store_true", help="Output JSON")
    args = parser.parse_args()
    
    analyzer = TypeScriptAnalyzer()
    result = analyzer.analyze(args.filepath)
    
    if args.json:
        print(json.dumps(result.to_dict(), indent=2))
    else:
        print(analyzer.generate_report(result))


if __name__ == "__main__":
    main()
