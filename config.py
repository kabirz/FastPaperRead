import os
from typing import Optional
from dotenv import load_dotenv

# 加载环境变量
load_dotenv(encoding="utf-8")

class Config:
    # API配置
    OPENAI_API_KEY: Optional[str] = os.getenv("OPENAI_API_KEY")
    PDFDEAL_API_KEY: Optional[str] = os.getenv("PDFDEAL_API_KEY")
    
    # 应用配置
    HOST: str = os.getenv("HOST", "0.0.0.0")
    PORT: int = int(os.getenv("PORT", "8000"))
    DEBUG: bool = os.getenv("DEBUG", "true").lower() == "true"
    
    # 文件配置
    UPLOAD_DIR: str = os.getenv("UPLOAD_DIR", "uploads")
    OUTPUT_DIR: str = os.getenv("OUTPUT_DIR", "output")
    TEMP_DIR: str = os.getenv("TEMP_DIR", "temp")
    
    # Claude Code 配置
    CLAUDE_CODE_COMMAND: str = os.getenv("CLAUDE_CODE_COMMAND", "claude -p")
    
    @classmethod
    def ensure_directories(cls):
        """确保必要的目录存在"""
        for dir_path in [cls.UPLOAD_DIR, cls.OUTPUT_DIR, cls.TEMP_DIR]:
            os.makedirs(dir_path, exist_ok=True)

config = Config()