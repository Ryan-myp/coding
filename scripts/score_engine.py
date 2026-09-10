#!/usr/bin/env python3
"""
Score Engine — 五轴评分核心引擎
基于 AST 分析结果，计算 Correctness/Readability/Architecture/Security/Performance
"""

from dataclasses import dataclass
import ast
import re
from ast_analyzer import AnalysisResult, Metric, Finding


@dataclass
class AxisScore:
    axis: str
    score: float       # 实际得分（满分 = max_score）
    max_score: float
    deductions: list   # 扣分原因
    metrics: list = None

    @property
    def percentage(self) -> float:
        return round(self.score / self.max_score * 100, 1) if self.max_score else 0


def score_correctness(result: AnalysisResult) -> AxisScore:
    """正确性：边界条件、错误处理、类型安全"""
    score = 20.0
    deductions = []

    # 检查是否有 error handling
    has_try = any(isinstance(n, ast.Try) for n in result.ast_tree.body) if result.ast_tree else False
    has_raise = any(isinstance(n, ast.Raise) for n in result.ast_tree.body) if result.ast_tree else False

    if not has_try and not has_raise:
        score -= 3
        deductions.append("No exception handling (try/raise)")

    # 检查边界条件
    has_none_check = False
    has_empty_check = False
    if result.ast_tree:
        for node in ast.walk(result.ast_tree):
            if isinstance(node, ast.Compare):
                if any(isinstance(c, ast.Constant) and c.value is None for c in node.comparators):
                    has_none_check = True
                if isinstance(node, ast.BoolOp) and any(
                    isinstance(n, ast.Compare) and any(
                        isinstance(c, ast.Constant) and c.value == 0 for c in (n.left if hasattr(n, 'left') else [])
                    ) for n in ast.walk(node)
                ):
                    has_empty_check = True
            if isinstance(node, ast.Call) and isinstance(node.func, ast.Attribute):
                if node.func.attr in ('__len__', 'count', 'size'):
                    has_empty_check = True

    if not has_none_check:
        score -= 2
        deductions.append("No null/None checks detected")

    # 从 findings 扣分
    critical_findings = [f for f in result.findings if f.severity == "critical"]
    for f in critical_findings:
        if f.name in ("eval_usage", "sql_injection", "hardcoded_secret"):
            score -= 5
            deductions.append(f"{f.name}: {f.message}")

    return AxisScore("correctness", max(0, score), 20, deductions)


def score_readability(result: AnalysisResult) -> AxisScore:
    """可读性：命名、函数长度、嵌套深度、重复代码"""
    score = 20.0
    deductions = []

    for m in result.metrics:
        if m.name == "max_function_lines" and m.value > 50:
            score -= 4
            deductions.append(f"Function > 50 lines ({m.value})")
        elif m.name == "nesting_depth" and m.value > 3:
            score -= 3
            deductions.append(f"Deep nesting ({m.value} levels)")
        elif m.name == "cyclomatic_complexity" and m.value > 10:
            score -= 3
            deductions.append(f"High cyclomatic complexity ({m.value})")

    # 检查命名规范
    source = ""
    if result.file:
        try:
            with open(result.file) as f:
                source = f.read()
        except:
            pass

    # 坏命名：单字母变量（非循环变量）
    bad_names = re.findall(r'\b(?:def|var|let|const)\s+(\w)\s*=', source)
    if len(bad_names) > 3:
        score -= 2
        deductions.append(f"Multiple single-letter variable names ({len(bad_names)})")

    # TODO/FIXME 遗留
    todos = len(re.findall(r'\bTODO\b|\bFIXME\b|\bHACK\b', source))
    if todos > 0:
        score -= min(todos, 3)
        deductions.append(f"{todos} TODO/FIXME comments")

    return AxisScore("readability", max(0, score), 20, deductions)


def score_architecture(result: AnalysisResult) -> AxisScore:
    """架构：分层、SRP、依赖方向"""
    score = 25.0
    deductions = []

    for m in result.metrics:
        if m.name == "max_class_methods" and m.value > 15:
            score -= 5
            deductions.append(f"God class: {m.value} methods")
        elif m.name == "max_function_lines" and m.value > 80:
            score -= 3
            deductions.append(f"Very long function: {m.value} lines")

    # 检查分层
    source = ""
    if result.file:
        try:
            with open(result.file) as f:
                source = f.read()
        except:
            pass

    has_service_layer = bool(re.search(r'class\s+\w*Service\w*', source))
    has_repository_layer = bool(re.search(r'class\s+\w*Repository\w*', source))
    has_controller = bool(re.search(r'class\s+\w*Controller\w*|@app\.(route|get|post)', source))

    if has_controller and not has_service_layer:
        score -= 3
        deductions.append("Controller calls DB directly (missing service layer)")

    if has_service_layer and not has_repository_layer:
        score -= 2
        deductions.append("Service layer without repository abstraction")

    # 循环依赖检测（简化版）
    import_count = len(re.findall(r'^(?:import|from)\s+', source, re.MULTILINE))
    if import_count > 10:
        score -= 2
        deductions.append(f"High coupling: {import_count} imports")

    return AxisScore("architecture", max(0, score), 25, deductions)


