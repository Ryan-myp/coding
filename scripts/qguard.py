#!/usr/bin/env python3
"""
Unified CLI — qguard.py
所有命令的统一入口，支持 review/threats/distill/metrics/gate/badge
"""

import argparse
import json
import sys
import os
from pathlib import Path

# 添加 scripts 目录到路径
sys.path.insert(0, str(Path(__file__).parent))

from ast_analyzer import analyze_file, AnalysisResult
from score_engine import score_result, SCORE_FUNCS


def cmd_review(args):
    """审查文件或目录"""
    path = Path(args.path)
    if path.is_file():
        results = [_review_file(str(path))]
    elif path.is_dir():
        results = []
        for ext in ['.py', '.ts', '.tsx', '.go', '.java', '.rs']:
            for f in path.rglob(f'*{ext}')[:args.max_files]:
                results.append(_review_file(str(f)))
    else:
        print(f"Error: {path} not found", file=sys.stderr)
        sys.exit(1)

    if args.json:
        print(json.dumps(results, indent=2, ensure_ascii=False))
    else:
        _print_review_report(results)


def _review_file(filepath: str) -> dict:
    """审查单个文件"""
    result = analyze_file(filepath)
    scored = score_result(result)
    # 附加 findings 详情
    scored["findings"] = [
        {"type": f.category, "name": f.name, "severity": f.severity,
         "line": f.line, "message": f.message}
        for f in result.findings
    ]
    scored["patterns"] = result.patterns
    return scored


def _print_review_report(results: list):
    """打印审查报告"""
    if not results:
        print("No files to review.")
        return

    print(f"\n{'='*65}")
    print(f"  Code Quality Review — {len(results)} file(s) analyzed")
    print(f"{'='*65}\n")

    for r in results:
        status_emoji = {"auto-approve": "✅", "conditional-pass": "⚠️",
                        "needs-fix": "🟠", "reject": "🔴"}.get(r["gate"], "❓")
        print(f"  {status_emoji}  {r['composite_score']:5.1f}/100  {r['grade']}  [{r['gate']}]")
        print(f"     {r['file']}")

        # 显示各轴分数条
        for axis_name in ["correctness", "readability", "architecture", "security", "performance"]:
            ax = r["axes"][axis_name]
            bar_len = int(ax["percentage"] / 5)
            bar = "█" * bar_len + "░" * (20 - bar_len)
            print(f"      [{axis_name:>14}] {bar} {ax['score']:3.0f}/{ax['max']}")

        if r["findings"]:
            print(f"      Findings ({len(r['findings'])}):")
            for f in r["findings"][:5]:
                icon = "🔴" if f["severity"] == "critical" else "🟡" if f["severity"] == "warning" else "ℹ️"
                print(f"        {icon} L{f['line']:4d} {f['message']}")

        print()

    # 汇总
    avg = sum(r["composite_score"] for r in results) / len(results)
    passed = sum(1 for r in results if r["composite_score"] >= 70)
    print(f"  Summary: avg={avg:.1f}, passed={passed}/{len(results)}, pass_rate={passed/len(results)*100:.0f}%")
    print()


def cmd_threats(args):
    """STRIDE 威胁建模"""
    from threat_modeler import ThreatModeler
    tm = ThreatModeler()

    path = Path(args.path)
    if path.is_file():
        threats = tm.analyze_file(str(path))
    else:
        threats = []
        for ext in ['.py', '.ts', '.go', '.java', '.rs']:
            threats.extend(tm.analyze_file(str(f)) for f in path.rglob(f'*{ext}')[:args.max_files])

    if args.json:
        print(json.dumps(threats, indent=2, ensure_ascii=False))
    else:
        if not threats:
            print("✅ No threats detected.")
            return
        print(f"\n{'='*60}")
        print(f"  STRIDE Threat Model — {len(threats)} threat(s) found")
        print(f"{'='*60}\n")
        for t in threats[:20]:
            sev = {"critical": "🔴", "warning": "🟡", "info": "ℹ️"}.get(t["severity"], "⚪")
            print(f"  {sev} [{t['category']:15s}] L{t['line']:4d}  {t['description']}")
            print(f"      Mitigation: {t['mitigation']}")
        print()


