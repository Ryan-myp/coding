# 硬编码反模式（Hardcoded Values Anti-Pattern）

> 识别和修复代码中的硬编码问题

## 问题表现

```python
# ❌ 各种硬编码
GATEWAY_URL = "https://pay.example.com/api"
MAX_RETRIES = 3
TIMEOUT = 30
API_KEY = "sk-abc123def456"
ADMIN_EMAIL = "admin@company.com"

if status == 3:  # 3 代表什么？
    ...

if region == "us_east":  # 硬编码的地区名
    ...
```

```typescript
// ❌ TypeScript 中的硬编码
const STRIPE_KEY = "sk_live_abc123";
const MAX_PAGE_SIZE = 100;

if (env === "production") {
  baseUrl = "https://api.example.com";
}
```

```go
// ❌ Go 中的硬编码
const apiKey = "pk_live_123"
var timeout = 30 * time.Second
```

## 修复方案

### 1. 环境变量

```python
# ✅ Python
import os
from dataclasses import dataclass

@dataclass(frozen=True)
class PaymentConfig:
    gateway_url: str = os.environ["PAYMENT_GATEWAY_URL"]
    timeout: int = int(os.environ.get("PAYMENT_TIMEOUT", "30"))
    max_retries: int = int(os.environ.get("PAYMENT_MAX_RETRIES", "3"))
    api_key: str = os.environ["PAYMENT_API_KEY"]
```

```typescript
// ✅ TypeScript
interface PaymentConfig {
  gatewayUrl: string;
  timeoutMs: number;
  maxRetries: number;
}

function loadConfig(): PaymentConfig {
  return {
    gatewayUrl: process.env.PAYMENT_GATEWAY_URL!,
    timeoutMs: parseInt(process.env.PAYMENT_TIMEOUT || '30000'),
    maxRetries: parseInt(process.env.PAYMENT_MAX_RETRIES || '3'),
  };
}
```

```go
// ✅ Go
type PaymentConfig struct {
    GatewayURL string
    Timeout    time.Duration
    MaxRetries int
}

func LoadPaymentConfig() PaymentConfig {
    return PaymentConfig{
        GatewayURL: os.Getenv("PAYMENT_GATEWAY_URL"),
        Timeout:    time.Duration(checkEnvInt("PAYMENT_TIMEOUT", 30)) * time.Second,
        MaxRetries: checkEnvInt("PAYMENT_MAX_RETRIES", 3),
    }
}
```

### 2. 配置文件

```yaml
# config/payment.yaml
payment:
  gateway_url: https://pay.example.com/api
  timeout_ms: 30000
  max_retries: 3
  environments:
    production:
      api_key: ${PAYMENT_API_KEY}  # 从环境变量注入
    staging:
      api_key: sk_test_xxx
```

### 3. 枚举替代魔法数字

```python
# ❌
if status == 3:
    ...

# ✅
class OrderStatus(enum.Enum):
    PENDING = 1
    PROCESSING = 2
    COMPLETED = 3
    CANCELLED = 4

if order.status == OrderStatus.COMPLETED:
    ...
```

```typescript
// ❌
const STATUS_PENDING = 1;
const STATUS_ACTIVE = 3;

// ✅
enum OrderStatus {
  PENDING = 1,
  PROCESSING = 2,
  COMPLETED = 3,
  CANCELLED = 4,
}
```

## 检测规则

| 模式 | 检查项 | 严重性 |
|------|--------|--------|
| URL/域名 | 硬编码的 `http://` 或 `https://` | 🔴 Critical |
| 密钥/密码 | 硬编码的 `api_key`, `secret`, `password` | 🔴 Critical |
| 魔法数字 | 大于 1 的数字常量无注释说明 | 🟡 Warning |
| 业务状态码 | 直接使用数字比较而非枚举 | 🟡 Warning |
| 邮箱/地址 | 硬编码的邮件地址 | 🟠 Info |
