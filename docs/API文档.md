# Grain API 文档

> 最后更新：2026-02-07（v3.1.4）  
> 当前版本：v3.1.4  
> 维护约定：接口变更后同步更新本文档与 `docs/status/` 测试报告。

---

## 1. 基础信息

- Base URL（本地）：`http://localhost:8001`
- API Version：`v1`
- 文档地址：`http://localhost:8001/docs`
- 认证：当前版本不需要认证

## 2. 端点总览

| 方法 | 路径 | 说明 | 状态 |
|---|---|---|---|
| GET | `/health` | 健康检查 | 已实现 |
| GET | `/api/v1/info` | API能力信息 | 已实现 |
| POST | `/api/v1/upload` | 上传并解析 `.docx` | 已实现 |
| GET | `/api/v1/upload/documents/{doc_id}` | 获取已上传文档详情 | 已实现（v3.1.2新增可用） |
| POST | `/api/v1/rewrite` | 文本改写（句子/段落） | 已实现 |
| POST | `/api/v1/export` | 导出修改后文档 | 已实现 |
| GET | `/api/v1/export/{doc_id}` | 导出当前文档状态 | 已实现 |
| GET | `/api/v1/export/stats` | 导出失败统计查询（时间窗/文档过滤） | 已实现（v3.1.3，SQLite 持久化） |
| GET | `/api/v1/export/stats/storage` | 导出统计存储体积与风险分级 | 已实现（v3.1.3） |
| GET | `/api/v1/monitoring/status` | 统一监控状态（聚合告警阈值） | 已实现（v3.1.4） |

---

## 3. 详细接口

### 3.1 GET `/health`

响应示例：

```json
{
  "status": "healthy",
  "service": "Grain API",
  "version": "3.1.3"
}
```

### 3.2 GET `/api/v1/info`

响应示例：

```json
{
  "api_version": "v1",
  "features": {
    "plagiarism_fix": true,
    "ai_detection_fix": true,
    "format_preservation": true,
    "sentence_rewrite": true,
    "marian_optional": true
  },
  "runtime": {
    "marian": {
      "enabled": true,
      "dependency_ready": true,
      "dependencies": {
        "transformers": true,
        "torch": true,
        "sentencepiece": true
      },
      "status": "enabled",
      "reason": null,
      "model_loaded": false,
      "first_load_duration_ms": null,
      "load_attempts": 0,
      "load_failures": 0,
      "generation_attempts": 0,
      "generation_failures": 0,
      "generation_failure_rate": 0.0,
      "last_generation_error": null
    }
  },
  "supported_formats": [".docx"],
  "max_file_size": "10.0MB"
}
```

### 3.3 POST `/api/v1/upload`

- Content-Type：`multipart/form-data`
- 字段：`file`（仅支持 `.docx`，最大 10MB）

响应示例：

```json
{
  "success": true,
  "message": "文档上传成功",
  "data": {
    "id": "doc_123456789abc",
    "filename": "sample.docx",
    "paragraphs": [
      {
        "id": "para_000000",
        "text": "第一段文本",
        "style": "Normal",
        "is_modified": false,
        "original_text": null
      }
    ],
    "uploaded_at": "2026-02-07T12:00:00.000000",
    "total_paragraphs": 1
  }
}
```

常见错误：
- `400`：文件格式错误
- `413`：文件超出 10MB
- `500`：文档解析失败

### 3.4 GET `/api/v1/upload/documents/{doc_id}`

说明：读取内存注册的文档详情（与上传后返回结构一致）。

成功响应示例：

```json
{
  "success": true,
  "message": "文档获取成功",
  "data": {
    "id": "doc_123456789abc",
    "filename": "sample.docx",
    "paragraphs": [],
    "uploaded_at": "2026-02-07T12:00:00.000000",
    "total_paragraphs": 0
  }
}
```

失败响应示例（`404`）：

```json
{
  "detail": "文档不存在: doc_missing"
}
```

### 3.5 POST `/api/v1/rewrite`

请求体：

