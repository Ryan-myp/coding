#!/usr/bin/env python3
"""
Code Quality Distillation Engine v2
从优质代码中蒸馏模式，从问题代码中提取反模式
支持多语言，持续进化检查清单
"""

import json
import os
import re
import sys
from datetime import datetime
from pathlib import Path
from typing import Any

SKILL_DIR = Path(__file__).parent.parent
PATTERNS_DIR = SKILL_DIR / "references" / "patterns"
BAD_SMELLS_DIR = SKILL_DIR / "references" / "anti-patterns"
DISTILLATION_DIR = SKILL_DIR / "distillation"

# 语言文件扩展名映射
LANGUAGE_EXTENSIONS = {
    "python": [".py"],
    "typescript": [".ts", ".tsx", ".mts", ".cts"],
    "javascript": [".js", ".jsx", ".mjs", ".cjs"],
    "go": [".go"],
    "java": [".java"],
    "rust": [".rs"],
}

# 检测模式定义
PATTERN_DETECTIONS: dict[str, dict] = {
    "repository_pattern": {
        "regex": r"class\s+\w+Repository|interface\s+\w+Repository",
        "description": "Repository Pattern — 数据访问抽象",
        "language_tags": ["python", "typescript", "go", "java", "rust"],
    },
    "strategy_pattern": {
        "regex": r"class\s+\w+Strategy|interface\s+\w+Strategy",
        "description": "Strategy Pattern — 算法可切换",
        "language_tags": ["python", "typescript", "go", "java"],
    },
    "circuit_breaker": {
        "regex": r"class\s+\w*CircuitBreaker|def\s+circuit_breaker",
        "description": "Circuit Breaker — 防止级联故障",
        "language_tags": ["python", "typescript", "go", "java"],
    },
    "guard_clause": {
        "regex": r"(?:if\s+.*:\s*raise|return.*error|if\s+.*\{[^}]*return)",
        "description": "Guard Clause — 提前返回减少嵌套",
        "language_tags": ["python", "typescript", "go", "java", "rust"],
    },
    "builder_pattern": {
        "regex": r"class\s+\w+Builder|def\s+build\b",
        "description": "Builder Pattern — 复杂对象构建",
        "language_tags": ["python", "typescript", "go", "java"],
    },
    "option_pattern": {
        "regex": r"type\s+\w+Option|func\s+With\w+|type\s+Option\s+func",
        "description": "Option Pattern — 函数式配置",
        "language_tags": ["go", "typescript", "rust"],
    },
    "result_type": {
        "regex": r"type\s+Result|class\s+Result|dataclass\s+Result|enum\s+Result",
        "description": "Result/Option Type — 函数式错误处理",
        "language_tags": ["rust", "typescript", "python"],
    },
    "context_manager": {
        "regex": r"@contextmanager|with\s+open|ContextManager",
        "description": "Context Manager — 资源管理",
        "language_tags": ["python", "typescript", "rust"],
    },
}

# 反模式检测定义
ANTI_PATTERN_DETECTIONS: dict[str, dict] = {
    "hardcoded_url": {
        "regex": r'"https?://[^\s"\'>]{8,}"',
        "description": "硬编码 URL",
        "severity": "critical",
        "fix": "提取到配置文件或环境变量",
    },
    "hardcoded_secret": {
        "regex": r"(?:api[_-]?key|secret|password|token)\s*[=:]\s*['\"][^'\"]{8,}['\"]",
        "description": "硬编码密钥/密码",
        "severity": "critical",
    },
    "sql_injection_risk": {
        "regex": r'(?:execute|query|fetch)\s*\(\s*f["\']|(?:query|sql)\s*=\s*f["\'].*(?:SELECT|INSERT|UPDATE|DELETE)',
        "description": "SQL 注入风险（字符串拼接查询）",
        "severity": "critical",
    },
    "eval_usage": {
        "regex": r"\beval\s*\(",
        "description": "使用了 eval() — 安全漏洞",
        "severity": "critical",
    },
    "god_class": {
        "regex": r"class\s+\w+:",
        "count_methods": True,
        "threshold": 15,
        "description": "可能的上帝类（方法数 > 15）",
        "severity": "warning",
    },
    "long_function": {
        "regex": r"def\s+\w+",
        "count_lines": True,
        "threshold": 50,
        "description": "过长函数（> 50 行）",
        "severity": "warning",
    },
    "deep_nesting": {
        "regex": r"(?:if|for|while|match)\s*.*:",
        "max_depth": 4,
        "description": "嵌套过深（> 4 层）",
        "severity": "warning",
    },
    "debug_print": {
        "regex": r"\bprint\s*\(",
        "description": "调试遗留 print 语句",
        "severity": "info",
    },
    "unused_import": {
        "regex": r"^import\s+|^from\s+\S+\s+import",
        "description": "可能未使用的导入",
        "severity": "info",
    },
    "magic_number": {
        "regex": r"(?<!['\"])\b\d{2,}\b(?!['\"])",
        "description": "魔法数字",
        "severity": "info",
    },
}


