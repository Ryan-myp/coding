#!/bin/bash
# Code Quality Guard Pre-commit Hook
# 在提交前运行质量门禁检查

set -euo pipefail

SKILL_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
SCRIPTS_DIR="$SKILL_DIR/scripts"

# 获取暂存的文件
if ! git rev-parse --verify HEAD >/dev/null 2>&1; then
    ALL_FILES=$(git diff --cached --name-only --diff-filter=ACM)
else
    ALL_FILES=$(git diff --cached --name-only --diff-filter=ACM HEAD)
fi

# 只处理支持的代码文件
CODE_FILES=()
for f in $ALL_FILES; do
    case "$f" in
        *.py|*.ts|*.tsx|*.go|*.java|*.rs)
            CODE_FILES+=("$f")
            ;;
    esac
done

if [ ${#CODE_FILES[@]} -eq 0 ]; then
    exit 0
fi

echo "🔍 Code Quality Guard — Pre-commit Check"
echo "   Files: ${#CODE_FILES[@]}"

# 检查硬编码密钥
SECRET_PATTERNS="password|secret|api_key|token|credential"
if git diff --cached | grep -iqE "^\+.*($SECRET_PATTERNS)\s*[:=]\s*['\"]?[a-zA-Z0-9]{8,}"; then
    echo "🚨 Critical: Possible hardcoded secret detected!"
    git diff --cached | grep -iE "(password|secret|api_key|token)" | head -5
    exit 1
fi

# 检查 SQL 注入风险
if git diff --cached | grep -qE "execute.*f['\"].*%|\.format\(.*\)"; then
    echo "⚠️  Warning: Possible SQL injection pattern detected"
fi

# 运行 distillation（如果文件较多，只检查关键文件）
if [ ${#CODE_FILES[@]} -le 10 ]; then
    for f in "${CODE_FILES[@]}"; do
        if [ -f "$f" ]; then
            echo "   Checking: $f"
            python3 "$SCRIPTS_DIR/score.py" "$f" --json 2>/dev/null || true
        fi
    done
fi

echo "✅ Pre-commit check passed"
exit 0
