#!/usr/bin/env python3
"""
STRIDE Threat Modeling Helper
帮助进行安全威胁建模分析
"""

import json
import re
import sys
from dataclasses import dataclass, field
from typing import Optional


@dataclass
class Threat:
    stride_type: str  # Spoofing, Tampering, Repudiation, Information Disclosure, DoS, Elevation
    description: str
    location: str
    mitigation: str
    severity: str  # high, medium, low


def analyze_threats(code: str, language: str = "unknown") -> list[Threat]:
    """基于代码内容分析 STRIDE 威胁"""
    threats = []

    # Spoofing: 认证相关
    if re.search(r'password|passwd|pwd|credential', code, re.IGNORECASE):
        if not re.search(r'hash|bcrypt|scrypt|argon2|sha256|sha512', code, re.IGNORECASE):
            threats.append(Threat(
                "Spoofing",
                "密码可能未加密存储",
                "密码处理区域",
                "使用 bcrypt/scrypt/argon2 哈希密码",
                "high"
            ))

    # Tampering: 输入验证
    if re.search(r'input|request\.body|req\.params|argv|args', code, re.IGNORECASE):
        if not re.search(r'validate|sanitize|escape|filter|allowlist|whitelist', code, re.IGNORECASE):
            threats.append(Threat(
                "Tampering",
                "用户输入可能未验证",
                "输入处理区域",
                "添加输入验证和 sanitization",
                "high"
            ))

    # SQL Injection
    if re.search(r'execute|query|fetch.*sql|db\.call', code, re.IGNORECASE):
        if re.search(r'f["\'].*(?:SELECT|INSERT|UPDATE|DELETE)|\.format\(|%s.*%|\.replace\(', code, re.IGNORECASE):
            threats.append(Threat(
                "Tampering",
                "可能存在 SQL 注入风险",
                "数据库查询区域",
                "使用参数化查询",
                "high"
            ))

    # XSS
    if re.search(r'innerHTML|document\.write|dangerouslySetInnerHTML|v-html', code, re.IGNORECASE):
        threats.append(Threat(
            "Tampering",
            "可能存在 XSS 漏洞",
            "DOM 操作区域",
            "使用框架自动转义或 DOMPurify",
            "high"
        ))

    # Information Disclosure
    if re.search(r'print|console\.log|logger\.(debug|info)|log\(', code):
        if re.search(r'password|token|secret|key|credit.?card|ssn', code, re.IGNORECASE):
            threats.append(Threat(
                "Information Disclosure",
                "敏感信息可能被记录到日志",
                "日志输出区域",
                "日志中脱敏敏感字段",
                "medium"
            ))

    # DoS
    if re.search(r'while.*True|for.*range.*inf|recursive|recursion', code, re.IGNORECASE):
        if not re.search(r'timeout|max.?iterations|limit', code, re.IGNORECASE):
            threats.append(Threat(
                "Denial of Service",
                "可能存在无限循环风险",
                "循环/递归区域",
                "添加超时和迭代次数限制",
                "medium"
            ))

    # Elevation of Privilege
    if re.search(r'admin|root|sudo|super.?user|permission|role', code, re.IGNORECASE):
        if not re.search(r'authorize|can_access|has_permission|rbac|abac', code, re.IGNORECASE):
            threats.append(Threat(
                "Elevation of Privilege",
                "权限检查可能缺失",
                "权限控制区域",
                "添加 RBAC/ABAC 权限校验",
                "high"
            ))

    return threats


def generate_threat_model_report(code: str, language: str = "unknown") -> str:
    """生成威胁建模报告"""
    threats = analyze_threats(code, language)

    report = f"""# STRIDE Threat Model Report

**Language**: {language}
**Analysis Time**: {__import__('datetime').datetime.now().strftime('%Y-%m-%d %H:%M:%S')}

## Summary
- Total threats identified: {len(threats)}
- High severity: {sum(1 for t in threats if t.severity == 'high')}
- Medium severity: {sum(1 for t in threats if t.severity == 'medium')}
- Low severity: {sum(1 for t in threats if t.severity == 'low')}

## Threats
"""

    if not threats:
        report += "\n✅ No obvious threats identified.\n"
    else:
        for i, t in enumerate(threats, 1):
            sev_emoji = "🔴" if t.severity == "high" else "🟡" if t.severity == "medium" else "🟢"
            report += f"""
### {sev_emoji} {i}. {t.stride_type}
- **Description**: {t.description}
- **Location**: {t.location}
- **Mitigation**: {t.mitigation}
"""

    report += """
## Next Steps
1. Review each threat and verify if it's a real risk
2. Implement mitigations before deploying
3. Re-run analysis after fixes
4. Consider a manual security audit for high-risk applications
"""

    return report


def main():
    import argparse
    parser = argparse.ArgumentParser(description="STRIDE Threat Modeling")
    parser.add_argument("input", help="Code file or stdin")
    parser.add_argument("--language", "-l", default="unknown", help="Programming language")
    parser.add_argument("--json", action="store_true", help="Output as JSON")
    args = parser.parse_args()

    if args.input == "-":
        code = sys.stdin.read()
    else:
        with open(args.input) as f:
            code = f.read()

    threats = analyze_threats(code, args.language)

    if args.json:
        print(json.dumps([
            {"type": t.stride_type, "description": t.description,
             "location": t.location, "mitigation": t.mitigation, "severity": t.severity}
            for t in threats
        ], indent=2))
    else:
        print(generate_threat_model_report(code, args.language))


if __name__ == "__main__":
    main()
