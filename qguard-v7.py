#!/usr/bin/env python3
"""
Code Quality Guard v7.0 — 顶级代码质量守护系统
整合所有创新功能：Context Engineering, EvoLearn, MITRE ATT&CK
"""

import argparse
import json
import sys
from pathlib import Path

# 添加路径
sys.path.insert(0, str(Path(__file__).parent / "scripts"))
sys.path.insert(0, str(Path(__file__).parent / "features"))

# 导入核心模块
try:
    from intent_detector import IntentDetector
except ImportError:
    from qguard import IntentDetector

try:
    from ast_analyzer import ASTAnalyzer
except ImportError:
    ASTAnalyzer = None

try:
    from ts_analyzer import TypeScriptAnalyzer
except ImportError:
    TypeScriptAnalyzer = None

try:
    from go_analyzer import GoAnalyzer
except ImportError:
    GoAnalyzer = None

try:
    from score_engine import ScoreEngine
except ImportError:
    ScoreEngine = None

try:
    from threat_modeler import ThreatModeler
except ImportError:
    ThreatModeler = None

try:
    from distiller import Distiller
except ImportError:
    Distiller = None

# 导入创新功能
try:
    from context_engine import ContextEngine
except ImportError:
    ContextEngine = None

try:
    from evo_learn import EvoLearn
except ImportError:
    EvoLearn = None

try:
    from threat_mapper import ThreatMapper
except ImportError:
    ThreatMapper = None

try:
    from health_trends import HealthTrends
except ImportError:
    HealthTrends = None

try:
    from pattern_library import PatternLibrary
except ImportError:
    PatternLibrary = None

try:
    from auto_fix import AutoFix
except ImportError:
    AutoFix = None

try:
    from adaptive_quality import AdaptiveQuality
except ImportError:
    AdaptiveQuality = None


class QGuardV7:
    """v7.0 主类"""
    
    def __init__(self, project_dir: str = "."):
        self.project_dir = Path(project_dir)
        
        # 初始化所有子系统
        self.intent_detector = IntentDetector()
        self.context_engine = ContextEngine(project_dir) if ContextEngine else None
        self.evo_learn = EvoLearn(project_dir) if EvoLearn else None
        self.threat_mapper = ThreatMapper(project_dir) if ThreatMapper else None
        self.health_trends = HealthTrends(project_dir) if HealthTrends else None
        self.pattern_library = PatternLibrary() if PatternLibrary else None
        self.auto_fix = AutoFix() if AutoFix else None
        self.adaptive_quality = AdaptiveQuality(project_dir) if AdaptiveQuality else None
        self.ts_analyzer = TypeScriptAnalyzer() if TypeScriptAnalyzer else None
        self.go_analyzer = GoAnalyzer() if GoAnalyzer else None
    
    def analyze(self, filepath: str, intent: str = None) -> dict:
        """综合分析"""
        # 1. 检测意图
        if not intent:
            intent = self.intent_detector.detect("code review")
        
        # 2. 注入上下文
        context = self.context_engine.analyze_context() if self.context_engine else {}
        injected_prompt = self.context_engine.inject_context(f"Review {filepath}") if self.context_engine else ""
        
        # 3. 读取代码
        try:
            with open(filepath, 'r', encoding='utf-8') as f:
                code = f.read()
        except:
            code = ""
        
        # 4. 生成报告
        report = {
            "intent": {
                "primary": intent.primary if hasattr(intent, 'primary') else "unknown",
                "confidence": intent.confidence if hasattr(intent, 'confidence') else 0.0
            },
            "context": context,
            "code_length": len(code),
            "features_available": {
                "context_engine": self.context_engine is not None,
                "evo_learn": self.evo_learn is not None,
                "threat_mapper": self.threat_mapper is not None,
                "health_trends": self.health_trends is not None,
                "pattern_library": self.pattern_library is not None,
                "auto_fix": self.auto_fix is not None,
                "adaptive_quality": self.adaptive_quality is not None
            }
        }
        
        return report
    
    def distill(self, source_dir: str, min_score: float = 90) -> dict:
        """模式蒸馏"""
        if not self.pattern_library:
            return {"error": "Pattern library not available"}
        
        # 扫描目录
        patterns = []
        for filepath in Path(source_dir).rglob("*.py"):
            try:
                with open(filepath, 'r') as f:
                    code = f.read()
                
                # 简单检测模式
                if "Repository" in code or "DAO" in code:
                    patterns.append({
                        "type": "repository",
                        "file": str(filepath),
                        "confidence": 0.9
                    })
                elif "Strategy" in code:
                    patterns.append({
                        "type": "strategy",
                        "file": str(filepath),
                        "confidence": 0.85
                    })
            except:
                pass
        
        return {"patterns": patterns, "count": len(patterns)}
    
    def generate_report(self, analysis: dict) -> str:
        """生成综合报告"""
        report = f"""
# Code Quality Guard v7.0 — Comprehensive Report

## Intent Analysis
**Primary Intent**: {analysis['intent']['primary']}
**Confidence**: {analysis['intent']['confidence']:.2f}

## Project Context
"""
        
        if analysis.get('context'):
            ctx = analysis['context']
            report += f"**Type**: {ctx.get('project_type', 'unknown')}\n"
            report += f"**Risk Level**: {ctx.get('risk_level', 'unknown')}\n"
            report += f"**Tech Stack**: {', '.join(ctx.get('tech_stack', {}).get('languages', []))}\n"
        
        report += f"""
## Code Stats
**File Length**: {analysis.get('code_length', 0)} characters

## Available Features
"""
        
        for feature, available in analysis.get('features_available', {}).items():
            status = "✅" if available else "❌"
            report += f"- {status} {feature.replace('_', ' ').title()}\n"
        
        return report


