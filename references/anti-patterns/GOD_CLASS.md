# 上帝类反模式（God Class Anti-Pattern）

> 识别和拆分过于庞大的类

## 问题表现

```python
# ❌ 上帝类 — 做了所有事情
class UserService:
    def validate_email(self, email): ...
    def hash_password(self, password): ...
    def send_welcome_email(self, user): ...
    def generate_token(self, user): ...
    def query_database(self, user_id): ...
    def format_response(self, data): ...
    def log_activity(self, user, action): ...
    def cache_result(self, key, value): ...
    def send_notification(self, user, msg): ...
    def update_profile(self, user, data): ...
    # ... 还有 40 个方法
```

```typescript
// ❌ TypeScript 上帝类
class UserService {
  validateEmail(email: string): boolean { ... }
  hashPassword(password: string): string { ... }
  sendWelcomeEmail(user: User): void { ... }
  generateToken(user: User): string { ... }
  findUserById(id: string): Promise<User> { ... }
  formatResponse(data: any): Response { ... }
  logActivity(user: User, action: string): void { ... }
  // ... 还有 50 个方法
}
```

```go
// ❌ Go 上帝结构体
type UserService struct {
    db       *sql.DB
    cache    *redis.Client
    mailer   *email.Mailer
    logger   *log.Logger
    config   Config
}

func (u *UserService) ValidateEmail(...) { }
func (u *UserService) HashPassword(...) { }
func (u *UserService) SendWelcomeEmail(...) { }
// ... 还有 60 个方法
```

## 识别指标

| 指标 | 阈值 | 含义 |
|------|------|------|
| 方法数量 | > 15 | 可能的上帝类 |
| 文件行数 | > 500 | 需要拆分 |
| 依赖注入参数 | > 5 | 职责过多 |
| 测试文件行数 | > 300 | 被测物过于复杂 |

## 修复方案

### 原则：单一职责 + 依赖注入

```python
# ✅ 拆分为多个职责明确的类
class UserService:
    def __init__(
        self,
        validator: UserValidator,
        hasher: PasswordHasher,
        token_provider: TokenProvider,
        repository: UserRepository,
        notifier: UserNotifier,
    ):
        self._validator = validator
        self._hasher = hasher
        self._token_provider = token_provider
        self._repository = repository
        self._notifier = notifier

    def create_user(self, data: dict) -> User:
        self._validator.validate(data)
        hashed = self._hasher.hash(data["password"])
        user = self._repository.save({
            "email": data["email"],
            "password_hash": hashed,
        })
        token = self._token_provider.generate(user)
        self._notifier.send_welcome(user)
        return user


class UserValidator:
    def validate(self, data: dict) -> None: ...

class PasswordHasher:
    def hash(self, password: str) -> str: ...

class TokenProvider:
    def generate(self, user: User) -> str: ...

class UserRepository:
    def save(self, data: dict) -> User: ...

class UserNotifier:
    def send_welcome(self, user: User) -> None: ...
```

```typescript
// ✅ TypeScript 拆分
interface UserServiceDependencies {
  validator: UserValidator;
  hasher: PasswordHasher;
  tokenProvider: TokenProvider;
  repository: UserRepository;
  notifier: UserNotifier;
}

class UserService {
  constructor(private deps: UserServiceDependencies) {}

  async createUser(data: CreateUserInput): Promise<User> {
    this.deps.validator.validate(data);
    const hashed = this.deps.hasher.hash(data.password);
    const user = await this.deps.repository.save({ email: data.email, passwordHash: hashed });
    const token = this.deps.tokenProvider.generate(user);
    await this.deps.notifier.sendWelcome(user);
    return user;
  }
}
```

## 拆分策略

| 策略 | 适用场景 | 示例 |
|------|---------|------|
| 按领域拆分 | 一类负责多种业务域 | `UserService` → `UserAuthService` + `UserEmailService` |
| 按层拆分 | 同一类混合了不同抽象层 | `UserService` → `UserService` + `UserRepository` |
| 按职责拆分 | 方法职责不相关 | `UserService` → `UserValidator` + `UserNotifier` |

## 反模式警示

```
⚠️ 不要为了拆分而拆分 — 如果类只有 5 个方法且都相关，保持内聚
⚠️ 避免过度设计 — 先有第二个使用场景再提取接口
⚠️ 依赖注入不是银弹 — 清晰的构造函数参数比隐式依赖更好
```
