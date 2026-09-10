#!/usr/bin/env python3
"""
Code Quality Guard v6 — 企业级质量守护系统
吸收 addyosmani/agent-skills 和 alirezarezvani/claude-skills 的优秀设计
"""

import ast
import re
import json
import os
import sys
from pathlib import Path
from typing import Dict, List, Tuple, Optional, Any
from dataclasses import dataclass, field, asdict
from datetime import datetime

# ============================================================================
# 六维评分系统 (吸收 addyosmani 的五轴 + 新增 Accessibility)
# ============================================================================

AXES = {
    "correctness": {"weight": 0.20, "name": "Correctness", "desc": "逻辑正确性、边界处理、错误处理"},
    "readability": {"weight": 0.15, "name": "Readability", "desc": "命名、结构、简洁性"},
    "architecture": {"weight": 0.20, "name": "Architecture", "desc": "分层、耦合、设计模式"},
    "security": {"weight": 0.20, "name": "Security", "desc": "密钥、注入、认证授权"},
    "performance": {"weight": 0.10, "name": "Performance", "desc": "查询、内存、算法复杂度"},
    "testing": {"weight": 0.10, "name": "Testing", "desc": "测试覆盖、边界用例"},
    "accessibility": {"weight": 0.05, "name": "Accessibility", "desc": "可访问性、国际化"},
}

# ============================================================================
# 数据模型
# ============================================================================

@dataclass
class Finding:
    """质量发现"""
    severity: str  # critical, required, optional, nit
    axis: str
    line: int
    description: str
    suggestion: str
    code_snippet: str = ""
    file_path: str = ""

@dataclass 
class ReviewResult:
    """审查结果"""
    file_path: str
    score: float
    axis_scores: Dict[str, float]
    findings: List[Finding]
    grade: str
    verdict: str  # approve, request_changes, reject

@dataclass
class Intent:
    """意图检测"""
    primary: str
    confidence: float
    all_intents: Dict[str, float] = field(default_factory=dict)

# ============================================================================
# 意图检测器 (吸收 OpenCode 的 Intent → Skill Mapping)
# ============================================================================

INTENT_PATTERNS = {
    "code-review": {
        "keywords": ["审查", "review", "检查", "check", "分析", "analyze", "评估", "evaluate", "评审", "assess"],
        "description": "代码审查任务"
    },
    "code-writing": {
        "keywords": ["实现", "implement", "编写", "write", "创建", "create", "构建", "build", "添加", "add", "开发", "develop"],
        "description": "代码编写任务"
    },
    "security-audit": {
        "keywords": ["安全", "security", "漏洞", "vulnerability", "注入", "injection", "密钥", "secret", "认证", "auth"],
        "description": "安全审计任务"
    },
    "debugging": {
        "keywords": ["修复", "fix", "调试", "debug", "解决", "resolve", "处理", "handle", "bug", "error"],
        "description": "调试修复任务"
    },
    "refactoring": {
        "keywords": ["重构", "refactor", "优化", "optimize", "整理", "clean", "简化", "simplify"],
        "description": "重构优化任务"
    },
    "testing": {
        "keywords": ["测试", "test", "用例", "case", "覆盖率", "coverage", "单测", "unit"],
        "description": "测试相关任务"
    },
    "architecture": {
        "keywords": ["架构", "architecture", "设计", "design", "模式", "pattern", "分层", "layer"],
        "description": "架构设计任务"
    },
    "performance": {
        "keywords": ["性能", "performance", "优化", "optimize", "慢", "slow", "耗时", "latency"],
        "description": "性能优化任务"
    },
}

class IntentDetector:
    """智能意图检测器"""
    
    def __init__(self):
        self.patterns = self._compile_patterns()
    
    def _compile_patterns(self) -> Dict[str, List[re.Pattern]]:
        compiled = {}
        for intent, config in INTENT_PATTERNS.items():
            compiled[intent] = [
                re.compile(kw, re.IGNORECASE) 
                for kw in config["keywords"]
            ]
        return compiled
    
    def detect(self, text: str) -> Intent:
        if not text:
            return Intent(primary="none", confidence=0.0)
        
        scores = {}
        for intent, patterns in self.patterns.items():
            score = sum(1 for p in patterns if p.search(text))
            if score > 0:
                scores[intent] = min(score / 3.0, 1.0)
        
        # 通用代码关键词
        code_keywords = ["code", "function", "class", "api", "数据库", "query", "实现", "编写"]
        code_count = sum(1 for kw in code_keywords if kw.lower() in text.lower())
        if code_count >= 2:
            scores["general-code"] = min(code_count * 0.1, 0.3)
        
        # 排序
        sorted_scores = sorted(scores.items(), key=lambda x: x[1], reverse=True)
        primary, confidence = sorted_scores[0] if sorted_scores else ("none", 0.0)
        
        return Intent(
            primary=primary,
            confidence=confidence,
            all_intents=dict(sorted_scores)
        )

