#!/usr/bin/env python3
"""
Fix Suggester
生成可操作的修复建议和 PR 描述
"""

import json
from typing import List, Dict, Any


class FixSuggester:
    """修复建议生成器"""
    
    # 常见问题的修复模板
    FIX_TEMPLATES = {
        "eval": {
            "pattern": r"\beval\s*\(",
            "severity": "critical",
            "fix": "Use JSON.parse() or safe alternatives instead of eval()",
            "example_before": "const result = eval(userInput);",
            "example_after": "const result = JSON.parse(userInput);"
        },
        "exec": {
            "pattern": r"\bexec\s*\(",
            "severity": "critical",
            "fix": "Use subprocess with argument list instead of exec()",
            "example_before": "exec(command)",
            "example_after": "subprocess.run(command.split(), check=True)"
        },
        "sql_injection": {
            "pattern": r"execute\s*\(.*%s",
            "severity": "critical",
            "fix": "Use parameterized queries",
            "example_before": "cursor.execute('SELECT * FROM users WHERE id = %s' % user_id)",
            "example_after": "cursor.execute('SELECT * FROM users WHERE id = %s', (user_id,))"
        },
        "hardcoded_secret": {
            "pattern": r"(password|secret|api_key)\s*[:=]\s*['\"]",
            "severity": "critical",
            "fix": "Use environment variables or secret management",
            "example_before": "password = 'hardcoded_password123'",
            "example_after": "import os\npassword = os.environ.get('DB_PASSWORD')"
        },
        "any_type": {
            "pattern": r"\bany\b",
            "severity": "high",
            "fix": "Use specific types or generics",
            "example_before": "function process(data: any) {}",
            "example_after": "function process<T>(data: T): T {}"
        },
        "console_log": {
            "pattern": r"console\.(log|warn|error)",
            "severity": "medium",
            "fix": "Use a proper logging library",
            "example_before": "console.log('debug info')",
            "example_after": "logger.info('debug info', { requestId })"
        },
        "debug_true": {
            "pattern": r"debug\s*=\s*True",
            "severity": "high",
            "fix": "Disable debug mode in production",
            "example_before": "app.run(debug=True)",
            "example_after": "app.run(debug=os.environ.get('FLASK_DEBUG') == 'true')"
        },
        "no_error_handling": {
            "pattern": r"except\s*:\s*pass",
            "severity": "medium",
            "fix": "Log the exception or handle it properly",
            "example_before": "try:\n    do_something()\nexcept:\n    pass",
            "example_after": "try:\n    do_something()\nexcept Exception as e:\n    logger.error(f'Error: {e}')\n    raise"
        },
        "missing_auth": {
            "pattern": r"@app\.route\(.*\)\s*(?!.*@login_required)",
            "severity": "high",
            "fix": "Add authentication decorator",
            "example_before": "@app.route('/api/data')\ndef get_data():\n    return data",
            "example_after": "@app.route('/api/data')\n@login_required\ndef get_data():\n    return data"
        }
    }
    
    def suggest_fix(self, finding: Dict) -> Dict:
        """为单个发现生成修复建议"""
        message = finding.get("message", "")
        rule_id = finding.get("rule_id", "")
        
        # 查找匹配的修复模板
        for template_key, template in self.FIX_TEMPLATES.items():
            if template_key in rule_id.lower() or template_key in message.lower():
                return {
                    "issue": finding.get("message"),
                    "severity": finding.get("severity", "medium"),
                    "fix": template["fix"],
                    "example_before": template["example_before"],
                    "example_after": template["example_after"],
                    "priority": self._get_priority(template["severity"])
                }
        
        # 通用建议
        return {
            "issue": message,
            "severity": finding.get("severity", "medium"),
            "fix": "Review and fix this issue manually",
            "example_before": "",
            "example_after": "",
            "priority": "medium"
        }
    
    def _get_priority(self, severity: str) -> int:
        """将严重性转换为优先级数字"""
        priorities = {"critical": 1, "high": 2, "medium": 3, "low": 4}
        return priorities.get(severity, 4)
    
    def generate_pr_description(self, findings: List[Dict], language: str = "python") -> str:
        """生成 PR 描述"""
        # 按优先级排序
        sorted_findings = sorted(
            [self.suggest_fix(f) for f in findings],
            key=lambda x: x["priority"]
        )
        
        critical = [f for f in sorted_findings if f["severity"] == "critical"]
        high = [f for f in sorted_findings if f["severity"] == "high"]
        medium = [f for f in sorted_findings if f["severity"] == "medium"]
        low = [f for f in sorted_findings if f["severity"] == "low"]
        
        pr = f"""# Code Quality Review Results

**Language**: {language.capitalize()}
**Total Issues**: {len(findings)}
- 🔴 Critical: {len(critical)}
- 🟠 High: {len(high)}
- 🟡 Medium: {len(medium)}
- 🟢 Low: {len(low)}

"""
        
        if critical:
            pr += "## 🔴 Critical Issues (Must Fix)\n\n"
            for i, fix in enumerate(critical, 1):
                pr += f"### {i}. {fix['fix']}\n\n"
                pr += f"**Issue**: {fix['issue']}\n\n"
                if fix.get('example_before'):
                    pr += f"```{language}\n{fix['example_before']}\n```\n\n"
                    pr += f"```{language}\n{fix['example_after']}\n```\n\n"
                pr += "---\n\n"
        
        if high:
            pr += "## 🟠 High Priority Issues\n\n"
            for i, fix in enumerate(high, 1):
                pr += f"{i}. **{fix['fix']}**\n"
                pr += f"   - {fix['issue']}\n\n"
        
        if medium or low:
            pr += "## 📝 Other Issues\n\n"
            for fix in medium + low:
                pr += f"- {fix['issue'][:60]}...\n"
        
        pr += "\n---\n\n**Recommendation**: Address all critical and high issues before merging."
        
        return pr
    
    def generate_summary(self, findings: List[Dict]) -> Dict:
        """生成总结"""
        critical = len([f for f in findings if f.get("severity") == "critical"])
        high = len([f for f in findings if f.get("severity") == "high"])
        medium = len([f for f in findings if f.get("severity") == "medium"])
        low = len([f for f in findings if f.get("severity") == "low"])
        
        return {
            "total": len(findings),
            "critical": critical,
            "high": high,
            "medium": medium,
            "low": low,
            "blocking": critical > 0 or high > 0,
            "recommendation": "Block merge" if critical > 0 else ("Review required" if high > 0 else "Approve")
        }


def main():
    import argparse
    parser = argparse.ArgumentParser(description="Fix Suggester")
    parser.add_argument("--findings", help="Findings JSON string or file")
    parser.add_argument("--language", default="python")
    parser.add_argument("--output", help="Output file")
    args = parser.parse_args()
    
    suggester = FixSuggester()
    
    # 加载 findings
    if args.findings:
        if args.findings.endswith('.json'):
            with open(args.findings) as f:
                findings = json.load(f)
        else:
            findings = json.loads(args.findings)
    else:
        findings = []
    
    # 生成 PR 描述
    pr_desc = suggester.generate_pr_description(findings, args.language)
    summary = suggester.generate_summary(findings)
    
    result = {
        "summary": summary,
        "pr_description": pr_desc
    }
    
    if args.output:
        with open(args.output, 'w') as f:
            json.dump(result, f, indent=2)
        print(f"Results saved to {args.output}")
    else:
        print(json.dumps(result, indent=2))


if __name__ == "__main__":
    main()
