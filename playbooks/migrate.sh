#!/bin/bash
# 迁移安全检查脚本
# 用法: ./playbooks/migrate-check.sh <source_dir> <target_branch>

set -euo pipefail

SOURCE="${1:-.}"
TARGET_BRANCH="${2:-main}"
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
SKILL_DIR="$(dirname "$SCRIPT_DIR")"
QGUARD="$SKILL_DIR/scripts/qguard.py"

echo "=========================================="
echo "  Migration Safety Check"
echo "  Source: $SOURCE"
echo "  Target: $TARGET_BRANCH"
echo "=========================================="
echo ""

# 检查数据库变更
echo "🔍 Checking for database schema changes..."
SCHEMA_CHANGES=$(git diff "${TARGET_BRANCH}...HEAD" --name-only 2>/dev/null | grep -E '\.(sql|migration)$' | wc -l)
if [ "$SCHEMA_CHANGES" -gt 0 ]; then
    echo "  ⚠️  $SCHEMA_CHANGES schema change file(s) found"
    git diff "${TARGET_BRANCH}...HEAD" --name-only 2>/dev/null | grep -E '\.(sql|migration)$' | while read f; do
        echo "     - $f"
    done
    echo "  → Ensure backward-compatible (ADD COLUMN nullable, don't DROP)"
else
    echo "  ✅ No schema changes detected"
fi
echo ""

# 检查环境变量变更
echo "🔍 Checking environment variable changes..."
ENV_CHANGES=$(git diff "${TARGET_BRANCH}...HEAD" -- '*.env*' '.env.*' 'env*' 2>/dev/null | wc -l)
if [ "$ENV_CHANGES" -gt 0 ]; then
    echo "  ⚠️  Environment config changes detected"
fi
echo ""

# 检查认证/授权变更
echo "🔍 Checking auth/security changes..."
AUTH_FILES=$(git diff "${TARGET_BRANCH}...HEAD" --name-only 2>/dev/null | grep -iE '(auth|security|permission|token|session)' | wc -l)
if [ "$AUTH_FILES" -gt 0 ]; then
    echo "  🔴 $AUTH_FILES auth-related file(s) changed — requires security review"
    git diff "${TARGET_BRANCH}...HEAD" --name-only 2>/dev/null | grep -iE '(auth|security|permission|token|session)' | while read f; do
        echo "     - $f"
    done
else
    echo "  ✅ No auth changes detected"
fi
echo ""

# 运行五轴评分
echo "📊 Running quality gate..."
python3 "$QGUARD" gate "$SOURCE" --min-score 70 2>&1 || {
    echo "  ❌ Quality gate failed"
    exit 1
}
echo "  ✅ Quality gate passed"
echo ""

echo "=========================================="
echo "  Migration check complete"
echo "=========================================="
