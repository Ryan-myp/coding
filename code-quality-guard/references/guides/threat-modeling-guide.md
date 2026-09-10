# 威胁建模指南

> 基于 STRIDE 模型的系统安全分析方法

---

## STRIDE 六维分析框架

### Spoofing（伪造）

**问题：** 谁能伪装成合法实体？

**典型攻击：**
- 伪造 JWT token
- 中间人攻击（MITM）
- 会话劫持
- 伪造客户端证书

**缓解措施：**
- 强认证机制（MFA、OAuth 2.0）
- 证书固定（Certificate Pinning）
- TLS 1.3 强制
- Session ID 随机化

```python
# ❌ 坏：不安全的认证
token = request.headers["Authorization"]  # 直接信任

# ✅ 好：验证 + 过期检查
from jose import jwt
token = request.headers["Authorization"].removeprefix("Bearer ")
payload = jwt.decode(token, SECRET_KEY, algorithms=["HS256"])
if payload.get("exp", 0) < time.time():
    raise ExpiredTokenError()
```

### Tampering（篡改）

**问题：** 数据能否在传输或存储中被篡改？

**典型攻击：**
- SQL 注入
- XSS（跨站脚本）
- MITM 修改请求体
- 本地存储篡改

**缓解措施：**
- 参数化查询（防 SQL 注入）
- 输出编码/转义（防 XSS）
- 完整性校验（HMAC/签名）
- WAF 防护

```python
# ❌ 坏：字符串拼接
query = f"SELECT * FROM users WHERE email = '{email}'"

# ✅ 好：参数化查询
cursor.execute("SELECT * FROM users WHERE email = %s", (email,))
```

### Repudiation（抵赖）

**问题：** 用户能否否认执行了某操作？

**典型攻击：**
- 否认发送消息
- 否认进行交易
- 删除操作日志

**缓解措施：**
- 不可变的审计日志
- 数字签名关键操作
- 操作时间戳

```python
# 审计日志模板
audit_log = {
    "event": "payment.processed",
    "actor_id": user.id,
    "timestamp": datetime.utcnow().isoformat(),
    "ip_address": request.ip,
    "signature": hmac_sign({"event": "payment.processed", ...}),
}
```

### Information Disclosure（信息泄露）

**问题：** 敏感信息是否可能泄露？

**典型攻击：**
- 错误信息泄露内部细节
- API 响应包含多余字段
- 日志记录敏感数据
- 侧信道攻击

**缓解措施：**
- 通用错误消息
- API 响应字段白名单
- 日志脱敏
- 最小权限原则

```python
# ❌ 坏：泄露内部细节
raise HTTPException(500, detail=f"Database error: {e}")

# ✅ 好：通用错误 + 详细日志
logger.exception("Database query failed")
raise HTTPException(500, detail="An internal error occurred")
```

### Denial of Service（拒绝服务）

**问题：** 系统能否被恶意压垮？

**典型攻击：**
- DDoS 攻击
- 资源耗尽（内存、连接）
- 无限循环/递归
- 大文件上传

**缓解措施：**
- 速率限制（Rate Limiting）
- 熔断器（Circuit Breaker）
- 请求大小限制
- 超时控制

```python
# 速率限制
from slowapi import Limiter
limiter = Limiter(key_func=get_remote_address)

@app.post("/api/login")
@limiter.limit("5/minute")
async def login(request: Request):
    ...
```

### Elevation of Privilege（权限提升）

**问题：** 低权限用户能否执行高权限操作？

**典型攻击：**
- IDOR（越权访问）
- 水平越权（访问他人数据）
- 垂直越权（管理员功能）
- 权限绕过

**缓解措施：**
- 资源所有权校验
- RBAC/ABAC 权限模型
- 最小权限原则

```python
# ❌ 坏：只检查 ID
order = db.get_order(request.params["order_id"])

# ✅ 好：检查所有权
order = db.get_order(request.params["order_id"])
if order.user_id != current_user.id and not current_user.is_admin:
    raise ForbiddenError()
```

---

## 信任边界图模板

```
┌─────────────────────────────────────────────────────────────┐
│                    INTERNET (Untrusted)                     │
│                                                             │
│  ┌─────────┐    ┌──────────┐    ┌─────────┐               │
│  │  Client  │    │  CDN     │    │ WAF     │               │
│  │ (User)   │───▶│          │───▶│         │               │
│  └─────────┘    └──────────┘    └────┬────┘               │
│                                      │                     │
├──────────────────────────────────────┼─────────────────────┤
│                   TRUST BOUNDARY 1                          │
│                                      │                     │
│  ┌─────────┐    ┌──────────┐       │    ┌─────────┐       │
│  │ API     │───▶│ Auth     │       │───▶│ Logger  │       │
│  │ Gateway │    │ Service  │       │    │         │       │
│  └────┬────┘    └────┬─────┘       │    └────┬────┘       │
│       │              │             │         │            │
├───────┼──────────────┼─────────────┼─────────┼────────────┤
│                   TRUST BOUNDARY 2                          │
│       │              │             │         │            │
│  ┌────▼────┐  ┌──────▼─────┐     │  ┌──────▼────┐       │
│  │ Business│  │ User       │     │  │ Audit     │       │
│  │ Logic   │  │ Service    │     │  │ Service   │       │
│  └────┬────┘  └──────┬─────┘     │  └──────┬────┘       │
│       │              │            │         │            │
├───────┼──────────────┼────────────┼─────────┼────────────┤
│                   TRUST BOUNDARY 3                          │
│       │              │            │         │            │
│  ┌────▼──────────────▼────────────▼─────────▼────┐       │
│  │              DATABASE / CACHE                  │       │
│  └───────────────────────────────────────────────┘       │
└─────────────────────────────────────────────────────────────┘
```

## 威胁报告模板

```markdown
# Threat Model: [功能名称]

## 信任边界
1. HTTP 入口 → API Gateway
2. API Gateway → 内部服务
3. 内部服务 → 数据库

## 资产清单
| 资产 | 类型 | 保护级别 |
|------|------|---------|
| User password | Credential | 🔴 Critical |
| Order data | Business | 🟡 Medium |
| API keys | Credential | 🔴 Critical |

## 识别的威胁
| # | STRIDE | 威胁描述 | 严重度 | 缓解措施 | 状态 |
|---|--------|---------|--------|---------|------|
| 1 | Tampering | SQL 注入风险 | 🔴 High | 参数化查询 | ✅ 已缓解 |
| 2 | Spoofing | JWT 未验证过期 | 🟡 Medium | 添加过期检查 | 🟡 待实现 |
| 3 | Elevation | 未校验订单所有权 | 🔴 High | 添加所有权检查 | 🟡 待实现 |
```

## 自动化威胁检测

```bash
# 使用 threat_model.py 进行自动化分析
python3 scripts/threat_model.py src/payment_service.py --output threat_report.md
```
