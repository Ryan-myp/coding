#!/usr/bin/env python3
"""
Skill Absorber
从 GitHub 优秀 skills 吸收最佳实践
"""

import json
import re
from pathlib import Path
from typing import Dict, List, Any
from dataclasses import dataclass, field


@dataclass
class SkillPattern:
    """技能模式"""
    name: str
    source: str  # GitHub repo or skill name
    category: str  # prompt-engineering, workflow, reflection
    description: str
    implementation: str
    quality_score: float = 0.0
    
    def to_dict(self) -> dict:
        return {
            "name": self.name,
            "source": self.source,
            "category": self.category,
            "description": self.description,
            "implementation": self.implementation[:300],
            "quality_score": self.quality_score
        }


class SkillAbsorber:
    """技能吸收器"""
    
    def __init__(self, project_dir: str = "."):
        self.project_dir = Path(project_dir)
        self.absorbed_file = self.project_dir / ".qguard" / "absorbed_patterns.json"
        self.absorbed_file.parent.mkdir(parents=True, exist_ok=True)
        self.patterns = self._load_absorbed()
    
    def _load_absorbed(self) -> List[Dict]:
        """加载已吸收的模式"""
        if self.absorbed_file.exists():
            with open(self.absorbed_file) as f:
                return json.load(f)
        return []
    
    def _save_absorbed(self):
        """保存吸收的模式"""
        with open(self.absorbed_file, 'w') as f:
            json.dump(self.patterns, f, indent=2)
    
    def absorb_from_github(self, repo_url: str, patterns: List[Dict]) -> List[SkillPattern]:
        """从 GitHub 吸收模式"""
        absorbed = []
        
        for pattern in patterns:
            skill = SkillPattern(
                name=pattern.get("name", "unknown"),
                source=repo_url,
                category=pattern.get("category", "general"),
                description=pattern.get("description", ""),
                implementation=pattern.get("implementation", ""),
                quality_score=pattern.get("score", 80.0)
            )
            
            # 检查是否已存在
            existing = self._find_pattern(skill.name)
            if not existing:
                self.patterns.append(skill.to_dict())
                absorbed.append(skill)
        
        self._save_absorbed()
        return absorbed
    
    def _find_pattern(self, name: str) -> Dict:
        """查找已有模式"""
        for p in self.patterns:
            if p.get("name") == name:
                return p
        return None
    
    def absorb_common_patterns(self) -> List[SkillPattern]:
        """吸收常见最佳实践"""
        patterns = [
            # Prompt Engineering
            SkillPattern(
                name="Role Prompting",
                source="multiple-agents",
                category="prompt-engineering",
                description="Assign a specific role/persona to the agent",
                implementation="""You are an expert software architect with 20 years of experience.
Your task is to review code for architecture quality.""",
                quality_score=95.0
            ),
            SkillPattern(
                name="Chain of Thought",
                source="multiple-agents",
                category="prompt-engineering",
                description="Ask agent to think step by step",
                implementation="""Let's think step by step:
1. First, understand the problem
2. Then, identify constraints
3. Next, design the solution
4. Finally, implement and verify""",
                quality_score=90.0
            ),
            SkillPattern(
                name="Self-Consistency",
                source="multiple-agents",
                category="prompt-engineering",
                description="Generate multiple solutions and compare",
                implementation="""Generate 3 different solutions to this problem.
Then compare them and choose the best one.""",
                quality_score=88.0
            ),
            # Workflow
            SkillPattern(
                name="Plan-Execute-Review",
                source="superpowers",
                category="workflow",
                description="Three-phase development workflow",
                implementation="""## Phase 1: Plan
Write a detailed plan before coding.

## Phase 2: Execute
Implement according to the plan.

## Phase 3: Review
Review and improve the result.""",
                quality_score=92.0
            ),
            SkillPattern(
                name="Self-Reflection",
                source="superpowers",
                category="workflow",
                description="Agent reflects on its own work",
                implementation="""After completing a task, reflect:
- What went well?
- What could be improved?
- What did I learn?""",
                quality_score=85.0
            ),
            # Context Engineering
            SkillPattern(
                name="Context Windows",
                source="open-code",
                category="context-engineering",
                description="Optimize context window usage",
                implementation="""Use structured context injection:
1. Project overview (1 paragraph)
2. Key files (list)
3. Current task (specific)
4. Constraints (clear)""",
                quality_score=87.0
            ),
            # Safety
            SkillPattern(
                name="Guardrails",
                source="cliner",
                category="safety",
                description="Set boundaries for agent behavior",
                implementation="""Rules:
- Never modify files outside src/
- Always run tests before commit
- Never hardcode secrets
- Ask for clarification when uncertain""",
                quality_score=90.0
            ),
            # Feedback
            SkillPattern(
                name="Feedback Loop",
                source="multiple-agents",
                category="feedback",
                description="Continuous improvement through feedback",
                implementation="""User feedback collected:
{feedback}

Improvements made:
1. {change1}
2. {change2}""",
                quality_score=83.0
            ),
        ]
        
        absorbed = []
        for pattern in patterns:
            existing = self._find_pattern(pattern.name)
            if not existing:
                self.patterns.append(pattern.to_dict())
                absorbed.append(pattern)
        
        self._save_absorbed()
        return absorbed
    
    def generate_enhanced_prompt(self, original_prompt: str, intent: str) -> str:
        """生成增强版 prompt"""
        enhanced = original_prompt
        
        # 添加角色设定
        if "You are" not in enhanced:
            role = self._get_role(intent)
            enhanced = f"{role}\n\n{enhanced}"
        
        # 添加思考步骤
        if "step by step" not in enhanced.lower():
            steps = self._get_steps(intent)
            enhanced = f"{enhanced}\n\n{steps}"
        
        # 添加约束
        if "Rules:" not in enhanced and "Constraints:" not in enhanced:
            rules = self._get_rules(intent)
            enhanced = f"{enhanced}\n\n{rules}"
        
        return enhanced
    
    def _get_role(self, intent: str) -> str:
        """获取角色设定"""
        roles = {
            "feature": "You are a senior software engineer specializing in feature development.",
            "fix": "You are a bug fix specialist with expertise in debugging and root cause analysis.",
            "refactor": "You are a code refactoring expert focused on maintainability and clean code.",
            "test": "You are a QA engineer specializing in comprehensive test coverage.",
            "optimize": "You are a performance engineer focused on optimization and efficiency."
        }
        return roles.get(intent, "You are an expert software engineer.")
    
    def _get_steps(self, intent: str) -> str:
        """获取思考步骤"""
        steps = {
            "feature": """
Think step by step:
1. Understand the requirement
2. Design the solution architecture
3. Implement core logic
4. Add error handling
5. Write tests
6. Review and refine""",
            "fix": """
Think step by step:
1. Reproduce the bug
2. Find root cause
3. Plan the fix
4. Implement minimal change
5. Verify no regressions
6. Add regression test""",
            "refactor": """
Think step by step:
1. Understand current behavior
2. Identify improvement areas
3. Plan incremental changes
4. Refactor with tests
5. Verify behavior unchanged
6. Document changes""",
            "test": """
Think step by step:
1. Identify testable units
2. Write boundary cases
3. Test error paths
4. Test happy paths
5. Achieve good coverage
6. Ensure tests are maintainable"""
        }
        return steps.get(intent, "Think through each step carefully.")
    
    def _get_rules(self, intent: str) -> str:
        """获取约束规则"""
        return """
Rules:
- Follow language-specific best practices
- Write clear, self-documenting code
- Handle errors gracefully
- Keep functions focused and small
- Add tests for new features
- Document public APIs"""
    
    def get_absorbed_stats(self) -> Dict:
        """获取吸收统计"""
        categories = {}
        for p in self.patterns:
            cat = p.get("category", "unknown")
            categories[cat] = categories.get(cat, 0) + 1
        
        return {
            "total_patterns": len(self.patterns),
            "by_category": categories,
            "average_score": sum(p.get("quality_score", 0) for p in self.patterns) / max(len(self.patterns), 1)
        }
    
    def generate_report(self) -> str:
        """生成吸收报告"""
        stats = self.get_absorbed_stats()
        
        report = f"""# Skill Absorption Report

## Statistics
- Total Patterns Absorbed: {stats['total_patterns']}
- Average Quality Score: {stats['average_score']:.1f}/100

## By Category
"""
        for cat, count in sorted(stats['by_category'].items()):
            report += f"- {cat}: {count}\n"
        
        report += "\n## Absorbed Patterns\n"
        for p in self.patterns:
            report += f"\n### {p.get('name')} ({p.get('source')})\n"
            report += f"- **Category**: {p.get('category')}\n"
            report += f"- **Score**: {p.get('quality_score', 0):.0f}/100\n"
            report += f"- **Description**: {p.get('description')}\n"
        
        return report


