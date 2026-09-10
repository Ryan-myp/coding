#!/bin/bash
# Pre-commit hook for code quality checks
# Usage: copy to .git/hooks/pre-commit and make executable

SKILL_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
DISTILL_SCRIPT="$SKILL_DIR/scripts/distill.py"
SCORE_SCRIPT="$SKILL_DIR/scripts/score.py"

# Get changed files
CHANGED_FILES=$(git diff --cached --name-only --diff-filter=ACM)

if [ -z "$CHANGED_FILES" ]; then
    exit 0
fi

# Filter to supported languages
SUPPORTED_EXTENSIONS="\.py$|\.ts$|\.tsx$|\.js$|\.jsx$|\.go$|\.java$|\.rs$"
FILES_TO_CHECK=$(echo "$CHANGED_FILES" | grep -E "$SUPPORTED_EXTENSIONS")

if [ -z "$FILES_TO_CHECK" ]; then
    exit 0
fi

echo "🔍 Running Code Quality Guard on changed files..."
echo ""

PASS=true
for file in $FILES_TO_CHECK; do
    echo "📄 Checking: $file"

    # Run distillation analysis
    if [ -f "$DISTILL_SCRIPT" ]; then
        result=$(python3 "$DISTILL_SCRIPT" "$file" 2>/dev/null)
        anti_count=$(echo "$result" | python3 -c "import sys,json; d=json.load(sys.stdin); print(d.get('summary',{}).get('critical_count',0))" 2>/dev/null || echo 0)

        if [ "$anti_count" -gt 0 ]; then
            echo "  ⚠️  Found $anti_count critical anti-pattern(s) in $file"
            PASS=false
        fi
    fi
done

echo ""
if [ "$PASS" = true ]; then
    echo "✅ Code quality checks passed"
    exit 0
else
    echo "❌ Code quality issues found. Please fix before committing."
    echo ""
    echo "Run manually for details:"
    echo "  python3 $SCORE_SCRIPT <file>"
    exit 1
fi
