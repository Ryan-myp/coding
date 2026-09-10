# Code Quality Guard — Improvement Roadmap (Honest)

## Current State (v7.0)

### Working Well
- Intent Detection (6 types, Chinese/English)
- Six-axis Scoring (correctness/readability/architecture/security/performance/accessibility)
- AST-based Python Analysis
- STRIDE Threat Model (basic)
- Multi-agent support (Pi/Claude/Codex/Cursor/Copilot)

### Framework-Level (Needs Real Implementation)
- Pattern Detection (keyword matching only)
- Health Tracking (score history, no prediction)
- Context Detection (file type analysis only)
- Failure Tracking (JSON recording, no learning)

### Not Implemented
- True AI Learning
- Self-improvement
- MITRE ATT&CK AI inference

## Next Iterations (Realistic & Practical)

### v7.1 — Improve Core Scoring (This Week)
- [ ] Add TypeScript AST parser (currently only Python)
- [ ] Improve scoring weights based on project type
- [ ] Add language-specific checklists
- [ ] Benchmark accuracy against manual review

### v7.2 — Expand Language Support (2 Weeks)
- [ ] TypeScript/JavaScript parser
- [ ] Go parser
- [ ] Java parser
- [ ] Rust parser
- [ ] Universal pattern detection (language-agnostic)

### v7.3 — Better Security Analysis (2 Weeks)
- [ ] OWASP Top 10 coverage
- [ ] Real CVE database integration
- [ ] Dependency vulnerability scanning
- [ ] Sensitive data detection (API keys, passwords)

### v7.4 — Actionable Reports (1 Week)
- [ ] Generate fix suggestions with code examples
- [ ] Create PR-ready descriptions
- [ ] Prioritize findings by impact
- [ ] Export to standard formats (JSON, SARIF)

### v7.5 — CI/CD Integration (1 Week)
- [ ] GitHub Actions workflow
- [ ] GitLab CI template
- [ ] Jenkins pipeline example
- [ ] Quality gate configuration

## Success Metrics

- [ ] Support 5+ programming languages
- [ ] OWASP Top 10 coverage
- [ ] < 5% false positive rate
- [ ] CI/CD integration working
- [ ] Zero exaggerated claims in docs

## What We Won't Claim

- ❌ "AI-powered" (unless we use actual ML)
- ❌ "Self-learning" (unless there's a feedback loop)
- ❌ "Intelligent" (unless there's real understanding)
- ❌ "Evolutionary" (unless there's actual evolution)

## Honest Value Proposition

**We are**: A practical, multi-language code quality toolkit with consistent scoring and security analysis.

**We are not**: An AI system, a learning platform, or a replacement for human code review.

---
Last updated: 2026-09-10
