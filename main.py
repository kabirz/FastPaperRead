import uvicorn
from config import config

if __name__ == "__main__":
    # 确保必要目录存在
    config.ensure_directories()
    
    # 启动应用
    uvicorn.run(
        "src.api.main:app",
        host=config.HOST,
        port=config.PORT,
        reload=config.DEBUG
    )
