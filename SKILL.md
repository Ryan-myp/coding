---
name: code-quality-guard
description: "Multi-language code quality guard with intent detection, self-learning, and pattern distillation. Guides AI agents to generate consistent code."
version: 7.6.0
author: ryan
tags: [code-quality, agent-guide, self-learning, patterns, multi-language]
metadata:
  platforms: [linux, macos, windows]
  auto-trigger: true
  trigger-contexts: [code-generation, code-review, security-check]
---

# Code Quality Guard v7.6

Multi-language code quality system that **guides AI agents** to generate consistent, high-quality code. Solves the problem of inconsistent code when different people use the same AI tool.

## Core Capabilities

### 1. Multi-Language Analysis
- **Python**: AST-based analysis, PEP 8 compliance
- **TypeScript**: Strict type checking, no `any`
- **Go**: Idiomatic Go, error handling
- **Java**: SOLID principles, null safety
- **Rust**: Ownership, error handling

### 2. Intent Detection (Bilingual)
- `feature` — New feature implementation
- `fix` — Bug fix
- `refactor` — Code improvement
- `test` — Test generation
- `optimize` — Performance improvement
- `general` — General code guidance

### 3. Security Analysis (OWASP Top 10)
- A01: Broken Access Control
- A02: Cryptographic Failures
- A03: Injection
- A04: Insecure Design
- A05: Security Misconfiguration
- A06: Vulnerable Components
- A07: Auth Failures
- A08: Software/Data Integrity
- A09: Logging Failures
- A10: SSRF

### 4. Self-Learning Engine
- Record successful generations
- Learn from failures
- Track improvement over time
- Calculate success rates

### 5. Pattern Distillation
- Extract reusable patterns
- Build team-specific library
- Filter by language/category
- Track pattern effectiveness

### 6. Skill Absorption
- Absorb best practices from GitHub
- Enhance prompts with role-playing
- Add chain-of-thought reasoning
- Apply guardrails and constraints

### 7. Team Custom Rules
- Define team-specific conventions
- Language-specific rules
- Severity levels (error/warning/info)
- Auto-injected into prompts

### 8. CI/CD Integration
- GitHub Actions workflow
- Pre-commit hooks
- VS Code integration
- GitLab CI support

## Quick Start

### Analyze Code
```bash
# Single file
python3 scripts/qguard-v7.py analyze path/to/file.py

# Multiple files
python3 scripts/qguard-v7.py analyze src/ --language python

# With fix suggestions
python3 scripts/qguard-v7.py analyze path/to/file.py --suggest
```

### Generate Guide
```bash
# Prepare context before generation
python3 scripts/guide.py prepare --intent feature --language python

# Generate enhanced prompt
echo "# Your task" | python3 features/skill_absorber.py enhance --intent feature
```

### Learn & Improve
```bash
# Record success
python3 features/self_learn.py record-success good_code.py --intent feature --tags "type-hint,error-handling"

# Record failure
python3 features/self_learn.py record-failure bad_code.py --error "Runtime error"

# View stats
python3 features/self_learn.py stats

# Generate report
python3 features/self_learn.py report
```

### Manage Patterns
```bash
# Add pattern manually
python3 features/enhanced_pattern_library.py add --name "Proper Error Handling" --category "error-handling" --language python

# Search similar patterns
cat code.py | python3 features/enhanced_pattern_library.py search --language python

# View stats
python3 features/enhanced_pattern_library.py stats

# Generate report
python3 features/enhanced_pattern_library.py report
```

### Absorb Skills
```bash
# Absorb common patterns
python3 features/skill_absorber.py absorb

# View stats
python3 features/skill_absorber.py stats
```

### Security Check
```bash
python3 scripts/qguard-v7.py security . --language python
```

### Generate Fix Suggestions
```bash
python3 scripts/fix_suggester.py suggest path/to/file.py
python3 scripts/fix_suggester.py pr-desc --diff
```

## Commands

| Command | Description |
|---------|-------------|
| `analyze` | Analyze code with AST/rule-based checks |
| `distill` | Extract patterns from good code |
| `report` | Generate quality report |
| `intent` | Detect generation intent |
| `threat` | STRIDE threat modeling |
| `evo` | Evolution tracking |
| `trend` | Quality trend analysis |
| `context` | Generate context injection |
| `ts/go/java/rust/security` | Language-specific checks |
| `guide` | Prepare generation context |
| `learn` | Record and query learning |
| `pattern` | Manage pattern library |

## File Structure

```
code-quality-guard/
├── scripts/
│   ├── qguard-v7.py         # Unified CLI
│   ├── ast_analyzer.py      # Python AST analysis
│   ├── ts_analyzer.py       # TypeScript analysis
│   ├── go_analyzer.py       # Go analysis
│   ├── java_analyzer.py     # Java analysis
│   ├── rust_analyzer.py     # Rust analysis
│   ├── security_analyzer.py # OWASP security
│   ├── fix_suggester.py     # Fix suggestions
│   └── guide.py             # Code generation guide
├── features/
│   ├── self_learn.py        # Self-learning engine
│   ├── pattern_distiller.py # Pattern extraction
│   ├── enhanced_pattern_library.py # Enhanced pattern library
│   └── skill_absorber.py    # Skill absorption
├── policies/
│   ├── gate.json            # Quality gates
│   └── team_rules.md        # Team custom rules
├── integrations/
│   └── .github/workflows/   # CI/CD workflows
├── .vscode/                 # VS Code integration
├── AGENT_GUIDE_V7.md        # Documentation
└── SKILL.md                 # This file
```

## Integration Points

- **GitHub Actions**: `.github/workflows/quality-check.yml`
- **VS Code**: `.vscode/settings.json`
- **Git Hooks**: `hooks/pre-commit.sh`
- **GitLab CI**: Supported via YAML

## GitHub

https://github.com/Ryan-myp/coding

## Version History

- v7.0 — Foundation + honest documentation
- v7.1 — TypeScript analyzer
- v7.2 — Go/Java/Rust analyzers
- v7.3 — OWASP Top 10 security
- v7.4 — Fix suggestions + CI/CD
- v7.5 — Agent code generation guide + self-learning
- v7.6 — Skill absorption + enhanced pattern library + team rules + tool integration

## Philosophy

- **Practical**: Real tools, not buzzwords
- **Honest**: No exaggerated AI claims
- **Learnable**: Self-improving through usage
- **Flexible**: Works with any AI coding tool