# ============================================================================
# AST 分析器 (吸收 alirezarezvani 的 AST 分析)
# ============================================================================

class ASTAnalyzer:
    """Python AST 分析器"""
    
    def __init__(self, source: str, filepath: str = ""):
        self.source = source
        self.filepath = filepath
        self.tree = None
        try:
            self.tree = ast.parse(source)
        except SyntaxError:
            self.tree = None
    
    def analyze(self) -> Dict[str, Any]:
        if not self.tree:
            return {"error": "Syntax error in file"}
        
        return {
            "functions": self._count_functions(),
            "classes": self._count_classes(),
            "complexity": self._cyclomatic_complexity(),
            "nesting_depth": self._max_nesting_depth(),
            "line_count": len(self.source.splitlines()),
        }
    
    def _count_functions(self) -> int:
        return sum(1 for node in ast.walk(self.tree) if isinstance(node, ast.FunctionDef))
    
    def _count_classes(self) -> int:
        return sum(1 for node in ast.walk(self.tree) if isinstance(node, ast.ClassDef))
    
    def _cyclomatic_complexity(self) -> int:
        complexity = 1
        for node in ast.walk(self.tree):
            if isinstance(node, (ast.If, ast.While, ast.For, ast.ExceptHandler)):
                complexity += 1
            elif isinstance(node, ast.BoolOp):
                complexity += len(node.values) - 1
        return complexity
    
    def _max_nesting_depth(self) -> int:
        max_depth = 0
        
        def visit(node, depth=0):
            nonlocal max_depth
            if isinstance(node, (ast.If, ast.While, ast.For, ast.With, ast.Try)):
                max_depth = max(max_depth, depth + 1)
                for child in ast.iter_child_nodes(node):
                    visit(child, depth + 1)
            else:
                for child in ast.iter_child_nodes(node):
                    visit(child, depth)
        
        visit(self.tree)
        return max_depth

# ============================================================================
# 规则引擎 (吸收 addyosmani 的 Common Rationalizations 设计)
# ============================================================================

RULES = {
    "hardcoded_secret": {
        "severity": "critical",
        "axis": "security",
        "pattern": r"(password|secret|api_key|token|private_key)\s*=\s*['\"][^'\"]+['\"]",
        "description": "Hardcoded secret detected",
        "suggestion": "Use environment variables or secrets manager",
        "rationalization": "It's just for development",
        "reality": "Development secrets leak to production through logs, error messages, or version control"
    },
    "sql_injection": {
        "severity": "critical",
        "axis": "security",
        "pattern": r'execute\s*\(\s*f?["\'].*\{.*\}.*["\']',
        "description": "SQL injection risk",
        "suggestion": "Use parameterized queries",
        "rationalization": "The input is sanitized",
        "reality": "Sanitization can be bypassed; parameterized queries are the only safe approach"
    },
    "eval_usage": {
        "severity": "critical",
        "axis": "security",
        "pattern": r'\beval\s*\(',
        "description": "eval() usage detected",
        "suggestion": "Use ast.literal_eval() or a proper parser",
        "rationalization": "It's just parsing JSON",
        "reality": "eval() can execute arbitrary code; use safe alternatives"
    },
    "god_class": {
        "severity": "required",
        "axis": "architecture",
        "pattern": r"class\s+\w+.*:$",
        "description": "Class with too many methods",
        "suggestion": "Extract responsibilities into focused classes",
        "rationalization": "It's convenient to keep everything together",
        "reality": "God classes are hard to test, maintain, and understand; they violate SRP"
    },
    "deep_nesting": {
        "severity": "required",
        "axis": "readability",
        "description": "Nesting depth > 3 levels",
        "suggestion": "Use early return or guard clauses",
        "rationalization": "It makes the logic clearer",
        "reality": "Deep nesting makes code hard to follow; flatten with early returns"
    },
    "long_function": {
        "severity": "optional",
        "axis": "readability",
        "description": "Function > 50 lines",
        "suggestion": "Extract smaller, focused functions",
        "rationalization": "The function is cohesive",
        "reality": "Long functions are hard to test and understand; split by responsibility"
    },
    "no_error_handling": {
        "severity": "required",
        "axis": "correctness",
        "description": "Missing error handling",
        "suggestion": "Add try/except or equivalent error handling",
        "rationalization": "This code won't fail",
        "reality": "External calls can fail; handle errors gracefully"
    },
    "magic_number": {
        "severity": "nit",
        "axis": "readability",
        "description": "Magic number detected",
        "suggestion": "Extract to named constant",
        "rationalization": "The number is self-explanatory",
        "reality": "Named constants make intent explicit and enable easy changes"
    },
}

