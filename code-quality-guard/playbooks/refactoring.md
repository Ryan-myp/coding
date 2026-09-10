# 重构手册 Playbook

## 触发条件

- 代码可读性差，难以理解
- 新功能需要修改大量已有代码
- 存在重复代码块
- 函数/类过于庞大
- 架构违背分层原则

## 重构原则

1. **小步前进** — 每次只做一个小的、安全的改变
2. **测试保护** — 有测试才重构，没有就先写测试
3. **保持行为** — 重构不改变外部行为
4. **频繁提交** — 每次重构后提交，方便回退

## 重构策略库

### 1. 提取函数（Extract Function）

**适用：** 函数过长（>50行）、一段代码有明确目的

```python
# ❌ 坏：长函数
def process_order(order):
    # 验证
    if not order.items:
        raise ValueError("No items")
    total = 0
    for item in order.items:
        if item.stock < item.qty:
            raise StockError(f"Insufficient stock for {item.id}")
        total += item.price * item.qty
    # 计算
    tax = total * TAX_RATE
    shipping = calculate_shipping(order.shipping_address)
    # 持久化
    order.total = total + tax + shipping
    db.save(order)
    # 通知
    send_confirmation(order)
    return order

# ✅ 好：提取为多个小函数
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
```

### 2. 提取类（Extract Class）

**适用：** 类职责过多（>15方法）、类过长（>500行）

```typescript
// ❌ 坏：上帝类
class UserService {
  validateEmail(email: string): boolean { ... }
  hashPassword(password: string): string { ... }
  sendWelcomeEmail(user: User): void { ... }
  generateToken(user: User): string { ... }
  findUserById(id: string): Promise<User> { ... }
  // ... 15+ methods
}

// ✅ 好：按职责拆分
class UserService {
  constructor(
    private validator: UserValidator,
    private hasher: PasswordHasher,
    private tokenProvider: TokenProvider,
    private repository: UserRepository,
    private notifier: UserNotifier,
  ) {}
  async createUser(data: CreateUserInput): Promise<User> {
    this.validator.validate(data);
    const hashed = this.hasher.hash(data.password);
    const user = await this.repository.save({ email: data.email, passwordHash: hashed });
    const token = this.tokenProvider.generate(user);
    await this.notifier.sendWelcome(user);
    return { ...user, token };
  }
}
```

### 3. 替换条件表达式（Replace Conditional with Polymorphism）

**适用：** 大量 if-else 分支处理同类问题

```python
# ❌ 坏：条件爆炸
def get_shipping_cost(order):
    if order.country == "US":
        if order.total > 100:
            return 0
        elif order.total > 50:
            return 5
        else:
            return 10
    elif order.country == "CA":
        return 15
    elif order.country == "UK":
        return 20
    else:
        return 50

# ✅ 好：多态
class ShippingStrategy(ABC):
    @abstractmethod
    def calculate(self, order: Order) -> float: ...

class USShipping(ShippingStrategy):
    def calculate(self, order: Order) -> float:
        if order.total > 100: return 0
        if order.total > 50: return 5
        return 10

class InternationalShipping(ShippingStrategy):
    def __init__(self, base_cost: float):
        self.base_cost = base_cost
    def calculate(self, order: Order) -> float:
        return self.base_cost

STRATEGIES = {
    "US": USShipping(),
    "CA": InternationalShipping(15),
    "UK": InternationalShipping(20),
}

def get_shipping_cost(order: Order) -> float:
    strategy = STRATEGIES.get(order.country, InternationalShipping(50))
    return strategy.calculate(order)
```

### 4. 引入策略模式（Introduce Strategy）

**适用：** 多种算法可切换

```go
// ❌ 坏
func processPayment(method string, amount float64) (*Payment, error) {
    if method == "alipay" {
        return callAlipay(amount)
    } else if method == "wechat" {
        return callWechat(amount)
    } else if method == "stripe" {
        return callStripe(amount)
    }
    return nil, fmt.Errorf("unknown payment method")
}

// ✅ 好
type PaymentStrategy interface {
    Process(ctx context.Context, amount float64) (*Payment, error)
}

func processPayment(ctx context.Context, strategy PaymentStrategy, amount float64) (*Payment, error) {
    return strategy.Process(ctx, amount)
}
```

### 5. 引入 Guard Clause

**适用：** 深层嵌套的条件判断

```python
# ❌ 坏：深层嵌套
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

# ✅ 好：Guard Clause
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

### 6. 提取配置（Extract Config）

**适用：** 硬编码的值

```python
# ❌ 坏
GATEWAY_URL = "https://pay.example.com/api"
MAX_RETRIES = 3
TIMEOUT_MS = 30000
API_KEY = os.environ.get("PAYMENT_API_KEY")

# ✅ 好
@dataclass(frozen=True)
class PaymentConfig:
    gateway_url: str = field(default_factory=lambda: os.environ["PAYMENT_GATEWAY_URL"])
    max_retries: int = field(default_factory=lambda: int(os.environ.get("PAYMENT_MAX_RETRIES", "3")))
    timeout_ms: int = field(default_factory=lambda: int(os.environ.get("PAYMENT_TIMEOUT_MS", "30000")))
```

## 重构安全检查清单

- [ ] 有测试保护
- [ ] 每次重构后运行测试
- [ ] 行为没有改变
- [ ] 提交粒度足够小
- [ ] 重构后有 code review
- [ ] 没有引入新的依赖
- [ ] 文档/注释已更新

## 重构反模式

| 反模式 | 表现 | 避免方法 |
|--------|------|---------|
| 没有测试就重构 | 改了代码但不知道是否破坏 | 先写测试再重构 |
| 一次性大重构 | 改动过大，难以 review | 小步重构，频繁提交 |
| 重构引入了新bug | 改错了东西 | 每次只做一个改变 |
| 过度抽象 | 为了抽象而抽象 | 遵循 YAGNI，第三次使用再抽象 |
| 重构了不该重构的代码 | 改动无关代码 | 只重构有明确问题的代码 |
