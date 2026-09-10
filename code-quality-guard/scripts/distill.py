#!/usr/bin/env python3
"""
Distillation Engine v3 - Industrial code distillation engine
Supports Python/TypeScript/Go/Java/Rust multi-language pattern detection
"""

import ast
import json
import re
import sys
from dataclasses import dataclass, field, asdict
from datetime import datetime
from pathlib import Path
from typing import Optional

PATTERNS = {
    "repository_pattern": {
        "description": "Repository Pattern - Data access abstraction",
        "keywords": ["repository", "dao", "mapper", "store"],
        "lang": ["python", "typescript", "go", "java", "rust"],
        "indicator": r"(?:class|interface)\s+\w*[Rr]epository\w*\s*[:\(]",
    },
    "strategy_pattern": {
        "description": "Strategy Pattern - Algorithm family encapsulation",
        "keywords": ["strategy", "payment", "shipping"],
        "lang": ["python", "typescript", "go", "java", "rust"],
        "indicator": r"(?:class|interface)\s+\w*[Ss]trategy\w*\s*[:\(]",
    },
    "guard_clause": {
        "description": "Guard Clause - Early return to avoid deep nesting",
        "keywords": [],
        "lang": ["python", "typescript", "go", "java", "rust"],
        "indicator": r"(?:if|return)\s+.*(?:reject|error|null|None)",
    },
    "builder_pattern": {
        "description": "Builder Pattern - Chain construction",
        "keywords": ["builder", "build"],
        "lang": ["python", "typescript", "go", "java"],
        "indicator": r"\.build\(\)|\.with_\w+\(|func\s+\w+Builder",
    },
    "circuit_breaker": {
        "description": "Circuit Breaker - Prevent cascading failures",
        "keywords": ["breaker", "circuit"],
        "lang": ["python", "typescript", "go"],
        "indicator": r"(?:class|type)\s+\w*[Cc]ircuitBreaker\w*|State\.(?:OPEN|CLOSED|HALF)",
    },
    "result_type": {
        "description": "Result Type - Explicit success/failure handling",
        "keywords": ["result", "either"],
        "lang": ["rust", "typescript"],
        "indicator": r"Result<|Either<|type\s+Result\s*=",
    },
    "singleton": {
        "description": "Singleton Pattern - Globally unique instance",
        "keywords": ["singleton", "instance"],
        "lang": ["python", "typescript", "go", "java"],
        "indicator": r"(?:class|def|func)\s+\w*Singleton\w*|getInstance\(\)",
    },
    "factory_method": {
        "description": "Factory Method - Encapsulate object creation",
        "keywords": ["factory", "create", "new"],
        "lang": ["python", "typescript", "go", "java", "rust"],
        "indicator": r"def?\s+\w*(?:Factory|Create|New)\w*\s*\(",
    },
}

ANTI_PATTERNS = {}
def _ap(name, desc, sev, pat, langs):
    ANTI_PATTERNS[name] = {"description": desc, "severity": sev, "pattern": pat, "lang": langs}

_ap("hardcoded_secret", "Hardcoded secret/key/token", "critical",
    r'(?:password|secret|api_key|token)\s*[:=]\s*["\x27]?[a-zA-Z0-9]{8,}',
    ["python", "typescript", "go", "java", "rust"])
_ap("hardcoded_url", "Hardcoded URL (should use config)", "warning",
    r'["\x27]https?://[a-zA-Z0-9\-._~:/?=&]+["\x27]',
    ["python", "typescript", "go", "java", "rust"])
_ap("sql_injection_risk", "SQL injection risk (string concatenation)", "critical",
    r'(?:execute|query|cursor)\s*\(\s*f["\x27]|\.format\(',
    ["python", "typescript", "go", "java", "rust"])
_ap("god_class", "God class (too many methods)", "warning",
    r'class\s+\w+\s*[:\(]',
    ["python", "typescript", "go", "java", "rust"])
_ap("deep_nesting", "Deep nesting (>3 levels)", "warning",
    r'(?:if|for|while|switch|match)\s*\(',
    ["python", "typescript", "go", "java", "rust"])
_ap("unused_import", "Potentially unused import", "info",
    r'(?:import|from)\s+',
    ["python", "typescript", "go", "java", "rust"])
_ap("magic_number", "Magic number (unnamed constant)", "info",
    r'\b\d{2,}\b',
    ["python", "typescript", "go", "java", "rust"])
_ap("eval_usage", "eval/exec usage (security risk)", "critical",
    r'\b(?:eval|exec|evalf)\s*\(',
    ["python", "typescript", "go"])
_ap("todo_comment", "TODO/FIXME legacy comment", "info",
    r'(?:TODO|FIXME|HACK|WORKAROUND|XXX)\s*:',
    ["python", "typescript", "go", "java", "rust"])
_ap("console_log", "Console.log in production", "info",
    r'(?:console\.log|print\s*\()',
    ["python", "typescript"])

LANG_EXTENSIONS = {
    "python": [".py"],
    "typescript": [".ts", ".tsx", ".mts", ".cts"],
    "go": [".go"],
    "java": [".java"],
    "rust": [".rs"],
}

