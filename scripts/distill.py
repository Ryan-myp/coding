#!/usr/bin/env python3
"""
Distillation Engine — 从优质代码中蒸馏最佳实践
持续进化检查清单和模式库
"""

import json
import os
import re
from datetime import datetime
from pathlib import Path

SKILL_DIR = Path(__file__).parent.parent
PATTERNS_DIR = SKILL_DIR / "references" / "patterns"
BAD_SMELLS_DIR = SKILL_DIR / "references" / "bad-smells"
DISTILLATION_LOG = SKILL_DIR / "distillation" / "log.md"


def ensure_dirs():
    """确保蒸馏目录存在"""
    (SKILL_DIR / "distillation").mkdir(exist_ok=True)
    PATTERNS_DIR.mkdir(exist_ok=True)
    BAD_SMELLS_DIR.mkdir(exist_ok=True)


def extract_patterns_from_code(code: str, source_desc: str = "") -> dict:
    """
    从代码中提取模式
    返回: {pattern_type: [patterns]}
    """
    patterns = {
        "design_patterns": [],
        "naming_conventions": [],
        "error_handling": [],
        "security_practices": [],
        "config_patterns": [],
    }

    # 检测 Repository 模式
    if re.search(r'class\s+\w+Repository', code):
        patterns["design_patterns"].append({
            "name": "Repository Pattern",
            "source": source_desc,
            "description": "数据访问层抽象，隔离业务逻辑与数据存储",
            "example_snippet": extract_snippet(code, r'class\s+\w+Repository', 10),
        })

    # 检测 Strategy 模式
    if re.search(r'class\s+\w+Strategy.*ABC|class\s+\w+Strategy.*Protocol', code, re.IGNORECASE):
        patterns["design_patterns"].append({
            "name": "Strategy Pattern",
            "source": source_desc,
            "description": "算法家族封装，运行时可切换",
            "example_snippet": extract_snippet(code, r'class\s+\w+Strategy', 15),
        })

    # 检测配置外化
    if re.search(r'os\.environ\.get|os\.environ\[', code):
        patterns["config_patterns"].append({
            "name": "Configuration Externalization",
            "source": source_desc,
            "description": "配置通过环境变量外部化，避免硬编码",
            "example_snippet": extract_snippet(code, r'os\.environ', 5),
        })

    # 检测参数化查询（防 SQL 注入）
    if re.search(r'execute\(.*%s|execute\(.*\?', code) or re.search(r'cursor\.execute.*\(', code):
        patterns["security_practices"].append({
            "name": "Parameterized Query",
            "source": source_desc,
            "description": "使用参数化查询防止 SQL 注入",
            "example_snippet": extract_snippet(code, r'execute\(.*\%', 5),
        })

    # 检测 Guard Clause 模式
    guard_count = len(re.findall(r'raise\s+\w+Error|return.*error|if.*:\s*raise', code))
    if guard_count >= 2:
        patterns["design_patterns"].append({
            "name": "Guard Clause Pattern",
            "source": source_desc,
            "description": "使用提前返回减少嵌套，提升可读性",
            "example_snippet": extract_snippet(code, r'if.*:', 10),
        })

    return patterns


