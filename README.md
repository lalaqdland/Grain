# Grain（守拙）- The AI Humanizer & Academic Shield

Grain 是一个 `.docx` 文档辅助改写工具，聚焦两件事：
- 降重（`plagiarism`）
- 降 AI 检测特征（`ai_detection`）

当前版本定位为“辅助驾驶”，支持用户按**句子/段落**选择候选并手动替换，不做整篇自动重写。

## 当前状态（2026-02-07）

- 后端：FastAPI，主端口 `8001`
- 前端：Next.js 14，主端口 `3000`
- 当前版本：`v3.1.2`
- 已修复：句子替换从“首次匹配”升级为基于 offset 的精确替换（重复句场景可控）
- 已支持：`POST /api/v1/export` 对无效段落 ID 返回 400 + `failed_ids`
- 已支持：`POST /api/v1/rewrite` 可选参数 `unit`、`option_count`
- 已支持：`GET /api/v1/upload/documents/{doc_id}` 文档详情查询
- 英文降 AI：默认 DeepSeek；可选 Marian `En -> De -> En` 噪声候选（开关控制）

详细测试与现状见：`docs/status/测试报告-2026-02-07-offset替换与E2E.md`

## 快速开始

### 1) 后端

```bash
cd backend
python -m venv venv
venv\Scripts\activate
pip install -r requirements.txt
uvicorn main:app --reload --host 0.0.0.0 --port 8001
```

环境变量在 `backend/.env`，至少需要：

```env
DEEPSEEK_API_KEY=your_key_here
```

可选 Marian：

```env
USE_MARIAN_MT=true
MARIAN_EN_DE_MODEL=Helsinki-NLP/opus-mt-en-de
MARIAN_DE_EN_MODEL=Helsinki-NLP/opus-mt-de-en
MARIAN_CACHE_DIR=../models
```

### 2) 前端

```bash
cd frontend
npm install
npm run dev
```

访问：
- 前端：`http://localhost:3000`
- 后端：`http://localhost:8001`
- Swagger：`http://localhost:8001/docs`

## 主要 API

- `POST /api/v1/upload` 上传并解析 `.docx`
- `GET /api/v1/upload/documents/{doc_id}` 获取已上传文档详情
- `POST /api/v1/rewrite` 改写文本
  - 请求字段：`text`, `mode`, `language`, 可选 `unit=sentence|paragraph`, `option_count=2|3`
  - 返回字段：`options`, 可选 `meta`（候选来源）
- `POST /api/v1/export` 导出文档
  - 请求字段：`doc_id`, `modifications`
  - 当存在无效段落 ID 时返回 `400`，包含 `failed_ids`
- `GET /api/v1/export/{doc_id}` 导出当前状态（不提交新修改）

## 目录结构（精简后）

```text
Gain-Project/
├── backend/
│   ├── app/
│   │   ├── api/v1/
│   │   ├── core/
│   │   ├── models/
│   │   ├── prompts/
│   │   └── services/
│   ├── config.py
│   └── main.py
├── frontend/
│   └── src/
│       ├── app/page.tsx
│       ├── lib/api.ts
│       ├── types/
│       └── archive/legacy/   # 旧组件链归档
├── tests/
│   ├── integration/
│   ├── unit/
│   └── scripts/              # 手工脚本
└── docs/
    ├── ops/
    ├── spec/
    └── status/
```

## 测试

```bash
python -m pytest -q
cd frontend && npm run build
cd frontend && npm run e2e
```

说明：
- `tests/integration` 和 `tests/unit` 为自动化基线
- `tests/scripts` 为手工脚本，不参与 pytest 收集
