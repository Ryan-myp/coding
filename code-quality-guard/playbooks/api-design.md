# API 设计 Playbook

## 触发条件

- 设计新的 REST/GraphQL 接口
- 定义模块间 API 契约
- 建立前后端接口规范
- 修改现有公开接口

## 核心原则

### 1. Contract First（契约优先）

**先定义接口，再实现。** 接口是spec，实现是contract的履行。

```typescript
// ✅ 先定义契约
interface OrderAPI {
  // POST /api/orders — 创建订单，返回创建后的订单（含服务端生成的字段）
  createOrder(input: CreateOrderInput): Promise<Order>;

  // GET /api/orders/:id — 获取单个订单，不存在时抛 NotFoundError
  getOrder(id: string): Promise<Order>;

  // GET /api/orders?userId=&status=&pageSize=&cursor=
  // — 分页查询，支持多条件过滤
  listOrders(params: ListOrdersParams): Promise<PaginatedResult<Order>>;

  // PATCH /api/orders/:id — 部分更新，仅更新提供的字段
  updateOrder(id: string, input: UpdateOrderInput): Promise<Order>;

  // DELETE /api/orders/:id — 幂等删除，已删除时不报错
  deleteOrder(id: string): Promise<void>;
}
```

### 2. 一致的错误语义

**统一错误响应格式：**

```typescript
interface APIError {
  error: {
    code: string;        // 机器可读: "VALIDATION_ERROR", "NOT_FOUND"
    message: string;     // 人类可读: "Email is required"
    details?: unknown;   // 附加上下文
  };
}

// HTTP 状态码语义
// 400 → 客户端发送了无效数据
// 401 → 未认证
// 403 → 已认证但无权限
// 404 → 资源不存在
// 409 → 冲突（重复、版本不匹配）
// 422 → 语义上无效（业务规则拒绝）
// 429 → 限流
// 500 → 服务端错误（不暴露内部细节）
```

### 3. 边界验证

```
外部输入 → [边界验证] → 内部信任代码
```

- **必须验证的点：** API路由、表单提交、外部服务响应、环境变量
- **不需要验证的点：** 内部函数间调用、已验证数据的后续处理

```typescript
// ✅ 在边界验证
app.post('/api/orders', async (req, res) => {
  const result = CreateOrderSchema.safeParse(req.body);
  if (!result.success) {
    return res.status(422).json({
      error: { code: 'VALIDATION_ERROR', details: result.error.flatten() }
    });
  }
  const order = await orderService.create(result.data);
  return res.status(201).json(order);
});

// ❌ 不要在内部函数重复验证
async function createOrder(data: CreateOrderInput) {
  // data 已经在边界验证过，不再验证
  return db.orders.insert(data);
}
```

### 4. 优先添加而非修改

```typescript
// ✅ 向后兼容：添加可选字段
interface CreateOrderInput {
  userId: string;
  items: OrderItem[];
  // 新字段，可选
  discountCode?: string;
  giftMessage?: string;
}

// ❌ 破坏兼容：修改或删除字段
interface CreateOrderInput {
  userId: string;
  products: OrderItem[];  // 改名了！
  // items 没了！
}
```

### 5. 幂等性设计

```
幂等键来源：客户端生成 UUID 或业务唯一键
幂等键推导：从意图派生，而非从尝试派生

❌ 错误：`crypto.randomUUID()` — 每次重试都是新键
❌ 错误：`${userId}:${amount}` — 两个合法请求坍缩为一个
✅ 正确：`${orderId}:${Date.now()}` — 业务唯一键
✅ 正确：客户端 `Idempotency-Key` header
```

**原子性保证：**
```typescript
// ❌ TOCTOU 竞态
if (!(await db.exists(key))) {
  await chargeCard(amount);
  await db.insert(key);
}

// ✅ 唯一约束作为机制
try {
  await db.insert({ key, state: 'in_progress', requestHash });
} catch (e) {
  if (isUniqueViolation(e)) return replayOrReject(key);
  throw;
}
```

## API 命名规范

| 模式 | 规范 | 示例 |
|------|------|------|
| REST 端点 | 复数名词，无动词 | `GET /api/orders` |
| 查询参数 | camelCase | `?sortBy=createdAt&pageSize=20` |
| 响应字段 | camelCase | `{ createdAt, updatedAt, orderId }` |
| 布尔字段 | is/has/can 前缀 | `isPaid`, `hasShipped` |
| 枚举值 | UPPER_SNAKE | `"PENDING"`, `"SHIPPED"` |

## 检查清单

- [ ] 接口契约已定义（先于实现）
- [ ] 错误响应格式统一
- [ ] 边界处验证了所有外部输入
- [ ] 外部服务响应被视为不可信
- [ ] 新字段添加为可选，不删除/改名现有字段
- [ ] 幂等接口有幂等键机制
- [ ] 命名符合规范
- [ ] 有 API 文档
- [ ] 有 contract test
