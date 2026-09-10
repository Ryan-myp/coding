#!/usr/bin/env python3
"""
biz-delivery 集成 — Post-TD 架构审查 Hook
在 TD（技术方案）输出后自动触发架构质量检查
"""

import json
import sys
from pathlib import Path


def post_td_check(td_output_dir: str, gate_config: dict = None) -> dict:
    """在 TD 阶段后运行架构质量检查"""
    from ast_analyzer import analyze_file
    from score_engine import score_result

    td_path = Path(td_output_dir)
    results = []

    # 扫描 TD 生成的代码
    for ext in ['.py', '.ts', '.go']:
        for f in td_path.rglob(f'*{ext}'):
            analysis = analyze_file(str(f))
            scored = score_result(analysis)
            results.append(scored)

    # 汇总
    avg_score = sum(r["composite_score"] for r in results) / len(results) if results else 0
    critical_count = sum(
        len([f for f in r.get("findings", []) if f["severity"] == "critical"])
        for r in results
    )

    passed = avg_score >= 70 and critical_count == 0

    return {
        "passed": passed,
        "avg_score": round(avg_score, 1),
        "files_reviewed": len(results),
        "critical_issues": critical_count,
        "results": results,
    }


def main():
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument("td_output", help="TD 输出目录")
    parser.add_argument("--config", default=None)
    parser.add_argument("--json", action="store_true")
    args = parser.parse_args()

    result = post_td_check(args.td_output)

    if args.json:
        print(json.dumps(result, indent=2, ensure_ascii=False))
    else:
        status = "✅ PASSED" if result["passed"] else "❌ FAILED"
        print(f"\n  biz-delivery TD Quality Check: {status}")
        print(f"  Avg Score: {result['avg_score']}/100")
        print(f"  Files: {result['files_reviewed']}, Critical: {result['critical_issues']}")
        if not result["passed"]:
            sys.exit(1)


if __name__ == "__main__":
    main()
