#!/usr/bin/env python3
"""
Security Analysis Engine
基于 OWASP Top 10 的安全分析
"""

import re
import json
from pathlib import Path
from typing import List, Dict, Any
from dataclasses import dataclass, field


@dataclass
class SecurityFinding:
    """安全发现"""
    owasp_id: str
    cwe_id: str
    severity: str  # critical, high, medium, low
    category: str
    message: str
    line: int = 0
    suggestion: str = ""
    reference: str = ""
    
    def to_dict(self) -> dict:
        return {
            "owasp_id": self.owasp_id,
            "cwe_id": self.cwe_id,
            "severity": self.severity,
            "category": self.category,
            "message": self.message,
            "line": self.line,
            "suggestion": self.suggestion,
            "reference": self.reference
        }


@dataclass
class SecurityAnalysisResult:
    """安全分析结果"""
    filepath: str
    language: str
    findings: List[SecurityFinding] = field(default_factory=list)
    metrics: Dict[str, Any] = field(default_factory=dict)
    
    def to_dict(self) -> dict:
        return {
            "filepath": self.filepath,
            "language": self.language,
            "findings": [f.to_dict() for f in self.findings],
            "metrics": self.metrics
        }


class SecurityAnalyzer:
    """安全分析器 - OWASP Top 10 覆盖"""
    
    def __init__(self):
        self.rules = self._load_owasp_rules()
    
    def _load_owasp_rules(self) -> Dict[str, Dict]:
        """加载 OWASP Top 10 规则"""
        return {
            # A01:2021 - Broken Access Control
            "A01_001": {
                "owasp_id": "A01:2021",
                "cwe_id": "CWE-285",
                "severity": "high",
                "category": "Broken Access Control",
                "description": "Missing authorization check",
                "patterns": [r"def\s+\w+\s*\([^)]*\):\s*#?\s*no\s*auth", r"@app\.route\([^)]*\)\s*(?!.*@login_required)"],
                "suggestion": "Add authentication/authorization checks",
                "reference": "https://owasp.org/Top10/A01_2021-Broken_Access_Control/"
            },
            
            # A02:2021 - Cryptographic Failures
            "A02_001": {
                "owasp_id": "A02:2021",
                "cwe_id": "CWE-327",
                "severity": "critical",
                "category": "Cryptographic Failures",
                "description": "Weak encryption algorithm",
                "patterns": [r"\bMD5\b", r"\bDES\b", r"\bRC4\b", r"\bblowfish\b"],
                "suggestion": "Use AES-256-GCM or ChaCha20-Poly1305",
                "reference": "https://owasp.org/Top10/A02_2021-Cryptographic_Failures/"
            },
            "A02_002": {
                "owasp_id": "A02:2021",
                "cwe_id": "CWE-312",
                "severity": "critical",
                "category": "Cryptographic Failures",
                "description": "Hardcoded secret/key",
                "patterns": [r"(api_key|secret|password|token)\s*[:=]\s*['\"][^'\"]{8,}['\"]"],
                "suggestion": "Use environment variables or secret management",
                "reference": "https://owasp.org/Top10/A02_2021-Cryptographic_Failures/"
            },
            
            # A03:2021 - Injection
            "A03_001": {
                "owasp_id": "A03:2021",
                "cwe_id": "CWE-89",
                "severity": "critical",
                "category": "Injection",
                "description": "SQL injection risk",
                "patterns": [r"execute\s*\(\s*f?['\"].*%s", r"execute\s*\(\s*f?['\"].*\{", r"query\s*[:=]\s*f?['\"].*%s"],
                "suggestion": "Use parameterized queries",
                "reference": "https://owasp.org/Top10/A03_2021-Injection/"
            },
            "A03_002": {
                "owasp_id": "A03:2021",
                "cwe_id": "CWE-78",
                "severity": "critical",
                "category": "Injection",
                "description": "OS command injection",
                "patterns": [r"os\.system\s*\(", r"subprocess\.call\s*\(.*shell\s*=\s*True", r"\beval\s*\(", r"\bexec\s*\("],
                "suggestion": "Use safe alternatives (subprocess with args list, avoid eval/exec)",
                "reference": "https://owasp.org/Top10/A03_2021-Injection/"
            },
            "A03_003": {
                "owasp_id": "A03:2021",
                "cwe_id": "CWE-79",
                "severity": "high",
                "category": "Injection",
                "description": "XSS risk",
                "patterns": [r"\.innerHTML\s*=", r"document\.write\s*\(", r"React\.createElement\s*\(.*\{\{"],
                "suggestion": "Use escaped output or templating",
                "reference": "https://owasp.org/Top10/A03_2021-Injection/"
            },
            
            # A04:2021 - Insecure Design
            "A04_001": {
                "owasp_id": "A04:2021",
                "cwe_id": "CWE-639",
                "severity": "medium",
                "category": "Insecure Design",
                "description": "Direct object reference",
                "patterns": [r"/api/\w+/(\d+|{id})", r"request\.args\.get\(['\"]id['\"]\)"],
                "suggestion": "Use indirect references or access control",
                "reference": "https://owasp.org/Top10/A04_2021-Insecure_Design/"
            },
            
            # A05:2021 - Security Misconfiguration
            "A05_001": {
                "owasp_id": "A05:2021",
                "cwe_id": "CWE-284",
                "severity": "high",
                "category": "Security Misconfiguration",
                "description": "Debug mode in production",
                "patterns": [r"debug\s*=\s*True", r"app\.run\(.*debug\s*=\s*True"],
                "suggestion": "Disable debug mode in production",
                "reference": "https://owasp.org/Top10/A05_2021-Security_Misconfiguration/"
            },
            "A05_002": {
                "owasp_id": "A05:2021",
                "cwe_id": "CWE-1004",
                "severity": "medium",
                "category": "Security Misconfiguration",
                "description": "CORS too permissive",
                "patterns": [r"Access-Control-Allow-Origin\s*:\s*['\"]\*['\"]"],
                "suggestion": "Restrict CORS to specific origins",
                "reference": "https://owasp.org/Top10/A05_2021-Security_Misconfiguration/"
            },
            
            # A06:2021 - Vulnerable and Outdated Components
            "A06_001": {
                "owasp_id": "A06:2021",
                "cwe_id": "CWE-1104",
                "severity": "medium",
                "category": "Vulnerable Components",
                "description": "Check dependencies for known vulnerabilities",
                "patterns": [r"requirements\.txt", r"package\.json", r"go\.mod", r"Cargo\.toml"],
                "suggestion": "Run dependency scan (npm audit, pip-audit, go audit)",
                "reference": "https://owasp.org/Top10/A06_2021-Vulnerable_and_Outdated_Components/"
            },
            
            # A07:2021 - Identification and Authentication Failures
            "A07_001": {
                "owasp_id": "A07:2021",
                "cwe_id": "CWE-287",
                "severity": "high",
                "category": "Authentication Failures",
                "description": "Weak password policy",
                "patterns": [r"password\s*length\s*[<=>]+\s*\d+\s*(?!.*(?i)(8|10|12))", r"min_length\s*=\s*\d{1,2}"],
                "suggestion": "Require minimum 8 characters, mix of upper/lower/number/symbol",
                "reference": "https://owasp.org/Top10/A07_2021-Identification_and_Authentication_Failures/"
            },
            
            # A08:2021 - Software and Data Integrity Failures
            "A08_001": {
                "owasp_id": "A08:2021",
                "cwe_id": "CWE-829",
                "severity": "high",
                "category": "Integrity Failures",
                "description": "Insecure dependency installation",
                "patterns": [r"pip\s+install\s+.*--trusted-host", r"npm\s+install\s+.*--ignore-scripts\s*false"],
                "suggestion": "Use verified dependencies and check signatures",
                "reference": "https://owasp.org/Top10/A08_2021-Software_and_Data_Integrity_Failures/"
            },
            
            # A09:2021 - Security Logging and Monitoring Failures
            "A09_001": {
                "owasp_id": "A09:2021",
                "cwe_id": "CWE-778",
                "severity": "medium",
                "category": "Logging Failures",
                "description": "Missing security logging",
                "patterns": [r"pass\s*$", r"except\s*:\s*pass", r"try:\s*\n\s*.*\n\s*pass"],
                "suggestion": "Log security-relevant events",
                "reference": "https://owasp.org/Top10/A09_2021-Security_Logging_and_Monitoring_Failures/"
            },
            
            # A10:2021 - SSRF
            "A10_001": {
                "owasp_id": "A10:2021",
                "cwe_id": "CWE-918",
                "severity": "high",
                "category": "SSRF",
                "description": "Server-side request forgery",
                "patterns": [r"requests\.(get|post|put|delete)\s*\([^)]*url\s*=", r"fetch\s*\([^)]*\{.*url.*\}"],
                "suggestion": "Validate and sanitize URLs, use allowlist",
                "reference": "https://owasp.org/Top10/A10_2021-SSRF/"
            }
        }
    
    def analyze(self, filepath: str, language: str = "python") -> SecurityAnalysisResult:
        """分析文件安全漏洞"""
        result = SecurityAnalysisResult(filepath=filepath, language=language)
        
        try:
            with open(filepath, 'r', encoding='utf-8') as f:
                code = f.read()
        except Exception as e:
            result.findings.append(SecurityFinding(
                owasp_id="ERROR",
                cwe_id="CWE-0",
                severity="critical",
                category="Error",
                message=str(e)
            ))
            return result
        
        lines = code.split('\n')
        result.metrics = {
            "lines": len([l for l in lines if l.strip()]),
            "rules_checked": len(self.rules),
            "issues_found": 0
        }
        
        # 应用所有规则
        for rule_id, rule in self.rules.items():
            for pattern in rule.get("patterns", []):
                try:
                    regex = re.compile(pattern, re.IGNORECASE)
                    for i, line in enumerate(lines, 1):
                        if regex.search(line):
                            finding = SecurityFinding(
                                owasp_id=rule["owasp_id"],
                                cwe_id=rule["cwe_id"],
                                severity=rule["severity"],
                                category=rule["category"],
                                message=f"{rule['description']}: {line.strip()[:80]}",
                                line=i,
                                suggestion=rule["suggestion"],
                                reference=rule.get("reference", "")
                            )
                            result.findings.append(finding)
                            result.metrics["issues_found"] += 1
                except re.error:
                    pass  # Skip invalid patterns
        
        # 计算风险分数
        result.metrics["risk_score"] = self._calculate_risk_score(result.findings)
        
        return result
    
    def _calculate_risk_score(self, findings: List[SecurityFinding]) -> float:
        """计算风险分数 (0-100, 越高越危险)"""
        if not findings:
            return 0.0
        
        weights = {"critical": 25, "high": 15, "medium": 8, "low": 3}
        total = sum(weights.get(f.severity, 0) for f in findings)
        
        return min(100, total)
    
    def generate_report(self, result: SecurityAnalysisResult) -> str:
        """生成安全报告"""
        risk_level = "LOW"
        if result.metrics.get("risk_score", 0) > 70:
            risk_level = "CRITICAL"
        elif result.metrics.get("risk_score", 0) > 50:
            risk_level = "HIGH"
        elif result.metrics.get("risk_score", 0) > 30:
            risk_level = "MEDIUM"
        
        report = f"""# Security Analysis Report (OWASP Top 10 2021)

## File: {result.filepath}
**Language**: {result.language}
**Risk Level**: {risk_level}
**Risk Score**: {result.metrics.get('risk_score', 0):.0f}/100

## Summary
- Lines of Code: {result.metrics.get('lines', 0)}
- Rules Checked: {result.metrics.get('rules_checked', 0)}
- Issues Found: {result.metrics.get('issues_found', 0)}

"""
        
        if result.findings:
            report += "## Findings\n\n"
            
            # 按 OWASP 分类分组
            by_category = {}
            for finding in result.findings:
                if finding.category not in by_category:
                    by_category[finding.category] = []
                by_category[finding.category].append(finding)
            
            for category, findings in sorted(by_category.items()):
                report += f"### {category}\n\n"
                for finding in findings:
                    report += f"- **[{finding.owasp_id}]** {finding.cwe_id} (line {finding.line})\n"
                    report += f"  - {finding.message}\n"
                    if finding.suggestion:
                        report += f"  - Fix: {finding.suggestion}\n"
                    if finding.reference:
                        report += f"  - Ref: {finding.reference}\n"
                report += "\n"
        else:
            report += "✅ No security issues found!\n"
        
        return report


def main():
    import argparse
    parser = argparse.ArgumentParser(description="Security Analyzer (OWASP Top 10)")
    parser.add_argument("filepath", help="File to analyze")
    parser.add_argument("--language", default="python", help="Programming language")
    parser.add_argument("--json", action="store_true", help="JSON output")
    args = parser.parse_args()
    
    analyzer = SecurityAnalyzer()
    result = analyzer.analyze(args.filepath, args.language)
    
    if args.json:
        print(json.dumps(result.to_dict(), indent=2))
    else:
        print(analyzer.generate_report(result))


if __name__ == "__main__":
    main()
