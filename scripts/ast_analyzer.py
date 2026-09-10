#!/usr/bin/env python3
"""
AST Analyzer — 真正的代码结构分析器
用 Python ast 模块解析源码，提取复杂度、模式、反模式
"""

import ast
import sys
import re
from dataclasses import dataclass, field
from typing import Optional


# ── 数据模型 ─────────────────────────────────────────────────────────────────

@dataclass
class Metric:
    name: str
    value: float
    threshold: float
    unit: str = ""

    @property
    def status(self) -> str:
        if self.threshold == 0:
            return "ok"
        ratio = self.value / self.threshold if self.threshold > 0 else 0
        if ratio <= 0.8:
            return "green"
        elif ratio <= 1.0:
            return "yellow"
        else:
            return "red"

    @property
    def penalty(self) -> float:
        ratio = self.value / self.threshold if self.threshold > 0 else 0
        return max(0, (ratio - 0.8) * 10) if ratio > 0.8 else 0


@dataclass
class Finding:
    category: str  # "pattern" | "anti_pattern" | "issue"
    name: str
    severity: str  # "critical" | "warning" | "info"
    line: int
    message: str
    suggestion: str = ""
    code_snippet: str = ""


@dataclass
class AnalysisResult:
    file: str
    language: str
    metrics: list = field(default_factory=list)
    findings: list = field(default_factory=list)
    patterns: list = field(default_factory=list)
    ast_tree: Optional[ast.AST] = None


# ── 复杂度分析 ────────────────────────────────────────────────────────────────

def compute_cyclomatic_complexity(tree: ast.AST) -> int:
    """计算圈复杂度 — 标准算法：E - N + 2P"""
    complexity = 1
    for node in ast.walk(tree):
        if isinstance(node, (ast.If, ast.While, ast.For, ast.ExceptHandler)):
            complexity += 1
        elif isinstance(node, ast.BoolOp):
            complexity += len(node.values) - 1
        elif isinstance(node, ast.Assert):
            complexity += 1
    return complexity


def compute_nesting_depth(tree: ast.AST) -> int:
    """最大嵌套深度"""
    max_depth = [0]

    def walk(node, depth=0):
        max_depth[0] = max(max_depth[0], depth)
        for child in ast.iter_child_nodes(node):
            if isinstance(child, (ast.If, ast.For, ast.While, ast.With, ast.Try)):
                walk(child, depth + 1)
            else:
                walk(child, depth)

    walk(tree)
    return max_depth[0]


def compute_function_lengths(tree: ast.AST) -> list:
    """各函数行数分布"""
    lengths = []
    for node in ast.walk(tree):
        if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
            end = getattr(node, 'end_lineno', node.lineno + 50)
            lengths.append((node.name, node.lineno, end - node.lineno + 1))
    return lengths


def compute_class_metrics(tree: ast.AST) -> list:
    """各类指标"""
    classes = []
    for node in ast.walk(tree):
        if isinstance(node, ast.ClassDef):
            methods = [n for n in node.body if isinstance(n, (ast.FunctionDef, ast.AsyncFunctionDef))]
            lines = getattr(node, 'end_lineno', node.lineno) - node.lineno + 1
            classes.append({
                "name": node.name,
                "line": node.lineno,
                "methods": len(methods),
                "lines": lines,
                "complexity": sum(compute_cyclomatic_complexity(m) for m in methods),
            })
    return classes


# ── 模式识别 ─────────────────────────────────────────────────────────────────

