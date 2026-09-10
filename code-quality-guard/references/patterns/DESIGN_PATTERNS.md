# 设计模式库

> 由蒸馏引擎从高质量代码库中提取，每种模式附多语言示例

---

## GoF 经典模式

### 1. Repository Pattern（仓库模式）

**问题：** 数据访问逻辑散落在业务层，难以测试和替换

**解决：** 抽象数据访问接口，业务层只依赖接口

```python
# Python
class UserRepository(ABC):
    @abstractmethod
    def find_by_id(self, user_id: str) -> Optional[User]: ...

    @abstractmethod
    def save(self, user: User) -> None: ...

class InMemoryUserRepository(UserRepository):
    def __init__(self):
        self._store: dict[str, User] = {}

    def find_by_id(self, user_id: str) -> Optional[User]:
        return self._store.get(user_id)

    def save(self, user: User) -> None:
        self._store[user.id] = user

class DatabaseUserRepository(UserRepository):
    def __init__(self, db: Database):
        self._db = db

    def find_by_id(self, user_id: str) -> Optional[User]:
        row = self._db.execute("SELECT * FROM users WHERE id = ?", (user_id,))
        return User.from_row(row) if row else None

    def save(self, user: User) -> None:
        self._db.execute(
            "INSERT INTO users (id, email, name) VALUES (?, ?, ?)",
            (user.id, user.email, user.name),
        )
```

```typescript
// TypeScript
interface UserRepository {
  findById(id: string): Promise<User | null>;
  save(user: User): Promise<void>;
  findAll(filter: UserFilter): Promise<User[]>;
}

class PrismaUserRepository implements UserRepository {
  constructor(private prisma: PrismaClient) {}
  async findById(id: string): Promise<User | null> {
    return this.prisma.user.findUnique({ where: { id } });
  }
  async save(user: User): Promise<void> {
    await this.prisma.user.upsert({
      where: { id: user.id },
      update: { email: user.email, name: user.name },
      create: user,
    });
  }
}
```

```go
// Go
type UserRepository interface {
    FindByID(ctx context.Context, id string) (*User, error)
    Save(ctx context.Context, user *User) error
    FindByPage(ctx context.Context, page, size int) ([]*User, int, error)
}

type DBUserRepository struct {
    db *sql.DB
}

func (r *DBUserRepository) FindByID(ctx context.Context, id string) (*User, error) {
    // ...
}
```

```rust
// Rust
trait UserRepository: Send + Sync {
    async fn find_by_id(&self, id: &str) -> Result<Option<User>, RepoError>;
    async fn save(&self, user: &User) -> Result<(), RepoError>;
}

struct PostgresRepository {
    pool: PgPool,
}

impl UserRepository for PostgresRepository {
    // ...
}
```

**适用场景：**
- 需要替换数据源（内存/数据库/外部 API）
- 需要单元测试业务逻辑
- 数据访问逻辑复杂，需要统一管理

---

### 2. Strategy Pattern（策略模式）

**问题：** 多种算法可切换，if-else 分支爆炸

**解决：** 将算法封装为独立策略类，通过接口统一调用

```python
# Python
class PaymentStrategy(ABC):
    @abstractmethod
    def pay(self, amount: float, currency: str) -> PaymentResult: ...

class AlipayStrategy(PaymentStrategy):
    def pay(self, amount: float, currency: str) -> PaymentResult:
        # 调用支付宝 API
        ...

class WechatPayStrategy(PaymentStrategy):
    def pay(self, amount: float, currency: str) -> PaymentResult:
        # 调用微信支付 API
        ...

class StripeStrategy(PaymentStrategy):
    def pay(self, amount: float, currency: str) -> PaymentResult:
        # 调用 Stripe API
        ...

# 使用
def checkout(strategy: PaymentStrategy, amount: float) -> PaymentResult:
    return strategy.pay(amount, "CNY")
```

```typescript
// TypeScript
type PaymentMethod = "alipay" | "wechat" | "stripe";

interface PaymentStrategy {
  pay(amount: number, currency: string): Promise<PaymentResult>;
}

const STRATEGIES: Record<PaymentMethod, PaymentStrategy> = {
  alipay: new AlipayGateway(),
  wechat: new WechatPayGateway(),
  stripe: new StripeGateway(),
};

function checkout(method: PaymentMethod, amount: number): Promise<PaymentResult> {
  return STRATEGIES[method].pay(amount, "CNY");
}
```

**适用场景：**
- 同一操作有多种实现方式
- 需要在运行时切换算法
- 避免条件分支膨胀

---

### 3. Observer / Event Emitter（观察者模式）

```typescript
// TypeScript
class EventEmitter {
  private listeners = new Map<string, Set<Function>>();

  on(event: string, listener: Function): void {
    (this.listeners.get(event) ??= new Set()).add(listener);
  }

  emit(event: string, data?: unknown): void {
    this.listeners.get(event)?.forEach(l => l(data));
  }

  off(event: string, listener: Function): void {
    this.listeners.get(event)?.delete(listener);
  }
}

// 使用
const emitter = new EventEmitter();
emitter.on("order.created", (order) => sendNotification(order));
emitter.on("order.created", (order) => updateInventory(order));
emitter.emit("order.created", order);
```

---

### 4. Builder Pattern（构建者模式）

