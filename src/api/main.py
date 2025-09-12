from fastapi import FastAPI, HTTPException, Request
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from pydantic import BaseModel
from typing import Optional, List
import os

from ..core.paper_processor import PaperProcessor
from ..core.code_analyzer import CodeAnalyzer
from ..core.blog_generator import BlogGenerator
from ..processors.pdf_processor import PDFProcessor
from ..processors.git_processor import GitProcessor
from config import config

# 创建FastAPI应用
app = FastAPI(
    title="ReadPaper With Code",
    description="论文阅读与代码分析系统",
    version="1.0.0"
)

# 挂载静态文件
static_path = os.path.join(os.path.dirname(__file__), "..", "static")
app.mount("/static", StaticFiles(directory=static_path), name="static")

# 设置模板
templates_path = os.path.join(os.path.dirname(__file__), "..", "templates")
templates = Jinja2Templates(directory=templates_path)

# 初始化处理器
paper_processor = PaperProcessor()
code_analyzer = CodeAnalyzer()
blog_generator = BlogGenerator()
pdf_processor = PDFProcessor()
git_processor = GitProcessor()

# 请求模型
class ProcessRequest(BaseModel):
    pdf_url: str
    git_url: Optional[str] = None
    knowledge_urls: Optional[List[str]] = []

class ProcessResponse(BaseModel):
    success: bool
    blog_html: Optional[str] = None
    error: Optional[str] = None

# 路由
@app.get("/", response_class=HTMLResponse)
async def index(request: Request):
    """主页"""
    return templates.TemplateResponse("input_form.html", {"request": request})

@app.post("/process", response_model=ProcessResponse)
async def process_paper(request_data: ProcessRequest):
    """处理论文的主要API"""
    try:
        # 1. 处理PDF
        tex_content, extracted_git_url = await pdf_processor.download_and_convert(
            request_data.pdf_url
        )
        
        # 2. 确定Git URL（优先使用用户提供的，否则使用从PDF提取的）
        git_url = request_data.git_url or extracted_git_url
        
        # 3. 处理代码（如果有Git URL）
        code_analysis = None
        if git_url:
            try:
                git_info = await git_processor.clone_and_analyze(git_url)
                code_analysis = await code_analyzer.analyze_code(git_info["path"])
                # 清理克隆的仓库
                git_processor.cleanup_repository(git_info["path"])
            except Exception as e:
                print(f"代码分析失败: {e}")
        
        # 4. 处理知识库（简化实现）
        knowledge_base = []
        for url in (request_data.knowledge_urls or []):
            # TODO: 实现知识库处理
            knowledge_base.append(f"知识库: {url}")
        
        # 5. 分析论文
        paper_analysis = await paper_processor.analyze_paper(
            tex_content, 
            knowledge_base if knowledge_base else None
        )
        
        # 6. 生成Blog
        blog_html = blog_generator.generate_blog(
            paper_analysis,
            code_analysis,
            {"sources": knowledge_base}
        )
        
        return ProcessResponse(success=True, blog_html=blog_html)
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/health")
async def health_check():
    """健康检查"""
    return {"status": "healthy", "version": "1.0.0"}

# 错误处理
@app.exception_handler(404)
async def not_found_handler(request: Request, exc):
    return templates.TemplateResponse(
        "error.html", 
        {"request": request, "error": "页面未找到"}, 
        status_code=404
    )

@app.exception_handler(500)
async def server_error_handler(request: Request, exc):
    return templates.TemplateResponse(
        "error.html",
        {"request": request, "error": "服务器内部错误"},
        status_code=500
    )

if __name__ == "__main__":
    import uvicorn
    config.ensure_directories()
    uvicorn.run(
        "src.api.main:app",
        host=config.HOST,
        port=config.PORT,
        reload=config.DEBUG
    )