PATTERNS = {
    "repository_pattern": {
        "desc": "Repository Pattern",
        "detect": lambda tree: [
            Finding("pattern", "repository_pattern", "info", n.lineno,
                    f"Repository pattern detected: {n.name}",
                    "Good abstraction for data access layer")
            for n in ast.walk(tree)
            if isinstance(n, ast.ClassDef) and re.search(r'[Rr]epository|[Dd]ao|[Mm]apper', n.name)
        ],
    },
    "strategy_pattern": {
        "desc": "Strategy Pattern",
        "detect": lambda tree: [
            Finding("pattern", "strategy_pattern", "info", n.lineno,
                    f"Strategy pattern detected: {n.name}",
                    "Good algorithm family abstraction")
            for n in ast.walk(tree)
            if isinstance(n, ast.ClassDef) and re.search(r'[Ss]trategy|[Ii]mplement', n.name)
            and not n.name.endswith('Exception')
        ],
    },
    "builder_pattern": {
        "desc": "Builder Pattern",
        "detect": lambda tree: [
            Finding("pattern", "builder_pattern", "info", n.lineno,
                    f"Builder pattern detected: {n.name}",
                    "Good for complex object construction")
            for n in ast.walk(tree)
            if isinstance(n, ast.ClassDef) and 'Builder' in n.name
        ],
    },
    "singleton_pattern": {
        "desc": "Singleton Pattern",
        "detect": lambda tree: [
            Finding("pattern", "singleton_pattern", "info", n.lineno,
                    f"Singleton pattern: {n.name}",
                    "Ensure thread-safety with lock")
            for n in ast.walk(tree)
            if isinstance(n, ast.ClassDef) and 'Singleton' in n.name
        ],
    },
    "factory_pattern": {
        "desc": "Factory Pattern",
        "detect": lambda tree: [
            Finding("pattern", "factory_pattern", "info", n.lineno,
                    f"Factory pattern: {n.name or 'func'}",
                    "Good abstraction for object creation")
            for n in ast.walk(tree)
            if isinstance(n, ast.FunctionDef) and re.search(r'create|factory|make', n.name, re.I)
        ],
    },
    "observer_pattern": {
        "desc": "Observer Pattern",
        "detect": lambda tree: [
            Finding("pattern", "observer_pattern", "info", n.lineno,
                    "Event/Observer pattern detected",
                    "Good for decoupling components")
            for n in ast.walk(tree)
            if isinstance(n, ast.ClassDef) and any(
                'observe' in m.name.lower() or 'listener' in m.name.lower()
                for m in n.body if isinstance(m, ast.FunctionDef)
            )
        ],
    },
}

ANTI_PATTERNS = {
    "god_class": {
        "desc": "God Class",
        "threshold": 15,  # max methods
        "severity": "warning",
        "detect": lambda classes: [
            Finding("anti_pattern", "god_class", "warning", c["line"],
                    f"God class: {c['name']} ({c['methods']} methods)",
                    "Split into smaller, focused classes")
            for c in classes if c["methods"] > 15
        ],
    },
    "long_function": {
        "desc": "Long Function",
        "threshold": 50,  # max lines
        "severity": "warning",
        "detect": lambda funcs: [
            Finding("anti_pattern", "long_function", "warning", f[1],
                    f"Long function: {f[0]} ({f[2]} lines)",
                    "Extract smaller functions")
            for f in funcs if f[2] > 50
        ],
    },
    "high_complexity": {
        "desc": "High Cyclomatic Complexity",
        "threshold": 10,
        "severity": "warning",
        "detect": lambda funcs_with_complexity: [
            Finding("anti_pattern", "high_complexity", "warning", f[1],
                    f"High complexity: {f[0]} (CC={f[2]})",
                    "Simplify with guard clauses or strategy pattern")
            for f in funcs_with_complexity if f[2] > 10
        ],
    },
    "deep_nesting": {
        "desc": "Deep Nesting",
        "threshold": 3,
        "severity": "warning",
        "detect": lambda depth: [
            Finding("anti_pattern", "deep_nesting", "warning", 1,
                    f"Deep nesting: {depth[0]} levels",
                    "Use guard clauses to flatten")
            for d in depth if d[0] > 3
        ],
    },
    "magic_numbers": {
        "desc": "Magic Numbers",
        "threshold": 5,
        "severity": "info",
        "detect": lambda source_lines: [
            Finding("anti_pattern", "magic_numbers", "info", i + 1,
                    f"Magic number: {m}",
                    "Extract to named constant")
            for i, line in enumerate(source_lines)
            for m in re.findall(r'\b(?<!\w)(\d{2,})(?!\w)', line)
            if not line.strip().startswith('#') and '=' not in line[:m.start()]
        ][:5],  # 最多报告5个
    },
    "eval_usage": {
        "desc": "Eval/Exec Usage",
        "severity": "critical",
        "detect": lambda tree: [
            Finding("anti_pattern", "eval_usage", "critical", n.lineno,
                    "eval()/exec() detected — security risk",
                    "Use ast.literal_eval() or proper parsing")
            for n in ast.walk(tree)
            if isinstance(n, ast.Call) and isinstance(n.func, ast.Name)
            and n.func.id in ('eval', 'exec')
        ],
    },
    "sql_injection": {
        "desc": "SQL Injection Risk",
        "severity": "critical",
        "detect": lambda source_lines: [
            Finding("anti_pattern", "sql_injection", "critical", i + 1,
                    "Potential SQL injection",
                    "Use parameterized queries")
            for i, line in enumerate(source_lines)
            if re.search(r'(execute|cursor\.execute)\s*\(\s*f["\']', line)
            or re.search(r'(execute|cursor\.execute)\s*\(.*%', line)
        ],
    },
    "hardcoded_secret": {
        "desc": "Hardcoded Secret",
        "severity": "critical",
        "detect": lambda source_lines: [
            Finding("anti_pattern", "hardcoded_secret", "critical", i + 1,
                    "Hardcoded secret/token/password",
                    "Use environment variables or secrets manager")
            for i, line in enumerate(source_lines)
            if re.search(r'''(?i)(password|secret|api_key|token|credential)\s*[:=]\s*["\'][a-zA-Z0-9]{8,}["\']''', line)
            and not line.strip().startswith('#')
        ],
    },
    "n_plus_one": {
        "desc": "N+1 Query Pattern",
        "severity": "warning",
        "detect": lambda source_lines: [
            Finding("anti_pattern", "n_plus_one", "warning", i + 1,
                    "Possible N+1 query in loop",
                    "Use bulk query or JOIN")
            for i, line in enumerate(source_lines)
            if re.search(r'for\s+\w+\s+in\s+.+:\s*\n\s+.+\.get\(|.+\.filter\(|.+\.query', line)
        ][:3],
    },
}


