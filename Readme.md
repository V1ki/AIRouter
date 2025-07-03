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



# 功能特性

## 预置的 AI 提供商

AI Router 已预置了以下常见的 AI 服务提供商：

### 国际服务
- **OpenAI** - GPT-4o, GPT-4o-mini, GPT-4-turbo, GPT-3.5-turbo
- **Anthropic** - Claude 3 Opus, Sonnet, Haiku, Claude 3.5 Sonnet
- **Google AI** - Gemini 1.5 Pro, Flash, Gemini 2.0 Flash (实验版)
- **DeepSeek** - DeepSeek Chat, DeepSeek Coder

### 国内服务
- **阿里云百炼** - 通义千问 Max, Plus, Turbo
- **智谱 AI** - GLM-4, GLM-4V
- **百度千帆** - 文心一言 4.0
- **讯飞星火** - Spark 4.0 Ultra
- **字节跳动** - 豆包 Pro
- **Moonshot** - Kimi (月之暗面)
- **硅基流动** - 提供多种开源模型的免费服务

这些提供商和模型会在数据库初始化时自动创建，您只需要在管理界面中添加对应的 API Key 即可使用。

# 使用方法

## Docker 部署

1. **准备 .env 文件**

在项目根目录下创建 `.env` 文件，内容示例：

```
DATABASE_URL=postgresql://postgres:postgres@host.docker.internal:5432/model_providers
```

- `host.docker.internal` 让容器内应用连接到宿主机数据库。
- 如数据库运行在其他容器，`host.docker.internal` 替换为对应服务名（如 `db`）。

2. **构建镜像**

```bash
docker build -t ai-router .
```

3. **运行容器**

```bash
docker run --env-file .env -p 8000:8000 ai-router
```

4. **访问服务**

使用`OpenAI` 的库 , 或者任何兼容`OpenAI` 方式的库如`langchain` 等.

<details>
<summary>Langchain 示例</summary>

```python
from langchain_openai import ChatOpenAI

llm = ChatOpenAI(
    model="model_name",
    api_key="your_api_key",
    base_url="http://localhost:8000/v1",
)
```
</details>

<details>
<summary>OpenAI 示例</summary>

```python
import openai

openai.api_key = "your_api_key"
openai.base_url = "http://localhost:8000/v1"

response = openai.chat.completions.create(
    model="model_name",
    messages=[{"role": "user", "content": "Hello, world!"}],
)
```
</details>

<details>
<summary>cURL 示例</summary>

```bash
curl -X POST http://localhost:8000/v1/chat/completions \
  -H "Content-Type: application/json" \
  -d '{"model": "model_name", "messages": [{"role": "user", "content": "Hello, world!"}]}'
```
</details>

## OpenAI Agents SDK 支持

AI Router 现已支持 OpenAI Agents SDK，包括以下功能：

### Assistants (助手)
- 创建、查询、更新、删除助手
- 支持工具配置（functions, code_interpreter, retrieval）
- 元数据和文件管理

### Threads (会话)
- 创建和管理会话线程
- 支持会话元数据

### Messages (消息)
- 在会话中创建和管理消息
- 支持文本、图片等多种内容类型

### Runs (运行)
- 在会话上执行助手
- 支持运行状态跟踪
- 运行步骤详情

### 使用示例

```python
from openai import OpenAI

client = OpenAI(
    api_key="your_api_key",
    base_url="http://localhost:8000/v1"
)

# 创建助手
assistant = client.beta.assistants.create(
    name="Math Tutor",
    instructions="You are a personal math tutor.",
    model="gpt-3.5-turbo"
)

# 创建会话
thread = client.beta.threads.create()

# 添加消息
message = client.beta.threads.messages.create(
    thread_id=thread.id,
    role="user",
    content="I need help solving 2x + 5 = 15"
)

# 运行助手
run = client.beta.threads.runs.create(
    thread_id=thread.id,
    assistant_id=assistant.id
)
```

# Roadmap

- [x] `/v1/models`  模型列表实现. ✅ 2025-03-18
- [x] `/v1/chat/completions` chat 接口实现. ✅ 2025-03-18
- [x] 统计对应的`api key` 使用了多少 token. ✅ 2025-03-18
- [x] 增加命令行用于查看 每天使用的 token. ✅ 2025-03-18
- [x] 增加免费token 额度/赠送金额的设置 ✅ 2025-03-25
- [x] 设置 API Key 以及 模型实现的排序 ✅ 2025-03-25
- [x] 支持 OpenAI Agents SDK (Assistants, Threads, Messages, Runs) ✅ 2025-07-03
- [x] 增加前端界面用于查看和管理 Provider 和 API Key ✅ 2025-07-03
- [x] 增加前端界面用于查看和管理模型以及模型实现 ✅ 2025-07-03
- [x] 增加前端界面用于统计 Token的使用情况 ✅ 2025-07-03