# 面条代码反模式（Spaghetti Code Anti-Pattern）

> 识别和修复混乱的控制流

## 问题表现

### 深层嵌套

```python
# ❌ 灾难性的嵌套
def process_order(order):
    if order.status == "pending":
        if order.user.is_active:
            if order.total > 0:
                for item in order.items:
                    if item.stock > 0:
                        if item.price > 0:
                            if order.shipping_address:
                                if can_ship_to(order.shipping_address.country):
                                    # 终于到核心逻辑了...
                                    ship(order)
                                else:
                                    raise ShippingError("Cannot ship to " + order.shipping_address.country)
                            else:
                                raise ValidationError("No shipping address")
                        else:
                            raise ValidationError("Item price must be positive")
                    else:
                        raise StockError(f"Item {item.id} out of stock")
                else:
                    raise ValidationError("No items in order")
            else:
                raise ValidationError("Total must be positive")
        else:
            raise UserError("User is not active")
    else:
        raise OrderError("Order is not pending")
```

```typescript
// ❌ TypeScript 回调地狱
fetchUserData(userId)
  .then(user => {
    if (user) {
      return fetchOrders(user.id)
        .then(orders => {
          if (orders.length > 0) {
            return processOrders(orders)
              .then(result => {
                return sendNotification(result)
              })
          }
        })
    }
  })
  .catch(err => {
    // 错误处理在这里
  });
```

### 重复条件

```python
# ❌ 重复的条件判断
def handle_request(req):
    if req.method == "POST":
        if req.path == "/api/users":
            if req.authenticated:
                if req.has_permission("user:create"):
                    return create_user(req.body)
    elif req.method == "GET":
        if req.path == "/api/users":
            if req.authenticated:
                return list_users(req.query)
    # ... 更多重复
```

## 修复方案

### Guard Clause（守卫子句）

```python
# ✅ 提前返回，消除嵌套
def process_order(order: Order) -> OrderResult:
    if order.status != "pending":
        raise OrderError("order must be pending")
    if not order.user.is_active:
        raise UserError("user is inactive")
    if order.total <= 0:
        raise ValidationError("total must be positive")
    if not order.items:
        raise ValidationError("order must have items")
    for item in order.items:
        if item.stock <= 0:
            raise StockError(f"Item {item.id} out of stock")
        if item.price <= 0:
            raise ValidationError(f"Item {item.id} price must be positive")
    if not order.shipping_address:
        raise ValidationError("shipping address required")
    if not can_ship_to(order.shipping_address.country):
        raise ShippingError(f"Cannot ship to {order.shipping_address.country}")

    return ship(order)
```

### 表驱动/分派器

```python
# ✅ 用映射替代重复条件
HANDLERS = {
    ("POST", "/api/users"): handle_create_user,
    ("GET",  "/api/users"): handle_list_users,
    ("PUT",  "/api/users/:id"): handle_update_user,
    ("DELETE", "/api/users/:id"): handle_delete_user,
}

def handle_request(req: Request) -> Response:
    handler = HANDLERS.get((req.method, req.path))
    if not handler:
        return Response(404, "Not found")
    if not req.authenticated:
        return Response(401, "Unauthorized")
    return handler(req)
```

```typescript
// ✅ TypeScript 路由表
const routes: Route[] = [
  { method: 'POST', path: '/api/users', handler: createUserController },
  { method: 'GET',  path: '/api/users', handler: listUsersController },
  { method: 'PUT',  path: '/api/users/:id', handler: updateUserController },
];

function handleRequest(req: Request): Response {
  const route = routes.find(r => r.method === req.method && matchPath(r.path, req.path));
  if (!route) return notFound();
  if (!req.authenticated) return unauthorized();
  return route.handler(req);
}
```

### Async/Await 替代回调

```typescript
// ✅ 用 async/await 替代回调地狱
async function processUserFlow(userId: string): Promise<void> {
  const user = await fetchUserData(userId);
  if (!user) throw new Error('User not found');

  const orders = await fetchOrders(user.id);
  if (orders.length === 0) return;

  const result = await processOrders(orders);
  await sendNotification(result);
}
```

## 检测指标

| 指标 | 阈值 | 严重性 |
|------|------|--------|
| 嵌套深度 | > 4 层 | 🔴 Critical |
| 函数长度 | > 50 行 | 🟡 Warning |
| 重复条件块 | 相同模式出现 > 2 次 | 🟡 Warning |
| 魔法数字 | 无注释的数字直接出现 | 🟠 Info |

## 重构检查清单

- [ ] 嵌套深度是否 ≤ 3 层
- [ ] 每个函数是否只做一件事
- [ ] 是否有重复的条件判断可以提取为映射
- [ ] 异步代码是否使用 async/await
- [ ] 错误处理是否集中而非散落各处
- [ ] 是否可以用 Guard Clause 替代深层嵌套
- [ ] 函数长度是否 ≤ 50 行（Python/Go）或 ≤ 80 行（Java/TypeScript）
