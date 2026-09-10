#!/usr/bin/env python3
"""
C# Code Analyzer
分析 C# 代码质量
"""

import re
from typing import List, Dict, Any
from dataclasses import dataclass, field


@dataclass
class Finding:
    """发现问题"""
    rule_id: str
    severity: str  # error, warning, info
    message: str
    line: int = 0
    code: str = ""
    
    def to_dict(self) -> dict:
        return {
            "rule_id": self.rule_id,
            "severity": self.severity,
            "message": self.message,
            "line": self.line,
            "code": self.code[:100] if self.code else ""
        }


class CSharpAnalyzer:
    """C# 代码分析器"""
    
    def __init__(self):
        self.rules = self._load_rules()
    
    def _load_rules(self) -> List[Dict]:
        """加载分析规则"""
        return [
            {
                "id": "CS001",
                "name": "No Magic Numbers",
                "severity": "warning",
                "pattern": r"\b\d{2,}\b(?!.*['\"])"
            },
            {
                "id": "CS002",
                "name": "Use Proper Exception Types",
                "severity": "error",
                "pattern": r"catch\s*\(\s*Exception\s+\w+\s*\)"
            },
            {
                "id": "CS003",
                "name": "Async Method Naming",
                "severity": "warning",
                "pattern": r"async\s+\w+\s+\w+.*?(?<!Async)\s*\("
            },
            {
                "id": "CS004",
                "name": "No Object.Equals without Override",
                "severity": "info",
                "pattern": r"\.Equals\s*\("
            },
            {
                "id": "CS005",
                "name": "Use Using Statement",
                "severity": "warning",
                "pattern": r"new\s+\w+.*?(?<!using\s)"
            },
            {
                "id": "CS006",
                "name": "Avoid Global State",
                "severity": "error",
                "pattern": r"static\s+\w+\s+\w+\s*="
            },
            {
                "id": "CS007",
                "name": "Proper XML Comments",
                "severity": "info",
                "pattern": r"///\s+\w"
            },
        ]
    
    def analyze(self, code: str, filepath: str = "") -> Dict[str, Any]:
        """分析代码"""
        findings = []
        lines = code.split('\n')
        
        for rule in self.rules:
            for i, line in enumerate(lines, 1):
                if re.search(rule["pattern"], line):
                    finding = Finding(
                        rule_id=rule["id"],
                        severity=rule["severity"],
                        message=rule["name"],
                        line=i,
                        code=line.strip()
                    )
                    findings.append(finding)
        
        # 计算质量分数
        score = self._calculate_score(findings)
        
        return {
            "filepath": filepath,
            "language": "csharp",
            "score": score,
            "findings": [f.to_dict() for f in findings],
            "summary": {
                "errors": len([f for f in findings if f.severity == "error"]),
                "warnings": len([f for f in findings if f.severity == "warning"]),
                "infos": len([f for f in findings if f.severity == "info"])
            }
        }
    
    def _calculate_score(self, findings: List[Finding]) -> int:
        """计算质量分数"""
        score = 100
        for f in findings:
            if f.severity == "error":
                score -= 10
            elif f.severity == "warning":
                score -= 5
            else:
                score -= 2
        return max(0, min(100, score))
    
    def generate_report(self, result: Dict) -> str:
        """生成报告"""
        report = f"""# C# Code Analysis Report

## Summary
- File: {result.get('filepath', 'unknown')}
- Language: {result.get('language', 'csharp')}
- Score: {result.get('score', 0)}/100

## Findings
"""
        for f in result.get("findings", []):
            icon = "🔴" if f["severity"] == "error" else "🟡" if f["severity"] == "warning" else "⚪"
            report += f"{icon} Line {f['line']}: {f['message']}\n"
            if f.get("code"):
                report += f"   ```\n   {f['code']}\n   ```\n"
        
        return report


def main():
    import argparse
    parser = argparse.ArgumentParser(description="C# Code Analyzer")
    parser.add_argument("target", help="File or directory to analyze")
    parser.add_argument("--json", action="store_true")
    args = parser.parse_args()
    
    analyzer = CSharpAnalyzer()
    
    try:
        with open(args.target) as f:
            code = f.read()
        result = analyzer.analyze(code, args.target)
        
        if args.json:
            print(__import__('json').dumps(result, indent=2))
        else:
            print(analyzer.generate_report(result))
    except FileNotFoundError:
        print(f"Error: File not found: {args.target}")
    except Exception as e:
        print(f"Error: {e}")


if __name__ == "__main__":
    main()
