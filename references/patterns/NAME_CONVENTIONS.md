# 命名规范库（Naming Conventions）

> 统一命名风格，提升代码可读性

## 1. 变量命名

### 1.1 基本原则
- 使用**有意义的名称**，让读者一眼理解用途
- 避免缩写（除非是行业通用缩写如 `id`, `url`, `api`）
- 长度与用途匹配（局部变量可以短，公共 API 要完整）

### 1.2 模式

| 类型 | 规范 | 示例 |
|------|------|------|
| 普通变量 | 小写+下划线 | `user_count`, `order_total` |
| 常量 | 全大写+下划线 | `MAX_RETRY_COUNT`, `API_VERSION` |
| 布尔变量 | `is_`/`has_`/`can_`/`should_` | `is_active`, `has_permission` |
| 集合 | 复数形式 | `users`, `orders`, `items` |
| 单个元素 | 单数形式 | `user`, `order` |

### 1.3 反模式

```python
# ❌ 坏
x = get_user(123)
flag = True
lst = [1, 2, 3]

# ✅ 好
user = get_user(user_id=123)
is_authenticated = True
user_ids = [1, 2, 3]
```

## 2. 函数命名

### 2.1 基本原则
- 以**动词**开头，明确表达动作
- 返回布尔值用 `is_`/`has_`/`can_`
- 返回新对象用 `create_`/`build_`/`fetch_`
- 修改状态用 `update_`/`set_`/`delete_`
- 无返回值（副作用）用 `process_`/`handle_`/`send_`

### 2.2 模式

| 返回值 | 命名前缀 | 示例 |
|--------|---------|------|
| 查询单个 | `get_`/`find_`/`fetch_` | `get_user_by_id`, `find_active_orders` |
| 查询列表 | `list_`/`search_` | `list_users`, `search_products` |
| 创建 | `create_`/`build_` | `create_order`, `build_report` |
| 更新 | `update_`/`modify_` | `update_user_profile` |
| 删除 | `delete_`/`remove_` | `delete_order` |
| 判断 | `is_`/`has_`/`can_` | `is_valid`, `has_permission` |
| 转换 | `to_`/`convert_`/`serialize_` | `to_dict`, `convert_to_json` |
| 处理 | `process_`/`handle_` | `process_payment`, `handle_request` |

## 3. 类命名

### 3.1 基本原则
- 使用**名词**或**名词短语**
- 首字母大写（PascalCase）
- 避免动词前缀（那是函数的职责）
- Interface/Abstract 类可加 `I` 前缀或 `-able`/-`ible` 后缀

### 3.2 模式

| 类型 | 命名方式 | 示例 |
|------|---------|------|
| 普通类 | PascalCase | `UserRepository`, `PaymentProcessor` |
| 异常类 | 名词 + `Error`/`Exception` | `NotFoundError`, `PaymentError` |
| 接口 | I前缀 或 -able后缀 | `IRepository`, `Serializable` |
| 工厂 | 名词 + `Factory` | `PaymentFactory`, `UserFactory` |
| 处理器 | 名词 + `Handler` | `RequestHandler`, `ErrorHandler` |
| 监听器 | 名词 + `Listener` | `OrderListener`, `EventSubscriber` |
| 适配器 | 名词 + `Adapter` | `PaymentAdapter`, `JsonAdapter` |

## 4. 模块/文件命名

- 小写+下划线：`payment_service.py`, `user_repository.py`
- 包名：`payment/`, `users/`, `common/`
- 测试文件：`test_<模块名>.py` 或 `<模块名>_test.py`
