# 遗留代码处理 Playbook

## 触发条件

- 接手遗留系统
- 需要修改无法理解的代码
- 测试覆盖率为零
- 代码耦合严重无法单元测试

## 遗留代码的特征

| 特征 | 表现 | 风险等级 |
|------|------|---------|
| 无测试 | 无法安全修改 | 🔴 Critical |
| 高耦合 | 改动一处影响多处 | 🔴 Critical |
| 隐式依赖 | 行为难以预测 | 🟡 High |
| 缺乏文档 | 不知道为什么这样写 | 🟡 High |
| 技术债累积 | 小改大动 | 🟠 Medium |

## 处理策略

### 策略 1：绞杀者模式（Strangler Fig）

```
旧系统 ──────────────────────────▶ 逐步替换
    │                              │
    ├──► API Gateway ──────────────┤
    │      ├── 新模块 1 (30%)      │
    │      ├── 新模块 2 (50%)      │
    │      └── 旧模块 (20%)        │
    │                              │
    └──────────────────────────────┘
                    │
                    ▼
                 旧系统废弃
```

**步骤：**
1. 在旧系统外围建立代理层（Facade/Adapter）
2. 逐步将功能迁移到新实现
3. 每次迁移后验证行为一致
4. 旧系统完全替换后移除

### 策略 2：防腐层（Anti-Corruption Layer）

```
┌─────────────┐      ┌──────────────┐      ┌─────────────┐
│  新代码     │ ───▶ │  ACL (适配)   │ ───▶ │  旧系统     │
│  (干净架构) │      │ (转换接口)    │      │ (遗留代码)  │
└─────────────┘      └──────────────┘      └─────────────┘
```

```python
# 防腐层示例
class LegacySystemAdapter:
    """将旧系统的混乱接口适配为干净的领域接口"""

    def __init__(self, legacy_client: LegacyAPI):
        self._client = legacy_client

    def get_user(self, user_id: str) -> User:
        # 旧系统返回的是 dict，混乱的字段名
        raw = self._client.fetchUser(user_id)
        # 适配为干净的领域对象
        return User(
            id=raw.get("usr_id"),
            email=raw.get("e_mail"),
            created_at=parse_date(raw.get("dt_created")),
        )

    def create_order(self, order: Order) -> OrderResult:
        # 旧系统要求特定格式
        legacy_input = {
            "uid": order.user_id,
            "items": [
                {"prod": item.product_id, "qty": item.quantity}
                for item in order.items
            ],
        }
        raw_result = self._client.submitOrder(legacy_input)
        return OrderResult(
            order_id=raw_result.get("ord_id"),
            status=LegacyStatusMap[raw_result.get("st")],
        )
```

### 策略 3：测试伞（Test Umbrella）

在修改前，先建立安全网：

```python
# Step 1: 记录现有行为（characterization test）
def test_existing_payment_behavior():
    """ capture the current behavior, even if it's weird """
    result = process_payment_old_way(100, "us")
    assert result.status == "processed"  # 记录现状

# Step 2: 在测试保护下重构
def test_payment_still_works_after_refactor():
    result = process_payment_new_way(100, "us")
    assert result.status == "processed"  # 行为不变
```

### 策略 4：逐步解耦

```
阶段 1: 添加接口抽象
  - 为关键依赖添加 interface
  - 实现类保持不变

阶段 2: 注入依赖
  - 使用 DI 注入接口
  - 可以 mock 进行测试

阶段 3: 提取子模块
  - 将耦合代码提取为独立模块
  - 原模块改为调用新模块

阶段 4: 替换实现
  - 逐步替换为新的、干净的实现
  - 旧实现保留直到完全迁移
```

## 遗留代码审查要点

修改遗留代码时：

1. **先理解再修改** — 阅读相关测试和日志
2. **最小变更** — 一次只改一件事
3. **添加测试** — 修改前后都记录行为
4. **记录假设** — ADR 记录为什么这样改
5. **逐步推进** — 不要试图一次性重写

## 检查清单

- [ ] 已识别核心依赖图
- [ ] 关键路径有 characterization tests
- [ ] 定义了防腐层/适配器
- [ ] 制定了绞杀者计划
- [ ] 每次变更都有回滚方案
- [ ] 变更日志记录了所有 assumption
- [ ] 有监控覆盖关键路径
- [ ] 团队成员了解遗留系统的约束
