# API 设计规范

> 基于 Contract First 原则的接口设计指南

---

## 核心原则

### 1. Contract First

**接口即契约。** 先定义接口，再实现。接口是 spec，实现是 contract 的履行。

```typescript
// ✅ 先定义契约
interface OrderAPI {
  createOrder(input: CreateOrderInput): Promise<Order>;
  getOrder(id: string): Promise<Order>;
  listOrders(params: ListOrdersParams): Promise<PaginatedResult<Order>>;
  updateOrder(id: string, input: UpdateOrderInput): Promise<Order>;
  deleteOrder(id: string): Promise<void>;
}

// 实现时只关心契约是否满足
class OrderServiceImpl implements OrderAPI { ... }
```

### 2. 边界验证（Boundary Validation）

```
外部输入 ──▶ [边界验证] ──▶ 内部信任代码
             ↑
         只在边界处验证一次
```

**验证层级：**

| 层级 | 验证内容 | 位置 |
|------|---------|------|
| L1: 格式 | JSON schema, 类型检查 | API Gateway |
| L2: 业务规则 | 业务约束 | Service 入口 |
| L3: 数据一致性 | DB 约束 | Repository |

```typescript
// ✅ Schema 在边界验证
app.post("/api/orders", async (req, res) => {
  const result = CreateOrderSchema.safeParse(req.body);
  if (!result.success) {
    return res.status(422).json({
      error: { code: "VALIDATION_ERROR", details: result.error.flatten() }
    });
  }
  const order = await orderService.create(result.data);
  return res.status(201).json(order);
});

// ❌ 不要在内部函数重复验证
async function createOrder(data: CreateOrderInput) {
  // data 已在边界验证过
  return db.orders.insert(data);
}
```

### 3. 外部服务响应视为不可信

```typescript
// 第三方 API 响应 ≠ 你的类型
type ExternalUser = {
  id: string;
  name: string;
  email: string;
  // 外部可能多出很多字段
  // 也可能缺少某些字段
};

type User = {
  id: string;
  name: string;
  email: string;
};

// ✅ 在边界处做转换
async function getUserFromExternal(id: string): Promise<User> {
  const external = await externalApi.getUser(id);
  // 严格转换，不信任外部格式
  return {
    id: external.id,
    name: external.name,
    email: external.email,
  };
}
```

### 4. 优先添加而非修改

```typescript
// ✅ 向后兼容：添加可选字段
interface CreateOrderInput {
  userId: string;
  items: OrderItem[];
  discountCode?: string;  // 新字段，可选
  giftMessage?: string;   // 新字段，可选
}

// ❌ 破坏兼容：删除或改名
interface CreateOrderInput {
  userId: string;
  products: OrderItem[];  // 改名了！
  // items 没了！
}
```

### 5. 统一的错误语义

```typescript
// 统一错误响应格式
interface APIError {
  error: {
    code: string;      // 机器可读: "VALIDATION_ERROR", "NOT_FOUND"
    message: string;   // 人类可读: "Email is required"
    details?: unknown; // 附加上下文
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

### 6. 幂等性设计

**幂等键原则：**
- 从意图推导，而非从尝试推导
- 避免使用 `crypto.randomUUID()` 作为幂等键（每次重试都是新键）
- 从业务上下文推导：`${orderId}:${Date.now()}`

**原子性保证：**
```typescript
// ❌ TOCTOU 竞态
if (!(await db.exists(key))) {
  await chargeCard(amount);
  await db.insert(key);
}

// ✅ 唯一约束作为机制
try {
  await db.insert({ key, state: "in_progress", requestHash });
} catch (e) {
  if (isUniqueViolation(e)) return replayOrReject(key);
  throw;
}
```

---

## API 命名规范

| 模式 | 规范 | 示例 |
|------|------|------|
| REST 端点 | 复数名词，无动词 | `GET /api/orders` |
| 查询参数 | camelCase | `?sortBy=createdAt&pageSize=20` |
| 响应字段 | camelCase | `{ createdAt, updatedAt }` |
| 布尔字段 | is/has/can 前缀 | `isPaid`, `hasShipped` |
| 枚举值 | UPPER_SNAKE | `"PENDING"`, `"SHIPPED"` |

## 分页规范

```typescript
interface PaginatedResult<T> {
  data: T[];
  pagination: {
    total: number;
    page: number;
    pageSize: number;
    totalPages: number;
  };
}

// 游标分页（大数据量推荐）
interface CursorPagination {
  cursor?: string;  // 上一页最后一条的 ID
  limit: number;    // 每页数量
}
```

## 版本控制

```
/api/v1/orders     → v1 稳定
/api/v2/orders     → v2 新功能
/api/orders        → 默认指向最新稳定版
```

**版本兼容性承诺：**
- v1 至少支持 12 个月
- breaking change 必须升版本号
- deprecation 提前 6 个月通知
