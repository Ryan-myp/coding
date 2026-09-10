# 遗留代码处理指南

> 如何在无测试、高耦合的遗留系统中安全地添加功能

---

## 遗留代码的特征

| 特征 | 表现 | 识别方法 |
|------|------|---------|
| 无测试 | 无法安全修改 | `git ls-files | xargs grep -l "test"` 返回空 |
| 高耦合 | 改动一处影响多处 | `git blame` 显示长期不变 |
| 隐式依赖 | 行为难以预测 | 注释说"不要动这段" |
| 缺乏文档 | 不知道为什么这样写 | 代码与需求文档不一致 |
| 技术债累积 | 小改大动 | PR review 时间异常长 |

## 三种核心策略

### 策略 1: 绞杀者模式（Strangler Fig）

```
旧系统 ──────────────────────────────────────
  │                                             │
  ├──► API Gateway ────────────────────────────┤
  │      ├── 新模块 A (已迁移)                 │
  │      ├── 新模块 B (已迁移)                 │
  │      ├── 新模块 C (迁移中 50%)             │
  │      └── 旧模块 D (待迁移)                 │
  │                                             │
  └─────────────────────────────────────────────┘
                          │
                          ▼
                      旧系统逐步废弃
```

**实施步骤：**
1. 在旧系统外围建立 Facade/API Gateway
2. 识别可独立迁移的边界
3. 逐步将功能迁移到新实现
4. 每次迁移后验证行为一致
5. 旧系统完全替换后移除

### 策略 2: 防腐层（Anti-Corruption Layer）

```
┌─────────────┐         ┌──────────────┐         ┌─────────────┐
│  新代码     │ ◀──────▶ │  ACL (适配器) │ ◀──────▶ │  旧系统     │
│  (干净架构) │         │ (转换接口)    │         │ (遗留代码)  │
└─────────────┘         └──────────────┘         └─────────────┘
```

```python
class LegacyAdapter:
    """将混乱的遗留接口适配为干净的领域接口"""

    def __init__(self, legacy_client: LegacyPaymentAPI):
        self._client = legacy_client

    def process_payment(self, amount: float, user: User) -> PaymentResult:
        # 旧系统返回的是 dict，字段名混乱
        raw = self._client.charge({
            "amt": amount,
            "uid": user.id,
            "cur": "CNY"
        })
        # 适配为干净的结果
        return PaymentResult(
            transaction_id=raw.get("txn_id"),
            status=LegacyStatusMap[raw.get("status_code")],
            amount=amount,
        )
```

### 策略 3: 测试伞（Test Umbrella）

在修改前建立安全网：

```python
# Step 1: 捕获现有行为
def test_capture_current_behavior():
    result = legacy_function(100)
    assert result == expected_result  # 即使结果很奇怪，也要记录

# Step 2: 在测试保护下修改
def test_still_works_after_change():
    result = new_function(100)
    assert result == expected_result  # 行为保持一致
```

## 修改遗留代码的规范

### Rule 1: 先理解，再修改

```
读代码 → 运行 → 加注释 → 修改 → 验证
 │       │      │        │       └── 测试通过？
 │       │      │        └─────── No → 回退重读
 │       │      └──────────────── 为什么这样写？
 │       └──────────────────────── 跑起来看效果
 └──────────────────────────────── 理解逻辑
```

### Rule 2: 最小变更

```python
# ❌ 坏：一次性重写整个模块
class NewPaymentProcessor:
    """完全重写的支付处理器"""
    ...

# ✅ 好：小步修改
def add_discount(order: Order, code: str) -> Order:
    """新增：支持折扣码功能"""
    discount = lookup_discount(code)
    order.total -= discount.amount
    return order
```

### Rule 3: 添加测试

```python
# 每次修改都至少添加一个测试
def test_new_discount_feature():
    order = Order(total=100)
    result = add_discount(order, "SUMMER20")
    assert result.total == 80
```

### Rule 4: 记录假设

```markdown
<!-- ADD_ASSUMPTION: 折扣码格式为 4 位大写字母，有效期 30 天 -->
<!-- ADD_REASON: 旧代码中 discount 逻辑散落在 3 个函数中，统一提取 -->
```

## 依赖图分析

```python
# 识别关键依赖
import ast
import sys

def analyze_dependencies(file_path):
    """分析文件的依赖关系"""
    with open(file_path) as f:
        tree = ast.parse(f.read())

    imports = []
    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            for alias in node.names:
                imports.append(alias.name)
        elif isinstance(node, ast.ImportFrom):
            imports.append(node.module)

    return imports
```

## 检查清单

修改遗留代码时：
- [ ] 已阅读相关代码和测试
- [ ] 理解了现有的行为和意图
- [ ] 添加了 characterization tests
- [ ] 变更范围最小化
- [ ] 添加了新的测试覆盖
- [ ] 更新了文档/注释
- [ ] 运行了全量测试
- [ ] 有回滚方案
- [ ] 记录了改动原因（ADR）

## 何时应该重写 vs 重构

| 情况 | 建议 |
|------|------|
| 系统整体健康，个别模块有问题 | 局部重构 |
| 架构合理，代码实现差 | 重构实现 |
| 架构反模式 + 大量债务 | 绞杀者模式逐步替换 |
| 技术栈已淘汰，无法维护 | 评估重写 ROI |
