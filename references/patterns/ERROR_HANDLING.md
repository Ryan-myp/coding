# 错误处理模式库（Error Handling Patterns）

> 跨语言的统一错误处理最佳实践

---

## 通用原则

1. **错误是可恢复的吗？** — 能恢复就恢复，不能就明确传播
2. **不要吞掉错误** — empty catch/except 是最大的bug来源
3. **错误信息要有意义** — 让调用方能理解发生了什么
4. **不要在错误信息中泄露敏感数据** — 密码、token、内部路径

---

## Python 错误处理

### 自定义异常层次

```python
class DomainError(Exception):
    """业务域异常基类"""
    pass

class PaymentError(DomainError):
    """支付相关错误"""
    pass

class GatewayTimeout(PaymentError):
    """网关超时"""
    def __init__(self, gateway: str, duration_ms: int):
        self.gateway = gateway
        self.duration_ms = duration_ms
        super().__init__(f"Gateway {gateway} timeout after {duration_ms}ms")

# 使用
try:
    result = gateway.pay(amount)
except GatewayTimeout as e:
    logger.warning(f"Retry needed: {e}")
    result = gateway.pay_with_retry(amount, max_retries=3)
```

### 结果对象替代异常（适合业务逻辑）

```python
from dataclasses import dataclass
from typing import Generic, TypeVar

T = TypeVar('T')

@dataclass
class Result(Generic[T]):
    value: T = None
    error: str = None

    @classmethod
    def ok(cls, value: T) -> 'Result[T]':
        return cls(value=value, error=None)

    @classmethod
    def fail(cls, error: str) -> 'Result[T]':
        return cls(value=None, error=error)

    @property
    def is_ok(self) -> bool:
        return self.error is None

# 使用
def process_payment(amount: float) -> Result[PaymentReceipt]:
    if amount <= 0:
        return Result.fail("Amount must be positive")
    receipt = charge_gateway(amount)
    return Result.ok(receipt)
```

---

## TypeScript/JavaScript 错误处理

### 自定义错误类

```typescript
class AppError extends Error {
  constructor(
    public code: string,
    public status: number,
    message: string
  ) {
    super(message);
    this.name = 'AppError';
  }
}

class PaymentError extends AppError {
  constructor(gateway: string, details?: string) {
    super('PAYMENT_ERROR', 502, `Payment gateway ${gateway} error: ${details || 'unknown'}`);
    this.name = 'PaymentError';
  }
}
```

### Either/Result 模式（函数式）

```typescript
type Result<T, E = Error> =
  | { ok: true; value: T }
  | { ok: false; error: E };

function processPayment(amount: number): Result<PaymentReceipt, PaymentError> {
  if (amount <= 0) {
    return { ok: false, error: new PaymentError('INVALID_AMOUNT') };
  }
  try {
    const receipt = await chargeGateway(amount);
    return { ok: true, value: receipt };
  } catch (e) {
    return { ok: false, error: new PaymentError('GATEWAY_FAILURE', e.message) };
  }
}

// 使用
const result = processPayment(100);
if (result.ok) {
  console.log('Paid:', result.value.receiptId);
} else {
  console.error('Failed:', result.error.message);
}
```

---

## Go 错误处理

### 错误哨兵（Error Sentinels）

```go
var (
    ErrNotFound      = errors.New("resource not found")
    ErrUnauthorized  = errors.New("unauthorized")
    ErrRateLimited   = errors.New("rate limited")
)

// 使用
func GetUser(id string) (*User, error) {
    user, err := db.Find(id)
    if err != nil {
        if errors.Is(err, sql.ErrNoRows) {
            return nil, ErrNotFound
        }
        return nil, fmt.Errorf("get user: %w", err)
    }
    return user, nil
}
```

### 结构化错误

```go
type PaymentError struct {
    Gateway  string
    Code     int
    Message  string
    Retryable bool
}

func (e *PaymentError) Error() string {
    return fmt.Sprintf("payment failed: %s (code=%d, retryable=%v)",
        e.Message, e.Code, e.Retryable)
}
```

---

## Java 错误处理

### 检查型 vs 非检查型异常

```java
// 检查型异常 — 必须处理（编译期强制）
public class InsufficientFundsException extends Exception {
    private final BigDecimal shortfall;
    public InsufficientFundsException(BigDecimal shortfall) {
        super(String.format("Short by %.2f", shortfall));
        this.shortfall = shortfall;
    }
}

// 非检查型异常 — 运行时抛出（编程错误）
public class PaymentGatewayException extends RuntimeException {
    public PaymentGatewayException(String message, Throwable cause) {
        super(message, cause);
    }
}
```

---

## Rust 错误处理

### Result 类型

```rust
#[derive(Debug)]
pub enum PaymentError {
    GatewayError(String),
    ValidationError(String),
    Timeout,
}

impl std::fmt::Display for PaymentError {
    fn fmt(&self, f: &mut std::fmt::Formatter<'_>) -> std::fmt::Result {
        match self {
            PaymentError::GatewayError(msg) => write!(f, "Gateway error: {}", msg),
            PaymentError::ValidationError(msg) => write!(f, "Validation error: {}", msg),
            PaymentError::Timeout => write!(f, "Payment gateway timeout"),
        }
    }
}

// 使用 ? 运算符传播错误
fn process_payment(amount: f64) -> Result<Receipt, PaymentError> {
    if amount <= 0.0 {
        return Err(PaymentError::ValidationError("Amount must be positive".to_string()));
    }
    let receipt = gateway_charge(amount)?;
    Ok(receipt)
}
```

---

## 错误处理反模式

```python
# ❌ 吞掉异常
try:
    process_payment()
except:
    pass  # 灾难！

# ✅ 记录并处理
try:
    process_payment()
except PaymentError as e:
    logger.error(f"Payment failed: {e}")
    notify_ops(e)
```

```typescript
// ❌ 错误消息泄露敏感信息
catch (e) {
  return res.status(500).json({ error: e.message }); // 可能泄露内部路径
}

// ✅ 通用错误消息
catch (e) {
  logger.error('Payment processing failed', { error: e.message });
  return res.status(500).json({ error: 'Payment processing failed' });
}
```