def extract_snippet(code: str, pattern: str, context_lines: int = 5) -> str:
    """从代码中提取匹配模式的片段"""
    match = re.search(pattern, code)
    if not match:
        return ""
    lines = code.split('\n')
    start = max(0, match.start() // len(lines[0]) - context_lines if lines else 0)
    end = min(len(lines), start + context_lines * 2)
    return '\n'.join(lines[start:end])


def extract_bad_smells_from_code(code: str, source_desc: str = "") -> list[dict]:
    """从代码中提取反模式"""
    bad_smells = []

    # 检测硬编码 URL
    if re.search(r'"https?://[^\s"\']+"', code):
        bad_smells.append({
            "type": "hardcoded_url",
            "description": "硬编码的 URL/地址",
            "source": source_desc,
            "fix": "提取到配置文件或环境变量",
        })

    # 检测硬编码密钥
    if re.search(r'(api[_-]?key|secret|password|token)\s*=\s*["\'][^"\']{8,}["\']', code, re.IGNORECASE):
        bad_smells.append({
            "type": "hardcoded_secret",
            "description": "硬编码的密钥/密码",
            "source": source_desc,
            "fix": "使用环境变量或密钥管理服务",
        })

    # 检测上帝类（方法过多）
    method_count = len(re.findall(r'def\s+\w+', code))
    if method_count > 15:
        bad_smells.append({
            "type": "god_class",
            "description": f"类包含 {method_count} 个方法，可能是上帝类",
            "source": source_desc,
            "fix": "按职责拆分多个类",
        })

    # 检测过长函数
    functions = re.findall(r'def\s+\w+.*?:\n(?:\s.*?\n)*?(?=\ndef\s|\Z)', code, re.MULTILINE)
    for func in functions:
        line_count = len(func.split('\n'))
        if line_count > 50:
            bad_smells.append({
                "type": "long_function",
                "description": f"函数 '{re.match(r'def\s+(\w+)', func).group(1)}' 有 {line_count} 行",
                "source": source_desc,
                "fix": "拆分为多个小函数",
            })

    # 检测字符串拼接 SQL
    if re.search(r'execute\(f["\']|execute\(.*%\s|query\s*=\s*f["\'].*SELECT|query\s*=\s*".*SELECT.*"', code):
        bad_smells.append({
            "type": "sql_injection_risk",
            "description": "可能存在 SQL 注入风险（字符串拼接查询）",
            "source": source_desc,
            "fix": "改用参数化查询",
        })

    # 检测 print 语句（可能是调试遗留）
    if re.search(r'\bprint\s*\(', code):
        bad_smells.append({
            "type": "debug_print",
            "description": "存在 print 语句，可能是调试遗留",
            "source": source_desc,
            "fix": "改用 logging 模块",
        })

    return bad_smells


def distill(source_code: str, source_desc: str = "unknown") -> dict:
    """
    主蒸馏入口
    从代码中提取模式和反模式
    """
    ensure_dirs()

    patterns = extract_patterns_from_code(source_code, source_desc)
    bad_smells = extract_bad_smells_from_code(source_code, source_desc)

    # 记录蒸馏日志
    log_entry = {
        "timestamp": datetime.now().isoformat(),
        "source": source_desc,
        "patterns_found": sum(len(v) for v in patterns.values()),
        "bad_smells_found": len(bad_smells),
    }

    log_dir = SKILL_DIR / "distillation"
    log_dir.mkdir(exist_ok=True)
    log_file = log_dir / "log.jsonl"
    with open(log_file, "a") as f:
        f.write(json.dumps(log_entry, ensure_ascii=False) + "\n")

    return {
        "patterns": patterns,
        "bad_smells": bad_smells,
        "log_entry": log_entry,
    }


def distill_file(file_path: str) -> dict:
    """蒸馏单个文件"""
    with open(file_path) as f:
        code = f.read()
    return distill(code, source_desc=file_path)


def distill_directory(dir_path: str, max_files: int = 50) -> dict:
    """蒸馏整个目录"""
    results = {"patterns": {}, "bad_smells": [], "files_processed": 0}

    for root, dirs, files in os.walk(dir_path):
        if results["files_processed"] >= max_files:
            break
        for filename in files:
            if filename.endswith(('.py', '.js', '.ts', '.go', '.java', '.rb')):
                file_path = os.path.join(root, filename)
                result = distill_file(file_path)
                results["files_processed"] += 1

                # 合并模式
                for ptype, items in result["patterns"].items():
                    if ptype not in results["patterns"]:
                        results["patterns"][ptype] = []
                    results["patterns"][ptype].extend(items)

                results["bad_smells"].extend(result["bad_smells"])

    return results


def main():
    import argparse
    parser = argparse.ArgumentParser(description="Code Quality Distillation Engine")
    parser.add_argument("path", help="File or directory to distill")
    parser.add_argument("--max-files", type=int, default=50, help="Max files to process")
    args = parser.parse_args()

    if os.path.isfile(args.path):
        result = distill_file(args.path)
    else:
        result = distill_directory(args.path, args.max_files)

    print(json.dumps(result, indent=2, ensure_ascii=False))


if __name__ == "__main__":
    main()
