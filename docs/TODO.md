# Grain 项目待办事项

> **📌 文档说明**：
> - 本文档记录项目的所有待办任务，按Sprint组织
> - ⚠️ 每次完成任务后必须更新状态
> - 任务状态：[ ] 待开始 | [⏳] 进行中 | [✅] 已完成 | [❌] 已取消

---

## 📊 项目总览

**当前版本**：v3.1.0 (Local MVP)  
**当前Sprint**：Sprint 1 ✅ 完成  
**下一Sprint**：Sprint 2-3（核心功能开发）  
**预计完成时间**：2026-03-28（8周）

---

## 🎯 Sprint 1：项目初始化（第1周）✅ 已完成

**时间**：2026-02-03 ~ 2026-02-07  
**状态**：✅ 已完成

- [✅] 创建项目目录结构
- [✅] 配置后端FastAPI框架
- [✅] 配置前端Next.js框架
- [✅] 创建基础API端点（/, /health, /api/v1/info）
- [✅] 创建落地页和编辑器页面框架
- [✅] 编写项目文档（README、API文档、开发日志等）
- [✅] 配置Git并连接到GitHub
- [✅] 配置环境变量

---

## 🔧 Sprint 2-3：核心功能开发（第2-5周）

**时间**：2026-02-08 ~ 2026-02-28  
**状态**：⏳ 待开始

### 后端任务（优先级P0）

#### 文件上传功能
- [✅] 创建 `app/api/v1/upload.py` 上传端点
- [✅] 实现文件格式验证（仅允许.docx）
- [✅] 实现文件大小验证（最大10MB）
- [✅] 实现临时文件存储
- [✅] 返回文档ID和基本信息

#### Word文档解析
- [✅] 创建 `app/core/docx_parser.py` 解析器
- [✅] 使用python-docx读取.docx文件
- [✅] 提取段落文本内容
- [✅] 提取段落格式信息（字体、字号、样式）
- [ ] 创建 `app/core/xml_processor.py` XML处理器
- [ ] 实现XML骨架提取
- [ ] 生成段落唯一ID索引
- [ ] 实现无损回填功能

#### 数据模型
- [✅] 创建 `app/models/document.py` 文档模型
  - [✅] DocumentUploadResponse
  - [✅] DocumentInfo
  - [✅] ParagraphInfo
- [✅] 创建 `app/models/rewrite.py` 改写模型
  - [✅] RewriteRequest
  - [✅] RewriteResponse

#### API集成
- [✅] 在main.py中注册上传路由
- [✅] 实现错误处理和异常捕获
- [ ] 添加日志记录

### 前端任务（优先级P0）

#### 文件上传组件
- [✅] 创建 `components/Upload/FileUploader.tsx`
- [✅] 使用react-dropzone实现拖拽上传
- [✅] 实现文件格式验证
- [✅] 实现文件大小验证
- [✅] 显示上传进度
- [✅] 显示错误提示

#### 文档展示
- [✅] 创建 `components/Editor/Editor.tsx` 编辑器组件
- [✅] 创建 `components/Editor/Paragraph.tsx` 段落组件
- [✅] 渲染文档段落列表
- [✅] 实现段落悬停效果
- [✅] 实现段落左侧指示条

#### 状态管理
- [✅] 创建 `store/editorStore.ts` Zustand store
- [✅] 管理文档状态（document, paragraphs）
- [✅] 管理加载状态（isLoading）
- [✅] 管理段落修改历史

#### 页面集成
- [✅] 更新 `app/editor/page.tsx`
- [✅] 集成FileUploader组件
- [✅] 集成Editor组件
- [✅] 实现上传成功后的文档展示
- [✅] 添加错误处理和用户提示

### 测试任务
- [ ] 编写后端单元测试（docx_parser）
- [ ] 编写API端点测试（upload）
- [ ] 前后端联调测试
- [ ] 测试格式保留功能（10个测试用例）

---

## 🤖 Sprint 4：AI集成（第6周）

**时间**：2026-03-01 ~ 2026-03-08  
**状态**：⏳ 待开始

### DeepSeek API集成
- [ ] 创建 `app/services/deepseek.py` DeepSeek服务
- [ ] 封装OpenAI SDK调用
- [ ] 实现API错误处理和重试机制
- [ ] 实现速率限制处理

### Prompt开发
- [ ] 创建 `app/prompts/plagiarism_fix.py` 降重Prompt
  - [ ] 中文降重Prompt
  - [ ] 英文降重Prompt
- [ ] 创建 `app/prompts/humanizer.py` 降AI Prompt
  - [ ] 中文降AI Prompt
  - [ ] 英文降AI Prompt

