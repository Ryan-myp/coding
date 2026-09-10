#!/usr/bin/env python3
"""
Go Code Quality Analyzer
分析 Go 代码质量问题
"""

import re
import json
from pathlib import Path
from typing import List, Dict, Any
from dataclasses import dataclass, field


@dataclass
class Finding:
    rule_id: str
    severity: str
    message: str
    line: int = 0
    suggestion: str = ""
    
    def to_dict(self) -> dict:
        return {
            "rule_id": self.rule_id,
            "severity": self.severity,
            "message": self.message,
            "line": self.line,
            "suggestion": self.suggestion
        }


@dataclass
class GoAnalysisResult:
    filepath: str
    findings: List[Finding] = field(default_factory=list)
    metrics: Dict[str, Any] = field(default_factory=dict)
    
    def to_dict(self) -> dict:
        return {
            "filepath": self.filepath,
            "findings": [f.to_dict() for f in self.findings],
            "metrics": self.metrics
        }


class GoAnalyzer:
    """Go 代码质量分析器"""
    
    def __init__(self):
        self.rules = self._load_rules()
    
    def _load_rules(self) -> Dict[str, Dict]:
        return {
            "GO001": {
                "severity": "high",
                "description": "Avoid fmt.Printf in production",
                "pattern": r"\bfmt\.(Print|Println|Printf)\s*\(",
                "suggestion": "Use a proper logging library"
            },
            "GO002": {
                "severity": "critical",
                "description": "Handle errors explicitly",
                "pattern": r"\berr\s*[:=]\s*.*\b(?:Wrap|Errorf|fmt\.Errorf)\b",
                "suggestion": "Always handle errors, don't ignore them"
            },
            "GO003": {
                "severity": "high",
                "description": "Avoid bare panic()",
                "pattern": r"\bpanic\s*\(",
                "suggestion": "Return errors instead of panicking"
            },
            "GO004": {
                "severity": "medium",
                "description": "Use context for cancellation",
                "pattern": r"func\s+\w+\s*\([^)]*\)\s*(\w+\s*,\s*)?\s*\{",
                "suggestion": "Consider adding context.Context as first parameter"
            },
            "GO005": {
                "severity": "critical",
                "description": "No hardcoded secrets",
                "pattern": r"(password|secret|api_key|token)\s*[:=]\s*\"[^\"]+\"",
                "suggestion": "Use environment variables or secret management"
            },
            "GO006": {
                "severity": "medium",
                "description": "Defer close for resources",
                "pattern": r":=\s*os\.Open\(|:=\s*filepath\.Open\(",
                "suggestion": "Add defer file.Close() after opening files"
            },
            "GO007": {
                "severity": "low",
                "description": "Check return values",
                "pattern": r"\w+\([^)]*\)\s*;",
                "suggestion": "Consider checking return values"
            }
        }
    
    def analyze(self, filepath: str) -> GoAnalysisResult:
        """分析 Go 文件"""
        result = GoAnalysisResult(filepath=filepath)
        
        try:
            with open(filepath, 'r', encoding='utf-8') as f:
                code = f.read()
        except Exception as e:
            result.findings.append(Finding(
                rule_id="ERROR",
                severity="critical",
                message=str(e)
            ))
            return result
        
        lines = code.split('\n')
        result.metrics = {
            "lines_of_code": len([l for l in lines if l.strip()]),
            "functions": len(re.findall(r'\bfunc\s+\w+\b', code)),
            "structs": len(re.findall(r'\btype\s+\w+\s+struct\b', code)),
            "interfaces": len(re.findall(r'\btype\s+\w+\s+interface\b', code)),
            "imports": len(re.findall(r'^\s*"[^"]+"', code, re.MULTILINE))
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
        
        # 计算评分
        result.metrics['score'] = self._calculate_score(result.findings)
        
        return result
    
    def _calculate_score(self, findings: List[Finding]) -> float:
        penalties = {"critical": 25, "high": 15, "medium": 8, "low": 3}
        total_penalty = sum(penalties.get(f.severity, 0) for f in findings)
        return max(0, 100 - total_penalty)
    
    def generate_report(self, result: GoAnalysisResult) -> str:
        report = f"""# Go Analysis Report

## File: {result.filepath}

## Metrics
- Lines of Code: {result.metrics.get('lines_of_code', 0)}
- Functions: {result.metrics.get('functions', 0)}
- Structs: {result.metrics.get('structs', 0)}
- Interfaces: {result.metrics.get('interfaces', 0)}
- Imports: {result.metrics.get('imports', 0)}
- **Quality Score: {result.metrics.get('score', 0):.1f}/100**

"""
        
        if result.findings:
            report += "## Findings\n\n"
            by_severity = {}
            for finding in result.findings:
                if finding.severity not in by_severity:
                    by_severity[finding.severity] = []
                by_severity[finding.severity].append(finding)
            
            for severity in ["critical", "high", "medium", "low"]:
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
    parser = argparse.ArgumentParser(description="Go Code Analyzer")
    parser.add_argument("filepath", help="Go file to analyze")
    parser.add_argument("--json", action="store_true")
    args = parser.parse_args()
    
    analyzer = GoAnalyzer()
    result = analyzer.analyze(args.filepath)
    
    if args.json:
        print(json.dumps(result.to_dict(), indent=2))
    else:
        print(analyzer.generate_report(result))


if __name__ == "__main__":
    main()
