---
name: code-quality-guard
description: "Multi-language code quality skill that guides AI agents to generate consistent, high-quality code. Absorbs best practices and learns from successes/failures."
version: 7.9.0
author: ryan
tags: [code-quality, agent-guide, self-learning, patterns, multi-language]
metadata:
  platforms: [linux, macos, windows]
  auto-trigger: true
---

# Code Quality Guard

Guide AI agents to generate **consistent, high-quality code** across different users and projects.

## Problem Solved

Different people using the same AI coding agent produce wildly different code quality. This skill:
1. **Guides** — Inject context and rules before code generation
2. **Learns** — Record successes/failures, improve over time
3. **Distills** — Extract reusable patterns from good code
4. **Absorbs** — Learn from top GitHub skills
5. **Templates** — Pre-designed prompts for common scenarios

## Quick Start

### Analyze Code
```bash
# Python
python3 scripts/qguard-v7.py analyze src/ --language python

# TypeScript
python3 scripts/qguard-v7.py ts src/

# Security
python3 scripts/qguard-v7.py security src/
```

### Guide Code Generation
```bash
# Prepare context before generating code
python3 scripts/guide.py prepare --intent feature --language python

# Generate enhanced prompt
echo "# Add error handling" | python3 features/skill_absorber.py enhance --intent feature
```

### Learn & Improve
```bash
# Record success
python3 features/self_learn.py record-success good_code.py --tags "error-handling,type-hints"

# Record failure
python3 features/self_learn.py record-failure bad_code.py --error "Runtime error"

# View stats
python3 features/self_learn.py stats
```

### Manage Patterns & Skills
```bash
# Add pattern
python3 features/enhanced_pattern_library.py add --name "Proper Error Handling" --category "error-handling"

# Absorb best practices
python3 features/skill_absorber.py absorb

# View skills
python3 scripts/qguard-v7.py skill stats
```

### Use Templates
```bash
# List templates
python3 scripts/qguard-v7.py template feature

# Available templates: feature, fix, review, refactor, test, security
```

## Core Scripts

| Script | Purpose |
|--------|---------|
| `scripts/qguard-v7.py` | Unified CLI |
| `scripts/ast_analyzer.py` | Python AST analysis |
| `scripts/ts/go/java/rust_analyzer.py` | Multi-language support |
| `scripts/security_analyzer.py` | OWASP Top 10 security |
| `scripts/fix_suggester.py` | Fix suggestions + PR desc |
| `scripts/guide.py` | Code generation guide |
| `features/self_learn.py` | Self-learning engine |
| `features/enhanced_pattern_library.py` | Pattern management |
| `features/skill_absorber.py` | Absorb GitHub best practices |

## Templates

Pre-designed prompt templates for:
- **feature** — New feature implementation
- **fix** — Bug fix
- **review** — Code review
- **refactor** — Code improvement
- **test** — Test generation
- **security** — Security review

Plus team rules templates for Python, TypeScript, Go, Java, Rust.

## Integration

Works with:
- OpenAI Codex
- Claude
- ChatGPT
- GitHub Copilot
- Pi
- Any LLM-based code generator

## GitHub

https://github.com/Ryan-myp/coding
