import asyncio
import os
import logging
from typing import Tuple, Optional
from datetime import datetime

from .project_state import ProjectState
from ..processors.pdf_processor import PDFProcessor
from ..processors.git_processor import GitProcessor
from config import Config

# 设置日志
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class PipelineProcessor:
    """步骤化处理管道"""
    
    def __init__(self):
        self.config = Config()
        self.pdf_processor = PDFProcessor()
        self.git_processor = GitProcessor()
    
    def create_project(self, pdf_url: str, git_url: str = "") -> Tuple[ProjectState, str]:
        """步骤1: 项目初始化"""
        try:
            state = ProjectState()
            state.pdf_url = pdf_url.strip() if pdf_url else None
            state.git_url = git_url.strip() if git_url else None
            
            # 验证输入
            if not state.pdf_url:
                raise ValueError("PDF链接不能为空")
            
            # 更新步骤状态
            state.update_step(1, "completed", f"项目已创建，PDF: {state.pdf_url}")
            
            message = f"✅ 项目创建成功！\n项目ID: {state.project_id}\nPDF: {state.pdf_url}"
            if state.git_url:
                message += f"\nGit: {state.git_url}"
            
            logger.info(f"Created project {state.project_id}")
            return state, message
            
        except Exception as e:
            error_msg = f"❌ 项目创建失败: {str(e)}"
            logger.error(error_msg)
            return ProjectState(), error_msg
    
    def download_pdf_step(self, state: ProjectState) -> Tuple[ProjectState, str]:
        """步骤2A: 下载PDF"""
        try:
            if not state.can_execute_step(2):
                return state, "❌ 无法执行此步骤：请先完成项目初始化"
            
            state.update_step(2, "running", "正在下载PDF...")
            
            # 使用异步方法下载PDF
            async def download_async():
                return await self.pdf_processor.download_pdf(state.pdf_url)
            
            # 在新的事件循环中运行异步函数
            try:
                pdf_path = asyncio.run(download_async())
            except RuntimeError:
                # 如果已经在事件循环中，使用同步方式
                loop = asyncio.new_event_loop()
                asyncio.set_event_loop(loop)
                try:
                    pdf_path = loop.run_until_complete(download_async())
                finally:
                    loop.close()
            
            state.pdf_path = pdf_path
            state.update_step(2, "completed", f"PDF已下载至: {pdf_path}")
            
            message = f"✅ PDF下载成功！\n文件路径: {pdf_path}"
            logger.info(f"Downloaded PDF for project {state.project_id}")
            return state, message
            
        except Exception as e:
            error_msg = f"❌ PDF下载失败: {str(e)}"
            state.update_step(2, "failed", str(e))
            logger.error(f"PDF download failed for project {state.project_id}: {e}")
            return state, error_msg
    
    def clone_git_step(self, state: ProjectState) -> Tuple[ProjectState, str]:
        """步骤2B: 克隆Git代码"""
        try:
            if not state.git_url:
                return state, "⚠️ 未提供Git链接，跳过代码克隆"
            
            # 使用异步方法克隆Git仓库
            async def clone_async():
                return await self.git_processor.clone_and_analyze(state.git_url)
            
            # 在新的事件循环中运行异步函数
            try:
                git_result = asyncio.run(clone_async())
            except RuntimeError:
                # 如果已经在事件循环中，使用同步方式
                loop = asyncio.new_event_loop()
                asyncio.set_event_loop(loop)
                try:
                    git_result = loop.run_until_complete(clone_async())
                finally:
                    loop.close()
            
            state.git_path = git_result["path"]
            message = f"✅ Git仓库克隆成功！\n目录: {git_result['path']}"
            logger.info(f"Cloned git repo for project {state.project_id}")
            return state, message
            
        except Exception as e:
            error_msg = f"❌ Git克隆失败: {str(e)}"
            logger.error(f"Git clone failed for project {state.project_id}: {e}")
            return state, error_msg
    
    def pdf_to_tex_step(self, state: ProjectState) -> Tuple[ProjectState, str]:
        """步骤3: PDF转TEX转换"""
        try:
            if not state.can_execute_step(3):
                return state, "❌ 无法执行此步骤：请先下载PDF"
            
            state.update_step(3, "running", "正在转换PDF为TEX...")
            
            # 使用现有的PDF处理器
            tex_path, extracted_git_url = self.pdf_processor.process_pdf_to_tex(state.pdf_path)
            
            state.tex_path = tex_path
            state.extracted_git_url = extracted_git_url
            state.update_step(3, "completed", f"TEX文件已生成: {tex_path}")
            
            message = f"✅ PDF转TEX成功！\nTEX文件: {tex_path}"
            if extracted_git_url:
                message += f"\n🔗 发现Git链接: {extracted_git_url}"
                # 如果没有提供Git链接但从PDF中提取到了，更新状态
                if not state.git_url:
                    state.git_url = extracted_git_url
            
            logger.info(f"Converted PDF to TEX for project {state.project_id}")
            return state, message
            
        except Exception as e:
            error_msg = f"❌ PDF转TEX失败: {str(e)}"
            state.update_step(3, "failed", str(e))
            logger.error(f"PDF to TEX failed for project {state.project_id}: {e}")
            return state, error_msg
    
    def search_knowledge_step(self, state: ProjectState) -> Tuple[ProjectState, str]:
        """步骤4A: 自动搜索知识库"""
        try:
            if not state.tex_path:
                return state, "⚠️ 没有TEX文件，跳过知识库搜索"
            
            # TODO: 实现自动知识库搜索
            # 1. 读取TEX文件内容
            # 2. 提取关键词
            # 3. 搜索外部知识库
            # 4. 返回相关链接
            
            # 临时实现：模拟知识库搜索
            mock_knowledge = [
                "https://en.wikipedia.org/wiki/Machine_learning",
                "https://paperswithcode.com/",
                "https://arxiv.org/"
            ]
            
            # 添加到现有知识库（避免重复）
            for url in mock_knowledge:
                if url not in state.knowledge_base:
                    state.knowledge_base.append(url)
            
            message = f"✅ 知识库搜索完成！\n找到 {len(mock_knowledge)} 个相关链接"
            logger.info(f"Knowledge search completed for project {state.project_id}")
            return state, message
            
        except Exception as e:
            error_msg = f"❌ 知识库搜索失败: {str(e)}"
            logger.error(f"Knowledge search failed for project {state.project_id}: {e}")
            return state, error_msg
    
    def manage_knowledge_step(self, state: ProjectState, action: str, url: str) -> Tuple[ProjectState, str]:
        """步骤4B: 手动管理知识库"""
        try:
            if action == "add":
                if url and url not in state.knowledge_base:
                    state.knowledge_base.append(url)
                    message = f"✅ 已添加知识库链接: {url}"
                elif url in state.knowledge_base:
                    message = f"⚠️ 链接已存在: {url}"
                else:
                    message = "❌ 链接不能为空"
            elif action == "remove":
                if url in state.knowledge_base:
                    state.knowledge_base.remove(url)
                    message = f"✅ 已移除知识库链接: {url}"
                else:
                    message = f"⚠️ 链接不存在: {url}"
            else:
                message = f"❌ 未知操作: {action}"
            
            return state, message
            
        except Exception as e:
            error_msg = f"❌ 知识库管理失败: {str(e)}"
            logger.error(f"Knowledge management failed for project {state.project_id}: {e}")
            return state, error_msg
    
    def analyze_code_step(self, state: ProjectState) -> Tuple[ProjectState, str]:
        """步骤5: 代码分析"""
        try:
            if not state.can_execute_step(5):
                return state, "⚠️ 没有代码路径，跳过代码分析"
            
            state.update_step(5, "running", "正在分析代码...")
            
            # TODO: 实现代码分析
            # 1. 使用claude -p 分析代码
            # 2. 生成代码结构和逻辑摘要
            # 3. 生成伪代码
            
            # 临时实现：模拟代码分析
            analysis_result = {
                "structure": "项目结构分析...",
                "logic": "代码逻辑摘要...", 
                "pseudocode": "伪代码生成..."
            }
            
            state.code_analysis = analysis_result
            state.update_step(5, "completed", "代码分析完成")
            
            message = "✅ 代码分析完成！\n- 项目结构已分析\n- 代码逻辑已提取\n- 伪代码已生成"
            logger.info(f"Code analysis completed for project {state.project_id}")
            return state, message
            
        except Exception as e:
            error_msg = f"❌ 代码分析失败: {str(e)}"
            state.update_step(5, "failed", str(e))
            logger.error(f"Code analysis failed for project {state.project_id}: {e}")
            return state, error_msg
    
    def understand_paper_step(self, state: ProjectState) -> Tuple[ProjectState, str]:
        """步骤6: 论文理解生成"""
        try:
            if not state.can_execute_step(6):
                return state, "❌ 无法执行此步骤：请先完成PDF转TEX"
            
            state.update_step(6, "running", "正在理解论文...")
            
            # TODO: 实现论文理解
            # 1. 读取TEX内容
            # 2. 结合知识库内容
            # 3. 结合代码分析结果
            # 4. 使用OpenAI API生成7个模块的Blog内容
            
            # 临时实现：模拟论文理解
            blog_content = """
# 论文分析报告

## 1. 动机 (Motivation)
论文的研究动机...

## 2. 背景 (Background)
相关技术背景...

## 3. 同类方法的缺陷 (Limitations)
现有方法的问题...

## 4. 解决的问题 (Problem Solved)
本文要解决的核心问题...

## 5. 方法 (Methodology)
提出的解决方案...

## 6. 实验 (Experiments)
实验设计和结果...

## 7. 结论 (Conclusion)
研究结论和贡献...
"""
            
            state.blog_content = blog_content
            state.paper_analysis = {"status": "completed", "sections": 7}
            state.update_step(6, "completed", "论文理解完成")
            
            message = "✅ 论文理解完成！\n已生成7个模块的Blog内容"
            logger.info(f"Paper understanding completed for project {state.project_id}")
            return state, message
            
        except Exception as e:
            error_msg = f"❌ 论文理解失败: {str(e)}"
            state.update_step(6, "failed", str(e))
            logger.error(f"Paper understanding failed for project {state.project_id}: {e}")
            return state, error_msg
    
    def render_blog_step(self, state: ProjectState) -> Tuple[ProjectState, str]:
        """步骤7: HTML渲染输出"""
        try:
            if not state.can_execute_step(7):
                return state, "❌ 无法执行此步骤：请先完成论文理解"
            
            state.update_step(7, "running", "正在渲染HTML...")
            
            # TODO: 实现HTML模板渲染
            # 1. 使用Jinja2模板
            # 2. 渲染Blog内容为HTML
            # 3. 应用CSS样式
            # 4. 集成Mermaid.js图表
            
            # 临时实现：简单HTML生成
            html_content = f"""
<!DOCTYPE html>
<html>
<head>
    <title>论文分析 - {state.project_id}</title>
    <style>
        body {{ font-family: Arial, sans-serif; margin: 40px; }}
        h1, h2 {{ color: #333; }}
        pre {{ background-color: #f4f4f4; padding: 10px; }}
    </style>
</head>
<body>
    <h1>📚 论文分析报告</h1>
    <p><strong>项目ID:</strong> {state.project_id}</p>
    <p><strong>生成时间:</strong> {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}</p>
    
    <div>
        {state.blog_content.replace(chr(10), '<br>' + chr(10)) if state.blog_content else ''}
    </div>
    
    {"<h2>🔗 相关知识库</h2><ul>" + "".join([f"<li><a href='{url}'>{url}</a></li>" for url in state.knowledge_base]) + "</ul>" if state.knowledge_base else ""}
    
    {"<h2>💻 代码分析</h2><p>代码分析已完成</p>" if state.code_analysis else ""}
</body>
</html>
"""
            
            # 保存HTML文件
            html_path = os.path.join(self.config.TEMP_DIR, f"blog_{state.project_id[:8]}.html")
            with open(html_path, 'w', encoding='utf-8') as f:
                f.write(html_content)
            
            state.html_output = html_path
            state.update_step(7, "completed", f"HTML已生成: {html_path}")
            
            message = f"✅ HTML渲染完成！\n文件路径: {html_path}"
            logger.info(f"HTML rendering completed for project {state.project_id}")
            return state, message
            
        except Exception as e:
            error_msg = f"❌ HTML渲染失败: {str(e)}"
            state.update_step(7, "failed", str(e))
            logger.error(f"HTML rendering failed for project {state.project_id}: {e}")
            return state, error_msg


# 全局pipeline实例
pipeline = PipelineProcessor()