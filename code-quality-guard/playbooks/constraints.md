# 规范约束 Playbook（Constraints）

## 触发条件

- 初始化新项目
- 制定团队编码规范
- 设定质量门禁
- 建立 CI/CD 规则

## 三 Tier 行为准则

### Tier 1: Always Do（必须遵守）

无条件遵守的规则，违反即不通过审查：

```markdown
## Always Do

### 代码质量
- [ ] 所有公开 API 有类型注解/接口定义
- [ ] 函数参数 ≤ 4 个，超出用对象封装
- [ ] 嵌套深度 ≤ 3 层（使用 Guard Clause）
- [ ] 重复代码块提取为函数/模块
- [ ] 魔法数字提取为命名常量

### 安全
- [ ] 所有外部输入在边界处验证
- [ ] 数据库查询使用参数化
- [ ] 密钥通过环境变量获取
- [ ] 敏感信息不在日志中

### 测试
- [ ] 新代码有对应测试
- [ ] 测试命名描述预期行为
- [ ] 边界条件和错误路径有覆盖
- [ ] 测试独立，无隐式依赖

### 提交
- [ ] commit message 遵循 Conventional Commits
- [ ] PR ≤ 300 行（超出自拆分）
- [ ] PR 描述说明 why，不只 what
```

### Tier 2: Ask First（需人工确认）

需要人工审批才能违反的规则：

```markdown
## Ask First

- [ ] 添加新依赖（说明必要性和替代方案）
- [ ] 修改数据库 schema（说明回滚方案）
- [ ] 修改认证/授权逻辑
- [ ] 修改安全相关配置
- [ ] 使用 eval() / exec() / 动态执行
- [ ] 关闭已有的安全检查
- [ ] 跳过测试直接合入
```

### Tier 3: Never Do（绝对禁止）

违反直接不通过，无例外：

```markdown
## Never Do

- [ ] 硬编码密钥/密码/API Key
- [ ] 字符串拼接 SQL 查询
- [ ] 在生产环境使用 console.log/print 调试
- [ ] commit 包含敏感信息
- [ ] 禁用 CSRF/CORS 保护
- [ ] 在前端存储敏感数据（密码、token）
- [ ] 使用已废弃或有已知 CVE 的依赖
- [ ] 绕过认证/授权检查
```

## 质量门禁配置

```json
{
  "quality_gate": {
    "min_score": 70,
    "max_critical_issues": 0,
    "max_warning_issues": 5,
    "required_axes": ["correctness", "security"],
    "min_axis_scores": {
      "correctness": 15,
      "security": 15
    },
    "distillation_candidate_threshold": 90
  }
}
```

## 变更规模规则

| 变更类型 | 最大行数 | 额外要求 |
|---------|---------|---------|
| 修复 typo/格式 | ≤ 10 | 无 |
| 单功能实现 | ≤ 100 | 标准审查 |
| 多功能实现 | ≤ 300 | 架构师审查 |
| 重构 | ≤ 500 | 全角色审查 |
| 大型重构 | > 500 | 必须拆分 |

## 审查级别

| 分数 | 级别 | 审查深度 |
|------|------|---------|
| ≥ 90 | Auto-approve | 仅需一人 review |
| 70-89 | Standard | 标准五轴审查 |
| 50-69 | Deep | 四角色联合审查 + 架构师复核 |
| < 50 | Reject | 必须重写 |
