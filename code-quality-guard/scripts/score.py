#!/usr/bin/env python3
"""五轴评分引擎 — Correctness(20%) | Readability(20%) | Architecture(25%) | Security(20%) | Performance(15%)"""

import json
import sys
from dataclasses import dataclass, field, asdict
from pathlib import Path


WEIGHTS = {"correctness": 0.20, "readability": 0.20, "architecture": 0.25, "security": 0.20, "performance": 0.15}
MAX_SCORES = {"correctness": 20, "readability": 20, "architecture": 25, "security": 20, "performance": 15}


@dataclass
class AxisScore:
    axis: str
    score: float
    max_score: float
    deductions: list = field(default_factory=list)


def calculate_score(content: str, language: str, detections: list) -> dict:
    """计算五轴评分"""
    lines = content.split("\n")
    total_lines = len(lines)

    # ── Correctness ──
    correctness = 20
    c_deduct = []
    if "try:" in content and "except" not in content:
        correctness -= 3; c_deduct.append("try without except")
    if "null" in content.lower() and ("is None" not in content and "!= None" not in content):
        correctness -= 2; c_deduct.append("potential null dereference")
    for d in detections:
        if d["type"] == "anti_pattern":
            if d["name"] in ("sql_injection_risk", "eval_usage"):
                correctness -= 5; c_deduct.append(d["name"])
            elif d["name"] == "god_class":
                correctness -= 3; c_deduct.append(d["name"])

    # ── Readability ──
    readability = 20
    r_deduct = []
    # function length
    func_lines = []
    current = 0
    for line in lines:
        if any(line.strip().startswith(k) for k in ["def ", "function ", "func "]):
            func_lines.append(current)
            current = 0
        current += 1
    if func_lines and max(func_lines) > 50:
        readability -= 4; r_deduct.append(f"long function ({max(func_lines)} lines)")
    # nesting depth
    max_depth = max((len(line) - len(line.lstrip())) // 4 for line in lines) if lines else 0
    if max_depth > 3:
        readability -= 3; r_deduct.append(f"deep nesting (depth {max_depth})")

    # ── Architecture ──
    architecture = 25
    a_deduct = []
    class_count = content.count("class ")
    func_count = content.count("def ") + content.count("func ") + content.count("function ")
    if class_count == 0 and func_count > 20:
        architecture -= 5; a_deduct.append("no class structure")
    if func_count > 0 and class_count > 0 and func_count / max(class_count, 1) > 20:
        architecture -= 3; a_deduct.append("high method-to-class ratio")

    # ── Security ──
    security = 20
    s_deduct = []
    if any(d["name"] == "hardcoded_secret" for d in detections):
        security -= 8; s_deduct.append("hardcoded secret")
    if any(d["name"] == "sql_injection_risk" for d in detections):
        security -= 8; s_deduct.append("SQL injection risk")
    if "eval(" in content or "exec(" in content:
        security -= 5; s_deduct.append("dynamic code execution")
    if "password" in content.lower() and "=" in content:
        security -= 3; s_deduct.append("possible password handling")

    # ── Performance ──
    performance = 15
    p_deduct = []
    if "range(len(" in content or "for .* in range" in content:
        performance -= 2; p_deduct.append("potential O(n^2) pattern")
    if "//" in content and "cache" in content.lower():
        pass  # has caching, good
    elif total_lines > 200 and "cache" not in content.lower() and "memo" not in content.lower():
        performance -= 2; p_deduct.append("no caching for large file")

    scores = {
        "correctness": AxisScore("correctness", max(0, correctness), 20, c_deduct),
        "readability": AxisScore("readability", max(0, readability), 20, r_deduct),
        "architecture": AxisScore("architecture", max(0, architecture), 25, a_deduct),
        "security": AxisScore("security", max(0, security), 20, s_deduct),
        "performance": AxisScore("performance", max(0, performance), 15, p_deduct),
    }

    composite = round(sum(s.score * WEIGHTS[s.axis] for s in scores.values()), 1)

    if composite >= 90:
        grade, gate = "Excellent", "auto-approve"
    elif composite >= 70:
        grade, gate = "Good", "conditional-pass"
    elif composite >= 50:
        grade, gate = "Fair", "needs-fix"
    else:
        grade, gate = "Poor", "reject"

    return {
        "file": "",
        "language": language,
        "composite_score": composite,
        "grade": grade,
        "gate": gate,
        "axes": {k: {"score": v.score, "max": v.max_score, "percentage": round(v.score / v.max_score * 100, 1), "deductions": v.deductions} for k, v in scores.items()},
        "distillation_candidate": composite >= 90,
    }


def main():
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument("path")
    parser.add_argument("--language", default=None)
    parser.add_argument("--detections", default=None, help="JSON string of detections")
    parser.add_argument("--json", action="store_true")
    args = parser.parse_args()

    filepath = Path(args.path)
    language = args.language or filepath.suffix.lstrip(".")

    try:
        content = filepath.read_text(errors="ignore")
    except Exception as e:
        print(json.dumps({"error": str(e)}))
        sys.exit(1)

    detections = []
    if args.detections:
        detections = json.loads(args.detections)

    result = calculate_score(content, language, detections)
    result["file"] = str(filepath)

    if args.json:
        print(json.dumps(result, indent=2, ensure_ascii=False))
    else:
        print(f"\n{'='*50}")
        print(f"  Code Review: {filepath.name}")
        print(f"  Language: {language.upper()}")
        print(f"  Score: {result['composite_score']}/100 ({result['grade']})")
        print(f"  Gate: {result['gate']}")
        print(f"{'='*50}")
        for axis, data in result["axes"].items():
            bar = "█" * int(data["percentage"] / 10) + "░" * (10 - int(data["percentage"] / 10))
            print(f"  [{axis:>12}] {bar} {data['score']:3.0f}/{data['max']} ({data['percentage']:3.0f}%)")
            for d in data["deductions"]:
                print(f"      └─ {d}")
        if result["distillation_candidate"]:
            print(f"\n  ✨ This code qualifies for distillation (≥90)")


if __name__ == "__main__":
    main()
