#!/usr/bin/env python3
"""
Code Quality Integration
将 code-quality-guard 集成到 biz-delivery 系统
"""

import json
import subprocess
from pathlib import Path
from typing import Dict, List, Any, Optional
from datetime import datetime


class CodeQualityIntegration:
    """代码质量集成类"""
    
    def __init__(self, skill_path: str = None):
        # 尝试从环境变量或默认路径找到 skill
        self.skill_path = skill_path or self._find_skill_path()
        self.scripts_dir = Path(self.skill_path) / "scripts" if self.skill_path else None
        self.features_dir = Path(self.skill_path) / "features" if self.skill_path else None
    
    def _find_skill_path(self) -> Optional[str]:
        """查找 skill 路径"""
        # 检查几个可能的位置
        paths = [
            "/Users/yanping.ma/.agents/skills/code-quality-guard",
            Path.home() / ".agents/skills/code-quality-guard",
            Path(__file__).parent.parent.parent / "code-quality-guard",
        ]
        for p in paths:
            if p.exists() and (p / "scripts" / "qguard-v7.py").exists():
                return str(p)
        return None
    
    def analyze_file(self, filepath: str, language: str = "python") -> Dict:
        """分析单个文件"""
        if not self.skill_path:
            return {"error": "code-quality-guard skill not found"}
        
        cmd = [
            "python3", str(self.scripts_dir / "qguard-v7.py"),
            "analyze", filepath, "--language", language, "--json"
        ]
        
        try:
            result = subprocess.run(cmd, capture_output=True, text=True, timeout=30)
            if result.returncode == 0:
                return json.loads(result.stdout)
            else:
                return {"error": result.stderr}
        except Exception as e:
            return {"error": str(e)}
    
    def analyze_directory(self, dirpath: str, language: str = "python") -> Dict:
        """分析整个目录"""
        if not self.skill_path:
            return {"error": "code-quality-guard skill not found"}
        
        cmd = [
            "python3", str(self.scripts_dir / "qguard-v7.py"),
            "analyze", dirpath, "--language", language, "--json"
        ]
        
        try:
            result = subprocess.run(cmd, capture_output=True, text=True, timeout=60)
            if result.returncode == 0:
                return json.loads(result.stdout)
            else:
                return {"error": result.stderr}
        except Exception as e:
            return {"error": str(e)}
    
    def run_security_check(self, path: str) -> Dict:
        """运行安全检查"""
        if not self.skill_path:
            return {"error": "code-quality-guard skill not found"}
        
        cmd = [
            "python3", str(self.scripts_dir / "qguard-v7.py"),
            "security", path, "--json"
        ]
        
        try:
            result = subprocess.run(cmd, capture_output=True, text=True, timeout=60)
            if result.returncode == 0:
                return json.loads(result.stdout)
            else:
                return {"error": result.stderr}
        except Exception as e:
            return {"error": str(e)}
    
    def generate_guide(self, intent: str, language: str = "python") -> str:
        """生成代码生成指南"""
        if not self.skill_path:
            return "# Code Generation Guide\n\nSkill not available"
        
        cmd = [
            "python3", str(self.scripts_dir / "guide.py"),
            "prepare", "--intent", intent, "--language", language
        ]
        
        try:
            result = subprocess.run(cmd, capture_output=True, text=True, timeout=30)
            return result.stdout if result.returncode == 0 else f"Error: {result.stderr}"
        except Exception as e:
            return f"Error: {str(e)}"
    
    def get_feedback_stats(self) -> Dict:
        """获取反馈统计"""
        if not self.skill_path:
            return {"error": "Skill not found"}
        
        cmd = [
            "python3", str(self.features_dir / "feedback_loop.py"),
            "stats", "--json"
        ]
        
        try:
            result = subprocess.run(cmd, capture_output=True, text=True, timeout=30)
            if result.returncode == 0:
                return json.loads(result.stdout)
            else:
                return {"error": result.stderr}
        except Exception as e:
            return {"error": str(e)}
    
    def get_pattern_stats(self) -> Dict:
        """获取模式统计"""
        if not self.skill_path:
            return {"error": "Skill not found"}
        
        cmd = [
            "python3", str(self.features_dir / "enhanced_pattern_library.py"),
            "stats", "--json"
        ]
        
        try:
            result = subprocess.run(cmd, capture_output=True, text=True, timeout=30)
            if result.returncode == 0:
                return json.loads(result.stdout)
            else:
                return {"error": result.stderr}
        except Exception as e:
            return {"error": str(e)}
    
    def get_skill_stats(self) -> Dict:
        """获取技能吸收统计"""
        if not self.skill_path:
            return {"error": "Skill not found"}
        
        cmd = [
            "python3", str(self.features_dir / "skill_absorber.py"),
            "stats", "--json"
        ]
        
        try:
            result = subprocess.run(cmd, capture_output=True, text=True, timeout=30)
            if result.returncode == 0:
                return json.loads(result.stdout)
            else:
                return {"error": result.stderr}
        except Exception as e:
            return {"error": str(e)}
    
    def generate_report(self, filepath: str) -> str:
        """生成分析报告"""
        if not self.skill_path:
            return "Skill not available"
        
        cmd = [
            "python3", str(self.scripts_dir / "qguard-v7.py"),
            "report", filepath
        ]
        
        try:
            result = subprocess.run(cmd, capture_output=True, text=True, timeout=30)
            return result.stdout if result.returncode == 0 else f"Error: {result.stderr}"
        except Exception as e:
            return f"Error: {str(e)}"


def main():
    import argparse
    parser = argparse.ArgumentParser(description="Code Quality Integration for biz-delivery")
    parser.add_argument("command", choices=["analyze", "security", "guide", "stats"])
    parser.add_argument("target", nargs="?", default=".")
    parser.add_argument("--language", default="python")
    parser.add_argument("--intent", default="feature")
    args = parser.parse_args()
    
    integration = CodeQualityIntegration()
    
    if args.command == "analyze":
        if Path(args.target).is_dir():
            result = integration.analyze_directory(args.target, args.language)
        else:
            result = integration.analyze_file(args.target, args.language)
        print(json.dumps(result, indent=2))
    
    elif args.command == "security":
        result = integration.run_security_check(args.target)
        print(json.dumps(result, indent=2))
    
    elif args.command == "guide":
        guide = integration.generate_guide(args.intent, args.language)
        print(guide)
    
    elif args.command == "stats":
        stats = integration.get_skill_stats()
        print(json.dumps(stats, indent=2))


if __name__ == "__main__":
    main()
