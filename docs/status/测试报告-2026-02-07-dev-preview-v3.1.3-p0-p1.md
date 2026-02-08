# 测试报告（dev 预览 v3.1.3 P0/P1）

- 日期：2026-02-07
- 分支：`dev`
- 环境范围：仅 `/opt/gain-preview`（未触碰 `/opt/gain-project`）

## 1. P0 部署与验收

### 1.1 部署前基线

- `GET /api/health`：`version=3.1.2`
- `GET /api/v1/info`：`runtime.marian.enabled=false`

### 1.2 部署动作

```bash
ssh capoo-hk "cd /opt/gain-preview && sed -i 's/^USE_MARIAN_MT=.*/USE_MARIAN_MT=true/' backend/.env"
mutagen sync flush code
ssh capoo-hk "cd /opt/gain-preview && docker compose -f docker-compose.preview.yml up -d --build --force-recreate"
```

### 1.3 部署后结果

- `GET /api/health`：`version=3.1.3`
- `GET /api/v1/info`：`runtime.marian.enabled=true` 且依赖就绪
- `docker inspect grain-preview-backend`：`USE_MARIAN_MT=true`

### 1.4 业务闭环与持久化

- 上传：`POST /api/v1/upload` -> `200`
- 改写：`POST /api/v1/rewrite` -> `200`（`option_count=2`）
- 无效导出：`POST /api/v1/export` -> `400 + failed_ids`
- 统计：`GET /api/v1/export/stats?window_minutes=60` -> `failed_requests=1`
- 重启 backend 后复查统计：`failed_requests=1`（未丢失）
- 文件检查：`/opt/gain-preview/storage/export_stats.db` 存在（约 `20K`）

## 2. P1 代码能力验收

### 2.1 新增能力

- `GET /api/v1/export/stats/storage`：输出 SQLite 体积、事件数、阈值、分级
- compose 显式环境变量：
  - `EXPORT_STATS_DB_WARN_BYTES=10485760`
  - `EXPORT_STATS_DB_CRITICAL_BYTES=52428800`
- `GET /api/v1/info` 的 `runtime.marian` 新增字段：
  - `model_loaded`
  - `first_load_duration_ms`
  - `load_attempts`
  - `load_failures`
  - `generation_attempts`
  - `generation_failures`
  - `generation_failure_rate`
  - `last_generation_error`
- `backend/.dockerignore` 排除 `.env`（镜像加固）

### 2.2 自动化测试

```bash
python -m pytest -q
cd frontend && npm run build
cd frontend && npm run e2e
```

结果：

- `pytest`：`28 passed`
- `frontend build`：通过
- `frontend e2e`：`1 passed`

## 3. 结论

- ✅ P0 完成：dev 预览已升级并通过闭环与持久化验收。
- ✅ P1 完成：监控接口与运行态指标落地，测试通过。
- ✅ 全程仅操作预览目录，生产环境未改动。