```json
{
  "text": "This is one sentence.",
  "mode": "ai_detection",
  "language": "en",
  "unit": "sentence",
  "option_count": 3
}
```

参数：
- `mode`: `plagiarism | ai_detection`
- `language`: `zh | en`
- `unit`: `paragraph | sentence`（默认 `paragraph`）
- `option_count`: `2 | 3`（默认 `3`）

响应示例：

```json
{
  "success": true,
  "message": "改写成功",
  "options": ["...", "...", "..."],
  "mode": "ai_detection",
  "language": "en",
  "unit": "sentence",
  "meta": [
    { "source": "deepseek" },
    { "source": "deepseek" },
    { "source": "marian" }
  ],
  "diagnostics": {
    "marian": {
      "enabled": true,
      "eligible": true,
      "attempted": true,
      "dependency_ready": true,
      "used": true,
      "status": "used",
      "reason": null
    }
  }
}
```

`diagnostics.marian.status` 取值：
- `used`: Marian 候选已生成并被采用
- `disabled`: Marian 开关未启用
- `not_eligible`: 请求不满足 Marian 参与条件（非英文或非 `ai_detection`）
- `dependency_missing`: 启用但依赖缺失
- `generation_failed`: Marian 调用异常
- `no_effect`: Marian 结果为空或与原文一致

**降级 diagnostics（v3.1.4 新增）**：

当 DeepSeek 超时或连接错误触发降级时，`diagnostics` 额外包含：

```json
{
  "deepseek_degradation": {
    "active": true,
    "reason": "timeout_or_connection_error:...",
    "returned_fallback": true
  }
}
```

- `active`: 是否触发了降级
- `reason`: 错误原因前缀（包含具体错误信息，最多 100 字符）
- `returned_fallback`: 是否返回了降级文本（原始文本作为候选）

### 3.6 POST `/api/v1/export/stats/prune`

说明：清理过期的导出失败统计事件，释放 SQLite 存储空间。

Query 参数：
- `retention_days`：保留天数（默认 `30`，范围 `1..365`）

响应示例：

```json
{
  "retention_days": 30,
  "cutoff_epoch": 1745616000.0,
  "before_count": 1500,
  "deleted_count": 1200,
  "remaining_count": 300
}
```

行为说明：
- 删除 `event_ts_epoch < (now - retention_days)` 的记录
- 返回清理前后的记录数量
- 幂等操作：重复调用安全

### 3.7 POST `/api/v1/export`

请求体：

```json
{
  "doc_id": "doc_123456789abc",
  "modifications": {
    "para_000000": "替换后的文本"
  }
}
```

成功：返回 `.docx` 二进制流。  
失败（无效段落 ID，`400`）：

```json
{
  "detail": {
    "message": "部分段落ID不存在，导出已中止",
    "failed_ids": ["para_not_exist"],
    "applied_ids": []
  }
}
```

行为说明（v3.1.2 回归修复后）：
- 接口采用严格原子语义：本次请求只要存在任意无效段落 ID，则不会应用任何修改。
- 因此失败响应中 `detail.applied_ids` 固定为 `[]`。

### 3.8 GET `/api/v1/export/{doc_id}`

说明：不提交新修改，直接导出当前文档状态。  
失败时：`404` 文档不存在。

### 3.9 GET `/api/v1/export/stats`

说明：查询导出失败统计（SQLite 持久化，服务重启后保留）。

Query 参数：
- `window_minutes`：统计时间窗（默认 `60`，范围 `1..43200`，约30天）
- `doc_id`：可选，仅查询目标文档
- `top_n`：按失败请求数排序的文档数量（默认 `20`，范围 `1..100`）

响应示例：

```json
{
  "window_minutes": 60,
  "generated_at": "2026-02-07T12:39:33.318017+00:00",
  "filters": {
    "doc_id": "doc_da004a4f9f0b"
  },
  "summary": {
    "failed_requests": 1,
    "failed_ids": 1
  },
  "by_doc": [
    {
      "doc_id": "doc_da004a4f9f0b",
      "failed_requests": 1,
      "failed_ids": 1,
      "last_failed_at": "2026-02-07T12:39:32.376998+00:00"
    }
  ]
}
```

