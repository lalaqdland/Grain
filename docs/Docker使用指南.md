# Docker 使用指南（当前版）

> 最后更新：2026-02-07  
> 当前版本：v3.1.3

---

## 1. 快速启动

```bash
# 在项目根目录
cp backend/.env.example backend/.env  # 首次

docker compose up -d --build
```

访问：
- 前端：`http://localhost:3001`
- 后端：`http://localhost:8001`
- API 文档：`http://localhost:8001/docs`

说明：仓库 `docker-compose.yml` 当前映射为 `frontend:3001`、`backend:8001`。

---

## 2. 常用命令

```bash
# 启动
docker compose up -d

# 停止
docker compose down

# 查看日志
docker compose logs -f backend
docker compose logs -f frontend

# 重建
docker compose up -d --build
```

---

## 3. 关键配置

- 编排文件：`docker-compose.yml`
- 生产编排：`docker-compose.server.yml` / `docker-compose.prod.yml`（按服务器实际）
- 预览编排：`docker-compose.preview.yml`
- 后端环境变量：`backend/.env`

核心环境变量：

```env
DEEPSEEK_API_KEY=...
USE_MARIAN_MT=true
TEMP_STORAGE_PATH=/storage/temp
MODEL_CACHE_DIR=/models
EXPORT_STATS_DB_PATH=/storage/export_stats.db
```

---

## 4. 常见问题

### 4.1 端口冲突

- 后端默认映射 `8001:8000`
- 前端默认映射 `3001:3000`

若冲突，调整 `docker-compose.yml` 的 `ports`。

### 4.2 容器启动后接口不可用

按顺序检查：

1. `docker compose ps`
2. `docker compose logs --tail=200 backend`
3. `curl http://localhost:8001/health`

### 4.3 Marian 相关报错

- 当前版本默认启用 Marian（`USE_MARIAN_MT=true`）
- 若需要紧急回滚 Marian 链路，可临时设置 `USE_MARIAN_MT=false` 并重建 backend 容器

---

## 5. 与本地开发切换

本地非 Docker：

```bash
# backend
cd backend
python -m uvicorn main:app --reload --host 0.0.0.0 --port 8001

# frontend
cd frontend
npm run dev
```

Docker 模式：

```bash
docker compose up -d --build
```

---

## 6. 相关文档

- API：`docs/API文档.md`
- 状态报告：`docs/status/README.md`
- 生产部署：`docs/ops/生产部署手册.md`
