import subprocess
import asyncio
from typing import Dict, Optional
from config import config

class CodeAnalyzer:
    def __init__(self):
        self.claude_command = config.CLAUDE_CODE_COMMAND
    
    async def analyze_code(self, repo_path: str) -> Dict:
        """使用Claude Code分析代码"""
        try:
            # 构建Claude Code分析命令
            analysis_prompt = self._build_code_analysis_prompt()
            
            # 使用claude -p分析代码
            result = await self._run_claude_analysis(repo_path, analysis_prompt)
            
            return {
                "pseudocode": result.get("pseudocode", ""),
                "architecture": result.get("architecture", ""),
                "key_functions": result.get("key_functions", []),
                "dependencies": result.get("dependencies", [])
            }
            
        except Exception as e:
            return {"error": f"代码分析失败: {str(e)}"}
    
    def _build_code_analysis_prompt(self) -> str:
        """构建代码分析提示词"""
        return """
        请分析这个代码仓库，并提供以下信息：
        1. 主要架构和模块结构
        2. 核心算法的伪代码
        3. 关键函数和类的说明
        4. 主要依赖和技术栈
        
        请以结构化的方式输出结果。
        """
    
    async def _run_claude_analysis(self, repo_path: str, prompt: str) -> Dict:
        """运行Claude Code分析"""
        try:
            # 切换到代码目录并运行claude -p
            cmd = f'cd "{repo_path}" && {self.claude_command} "{prompt}"'
            
            process = await asyncio.create_subprocess_shell(
                cmd,
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE
            )
            
            stdout, stderr = await process.communicate()
            
            if process.returncode == 0:
                return self._parse_claude_output(stdout.decode())
            else:
                raise Exception(f"Claude分析失败: {stderr.decode()}")
                
        except Exception as e:
            # 如果Claude Code不可用，返回基础分析
            return await self._fallback_analysis(repo_path)
    
    def _parse_claude_output(self, output: str) -> Dict:
        """解析Claude输出"""
        # 简单解析，后续可以优化
        return {
            "pseudocode": output,
            "architecture": "Claude分析结果",
            "key_functions": [],
            "dependencies": []
        }
    
    async def _fallback_analysis(self, repo_path: str) -> Dict:
        """备用分析方法"""
        return {
            "pseudocode": "代码分析功能需要Claude Code支持",
            "architecture": "请安装Claude Code进行详细分析",
            "key_functions": [],
            "dependencies": []
        }