def cmd_distill(args):
    """蒸馏模式"""
    from distiller import Distiller
    d = Distiller()

    path = Path(args.path)
    patterns, anti_patterns = d.distill(str(path), max_files=args.max_files)

    output = {"patterns": patterns, "anti_patterns": anti_patterns, "version": "4.0.0"}

    if args.output:
        Path(args.output).write_text(json.dumps(output, indent=2, ensure_ascii=False))
        print(f"Results written to {args.output}", file=sys.stderr)
    elif args.json:
        print(json.dumps(output, indent=2, ensure_ascii=False))
    else:
        print(f"\n{'='*60}")
        print(f"  Distillation Report — {len(patterns)} patterns, {len(anti_patterns)} anti-patterns")
        print(f"{'='*60}\n")
        if patterns:
            print("  Design Patterns Found:")
            for p in patterns[:10]:
                print(f"    ✅ {p['name']} — {p['desc']} (L{p['line']})")
        if anti_patterns:
            print("\n  Anti-Patterns Found:")
            for ap in anti_patterns[:10]:
                print(f"    ⚠️  {ap['name']} — {ap['desc']} (L{ap['line']})")
        print()


def cmd_metrics(args):
    """质量趋势"""
    from metrics_dashboard import MetricsDashboard
    md = MetricsDashboard()

    if args.last:
        data = md.get_recent(args.last)
    else:
        data = md.get_all()

    if args.json:
        print(json.dumps(data, indent=2, ensure_ascii=False))
    else:
        md.print_dashboard(data)


def cmd_gate(args):
    """质量门禁"""
    path = Path(args.path) if args.path else Path.cwd()
    results = []

    if path.is_file():
        results.append(_review_file(str(path)))
    elif path.is_dir():
        for ext in ['.py', '.ts', '.go', '.java', '.rs']:
            for f in path.rglob(f'*{ext}')[:args.max_files]:
                results.append(_review_file(str(f)))

    min_score = args.min_score
    passed = all(r["composite_score"] >= min_score for r in results) if results else True

    if args.json:
        print(json.dumps({"passed": passed, "min_score": min_score,
                          "results": [{"file": r["file"], "score": r["composite_score"],
                                       "gate": r["gate"]} for r in results]},
                         indent=2, ensure_ascii=False))
    else:
        failed = [r for r in results if r["composite_score"] < min_score]
        if failed:
            print(f"\n🚨 Quality Gate FAILED (min={min_score})")
            for r in failed:
                print(f"  ❌ {r['file']}: {r['composite_score']}/100")
            sys.exit(1)
        else:
            print(f"✅ Quality gate passed (min={min_score})")
            sys.exit(0)


def cmd_badge(args):
    """生成质量徽章"""
    from badge_generator import BadgeGenerator
    bg = BadgeGenerator()

    path = Path(args.path) if args.path else Path.cwd()
    svg = bg.generate(str(path), min_score=args.min_score)

    if args.output:
        Path(args.output).write_text(svg)
        print(f"Badge written to {args.output}", file=sys.stderr)
    else:
        print(svg)


def main():
    parser = argparse.ArgumentParser(description="Code Quality Guard v4 — Unified CLI")
    sub = parser.add_subparsers(dest="command", required=True)

    # review
    p_review = sub.add_parser("review", help="五轴评分审查")
    p_review.add_argument("path")
    p_review.add_argument("--max-files", type=int, default=50)
    p_review.add_argument("--json", action="store_true")

    # threats
    p_threats = sub.add_parser("threats", help="STRIDE威胁建模")
    p_threats.add_argument("path")
    p_threats.add_argument("--max-files", type=int, default=50)
    p_threats.add_argument("--json", action="store_true")

    # distill
    p_distill = sub.add_parser("distill", help="蒸馏设计模式")
    p_distill.add_argument("path")
    p_distill.add_argument("--max-files", type=int, default=50)
    p_distill.add_argument("--output", "-o")
    p_distill.add_argument("--json", action="store_true")

    # metrics
    p_metrics = sub.add_parser("metrics", help="质量趋势")
    p_metrics.add_argument("--last", type=int, help="最近N天")
    p_metrics.add_argument("--json", action="store_true")

    # gate
    p_gate = sub.add_parser("gate", help="质量门禁（CI集成）")
    p_gate.add_argument("path", nargs="?", default=None)
    p_gate.add_argument("--min-score", type=int, default=70)
    p_gate.add_argument("--max-files", type=int, default=50)
    p_gate.add_argument("--json", action="store_true")

    # badge
    p_badge = sub.add_parser("badge", help="生成质量徽章")
    p_badge.add_argument("path", nargs="?", default=None)
    p_badge.add_argument("--min-score", type=int, default=70)
    p_badge.add_argument("--output", "-o")

    args = parser.parse_args()
    commands = {"review": cmd_review, "threats": cmd_threats, "distill": cmd_distill,
                "metrics": cmd_metrics, "gate": cmd_gate, "badge": cmd_badge}
    commands[args.command](args)


if __name__ == "__main__":
    main()
