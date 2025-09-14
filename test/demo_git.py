"""
Git Processor 演示脚本
展示如何使用 GitProcessor 类来克隆和分析 Git 仓库
"""

import asyncio
import sys
import os

# 添加项目根目录到 Python 路径
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from src.processors.git_processor import GitProcessor
from config import config

async def demo_git_processor():
    """演示 GitProcessor 的基本用法"""
    
    # 确保必要的目录存在
    config.ensure_directories()
    
    # 创建 GitProcessor 实例
    git_processor = GitProcessor()
    
    print("🚀 Git Processor 演示")
    print("=" * 50)
    
    # 演示仓库列表（可以替换为你想测试的仓库）
    demo_repositories = [
        "git@github.com:cexll/myclaude.git",
    ]
    
    for i, repo_url in enumerate(demo_repositories, 1):
        print(f"\n📦 演示 {i}: 克隆仓库 {repo_url}")
        print("-" * 50)
        
        try:
            # 克隆并分析仓库
            result = await git_processor.clone_and_analyze(repo_url)
            repo_path = result["path"]
            
            print(f"✅ 仓库克隆成功!")
            print(f"📍 本地路径: {repo_path}")
            
            # 获取目录结构
            print(f"\n📁 目录结构 (前3层):")
            structure = git_processor._get_directory_structure(repo_path, max_depth=3)
            for line in structure[:20]:  # 只显示前20行
                print(line)
            
            if len(structure) > 20:
                print(f"... 还有 {len(structure) - 20} 个文件/目录")
            
            # 获取一些基本信息
            print(f"\n📊 基本信息:")
            total_files = len([f for f in structure if f.strip().startswith("📄")])
            total_dirs = len([f for f in structure if f.strip().startswith("📁")])
            print(f"  - 文件数量: {total_files}")
            print(f"  - 目录数量: {total_dirs}")
            
            user_input = input("\n是否清理克隆的仓库? (y/n): ").strip().lower()
            if user_input != 'y':
                print(f"📌 仓库保留在: {repo_path}")
                continue
            else:
                print(f"🧹 清理仓库...")
                git_processor.cleanup_repository(repo_path)
                print(f"✅ 清理完成")
            
        except Exception as e:
            print(f"❌ 处理失败: {e}")
        
        print("\n" + "=" * 50)
        
        # 如果是第一个仓库，询问是否继续
        if i == 1:
            user_input = input("\n继续演示下一个仓库吗? (y/n): ").strip().lower()
            if user_input != 'y':
                print("演示结束。")
                break

async def main():
    """主函数"""
    print("Git Processor 演示程序")
    print("=" * 50)
    
    await demo_git_processor()

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\n\n👋 程序被用户中断")
    except Exception as e:
        print(f"\n❌ 程序运行错误: {e}")