```python
# Python
@dataclass
class OrderBuilder:
    user_id: str = ""
    items: list[OrderItem] = field(default_factory=list)
    shipping_address: Address = field(default_factory=Address)
    payment_method: str = ""
    notes: str = ""

    def user(self, user_id: str) -> "OrderBuilder":
        self.user_id = user_id; return self

    def item(self, item: OrderItem) -> "OrderBuilder":
        self.items.append(item); return self

    def build(self) -> Order:
        if not self.user_id:
            raise ValueError("user_id is required")
        if not self.items:
            raise ValueError("items is required")
        return Order(
            user_id=self.user_id,
            items=self.items,
            total=sum(i.price * i.qty for i in self.items),
        )

# 使用
order = (OrderBuilder()
    .user("user_123")
    .item(OrderItem(product_id="p1", qty=2, price=29.99))
    .build())
```

```go
// Go - Functional Options
type Order struct {
    UserID    string
    Items     []OrderItem
    Total     float64
    Priority  bool
    GiftWrap  bool
}

type OrderOption func(*Order)

func WithPriority() OrderOption       { return func(o *Order) { o.Priority = true } }
func WithGiftWrap() OrderOption       { return func(o *Order) { o.GiftWrap = true } }
func WithItems(items ...OrderItem) OrderOption {
    return func(o *Order) { o.Items = items }
}

func NewOrder(userID string, opts ...OrderOption) *Order {
    o := &Order{UserID: userID}
    for _, opt := range opts { opt(o) }
    return o
}

// 使用
order := NewOrder("user_123",
    WithItems(item1, item2),
    WithPriority(),
)
```

---

## 架构模式

### 5. Circuit Breaker（熔断器）

```python
import time
from enum import Enum

class State(Enum):
    CLOSED = "closed"     # 正常
    OPEN = "open"         # 熔断
    HALF_OPEN = "half_open"  # 试探恢复

class CircuitBreaker:
    def __init__(self, failure_threshold=5, recovery_timeout=30):
        self._threshold = failure_threshold
        self._timeout = recovery_timeout
        self._state = State.CLOSED
        self._failures = 0
        self._opened_at = 0.0

    def call(self, func, *args, **kwargs):
        if self._state == State.OPEN:
            if time.time() - self._opened_at > self._timeout:
                self._state = State.HALF_OPEN
            else:
                raise ServiceUnavailable("Circuit breaker open")

        try:
            result = func(*args, **kwargs)
            self._on_success()
            return result
        except Exception as e:
            self._on_failure()
            raise

    def _on_success(self):
        self._failures = 0
        self._state = State.CLOSED

    def _on_failure(self):
        self._failures += 1
        if self._failures >= self._threshold:
            self._state = State.OPEN
            self._opened_at = time.time()
```

### 6. Bulkhead（隔离舱）

```python
# 不同功能使用独立的资源池
from concurrent.futures import ThreadPoolExecutor

class Bulkhead:
    def __init__(self, max_concurrent: int):
        self._executor = ThreadPoolExecutor(max_workers=max_concurrent)
        self._semaphore = threading.Semaphore(max_concurrent)

    def submit(self, fn, *args, **kwargs):
        future = self._executor.submit(fn, *args, **kwargs)
        return future

# 支付和通知互不影响
payment_bulkhead = Bulkhead(max_concurrent=10)
notification_bulkhead = Bulkhead(max_concurrent=5)
```

### 7. Retry with Exponential Backoff

```python
import functools
import random
import time

def retry(max_attempts=3, base_delay=1.0, max_delay=60.0, exceptions=(Exception,)):
    def decorator(func):
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            for attempt in range(1, max_attempts + 1):
                try:
                    return func(*args, **kwargs)
                except exceptions as e:
                    if attempt == max_attempts:
                        raise
                    delay = min(base_delay * (2 ** (attempt - 1)), max_delay)
                    jitter = delay * random.uniform(0, 0.1)
                    time.sleep(delay + jitter)
        return wrapper
    return decorator
```

### 8. Chain of Responsibility（责任链）

```typescript
// TypeScript
type Handler = (req: Request, next: () => Response) => Response;

function chain(...handlers: Handler[]): Handler {
  return (req: Request, next = () => ({ status: 404 })) => {
    return handlers.reduceRight(
      (nextHandler, handler) => () => handler(req, nextHandler),
      next,
    )();
  };
}

// 使用
const middleware = chain(
  (req, next) => { /* auth */ return next(); },
  (req, next) => { /* rate limit */ return next(); },
  (req, next) => { /* cors */ return next(); },
  (req, next) => { /* business logic */ return next(); },
);
```

---

## 错误处理模式

### 9. Result Type（结果类型）

```rust
// Rust
enum Result<T, E> {
    Ok(T),
    Err(E),
}

fn parse_config(path: &str) -> Result<Config, ConfigError> {
    let content = fs::read_to_string(path)?;
    let config: Config = toml::from_str(&content)
        .map_err(ConfigError::Parse)?;
    Ok(config)
}
```

```typescript
// TypeScript
type Result<T, E = Error> = { ok: true; value: T } | { ok: false; error: E };

function parseJSON<T>(input: string): Result<T> {
  try {
    return { ok: true, value: JSON.parse(input) as T };
  } catch (e) {
    return { ok: false, error: e as Error };
  }
}
```

### 10. Guard Clause（守卫子句）

```python
# ✅ 好：扁平结构
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

### 11. Error Context Enrichment（错误上下文富化）

```python
class AppError(Exception):
    def __init__(self, message: str, context: dict | None = None):
        super().__init__(message)
        self.context = context or {}

# 使用
try:
    result = process_payment(amount, user)
except PaymentError as e:
    raise AppError(
        "Failed to process payment",
        context={"user_id": user.id, "amount": amount, "gateway": "stripe"},
    ) from e
```
