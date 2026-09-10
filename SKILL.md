---
name: code-quality-guard
description: "Multi-language AI code quality guard with 6-axis scoring, intent detection, STRIDE threat modeling, and pattern distillation. Use before merging any change, when writing code, reviewing code, or checking security. Auto-triggers on code-related tasks across Pi/Claude/Codex/Cursor/Copilot."
version: 6.0.0
author: ryan
tags: [code-quality, ast-analysis, security, testing, ci-cd, distillation, six-axis-scoring, intent-detection]
metadata:
  platforms: [linux, macos, windows]
  auto-trigger: true
  trigger-contexts: [code-generation, code-review, pr-check, commit, merge, security-audit]
---

# Code Quality Guard v6

A unified code quality engine for coding agents. Absorbs best practices from top open-source skills.

## Overview

Six-dimensional code quality analysis with intent-aware rule injection. Provides AST-based metrics, STRIDE threat modeling, design pattern distillation, and CI/CD quality gates.

**The approval standard:** Approve when the change definitely improves overall code health. Perfect code doesn't exist — the goal is continuous improvement. Don't block a change because it isn't exactly how you would have written it.

## The Six-Axis Review

Every review evaluates code across these dimensions:

### 1. Correctness (20%)
Does the code do what it claims to do?

- Does it match the spec or task requirements?
- Are edge cases handled (null, empty, boundary values)?
- Are error paths handled (not just the happy path)?
- Does it pass all tests? Are tests testing the right things?
- Are there race conditions, off-by-one errors, or state inconsistencies?

### 2. Readability (15%)
Can another engineer (or agent) understand this without explanation?

