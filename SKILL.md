---
name: agent-code-guide
description: "Guides AI agents to generate consistent, high-quality code. Absorbs best practices from top GitHub skills. Self-learning from successful patterns."
version: 1.0.0
author: ryan
tags: [agent-guide, code-generation, consistency, self-learning, distillation]
metadata:
  platforms: [linux, macos, windows]
  auto-trigger: true
  trigger-contexts: [code-generation, agent-prompt, code-writing]
---

# Agent Code Generation Guide

Guides AI agents (Codex, Claude, ChatGPT, etc.) to generate **consistent, high-quality code** across different users and projects.

## Problem Solved

Different people using the same AI agent produce wildly different code quality. This skill:
1. **Standardizes** code generation across teams
2. **Learns** from successful patterns
3. **Distills** best practices into reusable rules

## Core Capabilities

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

### 3. Quality Guidelines
Language-specific rules:
- Python: PEP 8, type hints, error handling
- TypeScript: Strict types, no `any`, error boundaries
- Go: Idioms, error handling, context usage
- Java: SOLID, null safety, resource management
- Rust: Ownership, error handling, unsafe avoidance

### 4. Pattern Distillation
Extract and learn from:
- Successful code patterns
- Common anti-patterns
- Team-specific conventions
- Industry best practices

### 5. Self-Learning
Track what works:
- Record successful generations
- Identify recurring issues
- Learn from fixes
- Improve over time

## Usage

### Before Code Generation
```bash
# Inject context and guidelines
python3 scripts/guide.py prepare --intent feature --project ./myapp

# Output: Context injection for agent prompt
```

### After Code Generation
```bash
# Check quality and consistency
python3 scripts/guide.py review generated_code.py

# Output: Quality report with suggestions
```

### Learn from Success
```bash
# Distill patterns from good code
python3 scripts/guide.py distill --source ./good-code/ --output patterns.json

# Learn from failures
python3 scripts/guide.py learn --failure "SQL injection" --fix "Use parameterized queries"
```

## Files

- `scripts/guide.py` — Main entry point
- `scripts/intent_detector.py` — Intent detection
- `scripts/context_engine.py` — Context injection
- `scripts/pattern_distiller.py` — Pattern extraction
- `scripts/quality_guide.py` — Quality guidelines
- `features/self_learn.py` — Self-learning engine
- `policies/conventions.md` — Team conventions
- `patterns/library.json` — Distilled patterns

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
