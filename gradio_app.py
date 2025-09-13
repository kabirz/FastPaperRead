import gradio as gr
import os
from typing import List, Tuple, Optional

from src.core.pipeline import pipeline
from src.core.project_state import ProjectState
from config import Config

# 配置
config = Config()

# 确保temp目录存在
os.makedirs(config.TEMP_DIR, exist_ok=True)


def update_ui_state(state: ProjectState) -> Tuple:
    """根据项目状态更新UI组件的可用性"""
    return (
        # 按钮可用性
        gr.update(interactive=state.can_execute_step(2)),  # download_pdf_btn
        gr.update(interactive=bool(state.git_url)),         # clone_git_btn
        gr.update(interactive=state.can_execute_step(3)),   # pdf_to_tex_btn
        gr.update(interactive=bool(state.tex_path)),        # search_knowledge_btn
        gr.update(interactive=state.can_execute_step(5)),   # analyze_code_btn
        gr.update(interactive=state.can_execute_step(6)),   # understand_paper_btn
        gr.update(interactive=state.can_execute_step(7)),   # render_blog_btn
        
        # 状态显示
        state.to_status_text(),                             # status_display
        state.get_processing_log(),                         # log_display
        "\n".join(state.knowledge_base),                    # knowledge_list
        get_result_files(state),                            # result_files
        get_html_preview(state)                             # html_preview
    )


def get_result_files(state: ProjectState) -> List[str]:
    """获取结果文件列表"""
    files = []
    if state.pdf_path and os.path.exists(state.pdf_path):
        files.append(state.pdf_path)
    if state.tex_path and os.path.exists(state.tex_path):
        files.append(state.tex_path)
    if state.html_output and os.path.exists(state.html_output):
        files.append(state.html_output)
    return files


def get_html_preview(state: ProjectState) -> str:
    """获取HTML预览内容"""
    if state.html_output and os.path.exists(state.html_output):
        try:
            with open(state.html_output, 'r', encoding='utf-8') as f:
                return f.read()
        except Exception:
            return "<p>HTML文件读取失败</p>"
    elif state.blog_content:
        # 如果有blog内容但还没有HTML，显示markdown预览
        return f"<pre>{state.blog_content}</pre>"
    else:
        return "<p>等待生成内容...</p>"


# Gradio界面回调函数
def on_create_project(pdf_url: str, git_url: str, current_state: ProjectState):
    """项目初始化回调"""
    new_state, message = pipeline.create_project(pdf_url, git_url)
    return new_state, message, *update_ui_state(new_state)


def on_download_pdf(current_state: ProjectState):
    """下载PDF回调"""
    new_state, message = pipeline.download_pdf_step(current_state)
    return new_state, message, *update_ui_state(new_state)


def on_clone_git(current_state: ProjectState):
    """克隆Git回调"""
    new_state, message = pipeline.clone_git_step(current_state)
    return new_state, message, *update_ui_state(new_state)


def on_pdf_to_tex(current_state: ProjectState):
    """PDF转TEX回调"""
    new_state, message = pipeline.pdf_to_tex_step(current_state)
    return new_state, message, *update_ui_state(new_state)


def on_search_knowledge(current_state: ProjectState):
    """搜索知识库回调"""
    new_state, message = pipeline.search_knowledge_step(current_state)
    return new_state, message, *update_ui_state(new_state)


def on_add_knowledge(url: str, current_state: ProjectState):
    """添加知识库回调"""
    new_state, message = pipeline.manage_knowledge_step(current_state, "add", url)
    return new_state, message, "", *update_ui_state(new_state)  # 清空输入框


def on_analyze_code(current_state: ProjectState):
    """代码分析回调"""
    new_state, message = pipeline.analyze_code_step(current_state)
    return new_state, message, *update_ui_state(new_state)


def on_understand_paper(current_state: ProjectState):
    """论文理解回调"""
    new_state, message = pipeline.understand_paper_step(current_state)
    return new_state, message, *update_ui_state(new_state)


