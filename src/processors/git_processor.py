import git
import os
import tempfile
import shutil
from typing import Optional, Dict
from config import config

class GitProcessor:
    def __init__(self):
        self.temp_dir = config.TEMP_DIR
        os.makedirs(self.temp_dir, exist_ok=True)
    
    async def clone_and_analyze(self, git_url: str) -> Dict:
        """克隆Git仓库并进行基础分析"""
        repo_path = None
        try:
            # 克隆仓库
            repo_path = await self._clone_repository(git_url)
            
            return {
                "path": repo_path,
            }
            
        except Exception as e:
            if repo_path and os.path.exists(repo_path):
                shutil.rmtree(repo_path, ignore_errors=True)
            raise Exception(f"Git仓库处理失败: {str(e)}")
    
    async def _clone_repository(self, git_url: str) -> str:
        """克隆Git仓库"""
        try:
            # 创建临时目录
            repo_name = git_url.split('/')[-1].replace('.git', '')
            repo_path = os.path.join(self.temp_dir, f"repo_{hash(git_url)}_{repo_name}")
            
            # 如果目录已存在，先删除
            if os.path.exists(repo_path):
                shutil.rmtree(repo_path)
            
            # 克隆仓库
            git.Repo.clone_from(git_url, repo_path, depth=1)
            
            return repo_path
            
        except Exception as e:
            raise Exception(f"仓库克隆失败: {str(e)}")
    
    def _get_directory_structure(self, repo_path: str, max_depth: int = 3) -> list:
        """获取目录结构"""
        structure = []
        
        def walk_directory(path: str, current_depth: int = 0):
            if current_depth >= max_depth:
                return
            
            try:
                items = os.listdir(path)
                for item in sorted(items):
                    if item.startswith('.'):
                        continue
                    
                    item_path = os.path.join(path, item)
                    relative_path = os.path.relpath(item_path, repo_path)
                    
                    if os.path.isdir(item_path):
                        structure.append(f"{'  ' * current_depth}📁 {item}/")
                        walk_directory(item_path, current_depth + 1)
                    else:
                        structure.append(f"{'  ' * current_depth}📄 {item}")
            except PermissionError:
                pass
        
        walk_directory(repo_path)
        return structure
    
    def cleanup_repository(self, repo_path: str):
        """清理克隆的仓库"""
        if os.path.exists(repo_path):
            shutil.rmtree(repo_path, ignore_errors=True)