
# 命令行工具

AI Router 提供命令行工具用于查看 token 使用统计。

## 使用方法

### 查看 token 使用统计

```bash
$ python cli/token_stats.py --help                          
usage: token_stats.py [-h] [--by {day,hour}] [--group {model,provider,key}] [--from FROM_DATE] [--to TO_DATE] [--today]

Token usage statistics

options:
  -h, --help            show this help message and exit
  --by {day,hour}       Group statistics by day or hour
  --group {model,provider,key}
                        Group results by model, provider, or API key
  --from FROM_DATE      Start date (YYYY-MM-DD)
  --to TO_DATE          End date (YYYY-MM-DD)
  --today               Show only today's statistics
```

### 输出示例

``` 期: 2025-03-18

===== 2025-03-18 20:00 =====
+--------------------+----------+------------+
| 模型               | 提供商   |   Token 数 |
+====================+==========+============+
| DeepSeek-V3        | volc     |         15 |
+--------------------+----------+------------+
| Doubao-1.5-pro-32k | volc     |        176 |
+--------------------+----------+------------+
小计: 191 tokens

===== 2025-03-18 21:00 =====
+-------------+----------+------------+
| 模型        | 提供商   |   Token 数 |
+=============+==========+============+
| DeepSeek-R1 | volc     |       1358 |
+-------------+----------+------------+
小计: 1358 tokens
```