### 3.10 GET `/api/v1/export/stats/storage`

说明：查询导出失败统计 SQLite 的体积、事件边界和风险分级。

响应示例：

```json
{
  "generated_at": "2026-02-07T14:39:33.318017+00:00",
  "db_size_bytes": 20480,
  "event_count": 1,
  "oldest_event_at": "2026-02-07T14:39:32.376998+00:00",
  "newest_event_at": "2026-02-07T14:39:32.376998+00:00",
  "thresholds": {
    "warn_bytes": 10485760,
    "critical_bytes": 52428800
  },
  "level": "ok"
}
```

分级说明：
- `ok`：`db_size_bytes < warn_bytes`
- `warn`：`warn_bytes <= db_size_bytes < critical_bytes`
- `critical`：`db_size_bytes >= critical_bytes`

### 3.11 GET `/api/v1/monitoring/status`

说明：聚合所有健康指标，返回统一监控状态。整合 `runtime.marian` 运行态、`/export/stats` 失败率、`/export/stats/storage` 存储体积三组数据，按阈值判定健康级别。

Query 参数：
- `window_minutes`：统计时间窗（默认 `60`，范围 `1..43200`），用于导出失败计数

响应示例：

```json
{
  "generated_at": "2026-02-07T15:00:00.000000+00:00",
  "overall_level": "warn",
  "marian": {
    "level": "ok",
    "generation_failure_rate": 0.05,
    "generation_attempts": 100,
    "generation_failures": 5,
    "model_loaded": true,
    "status": "enabled",
    "thresholds": {
      "warn": 0.1,
      "critical": 0.3
    }
  },
  "export_failures": {
    "level": "warn",
    "failed_requests": 15,
    "failed_ids": 23,
    "window_minutes": 60,
    "thresholds": {
      "warn": 10,
      "critical": 30
    }
  },
  "storage": {
    "level": "ok",
    "db_size_bytes": 2048000,
    "event_count": 47
  }
}
```

告警阈值配置（`backend/config.py`）：

| 指标 | 字段 | warn | critical |
|---|---|---|---|
| Marian 生成失败率 | `marian_failure_rate_warn` / `marian_failure_rate_critical` | 10% | 30% |
| 导出失败请求数 | `export_failure_requests_warn` / `export_failure_requests_critical` | 10次 | 30次 |
| SQLite 存储体积 | `export_stats_db_warn_bytes` / `export_stats_db_critical_bytes` | 10MB | 50MB |

`overall_level` 取三项中最严重级别：`critical > warn > ok`。---

## 4. 状态码

| 状态码 | 含义 |
|---|---|
| 200 | 成功 |
| 400 | 请求参数或业务校验失败 |
| 404 | 文档不存在 |
| 413 | 上传文件过大 |
| 422 | 请求体验证失败 |
| 500 | 服务器内部错误 |

---

## 5. 最新验收结论（v3.1.3 P0/P1）

- `python -m pytest -q`：`28 passed`
- `cd frontend && npm run build`：通过
- `cd frontend && npm run e2e`：通过（1 条 Playwright 用例）
- 新覆盖：
  - `export/stats` SQLite 持久化与跨实例可见
  - `export/stats/storage` 体积分级能力（`ok/warn/critical`）
  - `window_minutes` 边界扩展到 `43200`（`43201` 返回 `422`）
  - Marian 运行态新增计数指标与失败率字段

相关报告：
- `docs/status/测试报告-2026-02-07-dev-preview-v3.1.3-p0-p1.md`
- `docs/status/测试报告-2026-02-07-v3.1.3-persistence-marian.md`
- `docs/status/测试报告-2026-02-07-核心闭环修复.md`
- `docs/status/测试报告-2026-02-07-offset替换与E2E.md`
- `docs/status/测试报告-2026-02-07-export原子性回归修复.md`
- `docs/status/测试报告-2026-02-07-dev回归与可观测性增强.md`
