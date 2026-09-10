# 重构手册

> 从遗留代码到优雅实现的系统化重构指南

---

## 重构前的准备

### 1. 建立安全网

```python
# Step 1: 先写 characterization test（捕获现有行为）
def test_current_payment_behavior():
    """记录现有行为，即使它很奇怪"""
    result = process_payment_old_way(100, "us")
    assert result.status == "processed"  # 即使这个行为不合理，也要先记录
    assert result.tax == 8.5

# Step 2: 在测试保护下重构
def test_payment_still_works_after_refactor():
    result = process_payment_new_way(100, "us")
    assert result.status == "processed"  # 行为不变
    assert result.tax == 8.5
```

### 2. 理解现有代码

```
读 → 跑 → 改 → 验证
 │    │    │    └── 测试通过？
 │    │    └─────── No → 回退
 │    └──────────── Yes → 继续下一步
 └───────────────── 不理解？先加注释
```

---

## 常用重构手法

### 手法 1: Extract Function（提取函数）

**信号：** 函数 > 50 行，或一段代码有明确目的

```python
# Before
def process_order(order):
    if not order.items:
        raise ValueError("No items")
    total = 0
    for item in order.items:
        if item.stock < item.qty:
            raise StockError(f"Insufficient stock for {item.id}")
        total += item.price * item.qty
    tax = total * TAX_RATE
    shipping = calculate_shipping(order.shipping_address)
    order.total = total + tax + shipping
    db.save(order)
    send_confirmation(order)
    return order

# After
def process_order(order: Order) -> Order:
    validate_order(order)
    total = calculate_order_total(order)
    tax = calculate_tax(total)
    shipping = calculate_shipping(order.shipping_address)
    order.total = total + tax + shipping
    persist_order(order)
    send_confirmation(order)
    return order

def validate_order(order: Order) -> None:
    if not order.items:
        raise ValueError("No items")
    for item in order.items:
        if item.stock < item.qty:
            raise StockError(f"Insufficient stock for {item.id}")

def calculate_order_total(order: Order) -> float:
    return sum(item.price * item.qty for item in order.items)
```

### 手法 2: Extract Class（提取类）

**信号：** 类 > 15 方法，或类做了不止一件事

```typescript
// Before: God Class
class UserService {
  validateEmail(email: string): boolean { ... }
  hashPassword(password: string): string { ... }
  sendWelcomeEmail(user: User): void { ... }
  generateToken(user: User): string { ... }
  findUserById(id: string): Promise<User> { ... }
  // ... 15+ methods
}

// After: Separated Concerns
class UserService {
  constructor(
    private validator: UserValidator,
    private hasher: PasswordHasher,
    private tokenProvider: TokenProvider,
    private repository: UserRepository,
    private notifier: UserNotifier,
  ) {}

  async createUser(data: CreateUserInput): Promise<User & { token: string }> {
    this.validator.validate(data);
    const hashed = this.hasher.hash(data.password);
    const user = await this.repository.save({ email: data.email, passwordHash: hashed });
    const token = this.tokenProvider.generate(user);
    await this.notifier.sendWelcome(user);
    return { ...user, token };
  }
}
```

### 手法 3: Replace Conditional with Polymorphism

**信号：** if-else 分支过多（> 3 层）

```python
# Before
def get_shipping_cost(country: str, total: float) -> float:
    if country == "US":
        if total > 100: return 0
        elif total > 50: return 5
        else: return 10
    elif country == "CA": return 15
    elif country == "UK": return 20
    else: return 50

# After: Polymorphism
class ShippingStrategy(ABC):
    @abstractmethod
    def calculate(self, total: float) -> float: ...

class USShipping(ShippingStrategy):
    def calculate(self, total: float) -> float:
        if total > 100: return 0
        if total > 50: return 5
        return 10

class InternationalShipping(ShippingStrategy):
    def __init__(self, base_cost: float):
        self.base_cost = base_cost
    def calculate(self, total: float) -> float:
        return self.base_cost

STRATEGIES: dict[str, ShippingStrategy] = {
    "US": USShipping(),
    "CA": InternationalShipping(15),
    "UK": InternationalShipping(20),
}

def get_shipping_cost(country: str, total: float) -> float:
    strategy = STRATEGIES.get(country, InternationalShipping(50))
    return strategy.calculate(total)
```

### 手法 4: Introduce Guard Clause

**信号：** 深层嵌套的条件判断

```python
# Before: Deep nesting
def approve_loan(applicant):
    if applicant.age >= 18:
        if applicant.income > 0:
            if applicant.credit_score > 600:
                if applicant.debt_to_income < 0.4:
                    return approve(applicant)
                else:
                    return reject("DTI too high")
            else:
                return reject("Credit score too low")
        else:
            return reject("No income")
    else:
        return reject("Under 18")

# After: Guard clauses
def approve_loan(applicant: Applicant) -> LoanDecision:
    if applicant.age < 18:
        return reject("Under 18")
    if applicant.income <= 0:
        return reject("No income")
    if applicant.credit_score <= 600:
        return reject("Credit score too low")
    if applicant.debt_to_income >= 0.4:
        return reject("DTI too high")
    return approve(applicant)
```

### 手法 5: Replace Magic Numbers with Named Constants

```python
# Before
if age < 18:
    return reject("Minor")
if score < 600:
    return reject("Bad credit")
MAX_RETRIES = 3

# After
MIN_AGE = 18
MIN_CREDIT_SCORE = 600
MAX_RETRIES = 3

if age < MIN_AGE:
    return reject("Minor")
if score < MIN_CREDIT_SCORE:
    return reject("Bad credit")
```

### 手法 6: Extract Configuration

```python
# Before: Scattered constants
GATEWAY_URL = "https://pay.example.com/api"
TIMEOUT = 30
MAX_RETRIES = 3

# After: Centralized config
@dataclass(frozen=True)
class PaymentConfig:
    gateway_url: str = field(default_factory=lambda: os.environ["PAYMENT_GATEWAY_URL"])
    timeout_sec: int = field(default_factory=lambda: int(os.environ.get("PAYMENT_TIMEOUT", "30")))
    max_retries: int = field(default_factory=lambda: int(os.environ.get("PAYMENT_MAX_RETRIES", "3")))
```

---

## 重构禁忌

| 禁忌 | 原因 | 替代方案 |
|------|------|---------|
| 无测试就重构 | 无法验证行为不变 | 先补测试 |
| 一次性大重构 | 难以 review，容易引入 bug | 小步迭代 |
| 过度抽象 | 增加复杂度，违反 YAGNI | 第三次使用再抽象 |
| 重构无关代码 | 增加风险，浪费时间 | 只重构有明确问题的代码 |
| 隐藏重构中的 bug | 无法定位问题来源 | 每次只做一个改变 |

## 重构检查清单

- [ ] 有测试保护
- [ ] 每次重构后运行测试
- [ ] 行为没有改变
- [ ] 提交粒度足够小
- [ ] 重构后有 code review
- [ ] 没有引入新的依赖
- [ ] 文档/注释已更新
- [ ] 无临时 TODO 遗留