def main():
    parser = argparse.ArgumentParser(description="Code Quality Guard v7.0")
    parser.add_argument("command", choices=[
        "analyze", "distill", "report", "intent", "threat", "evo", "trend", "context", "ts", "go", "java", "rust", "security", "guide", "learn", "pattern", "skill", "template", "guide", "learn", "pattern"
    ])
    parser.add_argument("target", nargs="?", default=".")
    parser.add_argument("--intent", help="Specify intent")
    parser.add_argument("--json", action="store_true", help="JSON output")
    parser.add_argument("--min-score", type=float, default=90, help="Min score for distillation")
    parser.add_argument("--project-dir", default=".", help="Project directory")
    
    args = parser.parse_args()
    
    guard = QGuardV7(args.project_dir)
    
    if args.command == "analyze":
        result = guard.analyze(args.target, args.intent)
        if args.json:
            print(json.dumps(result, indent=2, default=str))
        else:
            print(guard.generate_report(result))
    
    elif args.command == "distill":
        result = guard.distill(args.target, args.min_score)
        print(json.dumps(result, indent=2))
    
    elif args.command == "report":
        results_file = Path(args.project_dir) / ".qguard" / "latest_analysis.json"
        if results_file.exists():
            with open(results_file) as f:
                analysis = json.load(f)
            print(guard.generate_report(analysis))
        else:
            print("No analysis found. Run 'analyze' first.")
    
    elif args.command == "intent":
        prompt = args.target or "实现用户认证API"
        result = guard.intent_detector.detect(prompt)
        if isinstance(result, dict):
            print(json.dumps(result, indent=2))
        else:
            print(json.dumps({
                "primary": getattr(result, 'primary', 'unknown'),
                "confidence": round(getattr(result, 'confidence', 0), 2),
                "all_intents": {k: round(v, 2) for k, v in getattr(result, 'all_intents', {}).items()}
            }, indent=2))
    
    elif args.command == "threat":
        if guard.threat_mapper:
            try:
                with open(args.target) as f:
                    code = f.read()
                model = guard.threat_mapper.generate_threat_model(code, args.target)
                print(guard.threat_mapper.generate_report(model))
            except Exception as e:
                print(f"Error: {e}")
        else:
            print("ThreatMapper not available")
    
    elif args.command == "evo":
        if guard.evo_learn:
            print(guard.evo_learn.generate_insight_report())
        else:
            print("EvoLearn not available")
    
    elif args.command == "trend":
        if guard.health_trends:
            trend = guard.health_trends.get_trend()
            print(json.dumps(trend, indent=2))
        else:
            print("HealthTrends not available")
    
    elif args.command == "context":
        if guard.context_engine:
            context = guard.context_engine.analyze_context()
            print(json.dumps(context, indent=2))
        else:
            print("ContextEngine not available")
    
    elif args.command == "ts":
        if guard.ts_analyzer:
            result = guard.ts_analyzer.analyze(args.target)
            if args.json:
                print(json.dumps(result.to_dict(), indent=2))
            else:
                print(guard.ts_analyzer.generate_report(result))
        else:
            print("TypeScriptAnalyzer not available")
    
    elif args.command == "go":
        if guard.go_analyzer:
            result = guard.go_analyzer.analyze(args.target)
            if args.json:
                print(json.dumps(result.to_dict(), indent=2))
            else:
                print(guard.go_analyzer.generate_report(result))
        else:
            print("GoAnalyzer not available")


if __name__ == "__main__":
    main()
