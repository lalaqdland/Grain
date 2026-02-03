# Grain API 文档

> **📌 文档更新要求**：
> - ⚠️ 每次新增或修改API端点时必须更新本文档
> - 标注端点状态：[已实现/待实现/已废弃]
> - 包含完整的请求/响应示例
> - 详见：[文档结构说明.md](./文档结构说明.md) 和 [工作规范.md](./工作规范.md)

---

## 基础信息

- **Base URL**: `http://localhost:8001`
- **API Version**: v1
- **Content-Type**: `application/json`
- **当前版本**: v3.1.0 (Local MVP) ✅
- **测试状态**: 所有端点测试通过 🎉

## 认证

当前版本（v3.1.0）为本地开发版本，暂不需要认证。

---

## 端点列表

### 1. 健康检查

**端点**: `GET /health`

**状态**: ✅ 已实现 | ✅ 已测试

**描述**: 检查API服务是否正常运行

**响应示例**:
```json
{
  "status": "healthy",
  "service": "Grain API",
  "version": "3.1.0"
}
```

**测试结果**: ✅ 通过（状态码200）

---

### 2. API信息

**端点**: `GET /api/v1/info`

**状态**: ✅ 已实现 | ✅ 已测试

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
  "max_file_size": "10.0MB"
}
```

**测试结果**: ✅ 通过（状态码200）

---

### 3. 上传文档

**端点**: `POST /api/v1/upload`

**状态**: ✅ 已实现 | ✅ 已测试

**描述**: 上传Word文档进行解析

**请求**:
- Content-Type: `multipart/form-data`
- Body: 
  - `file`: .docx文件（最大10MB）

**响应示例**:
```json
{
  "success": true,
  "message": "文档上传成功",
  "data": {
    "id": "doc_988981e45a92",
    "filename": "test_document.docx",
    "paragraphs": [
      {
        "id": "para_6230deb3d335",
        "text": "测试文档",
        "style": "Title",
        "is_modified": false,
        "original_text": null
      },
      {
        "id": "para_c33732a53657",
        "text": "这是第一段测试内容。",
        "style": "Normal",
        "is_modified": false,
        "original_text": null
      }
    ],
    "uploaded_at": "2026-02-03T19:30:13.369466",
    "total_paragraphs": 6
  }
}
```

**错误响应**:

400 - 文件格式错误:
```json
{
  "detail": "❌ 仅支持 .docx 格式\n\n为了保证完美的排版格式，请在 Word 中将文件'另存为' .docx 格式后再上传"
}
```

413 - 文件过大:
```json
{
  "detail": "文件过大，最大支持10.0MB"
}
```

500 - 解析失败:
```json
{
  "detail": "文档解析失败: [错误信息]"
}
```

**测试结果**: 
- ✅ 有效文件上传：通过（状态码200）
- ✅ 无文件上传：正确返回422
- ✅ 错误格式：正确返回400
- ✅ 文档解析：6个段落正确提取

---

### 4. 改写文本

**端点**: `POST /api/v1/rewrite`

**状态**: ✅ 已实现 | ✅ 已测试

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
  "success": true,
  "message": "改写成功",
  "options": [
    "改写选项1：...",
    "改写选项2：...",
    "改写选项3：..."
  ],
  "mode": "plagiarism",
  "language": "zh"
}
```

**错误响应**:

400 - 参数错误:
```json
{
  "detail": "DeepSeek API Key未配置，请在.env文件中设置DEEPSEEK_API_KEY"
}
```

500 - 改写失败:
```json
{
  "detail": "改写失败: [错误信息]"
}
```

**测试结果**: 
- ✅ 降重模式（中文）：通过（耗时3.93秒，3个选项）
- ✅ 降AI模式（中文）：通过（耗时3.31秒，3个选项）
- ✅ 降重模式（英文）：通过（耗时2.67秒，3个选项）

---

### 5. 导出文档（GET方式）

**端点**: `GET /api/v1/export/{doc_id}`

**状态**: ✅ 已实现 | ✅ 已测试

**描述**: 导出原始文档（不带修改）

**路径参数**:
- `doc_id`: 文档ID

**响应**:
- Content-Type: `application/vnd.openxmlformats-officedocument.wordprocessingml.document`
- Body: .docx文件二进制数据

**错误响应**:

404 - 文档不存在:
```json
{
  "detail": "文档不存在: [doc_id]"
}
```

500 - 导出失败:
```json
{
  "detail": "导出失败: [错误信息]"
}
```

**测试结果**: ✅ 通过（文件大小36,885字节）

---

### 6. 导出文档（POST方式，带修改）

**端点**: `POST /api/v1/export`

**状态**: ✅ 已实现 | ✅ 已测试

**描述**: 导出修改后的Word文档

**请求体**:
```json
{
  "doc_id": "doc_988981e45a92",
  "modifications": {
    "para_6230deb3d335": "修改后的段落文本1",
    "para_c33732a53657": "修改后的段落文本2"
  }
}
```

**参数说明**:
- `doc_id`: 文档ID（必填）
- `modifications`: 段落修改映射（可选）
  - key: 段落ID
  - value: 新的段落文本

**响应**:
- Content-Type: `application/vnd.openxmlformats-officedocument.wordprocessingml.document`
- Body: .docx文件二进制数据

**错误响应**:

404 - 文档不存在:
```json
{
  "detail": "文档不存在: [doc_id]"
}
```

500 - 导出失败:
```json
{
  "detail": "导出失败: [错误信息]"
}
```

**测试结果**: ✅ 通过（完整工作流：上传-改写-导出）

---

## 测试总结

**测试日期**: 2026-02-03  
**测试版本**: v3.1.0 (Local MVP)

| 端点 | 状态 | 测试结果 |
|------|------|----------|
| GET /health | ✅ 已实现 | ✅ 通过 |
| GET /api/v1/info | ✅ 已实现 | ✅ 通过 |
| POST /api/v1/upload | ✅ 已实现 | ✅ 通过 |
| POST /api/v1/rewrite | ✅ 已实现 | ✅ 通过（3/3测试） |
| GET /api/v1/export/{doc_id} | ✅ 已实现 | ✅ 通过 |
| POST /api/v1/export | ✅ 已实现 | ✅ 通过 |

**总体通过率**: 100% 🎉

详细测试报告：[测试报告-2026-02-03.md](./测试报告-2026-02-03.md)

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