def main():
    import argparse
    parser = argparse.ArgumentParser(description="Skill Absorber")
    parser.add_argument("command", choices=["absorb", "generate", "enhance", "stats"])
    parser.add_argument("target", nargs="?", default=".")
    parser.add_argument("--intent", help="Intent type")
    parser.add_argument("--repo", help="GitHub repo URL")
    parser.add_argument("--json", action="store_true")
    args = parser.parse_args()
    
    absorber = SkillAbsorber(args.target)
    
    if args.command == "absorb":
        # 吸收常见模式
        patterns = absorber.absorb_common_patterns()
        print(f"Absorbed {len(patterns)} new patterns")
        for p in patterns:
            print(f"  - {p.name} ({p.category})")
    
    elif args.command == "generate":
        # 生成增强 prompt
        if not args.intent:
            print("Please provide --intent")
            return
        original = sys.stdin.read() if not sys.stdin.isatty() else "# Your task here"
        enhanced = absorber.generate_enhanced_prompt(original, args.intent)
        print(enhanced)
    
    elif args.command == "stats":
        stats = absorber.get_absorbed_stats()
        if args.json:
            print(json.dumps(stats, indent=2))
        else:
            print(f"Total patterns: {stats['total_patterns']}")
            print(f"Average score: {stats['average_score']:.1f}")
    
    elif args.command == "enhance":
        report = absorber.generate_report()
        print(report)


if __name__ == "__main__":
    import sys
    main()
