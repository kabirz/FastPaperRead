from typing import Dict, List, Optional
import openai
from config import config

class PaperProcessor:
    def __init__(self):
        if config.OPENAI_API_KEY:
            openai.api_key = config.OPENAI_API_KEY
    
    async def analyze_paper(self, tex_content: str, knowledge_base: Optional[List[str]] = None) -> Dict:
        """使用OpenAI分析论文内容"""
        try:
            prompt = self._build_analysis_prompt(tex_content, knowledge_base)
            
            response = await openai.ChatCompletion.acreate(
                model="gpt-4",
                messages=[
                    {"role": "system", "content": "你是一个专业的学术论文分析专家"},
                    {"role": "user", "content": prompt}
                ],
                max_tokens=4000
            )
            
            return self._parse_analysis_result(response.choices[0].message.content)
            
        except Exception as e:
            return {"error": f"论文分析失败: {str(e)}"}
    
    def _build_analysis_prompt(self, tex_content: str, knowledge_base: Optional[List[str]]) -> str:
        """构建分析提示词"""
        prompt = f"""
        请分析以下论文内容，并按照以下结构输出：
        
        1. 动机 (Motivation)
        2. 背景 (Background)
        3. 同类方法的缺陷 (Limitations of Existing Methods)
        4. 解决的问题 (Problem Solved)
        5. 方法 (Methodology)
        6. 实验 (Experiments)
        7. 结论 (Conclusion)
        
        论文内容：
        {tex_content[:8000]}  # 限制长度避免token超限
        """
        
        if knowledge_base:
            prompt += f"\n\n参考知识库：\n{chr(10).join(knowledge_base[:5])}"
        
        return prompt
    
    def _parse_analysis_result(self, content: str) -> Dict:
        """解析分析结果"""
        sections = {
            "motivation": "",
            "background": "",
            "limitations": "",
            "problem": "",
            "methodology": "",
            "experiments": "",
            "conclusion": ""
        }
        
        # 简单的文本解析逻辑，后续可以优化
        lines = content.split('\n')
        current_section = None
        
        for line in lines:
            line = line.strip()
            if "动机" in line or "Motivation" in line:
                current_section = "motivation"
            elif "背景" in line or "Background" in line:
                current_section = "background"
            elif "缺陷" in line or "Limitations" in line:
                current_section = "limitations"
            elif "问题" in line or "Problem" in line:
                current_section = "problem"
            elif "方法" in line or "Methodology" in line:
                current_section = "methodology"
            elif "实验" in line or "Experiments" in line:
                current_section = "experiments"
            elif "结论" in line or "Conclusion" in line:
                current_section = "conclusion"
            elif current_section and line:
                sections[current_section] += line + "\n"
        
        return sections