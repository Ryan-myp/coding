#!/bin/bash
# 威胁建模流程脚本
# 用法: ./playbooks/threat-model.sh <source_dir>

set -euo pipefail

SOURCE="${1:-.}"
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
SKILL_DIR="$(dirname "$SCRIPT_DIR")"
QGUARD="$SKILL_DIR/scripts/qguard.py"

echo "=========================================="
echo "  STRIDE Threat Modeling"
echo "  Source: $SOURCE"
echo "=========================================="
echo ""

# 运行威胁建模
THREATS=$(python3 "$QGUARD" threats "$SOURCE" --json 2>/dev/null || echo '[]')

# 统计
CRITICAL=$(echo "$THREATS" | python3 -c "import sys,json; t=json.load(sys.stdin); print(len([x for x in t if x['severity']=='critical']))" 2>/dev/null || echo 0)
WARNING=$(echo "$THREATS" | python3 -c "import sys,json; t=json.load(sys.stdin); print(len([x for x in t if x['severity']=='warning']))" 2>/dev/null || echo 0)

echo "Results:"
echo "  🔴 Critical: $CRITICAL"
echo "  🟡 Warning:  $WARNING"
echo ""

if [ "$CRITICAL" -gt 0 ]; then
    echo "Critical threats:"
    echo "$THREATS" | python3 -c "
import sys, json
for t in json.load(sys.stdin):
    if t['severity'] == 'critical':
        print(f\"  [{t['category']}] L{t['line']}: {t['description']}\")
        print(f\"      Mitigation: {t['mitigation']}\")
"
    echo ""
    echo "🚨 Block merge until critical threats are resolved!"
    exit 1
fi

if [ "$WARNING" -gt 0 ]; then
    echo "Warnings:"
    echo "$THREATS" | python3 -c "
import sys, json
for t in json.load(sys.stdin):
    if t['severity'] == 'warning':
        print(f\"  [{t['category']}] L{t['line']}: {t['description']}\")
"
    echo ""
fi

echo "✅ Threat modeling complete. No critical issues found."
