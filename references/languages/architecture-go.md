# Go 架构检查清单

## 1. 接口设计

### 检查项
- [ ] 接口是否小而专注（Go 习惯 1-3 个方法的接口）
- [ ] 是否遵循接受 interface、返回 struct 的原则
- [ ] 是否避免了过早抽象

```go
// ❌ 坏：接口太大
type UserRepository interface {
    FindByID(ctx context.Context, id string) (*User, error)
    FindByEmail(ctx context.Context, email string) (*User, error)
    Save(ctx context.Context, user *User) error
    Delete(ctx context.Context, id string) error
    List(ctx context.Context, page, size int) ([]*User, error)
    Count(ctx context.Context) (int, error)
}

// ✅ 好：按需定义小接口
type UserSaver interface {
    Save(ctx context.Context, user *User) error
}

type UserFinder interface {
    FindByID(ctx context.Context, id string) (*User, error)
}

// 需要时组合
type UserService struct {
    finder  UserFinder
    saver   UserSaver
}
```

## 2. 错误处理

- [ ] 是否使用了 `errors.Is` 和 `errors.As` 检查错误
- [ ] 是否定义了错误哨兵（error sentinels）
- [ ] 是否避免了裸 `if err != nil` 无上下文

```go
// ❌ 坏
user, err := db.Find(id)
if err != nil {
    return nil, err  // 丢失了上下文
}

// ✅ 好
user, err := db.Find(id)
if err != nil {
    if errors.Is(err, sql.ErrNoRows) {
        return nil, fmt.Errorf("get user %q: %w", id, ErrNotFound)
    }
    return nil, fmt.Errorf("get user %q: %w", id, err)
}
```

## 3. Context 传递

- [ ] 所有 IO 操作是否接收 context
- [ ] 是否避免了在 context 中传递不必要的数据
- [ ] 是否设置了合理的超时

```go
// ❌ 坏
func ProcessPayment(amount float64) (*Receipt, error) {
    // 没有超时控制
    return gateway.Charge(amount)
}

// ✅ 好
func ProcessPayment(ctx context.Context, amount float64) (*Receipt, error) {
    ctx, cancel := context.WithTimeout(ctx, 5*time.Second)
    defer cancel()
    return gateway.Charge(ctx, amount)
}
```

## 4. Option Pattern

```go
// ✅ Go 惯用的函数式配置
type PaymentConfig struct {
    Timeout    time.Duration
    MaxRetries int
    Logger     *log.Logger
}

type PaymentOption func(*PaymentConfig)

func WithTimeout(d time.Duration) PaymentOption {
    return func(c *PaymentConfig) { c.Timeout = d }
}

func WithMaxRetries(n int) PaymentOption {
    return func(c *PaymentConfig) { c.MaxRetries = n }
}

func NewPaymentGateway(opts ...PaymentOption) *PaymentGateway {
    cfg := &PaymentConfig{
        Timeout:    30 * time.Second,
        MaxRetries: 3,
        Logger:     log.Default(),
    }
    for _, opt := range opts {
        opt(cfg)
    }
    return &PaymentGateway{config: *cfg}
}
```

## 5. 并发模式

- [ ] 是否使用了 `sync.WaitGroup` 等待 goroutine
- [ ] channel 是否正确使用（producer/consumer 模式）
- [ ] 是否避免了 goroutine 泄漏
- [ ] 互斥锁的使用范围是否最小化

```go
// ❌ 坏：goroutine 泄漏风险
go func() {
    result := heavyComputation()
    // 没有等待，result 可能永远不会被使用
}()

// ✅ 好：使用 channel 传递结果
resultCh := make(chan Result, 1)
go func() {
    resultCh <- heavyComputation()
}()

select {
case result := <-resultCh:
    process(result)
case <-time.After(5 * time.Second):
    return ErrTimeout
}
```

## 6. 包结构

```
project/
├── cmd/                  # 可执行入口
│   └── server/
│       └── main.go
├── internal/             # 内部实现（不被外部 import）
│   ├── domain/
│   ├── application/
│   └── infrastructure/
├── pkg/                  # 可复用的包
├── api/                  # API 定义
└── tests/
```
