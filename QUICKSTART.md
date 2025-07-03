# AI Router 快速启动指南

## 系统要求

- Python 3.8+
- PostgreSQL 数据库
- Node.js 16+ (用于前端)

## 安装步骤

### 1. 后端设置

#### 安装依赖
```bash
pip install -r requirements.txt
```

#### 配置数据库
确保 `.env` 文件中的数据库连接字符串正确：
```
DATABASE_URL=postgresql://postgres:postgres@localhost:5432/model_providers
```

#### 初始化数据库
```bash
python scripts/init_db.py
```

#### 启动后端服务
```bash
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

### 2. 前端设置

#### 安装依赖
```bash
cd frontend
npm install
```

#### 启动前端开发服务器
```bash
npm start
```

前端将在 http://localhost:3000 启动

## 功能使用

### 1. 管理界面

访问 http://localhost:3000 使用管理界面：

- **Dashboard**: 查看系统概览
- **Providers & Keys**: 管理 AI 服务提供商和 API 密钥（统一管理界面）
- **Models**: 管理模型和实现
- **Usage**: 查看 Token 使用统计

### 2. API 使用

#### OpenAI 兼容 API
```python
from openai import OpenAI

client = OpenAI(
    api_key="your_api_key",
    base_url="http://localhost:8000/v1"
)

# 聊天完成
response = client.chat.completions.create(
    model="gpt-3.5-turbo",
    messages=[{"role": "user", "content": "Hello!"}]
)
```

#### OpenAI Agents SDK
```python
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

## 管理 API

管理接口提供了以下端点：

### Providers
- `GET /api/providers` - 获取所有提供商
- `POST /api/providers` - 创建提供商
- `PUT /api/providers/{id}` - 更新提供商
- `DELETE /api/providers/{id}` - 删除提供商

### API Keys
- `GET /api/api-keys` - 获取所有 API 密钥
- `POST /api/api-keys` - 创建 API 密钥
- `PUT /api/api-keys/{id}` - 更新 API 密钥
- `DELETE /api/api-keys/{id}` - 删除 API 密钥

### Models
- `GET /api/models` - 获取所有模型
- `POST /api/models` - 创建模型
- `PUT /api/models/{id}` - 更新模型
- `DELETE /api/models/{id}` - 删除模型

### Usage
- `GET /api/usage/stats` - 获取使用统计
- `GET /api/usage` - 获取详细使用记录

## Docker 部署

如果使用 Docker 部署，需要修改 `.env` 文件：
```
DATABASE_URL=postgresql://postgres:postgres@host.docker.internal:5432/model_providers
```

然后运行：
```bash
docker build -t ai-router .
docker run --env-file .env -p 8000:8000 ai-router
```

## 故障排查

1. **数据库连接失败**
   - 确保 PostgreSQL 服务正在运行
   - 检查 `.env` 文件中的数据库连接字符串
   - 确保数据库用户有足够的权限

2. **前端无法连接后端**
   - 确保后端服务在 8000 端口运行
   - 检查前端的代理配置（vite.config.ts）

3. **初始化数据库失败**
   - 如果表已存在，可以先运行 `python scripts/drop_all_tables.py` 清理数据库
   - 确保所有依赖都已正确安装