def on_render_blog(current_state: ProjectState):
    """渲染Blog回调"""
    new_state, message = pipeline.render_blog_step(current_state)
    return new_state, message, *update_ui_state(new_state)


# 创建Gradio界面
with gr.Blocks(title="论文阅读与代码分析系统", theme="soft") as app:
    # 全局状态
    project_state = gr.State(ProjectState())
    
    # 页面标题
    gr.Markdown("# 📚 论文阅读与代码分析系统")
    gr.Markdown("*步骤化处理学术论文，生成结构化Blog内容*")
    
    with gr.Row():
        # 左侧：步骤控制面板
        with gr.Column(scale=1, variant="panel"):
            gr.Markdown("## 🔄 处理步骤")
            
            # 步骤1: 项目初始化
            with gr.Group():
                gr.Markdown("### 1️⃣ 项目初始化")
                pdf_url_input = gr.Textbox(
                    label="PDF链接",
                    placeholder="输入arXiv或其他PDF链接",
                    lines=1,
                    interactive=True
                )
                git_url_input = gr.Textbox(
                    label="Git链接(可选)",
                    placeholder="代码仓库链接",
                    lines=1,
                    interactive=True
                )
                init_btn = gr.Button("🚀 创建项目", variant="primary", size="lg")
            
            # 步骤2: 资源下载
            with gr.Group():
                gr.Markdown("### 2️⃣ 资源下载")
                with gr.Row():
                    download_pdf_btn = gr.Button("📄 下载PDF", interactive=False)
                    clone_git_btn = gr.Button("💻 克隆代码", interactive=False)
            
            # 步骤3: PDF转换
            with gr.Group():
                gr.Markdown("### 3️⃣ PDF转TEX")
                pdf_to_tex_btn = gr.Button("🔄 转换PDF", interactive=False)
            
            # 步骤4: 知识库管理
            with gr.Group():
                gr.Markdown("### 4️⃣ 知识库管理")
                search_knowledge_btn = gr.Button("🔍 自动搜索", interactive=False)
                with gr.Row():
                    knowledge_url_input = gr.Textbox(
                        label="知识库链接",
                        placeholder="输入相关资源链接",
                        scale=3
                    )
                    add_knowledge_btn = gr.Button("➕ 添加", scale=1)
                knowledge_list = gr.Textbox(
                    label="已添加知识库",
                    lines=4,
                    interactive=False,
                    placeholder="暂无知识库链接"
                )
            
            # 步骤5-7: 分析和生成
            with gr.Group():
                gr.Markdown("### 5️⃣ 代码分析")
                analyze_code_btn = gr.Button("🔬 分析代码", interactive=False)
            
            with gr.Group():
                gr.Markdown("### 6️⃣ 论文理解") 
                understand_paper_btn = gr.Button("📖 理解论文", interactive=False)
            
            with gr.Group():
                gr.Markdown("### 7️⃣ HTML渲染")
                render_blog_btn = gr.Button("🎨 生成Blog", interactive=False)
        
        # 右侧：结果显示面板
        with gr.Column(scale=2):
            gr.Markdown("## 📊 处理结果")
            
            # 消息显示
            message_output = gr.Textbox(
                label="操作结果",
                lines=3,
                interactive=False,
                value="等待操作..."
            )
            
            # 状态显示
            status_display = gr.Textbox(
                label="项目状态",
                lines=6,
                interactive=False,
                value="等待项目初始化..."
            )
            
            # 日志输出
            log_display = gr.Textbox(
                label="处理日志",
                lines=8,
                interactive=False,
                value="系统就绪..."
            )
            
            # 文件下载
            result_files = gr.File(
                label="生成的文件",
                file_count="multiple",
                interactive=False
            )
            
            # HTML预览
            with gr.Tab("Blog预览"):
                html_preview = gr.HTML(
                    value="<p>等待生成内容...</p>",
                    show_label=False
                )
    
    # 绑定事件处理
    init_btn.click(
        fn=on_create_project,
        inputs=[pdf_url_input, git_url_input, project_state],
        outputs=[
            project_state, message_output,
            download_pdf_btn, clone_git_btn, pdf_to_tex_btn, search_knowledge_btn,
            analyze_code_btn, understand_paper_btn, render_blog_btn,
            status_display, log_display, knowledge_list, result_files, html_preview
        ]
    )
    
    download_pdf_btn.click(
        fn=on_download_pdf,
        inputs=[project_state],
        outputs=[
            project_state, message_output,
            download_pdf_btn, clone_git_btn, pdf_to_tex_btn, search_knowledge_btn,
            analyze_code_btn, understand_paper_btn, render_blog_btn,
            status_display, log_display, knowledge_list, result_files, html_preview
        ]
    )
    
    clone_git_btn.click(
        fn=on_clone_git,
        inputs=[project_state],
        outputs=[
            project_state, message_output,
            download_pdf_btn, clone_git_btn, pdf_to_tex_btn, search_knowledge_btn,
            analyze_code_btn, understand_paper_btn, render_blog_btn,
            status_display, log_display, knowledge_list, result_files, html_preview
        ]
    )
    
    pdf_to_tex_btn.click(
        fn=on_pdf_to_tex,
        inputs=[project_state],
        outputs=[
            project_state, message_output,
            download_pdf_btn, clone_git_btn, pdf_to_tex_btn, search_knowledge_btn,
            analyze_code_btn, understand_paper_btn, render_blog_btn,
            status_display, log_display, knowledge_list, result_files, html_preview
        ]
    )
    
    search_knowledge_btn.click(
        fn=on_search_knowledge,
        inputs=[project_state],
        outputs=[
            project_state, message_output,
            download_pdf_btn, clone_git_btn, pdf_to_tex_btn, search_knowledge_btn,
            analyze_code_btn, understand_paper_btn, render_blog_btn,
            status_display, log_display, knowledge_list, result_files, html_preview
        ]
    )
    
    add_knowledge_btn.click(
        fn=on_add_knowledge,
        inputs=[knowledge_url_input, project_state],
        outputs=[
            project_state, message_output, knowledge_url_input,
            download_pdf_btn, clone_git_btn, pdf_to_tex_btn, search_knowledge_btn,
            analyze_code_btn, understand_paper_btn, render_blog_btn,
            status_display, log_display, knowledge_list, result_files, html_preview
        ]
    )
    
    analyze_code_btn.click(
        fn=on_analyze_code,
        inputs=[project_state],
        outputs=[
            project_state, message_output,
            download_pdf_btn, clone_git_btn, pdf_to_tex_btn, search_knowledge_btn,
            analyze_code_btn, understand_paper_btn, render_blog_btn,
            status_display, log_display, knowledge_list, result_files, html_preview
        ]
    )
    
    understand_paper_btn.click(
        fn=on_understand_paper,
        inputs=[project_state],
        outputs=[
            project_state, message_output,
            download_pdf_btn, clone_git_btn, pdf_to_tex_btn, search_knowledge_btn,
            analyze_code_btn, understand_paper_btn, render_blog_btn,
            status_display, log_display, knowledge_list, result_files, html_preview
        ]
    )
    
    render_blog_btn.click(
        fn=on_render_blog,
        inputs=[project_state],
        outputs=[
            project_state, message_output,
            download_pdf_btn, clone_git_btn, pdf_to_tex_btn, search_knowledge_btn,
            analyze_code_btn, understand_paper_btn, render_blog_btn,
            status_display, log_display, knowledge_list, result_files, html_preview
        ]
    )

# 启动应用
if __name__ == "__main__":
    print("🚀 启动论文阅读与代码分析系统...")
    print(f"📁 临时文件目录: {config.TEMP_DIR}")
    print("🌐 Gradio界面将在浏览器中打开...")
    
    app.launch(
        server_name="0.0.0.0",
        server_port=7860,
        share=False,
        debug=True,
        show_error=True
    )