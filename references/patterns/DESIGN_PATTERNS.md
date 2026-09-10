# 架构设计模式库（Design Patterns）

> 按语言分类的优秀架构模式，从优质代码中蒸馏提取

---

## 通用架构模式（所有语言适用）

### 1. Repository 模式

**适用场景**：数据访问抽象、测试时 Mock 数据库、多数据源切换

```python
# Python
class UserRepository:
    def __init__(self, db: Database):
        self._db = db

    def find_by_id(self, user_id: int) -> Optional[User]:
        return self._db.query("SELECT * FROM users WHERE id = %s", (user_id,))
```

```typescript
// TypeScript
interface UserRepository {
  findById(id: string): Promise<User | null>;
  findAll(filter: UserFilter): Promise<User[]>;
  save(user: User): Promise<void>;
}

class PrismaUserRepository implements UserRepository {
  async findById(id: string): Promise<User | null> {
    return this.prisma.user.findUnique({ where: { id } });
  }
}
```

```go
// Go
type UserRepository interface {
    FindByID(ctx context.Context, id string) (*User, error)
    FindByEmail(ctx context.Context, email string) (*User, error)
    Save(ctx context.Context, user *User) error
}
```

---

### 2. Strategy 模式

**适用场景**：多种算法可切换、避免 if-else 分支爆炸

```python
# Python
class PaymentStrategy(ABC):
    @abstractmethod
    def pay(self, amount: float, currency: str) -> PaymentResult: ...

class AlipayStrategy(PaymentStrategy):
    def pay(self, amount: float, currency: str) -> PaymentResult:
        return self._call_alipay_api(amount, currency)

class WechatPayStrategy(PaymentStrategy):
    def pay(self, amount: float, currency: str) -> PaymentResult:
        return self._call_wechat_api(amount, currency)
```

```typescript
// TypeScript
interface PaymentStrategy {
  pay(amount: number, currency: string): Promise<PaymentResult>;
}

const strategies: Record<string, PaymentStrategy> = {
  alipay: new AlipayStrategy(),
  wechat: new WechatStrategy(),
  stripe: new StripeStrategy(),
};
```

---

### 3. Circuit Breaker 模式

**适用场景**：调用外部服务、防止级联故障

```python
# Python
class CircuitBreaker:
    def __init__(self, failure_threshold=5, reset_timeout=60):
        self._failures = 0
        self._threshold = failure_threshold
        self._last_failure = 0
        self._state = "closed"

    def call(self, func, *args, **kwargs):
        if self._state == "open":
            if time.time() - self._last_failure > self._reset_timeout:
                self._state = "half-open"
            else:
                raise ServiceUnavailable("Circuit is open")
        try:
            result = func(*args, **kwargs)
            self._on_success()
            return result
        except Exception as e:
            self._on_failure()
            raise
```

---

### 4. Builder 模式

**适用场景**：对象参数众多且大部分可选

```python
# Python
class ReportBuilder:
    def __init__(self):
        self._title = ""
        self._data = []
        self._format = "pdf"

    def set_title(self, title: str) -> 'ReportBuilder':
        self._title = title
        return self

    def build(self) -> Report:
        return Report(self._title, self._data, self._format)

# Usage
report = (ReportBuilder()
          .set_title("Q3 Report")
          .add_data(q3_data)
          .set_format("html")
          .build())
```

```typescript
// TypeScript
class ReportBuilder {
  private _title = '';
  private _data: DataPoint[] = [];
  private _format: 'pdf' | 'html' | 'csv' = 'pdf';

  setTitle(title: string): this { this._title = title; return this; }
  addData(data: DataPoint[]): this { this._data.push(...data); return this; }
  setFormat(format: 'pdf' | 'html' | 'csv'): this { this._format = format; return this; }
  build(): Report { return new Report(this._title, this._data, this._format); }
}
```

---

### 5. Guard Clause 模式

**适用场景**：减少嵌套、提升可读性

```python
# 反模式：深层嵌套
def process_order(order):
    if order.status == "pending":
        if order.user.is_active:
            if order.total > 0:
                # ... 10层嵌套
```

```python
# 正确模式：Guard Clause
def process_order(order: Order) -> OrderResult:
    if order.status != "pending":
        raise OrderError("order must be pending")
    if not order.user.is_active:
        raise UserError("user is inactive")
    if order.total <= 0:
        raise ValueError("total must be positive")
    # 正常流程
    return do_process(order)
```

---

### 6. Configuration Externalization 模式

**适用场景**：环境差异配置、密钥管理

```python
# Python
from dataclasses import dataclass
import os

@dataclass(frozen=True)
class PaymentConfig:
    gateway_url: str = field(default_factory=lambda: os.environ["PAYMENT_GATEWAY_URL"])
    timeout: int = field(default_factory=lambda: int(os.environ.get("PAYMENT_TIMEOUT", "30")))
    max_retries: int = field(default_factory=lambda: int(os.environ.get("PAYMENT_MAX_RETRIES", "3")))
```

```typescript
// TypeScript
interface AppConfig {
  gatewayUrl: string;
  timeoutMs: number;
  maxRetries: number;
}

function loadConfig(): AppConfig {
  return {
    gatewayUrl: process.env.PAYMENT_GATEWAY_URL!,
    timeoutMs: parseInt(process.env.PAYMENT_TIMEOUT || '30000'),
    maxRetries: parseInt(process.env.PAYMENT_MAX_RETRIES || '3'),
  };
}
```

---

## 语言特定模式

### Python 特有

| 模式 | 适用场景 | 示例 |
|------|---------|------|
| Context Manager | 资源管理 | `with open(...) as f:` |
| Decorator | 横切关注点 | `@retry(max_attempts=3)` |
| Dataclass | 简单数据对象 | `@dataclass class User:` |
| Protocol | 结构子类型 | `class Serializable(Protocol):` |

### TypeScript 特有

| 模式 | 适用场景 | 示例 |
|------|---------|------|
| Discriminated Union | 类型安全的状态机 | `type Result = Success | Failure` |
| Generic Constraints | 类型约束 | `function pick<T, K extends keyof T>(...)` |
| Template Literal Types | 类型级字符串 | `type Route = \`/api/\${string}\`` |
| Utility Types | 类型变换 | `Pick<T, K>`, `Partial<T>` |

### Go 特有

| 模式 | 适用场景 | 示例 |
|------|---------|------|
| Option Pattern | 函数式配置 | `func WithTimeout(d time.Duration) Option` |
| Interface Segregation | 小接口组合 | `io.Reader`, `io.Writer` |
| Context Propagation | 取消/超时传递 | `ctx, cancel := context.WithTimeout(...)` |
| Error Sentinel | 错误分类 | `var ErrNotFound = errors.New("not found")` |
