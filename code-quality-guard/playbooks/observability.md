# 可观测性指南 Playbook

## 触发条件

- 新增服务/模块
- 排查线上问题
- 建立监控体系
- 设置告警

## 三支柱：Logs + Metrics + Traces

```
┌─────────────────────────────────────────────────────────────┐
│                      Observability                          │
├─────────────┬─────────────┬─────────────────────────────────┤
│    Logs     │   Metrics   │           Traces                │
│  "什么发生  │ "发生的      │  "为什么会发生"                 │
│   了？"     │   频率如何？"│                                 │
├─────────────┼─────────────┼─────────────────────────────────┤
│ 结构化日志   │ Counter     │ Span/Segment                    │
│ 日志级别     │ Gauge       │ Context Propagation             │
│ 关联ID       │ Histogram   │ Sampling                        │
│ 上下文字段   │ Summary     │ Distributed Tracing             │
└─────────────┴─────────────┴─────────────────────────────────┘
```

## Logging 规范

### 日志级别

| 级别 | 使用场景 | 示例 |
|------|---------|------|
| DEBUG | 调试详情，生产关闭 | 变量值、循环迭代 |
| INFO | 关键业务流程点 | 用户登录、订单创建 |
| WARNING | 异常但可恢复 | 重试、降级 |
| ERROR | 需要关注的问题 | 请求失败、外部服务错误 |
| FATAL | 系统不可用 | 数据库连接中断 |

### 结构化日志

```python
# ❌ 坏：非结构化
logger.info(f"Processing payment for user {user_id} amount {amount}")

# ✅ 好：结构化
logger.info(
    "payment.processing",
    extra={
        "user_id": user_id,
        "amount": amount,
        "currency": currency,
        "request_id": correlation_id,
    }
)
```

### 日志内容规范

**必须包含：**
- `request_id` / `trace_id` — 关联追踪
- `user_id` — 操作主体
- `action` — 发生了什么
- `result` — 成功/失败

**禁止包含：**
- 密码、token、密钥
- 完整信用卡号
- PII（除非加密）
- 内部 stack trace（生产环境）

### 日志采样

```python
# 高流量路径采样
if random.random() < 0.1:  # 10% 采样
    logger.debug("full_request_payload", extra={"payload": json.dumps(body)})
```

## Metrics 规范

### 四大黄金信号

| 信号 | 含义 | 典型指标 |
|------|------|---------|
| **Latency** | 请求处理时间 | p50/p95/p99 latency |
| **Traffic** | 负载强度 | RPS、并发连接数 |
| **Errors** | 失败率 | 5xx rate、4xx rate |
| **Saturation** | 资源利用率 | CPU、内存、连接池 |

### 指标命名规范

```
{service}.{resource}.{metric}.{unit}

# 示例
payment.gateway.latency_ms
payment.gateway.requests_total
payment.gateway.errors_total
payment.gateway.active_connections
```

### RED 方法（Michael Nygard）

| 维度 | 指标 | 聚合方式 |
|------|------|---------|
| **R**ate | 每秒请求数 | count / time |
| **E**rrors | 错误请求数 | count(where(error)) |
| **D**uration | 请求持续时间 | histogram / summary |

## Tracing 规范

### Context Propagation

```python
# 跨服务传递 trace context
from opentelemetry import trace

tracer = trace.get_tracer(__name__)

with tracer.start_as_current_span("process_payment") as span:
    span.set_attribute("user.id", user_id)
    span.set_attribute("payment.amount", amount)

    # 传播到下游
    carrier = {}
    trace.get_current_span().inject(carrier)
    headers["traceparent"] = carrier["traceparent"]

    result = call_payment_gateway(headers)
```

### Span 设计

```
父 Span: process_payment (user: 123, amount: $50)
├── Span: validate_input (duration: 2ms)
├── Span: charge_gateway (duration: 450ms)
│   ├── Span: connect (duration: 5ms)
│   ├── Span: send_request (duration: 400ms)
│   └── Span: parse_response (duration: 45ms)
├── Span: update_order (duration: 10ms)
└── Span: send_notification (duration: 200ms)
```

## 告警规范

### 告警分级

| 级别 | 响应时间 | 触发条件 | 通知方式 |
|------|---------|---------|---------|
| P0/Critical | 5分钟 | 服务不可用 | PagerDuty + Slack + 电话 |
| P1/High | 15分钟 | 性能严重下降 | PagerDuty + Slack |
| P2/Medium | 1小时 | 错误率升高 | Slack |
| P3/Low | 24小时 | 预警趋势 | Slack |

### 告警原则

1. **每个告警必须有 runbook** — 知道如何处理
2. **告警必须可操作** — 收到后能采取行动
3. **避免告警疲劳** — 宁可使用静默期也不发无效告警
4. **SLO 驱动** — 基于用户体验设定阈值

```yaml
# 告警配置示例
alerts:
  - name: payment_high_error_rate
    expr: rate(payment_gateway_errors_total[5m]) / rate(payment_gateway_requests_total[5m]) > 0.01
    for: 5m
    severity: critical
    runbook: https://wiki.internal/runbooks/payment-errors
    annotations:
      summary: "Payment gateway error rate > 1% for 5 minutes"
```

## 检查清单

- [ ] 关键路径有结构化日志
- [ ] 日志包含 trace_id 关联
- [ ] 敏感信息已从日志中移除
- [ ] 核心指标已定义（RED方法）
- [ ] 黄金信号有监控面板
- [ ] 关键链路有分布式追踪
- [ ] 告警有 runbook
- [ ] 告警阈值基于 SLO
- [ ] 日志有保留策略和采样
- [ ] 异常有统一收集和上报
