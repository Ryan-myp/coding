---
name: code-quality-guard
description: "Multi-language code quality skill supporting 7+ languages with feedback loop for continuous improvement."
version: 7.11.0
author: ryan
tags: [code-quality, agent-guide, self-learning, patterns, multi-language, feedback]
metadata:
  platforms: [linux, macos, windows]
  auto-trigger: true
---

# Code Quality Guard v7.11

Guide AI agents to generate **consistent, high-quality code** across different users and projects.

## Supported Languages

| Language | Analyzer | Rules | Status |
|----------|----------|-------|--------|
| Python | ast_analyzer.py | ~15 | ✅ |
| TypeScript | ts_analyzer.py | ~8 | ✅ |
| Go | go_analyzer.py | ~7 | ✅ |
| Java | java_analyzer.py | ~5 | ✅ |
| Rust | rust_analyzer.py | ~5 | ✅ |
| C# | csharp_analyzer.py | ~7 | ✅ New |
| PHP | php_analyzer.py | ~7 | ✅ New |

**Total: ~50 rules across 7 languages**

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

### Guide Generation
```bash
python3 scripts/guide.py prepare --intent feature --language python
```

### Learn & Feedback
```bash
# Record success/failure
python3 features/self_learn.py record-success good_code.py
python3 features/feedback_loop.py record --type confirmed --suggestion-id xxx

# View stats
python3 features/self_learn.py stats
python3 features/feedback_loop.py stats
```

### Use Templates
```bash
python3 scripts/qguard-v7.py template list
python3 scripts/qguard-v7.py template get feature
```

## CLI Commands

```bash
# Analysis
qguard-v7.py analyze <path> [--language python]
qguard-v7.py ts/go/java/rust/csharp/php <path>
qguard-v7.py security <path>

# Learning
self_learn.py record-success|record-failure <file>
feedback_loop.py record --type confirmed/rejected --suggestion-id <id>

# Templates
qguard-v7.py template list|get <name>
```

## Web API

```bash
# Start API server
python3 web/api.py --port 8080

# Endpoints
GET  /api/health
GET  /api/stats
POST /api/analyze
```

## Integration

- GitHub Actions: `.github/workflows/quality-check.yml`
- VS Code: `.vscode/settings.json`
- Git hooks: `hooks/pre-commit.sh`

## GitHub

https://github.com/Ryan-myp/coding
