# 蒸馏日志

> 记录每次蒸馏的结果，用于追踪 Skill 的进化历史

## 格式

```jsonl
{
  "timestamp": "2025-09-10T14:30:00",
  "source": "src/service/payment.py",
  "patterns_found": 3,
  "bad_smells_found": 2,
  "patterns": [...],
  "bad_smells": [...]
}
```

## 历史记录

<!-- 每次蒸馏追加一行 JSON -->