def detect_language(path: str) -> Optional[str]:
    ext = Path(path).suffix
    for lang, exts in LANG_EXTENSIONS.items():
        if ext in exts:
            return lang
    return None

@dataclass
class Detection:
    type: str
    name: str
    severity: str
    line: int
    message: str
    lang: str
    file: str

@dataclass
class FileResult:
    path: str
    language: str
    score: float
    patterns_found: list = field(default_factory=list)
    anti_patterns_found: list = field(default_factory=list)
    metrics: dict = field(default_factory=dict)

def safe_search(pattern, text):
    try:
        return re.search(pattern, text, re.IGNORECASE)
    except re.error:
        return None

def analyze_python(filepath, content):
    detections = []
    lines = content.split("\n")
    try:
        tree = ast.parse(content)
    except SyntaxError:
        return detections
    for node in ast.walk(tree):
        if isinstance(node, ast.FunctionDef):
            mc = sum(1 for n in ast.walk(node) if isinstance(n, ast.FunctionDef))
            if mc > 5:
                detections.append(Detection("pattern", "method_grouping", "info", node.lineno,
                    f"Nested {mc} sub-functions", "python", filepath))
        elif isinstance(node, ast.ClassDef):
            methods = [n for n in ast.iter_child_nodes(node) if isinstance(n, ast.FunctionDef)]
            if len(methods) > 15:
                detections.append(Detection("anti_pattern", "god_class", "warning", node.lineno,
                    f"Class '{node.name}' has {len(methods)} methods (recommend < 15)", "python", filepath))
    for i, line in enumerate(lines, 1):
        stripped = line.strip()
        if not stripped or stripped.startswith("#"):
            continue
        for key, ap in ANTI_PATTERNS.items():
            if "python" not in ap.get("lang", []):
                continue
            if safe_search(ap["pattern"], line):
                detections.append(Detection("anti_pattern", key, ap["severity"], i,
                    ap["description"], "python", filepath))
                break
    max_depth = max(((len(l) - len(l.lstrip())) // 4) for l in lines) if lines else 0
    if max_depth > 3:
        detections.append(Detection("anti_pattern", "deep_nesting", "warning", 1,
            f"Max nesting depth {max_depth} (recommend <= 3)", "python", filepath))
    return detections

def analyze_ts(filepath, content):
    detections = []
    lines = content.split("\n")
    for i, line in enumerate(lines, 1):
        stripped = line.strip()
        if not stripped or stripped.startswith("//"):
            continue
        for key, ap in ANTI_PATTERNS.items():
            if "typescript" not in ap.get("lang", []):
                continue
            if safe_search(ap["pattern"], line):
                detections.append(Detection("anti_pattern", key, ap["severity"], i,
                    ap["description"], "typescript", filepath))
                break
        for key, p in PATTERNS.items():
            if "typescript" not in p.get("lang", []):
                continue
            if safe_search(p["indicator"], line):
                detections.append(Detection("pattern", key, "info", i,
                    p["description"], "typescript", filepath))
                break
    max_d = max(((len(l) - len(l.lstrip())) // 2) for l in lines) if lines else 0
    if max_d > 3:
        detections.append(Detection("anti_pattern", "deep_nesting", "warning", 1,
            f"Max indent depth {max_d} (recommend <= 3)", "typescript", filepath))
    return detections

def analyze_go(filepath, content):
    detections = []
    lines = content.split("\n")
    for i, line in enumerate(lines, 1):
        stripped = line.strip()
        if not stripped or stripped.startswith("//"):
            continue
        for key, ap in ANTI_PATTERNS.items():
            if "go" not in ap.get("lang", []):
                continue
            if safe_search(ap["pattern"], line):
                detections.append(Detection("anti_pattern", key, ap["severity"], i,
                    ap["description"], "go", filepath))
                break
        for key, p in PATTERNS.items():
            if "go" not in p.get("lang", []):
                continue
            if safe_search(p["indicator"], line):
                detections.append(Detection("pattern", key, "info", i,
                    p["description"], "go", filepath))
                break
    return detections

def analyze_java(filepath, content):
    detections = []
    lines = content.split("\n")
    for i, line in enumerate(lines, 1):
        stripped = line.strip()
        if not stripped or stripped.startswith("//"):
            continue
        for key, ap in ANTI_PATTERNS.items():
            if "java" not in ap.get("lang", []):
                continue
            if safe_search(ap["pattern"], line):
                detections.append(Detection("anti_pattern", key, ap["severity"], i,
                    ap["description"], "java", filepath))
                break
    return detections

def analyze_rust(filepath, content):
    detections = []
    lines = content.split("\n")
    for i, line in enumerate(lines, 1):
        stripped = line.strip()
        if not stripped or stripped.startswith("//"):
            continue
        for key, ap in ANTI_PATTERNS.items():
            if "rust" not in ap.get("lang", []):
                continue
            if safe_search(ap["pattern"], line):
                detections.append(Detection("anti_pattern", key, ap["severity"], i,
                    ap["description"], "rust", filepath))
                break
        for key, p in PATTERNS.items():
            if "rust" not in p.get("lang", []):
                continue
            if safe_search(p["indicator"], line):
                detections.append(Detection("pattern", key, "info", i,
                    p["description"], "rust", filepath))
                break
    return detections

ANALYZERS = {"python": analyze_python, "typescript": analyze_ts, "go": analyze_go,
             "java": analyze_java, "rust": analyze_rust}

def calculate_score(detections, total_lines):
    if total_lines == 0:
        return 0
    base = 100
    deductions = {"critical": 15, "warning": 5, "info": 2}
    total = sum(deductions.get(d.severity, 2) for d in detections)
    return round(max(0, base - total), 1)

def distill(path, max_files=50, languages=None):
    target = Path(path)
    if not target.exists():
        print(f"Error: {path} does not exist", file=sys.stderr)
        sys.exit(1)
    languages = languages or ["python", "typescript", "go", "java", "rust"]
    results, count = [], 0
    files = []
    if target.is_file():
        files = [target]
    else:
        for lang in languages:
            for ext in LANG_EXTENSIONS.get(lang, []):
                files.extend(target.rglob(f"*{ext}"))
    seen, unique = set(), []
    for f in files:
        if f not in seen:
            seen.add(f)
            unique.append(f)
    files = unique[:max_files]
    for fp in files:
        lang = detect_language(str(fp))
        if lang not in languages:
            continue
        try:
            content = fp.read_text(encoding="utf-8", errors="ignore")
        except Exception as e:
            print(f"Warning: Could not read {fp}: {e}", file=sys.stderr)
            continue
        analyzer = ANALYZERS.get(lang)
        if not analyzer:
            continue
        detections = analyzer(str(fp), content)
        score = calculate_score(detections, len(content.split("\n")))
        results.append(FileResult(str(fp), lang, score,
            [d.name for d in detections if d.type == "pattern"],
            [d.name for d in detections if d.type == "anti_pattern"],
            {"lines": len(content.split("\n")), "detections": len(detections),
             "critical": sum(1 for d in detections if d.severity == "critical"),
             "warnings": sum(1 for d in detections if d.severity == "warning"),
             "info": sum(1 for d in detections if d.severity == "info")}))
        count += 1
        if count % 10 == 0:
            print(f"  Analyzed {count}/{len(files)} files...", file=sys.stderr)
    return results

def main():
    import argparse
    parser = argparse.ArgumentParser(description="Code Distillation Engine v3")
    parser.add_argument("path", help="File or directory to analyze")
    parser.add_argument("--max-files", type=int, default=50)
    parser.add_argument("--languages", nargs="+", default=None)
    parser.add_argument("--output", "-o", help="Output file")
    parser.add_argument("--json", action="store_true")
    args = parser.parse_args()
    results = distill(args.path, args.max_files, args.languages)
    total = len(results)
    avg = sum(r.score for r in results) / total if total else 0
    crit = sum(r.metrics["critical"] for r in results)
    warn = sum(r.metrics["warnings"] for r in results)
    output = {"version": "3.0.0", "timestamp": datetime.utcnow().isoformat() + "Z",
        "summary": {"total_files": total, "avg_score": avg, "critical_issues": crit,
                     "warning_issues": warn,
                     "pass_rate": sum(1 for r in results if r.score >= 70) / total if total else 0},
        "results": [asdict(r) for r in results]}
    jo = json.dumps(output, indent=2, ensure_ascii=False)
    if args.output:
        Path(args.output).write_text(jo)
        print(f"Results written to {args.output}", file=sys.stderr)
    elif args.json:
        print(jo)
    else:
        print(f"\n{'='*60}\n  Code Distillation Report v3\n{'='*60}\n")
        print(f"  Files analyzed:  {total}")
        print(f"  Average score:   {avg:.1f}/100")
        print(f"  Critical issues: {crit}")
        print(f"  Warnings:        {warn}")
        print(f"  Pass rate:       {output['summary']['pass_rate']:.1%}\n")
        print(f"{'-'*60}")
        for r in results[:20]:
            st = "OK  " if r.score >= 90 else "WARN" if r.score >= 70 else "FAIL"
            print(f"  [{st}] [{r.language.upper():>10}] {r.score:5.1f}  {r.path}")
            for ap in r.anti_patterns_found:
                print(f"      |-- {ap}")
        if len(results) > 20:
            print(f"\n  ... and {len(results) - 20} more files")
    hd = Path(__file__).parent.parent / "distillation"
    hd.mkdir(exist_ok=True)
    with open(hd / "history.jsonl", "a") as f:
        f.write(json.dumps({"timestamp": datetime.utcnow().isoformat() + "Z",
            "source": args.path, "languages": list({r.language for r in results}),
            "files_analyzed": total, "avg_score": avg, "critical_count": crit,
            "patterns_found": list({p for r in results for p in r.patterns_found}),
            "anti_patterns_found": list({a for r in results for a in r.anti_patterns_found})}) + "\n")

if __name__ == "__main__":
    main()
