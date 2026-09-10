# TDD 工作流 Playbook

## 触发条件

- 实现新逻辑或新功能
- 修复 bug（必须先写复现测试）
- 修改现有行为
- 重构前需要安全网

## 不做 TDD 的场景

- 纯配置变更
- 文档更新
- 静态内容修改
- 用户明确要求速度优先

## 工作流

### Step 1: RED — 写失败测试

```
1. 发现项目测试框架和命令
2. 写一个描述预期行为的测试
3. 确认测试失败（真正的失败，不是跳过）
```

**测试命名规范：**
```python
# ✅ 好：描述行为
def test_should_return_404_when_user_not_found(): ...
def test_should_calculate_total_with_tax(): ...

# ❌ 坏：描述实现
def test_call_get_user(): ...
def test_use_database(): ...
```

**边界条件检查清单：**
- [ ] 正常路径
- [ ] null/empty 输入
- [ ] 边界值（0, -1, 最大值）
- [ ] 异常输入（类型错误、非法格式）
- [ ] 并发场景（如适用）

### Step 2: GREEN — 最小实现

```
1. 写最少代码让测试通过
2. 不优化、不重构、不添加功能
3. 允许临时方案（标记 TODO）
```

```typescript
// ❌ 坏：直接写完整实现
export async function createOrder(input: CreateOrderInput): Promise<Order> {
  // 验证
  if (!input.items?.length) throw new Error('No items');
  if (!input.userId) throw new Error('No user');
  // 计算
  const total = input.items.reduce((sum, item) => sum + item.price * item.qty, 0);
  // 持久化
  const order = await db.orders.insert({ ...input, total });
  // 通知
  await notifyWarehouse(order);
  // 返回
  return order;
}

// ✅ 好：最小实现
export async function createOrder(input: CreateOrderInput): Promise<Order> {
  const total = calculateTotal(input.items);
  return db.orders.insert({ ...input, total });
}
```

### Step 3: REFACTOR — 清理

```
1. 在测试保护下重构
2. 提取重复逻辑
3. 改进命名
4. 消除代码异味
5. 每步运行测试确认
```

### Step 4: 五轴审查

测试通过后，运行完整五轴审查：
- Correctness: 测试覆盖了哪些场景？
- Readability: 代码是否清晰？
- Architecture: 是否符合分层？
- Security: 有无安全隐患？
- Performance: 有无性能问题？

## Prove-It Pattern（Bug 修复）

```
Bug 报告 → 写复现测试(REDA) → 确认测试失败 → 修复(GREEN) → 全量回归(REFACTOR)
```

```python
# 1. 复现测试（应该失败）
def test_complete_order_updates_completed_at():
    order = create_order()
    complete = complete_order(order.id)
    assert complete.completed_at is not None  # 失败 → bug 确认
```

## 测试金字塔

```
        /‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾\
       /        E2E Tests (~5%)            \
      /--------------------------------------\
     /           Integration Tests (~15%)     \
    /------------------------------------------\
   /          Unit Tests (~80%)                 \
  /----------------------------------------------\
```

| 层级 | 覆盖率目标 | 运行速度 | 重点 |
|------|-----------|---------|------|
| Unit | ≥80% | 毫秒级 | 边界条件、错误路径 |
| Integration | ≥60% 关键路径 | 秒级 | 模块间协作 |
| E2E | 关键用户旅程 | 分钟级 | 端到端流程 |

## 常见陷阱

| 陷阱 | 表现 | 修复 |
|------|------|------|
| 测试实现了细节 | 重构时测试也失败 | 测试行为而非实现 |
| 假阳性测试 | 测试通过但代码有 bug | 审查测试是否真正验证了行为 |
| 测试间耦合 | 一个测试影响另一个 | 每个测试独立初始化 |
| 过度 mocking | 测试了 mock 而非真实逻辑 | 减少 mock，增加集成测试 |
| 忽略了负向测试 | 只测了 happy path | 显式测试错误路径 |
