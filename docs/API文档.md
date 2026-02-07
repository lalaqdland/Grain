# Grain API 文档

> 最后更新：2026-02-07  
> 当前版本：v3.1.2  
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

---

## 3. 详细接口

### 3.1 GET `/health`

响应示例：

```json
{
  "status": "healthy",
  "service": "Grain API",
  "version": "3.1.2"
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
    "marian_optional": false
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
  ]
}
```

### 3.6 POST `/api/v1/export`

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

### 3.7 GET `/api/v1/export/{doc_id}`

说明：不提交新修改，直接导出当前文档状态。  
失败时：`404` 文档不存在。

---

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

## 5. 最新验收结论（v3.1.2）

- `python -m pytest -q`：`12 passed`
- `cd frontend && npm run build`：通过
- `cd frontend && npm run e2e`：通过（1 条 Playwright 用例）
- 新覆盖：重复句场景按 selection offset 精确替换；导出请求 `modifications` 与页面文本一致；导出失败不会污染缓存文档状态

相关报告：
- `docs/status/测试报告-2026-02-07-核心闭环修复.md`
- `docs/status/测试报告-2026-02-07-offset替换与E2E.md`
- `docs/status/测试报告-2026-02-07-export原子性回归修复.md`