def score_security(result: AnalysisResult) -> AxisScore:
    """安全：STRIDE 六维 + OWASP Top10"""
    score = 20.0
    deductions = []

    critical_findings = [f for f in result.findings if f.severity == "critical"]
    warning_findings = [f for f in result.findings if f.severity == "warning"]

    for f in critical_findings:
        if f.name == "hardcoded_secret":
            score -= 8
            deductions.append(f"[Critical] {f.message}")
        elif f.name == "sql_injection":
            score -= 8
            deductions.append(f"[Critical] {f.message}")
        elif f.name == "eval_usage":
            score -= 6
            deductions.append(f"[Critical] {f.message}")
        else:
            score -= 4
            deductions.append(f"[Critical] {f.message}")

    for f in warning_findings:
        if f.name in ("n_plus_one", "deep_nesting", "high_complexity"):
            score -= 2
            deductions.append(f"[Warning] {f.message}")

    return AxisScore("security", max(0, score), 20, deductions)


def score_performance(result: AnalysisResult) -> AxisScore:
    """性能：N+1、算法复杂度、内存泄漏"""
    score = 15.0
    deductions = []

    for f in result.findings:
        if f.name == "n_plus_one":
            score -= 5
            deductions.append(f"N+1 query risk: {f.message}")
        elif f.name == "high_complexity":
            score -= 3
            deductions.append(f"Algorithmic complexity: {f.message}")

    # 检查大对象
    source = ""
    if result.file:
        try:
            with open(result.file) as f:
                source = f.read()
        except:
            pass

    large_lists = len(re.findall(r'\[\s*\d+\s*,\s*\d+\s*,\s*\d+\s*(?:,\s*\w+\s*){5,}', source))
    if large_lists > 0:
        score -= 2
        deductions.append(f"{large_lists} large inline lists (consider loading from file)")

    # 检查递归无终止
    if result.ast_tree:
        for node in ast.walk(result.ast_tree):
            if isinstance(node, ast.FunctionDef):
                for child in ast.walk(node):
                    if isinstance(child, ast.Call) and isinstance(child.func, ast.Name):
                        if child.func.id == node.name:
                            # 递归调用
                            passes = sum(1 for n in ast.walk(node) if isinstance(n, ast.Return))
                            if passes == 0:
                                score -= 3
                                deductions.append(f"Recursive function '{node.name}' may lack termination")

    return AxisScore("performance", max(0, score), 15, deductions)


# ── 评分调度 ──────────────────────────────────────────────────────────────────

SCORE_FUNCS = {
    "correctness": score_correctness,
    "readability": score_readability,
    "architecture": score_architecture,
    "security": score_security,
    "performance": score_performance,
}

WEIGHTS = {
    "correctness": 0.20,
    "readability": 0.20,
    "architecture": 0.25,
    "security": 0.20,
    "performance": 0.15,
}


def compute_composite(axes: dict) -> float:
    """计算加权综合分"""
    total = sum(axes[name].score * WEIGHTS[name] for name in WEIGHTS)
    return round(total, 1)


def grade(composite: float) -> tuple:
    """判定等级和门禁"""
    if composite >= 90:
        return "Excellent", "auto-approve"
    elif composite >= 70:
        return "Good", "conditional-pass"
    elif composite >= 50:
        return "Fair", "needs-fix"
    else:
        return "Poor", "reject"


def score_result(result: AnalysisResult) -> dict:
    """计算完整五轴评分"""
    axes = {}
    for axis_name, scorer in SCORE_FUNCS.items():
        axes[axis_name] = scorer(result)

    composite = compute_composite(axes)
    grade_name, gate = grade(composite)

    return {
        "file": result.file,
        "language": result.language,
        "composite_score": composite,
        "grade": grade_name,
        "gate": gate,
        "axes": {k: {"score": v.score, "max": v.max_score,
                      "percentage": v.percentage, "deductions": v.deductions}
                 for k, v in axes.items()},
        "distillation_candidate": composite >= 90,
        "metrics": [{"name": m.name, "value": m.value, "threshold": m.threshold,
                     "status": m.status} for m in result.metrics],
    }