- Are names descriptive and consistent with project conventions?
- Is the control flow straightforward (avoid nested ternaries, deep callbacks)?
- Is the code organized logically (related code grouped, clear module boundaries)?
- **Could this be done in fewer lines?** (1000 lines where 100 suffice is a failure)
- **Are abstractions earning their complexity?** (Don't generalize until the third use case)

### 3. Architecture (20%)
Does the change fit the system's design?

- Does it follow existing patterns or introduce a new one? If new, is it justified?
- Does it maintain clean module boundaries?
- Is there code duplication that should be shared?
- Are dependencies flowing in the right direction (no circular dependencies)?
- Is the abstraction level appropriate (not over-engineered, not too coupled)?

### 4. Security (20%)
Does the change introduce vulnerabilities?

- Is user input validated and sanitized?
- Are secrets kept out of code, logs, and version control?
- Is authentication/authorization checked where needed?
- Are SQL queries parameterized (no string concatenation)?
- Are outputs encoded to prevent XSS?

### 5. Performance (10%)
Does the change introduce performance problems?

- Any N+1 query patterns?
- Any unbounded loops or unconstrained data fetching?
- Any synchronous operations that should be async?
- Any missing pagination on list endpoints?

### 6. Testing (10%)
Is the change properly tested?

- Are there tests for the new behavior?
- Are edge cases covered?
- Are error paths tested?
- Is test coverage adequate?

### 7. Accessibility (5%)
Is the code accessible and internationalized?

- Are labels and ARIA attributes present?
- Is color contrast sufficient?
- Are i18n strings extracted?

## When to Use

- Before merging any PR or change
- After completing a feature implementation
- When another agent or model produced code you need to evaluate
- When refactoring existing code
- After any bug fix (review both the fix and the regression test)
- When building features that accept untrusted data
- When implementing authentication or authorization

## Process: Intent Detection First

Before running checks, detect the user's intent to inject the right rules:

```bash
# Detect intent from prompt
python3 qguard.py intent "实现用户认证API"
# Output: Primary Intent: code-writing (confidence: 0.85)

# Run appropriate review
python3 qguard.py review src/
```

**Intent → Rule Mapping:**

| Intent | Injected Rules |
|--------|---------------|
| code-writing | Six-axis standards + architecture rules |
| code-review | Complete checklist + scoring rubric |
| security-audit | STRIDE threat model + OWASP Top 10 |
| debugging | Root cause analysis + prevention patterns |
| refactoring | Code smell detection + migration guide |
| testing | TDD workflow + coverage requirements |
| architecture | Layer separation + dependency rules |
| performance | Profiling guide + optimization patterns |

## Structural Remedies

When you flag a structural problem, propose the move — not just the problem:

- **Replace a chain of conditionals** with a typed model or explicit dispatcher
- **Collapse duplicate branches** into a single clearer flow
- **Separate orchestration from business logic** so each reads on its own
- **Move feature-specific logic** out of a shared module into the package that owns the concept
- **Reuse the canonical helper** instead of a bespoke near-duplicate
- **Make a type boundary explicit** so downstream branching disappears
- **Delete a pass-through wrapper** that adds indirection without clarifying the API
- **Extract a helper, or split a large file** into focused modules

Prefer the remedy that removes moving pieces over one that spreads the same complexity around.

## Change Sizing

Small, focused changes are easier to review, faster to merge, and safer to deploy:

```
~100 lines changed   → Good. Reviewable in one sitting.
~300 lines changed   → Acceptable if it's a single logical change.
~1000 lines changed  → Too large. Split it.
```

**What counts as "one change":** A single self-contained modification that addresses one thing, includes related tests, and keeps the system functional after submission.

## Common Rationalizations

| Rationalization | Reality |
|----------------|---------|
| "I'll add tests later" | Tests written after code are incomplete; TDD reveals design issues early |
| "This is simple enough to skip review" | Simple code often has subtle edge cases; review catches them |
| "The security check will catch it" | Security checks are automated; human review catches architectural issues |
| "It works on my machine" | Works locally ≠ works in production; test in representative environment |
| "This is a one-time script" | One-time scripts become production code; maintain them properly |
| "We're too busy for this" | Technical debt accumulates interest; paying it now is cheaper later |
| "The code is already bad" | Bad code attracts more bad code; stop the bleed |
| "Perfect is the enemy of good" | Good enough ≠ poor; raise the bar incrementally |

## Red Flags

Watch for these patterns indicating the skill is being violated:

- Skipping tests to meet deadlines
- Adding `eslint-disable` or `@ts-ignore` without justification
- Swallowing exceptions with bare `except:` or `catch (e) {}`
- Hardcoding secrets "just for now"
- Creating classes with 20+ methods
- Nesting more than 3 levels deep
- Writing functions longer than 50 lines
- Merging without review because "it's urgent"

## Quick Commands

| Command | Description |
|---------|-------------|
| `qguard review <path>` | Six-axis scoring of file/directory |
| `qguard intent <text>` | Detect intent from prompt |
| `qguard threats <path>` | STRIDE threat modeling |
| `qguard distill <path>` | Extract design patterns |
| `qguard gate <path>` | Quality gate (CI integration) |
| `qguard score <path>` | Quick score without details |

## Integration Points

### Pre-commit Hook
```bash
python3 ~/.agents/skills/code-quality-guard/scripts/qguard.py gate . --min-score 70
```

### GitHub Actions
```yaml
- uses: actions/setup-python@v5
- run: python3 code-quality-guard/scripts/qguard.py gate . --min-score 70
- run: python3 code-quality-guard/scripts/qguard.py threats src/ --json > threats.json
```

### biz-delivery Integration
```python
from integrations.biz_delivery.post_td_review import post_td_check
result = post_td_check(td_output_dir)
assert result["passed"], f"TD quality check failed: {result['avg_score']}"
```

## Anti-Patterns (Auto-Detected)

| Anti-Pattern | Severity | Detection | Fix |
|-------------|----------|-----------|-----|
| Hardcoded Secret | 🔴 Critical | `password`/`secret`/`api_key` = literal | Use env vars |
| SQL Injection | 🔴 Critical | `execute(f"...{var}...")` | Parameterized queries |
| Eval/Exec Usage | 🔴 Critical | `eval()` or `exec()` calls | Safe parsers |
| God Class | 🟡 Required | Class > 15 methods | Split classes |
| Long Function | 🟡 Optional | Function > 50 lines | Extract functions |
| High Complexity | 🟡 Required | Cyclomatic complexity > 10 | Guard clauses |
| Deep Nesting | 🟡 Required | Nesting depth > 3 | Early return |
| Magic Numbers | ⚪ Nit | Unexplained numeric literals | Named constants |
| N+1 Query | 🟠 Optional | DB query inside loop | Bulk query |

## Design Patterns (Auto-Detected)

| Pattern | Detection | Use Case |
|---------|-----------|----------|
| Repository | Class name contains "Repository"/"DAO" | Data access abstraction |
| Strategy | Class name contains "Strategy" | Algorithm family encapsulation |
| Builder | Class name contains "Builder" | Complex object construction |
| Factory | Function with "create"/"factory" | Object creation abstraction |
| Observer | Methods with "observe"/"listener" | Event-driven decoupling |
| Circuit Breaker | Class with "Breaker"/"Circuit" | Prevent cascade failures |
| Singleton | Class name contains "Singleton" | Global unique instance |
| Dependency Injection | Constructor/method injection | Loose coupling |
| Result Type | `Result<T, E>` or `Either<A, B>` | Explicit error handling |
| Option Pattern | Functional option/config patterns | Type-safe configuration |

## Quality Gate

Gate rules determine merge eligibility:

- **auto-approve**: score ≥ 90
- **conditional-pass**: score ≥ 70, no critical findings
- **needs-fix**: score ≥ 50, requires review
- **reject**: score < 50 or any critical finding

Configure in `policies/gate.json`.

## File Structure

```
code-quality-guard/
├── SKILL.md                          # This file
├── scripts/
│   ├── qguard.py                     # Unified CLI (v6)
│   ├── intent_detector.py            # Intent detection
│   ├── ast_analyzer.py               # AST-based analysis
│   ├── score_engine.py               # Six-axis scoring
│   ├── threat_modeler.py             # STRIDE threat modeling
│   ├── distiller.py                  # Pattern distillation
│   ├── metrics_dashboard.py          # Quality trends
│   └── badge_generator.py            # SVG badges
├── playbooks/
│   ├── tdd.sh                        # TDD workflow
│   ├── review.sh                     # Code review pipeline
│   ├── threat-model.sh               # Threat modeling
│   └── migrate.sh                    # Migration safety
├── ci/
│   └── quality-check.yml             # GitHub Actions
├── policies/
│   └── gate.json                     # Gate configuration
└── distillation/
    ├── patterns.json                 # Extracted patterns
    └── history.jsonl                 # Distillation history
```

## Version History

| Version | Date | Changes |
|---------|------|---------|
| v6.0 | 2025 | 6-axis scoring, intent detection, absorbed open-source best practices |
| v5.0 | 2025 | Multi-agent support, one-click install, bilingual detection |
| v4.0 | 2025 | AST-based analysis, 5-axis scoring, STRIDE, distillation |
| v3.0 | 2025 | 13 playbooks, threat modeling, improved patterns |
| v2.0 | 2025 | Multi-language, 4-role framework, GitHub push |
| v1.0 | 2025 | Initial Python-only version |
