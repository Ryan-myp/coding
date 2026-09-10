# 通用安全检查清单（Security — Language Agnostic）

> 基于 OWASP Top 10 + STRIDE 威胁建模框架

## 1. STRIDE 威胁建模

审查每个功能前，先做 5 分钟威胁建模：

| 威胁类型 | 问题 | 典型防护 |
|---------|------|---------|
| **S**poofing | 谁能伪装成合法用户/服务？ | 强认证、签名验证 |
| **T**ampering | 数据能否被篡改？ | 完整性校验、参数化查询 |
| **R**epudiation | 操作能否抵赖？ | 审计日志 |
| **I**nformation Disclosure | 敏感数据是否泄露？ | 加密、最小化输出 |
| **D**enial of Service | 能否被淹没？ | 限流、超时、熔断 |
| **E**levation of Privilege | 能否越权？ | RBAC、权限校验 |

## 2. 输入验证（Always Do）

- [ ] **所有外部输入**在边界处验证（API路由、表单、webhook、消息队列）
- [ ] **数据库查询**使用参数化，禁止字符串拼接
- [ ] **HTML 输出**进行转义或使用框架自动转义
- [ ] **文件上传**验证 MIME 类型和大小限制
- [ ] **URL 重定向**使用白名单验证

```
# 输入验证原则
Trust nothing from outside. Validate at the boundary.
```

## 3. 认证与授权

### 认证
- [ ] 密码使用 bcrypt/scrypt/argon2 哈希（≥12 rounds）
- [ ] Session 使用 httpOnly + secure + sameSite cookie
- [ ] JWT 设置合理过期时间，不使用长有效期 token
- [ ] 实现了登录失败锁定/限流

### 授权
- [ ] 每个资源操作前检查权限（不只是认证）
- [ ] 防止水平越权（IDOR）：检查资源归属
- [ ] 管理接口有额外权限校验
- [ ] API 有 Rate Limiting

## 4. 数据安全

### 传输安全
- [ ] 所有外部通信使用 TLS 1.2+
- [ ] HSTS 已启用
- [ ] 证书固定（certificate pinning）用于高敏感场景

### 存储安全
- [ ] PII/敏感数据加密存储
- [ ] 密钥不硬编码，通过环境变量或密钥管理服务获取
- [ ] 日志不记录敏感信息（密码、token、卡号）

## 5. OWASP Top 10 检查矩阵

| # | 漏洞 | 检查项 |
|---|------|--------|
| 1 | 破败的认证 | 密码强度、Session管理、MFA |
| 2 | 失效的访问控制 | 水平/垂直越权、IDOR |
| 3 | 注入 | SQL/NoSQL/OS/LDAP/XXE |
| 4 | 不安全设计 | 业务逻辑漏洞、竞态条件 |
| 5 | 失效的安全配置 | 默认凭据、CORS、调试开关 |
| 6 | 脆弱组件 | 已知CVE依赖 |
| 7 | 认证与通信失败 | TLS配置、证书校验 |
| 8 | 软件与数据完整性 | 反序列化、代码签名 |
| 9 | 安全日志与监控 | 审计日志、告警 |
| 10 | SSRF | 用户控制的URL请求 |

## 6. 安全坏味道

| 坏味道 | 表现 | 修复 |
|--------|------|------|
| 硬编码密钥 | `api_key = "sk_abc123"` | 环境变量/密钥管理 |
| 字符串拼接SQL | `query = f"SELECT * FROM users WHERE id = '{id}'"` | 参数化查询 |
| eval() 执行 | `eval(user_input)` | 避免动态执行 |
| 不安全的反序列化 | `pickle.loads(data)` / `JSON.parse` without validation | 使用安全格式 |
| 过多信息泄露 | `500 Internal Server Error: {stack_trace}` | 通用错误页 |
| 缺失 CSP | 无 Content-Security-Policy 头 | 配置 CSP |

## 7. 依赖安全

- [ ] 定期运行依赖安全扫描（`npm audit`, `pip audit`, `cargo audit`）
- [ ] 锁定依赖版本（package-lock.json / poetry.lock）
- [ ] 避免直接从 GitHub URL 安装依赖
- [ ] 审查依赖链中的间接依赖
