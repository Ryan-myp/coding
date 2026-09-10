# TDD 工作流指南

> Test-Driven Development 完整实践指南

---

## TDD 的三重收益

1. **设计驱动** — 先想清楚接口，再想实现
2. **安全网** — 重构时有信心
3. **文档** — 测试即规格

## 工作流详解

### Phase 1: RED — 写失败测试

```python
# 1. 明确要测试的行为
def test_should_calculate_discount_for_premium_users():
    """Premium 用户享受 20% 折扣"""
    pricing = PricingService()
    result = pricing.calculate(100.0, user_type="premium")
    assert result == 80.0  # 这步会失败（RED）
```

**测试命名规则：**
```python
# ✅ 好：描述行为
def test_returns_404_when_user_not_found():
def test_applies_20pct_discount_for_premium_tiers():
def test_rejects_negative_quantity():

# ❌ 坏：描述实现
def test_call_get_user_endpoint():
def test_use_database_query():
```

**边界条件检查清单：**
```
☐ 正常路径（happy path）
☐ null / empty 输入
☐ 边界值（0, -1, 最大值，最小值）
☐ 类型错误（传了 wrong type）
☐ 并发场景（如果适用）
☐ 权限不足（如果适用）
```

### Phase 2: GREEN — 最小实现

```python
# 目标：让测试通过，不惜任何代价
def calculate(price: float, user_type: str) -> float:
    if user_type == "premium":
        return price * 0.8
    return price
```

**允许临时方案：**
```python
# 可以暂时硬编码，加 TODO
def calculate(price: float, user_type: str) -> float:
    # TODO: 需要支持更多用户类型
    return price * 0.8 if user_type == "premium" else price
```

### Phase 3: REFACTOR — 清理

```python
# 在测试保护下清理
DISCOUNT_RATES = {
    "regular": 1.0,
    "premium": 0.8,
    "vip": 0.7,
}

def calculate(price: float, user_type: str) -> float:
    rate = DISCOUNT_RATES.get(user_type, 1.0)
    return price * rate
```

## 测试金字塔

```
        ╭────────────────────────────────────────╮
        │          E2E Tests (~5%)               │
        │    关键用户旅程验证                      │
       ╱──────────────────────────────────────────╲
      │         Integration Tests (~15%)           │
      │    模块间协作验证                           │
     ╱─────────────────────────────────────────────╲
    │           Unit Tests (~80%)                    │
    │     边界条件、错误路径覆盖                      │
   ╱────────────────────────────────────────────────╲
```

| 层级 | 数量 | 速度 | 重点 |
|------|------|------|------|
| Unit | 最多 | 毫秒 | 单个函数的所有分支 |
| Integration | 中等 | 秒级 | 模块间协作 |
| E2E | 最少 | 分钟级 | 关键用户路径 |

## Prove-It Pattern（Bug 修复）

```
Bug 报告 → 写复现测试(REDA) → 确认失败 → 修复(GREEN) → 全量回归(REFACTOR)
```

```python
# Bug 报告：completed_at 在完成订单后未设置

# 1. 写复现测试（应该失败）
def test_complete_order_sets_completed_at():
    order = create_order_in_db(status="pending")
    result = complete_order(order.id)
    assert result.completed_at is not None  # 💥 失败

# 2. 最小修复
def complete_order(order_id: str) -> Order:
    order = db.get(order_id)
    order.status = "completed"
    order.completed_at = datetime.utcnow()  # 🟢 修复
    db.save(order)
    return order

# 3. 运行全量测试
pytest tests/  # 确保无回归
```

## TDD 常见陷阱

| 陷阱 | 症状 | 修复 |
|------|------|------|
| 测试实现细节 | 重构时测试也失败 | 改为测试行为 |
| 假阳性测试 | 测试通过但代码有 bug | 审查测试是否真正验证了行为 |
| 测试间耦合 | 一个测试影响另一个 | 每个测试独立初始化 |
| 过度 mocking | 测试了 mock 而非真实逻辑 | 减少 mock，增加集成测试 |
| 忽略负向测试 | 只测 happy path | 显式测试错误路径 |
| 过早抽象 | 第一次就用泛型/策略模式 | 先写具体实现，第三次再用抽象 |
