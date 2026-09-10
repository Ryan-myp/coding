#!/usr/bin/env python3
"""
STRIDE Threat Modeler — 六维自动化威胁检测
"""

import re
from pathlib import Path
from dataclasses import dataclass
from typing import Optional


STRIDE = {
    "spoofing": {
        "desc": "Spoofing — 身份伪造",
        "checks": [
            (r'(?i)(token|secret|password|key)\s*[=:]\s*["\x27][a-zA-Z0-9]{8,}',
             "Hardcoded credential", "Use env vars or secrets manager"),
            (r'(?i)Authorization:\s*Bearer\s+[a-zA-Z0-9]',
             "Exposed bearer token", "Remove from source code"),
            (r'(?i)(jwt|session)\s*=\s*None',
             "Missing auth check", "Add authentication middleware"),
        ],
    },
    "tampering": {
        "desc": "Tampering — 数据篡改",
        "checks": [
            (r'(?:execute|query|cursor)\s*\(\s*f["\x27]',
             "f-string SQL injection", "Use parameterized queries"),
            (r'(?:execute|query|cursor)\s*\(\s*.*%\s*\(?',
             "Format-string SQL injection", "Use parameterized queries"),
            (r'innerHTML\s*=',
             "XSS via innerHTML", "Use textContent or sanitize"),
            (r'eval\s*\(',
             "Dynamic code execution", "Use ast.literal_eval or parser"),
            (r'unpickle|marshal\.loads|yaml\.unsafe_load',
             "Insecure deserialization", "Use safe deserializer"),
        ],
    },
    "repudiation": {
        "desc": "Repudiation — 抵赖",
        "checks": [
            (r'#\s*TODO.*audit|#\s*TODO.*log',
             "Missing audit trail", "Add immutable audit logging"),
            (r'(?i)(delete|update|transfer)\s*\(.*\)\s*(?!.*log)',
             "Destructive op without audit", "Log all state-changing operations"),
        ],
    },
    "information_disclosure": {
        "desc": "Info Disclosure — 信息泄露",
        "checks": [
            (r'print\s*\(.*(?:traceback|exception|error|stack)',
             "Error details exposed", "Log internally, return generic message"),
            (r'return\s+.*(?:password|secret|token|credential)',
             "Sensitive data in response", "Sanitize response fields"),
            (r'(?i)logging\.(debug|info)\s*\(.*(?:password|token|secret|key)',
             "Sensitive data in logs", "Mask sensitive fields"),
            (r'expose_env_vars\s*=\s*True',
             "Environment variables exposed", "Restrict to required vars only"),
        ],
    },
    "denial_of_service": {
        "desc": "DoS — 拒绝服务",
        "checks": [
            (r'while\s+True:',
             "Potential infinite loop", "Add termination condition"),
            (r'requests\.(get|post|put|delete)\s*\([^)]*\)(?!\s*.*timeout)',
             "Missing request timeout", "Set explicit timeout"),
            (r'open\s*\([^)]+\.\s*read\(\s*\)',
             "Unbounded file read", "Limit read size"),
        ],
    },
    "elevation_of_privilege": {
        "desc": "Elevation — 权限提升",
        "checks": [
            (r'(?i)admin|root|superuser',
             "Privileged operation", "Verify admin role explicitly"),
            (r'(?i)if\s+.*(?:role|permission|auth)\s*is\s*None',
             "Missing permission check", "Add RBAC/ABAC middleware"),
            (r'request\.(params|body|json)\s*\[',
             "Direct request access", "Validate and sanitize input"),
        ],
    },
}


@dataclass
class Threat:
    category: str
    severity: str
    line: int
    description: str
    mitigation: str
    code_snippet: str = ""


class ThreatModeler:
    def __init__(self):
        self._compiled = {}
        for cat, config in STRIDE.items():
            self._compiled[cat] = []
            for pattern, desc, mitigation in config["checks"]:
                try:
                    self._compiled[cat].append((re.compile(pattern, re.IGNORECASE), desc, mitigation))
                except re.error:
                    pass

    def analyze_file(self, filepath: str) -> list:
        threats = []
        try:
            source = Path(filepath).read_text(errors="ignore")
        except Exception:
            return threats

        lines = source.split("\n")
        for cat, checks in self._compiled.items():
            for i, line in enumerate(lines, 1):
                for pattern, desc, mitigation in checks:
                    if pattern.search(line):
                        threats.append(Threat(
                            category=cat,
                            severity="critical" if cat in ("spoofing", "tampering") else "warning",
                            line=i,
                            description=f"{STRIDE[cat]['desc']}: {desc}",
                            mitigation=mitigation,
                            code_snippet=line.strip()[:80],
                        ).__dict__)
        return threats

    def analyze_dir(self, dirpath: str, max_files: int = 50) -> list:
        threats = []
        path = Path(dirpath)
        count = 0
        for ext in ['.py', '.ts', '.tsx', '.go', '.java', '.rs']:
            for f in path.rglob(f'*{ext}'):
                if count >= max_files:
                    break
                threats.extend(self.analyze_file(str(f)))
                count += 1
        return threats
