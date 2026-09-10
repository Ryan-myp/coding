---
name: code-quality-guard
description: "Multi-language code quality skill that guides AI agents to generate consistent, high-quality code. Includes feedback loop for continuous improvement."
version: 7.10.0
author: ryan
tags: [code-quality, agent-guide, self-learning, patterns, multi-language, feedback]
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
6. **Feedback** — User feedback loop for continuous improvement

## Quick Start

### Analyze Code
```bash
python3 scripts/qguard-v7.py analyze src/ --language python
python3 scripts/qguard-v7.py security src/
```

### Guide Code Generation
```bash
python3 scripts/guide.py prepare --intent feature --language python
```

### Learn & Improve
```bash
python3 features/self_learn.py record-success good_code.py
python3 features/self_learn.py record-failure bad_code.py --error "Error msg"
python3 features/self_learn.py stats
```

### Provide Feedback
```bash
# Record user feedback on suggestions
python3 features/feedback_loop.py record --type confirmed --suggestion-id xxx --feedback "This fix worked!"
python3 features/feedback_loop.py record --type rejected --suggestion-id xxx --feedback "Wrong approach"
python3 features/feedback_loop.py stats
```

### Use Templates
```bash
# List templates
python3 scripts/qguard-v7.py template list

# Generate prompt
echo '{"task": "...", "language": "python"}' | python3 scripts/qguard-v7.py template generate feature
```

## Core Scripts

| Script | Purpose |
|--------|---------|
| `scripts/qguard-v7.py` | Unified CLI |
| `scripts/*_analyzer.py` | Multi-language analysis |
| `scripts/security_analyzer.py` | OWASP security |
| `scripts/fix_suggester.py` | Fix suggestions |
| `scripts/guide.py` | Code generation guide |
| `features/self_learn.py` | Self-learning engine |
| `features/feedback_loop.py` | User feedback loop |
| `features/template_customizer.py` | Template management |
| `features/skill_absorber.py` | Absorb GitHub best practices |

## Commands

```bash
# Analysis
qguard-v7.py analyze <path> [--language python]
qguard-v7.py security <path>
qguard-v7.py ts/go/java/rust <path>

# Learning
self_learn.py record-success|record-failure <file>
self_learn.py stats|report

# Feedback
feedback_loop.py record --type confirmed/rejected --suggestion-id <id> --feedback "<text>"
feedback_loop.py stats|report

# Templates
qguard-v7.py template list|get <name>
template_customizer.py add --name <name>
```

## Integration

Works with:
- OpenAI Codex, Claude, ChatGPT, GitHub Copilot, Pi
- GitHub Actions, VS Code, Git hooks

## GitHub

https://github.com/Ryan-myp/coding
