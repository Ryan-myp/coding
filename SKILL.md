# Code Quality Guard v4 — Multi-Language AI Code Review Skill

A unified code quality engine for coding agents (Codex/Cursor/Claude/Gemini/Copilot). Provides 5-axis scoring, STRIDE threat modeling, pattern distillation, and CI/CD quality gates.

## Quick Reference

| Command | Description |
|---------|-------------|
| `qguard review <path>` | Five-axis scoring of file/directory |
| `qguard threats <path>` | STRIDE threat modeling |
| `qguard distill <path>` | Extract design patterns from code |
| `qguard metrics` | Quality trend dashboard |
| `qguard gate <path>` | CI quality gate (exit 0/1) |
| `qguard badge <path>` | Generate quality badge SVG |

## Five-Axis Scoring System (0-100)

| Axis | Weight | Focus | Threshold |
|------|--------|-------|-----------|
| **Correctness** | 20% | Error handling, boundary conditions, null checks | ≥ 15 |
| **Readability** | 20% | Naming, function length (<50), nesting depth (≤3), TODOs | ≥ 15 |
| **Architecture** | 25% | Layering (controller→service→repository), coupling, god classes (<15 methods) | ≥ 18 |
| **Security** | 20% | Hardcoded secrets, SQL injection, eval/exec, auth checks | ≥ 15 |
| **Performance** | 15% | N+1 queries, recursion without termination, large inline data | ≥ 10 |

**Composite Score** = Σ(axis_score × weight). Grade: Excellent≥90 / Good≥70 / Fair≥50 / Poor<50.

## Gate Rules

- **auto-approve**: score ≥ 90
- **conditional-pass**: score ≥ 70, no critical issues
- **needs-fix**: score ≥ 50, requires review
- **reject**: score < 50 or any critical finding

## Design Patterns (Auto-Detected)

| Pattern | Detection | When to Use |
|---------|-----------|-------------|
| Repository | Class name contains "Repository"/"DAO"/"Mapper" | Data access abstraction |
| Strategy | Class name contains "Strategy" | Algorithm family encapsulation |
| Builder | Class name contains "Builder" | Complex object construction |
| Factory | Function/class with "create"/"factory" in name | Object creation abstraction |
| Observer | Methods with "observe"/"listener" | Event-driven decoupling |
| Circuit Breaker | Class with "Breaker"/"Circuit" | Prevent cascade failures |
| Singleton | Class name contains "Singleton" | Global unique instance |
| Dependency Injection | Constructor/method injection patterns | Loose coupling |
| Result Type | `Result<T, E>` or `Either<A, B>` patterns | Explicit error handling |
| Option Pattern | Functional option/config patterns | Type-safe configuration |

## Anti-Patterns (Auto-Detected)

| Anti-Pattern | Severity | Detection Rule | Fix |
|-------------|----------|---------------|-----|
| Hardcoded Secret | 🔴 Critical | `password`/`secret`/`api_key` = literal string | Use env vars or secrets manager |
| SQL Injection | 🔴 Critical | `execute(f"...{var}...")` or format-string SQL | Use parameterized queries |
| Eval/Exec Usage | 🔴 Critical | `eval()` or `exec()` calls | Use `ast.literal_eval()` or parser |
| God Class | 🟡 Warning | Class > 15 methods | Split into focused classes |
| Long Function | 🟡 Warning | Function > 50 lines | Extract smaller functions |
| High Complexity | 🟡 Warning | Cyclomatic complexity > 10 | Use guard clauses or strategy |
| Deep Nesting | 🟡 Warning | Nesting depth > 3 levels | Use early return/guard clauses |
| Magic Numbers | ℹ️ Info | Unexplained numeric literals > 2 digits | Extract to named constants |
| N+1 Query | 🟡 Warning | DB query inside loop | Use bulk query or JOIN |

## Architecture Checklist

```
✅ Separation of concerns: Controller → Service → Repository
✅ Dependency injection over global state
✅ Single Responsibility: one class/function per concern
✅ Interface segregation: narrow contracts
✅ Open/Closed: extensible via composition
✅ No god classes (>15 methods)
✅ No deep nesting (>3 levels)
✅ Explicit error handling (no swallowed exceptions)
```

## Security Checklist (STRIDE)

| Category | Check | Mitigation |
|----------|-------|------------|
| **Spoofing** | No hardcoded credentials | Env vars, secrets manager |
| **Tampering** | No SQL injection, XSS, eval() | Parameterized queries, sanitization |
| **Repudiation** | Audit trail for state changes | Immutable logging |
| **Info Disclosure** | No sensitive data in logs/responses | Mask PII, sanitize outputs |
| **DoS** | Request timeouts, bounded reads | Explicit limits |
| **Elevation** | Role checks on privileged ops | RBAC/ABAC middleware |

