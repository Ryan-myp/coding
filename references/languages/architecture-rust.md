# Rust 架构检查清单

## 1. 所有权与借用

### 检查项
- [ ] 是否避免了不必要的 clone
- [ ] 引用生命周期是否正确标注
- [ ] 是否使用了 `Cow<str>` 避免不必要的分配

```rust
// ❌ 坏：不必要的 clone
fn process_data(data: &String) -> String {
    data.clone().to_uppercase()
}

// ✅ 好：使用引用
fn process_data(data: &str) -> String {
    data.to_uppercase()
}

// ✅ 更好的：按需分配
fn process_data<'a>(data: &'a str, prefix: &str) -> Cow<'a, str> {
    if data.starts_with(prefix) {
        Cow::Borrowed(data)
    } else {
        Cow::Owned(format!("{}{}", prefix, data))
    }
}
```

## 2. 错误处理

### Result 类型
- [ ] 是否使用了 `?` 运算符传播错误
- [ ] 是否定义了有意义的错误类型
- [ ] 是否避免了 `unwrap()` 在生产代码中

```rust
// ❌ 坏
let user = users.find(id).unwrap();  // 可能 panic

// ✅ 好
let user = users.find(id).ok_or_else(|| Error::NotFound(id.to_string()))?;
```

### 自定义错误
```rust
#[derive(Debug)]
pub enum PaymentError {
    GatewayError(String),
    ValidationError(String),
    #[error("timeout after {duration:?}")]
    Timeout { duration: Duration },
}

impl std::fmt::Display for PaymentError {
    fn fmt(&self, f: &mut std::fmt::Formatter<'_>) -> std::fmt::Result {
        match self {
            PaymentError::GatewayError(msg) => write!(f, "Gateway: {}", msg),
            PaymentError::ValidationError(msg) => write!(f, "Validation: {}", msg),
            PaymentError::Timeout { duration } => write!(f, "Timeout after {:?}", duration),
        }
    }
}
```

## 3. 模块化

### 包结构
```
project/
├── src/
│   ├── domain/          # 领域层
│   │   ├── models.rs
│   │   └── errors.rs
│   ├── application/     # 应用层
│   │   ├── services.rs
│   │   └── dtos.rs
│   ├── infrastructure/  # 基础设施层
│   │   ├── repository/
│   │   └── external/
│   └── interfaces/      # 接口层
│       ├── http/
│       └── cli/
├── tests/
│   ├── unit/
│   └── integration/
└── Cargo.toml
```

## 4. 并发安全

- [ ] 是否使用了 `Send` 和 `Sync` 边界
- [ ] 是否避免了数据竞争
- [ ] channel 是否正确使用

```rust
// ✅ 安全的并发模式
use std::sync::{Arc, Mutex};
use std::thread;

let data = Arc::new(Mutex::new(vec![1, 2, 3]));
let mut handles = vec![];

for i in 0..4 {
    let data_clone = Arc::clone(&data);
    handles.push(thread::spawn(move || {
        let mut guard = data_clone.lock().unwrap();
        guard.push(i);
    }));
}

for handle in handles {
    handle.join().unwrap();
}
```

## 5. 零成本抽象

- [ ] 是否理解了抽象的运行时开销
- [ ] 是否避免了过度使用泛型导致的代码膨胀
- [ ] 是否使用了合适的抽象层级

## 6. 测试

- [ ] 是否使用了 `#[cfg(test)]` 模块
- [ ] 是否编写了单元测试和集成测试
- [ ] 是否使用了 `#[should_panic]` 测试预期失败
