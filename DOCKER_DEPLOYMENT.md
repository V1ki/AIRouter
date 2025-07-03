# AI Router Docker 部署指南

## 快速开始（推荐）

使用 Docker Compose 一键部署完整的 AI Router 系统：

```bash
# 1. 克隆项目
git clone https://github.com/your-repo/ai-router.git
cd ai-router

# 2. 创建环境配置文件
cp .env.example .env

# 3. 启动服务
docker-compose up -d

# 4. 访问应用
# 管理界面: http://localhost:8000
# API 端点: http://localhost:8000/v1/
```

首次启动时会自动：
- 创建 PostgreSQL 数据库
- 初始化数据库表结构
- （可选）导入常用 AI 提供商配置

## Docker Compose 配置

默认的 `docker-compose.yml` 包含：

- **PostgreSQL 数据库**: 端口 5432
- **AI Router 应用**: 端口 8000（包含前端和后端）

### 环境变量

| 变量名 | 描述 | 默认值 |
|--------|------|--------|
| DATABASE_URL | PostgreSQL 连接字符串 | postgresql://postgres:postgres@postgres:5432/ai_router |
| INIT_COMMON_PROVIDERS | 是否初始化常用 AI 提供商 | true |

## 单独使用 Docker（不使用 Compose）

### 1. 构建镜像

```bash
docker build -t ai-router .
```

### 2. 运行 PostgreSQL

```bash
docker run -d \
  --name ai-router-db \
  -e POSTGRES_USER=postgres \
  -e POSTGRES_PASSWORD=postgres \
  -e POSTGRES_DB=ai_router \
  -p 5432:5432 \
  postgres:15-alpine
```

### 3. 运行 AI Router

```bash
docker run -d \
  --name ai-router \
  -e DATABASE_URL=postgresql://postgres:postgres@host.docker.internal:5432/ai_router \
  -e INIT_COMMON_PROVIDERS=true \
  -p 8000:8000 \
  ai-router
```

## 生产环境部署

### 1. 使用外部数据库

修改 `.env` 文件中的 `DATABASE_URL`：

```env
DATABASE_URL=postgresql://user:password@your-db-host:5432/ai_router
```

### 2. 使用 Docker Compose Override

创建 `docker-compose.override.yml`：

```yaml
version: '3.8'

services:
  ai_router:
    environment:
      DATABASE_URL: postgresql://user:password@external-db:5432/ai_router
      # 其他生产环境配置
    restart: always
```

### 3. 使用 Nginx 反向代理

```nginx
server {
    listen 80;
    server_name your-domain.com;

    location / {
        proxy_pass http://localhost:8000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }
}
```

## 数据持久化

Docker Compose 默认创建命名卷 `postgres_data` 来持久化数据库数据。

备份数据：
```bash
docker exec ai_router_db pg_dump -U postgres ai_router > backup.sql
```

恢复数据：
```bash
docker exec -i ai_router_db psql -U postgres ai_router < backup.sql
```

## 更新部署

```bash
# 1. 拉取最新代码
git pull

# 2. 重新构建并启动
docker-compose down
docker-compose up -d --build
```

## 故障排查

### 查看日志

```bash
# 查看所有服务日志
docker-compose logs

# 查看特定服务日志
docker-compose logs ai_router
docker-compose logs postgres
```

### 常见问题

1. **数据库连接失败**
   ```bash
   # 检查数据库是否运行
   docker-compose ps
   
   # 测试数据库连接
   docker exec ai_router_db pg_isready
   ```

2. **端口占用**
   ```bash
   # 修改 docker-compose.yml 中的端口映射
   ports:
     - "8080:8000"  # 改为其他端口
   ```

3. **初始化失败**
   ```bash
   # 手动初始化
   docker exec ai_router python scripts/init_db.py
   docker exec ai_router python scripts/init_common_providers.py
   ```

## 健康检查

AI Router 包含健康检查端点：

```bash
# 检查服务健康状态
curl http://localhost:8000/health

# 检查 API 可用性
curl http://localhost:8000/v1/models
```