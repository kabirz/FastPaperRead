# ReadPaper With Code

一个智能的论文阅读与代码分析系统，能够将学术论文转换为结构化的blog格式，并提供代码分析和知识库支持。

## ✨ 功能特性

- 📄 **PDF论文处理** - 支持arXiv、IEEE、ACM等平台的PDF下载和文本提取
- 🔗 **Git链接提取** - 自动从PDF中提取代码仓库链接
- 🤖 **AI驱动分析** - 使用OpenAI进行论文理解，Claude Code进行代码分析
- 📊 **结构化输出** - 生成包含7个标准模块的blog格式论文
- 🎨 **美观界面** - 响应式Web界面，支持实时进度显示
- 📚 **知识库集成** - 支持外部知识库链接补充

## 🏗️ 系统架构

```
输入论文PDF → 文本提取 → AI分析 → 代码分析 → Blog生成 → HTML输出
```

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
python main.py
```

5. **访问应用**
打开浏览器访问：`http://localhost:8000`

## 📖 使用方法

1. **输入论文信息**
   - 输入PDF链接（必需）
   - 输入Git项目链接（可选）
   - 添加知识库外链（可选）

2. **等待处理**
   - 系统会自动下载PDF
   - 提取文本内容
   - 分析代码仓库（如果有）
   - 使用AI进行深度分析

3. **查看结果**
   - 生成结构化的blog格式论文
   - 包含代码分析和伪代码
   - 支持导出HTML文件

## 🛠️ 技术栈

### 后端
- **FastAPI** - 现代化Web框架
- **OpenAI API** - 论文理解分析
- **Claude Code** - 代码分析
- **PDFDeal** - 高质量PDF转TEX转换
- **GitPython** - Git仓库操作

### 前端
- **Bootstrap 5** - UI框架
- **Jinja2** - 模板引擎
- **Mermaid.js** - 流程图生成
- **Prism.js** - 代码高亮

## 📁 项目结构

```
readpaperWithCode/
├── src/
│   ├── core/                   # 核心业务逻辑
│   │   ├── paper_processor.py  # 论文处理
│   │   ├── code_analyzer.py    # 代码分析
│   │   └── blog_generator.py   # Blog生成
│   ├── processors/             # 各种处理器
│   │   ├── pdf_processor.py    # PDF处理
│   │   └── git_processor.py    # Git处理
│   ├── templates/              # HTML模板
│   │   ├── base.html
│   │   ├── input_form.html
│   │   └── blog.html
│   ├── static/                 # 静态资源
│   │   ├── css/
│   │   └── js/
│   └── api/                    # API接口
│       └── main.py
├── config.py                   # 配置管理
├── main.py                     # 应用启动
├── requirements.txt            # 依赖管理
└── .env.example               # 环境变量模板
```

## ⚙️ 配置说明

### 环境变量

| 变量名 | 说明 | 默认值 |
|--------|------|--------|
| `OPENAI_API_KEY` | OpenAI API密钥 | 必需 |
| `PDFDEAL_API_KEY` | PDFDeal API密钥 | 必需 |
| `HOST` | 服务器地址 | `0.0.0.0` |
| `PORT` | 服务器端口 | `8000` |
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

## 🚀 未来计划

- [ ] 支持更多论文源（ResearchGate、Google Scholar等）
- [ ] 增加多语言支持
- [ ] 实现用户账户和历史记录
- [ ] 添加论文对比功能
- [ ] 支持批量处理
- [ ] 移动端适配优化