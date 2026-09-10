# Changelog v7.6

## New Features

### 1. Skill Absorber (`features/skill_absorber.py`)
Absorb best practices from top GitHub agent skills:
- addyosmani/agent-skills — Structured prompt design
- alirezarezvani/claude-skills — Persona-based prompting
- superpowers — Self-reflection and iteration
- open-code — Context engineering
- cline — Safety guardrails

Absorbed patterns:
- Role Prompting (95/100)
- Chain of Thought (90/100)
- Self-Consistency (88/100)
- Plan-Execute-Review (92/100)
- Self-Reflection (85/100)
- Context Windows (87/100)
- Guardrails (90/100)
- Feedback Loop (83/100)

Usage:
```bash
# Absorb common patterns
python3 features/skill_absorber.py absorb

# Generate enhanced prompt
echo "# Your task" | python3 features/skill_absorber.py enhance --intent feature
```

### 2. Enhanced Pattern Library (`features/enhanced_pattern_library.py`)
More powerful pattern management:
- Usage tracking (how many times used)
- Success rate calculation
- Keyword-based similarity search
- History logging
- Source tracking (manual/ai/github)

Usage:
```bash
# Add pattern manually
python3 features/enhanced_pattern_library.py add \
  --name "Proper Error Handling" \
  --category "error-handling" \
  --language python

# Search similar patterns
cat code.py | python3 features/enhanced_pattern_library.py search --language python

# View statistics
python3 features/enhanced_pattern_library.py stats

# Generate report
python3 features/enhanced_pattern_library.py report
```

### 3. Team Custom Rules (`policies/team_rules.md`)
Define team-specific conventions:
- Language-specific rules
- Severity levels (error/warning/info)
- Pattern matching and fix suggestions
- Auto-injected into generation prompts

Template includes examples for Python and TypeScript.

### 4. VS Code Integration (`.vscode/`)
- `settings.json` — Quality check settings
- `tasks.json` — Quick commands for analysis

Tasks available:
- Code Quality Check
- Security Check
- Generate PR Description

## Updated Files

- `SKILL.md` — Updated for v7.6
- `qguard-v7.py` — Added skill/learn/pattern commands
- `CHANGELOG_V7.md` — This file

## GitHub

https://github.com/Ryan-myp/coding

## Commit

`$(git rev-parse --short HEAD)`
