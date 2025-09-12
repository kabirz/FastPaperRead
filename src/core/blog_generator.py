from typing import Dict, Optional
from jinja2 import Environment, FileSystemLoader
import os

class BlogGenerator:
    def __init__(self):
        # 设置Jinja2环境
        template_dir = os.path.join(os.path.dirname(__file__), '..', 'templates')
        self.env = Environment(loader=FileSystemLoader(template_dir))
    
    def generate_blog(self, 
                     paper_analysis: Dict, 
                     code_analysis: Optional[Dict] = None,
                     knowledge_base: Optional[Dict] = None) -> str:
        """生成Blog HTML"""
        
        # 准备模板数据
        template_data = {
            "sections": self._prepare_sections(paper_analysis, code_analysis),
            "has_code": code_analysis is not None,
            "knowledge_base": knowledge_base or {}
        }
        
        # 渲染模板
        template = self.env.get_template('blog.html')
        return template.render(**template_data)
    
    def _prepare_sections(self, paper_analysis: Dict, code_analysis: Optional[Dict]) -> Dict:
        """准备各个部分的内容"""
        sections = {}
        
        # 论文分析部分
        section_mapping = {
            "motivation": "动机",
            "background": "背景", 
            "limitations": "同类方法的缺陷",
            "problem": "解决的问题",
            "methodology": "方法",
            "experiments": "实验",
            "conclusion": "结论"
        }
        
        for key, title in section_mapping.items():
            content = paper_analysis.get(key, "")
            details = []
            
            # 如果有代码分析，添加到方法部分
            if key == "methodology" and code_analysis:
                details.append({
                    "type": "pseudocode",
                    "title": "算法伪代码",
                    "content": code_analysis.get("pseudocode", "")
                })
                details.append({
                    "type": "architecture",
                    "title": "系统架构",
                    "content": code_analysis.get("architecture", "")
                })
            
            sections[key] = {
                "title": title,
                "content": content,
                "details": details
            }
        
        return sections
    
    def generate_mermaid_diagram(self, diagram_type: str, data: Dict) -> str:
        """生成Mermaid流程图"""
        if diagram_type == "flowchart":
            return self._generate_flowchart(data)
        elif diagram_type == "sequence":
            return self._generate_sequence_diagram(data)
        return ""
    
    def _generate_flowchart(self, data: Dict) -> str:
        """生成流程图"""
        mermaid = "graph TD\n"
        # 简单示例
        mermaid += "    A[输入] --> B[处理]\n"
        mermaid += "    B --> C[输出]\n"
        return mermaid
    
    def _generate_sequence_diagram(self, data: Dict) -> str:
        """生成序列图"""
        mermaid = "sequenceDiagram\n"
        mermaid += "    participant A as 用户\n"
        mermaid += "    participant B as 系统\n"
        mermaid += "    A->>B: 请求\n"
        mermaid += "    B->>A: 响应\n"
        return mermaid