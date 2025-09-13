# ReadPaper With Code

一个基于Gradio构建的智能论文阅读与代码分析系统，提供步骤化的交互界面，能够将学术论文转换为结构化的blog格式，并提供代码分析和知识库支持。

## ✨ 功能特性

- 📄 **PDF论文处理** - 支持arXiv、IEEE、ACM等平台的PDF下载和文本提取
- 🔗 **Git链接提取** - 自动从PDF中提取代码仓库链接
- 🤖 **AI驱动分析** - 使用OpenAI进行论文理解，Claude Code进行代码分析
- 📊 **结构化输出** - 生成包含7个标准模块的blog格式论文
- 🎨 **Gradio界面** - 基于Gradio的交互式Web界面，支持步骤化处理和实时进度显示
- 📚 **知识库集成** - 支持外部知识库链接补充

## 🏗️ 系统架构

基于**Gradio步骤化处理**的交互式架构：

```
项目初始化 → 资源下载 → PDF转TEX → 知识库管理 → 代码分析 → 论文理解 → HTML渲染
```

### Gradio架构优势
- **简化开发**: 无需复杂的前后端分离，直接调用Python函数
- **自动UI生成**: Gradio自动生成界面组件和交互逻辑
- **状态管理**: 使用Gradio.State组件管理会话状态
- **步骤化处理**: 每个步骤对应一个独立的处理函数，用户可控制执行流程

### 7步处理流程
1. **项目初始化** - 输入PDF和Git链接
2. **资源下载** - 下载PDF文件和克隆代码仓库
3. **PDF转TEX** - 使用pdfdeal进行高质量转换
4. **知识库管理** - 自动搜索和手动添加知识库
5. **代码分析** - 使用Claude Code分析项目结构
6. **论文理解** - AI驱动的论文内容分析
7. **HTML渲染** - 生成美观的Blog格式输出

### 7个标准输出模块
1. **动机** (Motivation)
2. **背景** (Background)
3. **同类方法的缺陷** (Limitations of Existing Methods)
4. **解决的问题** (Problem Solved)
5. **方法** (Methodology)
6. **实验** (Experiments)
7. **结论** (Conclusion)

## 🚀 快速开始

### 环境要求
- Python 3.8+
- OpenAI API Key
- PDFDeal API Key (用于PDF转TEX)
- Claude Code (可选，用于代码分析)

### 安装步骤

1. **克隆项目**
```bash
git clone <repository-url>
cd readpaperWithCode
```

2. **安装依赖**
```bash
pip install -r requirements.txt
```

3. **配置环境变量**
```bash
# 复制环境变量模板
cp .env.example .env

# 编辑 .env 文件，添加你的配置
OPENAI_API_KEY=your_openai_api_key_here
PDFDEAL_API_KEY=your_pdfdeal_api_key_here
HOST=0.0.0.0
PORT=8000
DEBUG=true
```

