# TypeScript/JavaScript 架构检查清单

## 1. 类型系统

### 检查项
- [ ] 是否避免了 `any` 类型
- [ ] 接口/类型是否明确定义
- [ ] 是否使用了泛型约束
- [ ] 联合类型是否充分利用

```typescript
// ❌ 坏
function process(data: any): any {
  return data.result;
}

// ✅ 好
interface ApiResponse<T> {
  data: T;
  status: number;
  message?: string;
}

function process<T>(response: ApiResponse<T>): T {
  return response.data;
}
```

## 2. 模块化

### ESM vs CJS
- [ ] 新项目是否使用 ESM (`import/export`)
- [ ] 是否避免了 `require()` 混用
- [ ] 循环依赖是否已解决

### 模块边界
- [ ] 是否按领域划分模块
- [ ] 内部实现是否通过 `export interface` 限制暴露

```typescript
// ✅ 良好的模块边界
// user.service.ts — 仅导出接口
export interface IUserService {
  findById(id: string): Promise<User>;
  create(input: CreateUserInput): Promise<User>;
}

// user.service.impl.ts — 具体实现
class UserServiceImpl implements IUserService { ... }
export const userService = new UserServiceImpl();
```

## 3. 错误处理

- [ ] 是否使用了统一的错误类层次
- [ ] 异步错误是否通过 Promise rejection 正确传播
- [ ] 是否避免了 `catch { }` 吞掉错误

```typescript
// ❌ 坏
try {
  await fetchData();
} catch {
  // 吞掉了错误
}

// ✅ 好
try {
  await fetchData();
} catch (error) {
  if (error instanceof NetworkError) {
    logger.warn('Network issue', { error });
    return fallbackData();
  }
  throw error; // 重新抛出未知错误
}
```

## 4. 框架特定模式

### React
- [ ] 组件是否职责单一
- [ ] 是否避免了在组件内直接操作 DOM
- [ ] 自定义 Hook 是否遵循命名规范 `useXxx`
- [ ] 状态管理是否适度（避免过度使用全局状态）

### Node.js
- [ ] 是否使用了 middleware 模式处理横切关注点
- [ ] 路由处理器是否只做编排，不包含业务逻辑
- [ ] 是否避免了回调地狱（使用 async/await）

```typescript
// ❌ 坏：路由里包含业务逻辑
app.post('/api/orders', async (req, res) => {
  const user = await db.users.findById(req.userId);
  const product = await db.products.findById(req.body.productId);
  const stock = await checkStock(product);
  // ... 50 行业务逻辑
  res.json(result);
});

// ✅ 好：路由只做参数解析和编排
app.post('/api/orders', authenticate, async (req, res) => {
  const result = await orderService.create({
    userId: req.userId,
    productId: req.body.productId,
    quantity: req.body.quantity,
  });
  res.status(201).json(result);
});
```

## 5. 性能相关

- [ ] 是否避免了不必要的重渲染（React）
- [ ] 大数据处理是否使用了流式处理
- [ ] 是否设置了合适的超时和重试
- [ ] 缓存策略是否合理

## 6. 测试

- [ ] 是否使用了合适的测试框架（Jest/Vitest）
- [ ] 单元测试是否 mock 了外部依赖
- [ ] 集成测试是否覆盖了关键路径
- [ ] 是否使用了 test double 模式
