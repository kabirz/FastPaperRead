import uuid
from datetime import datetime
from typing import Optional, List, Dict, Any
from dataclasses import dataclass, field


@dataclass
class ProjectState:
    """Gradio项目状态数据结构"""
    
    # 基本信息
    project_id: str = field(default_factory=lambda: str(uuid.uuid4()))
    created_at: datetime = field(default_factory=datetime.now)
    
    # 输入参数
    pdf_url: Optional[str] = None
    git_url: Optional[str] = None
    
    # 处理结果文件路径
    pdf_path: Optional[str] = None
    git_path: Optional[str] = None
    tex_path: Optional[str] = None
    summary_path: Optional[str] = None
    code_analysis_path: Optional[str] = None
    knowledge_path: Optional[str] = None
    blog_path: Optional[str] = None


    extracted_git_url: Optional[str] = None
    
    # 知识库和分析结果
    knowledge_base: List[str] = field(default_factory=list)
    code_analysis: Optional[Dict[str, Any]] = None
    paper_analysis: Optional[Dict[str, Any]] = None
    blog_content: Optional[str] = None
    html_output: Optional[str] = None
    
    # 步骤状态管理
    current_step: int = 0
    step_status: Dict[int, str] = field(default_factory=dict)  # "pending", "running", "completed", "failed"
    step_messages: Dict[int, str] = field(default_factory=dict)  # 步骤执行消息
    
    def __post_init__(self):
        """初始化所有步骤状态为pending"""
        if not self.step_status:
            for i in range(1, 9):  # 8个步骤
                self.step_status[i] = "pending"
                self.step_messages[i] = ""
    
    def update_step(self, step_num: int, status: str, message: str = ""):
        """更新步骤状态和消息"""
        self.step_status[step_num] = status
        self.step_messages[step_num] = message
        if status == "completed":
            self.current_step = max(self.current_step, step_num)
    
    def to_status_text(self) -> str:
        """生成状态文本显示"""
        status_lines = [
            f"📋 项目ID: {self.project_id[:8]}...",
            f"🔄 当前步骤: {self.current_step}/8",
            f"📄 PDF: {'✅ ' + (self.pdf_path.split('/')[-1] if self.pdf_path else '') if self.pdf_path else '❌'}",
            f"💻 代码: {'✅ ' + (self.git_path.split('/')[-1] if self.git_path else '') if self.git_path else '❌'}",
            f"📝 TEX: {'✅ ' + (self.tex_path.split('/')[-1] if self.tex_path else '') if self.tex_path else '❌'}",
            f"🔍 知识库: {len(self.knowledge_base)}条",
            f"📊 代码分析: {'✅' if self.code_analysis else '❌'}",
            f"📖 论文理解: {'✅' if self.paper_analysis else '❌'}",
            f"📖 Blog生成: {'✅' if self.blog_content else '❌'}",
            f"🎨 Html渲染: {'✅' if self.html_output else '❌'}",
        ]
        return "\n".join(status_lines)
    
    def get_step_status_emoji(self, step_num: int) -> str:
        """获取步骤状态对应的emoji"""
        status = self.step_status.get(step_num, "pending")
        emoji_map = {
            "pending": "⏳",
            "running": "🔄", 
            "completed": "✅",
            "failed": "❌"
        }
        return emoji_map.get(status, "❓")
    
    def get_processing_log(self) -> str:
        """获取处理日志"""
        log_lines = [f"项目创建时间: {self.created_at.strftime('%Y-%m-%d %H:%M:%S')}"]
        
        step_names = {
            1: "项目初始化",
            2: "下载PDF", 
            3: "PDF转TEX",
            4: "知识库管理",
            5: "代码分析",
            6: "论文理解",
            7: "Blog生成",
            8: "HTML渲染"
        }
        
        for step_num in range(1, 9):
            status = self.step_status.get(step_num, "pending")
            emoji = self.get_step_status_emoji(step_num)
            name = step_names.get(step_num, f"步骤{step_num}")
            message = self.step_messages.get(step_num, "")
            
            log_lines.append(f"{emoji} {name}: {status}")
            if message:
                log_lines.append(f"   └─ {message}")
        
        return "\n".join(log_lines)
    
    def can_execute_step(self, step_num: int) -> bool:
        """检查是否可以执行指定步骤"""
        if step_num == 1:  # 项目初始化
            return True
        elif step_num == 2:  # 下载PDF - 需要项目初始化完成
            return self.step_status.get(1) == "completed" and self.pdf_url
        elif step_num == 3:  # PDF转TEX - 需要PDF下载完成  
            return self.step_status.get(2) == "completed" and self.pdf_path
        elif step_num == 4:  # 知识库管理 - 可独立执行
            return True
        elif step_num == 5:  # 代码分析 - 需要有代码路径
            return self.git_path is not None
        elif step_num == 6:  # 论文理解 - 需要TEX文件
            return self.tex_path is not None
        elif step_num == 7:  # Blog生成 - 需要论文理解完成
            return self.step_status.get(6) == "completed"
        elif step_num == 8:  # HTML渲染 - 需要论文理解完成
            return self.step_status.get(7) == "completed"
        
        return False
