#!/usr/bin/env python3
"""Diff Analyzer — 分析代码变更的影响面和风险"""

import json
import sys
from pathlib import Path
from datetime import datetime


DANGEROUS_PATTERNS = {
    "database": {
        "patterns": [r"(?i)(ALTER|DROP|TRUNCATE|CREATE\s+TABLE)", r"(?i)(execute|query|cursor)\s*\("],
        "severity": "critical",
        "label": "Database Schema Change",
    },
    "authentication": {
        "patterns": [r"(?i)(auth|login|token|session|password|jwt|oauth)"],
        "severity": "critical",
        "label": "Auth/Security Related",
    },
    "payment": {
        "patterns": [r"(?i)(payment|charge|billing|invoice|transaction)"],
        "severity": "critical",
        "label": "Payment/Billing",
    },
    "configuration": {
        "patterns": [r"(?i)(\.env|config|settings|constants|constants)"],
        "severity": "warning",
        "label": "Configuration Change",
    },
    "api_contract": {
        "patterns": [r"(?i)(interface|type\s+\w+\s*=|schema|router|route|endpoint)"],
        "severity": "warning",
        "label": "API Contract Change",
    },
}


def analyze_diff(diff_content: str) -> dict:
    """分析 diff 内容，识别风险"""
    findings = []
    lines = diff_content.split("\n")

    for line in lines:
        if not line.startswith("+") or line.startswith("+++"):
            continue

        added_line = line[1:]  # 去掉 "+"

        for category, config in DANGEROUS_PATTERNS.items():
            for pattern in config["patterns"]:
                if re.search(pattern, added_line, re.IGNORECASE):
                    findings.append({
                        "category": category,
                        "severity": config["severity"],
                        "label": config["label"],
                        "line": added_line.strip()[:100],
                    })
                    break

    # 统计变更行数
    add_count = sum(1 for l in lines if l.startswith("+") and not l.startswith("+++"))
    del_count = sum(1 for l in lines if l.startswith("-") and not l.startswith("---"))

    return {
        "added_lines": add_count,
        "removed_lines": del_count,
        "net_change": add_count - del_count,
        "findings": findings,
        "risk_level": _assess_risk(findings, add_count),
    }


def _assess_risk(findings: list, added_lines: int) -> str:
    """评估整体风险级别"""
    if not findings:
        return "low"
    severities = [f["severity"] for f in findings]
    if "critical" in severities:
        return "high"
    if "warning" in severities:
        return "medium"
    return "low"


def main():
    import argparse
    import re
    parser = argparse.ArgumentParser()
    parser.add_argument("diff_file", help="Path to diff/patch file")
    parser.add_argument("--json", action="store_true")
    args = parser.parse_args()

    try:
        diff_content = Path(args.diff_file).read_text()
    except FileNotFoundError:
        # 尝试从 stdin 读取
        diff_content = sys.stdin.read()

    result = analyze_diff(diff_content)

    if args.json:
        print(json.dumps(result, indent=2, ensure_ascii=False))
    else:
        print(f"\n{'='*50}")
        print(f"  Diff Analysis Report")
        print(f"{'='*50}")
        print(f"  Added:   {result['added_lines']} lines")
        print(f"  Removed: {result['removed_lines']} lines")
        print(f"  Net:     {result['net_change']:+d} lines")
        print(f"  Risk:    {result['risk_level'].upper()}")
        print(f"{'-'*50}")

        if result["findings"]:
            print(f"\n  Findings ({len(result['findings'])}):")
            for f in result["findings"][:10]:
                icon = "🔴" if f["severity"] == "critical" else "🟡"
                print(f"    {icon} [{f['label']}] {f['line'][:60]}")
        else:
            print("\n  No risky patterns detected.")


if __name__ == "__main__":
    main()
