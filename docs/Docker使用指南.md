# Docker 使用指南

## 📦 为什么使用 Docker？

✅ **依赖隔离**：避免与系统Python/Node环境冲突  
✅ **环境一致性**：开发、测试、生产环境保持一致  
✅ **易于部署**：一键启动整个项目  
✅ **团队协作**：团队成员使用相同的环境  

---

## 🚀 快速开始

### 1. 前置要求

- 安装 [Docker Desktop](https://www.docker.com/products/docker-desktop/)
- 安装 [Docker Compose](https://docs.docker.com/compose/install/)（Docker Desktop已包含）

### 2. 配置环境变量

```bash
# 复制环境变量模板
cp backend/.env.example backend/.env

# 编辑 backend/.env，填入你的API密钥
# DEEPSEEK_API_KEY=your_actual_api_key_here
```

### 3. 启动项目

```bash
# 构建并启动所有服务
docker-compose up --build

# 或者在后台运行
docker-compose up -d --build
```

### 4. 访问服务

- **前端**: http://localhost:3000
- **后端API**: http://localhost:8000
- **API文档**: http://localhost:8000/docs

---

## 🛠️ 常用命令

### 启动服务

```bash
# 启动所有服务
docker-compose up

# 后台启动
docker-compose up -d

# 重新构建并启动
docker-compose up --build
```

### 停止服务

```bash
# 停止所有服务
docker-compose down

# 停止并删除数据卷
docker-compose down -v
```

### 查看日志

```bash
# 查看所有服务日志
docker-compose logs

# 查看特定服务日志
docker-compose logs backend
docker-compose logs frontend

# 实时查看日志
docker-compose logs -f
```

### 进入容器

```bash
# 进入后端容器
docker-compose exec backend bash

# 进入前端容器
docker-compose exec frontend sh
```

### 重启服务

```bash
# 重启所有服务
docker-compose restart

# 重启特定服务
docker-compose restart backend
```

---

## 📁 项目结构

```
Gain-Project/
├── docker-compose.yml          # Docker Compose配置
├── .dockerignore              # Docker忽略文件
├── backend/
│   ├── Dockerfile             # 后端Docker配置
│   ├── requirements.txt       # Python依赖
│   └── .env                   # 环境变量（需手动创建）
├── frontend/
│   ├── Dockerfile             # 前端Docker配置
│   └── package.json           # Node依赖
└── storage/
    └── temp/                  # 临时文件存储
```

---

## 🔧 开发模式 vs 生产模式

### 当前配置（开发模式）

- ✅ 代码热重载
- ✅ 挂载本地目录
- ✅ 详细日志输出

### 生产模式配置

如需部署到生产环境，需要修改：

1. **后端 Dockerfile**：
```dockerfile
# 移除 --reload 参数
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]
```

2. **前端 Dockerfile**：
```dockerfile
# 构建生产版本
RUN npm run build
CMD ["npm", "start"]
```

3. **docker-compose.yml**：
```yaml
# 移除 volumes 挂载（生产环境不需要）
# 设置 restart: always
```

---

## 🐛 常见问题

### 1. 端口被占用

**问题**：`Error: bind: address already in use`

**解决**：
```bash
# 停止占用端口的进程
# Windows
netstat -ano | findstr :8000
taskkill /PID <PID> /F

# 或修改 docker-compose.yml 中的端口映射
ports:
  - "8001:8000"  # 使用8001端口
```

### 2. 依赖安装失败

**问题**：`pip install` 或 `npm install` 失败

**解决**：
```bash
# 清理并重新构建
docker-compose down
docker-compose build --no-cache
docker-compose up
```

### 3. 文件权限问题

**问题**：容器内无法写入文件

**解决**：
```bash
# 修改 storage 目录权限
chmod -R 777 storage/
```

### 4. 容器无法访问网络

**问题**：无法下载依赖或访问API

**解决**：
```bash
# 检查Docker网络设置
docker network ls
docker network inspect grain-network

# 重启Docker Desktop
```

---

## 📊 性能优化

### 1. 使用多阶段构建

```dockerfile
# 生产环境优化
FROM python:3.11-slim as builder
WORKDIR /app
COPY requirements.txt .
RUN pip install --user -r requirements.txt

FROM python:3.11-slim
WORKDIR /app
COPY --from=builder /root/.local /root/.local
COPY . .
ENV PATH=/root/.local/bin:$PATH
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]
```

### 2. 使用 .dockerignore

确保 `.dockerignore` 文件排除不必要的文件，减少构建上下文大小。

### 3. 缓存依赖层

先复制依赖文件，再复制代码，利用Docker层缓存。

---

## 🔄 从本地开发切换到Docker

### 当前状态（本地开发）

```bash
# 后端
cd backend
python -m uvicorn main:app --reload

# 前端
cd frontend
npm run dev
```

### 切换到Docker

```bash
# 1. 停止本地服务（Ctrl+C）

# 2. 启动Docker服务
docker-compose up --build

# 3. 访问相同的URL
# 前端: http://localhost:3000
# 后端: http://localhost:8000
```

### 优势对比

| 特性 | 本地开发 | Docker开发 |
|------|---------|-----------|
| 环境隔离 | ❌ | ✅ |
| 依赖管理 | 手动 | 自动 |
| 团队协作 | 困难 | 简单 |
| 部署一致性 | ❌ | ✅ |
| 启动速度 | 快 | 稍慢（首次） |
| 资源占用 | 低 | 中等 |

---

## 📝 最佳实践

1. **始终使用 .env 文件管理敏感信息**
2. **定期清理未使用的镜像和容器**
   ```bash
   docker system prune -a
   ```
3. **使用特定版本的基础镜像**（避免使用 `latest`）
4. **为生产环境创建单独的 docker-compose.prod.yml**
5. **使用健康检查确保服务可用**
   ```yaml
   healthcheck:
     test: ["CMD", "curl", "-f", "http://localhost:8000/health"]
     interval: 30s
     timeout: 10s
     retries: 3
   ```

---

## 🎯 下一步

- [ ] 添加数据库服务（PostgreSQL/MongoDB）
- [ ] 配置Nginx反向代理
- [ ] 添加Redis缓存
- [ ] 配置CI/CD自动部署
- [ ] 添加监控和日志收集

---

**创建时间**：2026-02-03  
**维护者**：Grain Team  
**版本**：v1.0.0