# ============================================================================
# 质量门禁 (吸收 constraints-driven-development 的设计)
# ============================================================================

class QualityGate:
    """质量门禁"""
    
    def __init__(self, config: Dict[str, Any] = None):
        self.config = config or {
            "min_score": 70,
            "blocking_severities": ["critical", "required"],
            "axis_minimums": {
                "security": 15,
                "correctness": 15,
                "architecture": 18,
            }
        }
    
    def check(self, result: ReviewResult) -> Tuple[bool, List[str]]:
        """检查是否通过门禁"""
        violations = []
        
        # 分数检查
        if result.score < self.config["min_score"]:
            violations.append(f"Score {result.score} below minimum {self.config['min_score']}")
        
        # 维度检查
        for axis, min_score in self.config.get("axis_minimums", {}).items():
            if result.axis_scores.get(axis, 0) < min_score:
                violations.append(f"{axis} score {result.axis_scores.get(axis, 0)} below minimum {min_score}")
        
        # 严重性检查
        for finding in result.findings:
            if finding.severity in self.config.get("blocking_severities", []):
                violations.append(f"[{finding.severity.upper()}] {finding.description} at {finding.file_path}:{finding.line}")
        
        return len(violations) == 0, violations

# ============================================================================
# 主分析器
# ============================================================================

class CodeQualityGuard:
    """主分析器"""
    
    def __init__(self):
        self.intent_detector = IntentDetector()
        self.gate = QualityGate()
    
    def review(self, filepath: str) -> ReviewResult:
        """审查单个文件"""
        with open(filepath, 'r', encoding='utf-8') as f:
            source = f.read()
        
        # AST 分析
        analyzer = ASTAnalyzer(source, filepath)
        ast_info = analyzer.analyze()
        
        # 规则匹配
        findings = []
        for rule_name, rule in RULES.items():
            if "pattern" in rule:
                matches = re.findall(rule["pattern"], source)
                if matches:
                    for match in matches:
                        line_num = source[:source.find(match)].count('\n') + 1
                        findings.append(Finding(
                            severity=rule["severity"],
                            axis=rule["axis"],
                            line=line_num,
                            description=rule["description"],
                            suggestion=rule["suggestion"],
                            code_snippet=match[:50],
                            file_path=filepath
                        ))
        
        # 计算分数
        axis_scores = self._calculate_axis_scores(source, findings, ast_info)
        composite = sum(axis_scores[axis] * AXES[axis]["weight"] for axis in AXES)
        
        # 定级
        grade = self._get_grade(composite)
        verdict = self._get_verdict(composite, findings)
        
        return ReviewResult(
            file_path=filepath,
            score=composite,
            axis_scores=axis_scores,
            findings=findings,
            grade=grade,
            verdict=verdict
        )
    
    def _calculate_axis_scores(self, source: str, findings: List[Finding], ast_info: Dict) -> Dict[str, float]:
        """计算各维度分数"""
        scores = {}
        
        for axis in AXES:
            base_score = 100
            axis_findings = [f for f in findings if f.axis == axis]
            
            # 扣分
            for finding in axis_findings:
                if finding.severity == "critical":
                    base_score -= 20
                elif finding.severity == "required":
                    base_score -= 10
                elif finding.severity == "optional":
                    base_score -= 5
                else:
                    base_score -= 2
            
            # AST 额外检查
            if axis == "architecture" and ast_info.get("classes", 0) > 0:
                for cls_name, cls_node in self._find_classes(source):
                    if len(cls_node.body) > 15:
                        base_score -= 15
                        findings.append(Finding(
                            severity="required",
                            axis="architecture",
                            line=cls_node.lineno,
                            description=f"God class: {cls_name} has {len(cls_node.body)} methods",
                            suggestion="Split into focused classes"
                        ))
            
            scores[axis] = max(0, min(20, base_score / 5))  # Normalize to 0-20 scale
        
        return scores
    
    def _find_classes(self, source: str) -> List[Tuple[str, ast.ClassDef]]:
        """查找类定义"""
        try:
            tree = ast.parse(source)
            return [(node.name, node) for node in ast.walk(tree) if isinstance(node, ast.ClassDef)]
        except:
            return []
    
    def _get_grade(self, score: float) -> str:
        """获取等级"""
        if score >= 90:
            return "Excellent"
        elif score >= 70:
            return "Good"
        elif score >= 50:
            return "Fair"
        else:
            return "Poor"
    
    def _get_verdict(self, score: float, findings: List[Finding]) -> str:
        """获取裁决"""
        critical_count = sum(1 for f in findings if f.severity == "critical")
        required_count = sum(1 for f in findings if f.severity == "required")
        
        if critical_count > 0 or score < 50:
            return "reject"
        elif required_count > 0 or score < 70:
            return "request_changes"
        else:
            return "approve"
    
    def detect_intent(self, text: str) -> Intent:
        """检测意图"""
        return self.intent_detector.detect(text)

