# 设计模式库（Design Patterns）

> 从优质代码中蒸馏提取的最佳实践模式

## 1. Repository 模式

```python
# 模式：数据访问抽象
class UserRepository:
    def __init__(self, db: Database):
        self._db = db

    def find_by_id(self, user_id: int) -> Optional[User]:
        return self._db.query("SELECT * FROM users WHERE id = %s", (user_id,))

    def save(self, user: User) -> None:
        self._db.execute("INSERT INTO users (...) VALUES (...)", user.to_dict())
```

**适用场景**：数据访问逻辑需要抽象、测试时需要 Mock 数据库、多数据源切换

## 2. Strategy 模式

```python
# 模式：算法家族封装，可互换
class PaymentStrategy(ABC):
    @abstractmethod
    def pay(self, amount: float) -> PaymentResult: ...

class AlipayStrategy(PaymentStrategy):
    def pay(self, amount: float) -> PaymentResult:
        return self._call_alipay_api(amount)

class WechatPayStrategy(PaymentStrategy):
    def pay(self, amount: float) -> PaymentResult:
        return self._call_wechat_api(amount)

# 使用
def process_payment(strategy: PaymentStrategy, amount: float) -> PaymentResult:
    return strategy.pay(amount)
```

**适用场景**：多种算法可切换、避免大量的 if-else 分支

## 3. Builder 模式

```python
# 模式：复杂对象逐步构建
class ReportBuilder:
    def __init__(self):
        self._title = ""
        self._data = []
        self._format = "pdf"

    def set_title(self, title: str) -> 'ReportBuilder':
        self._title = title
        return self

    def add_data(self, data: list) -> 'ReportBuilder':
        self._data.extend(data)
        return self

    def set_format(self, fmt: str) -> 'ReportBuilder':
        self._format = fmt
        return self

    def build(self) -> Report:
        return Report(self._title, self._data, self._format)
```

**适用场景**：对象参数众多且大部分可选、需要多种构建变体

## 4. Observer / PubSub 模式

```python
# 模式：事件驱动解耦
class EventBus:
    def __init__(self):
        self._listeners: dict[str, list[Callable]] = defaultdict(list)

    def subscribe(self, event: str, handler: Callable):
        self._listeners[event].append(handler)

    def publish(self, event: str, **kwargs):
        for handler in self._listeners[event]:
            handler(**kwargs)
```

**适用场景**：模块间松耦合通信、事件驱动架构

## 5. Circuit Breaker 模式

```python
# 模式：防止级联故障
class CircuitBreaker:
    def __init__(self, failure_threshold=5, reset_timeout=60):
        self._failures = 0
        self._threshold = failure_threshold
        self._last_failure = 0
        self._state = "closed"  # closed | open | half-open

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

**适用场景**：调用外部服务、防止雪崩效应

## 6. 配置外化模式

```python
# 模式：配置与代码分离
from dataclasses import dataclass
from typing import Optional

@dataclass
class PaymentConfig:
    gateway_url: str = ""
    timeout: int = 30
    max_retries: int = 3
    api_key: str = ""

    @classmethod
    def from_env(cls) -> 'PaymentConfig':
        return cls(
            gateway_url=os.environ["PAYMENT_GATEWAY_URL"],
            timeout=int(os.environ.get("PAYMENT_TIMEOUT", "30")),
            api_key=os.environ["PAYMENT_API_KEY"],
        )
```

**适用场景**：环境差异配置、密钥管理、运维可调参数
