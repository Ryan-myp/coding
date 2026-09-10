#!/bin/bash
# 质量门禁预提交脚本
# 用法: 添加到 .git/hooks/pre-commit 或手动运行

set -euo pipefail

SKILL_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/../.." && pwd)"
QGUARD="$SKILL_DIR/scripts/qguard.py"

# 获取暂存的文件
STAGED_FILES=$(git diff --cached --name-only --diff-filter=ACM 2>/dev/null || true)
if [ -z "$STAGED_FILES" ]; then
    exit 0
fi

# 只检查代码文件
CODE_FILES=$(echo "$STAGED_FILES" | grep -E '\.(py|ts|tsx|go|java|rs)$' || true)
if [ -z "$CODE_FILES" ]; then
    exit 0
fi

echo "🔍 Code Quality Guard — Pre-commit ($(( $(echo "$CODE_FILES" | wc -l) )) files)"

# 检查硬编码密钥（快速过滤）
for f in $CODE_FILES; do
    if grep -iqE '(password|secret|api_key|token)\s*[:=]\s*["\x27][a-zA-Z0-9]{8,}' "$f" 2>/dev/null; then
        echo "🚨 Critical: Possible hardcoded secret in $f"
        grep -iE '(password|secret|api_key|token)\s*[:=]\s*["\x27][a-zA-Z0-9]{8,}' "$f" | head -3
        exit 1
    fi
done

# 运行五轴评分
echo "  Running five-axis review..."
if [ -f "$QGUARD" ]; then
    echo "$CODE_FILES" | while read f; do
        if [ -f "$f" ]; then
            python3 "$QGUARD" review "$f" --json 2>/dev/null | python3 -c "
import sys, json
try:
    r = json.load(sys.stdin)
    score = r.get('composite_score', 0)
    gate = r.get('gate', 'unknown')
    icon = '✅' if score >= 90 else '⚠️' if score >= 70 else '❌'
    print(f'  {icon} {score:.0f}/100  {gate}  {sys.argv[1]}')
except: pass
" "$f" 2>/dev/null || true
        fi
    done
fi

echo ""
echo "✅ Pre-commit check passed"
exit 0
