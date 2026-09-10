#!/usr/bin/env python3
"""Distiller"""

import json, re
from pathlib import Path
from datetime import datetime


PATTERN_REGISTRY = {}

def register_pattern(name, desc, detector):
    PATTERN_REGISTRY[name] = {"desc": desc, "detector": detector}
    return detector


def _mk_tree_detector(name_kw, **kwargs):
    kw = kwargs.get("kw", name_kw)
    def detector(tree):
        results = []
        for n in tree.body:
            if isinstance(n, type) and kw in getattr(n, "name", ""):
                results.append(n)
        return results
    return detector


def _factory_detector(tree):
    results = []
    for n in tree.body:
        if not isinstance(n, type):
            continue
        name = getattr(n, "name", "")
        has_factory = "Factory" in name
        has_create = False
        for m in getattr(n, "body", []):
            if hasattr(m, "name") and "create" in m.name.lower():
                has_create = True
                break
        if has_factory or has_create:
            results.append(n)
    return results


def _observer_detector(tree):
    results = []
    for n in tree.body:
        if not isinstance(n, type):
            continue
        has_pattern = False
        for m in getattr(n, "body", []):
            if hasattr(m, "name"):
                name_lower = m.name.lower()
                if "observe" in name_lower or "listener" in name_lower:
                    has_pattern = True
                    break
        if has_pattern:
            results.append(n)
    return results


def _di_detector(tree):
    results = []
    for n in tree.body:
        if not isinstance(n, type):
            continue
        has_pattern = False
        for m in getattr(n, "body", []):
            if hasattr(m, "name"):
                name_lower = m.name.lower()
                if "inject" in name_lower or "dep" in name_lower:
                    has_pattern = True
                    break
        if has_pattern:
            results.append(n)
    return results


register_pattern("repository", "Repository Pattern", _mk_tree_detector("repository"))
register_pattern("strategy", "Strategy Pattern", _mk_tree_detector("strategy"))
register_pattern("builder", "Builder Pattern", _mk_tree_detector("builder"))
register_pattern("factory", "Factory Pattern", _factory_detector)
register_pattern("observer", "Observer Pattern", _observer_detector)
register_pattern("circuit_breaker", "Circuit Breaker", _mk_tree_detector("circuit_breaker", kw="Breaker"))
register_pattern("singleton", "Singleton Pattern", _mk_tree_detector("singleton"))
register_pattern("dependency_injection", "Dependency Injection", _di_detector)


class Distiller:
    def __init__(self, output_dir=None):
        self.output_dir = Path(output_dir or str(
            Path(__file__).parent.parent / "distillation"))
        self.output_dir.mkdir(parents=True, exist_ok=True)
        self._load_registry()

    def _load_registry(self):
        self.registered = {}
        pf = self.output_dir / "patterns.json"
        if pf.exists():
            try:
                self.registered = json.loads(pf.read_text())
            except Exception:
                self.registered = {}

    def distill(self, path, max_files=50):
        import ast
        from ast_analyzer import analyze_file
        path_obj = Path(path)
        files = []
        if path_obj.is_file():
            files = [path_obj]
        else:
            for ext in [".py", ".ts", ".tsx", ".go", ".java", ".rs"]:
                files.extend(path_obj.rglob(f"*{ext}"))
        files = files[:max_files]
        patterns_found = []
        anti_patterns_found = []
        for fp in files:
            try:
                source = fp.read_text(errors="ignore")
            except Exception:
                continue
            try:
                tree = ast.parse(source)
            except SyntaxError:
                continue
            lang = fp.suffix.lstrip(".")
            for name, reg in PATTERN_REGISTRY.items():
                try:
                    results = reg["detector"](tree)
                    if results:
                        for r in results[:2]:
                            line = getattr(r, "lineno", 1)
                            sample_lines = source.split(chr(10))[line-1:line+4]
                            patterns_found.append({
                                "name": name, "desc": reg["desc"],
                                "language": lang, "file": str(fp),
                                "line": line,
                                "sample": chr(10).join(sample_lines)[:200],
                                "confidence": 0.85,
                            })
                except Exception:
                    pass
            analysis = analyze_file(str(fp))
            for fin in analysis.findings:
                if fin.category == "anti_pattern":
                    anti_patterns_found.append({
                        "name": fin.name, "desc": fin.message,
                        "language": lang, "file": str(fp),
                        "line": fin.line, "severity": fin.severity,
                    })
        self._save_patterns(patterns_found)
        self._save_history(path, patterns_found, anti_patterns_found)
        return patterns_found, anti_patterns_found

    def _save_patterns(self, patterns):
        existing = self.registered.get("patterns", [])
        seen = set()
        for p in patterns:
            key = ":".join([p["name"], p["language"], p["file"]])
            if key not in seen:
                seen.add(key)
                existing.append(p)
        self.registered["patterns"] = existing
        (self.output_dir / "patterns.json").write_text(
            json.dumps(self.registered, indent=2, ensure_ascii=False))

    def _save_history(self, source, patterns, anti_patterns):
        record = {
            "timestamp": datetime.utcnow().isoformat() + "Z",
            "source": source,
            "patterns_found": len(patterns),
            "anti_patterns_found": len(anti_patterns),
            "pattern_names": list(set(p["name"] for p in patterns)),
            "anti_pattern_names": list(set(a["name"] for a in anti_patterns)),
        }
        with open(self.output_dir / "history.jsonl", "a") as fh:
            fh.write(json.dumps(record) + chr(10))
