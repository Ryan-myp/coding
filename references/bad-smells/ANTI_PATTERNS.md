# 反模式库（Anti-Patterns）

> 已识别的代码坏味道，供审查时对照

## 1. 硬编码（Hardcode）

### 问题表现
```python
# ❌ 坏
GATEWAY_URL = "https://pay.example.com/api"
MAX_RETRIES = 3
TIMEOUT = 30
API_KEY = "sk-abc123def456"

if status == 3:  # 3 代表什么？
    ...
```

### 修复方案
```python
# ✅ 好
from dataclasses import dataclass

@dataclass
class PaymentConfig:
    gateway_url: str = os.environ["PAYMENT_GATEWAY_URL"]
    max_retries: int = int(os.environ.get("PAYMENT_MAX_RETRIES", "3"))
    timeout: int = int(os.environ.get("PAYMENT_TIMEOUT", "30"))
    api_key: str = os.environ["PAYMENT_API_KEY"]
```

### 蒸馏规则
- 凡是直接出现在代码中的 URL、IP、端口 → 提取为配置
- 凡是直接出现的数字常量（除 0/1 外）→ 考虑提取为命名常量
- 凡是业务状态码 → 提取为枚举

## 2. 上帝类（God Class）

### 问题表现
```python
# ❌ 坏 - 一个类做了所有事
class UserService:
    def validate_email(self, email): ...
    def hash_password(self, password): ...
    def send_welcome_email(self, user): ...
    def generate_token(self, user): ...
    def query_database(self, user_id): ...
    def format_response(self, data): ...
    def log_activity(self, user, action): ...
    # ... 还有 50 个方法
```

### 修复方案
```python
# ✅ 好 - 按职责拆分
class UserService:
    def __init__(self, validator, hasher, token_provider, repository):
        self._validator = validator
        self._hasher = hasher
        self._token_provider = token_provider
        self._repository = repository

    def create_user(self, data):
        self._validator.validate(data)
        hashed = self._hasher.hash(data["password"])
        user = self._repository.save({"email": data["email"], "password": hashed})
        token = self._token_provider.generate(user)
        return {"user": user, "token": token}

class UserValidator:
    def validate(self, data): ...

class PasswordHasher:
    def hash(self, password): ...
```

## 3.  spaghetti 代码（意大利面条代码）

### 问题表现
```python
# ❌ 坏 - 多层嵌套，无从读起
def process_order(order):
    if order.status == "pending":
        if order.user.is_active:
            if order.total > 0:
                for item in order.items:
                    if item.stock > 0:
                        if item.price > 0:
                            # ... 10 层嵌套
                        else:
                            raise ValueError("price")
                    else:
                        raise StockError("out of stock")
            else:
                raise ValueError("total")
        else:
            raise UserError("inactive")
    else:
        raise OrderError("not pending")
```

### 修复方案
```python
# ✅ 好 - Guard Clause 提前返回
def process_order(order: Order) -> OrderResult:
    if order.status != "pending":
        raise OrderError("order must be pending")

    user = order.user
    if not user.is_active:
        raise UserError("user is inactive")

    if order.total <= 0:
        raise ValueError("total must be positive")

    for item in order.items:
        if item.stock <= 0:
            raise StockError(f"item {item.id} out of stock")
        if item.price <= 0:
            raise ValueError(f"item {item.id} price must be positive")

    # 正常流程
    return do_process(order)
```

## 4. 瑞士军刀函数（Swiss Army Function）

### 问题表现
```python
# ❌ 坏 - 一个函数做太多事
def handle_request(request):
    # 解析
    data = json.loads(request.body)
    # 验证
    if not data.get("email"):
        return error(400)
    # 业务逻辑
    user = find_user(data["email"])
    # 计算
    total = calculate_total(user, data["items"])
    # 持久化
    save_order(total)
    # 通知
    send_notification(user, total)
    # 返回
    return success(total)
```

### 修复方案
```python
# ✅ 好 - 单一职责
def handle_request(request: Request) -> Response:
    data = parse_request(request)
    validate(data)
    user = find_or_create_user(data)
    total = calculate_total(user, data.items)
    order = persist_order(total)
    notify_user(user, order)
    return build_response(order)
```

## 5. 功能投射（Feature Regressions / 功能蔓延）

### 问题表现
- 一个模块/文件包含不相关的功能
- 随着需求增长，模块越来越庞大
- 没人敢改，因为不知道会影响什么

### 修复方案
- 建立 Bounded Context（边界上下文）
- 按领域拆分模块
- 设立 Code Review 门禁，阻止无意义的功能增长
