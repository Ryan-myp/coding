#!/usr/bin/env python3
"""Java Code Quality Analyzer (Rule-based)"""
import re, json
from dataclasses import dataclass, field
from typing import List, Dict, Any

@dataclass
class Finding:
    rule_id: str; severity: str; message: str; line: int = 0; suggestion: str = ""
    def to_dict(self): return {"rule_id": self.rule_id, "severity": self.severity, "message": self.message, "line": self.line, "suggestion": self.suggestion}

@dataclass
class JavaAnalysisResult:
    filepath: str; findings: List[Finding] = field(default_factory=list); metrics: Dict[str, Any] = field(default_factory=dict)
    def to_dict(self): return {"filepath": self.filepath, "findings": [f.to_dict() for f in self.findings], "metrics": self.metrics}

class JavaAnalyzer:
    def __init__(self):
        self.rules = {
            "JV001": {"severity": "high", "description": "Avoid System.out.println", "pattern": r"System\.out\.println", "suggestion": "Use logging framework"},
            "JV002": {"severity": "critical", "description": "No hardcoded passwords", "pattern": r"password\s*=\s*\"[^\"]+\"", "suggestion": "Use environment variables"},
            "JV003": {"severity": "high", "description": "Handle exceptions properly", "pattern": r"catch\s*\([^)]*\)\s*\{?\s*\}", "suggestion": "Log or handle exception"},
            "JV004": {"severity": "medium", "description": "Use try-with-resources", "pattern": r"new\s+(FileInputStream|BufferedReader|Connection)", "suggestion": "Use try-with-resources"},
            "JV005": {"severity": "low", "description": "Avoid raw types", "pattern": r"List\s+\w+\s*=", "suggestion": "Use generics: List<String>"},
        }
    
    def analyze(self, filepath: str) -> JavaAnalysisResult:
        result = JavaAnalysisResult(filepath=filepath)
        try:
            with open(filepath, 'r', encoding='utf-8') as f:
                code = f.read()
        except Exception as e:
            result.findings.append(Finding("ERROR", "critical", str(e))); return result
        
        lines = code.split('\n')
        result.metrics = {"lines_of_code": len([l for l in lines if l.strip()]), "classes": len(re.findall(r'\bclass\s+\w+', code))}
        
        for rule_id, rule in self.rules.items():
            for i, line in enumerate(lines, 1):
                if re.search(rule['pattern'], line):
                    result.findings.append(Finding(rule_id, rule['severity'], f"{rule['description']}: {line.strip()[:80]}", i, rule['suggestion']))
        
        result.metrics['score'] = max(0, 100 - sum({"critical": 25, "high": 15, "medium": 8, "low": 3}.get(f.severity, 0) for f in result.findings))
        return result
    
    def generate_report(self, result: JavaAnalysisResult) -> str:
        report = f"# Java Analysis Report\n\n## File: {result.filepath}\n\n**Score: {result.metrics.get('score', 0):.1f}/100**\n\n"
        if result.findings:
            report += "## Findings\n\n"
            for sev in ["critical", "high", "medium", "low"]:
                findings = [f for f in result.findings if f.severity == sev]
                if findings:
                    report += f"### {sev.upper()}\n\n"
                    for f in findings:
                        report += f"- **{f.rule_id}** (line {f.line}): {f.message}\n"
        else:
            report += "✅ No issues found!\n"
        return report

if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser(); parser.add_argument("filepath"); parser.add_argument("--json", action="store_true")
    args = parser.parse_args()
    analyzer = JavaAnalyzer(); result = analyzer.analyze(args.filepath)
    print(json.dumps(result.to_dict(), indent=2) if args.json else analyzer.generate_report(result))