# ── 主分析器 ─────────────────────────────────────────────────────────────────

def analyze_python_source(source: str, filepath: str = "") -> AnalysisResult:
    """对 Python 源码进行完整的 AST 分析"""
    result = AnalysisResult(file=filepath, language="python")

    try:
        tree = ast.parse(source)
    except SyntaxError as e:
        result.findings.append(Finding("issue", "syntax_error", "critical", e.lineno,
                                        f"Syntax error: {e.msg}"))
        return result

    result.ast_tree = tree
    source_lines = source.split("\n")

    # ── 复杂度指标 ──
    cc = compute_cyclomatic_complexity(tree)
    nesting = compute_nesting_depth(tree)
    func_lengths = compute_function_lengths(tree)
    classes = compute_class_metrics(tree)

    result.metrics = [
        Metric("cyclomatic_complexity", cc, 10, "CC"),
        Metric("nesting_depth", nesting, 3, "levels"),
        Metric("max_function_lines", max((f[2] for f in func_lengths), default=0), 50, "lines"),
        Metric("max_class_methods", max((c["methods"] for c in classes), default=0), 15, "methods"),
        Metric("total_functions", len(func_lengths), 0, "funcs"),
        Metric("total_classes", len(classes), 0, "classes"),
    ]

    # ── 模式识别 ──
    for pattern_name, pattern in PATTERNS.items():
        try:
            result.findings.extend(pattern["detect"](tree))
        except Exception:
            pass

    # ── 反模式识别 ──
    for ap_name, ap in ANTI_PATTERNS.items():
        try:
            if ap_name == "god_class":
                result.findings.extend(ap["detect"](classes))
            elif ap_name == "long_function":
                result.findings.extend(ap["detect"](func_lengths))
            elif ap_name == "high_complexity":
                # 计算每个函数的复杂度
                func_cc = []
                for node in ast.walk(tree):
                    if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
                        func_cc.append((node.name, node.lineno, compute_cyclomatic_complexity(node)))
                result.findings.extend(ap["detect"](func_cc))
            elif ap_name == "deep_nesting":
                result.findings.extend(ap["detect"]([(nesting,)]))
            elif ap_name in ("magic_numbers", "sql_injection", "hardcoded_secret", "n_plus_one"):
                result.findings.extend(ap["detect"](source_lines))
            else:
                result.findings.extend(ap["detect"](tree))
        except Exception:
            pass

    # ── 提取模式（用于蒸馏） ──
    for f in result.findings:
        if f.category == "pattern":
            result.patterns.append({"name": f.name, "line": f.line, "file": filepath})

    return result


def analyze_file(filepath: str) -> AnalysisResult:
    """分析单个文件"""
    try:
        with open(filepath, 'r', encoding='utf-8', errors='ignore') as f:
            source = f.read()
    except Exception as e:
        result = AnalysisResult(file=filepath, language="unknown")
        result.findings.append(Finding("issue", "read_error", "critical", 0, str(e)))
        return result

    return analyze_python_source(source, filepath)
