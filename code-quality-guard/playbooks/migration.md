# 迁移指南 Playbook

## 触发条件

- 数据库 schema 变更
- 依赖版本升级
- 技术栈迁移
- API 版本升级
- 数据结构重构

## 零停机迁移模式

###模式 1：扩展与收缩（Expand and Contract）

```
Phase 1: 扩展（向前兼容）
  - 添加新字段/新列（nullable/default）
  - 双写：新旧同时写入
  - 新代码读取新字段，旧代码继续工作

Phase 2: 数据迁移
  - 后台脚本迁移数据
  - 验证数据一致性
  - 监控迁移进度

Phase 3: 收缩（向后兼容删除）
  - 切换默认值到新字段
  - 移除旧字段读取逻辑
  - 删除旧字段/旧列
```

### 模式 2：特性开关（Feature Flags）

```python
# 阶段 1：默认关闭
def process_payment(data):
    if use_new_gateway():  # 特性开关
        return new_gateway_charge(data)
    return legacy_gateway_charge(data)

# 阶段 2：小流量灰度
def use_new_gateway() -> bool:
    return random.random() < 0.01  # 1% 流量

# 阶段 3：全量
def use_new_gateway() -> bool:
    return True  # 或从配置读取

# 阶段 4：清理
# 删除 legacy 代码路径
```

### 模式 3：双跑比对（Dual Run）

```python
# 新旧系统同时运行，结果比对
old_result = legacy_process(input)
new_result = new_process(input)

if not compare(old_result, new_result):
    log_mismatch(input, old_result, new_result)
    # 不切换，继续双跑

# 比对稳定后切换
switch_to_new()
```

## 数据库迁移检查清单

### DDL 变更

- [ ] 新增列 nullable 或有默认值
- [ ] 删除列前先停止读取
- [ ] 重命名列用 double-translate（先加新列，迁移数据，删旧列）
- [ ] 索引变更在线进行（ADD INDEX ONLINE）
- [ ] 大表变更分批进行（pt-online-schema-change / gh-ost）

### 数据迁移

- [ ] 迁移脚本幂等（可重复执行）
- [ ] 有回滚方案
- [ ] 迁移前后数据校验
- [ ] 迁移在低峰期执行
- [ ] 有迁移进度监控

## 依赖升级检查清单

### 小版本升级（patch）

- [ ] 阅读 changelog
- [ ] 运行测试套件
- [ ] 灰度发布

### 大版本升级（major）

- [ ] 阅读 migration guide
- [ ] 识别 breaking changes
- [ ] 逐个 dependency 升级（不要 bulk bump）
- [ ] 升级后运行 full test suite
- [ ] 审查 lockfile diff
- [ ] 检查 transitive dependencies
- [ ] 灰度发布 + 监控

## API 版本升级

```
v1 (deprecated)  ──┐
                   ├──▶ 共存期（至少 6 个月）
v2 (current)     ──┘
                   │
                   ▼
               sunset 期（警告 + 监控）
                   │
                   ▼
              v1 下线
```

检查清单：
- [ ] 新旧 API 并存
- [ ] 迁移文档
- [ ] 客户端通知
- [ ] deprecation 头信息
- [ ] sunset 日期明确
- [ ] 旧版本流量监控

## 回滚策略

| 场景 | 回滚方式 |
|------|---------|
| 代码回滚 | revert commit + 重新部署 |
| 数据库回滚 | migration rollback script |
| 数据回滚 | 备份恢复 / 反向迁移脚本 |
| 配置回滚 | 配置文件版本控制 |

## 迁移安全网

```bash
# 迁移前
1. 数据库快照
2. 应用日志基线
3. 关键指标快照

# 迁移中
4. 逐步滚动发布
5. 实时监控错误率
6. 监控性能指标

# 迁移后
7. 数据一致性校验
8. 回归测试
9. 观察期（至少 24h）
```
