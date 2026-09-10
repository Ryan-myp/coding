# 安全专家检查清单（Security Checklist）

> 详细版，供深度审查时加载

## 1. 输入验证与 sanitization

### 1.1 SQL 注入
- [ ] 所有数据库查询是否使用参数化查询
- [ ] 是否避免了字符串拼接 SQL
- [ ] ORM 使用时是否注意了原生查询部分的安全性

```python
# ❌ 危险
query = f"SELECT * FROM users WHERE id = {user_id}"

# ✅ 安全
cursor.execute("SELECT * FROM users WHERE id = %s", (user_id,))
```

### 1.2 XSS 防护
- [ ] 用户输入是否在输出时进行了 HTML 转义
- [ ] 是否使用了 CSP（Content Security Policy）
- [ ] 富文本输入是否做了 sanitized 处理

### 1.3 命令注入
- [ ] 是否避免了将用户输入直接传入 `os.system()` / `subprocess`
- [ ] 是否使用了参数化而非字符串拼接

```python
# ❌ 危险
os.system(f"ls {user_input}")

# ✅ 安全
subprocess.run(["ls", user_input], shell=False)
```

### 1.4 通用输入验证
- [ ] 所有外部输入是否经过白名单验证
- [ ] 类型、长度、格式是否正确校验
- [ ] 是否有统一的输入校验中间件/装饰器

## 2. 认证与授权

### 2.1 认证
- [ ] 密码是否使用强哈希算法（bcrypt/scrypt/argon2）
- [ ] 是否实现了多因素认证（2FA）
- [ ] Session 管理是否安全（HttpOnly, Secure, SameSite）
- [ ] 是否限制了登录尝试次数

### 2.2 授权
- [ ] 是否在做资源操作前校验权限
- [ ] 是否存在水平越权（IDOR）风险
- [ ] 管理接口是否有额外的权限控制
- [ ] API 是否有 Rate Limiting

## 3. 数据安全

### 3.1 数据加密
- [ ] 传输中是否使用 TLS 1.2+
- [ ] 敏感数据（PII）是否加密存储
- [ ] 加密密钥是否安全存储（不在代码中）

### 3.2 日志安全
- [ ] 是否避免了在日志中打印密码、token、卡号
- [ ] 敏感操作是否有审计日志
- [ ] 日志文件是否有访问控制

### 3.3 密钥管理
- [ ] API Key / Secret 是否通过环境变量获取
- [ ] 是否避免了在代码中硬编码密钥
- [ ] 是否有密钥轮换机制

```python
# ❌ 危险
API_KEY = "sk-abc123def456"

# ✅ 安全
import os
API_KEY = os.environ.get("API_KEY")
```

## 4. 依赖安全

- [ ] 是否定期检查依赖包的 CVE
- [ ] 是否锁定了依赖版本（requirements.txt/poetry.lock）
- [ ] 是否避免了已知有漏洞的依赖版本
- [ ] CI 中是否有依赖安全扫描（如 Snyk/Dependabot）

## 5. 常见安全漏洞 OWASP Top 10

| 漏洞 | 检查要点 |
|------|---------|
| A01 破败的认证 | 密码强度、Session 管理、MFA |
| A02 失效的访问控制 | 水平/垂直越权检查 |
| A03 注入 | SQL/NoSQL/OS/LDAP 注入 |
| A04 不安全设计 | 业务逻辑漏洞 |
| A05 失效的安全配置 | 默认配置、CORS、CSP |
| A06 脆弱组件 | 已知 CVE 依赖 |
| A07 认证与通信失败 | TLS 配置、证书校验 |
| A08 软件与数据完整性 | 反序列化、代码签名 |
| A09 安全日志与监控 | 审计日志、告警 |
| A10 SSRF | 用户控制的 URL 请求 |
