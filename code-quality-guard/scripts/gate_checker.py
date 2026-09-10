#!/usr/bin/env python3
"""质量门禁检查 — CI/CD 集成"""

import json
import sys
from pathlib import Path


GATE_CONFIG = {
    "min_score": 70,
    "max_critical": 0,
    "max_warning": 5,
    "required_axes": ["correctness", "security"],
    "min_axis_scores": {"correctness": 15, "security": 15},
}


def check_gate(results: list[dict]) -> dict:
    """检查质量门禁"""
    passed = True
    issues = []

    for r in results:
        score = r.get("composite_score", 0)
        axes = r.get("axes", {})

        # 综合分数检查
        if score < GATE_CONFIG["min_score"]:
            passed = False
            issues.append(f"❌ {r.get('file', 'unknown')}: score {score} < {GATE_CONFIG['min_score']}")

        # 关键轴检查
        for axis in GATE_CONFIG.get("required_axes", []):
            axis_score = axes.get(axis, {}).get("score", 0)
            min_score = GATE_CONFIG["min_axis_scores"].get(axis, 0)
            if axis_score < min_score:
                passed = False
                issues.append(f"❌ {r.get('file', 'unknown')}: {axis} score {axis_score} < {min_score}")

        # Critical 计数
        critical = sum(1 for d in r.get("detections", []) if d.get("severity") == "critical")
        if critical > GATE_CONFIG["max_critical"]:
            passed = False
            issues.append(f"❌ {r.get('file', 'unknown')}: {critical} critical issues (max: {GATE_CONFIG['max_critical']})")

    return {
        "passed": passed,
        "issues": issues,
        "config": GATE_CONFIG,
    }


def main():
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument("input", help="JSON review results file")
    parser.add_argument("--config", default=None, help="Custom gate config")
    args = parser.parse_args()

    with open(args.input) as f:
        data = json.load(f)

    results = data if isinstance(data, list) else data.get("results", [])
    gate_result = check_gate(results)

    print(json.dumps(gate_result, indent=2, ensure_ascii=False))

    if not gate_result["passed"]:
        print("\n🚨 QUALITY GATE FAILED", file=sys.stderr)
        for issue in gate_result["issues"]:
            print(f"  {issue}", file=sys.stderr)
        sys.exit(1)
    else:
        print("\n✅ Quality gate passed", file=sys.stderr)
        sys.exit(0)


if __name__ == "__main__":
    main()