def detect_language(file_path: str) -> str:
    """检测文件语言"""
    ext = Path(file_path).suffix.lower()
    for lang, extensions in LANGUAGE_EXTENSIONS.items():
        if ext in extensions:
            return lang
    return "unknown"


def extract_snippet(code: str, pattern: str, context_lines: int = 5) -> str:
    """从代码中提取匹配片段"""
    lines = code.split('\n')
    matches = list(re.finditer(pattern, code, re.MULTILINE))
    if not matches:
        return ""
    match = matches[0]
    start_pos = match.start()
    start_line = code[:start_pos].count('\n')
    end_line = min(len(lines), start_line + context_lines * 2)
    return '\n'.join(lines[start_line:end_line])


def analyze_patterns(code: str, language: str, source: str) -> dict:
    """分析代码中的设计模式"""
    found = {}
    for pattern_name, config in PATTERN_DETECTIONS.items():
        if language not in config.get("language_tags", []) and language != "unknown":
            continue
        if re.search(config["regex"], code, re.IGNORECASE):
            found[pattern_name] = {
                "name": config["description"],
                "source": source,
                "language": language,
                "example": extract_snippet(code, config["regex"]),
            }
    return found


def analyze_anti_patterns(code: str, language: str, source: str) -> list[dict]:
    """分析代码中的反模式"""
    issues = []
    lines = code.split('\n')

    for pattern_name, config in ANTI_PATTERN_DETECTIONS.items():
        if pattern_name == "god_class":
            # 统计类的方法数
            classes = re.findall(r'class\s+(\w+)', code)
            for cls_name in classes:
                # 简单估算：找类下面的方法
                class_match = re.search(rf'class\s+{re.escape(cls_name)}.*?(?=\nclass |\Z)', code, re.DOTALL)
                if class_match:
                    method_count = len(re.findall(r'\s+def\s+\w+|\s+public\s+\w+|\s+private\s+\w+|\s+protected\s+\w+', class_match.group()))
                    if method_count > config["threshold"]:
                        issues.append({
                            "type": pattern_name,
                            "name": f"{cls_name} — {config['description']}",
                            "severity": config["severity"],
                            "source": source,
                            "language": language,
                            "detail": f"Class has {method_count} methods (threshold: {config['threshold']})",
                            "fix": config.get("fix", "按职责拆分类"),
                        })
            continue

        if pattern_name == "long_function":
            functions = re.findall(r'(?:def|function|fn|func)\s+(\w+)\s*[^:]*:', code)
            for func_name in functions:
                func_match = re.search(rf'(?:def|function|fn|func)\s+{re.escape(func_name)}.*?(?=\n(?:def|function|fn|func)|\Z)', code, re.DOTALL)
                if func_match:
                    func_lines = len(func_match.group().split('\n'))
                    if func_lines > config["threshold"]:
                        issues.append({
                            "type": pattern_name,
                            "name": f"{func_name} — {config['description']}",
                            "severity": config["severity"],
                            "source": source,
                            "language": language,
                            "detail": f"Function has {func_lines} lines (threshold: {config['threshold']})",
                            "fix": config.get("fix", "拆分为多个小函数"),
                        })
            continue

        if re.search(config["regex"], code, re.IGNORECASE):
            issues.append({
                "type": pattern_name,
                "name": config["description"],
                "severity": config.get("severity", "info"),
                "source": source,
                "language": language,
                "fix": config.get("fix", "请人工评估修复方案"),
            })

    return issues


