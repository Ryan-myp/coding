# Code Quality Constraints

This document defines the quality bar for this project. All agents must adhere to these constraints.

## Core Constraints

### 1. Security Constraints
- **NO** hardcoded secrets (passwords, API keys, tokens)
- **NO** SQL injection (use parameterized queries)
- **NO** eval()/exec() usage
- **YES** input validation at all boundaries
- **YES** authentication on all sensitive operations
- **YES** authorization checks on all data access

### 2. Architecture Constraints
- **Layer separation:** Controller → Service → Repository
- **Single Responsibility:** One class/function per concern
- **Dependency Injection:** No global state
- **Max class size:** 15 methods
- **Max function length:** 50 lines
- **Max nesting depth:** 3 levels

### 3. Testing Constraints
- **TDD:** Write tests before implementation
- **Coverage:** ≥ 80% for new code
- **Edge cases:** Test null, empty, boundary values
- **Error paths:** Test failure scenarios
- **Integration:** Test component interactions

### 4. Performance Constraints
- **No N+1 queries:** Use bulk operations
- **Timeouts:** All external calls need timeouts
- **Pagination:** All list endpoints must paginate
- **Caching:** Cache expensive computations

### 5. Readability Constraints
- **Naming:** Descriptive, consistent with project
- **Functions:** < 50 lines
- **Files:** < 300 lines
- **Classes:** < 200 lines
- **Comments:** Explain why, not what

## Quality Gates

### Minimum Scores
| Metric | Threshold |
|--------|-----------|
| Composite Score | ≥ 70 |
| Correctness | ≥ 15/20 |
| Readability | ≥ 12/20 |
| Architecture | ≥ 18/20 |
| Security | ≥ 15/20 |
| Performance | ≥ 8/20 |
| Testing | ≥ 8/20 |

### Blocking Conditions
Any of the following will block merge:
- Score < 70
- Any Critical finding
- Security score < 15
- Architecture score < 18
- Missing tests for new functionality

## Constraint Evolution

Constraints are living documents. Review and update quarterly:
1. Collect feedback from code reviews
2. Analyze common violations
3. Adjust thresholds based on project maturity
4. Document reasoning for changes

## Enforcement

Constraints are enforced by:
- Pre-commit hooks (`qguard gate`)
- CI/CD pipelines (`quality-check.yml`)
- Code review checklists (`personas/code-reviewer.md`)
- Automated scanning (`qguard review`)
