#!/usr/bin/env python3
"""
biz-delivery 集成 — Pre-Merge 门禁 Hook
在 PR merge 前运行完整质量门禁
"""

import json
import sys
from pathlib import Path


def pre_merge_check(pr_dir: str, min_score: int = 70) -> dict:
    """PR merge 前的完整质量门禁"""
    from ast_analyzer import analyze_file
    from score_engine import score_result
    from threat_modeler import ThreatModeler

    target_path = Path(pr_dir)
    results = []
    all_threats = []

    # 五轴评分
    for ext in ['.py', '.ts', '.tsx', '.go', '.java', '.rs']:
        for f in target_path.rglob(f'*{ext}'):
            analysis = analyze_file(str(f))
            scored = score_result(analysis)
            results.append(scored)

    # STRIDE 威胁建模
    tm = ThreatModeler()
    for ext in ['.py', '.ts', '.go']:
        all_threats.extend(tm.analyze_file(str(f)) for f in target_path.rglob(f'*{ext}'))

    # 计算指标
    avg_score = sum(r["composite_score"] for r in results) / len(results) if results else 0
    critical_count = sum(
        len([f for f in r.get("findings", []) if f["severity"] == "critical"])
        for r in results
    )
    threat_critical = len([t for t in all_threats if t.get("severity") == "critical"])

    passed = avg_score >= min_score and critical_count == 0 and threat_critical == 0

    return {
        "passed": passed,
        "avg_score": round(avg_score, 1),
        "min_score_required": min_score,
        "files_reviewed": len(results),
        "critical_issues": critical_count,
        "critical_threats": threat_critical,
        "total_threats": len(all_threats),
        "results": results,
        "threats": all_threats,
    }


def main():
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument("pr_dir", help="PR 变更目录或文件")
    parser.add_argument("--min-score", type=int, default=70)
    parser.add_argument("--json", action="store_true")
    args = parser.parse_args()

    result = pre_merge_check(args.pr_dir, args.min_score)

    if args.json:
        print(json.dumps(result, indent=2, ensure_ascii=False))
        sys.exit(0 if result["passed"] else 1)
    else:
        status = "✅ MERGE ALLOWED" if result["passed"] else "🚫 MERGE BLOCKED"
        print(f"\n  Pre-Merge Quality Gate: {status}")
        print(f"  Score: {result['avg_score']}/100 (required ≥ {result['min_score_required']})")
        print(f"  Files: {result['files_reviewed']}")
        print(f"  Critical issues: {result['critical_issues']}")
        print(f"  Critical threats: {result['critical_threats']}")
        if not result["passed"]:
            print("\n  Blockers:")
            if result['critical_issues'] > 0:
                print(f"    - {result['critical_issues']} critical code issues")
            if result['critical_threats'] > 0:
                print(f"    - {result['critical_threats']} critical security threats")
            sys.exit(1)


if __name__ == "__main__":
    main()
