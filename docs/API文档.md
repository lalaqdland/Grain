# Grain API 文档

> **📌 文档更新要求**：
> - ⚠️ 每次新增或修改API端点时必须更新本文档
> - 标注端点状态：[已实现/待实现/已废弃]
> - 包含完整的请求/响应示例
> - 详见：[文档结构说明.md](./文档结构说明.md) 和 [工作规范.md](./工作规范.md)

---

## 基础信息

- **Base URL**: `http://localhost:8000`
- **API Version**: v1
- **Content-Type**: `application/json`

## 认证

当前版本（v3.1.0）为本地开发版本，暂不需要认证。

---

## 端点列表

### 1. 健康检查

**端点**: `GET /health`

**状态**: ✅ 已实现

**描述**: 检查API服务是否正常运行

**响应示例**:
```json
{
  "status": "healthy",
  "service": "Grain API",
  "version": "3.1.0"
}
```

---

### 2. API信息

**端点**: `GET /api/v1/info`

**状态**: ✅ 已实现

**描述**: 获取API功能和配置信息

**响应示例**:
```json
{
  "api_version": "v1",
  "features": {
    "plagiarism_fix": true,
    "ai_detection_fix": true,
    "format_preservation": true
  },
  "supported_formats": [".docx"],
  "max_file_size": "10MB"
}
```

---

### 3. 上传文档

**端点**: `POST /api/v1/upload`

**状态**: ⏳ 待实现

**描述**: 上传Word文档进行解析

**请求**:
- Content-Type: `multipart/form-data`
- Body: 
  - `file`: .docx文件（最大10MB）

**响应示例**:
```json
{
  "document_id": "doc_123456",
  "filename": "example.docx",
  "paragraphs": [
    {
      "id": "para_1",
      "text": "这是第一段内容",
      "style": "Normal"
    }
  ],
  "uploaded_at": "2026-02-03T16:00:00Z"
}
```

**错误响应**:
```json
{
  "detail": "File format not supported. Only .docx files are allowed."
}
```

---

### 4. 改写文本

**端点**: `POST /api/v1/rewrite`

**状态**: ⏳ 待实现

**描述**: 使用AI改写文本（降重或降AI）

**请求体**:
```json
{
  "text": "需要改写的文本内容",
  "mode": "plagiarism",  // 或 "ai_detection"
  "language": "zh"       // 或 "en"
}
```

**参数说明**:
- `text`: 需要改写的文本（必填）
- `mode`: 改写模式（必填）
  - `plagiarism`: 降重模式
  - `ai_detection`: 降AI模式
- `language`: 文本语言（必填）
  - `zh`: 中文
  - `en`: 英文

**响应示例**:
```json
{
  "options": [
    "改写选项1：...",
    "改写选项2：...",
    "改写选项3：..."
  ],
  "mode": "plagiarism",
  "language": "zh"
}
```

---

### 5. 导出文档

**端点**: `GET /api/v1/export/{document_id}`

**状态**: ⏳ 待实现

**描述**: 导出修改后的Word文档

**路径参数**:
- `document_id`: 文档ID

**响应**:
- Content-Type: `application/vnd.openxmlformats-officedocument.wordprocessingml.document`
- Body: .docx文件二进制数据

---

## 错误代码

| 状态码 | 说明 |
|--------|------|
| 200 | 请求成功 |
| 400 | 请求参数错误 |
| 404 | 资源不存在 |
| 413 | 文件过大 |
| 422 | 请求验证失败 |
| 500 | 服务器内部错误 |

---

## 使用示例

### Python

```python
import requests

# 健康检查
response = requests.get('http://localhost:8000/health')
print(response.json())

# 上传文档
with open('document.docx', 'rb') as f:
    files = {'file': f}
    response = requests.post('http://localhost:8000/api/v1/upload', files=files)
    print(response.json())

# 改写文本
data = {
    'text': '这是需要改写的文本',
    'mode': 'plagiarism',
    'language': 'zh'
}
response = requests.post('http://localhost:8000/api/v1/rewrite', json=data)
print(response.json())
```

### JavaScript (Axios)

```javascript
import axios from 'axios'

// 健康检查
const health = await axios.get('http://localhost:8000/health')
console.log(health.data)

// 上传文档
const formData = new FormData()
formData.append('file', file)
const upload = await axios.post('http://localhost:8000/api/v1/upload', formData)
console.log(upload.data)

// 改写文本
const rewrite = await axios.post('http://localhost:8000/api/v1/rewrite', {
  text: '这是需要改写的文本',
  mode: 'plagiarism',
  language: 'zh'
})
console.log(rewrite.data)
```

---

**文档版本**: v3.1.0  
**最后更新**: 2026-02-03  
**在线文档**: http://localhost:8000/docs

