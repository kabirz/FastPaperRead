import requests
import re
from typing import Optional
import os
from pdfdeal import Doc2X
from config import config

class PDFProcessor:
    def __init__(self):
        self.temp_dir = config.TEMP_DIR
        self.api_key = config.PDFDEAL_API_KEY
        self.client = Doc2X(apikey=self.api_key, debug=True, thread=5, full_speed=True)

        # 确保临时目录存在
        os.makedirs(self.temp_dir, exist_ok=True)
        
        if not self.api_key:
            raise ValueError("PDFDEAL_API_KEY 未配置，请在.env文件中添加")
    
    async def download_pdf(self, pdf_url: str, target_dir: str = None) -> str:
        """下载PDF文件到指定目录
        
        Args:
            pdf_url: PDF下载链接
            target_dir: 目标目录，如果为None则使用默认temp目录
            
        Returns:
            str: 下载的PDF文件路径
        """
        try:
            response = requests.get(pdf_url, stream=True, timeout=30)
            response.raise_for_status()
            
            # 确定保存目录
            save_dir = target_dir if target_dir else self.temp_dir
            os.makedirs(save_dir, exist_ok=True)
            
            # 保存到文件
            file_path = os.path.join(save_dir, f"paper_{hash(pdf_url)}.pdf")
            
            with open(file_path, 'wb') as f:
                for chunk in response.iter_content(chunk_size=8192):
                    f.write(chunk)
            
            return file_path
            
        except Exception as e:
            raise Exception(f"PDF下载失败: {str(e)}")
    
    def convert_pdf_to_tex_async(self, pdf_path: str) -> str:
        """同步版本的PDF转TEX"""
        '''返回zip的tex路径'''
        import pathlib
        output_path = pathlib.Path(pdf_path).parent
        print(f'output_path: {output_path}')
        success, failed, flag = self.client.pdf2file(
            pdf_file=pdf_path,
            output_path=output_path.as_posix(),
            output_format="tex",
        )
        print(success)
        print(failed)
        print(flag)
        return success[0]
    
    def extract_git_url(self, text: str) -> Optional[str]:
        """从文本中提取Git仓库链接"""
        # 常见的Git URL模式
        git_patterns = [
            r'https://github\.com/[\w\-_./]+',
            r'https://gitlab\.com/[\w\-_./]+',
            r'https://bitbucket\.org/[\w\-_./]+',
            r'git@github\.com:[\w\-_./]+\.git',
        ]
        
        for pattern in git_patterns:
            matches = re.findall(pattern, text, re.IGNORECASE)
            if matches:
                # 清理URL，移除可能的标点符号
                url = matches[0].rstrip('.,;:')
                return url
        
        return None
    
    def process_pdf_to_tex(self, pdf_path: str) -> tuple[str, Optional[str]]:
        """处理PDF文件转换为TEX，返回TEX文件路径和Git链接
        
        Args:
            pdf_path: PDF文件路径
            
        Returns:
            tuple: (tex_file_path, git_url) - TEX文件路径和Git链接（可选）
        """
        import zipfile
        import shutil
        from pathlib import Path
        
        try:
            if not os.path.exists(pdf_path):
                raise FileNotFoundError(f"PDF文件不存在: {pdf_path}")
            
            # 步骤1: 转换PDF为TEX
            zip_path = self.convert_pdf_to_tex_async(pdf_path)
            
            if not os.path.exists(zip_path):
                raise Exception(f"转换后的ZIP文件未找到: {zip_path}")
            
            # 步骤2: 解压并提取TEX内容
            extract_dir = Path(zip_path).parent / f"extracted_{Path(zip_path).stem}"
            extract_dir.mkdir(exist_ok=True)
            
            with zipfile.ZipFile(zip_path, 'r') as zip_ref:
                zip_ref.extractall(extract_dir)
            
            # 步骤3: 查找TEX文件
            tex_files = list(extract_dir.glob("*.tex"))
            if not tex_files:
                raise Exception("解压后未找到TEX文件")
            
            tex_file_path = str(tex_files[0])
            
            # 步骤4: 读取TEX内容并提取Git链接
            with open(tex_file_path, 'r', encoding='utf-8') as f:
                tex_content = f.read()
            
            git_url = self.extract_git_url(tex_content)
            
            return tex_file_path, git_url
            
        except Exception as e:
            raise Exception(f"PDF处理失败: {str(e)}")
