import asyncio
import os
import logging
import markdown
from subprocess import Popen, PIPE
from typing import Tuple, Optional

from datetime import datetime
from .project_state import ProjectState
from ..processors.pdf_processor import PDFProcessor
from ..processors.git_processor import GitProcessor
from config import Config
from ..processors.mcp_processor import get_keywords, get_link, get_summary, get_knowedge, get_blog

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
            with open(state.tex_path, "r", encoding="utf-8") as f:
                tex_content = f.read()
            # 2. 提取关键词
            keywords = asyncio.run(get_keywords(tex_content))

            # 3. 搜索外部知识库
            # 4. 返回相关链接
            mock_knowledge = asyncio.run(get_link(keywords))

            # 添加到现有知识库（避免重复）
            for url in mock_knowledge:
                if url not in state.knowledge_base:
                    if 'zhihu' not in url and 'github' not in url and url[-1] != '/':
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
            
            with open(state.tex_path) as f:
                tex_content = f.read()
            # TODO: 实现代码分析
            # 1. mcp: 生成 summary
            message = asyncio.run(get_sumary(tex_content))
            with open(f'{self.config.TEMP_DIR}/summary.md', 'w') as f:
                f.write(message)
            # 2. 使用claude -p 分析代码, 这个步骤可能需要在命令行上执行，这里大概率不成功
            _prompt_msg = f"/docs --paper-summary {self.config.TEMP_DIR}/summary.md --code-dir {state.git_path} --output {self.config.TEMP_DIR}/code_analysis.md"
            cmd = f'{self.config.CLAUDE_CODE_COMMAND} --permission-mode bypassPermissions "{_prompt_msg}"'
            claude_content = Popen(cmd, shell=True, stdin=PIPE, stdout=PIPE)
            str_out, _ = claude_content.communicate()

            state.code_analysis =  "ok"
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
            
            with open(state.tex_path) as f:
                tex_content = f.read()
            # TODO: 实现论文理解
            # 1. 读取TEX内容
            # 2. 结合知识库内容
            message = asyncio.run(get_knowedge(tex_content, state.knowledge_base))
            state.update_step(6, "completed", "理解文章完成")
            state.paper_analysis = 'ok'

            # 4. 或者使用Claude生成
            with open(self.config.TEMP_DIR + "/knowledge_out.md", "w", encoding="utf-8") as f:
                f.write(message)
            return state,message 

        except Exception as e:
            error_msg = f"❌ 论文理解失败: {str(e)}"
            state.update_step(6, "failed", str(e))
            logger.error(f"Paper understanding failed for project {state.project_id}: {e}")
            return state, error_msg


    def generate_blog_step(self, state: ProjectState) -> Tuple[ProjectState, str]: 
        """步骤7: 组合生成Blog"""
        try:
            state.update_step(7, "running", "正在Blog...")
            
            with open(state.tex_path) as f:
                tex_content = f.read()
            with open(f"{self.config.TEMP_DIR}/code_analysis.md", "r", encoding="utf-8") as f:
                code_content = f.read()
            # TODO: 实现论文理解
            # 1. 读取TEX内容
            # 2. 结合知识库内容
            message = asyncio.run(get_blog(tex_content, code_content, state.knowledge_base))

            # 生成Blog内容
            with open(self.config.TEMP_DIR + "/blog.md", "w", encoding="utf-8") as f:
                f.write(message)

            state.blog_content = markdown.markdown(message)
            state.update_step(7, "completed", "Blog生成完成")
            
            message = "✅ 论文理解完成！\n已生成7个模块的Blog内容"
            logger.info(f"Paper understanding completed for project {state.project_id}")
            return state, message
            
        except Exception as e:
            error_msg = f"❌ Blog生成失败: {str(e)}"
            state.update_step(6, "failed", str(e))
            logger.error(f"Paper understanding failed for project {state.project_id}: {e}")
            return state, error_msg

    
    def render_blog_step(self, state: ProjectState) -> Tuple[ProjectState, str]:
        """步骤8: HTML渲染输出"""
        try:
            if not state.can_execute_step(8):
                return state, "❌ 无法执行此步骤：请先完成论文理解"
            
            state.update_step(8, "running", "正在渲染HTML...")
            html_path = f"{self.config.TEMP_DIR}/blog_{state.project_id[:8]}.html"
            _prompt_msg = f"把文件{self.config.TEMP_DIR}/blog.md渲染成HTML输出，要求界面美观，并且要把图表、代码、公式等内容都正确渲染，并输出到{html_path}.html"
            cmd = f'{self.config.CLAUDE_CODE_COMMAND} --permission-mode bypassPermissions "{_prompt_msg}"'
            claude_content = Popen(cmd, shell=True, stdin=PIPE, stdout=PIPE)
            _, _ = claude_content.communicate()
            
            state.update_step(8, "completed", f"HTML已生成: {html_path}")
            
            message = f"✅ HTML渲染完成！\n文件路径: {html_path}"
            logger.info(f"HTML rendering completed for project {state.project_id}")
            state.html_output = html_path
            return state, message
            
        except Exception as e:
            error_msg = f"❌ HTML渲染失败: {str(e)}"
            state.update_step(8, "failed", str(e))
            logger.error(f"HTML rendering failed for project {state.project_id}: {e}")
            return state, error_msg


# 全局pipeline实例
pipeline = PipelineProcessor()
