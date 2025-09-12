import git
import os
import tempfile
import shutil
from typing import Optional, Dict

class GitProcessor:
    def __init__(self):
        self.temp_dir = tempfile.gettempdir()
    
    async def clone_and_analyze(self, git_url: str) -> Dict:
        """克隆Git仓库并进行基础分析"""
        repo_path = None
        try:
            # 克隆仓库
            repo_path = await self._clone_repository(git_url)
            
            # 分析仓库结构
            analysis = await self._analyze_repository(repo_path)
            
            return {
                "path": repo_path,
                "structure": analysis["structure"],
                "languages": analysis["languages"],
                "main_files": analysis["main_files"],
                "readme": analysis["readme"]
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
    
    async def _analyze_repository(self, repo_path: str) -> Dict:
        """分析仓库结构"""
        analysis = {
            "structure": [],
            "languages": {},
            "main_files": [],
            "readme": ""
        }
        
        try:
            # 分析目录结构
            analysis["structure"] = self._get_directory_structure(repo_path)
            
            # 分析编程语言
            analysis["languages"] = self._detect_languages(repo_path)
            
            # 找到主要文件
            analysis["main_files"] = self._find_main_files(repo_path)
            
            # 读取README
            analysis["readme"] = self._read_readme(repo_path)
            
        except Exception as e:
            print(f"仓库分析警告: {str(e)}")
        
        return analysis
    
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
    
    def _detect_languages(self, repo_path: str) -> Dict[str, int]:
        """检测编程语言"""
        language_extensions = {
            '.py': 'Python',
            '.js': 'JavaScript', 
            '.ts': 'TypeScript',
            '.java': 'Java',
            '.cpp': 'C++',
            '.c': 'C',
            '.go': 'Go',
            '.rs': 'Rust',
            '.php': 'PHP',
            '.rb': 'Ruby'
        }
        
        language_count = {}
        
        for root, dirs, files in os.walk(repo_path):
            # 跳过隐藏目录
            dirs[:] = [d for d in dirs if not d.startswith('.')]
            
            for file in files:
                _, ext = os.path.splitext(file)
                if ext in language_extensions:
                    lang = language_extensions[ext]
                    language_count[lang] = language_count.get(lang, 0) + 1
        
        return language_count
    
    def _find_main_files(self, repo_path: str) -> list:
        """找到主要文件"""
        main_files = []
        important_files = [
            'main.py', 'app.py', 'index.js', 'main.js', 'main.go',
            'main.cpp', 'main.c', 'Main.java', 'package.json',
            'requirements.txt', 'Cargo.toml', 'pom.xml'
        ]
        
        for root, dirs, files in os.walk(repo_path):
            dirs[:] = [d for d in dirs if not d.startswith('.')]
            
            for file in files:
                if file in important_files:
                    relative_path = os.path.relpath(os.path.join(root, file), repo_path)
                    main_files.append(relative_path)
        
        return main_files
    
    def _read_readme(self, repo_path: str) -> str:
        """读取README文件"""
        readme_files = ['README.md', 'README.txt', 'README.rst', 'readme.md']
        
        for readme_file in readme_files:
            readme_path = os.path.join(repo_path, readme_file)
            if os.path.exists(readme_path):
                try:
                    with open(readme_path, 'r', encoding='utf-8') as f:
                        return f.read()[:2000]  # 限制长度
                except Exception:
                    continue
        
        return ""
    
    def cleanup_repository(self, repo_path: str):
        """清理克隆的仓库"""
        if os.path.exists(repo_path):
            shutil.rmtree(repo_path, ignore_errors=True)