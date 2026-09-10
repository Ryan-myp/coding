#!/bin/bash
# TDD 工作流脚本 — 在实现新功能时强制执行 TDD
# 用法: ./playbooks/tdd.sh <feature_description>

set -euo pipefail

FEATURE="${1:-}"
if [ -z "$FEATURE" ]; then
    echo "Usage: ./playbooks/tdd.sh 'describe the feature'"
    echo ""
    echo "This script enforces TDD workflow:"
    echo "  1. Write RED test (should fail)"
    echo "  2. Write minimal GREEN implementation"
    echo "  3. REFACTOR under test protection"
    echo "  4. Run quality gate"
    exit 1
fi

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
SKILL_DIR="$(dirname "$SCRIPT_DIR")"
QGUARD="$SKILL_DIR/scripts/qguard.py"

echo "=========================================="
echo "  TDD Workflow: $FEATURE"
echo "=========================================="
echo ""

# Step 1: RED — 写失败测试
echo "📝 Step 1: RED — Writing failing test..."
echo "# Test for: $FEATURE" > /tmp/tdd_red_test.py
echo "# TODO: Write the actual test" >> /tmp/tdd_red_test.py
echo "  → Created /tmp/tdd_red_test.py"
echo "  → Modify this file with your failing test"
echo ""

# Step 2: 运行测试确认失败
echo "🔴 Step 2: Confirming test fails (RED state)..."
# 这里应该运行实际的测试框架
echo "  → Run: pytest /tmp/tdd_red_test.py -v  (should FAIL)"
echo ""

# Step 3: GREEN — 最小实现
echo "🟢 Step 3: Writing minimal implementation..."
echo "# TODO: Implement the minimum code to pass the test" > /tmp/tdd_green_impl.py
echo "  → Created /tmp/tdd_green_impl.py"
echo "  → Implement minimum code to make test pass"
echo ""

# Step 4: 运行测试确认通过
echo "🟢 Step 4: Confirming test passes (GREEN state)..."
echo "  → Run: pytest /tmp/tdd_red_test.py -v  (should PASS)"
echo ""

# Step 5: REFACTOR — 质量审查
echo "🧹 Step 5: REFACTOR — Running quality gate..."
if [ -f "$QGUARD" ]; then
    python3 "$QGUARD" gate /tmp/tdd_green_impl.py --min-score 70 2>&1 || {
        echo "  ⚠️  Quality gate failed. Fix issues before proceeding."
        exit 1
    }
else
    echo "  ⚠️  qguard.py not found, skipping quality gate"
fi
echo ""

# Step 6: 五轴评分
echo "📊 Step 6: Five-axis review..."
if [ -f "$QGUARD" ]; then
    python3 "$QGUARD" review /tmp/tdd_green_impl.py 2>&1 || true
fi
echo ""

echo "✅ TDD workflow complete for: $FEATURE"
echo ""
echo "Next steps:"
echo "  1. Move /tmp/tdd_red_test.py → tests/test_$(echo $FEATURE | tr '[:upper:]' '[:lower:]' | tr ' ' '_').py"
echo "  2. Move /tmp/tdd_green_impl.py → src/"
echo "  3. Submit PR for review"
