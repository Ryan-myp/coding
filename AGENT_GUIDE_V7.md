# Agent Code Generation Guide v7.5

## Problem Statement

Different people using the same AI coding agent (Codex, Claude, ChatGPT) produce wildly different code quality and style. This leads to:
- Inconsistent codebases
- Harder code reviews
- Maintenance nightmares
- Security vulnerabilities from inconsistent patterns

## Solution: Agent Code Generation Guide

A system that:
1. **Guides** agents to generate consistent code
2. **Learns** from successful generations
3. **Distills** best practices into reusable patterns
4. **Improves** over time

## Core Features

### 1. Intent Detection
Detect what the agent is trying to generate:
- `feature` — New feature implementation
- `fix` — Bug fix
- `refactor` — Code improvement
- `test` — Test generation
- `optimize` — Performance improvement

### 2. Context Injection
Before code generation, inject:
- Project type (web/mobile/backend)
- Tech stack (language/framework)
- Team conventions
- Security requirements
- Performance constraints

### 3. Multi-Language Support
- Python (AST-based analysis)
- TypeScript (rule-based)
- Go (rule-based)
- Java (rule-based)
- Rust (rule-based)

### 4. Security Analysis
- OWASP Top 10 coverage
- CWE mapping
- Risk scoring
- Remediation suggestions

### 5. Self-Learning
Track what works:
- Record successful generations
- Identify recurring issues
- Learn from fixes
- Improve over time

### 6. Pattern Distillation
Extract and learn from:
- Successful code patterns
- Common anti-patterns
- Team-specific conventions
- Industry best practices

## Commands

```bash
# Prepare generation context
python3 scripts/guide.py prepare --intent feature --language python

# Review generated code
python3 scripts/guide.py review generated_code.py

# Learn from success/failure
python3 features/self_learn.py record-success good_code.py
python3 features/self_learn.py record-failure bad_code.py "Error msg"

# Distill patterns
python3 features/pattern_distiller.py distill ./good-code/

# View stats
python3 features/self_learn.py stats
```

## Files

- `scripts/guide.py` — Main entry point
- `scripts/intent_detector.py` — Intent detection
- `scripts/*_analyzer.py` — Language-specific analyzers
- `scripts/security_analyzer.py` — OWASP security checks
- `features/self_learn.py` — Self-learning engine
- `features/pattern_distiller.py` — Pattern extraction
- `.github/workflows/quality-check.yml` — CI/CD integration

## GitHub

https://github.com/Ryan-myp/coding

## Next Steps (v7.6)

- [ ] Absorb more GitHub skill best practices
- [ ] Enhance pattern library (human + AI assisted)
- [ ] Add team custom rules support
- [ ] Integrate with more AI coding tools
