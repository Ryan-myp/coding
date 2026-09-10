# 性能优化指南

> 系统性能优化的方法论和工具

---

## 性能分析方法论

```
Measure → Analyze → Optimize → Verify
  │          │          │          │
  ▼          ▼          ▼          ▼
 基准      瓶颈      修复      验证
 测量      定位      回归      对比
```

## Step 1: 建立基准

```python
import time
import statistics

def benchmark(func, *args, iterations=1000):
    times = []
    for _ in range(iterations):
        start = time.perf_counter()
        func(*args)
        times.append(time.perf_counter() - start)

    return {
        "mean_ms": statistics.mean(times) * 1000,
        "p50_ms": statistics.median(times) * 1000,
        "p95_ms": sorted(times)[int(len(times) * 0.95)] * 1000,
        "p99_ms": sorted(times)[int(len(times) * 0.99)] * 1000,
    }
```

## Step 2: 定位瓶颈

### CPU 密集型

```bash
# Python: cProfile
python -m cProfile -s tottime script.py

# Go: pprof
go test -cpuprofile=cpu.prof
go tool pprof cpu.prof

# Node.js
node --prof app.js
node --prof-process isolated-vm-profile.txt

# Java
java -agentpath:/path/to/jprofiler.so MyApp
```

### I/O 密集型

```python
# 检测慢查询
import time

def timed_execute(cursor, sql, params=None):
    start = time.perf_counter()
    result = cursor.execute(sql, params)
    elapsed = time.perf_counter() - start
    if elapsed > 0.1:  # 超过 100ms
        logger.warning(f"Slow query: {elapsed:.3f}s - {sql[:200]}")
    return result
```

### 内存泄漏

```python
# Python: tracemalloc
import tracemalloc
tracemalloc.start()

# ... 运行代码 ...

snapshot = tracemalloc.take_snapshot()
top_stats = snapshot.statistics('lineno')
for stat in top_stats[:10]:
    print(stat)
```

## 常见性能反模式

| 反模式 | 表现 | 修复方案 |
|--------|------|---------|
| N+1 查询 | 循环中单次查询 | 批量查询 / JOIN |
| 未使用索引 | 全表扫描 | EXPLAIN 分析 + 添加索引 |
| 大对象传输 | 响应体过大 | 分页 / 字段选择 |
| 同步阻塞 | 等待 IO 不释放线程 | 异步 / 连接池 |
| 重复计算 | 相同结果反复计算 | 缓存 / memoization |
| 内存泄漏 | 持续增长不释放 | 正确关闭连接/文件 |
| 锁竞争 | 并发时性能下降 | 减少锁粒度 / 无锁结构 |

## 性能预算

```yaml
performance_budget:
  api:
    p50_latency_ms: 100
    p95_latency_ms: 300
    p99_latency_ms: 500
    error_rate: 0.001
  database:
    slow_query_threshold_ms: 100
    connection_pool_min: 5
    connection_pool_max: 50
  frontend:
    fcp_ms: 1500
    lcp_ms: 2500
    cls: 0.1
```

## 持续性能监控

```python
class PerformanceGate:
    def __init__(self, baseline: dict):
        self.baseline = baseline

    def check(self, metrics: dict) -> tuple[bool, str]:
        for key, threshold in self.baseline.items():
            current = metrics.get(key, 0)
            if current > threshold * 1.5:  # 超过 150% 基线
                return False, f"{key}: {current} > {threshold * 1.5}"
        return True, "OK"
```

## 检查清单

### 数据库
- [ ] 慢查询已识别（> 100ms）
- [ ] 查询使用了合适索引
- [ ] 无 N+1 查询模式
- [ ] 大表查询已分页
- [ ] 连接池配置合理

### 应用层
- [ ] 热点数据已缓存
- [ ] 缓存有合理的 TTL 和淘汰策略
- [ ] 异步处理非关键路径
- [ ] 无不必要的序列化

### 系统层
- [ ] CPU 使用率 < 70%
- [ ] 内存使用有空间
- [ ] 网络延迟正常
- [ ] 磁盘 IO 未饱和
