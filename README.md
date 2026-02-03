# Grain（守拙）- The AI Humanizer & Academic Shield

<div align="center">

![Version](https://img.shields.io/badge/version-3.1.0-blue)
![License](https://img.shields.io/badge/license-MIT-green)
![Python](https://img.shields.io/badge/python-3.11+-blue)
![Next.js](https://img.shields.io/badge/next.js-14+-black)

**一款智能文档润色编辑器，专注于降低查重率和AI检测率，同时完美保留文档格式**

[功能特性](#功能特性) • [快速开始](#快速开始) • [技术栈](#技术栈) • [开发计划](#开发计划)

</div>

---

## 📖 项目简介

**Grain（守拙）** 是一款Web端的智能文档润色编辑器。它允许用户上传Word文档，在保留原始格式（排版、引用、图片）的前提下，通过AI针对性地降低**查重率**或**AI检测率**。

### 核心理念

- **格式神圣（Format Sanctity）**：采用XML骨架置换技术，确保修改后的文档格式分毫不差
- **外屏协同（External Sync）**：配合系统分屏，专注于极致的编辑体验
- **双模引擎（Dual Engine）**：降重与降AI两套完全不同的底层算法逻辑

---

## ✨ 功能特性

### 🔴 降重模式（Fix Plagiarism）
- 适用于知网（CNKI）、Turnitin标红的重复段落
- 通过学术化扩写、句式重构、同义词替换降低查重率
- 支持中英文双语

### 🟠 降AI模式（Fix AI Detection）
- 适用于GPTZero、Turnitin AI检测的高风险段落
- 通过熵增、口语化、短句化让文本更自然
- 中文使用DeepSeek，英文混合MarianMT回译

### 📄 格式保留
- XML骨架置换技术，确保字体、字号、行间距、图片位置完全不变
- 支持复杂文档结构（表格、引用、脚注等）

### 🎨 沉浸式编辑
- 极简单栏设计，类似Notion的纯白编辑器
- 智能光标、原位触发、流畅动画
- 绿色高亮标记已修改段落，一键撤销

---

## 🚀 快速开始

### 环境要求

- **Python**: 3.10+ （推荐3.11）
- **Node.js**: 18+ LTS （推荐20 LTS）
- **Git**: 2.40+

### 安装步骤

#### 1. 克隆项目

```bash
git clone <repository-url>
cd Gain-Project
```

#### 2. 后端设置

```bash
# 进入后端目录
cd backend

# 创建虚拟环境
python -m venv venv

# 激活虚拟环境
# Windows:
venv\Scripts\activate
# macOS/Linux:
source venv/bin/activate

# 安装依赖
pip install -r requirements.txt

# 复制环境变量文件
copy .env.example .env  # Windows
# cp .env.example .env  # macOS/Linux

# 编辑.env文件，填入你的DeepSeek API Key
# DEEPSEEK_API_KEY=your_api_key_here
```

#### 3. 前端设置

```bash
# 进入前端目录
cd ../frontend

# 安装依赖
npm install

# 环境变量已配置好，无需修改
```

### 启动项目

#### 方法一：快速启动（推荐）

**1. 启动后端服务**

打开第一个终端窗口：

```bash
cd backend
python -m uvicorn main:app --reload --host 0.0.0.0 --port 8001
```

看到以下输出表示后端启动成功：
```
INFO:     Uvicorn running on http://0.0.0.0:8001 (Press CTRL+C to quit)
INFO:     Started reloader process
INFO:     Started server process
INFO:     Application startup complete.
```

后端服务地址：`http://localhost:8001`  
API文档地址：`http://localhost:8001/docs`

**2. 启动前端服务**

打开第二个终端窗口：

```bash
cd frontend
npm run dev
```

看到以下输出表示前端启动成功：
```
▲ Next.js 14.2.35
- Local:        http://localhost:3000

✓ Ready in 3s
```

前端服务地址：`http://localhost:3000`

**3. 打开浏览器测试**

在浏览器中访问：**http://localhost:3000**

你将看到Grain的主界面，可以：
- ✅ 切换降重/降AI模式
- ✅ 拖拽上传.docx文件
- ✅ 查看文档解析结果
- ✅ 测试段落改写功能

**⚠️ 重要提示**：
- 确保后端服务运行在 **8001端口**（不是8000）
- 确保前端服务运行在 **3000端口**
- 两个服务必须同时运行才能正常使用

#### 方法二：使用Docker（可选）

```bash
# 构建并启动所有服务
docker-compose up --build

# 后台运行
docker-compose up -d

# 停止服务
docker-compose down
```

访问地址：
- 前端：http://localhost:3001
- 后端：http://localhost:8001

---

## 🧪 测试指南

### 1. 测试后端API

访问API文档：http://localhost:8001/docs

或使用测试脚本：

```bash
cd tests
python test_upload.py
```

### 2. 测试前端功能

1. 打开浏览器访问：http://localhost:3000
2. 准备一个.docx格式的Word文档（小于10MB）
3. 拖拽文件到上传区域或点击选择文件
4. 等待文档解析完成
5. 查看段落列表
6. 悬停段落查看操作按钮
7. 点击"降重"或"降AI"按钮测试改写功能

### 3. 常见问题排查

**问题1：上传文件显示"上传接口未找到"**
- 检查后端服务是否运行在8001端口
- 访问 http://localhost:8001/health 确认后端正常
- 检查前端环境变量配置

**问题2：前端无法连接后端**
- 确保后端使用 `--host 0.0.0.0 --port 8001` 启动
- 检查防火墙设置
- 查看浏览器控制台的网络请求

**问题3：文件上传失败**
- 确保文件格式为.docx
- 确保文件大小小于10MB
- 查看后端终端的错误日志

---

## 🛠️ 技术栈

### 前端
- **框架**: Next.js 14 (App Router)
- **语言**: TypeScript
- **样式**: Tailwind CSS
- **状态管理**: Zustand
- **动画**: Framer Motion
- **HTTP客户端**: Axios

### 后端
- **框架**: FastAPI
- **语言**: Python 3.11
- **Word解析**: python-docx
- **AI服务**: DeepSeek API
- **本地模型**: Transformers + MarianMT（可选）

---

## 📁 项目结构

```
Gain-Project/
├── frontend/              # Next.js前端
│   ├── src/
│   │   ├── app/          # 页面路由
│   │   ├── components/   # React组件
│   │   ├── lib/          # 工具函数
│   │   ├── hooks/        # 自定义Hooks
│   │   ├── store/        # 状态管理
│   │   └── types/        # TypeScript类型
│   └── package.json
│
├── backend/              # FastAPI后端
│   ├── app/
│   │   ├── api/         # API路由
│   │   ├── core/        # 核心业务逻辑
│   │   ├── services/    # 服务层
│   │   ├── prompts/     # Prompt库
│   │   ├── models/      # 数据模型
│   │   └── utils/       # 工具函数
│   ├── main.py          # FastAPI入口
│   ├── config.py        # 配置管理
│   └── requirements.txt
│
├── storage/             # 临时存储
│   └── temp/           # 临时文件
│
└── docs/               # 文档
    ├── 产品设计文档 (PDD)：Grain (守拙) v3.1.0.md
    ├── 开发日志.md
    ├── API文档.md
    ├── TODO.md
    ├── 下一次对话提示词.md
    └── 工作规范.md
```

---

## 📅 开发计划

### 当前版本：v3.1.0（本地MVP）

本版本专注于**本地开发部署**，完成完整的本地可运行版本。

#### 开发时间线（8周）

- **第1-2周**：项目初始化 + 后端基础
- **第3-5周**：Word解析 + 前端基础
- **第6周**：AI集成（DeepSeek + MarianMT）
- **第7周**：交互完善（悬浮菜单、动画效果）
- **第8周**：测试与优化

详细开发计划请参考：[产品设计文档](./docs/产品设计文档%20(PDD)：Grain%20(守拙)%20v3.1.0.md)

### 后续版本：v3.2.0（云端部署）

- Docker容器化
- 云端部署（Zeabur + Netlify）
- 域名配置
- 安全加固

---

## 🔧 开发命令

### 后端

```bash
# 启动开发服务器
uvicorn main:app --reload

# 运行测试
pytest

# 查看API文档
# 访问 http://localhost:8000/docs
```

### 前端

```bash
# 启动开发服务器
npm run dev

# 构建生产版本
npm run build

# 启动生产服务器
npm start

# 代码检查
npm run lint
```

---

## 📝 API文档

启动后端后，访问以下地址查看完整API文档：

- **Swagger UI**: http://localhost:8000/docs
- **ReDoc**: http://localhost:8000/redoc

### 主要端点

- `GET /health` - 健康检查
- `GET /api/v1/info` - API信息
- `POST /api/v1/upload` - 上传文档
- `POST /api/v1/rewrite` - 改写文本
- `GET /api/v1/export/{id}` - 导出文档

---

## 🤝 贡献指南

欢迎贡献代码！请遵循以下步骤：

1. Fork本项目
2. 创建特性分支 (`git checkout -b feature/AmazingFeature`)
3. 提交更改 (`git commit -m 'Add some AmazingFeature'`)
4. 推送到分支 (`git push origin feature/AmazingFeature`)
5. 开启Pull Request

---

## 📄 许可证

本项目采用 MIT 许可证。详见 [LICENSE](LICENSE) 文件。

---

## 📧 联系方式

- **项目主页**: [GitHub Repository]
- **问题反馈**: [Issues]
- **版本**: v3.1.0 (Local MVP)
- **更新日期**: 2026-02-03

---

<div align="center">

**Made with ❤️ by Matrix Agent**

⭐ 如果这个项目对你有帮助，请给个Star！

</div>

