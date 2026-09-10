# Python 架构检查清单

## 1. 类型系统

### 检查项
- [ ] 公共 API 是否有类型注解
- [ ] 是否使用了 `typing` 模块的正确类型
- [ ] 是否避免了滥用 `Any`
- [ ] 复杂类型是否使用了 `TypedDict` 或 `dataclass`

```python
# ❌ 坏
def process(data):
    return data['key']

# ✅ 好
from typing import TypedDict, Optional

class UserData(TypedDict):
    name: str
    email: str
    age: Optional[int]

def process_user(data: UserData) -> str:
    return data['name']
```

## 2. 包结构

### 推荐结构
```
project/
├── src/
│   └── mypackage/
│       ├── __init__.py
│       ├── domain/          # 领域模型
│       │   ├── models.py
│       │   └── value_objects.py
│       ├── application/     # 用例/服务
│       │   ├── services.py
│       │   └── dtos.py
│       ├── infrastructure/  # 基础设施
│       │   ├── repositories/
│       │   ├── external/
│       │   └── config.py
│       └── interfaces/      # API入口
│           ├── api/
│           └── cli/
├── tests/
│   ├── unit/
│   ├── integration/
│   └── fixtures/
└── pyproject.toml
```

## 3. 装饰器使用

- [ ] 装饰器是否职责单一
- [ ] 是否避免了装饰器链过深
- [ ] `@property` 是否只用于简单访问
- [ ] 异步装饰器是否正确处理了 await

```python
# ❌ 坏：装饰器链太深且职责混乱
@cache
@retry(max_attempts=3)
@timeout(30)
@validate_input
def process(data): ...

# ✅ 好：单一职责的装饰器
def with_retry(func):
    @wraps(func)
    def wrapper(*args, **kwargs):
        for attempt in range(3):
            try:
                return func(*args, **kwargs)
            except RetryableError:
                if attempt == 2:
                    raise
                time.sleep(2 ** attempt)
    return wrapper
```

## 4. GIL 与并发

- [ ] CPU 密集型任务是否使用了 `multiprocessing`
- [ ] I/O 密集型任务是否使用了 `asyncio`
- [ ] 是否避免了在多线程中共享可变状态
- [ ] 锁的使用是否必要且正确

```python
# ❌ 坏：多线程处理 CPU 密集型任务
threads = [Thread(target=cpu_heavy_task) for _ in range(10)]

# ✅ 好：进程池处理 CPU 密集型任务
from multiprocessing import Pool
with Pool(4) as p:
    results = p.map(cpu_heavy_task, items)
```

## 5. 异常处理

- [ ] 是否定义了自定义异常层次
- [ ] 是否避免了裸 `except:`
- [ ] 异常信息是否包含足够上下文
- [ ] 资源是否正确释放（使用 context manager）

```python
# ❌ 坏
try:
    do_something()
except:
    pass

# ✅ 好
class DomainError(Exception): pass
class ValidationError(DomainError): pass

try:
    do_something()
except ValidationError as e:
    logger.warning(f"Validation failed: {e}")
    return Response(400, error=str(e))
```

## 6. 测试

- [ ] 单元测试是否独立（不依赖外部环境）
- [ ] 是否使用了 `pytest` 的 fixture 管理测试数据
- [ ] 边界条件和异常路径是否有测试覆盖
- [ ] 是否使用了 `unittest.mock` 进行依赖模拟
