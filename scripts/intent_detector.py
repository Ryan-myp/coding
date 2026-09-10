#!/usr/bin/env python3
"""
Code Quality Guard v5 — 智能意图检测器（简化版）
"""

import re
import sys
import json
from typing import List, Tuple, Dict

# 简化的意图关键词映射（中英双语）
INTENT_KEYWORDS = {
    "code-writing": {
        "keywords": ["实现", "编写", "创建", "添加", "构建", "开发", "implement", "write", "create", "build", "develop", "add", "make"],
        "priority": 1,
        "description": "代码编写"
    },
    "code-review": {
        "keywords": ["审查", "检查", "分析", "评估", "评审", "review", "check", "analyze", "evaluate", "assess"],
        "priority": 2,
        "description": "代码审查"
    },
    "security-review": {
        "keywords": ["安全", "漏洞", "注入", "密钥", "secret", "vulnerability", "injection", "threat", "security", "fix.*bug", "fix.*error"],
        "priority": 3,
        "description": "安全审查"
    },
    "debugging": {
        "keywords": ["修复", "调试", "解决", "处理", "fix", "debug", "resolve", "troubleshoot"],
        "priority": 4,
        "description": "调试修复"
    },
    "refactoring": {
        "keywords": ["重构", "优化", "整理", "refactor", "optimize", "restructure", "clean"],
        "priority": 5,
        "description": "重构优化"
    },
    "testing": {
        "keywords": ["测试", "用例", "单测", "集成测试", "test", "coverage", "unit test"],
        "priority": 6,
        "description": "测试相关"
    },
}

# 通用代码关键词（低权重）
GENERAL_CODE_KEYWORDS = [
    "代码", "函数", "类", "方法", "接口", "数据库", "查询", "API",
    "code", "function", "class", "method", "api", "database", "query",
    "impl", "service", "handler", "controller", "repository"
]


class IntentDetector:
    """智能意图检测器（简化版）"""
    
    def __init__(self):
        self.keyword_patterns = self._build_patterns()
    
    def _build_patterns(self) -> Dict[str, List[str]]:
        """构建关键词模式"""
        patterns = {}
        for intent, config in INTENT_KEYWORDS.items():
            patterns[intent] = [k.lower() for k in config["keywords"]]
        return patterns
    
    def detect(self, prompt: str) -> List[Tuple[str, float]]:
        """检测意图"""
        if not prompt:
            return []
        
        prompt_lower = prompt.lower()
        scores = {}
        
        # 1. 意图关键词匹配
        for intent, keywords in self.keyword_patterns.items():
            score = 0
            for keyword in keywords:
                if keyword in prompt_lower:
                    score += 1
            if score > 0:
                # 根据优先级加权
                priority = INTENT_KEYWORDS[intent]["priority"]
                scores[intent] = min(score * priority / 30.0, 1.0)
        
        # 2. 通用关键词匹配（低权重）
        general_count = 0
        for keyword in GENERAL_CODE_KEYWORDS:
            if keyword.lower() in prompt_lower:
                general_count += 1
        
        if general_count >= 2:
            scores["general-code"] = min(general_count * 0.05, 0.3)
        
        # 3. 排序并返回
        results = sorted(
            [(intent, score) for intent, score in scores.items() if score > 0],
            key=lambda x: x[1],
            reverse=True
        )
        
        return results if results else [("none", 0.0)]
    
    def get_primary_intent(self, prompt: str) -> str:
        """获取主要意图"""
        intents = self.detect(prompt)
        return intents[0][0] if intents else "none"
    
    def should_inject(self, prompt: str, min_confidence: float = 0.1) -> bool:
        """判断是否应该注入质量规则"""
        intents = self.detect(prompt)
        return any(score >= min_confidence for _, score in intents)
    
    def get_injection_rules(self, prompt: str) -> str:
        """获取要注入的质量规则"""
        intents = self.detect(prompt)
        primary_intent = intents[0][0] if intents else "none"
        
        rules_map = {
            "code-writing": """
## Code Quality Standards (Auto-Enforced)

### 🚨 Critical Rules
1. **No hardcoded secrets** — Use environment variables
2. **No SQL injection** — Use parameterized queries  
3. **No eval()/exec()** — Use safe parsers
4. **Error handling** — Every external call must have try/catch
5. **Input validation** — Validate all inputs

### 🏗️ Architecture Rules
6. **Layer separation** — Controller → Service → Repository
7. **Single Responsibility** — One class/function per concern
8. **No god classes** — Max 15 methods per class
9. **No deep nesting** — Max 3 levels, use early return

### ✅ Quality Gate
Before completing: Score ≥ 70 on all 5 axes
""",
            "code-review": """
## Code Review Checklist

Score each axis (0-100):
- **Correctness** (20%): Error handling, null checks, boundaries
- **Readability** (20%): Naming, function length, nesting  
- **Architecture** (25%): Layering, SRP, coupling
- **Security** (20%): Secrets, injection, auth
- **Performance** (15%): N+1 queries, timeouts

Pass threshold: Composite ≥ 70, no critical findings
""",
            "security-review": """
## STRIDE Threat Model

Check each dimension:
- **Spoofing**: No hardcoded credentials
- **Tampering**: No SQL injection, XSS, eval()
- **Repudiation**: Audit trail for state changes
- **Info Disclosure**: No sensitive data in logs
- **DoS**: Rate limiting, timeouts
- **Elevation**: Role checks on privileged ops
"""
        }
        
        return rules_map.get(primary_intent, rules_map["code-writing"])


def main():
    """命令行入口"""
    import argparse
    
    parser = argparse.ArgumentParser(description="Code Quality Guard Intent Detector")
    parser.add_argument("prompt", nargs="?", help="Input prompt to analyze")
    parser.add_argument("--verbose", "-v", action="store_true", help="Verbose output")
    parser.add_argument("--json", action="store_true", help="JSON output")
    
    args = parser.parse_args()
    
    detector = IntentDetector()
    
    if args.prompt:
        intents = detector.detect(args.prompt)
        
        if args.json:
            print(json.dumps({
                "prompt": args.prompt,
                "intents": [
                    {"intent": i, "confidence": round(c, 2)}
                    for i, c in intents
                ],
                "primary_intent": intents[0][0] if intents else "none",
                "should_inject": detector.should_inject(args.prompt)
            }, indent=2, ensure_ascii=False))
        elif args.verbose:
            print(f"Prompt: {args.prompt}")
            print(f"\nDetected Intents:")
            for intent, confidence in intents:
                bar = "█" * int(confidence * 20)
                desc = INTENT_KEYWORDS.get(intent, {}).get("description", "")
                print(f"  {intent:20s} {bar} ({confidence:.2f}) {desc}")
            print(f"\nPrimary Intent: {intents[0][0] if intents else 'none'}")
            print(f"Should Inject Rules: {detector.should_inject(args.prompt)}")
            
            if detector.should_inject(args.prompt):
                print(f"\nInjection Rules:\n{detector.get_injection_rules(args.prompt)}")
        else:
            if intents and intents[0][0] != "none":
                print(f"Intent: {intents[0][0]} (confidence: {intents[0][1]:.2f})")
            else:
                print("Intent: none")
    else:
        parser.print_help()
        print("\nExamples:")
        print('  python3 intent_detector.py "实现用户认证API"')
        print('  python3 intent_detector.py "修复SQL注入漏洞" --verbose')
        print('  python3 intent_detector.py "审查这段代码" --json')
        print('  python3 intent_detector.py "Implement a payment service"')


if __name__ == "__main__":
    main()