# ============================================================================
# CLI 入口
# ============================================================================

def main():
    import argparse
    
    parser = argparse.ArgumentParser(description="Code Quality Guard v6")
    parser.add_argument("command", choices=["review", "intent", "gate", "score"])
    parser.add_argument("target", nargs="?", help="File or directory to analyze")
    parser.add_argument("--json", action="store_true", help="JSON output")
    parser.add_argument("--verbose", "-v", action="store_true", help="Verbose output")
    
    args = parser.parse_args()
    
    guard = CodeQualityGuard()
    
    if args.command == "intent":
        prompt = args.target or "实现一个用户认证API"
        intent = guard.detect_intent(prompt)
        
        if args.json:
            print(json.dumps({
                "primary": intent.primary,
                "confidence": round(intent.confidence, 2),
                "all_intents": {k: round(v, 2) for k, v in intent.all_intents.items()}
            }, indent=2))
        else:
            print(f"Primary Intent: {intent.primary} (confidence: {intent.confidence:.2f})")
            if intent.all_intents:
                print("\nAll detected intents:")
                for intent_name, confidence in intent.all_intents.items():
                    if intent_name != "none":
                        print(f"  - {intent_name}: {confidence:.2f}")
    
    elif args.command == "review":
        target = args.target or "."
        
        if os.path.isfile(target):
            results = [guard.review(target)]
        else:
            results = []
            for root, dirs, files in os.walk(target):
                for file in files:
                    if file.endswith(('.py', '.ts', '.js', '.go', '.java', '.rs')):
                        filepath = os.path.join(root, file)
                        try:
                            results.append(guard.review(filepath))
                        except Exception as e:
                            if args.verbose:
                                print(f"Error processing {filepath}: {e}")
        
        if args.json:
            print(json.dumps([asdict(r) for r in results], indent=2, default=str))
        else:
            print(f"\n{'='*60}")
            print(f"  Code Quality Review — {len(results)} file(s) analyzed")
            print(f"{'='*60}\n")
            
            for result in results:
                grade_emoji = {"Excellent": "🟢", "Good": "🟡", "Fair": "🟠", "Poor": "🔴"}.get(result.grade, "⚪")
                print(f"  {grade_emoji}   {result.score:.1f}/100  {result.grade}  [{result.verdict}]")
                print(f"     {result.file_path}")
                
                for axis, score in result.axis_scores.items():
                    bar_len = int(score / 2)
                    bar = "█" * bar_len + "░" * (10 - bar_len)
                    print(f"      [{axis:>12}] {bar}  {score:.0f}/20")
                
                if result.findings:
                    print(f"      Findings ({len(result.findings)}):")
                    for f in result.findings[:5]:
                        emoji = {"critical": "🔴", "required": "🟡", "optional": "🟠", "nit": "⚪"}.get(f.severity, "⚪")
                        print(f"        {emoji} L{f.line:>4} {f.description}")
                
                print()
            
            if results:
                avg = sum(r.score for r in results) / len(results)
                passed = sum(1 for r in results if r.verdict == "approve")
                print(f"  Summary: avg={avg:.1f}, passed={passed}/{len(results)}, pass_rate={passed/len(results)*100:.0f}%")
    
    elif args.command == "gate":
        target = args.target or "."
        
        if os.path.isfile(target):
            results = [guard.review(target)]
        else:
            results = []
            for root, dirs, files in os.walk(target):
                for file in files:
                    if file.endswith(('.py', '.ts', '.js', '.go', '.java', '.rs')):
                        filepath = os.path.join(root, file)
                        try:
                            results.append(guard.review(filepath))
                        except:
                            pass
        
        all_passed = True
        for result in results:
            passed, violations = guard.gate.check(result)
            if not passed:
                all_passed = False
                print(f"❌ {result.file_path}: {result.score:.1f}/100")
                for v in violations[:3]:
                    print(f"   - {v}")
        
        if all_passed and results:
            print("✅ Quality gate passed")
            sys.exit(0)
        elif not results:
            print("⚠️  No files to check")
            sys.exit(0)
        else:
            sys.exit(1)
    
    elif args.command == "score":
        target = args.target or "."
        result = guard.review(target) if os.path.isfile(target) else None
        
        if result:
            print(json.dumps({
                "score": result.score,
                "grade": result.grade,
                "verdict": result.verdict,
                "axis_scores": result.axis_scores,
                "findings_count": len(result.findings)
            }, indent=2))
        else:
            print({"error": "No results"})

if __name__ == "__main__":
    main()