## Integration Points

### Pre-commit Hook
```bash
# .git/hooks/pre-commit
python3 ~/.agents/skills/code-quality-guard/scripts/qguard.py gate . --min-score 70
```

### CI/CD (GitHub Actions)
```yaml
# .github/workflows/quality-check.yml
- uses: actions/setup-python@v5
- run: python3 code-quality-guard/scripts/qguard.py gate . --min-score 70
- run: python3 code-quality-guard/scripts/qguard.py threats src/ --json > threats.json
```

### biz-delivery Integration
```python
# After TD phase
from integrations.biz_delivery.post_td_review import post_td_check
result = post_td_check(td_output_dir)
assert result["passed"], f"TD quality check failed: {result['avg_score']}"

# Before merge
from integrations.biz_delivery.pre_merge_gate import pre_merge_check
result = pre_merge_gate(pr_dir)
assert result["passed"], f"Merge gate failed: {result['avg_score']}"
```

## Playbooks

| Playbook | File | Use Case |
|----------|------|----------|
| TDD Workflow | `playbooks/tdd.sh` | Test-driven development enforcement |
| Code Review | `playbooks/review.sh` | Multi-phase review pipeline |
| Threat Modeling | `playbooks/threat-model.sh` | STRIDE analysis on source |
| Migration Safety | `playbooks/migrate.sh` | Schema/ auth change detection |
| Distillation | `playbooks/distillation.md` | Pattern extraction workflow |

## Distillation Engine

High-quality code (score ≥ 90) auto-qualifies as pattern candidates:

```bash
# Extract patterns from codebase
python3 qguard.py distill src/ --output distillation/patterns.json

# View history
python3 qguard.py metrics --last 30
```

Results stored in `distillation/history.jsonl` and `distillation/patterns.json`.

## File Structure

```
code-quality-guard/
├── SKILL.md                          # This file
├── scripts/
│   ├── qguard.py                     # Unified CLI entry point
│   ├── ast_analyzer.py               # AST-based code analysis
│   ├── score_engine.py               # Five-axis scoring engine
│   ├── threat_modeler.py             # STRIDE threat detection
│   ├── distiller.py                  # Pattern distillation
│   ├── metrics_dashboard.py          # Quality trend tracking
│   └── badge_generator.py            # SVG badge generation
├── playbooks/
│   ├── tdd.sh                        # TDD workflow script
│   ├── review.sh                     # Code review pipeline
│   ├── threat-model.sh               # Threat modeling
│   └── migrate.sh                    # Migration safety
├── ci/
│   └── quality-check.yml             # GitHub Actions workflow
├── policies/
│   └── gate.json                     # Quality gate configuration
├── integrations/
│   └── biz-delivery/                 # biz-delivery integration hooks
└── distillation/                     # Generated pattern database
    ├── patterns.json
    └── history.jsonl
```

## Usage Examples

```bash
# Review a single file
python3 qguard.py review src/payment_processor.py

# Review entire project
python3 qguard.py review src/ --max-files 100

# Threat model
python3 qguard.py threats src/ --json > threats.json

# Quality gate (for CI)
python3 qguard.py gate src/ --min-score 70
echo $?  # 0 = pass, 1 = fail

# Generate badge for README
python3 qguard.py badge src/ --output badge.svg

# Full review report
python3 qguard.py review src/ --json > report.json
```

## Multi-Language Support

| Language | AST Analysis | Pattern Detection | Security Scan |
|----------|-------------|-------------------|---------------|
| Python | ✅ | ✅ | ✅ |
| TypeScript | ✅ | ✅ | ✅ |
| Go | ✅ | ✅ | ✅ |
| Java | ✅ | ✅ | ✅ |
| Rust | ✅ | ✅ | ✅ |

## Development

```bash
# Install locally
pip install -e ~/.agents/skills/code-quality-guard

# Run tests
python3 -m pytest tests/ -v

# Add new language support
# 1. Add AST parser to ast_analyzer.py
# 2. Add language-specific patterns to distiller.py
# 3. Update multi-language table above
```

## Version History

| Version | Date | Changes |
|---------|------|---------|
| v4.0.0 | 2025 | AST-based analysis, 5-axis scoring, STRIDE, distillation, CI/CD |
| v3.0.0 | 2025 | 13 playbooks, threat modeling, improved patterns |
| v2.0.0 | 2025 | Multi-language, 4-role framework, GitHub push |
| v1.0.0 | 2025 | Initial Python-only version |
