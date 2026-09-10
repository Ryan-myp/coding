# 命名规范库（Naming Conventions）

> 跨语言的统一命名约定，提升代码可读性

---

## 变量命名

### 基本原则
- 使用**有意义的名称**，让读者一眼理解用途
- 避免缩写（除非是行业通用缩写如 `id`, `url`, `api`, `html`）
- 长度与用途匹配（局部变量可以短，公共 API 要完整）

### 各语言规范

| 语言 | 变量 | 常量 | 布尔 | 集合 |
|------|------|------|------|------|
| Python | `user_count` | `MAX_RETRIES` | `is_active` | `users` |
| TypeScript | `userCount` | `MAX_RETRIES` | `isActive` | `users` |
| Go | `userCount` | `MaxRetries` | `isActive` | `users` |
| Java | `userCount` | `MAX_RETRIES` | `isActive` | `users` |
| Rust | `user_count` | `MAX_RETRIES` | `is_active` | `users` |

---

## 函数/方法命名

### 基本原则
- 以**动词**开头，明确表达动作
- 返回布尔值用 `is_`/`has_`/`can_`/`should_`
- 返回新对象用 `create_`/`build_`/`fetch_`
- 修改状态用 `update_`/`set_`/`delete_`

| 返回值 | Python | TypeScript | Go | Java | Rust |
|--------|--------|-----------|-----|------|------|
| 查询单个 | `get_user` | `getUser` | `GetUser` | `getUser` | `get_user` |
| 查询列表 | `list_users` | `listUsers` | `ListUsers` | `listUsers` | `list_users` |
| 创建 | `create_order` | `createOrder` | `CreateOrder` | `createOrder` | `create_order` |
| 判断 | `is_valid` | `isValid` | `IsValid` | `isValid` | `is_valid` |
| 转换 | `to_dict` | `toDict` | `ToDict` | `toDict` | `to_dict` |
| 处理 | `process_payment` | `processPayment` | `ProcessPayment` | `processPayment` | `process_payment` |

---

## 类/类型命名

| 语言 | 规范 | 示例 |
|------|------|------|
| Python | PascalCase | `PaymentProcessor`, `UserRepository` |
| TypeScript | PascalCase | `PaymentProcessor`, `UserRepository` |
| Go | PascalCase (导出) | `PaymentProcessor`, `userRepository` (包内) |
| Java | PascalCase | `PaymentProcessor`, `UserRepository` |
| Rust | PascalCase | `PaymentProcessor`, `UserRepository` |

### 特殊后缀约定

| 后缀 | 含义 | 示例 |
|------|------|------|
| `Handler` | 请求处理器 | `PaymentHandler` |
| `Controller` | MVC控制器 | `UserController` |
| `Service` | 业务逻辑层 | `OrderService` |
| `Repository` | 数据访问层 | `UserRepository` |
| `Factory` | 工厂类 | `PaymentFactory` |
| `Strategy` | 策略类 | `PaymentStrategy` |
| `Adapter` | 适配器 | `StripeAdapter` |
| `Listener` | 事件监听器 | `OrderListener` |
| `Middleware` | 中间件 | `AuthMiddleware` |
| `Exception/Error` | 异常类 | `PaymentError` |

---

## 模块/文件命名

| 语言 | 规范 | 示例 |
|------|------|------|
| Python | 小写+下划线 | `payment_service.py`, `user_repository.py` |
| TypeScript | camelCase 或 kebab-case | `paymentService.ts`, `user-repository.ts` |
| Go | 小写+下划线 | `payment_service.go` |
| Java | PascalCase | `PaymentService.java` |
| Rust | 小写+下划线 | `payment_service.rs` |

### 测试文件命名

| 语言 | 规范 | 示例 |
|------|------|------|
| Python | `test_<module>.py` | `test_payment_service.py` |
| TypeScript | `<module>.test.ts` 或 `<module>.spec.ts` | `payment.service.test.ts` |
| Go | `<module>_test.go` | `payment_service_test.go` |
| Java | `<ClassName>Test.java` | `PaymentServiceTest.java` |
| Rust | `<module>_test.rs` 或 test 模块内 | `mod test { }` |

---

## 反模式（Bad Naming）

```python
# ❌ 坏
x = get_user(123)
flag = True
lst = [1, 2, 3]
temp = do_something()

# ✅ 好
user = get_user(user_id=123)
is_authenticated = True
user_ids = [1, 2, 3]
result = process_payment(order)
```

```typescript
// ❌ 坏
let d = getData();
let r = result;
let b = true;

// ✅ 好
let userData = fetchUserData(userId);
let paymentResult = processPayment(order);
let isActive = checkAccountStatus(userId);
```
