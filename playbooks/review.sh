#!/bin/bash
# Code Review 流程脚本
# 用法: ./playbooks/review.sh <diff_file_or_dir>

set -euo pipefail

TARGET="${1:-}"
if [ -z "$TARGET" ]; then
    echo "Usage: ./playbooks/review.sh <diff_file|directory|->"
    echo ""
    echo "Examples:"
    echo "  ./playbooks/review.sh src/payment/"
    echo "  ./playbooks/review.sh changes.diff"
    echo "  git diff main...HEAD | ./playbooks/review.sh -"
    exit 1
fi

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
SKILL_DIR="$(dirname "$SCRIPT_DIR")"
QGUARD="$SKILL_DIR/scripts/qguard.py"

echo "=========================================="
echo "  Code Review Pipeline"
echo "=========================================="
echo ""

# Phase 1: 五轴评分
echo "📊 Phase 1: Five-axis scoring..."
if [ "$TARGET" = "-" ]; then
    python3 "$QGUARD" review /dev/stdin --json 2>/dev/null | python3 -c "
import sys, json
data = json.load(sys.stdin)
for r in data.get('results', []):
    print(f\"  [{r['gate']}] {r['file']}: {r['composite_score']}/100 ({r['grade']})\")
" || echo "  (diff input, skipping detailed review)"
else
    python3 "$QGUARD" review "$TARGET" --json 2>/dev/null | python3 -c "
import sys, json
data = json.load(sys.stdin)
for r in data.get('results', []):
    emoji = '✅' if r['composite_score'] >= 90 else '⚠️' if r['composite_score'] >= 70 else '❌'
    print(f\"  {emoji} {r['file']}: {r['composite_score']}/100 ({r['grade']})\")
"
fi
echo ""

# Phase 2: 威胁建模
echo "🔒 Phase 2: STRIDE threat modeling..."
python3 "$QGUARD" threats "$TARGET" --json 2>/dev/null | python3 -c "
import sys, json
threats = json.load(sys.stdin)
critical = [t for t in threats if t['severity'] == 'critical']
warnings = [t for t in threats if t['severity'] == 'warning']
if critical:
    print(f'  🔴 {len(critical)} critical threat(s):')
    for t in critical[:5]:
        print(f\"      [{t['category']}] L{t['line']}: {t['description']}\")
else:
    print('  ✅ No critical threats')
if warnings:
    print(f'  🟡 {len(warnings)} warning(s)')
" || echo "  (threat scan skipped)"
echo ""

# Phase 3: 门禁判定
echo "🚦 Phase 3: Quality gate..."
python3 "$QGUARD" gate "$TARGET" --min-score 70 --json 2>/dev/null | python3 -c "
import sys, json
data = json.load(sys.stdin)
if data.get('passed'):
    print('  ✅ Quality gate PASSED')
else:
    print('  ❌ Quality gate FAILED')
    for issue in data.get('issues', []):
        print(f'      {issue}')
" || echo "  ⚠️  Gate check unavailable"
echo ""

# Phase 4: 模式蒸馏
echo "🧬 Phase 4: Pattern distillation..."
python3 "$QGUARD" distill "$TARGET" --json 2>/dev/null | python3 -c "
import sys, json
data = json.load(sys.stdin)
patterns = data.get('patterns', [])
anti_patterns = data.get('anti_patterns', [])
if patterns:
    print(f'  ✨ {len(patterns)} pattern(s) found:')
    for p in patterns[:5]:
        print(f\"      + {p['name']} — {p.get('desc', '')}\")
if anti_patterns:
    print(f'  ⚠️  {len(anti_patterns)} anti-pattern(s):')
    for a in anti_patterns[:5]:
        print(f\"      - {a['name']} — {a.get('desc', '')}\")
if not patterns and not anti_patterns:
    print('  (no patterns extracted)')
" || echo "  (distillation skipped)"
echo ""

echo "=========================================="
echo "  Review complete"
echo "=========================================="