def distill(source_code: str, source_desc: str = "unknown") -> dict:
    """主蒸馏入口"""
    language = detect_language(source_desc)
    patterns = analyze_patterns(source_code, language, source_desc)
    anti_patterns = analyze_anti_patterns(source_code, language, source_desc)

    result = {
        "timestamp": datetime.now().isoformat(),
        "source": source_desc,
        "language": language,
        "patterns_found": patterns,
        "anti_patterns_found": anti_patterns,
        "summary": {
            "patterns_count": len(patterns),
            "anti_patterns_count": len(anti_patterns),
            "critical_count": sum(1 for a in anti_patterns if a["severity"] == "critical"),
            "warning_count": sum(1 for a in anti_patterns if a["severity"] == "warning"),
            "info_count": sum(1 for a in anti_patterns if a["severity"] == "info"),
        },
    }

    # 记录到蒸馏历史
    _append_distillation_log(result)

    return result


def distill_file(file_path: str) -> dict:
    """蒸馏单个文件"""
    with open(file_path, errors='replace') as f:
        code = f.read()
    return distill(code, file_path)


def distill_directory(dir_path: str, max_files: int = 50, languages: list[str] = None) -> dict:
    """蒸馏整个目录"""
    all_patterns: dict[str, dict] = {}
    all_anti_patterns: list[dict] = []
    files_processed = 0

    for root, _, files in os.walk(dir_path):
        if files_processed >= max_files:
            break
        for filename in files:
            if languages:
                lang = detect_language(filename)
                if lang not in languages:
                    continue
            file_path = os.path.join(root, filename)
            result = distill_file(file_path)
            files_processed += 1

            # 合并结果
            for name, pattern in result["patterns_found"].items():
                if name not in all_patterns:
                    all_patterns[name] = pattern
                else:
                    # 记录所有来源
                    if "examples" not in all_patterns[name]:
                        all_patterns[name]["examples"] = [all_patterns[name].get("example", "")]
                    all_patterns[name]["examples"].append(pattern.get("example", ""))
                    all_patterns[name]["sources"].append(pattern["source"])

            all_anti_patterns.extend(result["anti_patterns_found"])

    return {
        "patterns": all_patterns,
        "anti_patterns": all_anti_patterns,
        "files_processed": files_processed,
        "languages_found": list(set(
            r["language"]
            for r in [
                distill_file(os.path.join(root, f))
                for root, _, files in os.walk(dir_path)
                for f in files
                if any(f.endswith(ext) for exts in LANGUAGE_EXTENSIONS.values() for ext in exts)
            ]
        )),
    }


def _append_distillation_log(entry: dict):
    """追加蒸馏日志"""
    DISTILLATION_DIR.mkdir(parents=True, exist_ok=True)
    log_file = DISTILLATION_DIR / "history.jsonl"
    with open(log_file, "a", encoding="utf-8") as f:
        f.write(json.dumps(entry, ensure_ascii=False) + "\n")


def main():
    import argparse
    parser = argparse.ArgumentParser(description="Code Quality Distillation Engine v2")
    parser.add_argument("path", help="File or directory to distill")
    parser.add_argument("--max-files", type=int, default=50)
    parser.add_argument("--languages", nargs="*", help="Filter by language (python, typescript, go, java, rust)")
    parser.add_argument("--output", "-o", help="Output file (default: stdout)")
    args = parser.parse_args()

    if os.path.isfile(args.path):
        result = distill_file(args.path)
    elif os.path.isdir(args.path):
        result = distill_directory(args.path, args.max_files, args.languages)
    else:
        print(f"Error: {args.path} not found", file=sys.stderr)
        sys.exit(1)

    output = json.dumps(result, indent=2, ensure_ascii=False)
    if args.output:
        with open(args.output, "w", encoding="utf-8") as f:
            f.write(output)
        print(f"Results written to {args.output}")
    else:
        print(output)


if __name__ == "__main__":
    main()
