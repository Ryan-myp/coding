#!/usr/bin/env python3
"""STRIDE 威胁建模器 — 自动化安全威胁分析"""

import json
import re
import sys
from dataclasses import dataclass, field, asdict
from pathlib import Path
from typing import Optional


STRIDE_CATEGORIES = {
    "spoofing": {
        "name": "Spoofing (身份伪造)",
        "checks": [
            (r'(?i)(token|secret|password|key)\s*[=:]\s*["\']?[a-zA-Z0-9]{8,}', "Hardcoded credential"),
            (r'(?i)(auth|token|session)\s*=\s*None', "Missing auth check"),
            (r'(?i)bearer\s+["\']?[a-zA-Z0-9]', "Exposed bearer token"),
        ],
        "severity": "critical",
        "mitigation": "使用环境变量注入凭据，启用 MFA，证书固定",
    },
    "tampering": {
        "name": "Tampering (数据篡改)",
        "checks": [
            (r'(?:execute|query|cursor)\s*\(\s*f["\']', "String interpolation in SQL"),
            (r'(?:execute|query|cursor)\s*\(\s*["\'].*%\s*', "Format string in SQL"),
            (r'innerHTML\s*=', "Direct HTML injection"),
            (r'eval\s*\(', "Dynamic code execution"),
        ],
        "severity": "critical",
        "mitigation": "参数化查询，输出编码，避免 eval",
    },
    "repudiation": {
        "name": "Repudiation (抵赖)",
        "checks": [
            (r'# TODO.*audit|# TODO.*log', "Missing audit trail"),
            (r'(?i)logger\.(debug|info)\s*\(', None),  # informational
        ],
        "severity": "warning",
        "mitigation": "添加不可变审计日志，关键操作数字签名",
    },
    "information_disclosure": {
        "name": "Information Disclosure (信息泄露)",
        "checks": [
            (r'print\s*\(.*(?:traceback|exception|error)', "Error details in output"),
            (r'return\s+.*(?:password|secret|token)', "Sensitive data in response"),
            (r'(?i)logging\.(debug|info)\s*\(.*(?:password|token|secret)', "Sensitive data in logs"),
        ],
        "severity": "warning",
        "mitigation": "通用错误消息，响应字段白名单，日志脱敏",
    },
    "denial_of_service": {
        "name": "DoS (拒绝服务)",
        "checks": [
            (r'while\s+True:', "Infinite loop risk"),
            (r'for\s+\w+\s+in\s+range\s*\(\s*int\s*\(', "Unbounded iteration"),
            (r'(?i)(socket|connect|request)\s*(?:without|no\s+)?(?:timeout|limit)', "Missing timeout"),
        ],
        "severity": "warning",
        "mitigation": "设置超时，添加速率限制，实现熔断",
    },
    "elevation_of_privilege": {
        "name": "Elevation of Privilege (权限提升)",
        "checks": [
            (r'(?i)admin|root|superuser', "Privileged operation detected"),
            (r'(?i)if\s+.*(?:role|permission|auth)\s*is\s*None', "Missing permission check"),
            (r'(?i)request\.(params|body|json)\s*\[', "Direct request parameter access"),
        ],
        "severity": "warning",
        "mitigation": "RBAC 权限模型，资源所有权校验，最小权限原则",
    },
}


@dataclass
class Threat:
    category: str
    description: str
    severity: str
    line: int
    code_snippet: str
    mitigation: str


def analyze_threats(filepath: str) -> list[Threat]:
    """分析文件中的 STRIDE 威胁"""
    threats = []
    try:
        content = Path(filepath).read_text(errors="ignore")
    except Exception as e:
        print(f"Error reading {filepath}: {e}", file=sys.stderr)
        return threats

    lines = content.split("\n")

    for cat, config in STRIDE_CATEGORIES.items():
        for pattern, custom_msg in config["checks"]:
            for i, line in enumerate(lines, 1):
                match = re.search(pattern, line)
                if match:
                    snippet = line.strip()[:80]
                    threats.append(Threat(
                        category=cat,
                        description=custom_msg or config["checks"][0][1] or "Potential threat",
                        severity=config["severity"],
                        line=i,
                        code_snippet=snippet,
                        mitigation=config["mitigation"],
                    ))

    return threats


def generate_report(threats: list[Threat], filepath: str) -> str:
    """生成威胁报告"""
    if not threats:
        return f"✅ No STRIDE threats detected in {filepath}\n"

    lines = [f"# STRIDE Threat Model: {Path(filepath).name}\n", f"**Analyzed:** {Path(filepath).resolve()}\n"]
    lines.append(f"**Threats Found:** {len(threats)}\n")
    lines.append("| Category | Severity | Line | Description | Mitigation |")
    lines.append("|----------|----------|------|-------------|------------|")

    for t in threats:
        lines.append(f"| {t.category} | 🔴{t.severity} | L{t.line} | {t.description} | {t.mitigation} |")

    lines.append("\n## Recommendations\n")
    for cat in set(t.category for t in threats):
        cat_threats = [t for t in threats if t.category == cat]
        lines.append(f"### {cat} ({len(cat_threats)} issues)\n")
        lines.append(f"- **Mitigation:** {cat_threats[0].mitigation}\n")
        for t in cat_threats[:3]:
            lines.append(f"  - L{t.line}: {t.description}")
        lines.append("")

    return "\n".join(lines)


def main():
    import argparse
    parser = argparse.ArgumentParser(description="STRIDE Threat Modeler")
    parser.add_argument("path", help="File or directory to analyze")
    parser.add_argument("--output", "-o", help="Output file")
    parser.add_argument("--json", action="store_true")
    args = parser.parse_args()

    path = Path(args.path)
    all_threats = []

    if path.is_file():
        all_threats.extend(analyze_threats(str(path)))
    else:
        for ext in [".py", ".ts", ".tsx", ".go", ".java", ".rs"]:
            all_threats.extend(analyze_threats(str(p)) for p in path.rglob(f"*{ext}"))

    if args.json:
        output = json.dumps([asdict(t) for t in all_threats], indent=2, ensure_ascii=False)
    else:
        output = generate_report(all_threats, args.path)

    if args.output:
        Path(args.output).write_text(output)
        print(f"Report written to {args.output}", file=sys.stderr)
    else:
        print(output)


if __name__ == "__main__":
    main()