### MarianMT集成（可选）
- [ ] 创建 `app/services/marian.py` MarianMT服务
- [ ] 下载并加载模型（Helsinki-NLP/opus-mt-en-de）
- [ ] 实现En->De->En回译
- [ ] 优化推理性能

### 改写API
- [ ] 创建 `app/api/v1/rewrite.py` 改写端点
- [ ] 实现语言检测
- [ ] 实现模式选择（降重/降AI）
- [ ] 生成3个改写选项
- [ ] 实现异步处理

### 前端集成
- [ ] 创建 `hooks/useRewrite.ts` 改写Hook
- [ ] 实现改写API调用
- [ ] 实现异步状态管理

---

## 🎨 Sprint 5：交互完善（第7周）

**时间**：2026-03-10 ~ 2026-03-18  
**状态**：⏳ 待开始

### 悬浮菜单
- [ ] 创建 `components/Editor/FloatingMenu.tsx`
- [ ] 实现点击段落弹出菜单
- [ ] 显示"降重"和"降AI"选项
- [ ] 实现菜单定位和动画

### 结果气泡
- [ ] 创建 `components/Editor/ResultBubble.tsx`
- [ ] 显示3个改写选项
- [ ] 实现选项点击替换原文
- [ ] 实现气泡展开/收起动画

### 加载动画
- [ ] 创建 `components/UI/Loading.tsx`
- [ ] 实现波浪形呼吸线动画
- [ ] 在段落下方显示Loading状态

### 高亮和撤销
- [ ] 创建 `components/Editor/UndoButton.tsx`
- [ ] 实现已修改段落的绿色高亮
- [ ] 实现一键撤销功能
- [ ] 存储原文快照
- [ ] 实现悬停显示原文

### 导出功能
- [ ] 创建 `app/api/v1/export.py` 导出端点
- [ ] 实现修改后的文档回填
- [ ] 生成.docx文件
- [ ] 实现文件下载

---

## ✅ Sprint 6：测试与优化（第8周）

**时间**：2026-03-20 ~ 2026-03-28  
**状态**：⏳ 待开始

### 功能测试
- [ ] 编写完整的测试用例
- [ ] 测试文件上传流程
- [ ] 测试文档解析功能
- [ ] 测试改写功能（降重/降AI）
- [ ] 测试格式保留功能
- [ ] 测试导出功能

### Bug修复
- [ ] 修复已知Bug
- [ ] 处理边界情况
- [ ] 优化错误提示

### 性能优化
- [ ] 优化首屏加载速度（<3秒）
- [ ] 优化大文件处理
- [ ] 优化API响应时间
- [ ] 实现代码分割和懒加载

### 响应式适配
- [ ] 适配移动端布局
- [ ] 适配平板布局
- [ ] 测试不同屏幕尺寸

### 文档完善
- [ ] 更新README.md
- [ ] 完善API文档
- [ ] 编写用户使用指南
- [ ] 编写部署文档

### 验收
- [ ] 产品负责人验收
- [ ] 功能演示
- [ ] 签字确认

---

## 🚀 Sprint 7：云端部署（v3.2.0）

**时间**：2026-03-29 ~ 2026-04-12  
**状态**：⏳ 待开始（后续版本）

### Docker容器化
- [ ] 编写Dockerfile（后端）
- [ ] 编写Dockerfile（前端）
- [ ] 编写docker-compose.yml
- [ ] 本地测试容器

### 后端部署
- [ ] 部署到Zeabur
- [ ] 配置环境变量
- [ ] 配置数据库（如需要）
- [ ] 测试公网API

### 前端部署
- [ ] 部署到Netlify
- [ ] 配置环境变量
- [ ] 配置API地址
- [ ] 测试公网站点

### 域名和安全
- [ ] 配置自定义域名
- [ ] 配置HTTPS
- [ ] 配置CORS策略
- [ ] 实现Rate Limit
- [ ] 实现API认证（如需要）

---

## 📝 任务优先级说明

- **P0**：必须完成，阻塞后续开发
- **P1**：重要但可延后
- **P2**：可选功能，时间允许时完成

---

## 🔄 任务更新规范

每次完成任务时：
1. 将任务状态从 `[ ]` 改为 `[✅]`
2. 在 `docs/开发日志.md` 中记录完成情况
3. 如有API变更，更新 `docs/API文档.md`
4. 更新 `docs/下一次对话提示词.md`

---

**创建时间**：2026-02-03  
**最后更新**：2026-02-03  
**维护者**：开发团队

