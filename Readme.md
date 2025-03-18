# AI Router


## 项目来源

项目来源于自己想做的 Agent ,虽然还没做好,但是在中间中遇到了一些问题:
1. 服务提供商太多了, 阿里, 硅基流动, 字节方舟等等.
2. 服务商多太多导致对应需要的 API Key 也增加了. 
3. 不同的平台之间偶尔会有些活动, 如果想要切换请求也很麻烦.
4. 在不同的项目之间,都需要记录一个对应的`.env` 文件用来去保存, 这样也增加了暴露密钥的风险.
5. `langchain` 等库虽然能解决对接不同的模型,但是对于不同的模型替换起来也比较麻烦.

所以我就在想,能不能有一个库能够帮我解决如下痛点
1. 管理我所有的平台下的 `API Key`.
2. 对于使用者,也就是我来说, 只需要一个统一的接口.
3. 有活动的时候,或者说免费的时候,当我有一些账号, 可以自动在这些账号中进行分流.

所以`AI Router` 就出现了, 这个项目最开始在`My Agent` 这个项目中进行了部分实现, 并且我尝试对其增加了部分聊天界面, 但是我很快意识到暂时没有必要. 于是我决定将其拆分出来.



# 使用方法

使用`OpenAI` 的库 , 或者任何兼容`OpenAI` 方式的库如`langchain` 等.

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

# Roadmap

- [x] `/v1/models`  模型列表实现. ✅ 2025-03-18
- [x] `/v1/chat/completions` chat 接口实现. ✅ 2025-03-18
- [x] 统计对应的`api key` 使用了多少 token. ✅ 2025-03-18
- [x] 增加命令行用于查看 每天使用的 token. ✅ 2025-03-18