**获取API密钥：**
- [OpenAI API Key](https://platform.openai.com/api-keys) - 用于论文分析
- [PDFDeal API Key](https://pdfdeal.com) - 用于PDF转TEX转换

4. **启动应用**
```bash
python gradio_app.py
```

5. **访问应用**
启动后Gradio会自动打开浏览器，或手动访问显示的本地URL（通常是 `http://127.0.0.1:7860`）

## 📱 使用方法

### 步骤化交互界面
系统采用**步骤化处理**模式，用户可以逐步执行处理流稏：

#### 步骤1：项目初始化
- 输入PDF链接（必需）
- 输入Git仓库链接（可选）
- 点击“🚀 创建项目”按钮

#### 步骤2：资源下载
- 点击“📄 下载PDF”下载论文文件
- 点击“💻 克隆代码”克隆Git仓库（如果提供）

#### 步骤3：PDF转TEX
- 点击“🔄 转换PDF”将PDF转换为TEX格式
- 系统会自动提取Git链接（如果在论文中发现）

#### 步骤4：知识库管理
- 点击“🔍 自动搜索”自动获取相关知识库
- 手动添加/删除知识库链接

#### 步骤5：代码分析
- 点击“🔬 分析代码”对代码仓库进行深度分析

#### 步骤6：论文理解
- 点击“📖 理解论文”生成AI驱动的论文分析

#### 步骤7：HTML渲染
- 点击“🎨 生成Blog”创建最终的HTML输出
- 可以在界面中直接预览或下载文件

### 特色功能
- **状态追踪**: 实时显示处理进度和结果
- **灵活执行**: 每个步骤都可以独立执行
- **错误处理**: 友好的错误提示和重试机制
- **文件管理**: 自动保存中间结果，支持文件下载

## 🛠️ 技术栈

### 核心技术
- **Python 3.8+** - 主要开发语言
- **Gradio** - 交互式Web界面框架
- **PDFDeal** - 高质量PDF转TEX转换
- **GitPython** - Git仓库操作
- **requests** - HTTP请求处理

### AI/ML集成
- **OpenAI API** - 论文理解和分析
- **Claude Code** - 代码分析和伪代码生成

### 文档处理
- **Jinja2** - HTML模板渲染
- **Mermaid.js** - 流程图生成(集成到HTML模板中)

## 📁 项目结构(Gradio版)

```
readpaperWithCode/
├── gradio_app.py               # Gradio主应用入口
├── src/
│   ├── core/                   # 核心业务逻辑
│   │   ├── __init__.py
│   │   ├── pipeline.py         # 步骤化处理管道
│   │   └── project_state.py    # 项目状态管理
│   ├── processors/             # 保留现有处理器
│   │   ├── __init__.py
│   │   ├── pdf_processor.py    # PDF处理(已实现)
│   │   ├── git_processor.py    # Git处理
│   │   ├── openai_processor.py # OpenAI分析
│   │   └── knowledge_processor.py # 知识库处理
│   ├── templates/              # HTML模板(简化)
│   │   ├── blog.html           # Blog展示模板
│   │   └── components/         # 组件模板
│   └── utils/                  # 工具函数
│       ├── __init__.py
│       ├── file_utils.py
│       └── text_utils.py
├── temp/                       # 临时文件目录
├── demo_pdf.py                 # 保留测试文件
├── requirements.txt            # Python依赖(添加gradio)
├── config.py                   # 配置文件(已存在)
├── .env.example               # 环境变量模板(已存在)
└── README.md                  # 使用说明
```

## ⚙️ 配置说明

### 环境变量

| 变量名 | 说明 | 默认值 |
|--------|------|--------|
| `OPENAI_API_KEY` | OpenAI API密钥 | 必需 |
| `PDFDEAL_API_KEY` | PDFDeal API密钥 | 必需 |
| `TEMP_DIR` | 临时文件目录 | `temp/` |
| `DEBUG` | 调试模式 | `true` |
| `CLAUDE_CODE_COMMAND` | Claude Code命令 | `claude -p` |

## 🤝 贡献指南

1. Fork 本仓库
2. 创建功能分支 (`git checkout -b feature/AmazingFeature`)
3. 提交更改 (`git commit -m 'Add some AmazingFeature'`)
4. 推送到分支 (`git push origin feature/AmazingFeature`)
5. 打开 Pull Request

## 📄 许可证

本项目采用 MIT 许可证 - 查看 [LICENSE](LICENSE) 文件了解详情

## 🐛 问题反馈

如果遇到问题或有建议，请在 [Issues](../../issues) 页面提交

## Gradio工作流程

1. **界面启动**: `python gradio_app.py` 启动Gradio界面
2. **项目初始化**: 用户输入PDF和Git链接，创建ProjectState
3. **步骤化处理**: 用户点击按钮逐步执行7个处理步骤
4. **状态管理**: Gradio.State自动管理项目状态和中间结果
5. **实时反馈**: 界面实时显示处理进度和结果
6. **文件下载**: 提供生成文件的下载链接
7. **HTML预览**: 在界面中直接预览生成的Blog内容

## 🚀 未来计划

- [ ] 支持更多论文源（ResearchGate、Google Scholar等）
- [ ] 增加多语言支持
- [ ] 实现用户账户和历史记录
- [ ] 添加论文对比功能
- [ ] 支持批量处理
- [ ] 优化Gradio界面交互体验