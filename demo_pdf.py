#!/usr/bin/env python3
"""
PDF处理演示脚本
实际下载和转换PDF文件进行测试
"""

import asyncio
import os
import sys
from pathlib import Path

# 添加项目根目录到Python路径
sys.path.insert(0, str(Path(__file__).parent))

from src.processors.pdf_processor import PDFProcessor
from config import config

# 测试用的PDF URL（写死在代码中）
TEST_URLS = {
    "attention": {
        "url": "https://arxiv.org/pdf/1706.03762.pdf",
        "name": "Attention Is All You Need",
        "description": "Google的Transformer论文，应该包含GitHub链接"
    },
    
    "resnet": {
        "url": "https://arxiv.org/pdf/1512.03385.pdf", 
        "name": "ResNet论文",
        "description": "微软的ResNet论文"
    }
}

async def test_pdf_download(processor, test_key):
    """测试PDF下载功能"""
    print(f"\n{'='*60}")
    print(f"🔍 测试PDF下载: {TEST_URLS[test_key]['name']}")
    print(f"📄 描述: {TEST_URLS[test_key]['description']}")
    print(f"🔗 URL: {TEST_URLS[test_key]['url']}")
    print(f"{'='*60}")
    
    try:
        # 下载PDF
        print("⏬ 开始下载PDF...")
        pdf_path = await processor._download_pdf(TEST_URLS[test_key]["url"])
        
        # 检查文件信息
        if os.path.exists(pdf_path):
            file_size = os.path.getsize(pdf_path)
            print(f"✅ PDF下载成功!")
            print(f"   📁 文件路径: {pdf_path}")
            print(f"   📏 文件大小: {file_size:,} 字节 ({file_size/1024:.1f} KB)")
            
            # 清理文件
            os.unlink(pdf_path)
            print(f"🗑️ 清理临时文件完成")
            return True
        else:
            print(f"❌ PDF文件未找到")
            return False
            
    except Exception as e:
        print(f"❌ PDF下载失败: {e}")
        return False

async def test_pdf_to_tex(processor, test_key):
    """测试完整的PDF转TEX流程"""
    print(f"\n{'='*60}")
    print(f"🔄 测试PDF转TEX: {TEST_URLS[test_key]['name']}")  
    print(f"⚠️  这需要有效的PDFDEAL_API_KEY")
    print(f"{'='*60}")
    
    if not config.PDFDEAL_API_KEY:
        print("❌ 未配置PDFDEAL_API_KEY，跳过转换测试")
        print("💡 请在.env文件中添加你的PDFDeal API密钥")
        return False
        
    try:
        print("🚀 开始完整PDF处理流程...")
        print("   1️⃣ 下载PDF文件...")
        print("   2️⃣ 执行本地转换...")
        print("   3️⃣ 解压转换结果...")
        print("   4️⃣ 提取TEX内容...")
        print("   5️⃣ 分析Git链接...")
        
        # 步骤1: 下载PDF文件
        print("\n📥 开始下载PDF...")
        pdf_path = await processor.download_pdf(TEST_URLS[test_key]["url"])
        print(f"   ✅ 下载完成: {pdf_path}")
        
        # 步骤2: 转换PDF为TEX (使用本地测试文件)
        print("\n🔄 开始PDF转换...")
        # test_pdf_path = r'1706.03762v7 - 副本.pdf'
        test_pdf_path = pdf_path
        
        if not os.path.exists(test_pdf_path):
            print(f"   ⚠️  测试PDF文件不存在: {test_pdf_path}")
            print("   📝 使用下载的PDF文件进行转换...")
            test_pdf_path = pdf_path
            
        zip_path = await asyncio.to_thread(processor.convert_pdf_to_tex_async, test_pdf_path)
        print(f"   ✅ 转换完成，ZIP文件: {zip_path}")
        
        # 步骤3: 解压并提取TEX内容
        print("\n📦 解压转换结果...")
        if not os.path.exists(zip_path):
            raise Exception(f"转换后的ZIP文件未找到: {zip_path}")
            
        import zipfile
        extract_dir = Path(zip_path).parent / Path(f"extracted_{Path(zip_path).stem}")
        extract_dir.mkdir(exist_ok=True)
        
        with zipfile.ZipFile(zip_path, 'r') as zip_ref:
            zip_ref.extractall(extract_dir)
            
        # 查找TEX文件
        tex_files = list(extract_dir.glob("*.tex"))
        if not tex_files:
            raise Exception("解压后未找到TEX文件")
            
        tex_file_path = tex_files[0]
        print(f"   ✅ 找到TEX文件: {tex_file_path}")
        
        # 步骤4: 读取TEX内容
        print("\n📖 读取TEX内容...")
        with open(tex_file_path, 'r', encoding='utf-8') as f:
            tex_content = f.read()
        print(f"   ✅ TEX内容长度: {len(tex_content):,} 字符")
            
        # 步骤5: 分析Git链接
        print("\n🔍 分析Git链接...")
        git_url = processor.extract_git_url(tex_content)
        print(f"   🔗 提取的Git链接: {git_url or '未找到'}")
        
        # 显示结果摘要
        print(f"\n{'='*60}")
        print(f"✅ PDF转TEX处理成功!")
        print(f"   📄 原始PDF: {TEST_URLS[test_key]['name']}")
        print(f"   📝 TEX文件: {tex_file_path}")
        print(f"   📊 内容长度: {len(tex_content):,} 字符")
        print(f"   🔗 Git链接: {git_url or '未找到'}")
        print(f"{'='*60}")
        
        # 显示TEX内容预览
        if tex_content:
            print(f"\n📖 TEX内容预览 (前800字符):")
            print("─" * 60)
            preview = tex_content[:800]
            print(preview)
            if len(tex_content) > 800:
                print(f"\n... (省略剩余 {len(tex_content)-800:,} 字符)")
            print("─" * 60)
        
        # 清理临时文件
        if 0:
            print(f"\n🧹 清理临时文件...")
            cleanup_files = [pdf_path, zip_path]
            for file_path in cleanup_files:
                if os.path.exists(file_path):
                    os.unlink(file_path)
                    print(f"   🗑️  删除: {file_path}")
                
            # 清理解压目录
            import shutil
            if extract_dir.exists():
                shutil.rmtree(extract_dir)
                print(f"   🗑️  删除目录: {extract_dir}")
        
        return True
        
    except Exception as e:
        print(f"\n❌ PDF转TEX处理失败:")
        print(f"   错误信息: {e}")
        print(f"   建议检查:")
        print(f"   • PDFDEAL_API_KEY 配置是否正确")
        print(f"   • PDF文件是否存在且可读")
        print(f"   • 网络连接是否正常")
        return False

async def test_git_extraction():
    """测试Git链接提取功能"""
    print(f"\n{'='*60}")
    print(f"🔍 测试Git链接提取功能")
    print(f"{'='*60}")
    
    processor = PDFProcessor()
    
    test_texts = [
        "Code is available at https://github.com/tensorflow/tensor2tensor",
        "See our implementation: https://github.com/openai/gpt-2.git",
        "Repository: https://gitlab.com/nvidia/transformer for details.",
        "Clone via: git@github.com:facebookresearch/fairseq.git",
        "This text has no code repositories.",
    ]
    
    for i, text in enumerate(test_texts, 1):
        git_url = processor.extract_git_url(text)
        print(f"{i}. 文本: {text[:50]}...")
        print(f"   提取结果: {git_url or '未找到'}")
        print()

def check_environment():
    """检查环境配置"""
    print("🔧 检查环境配置...")
    
    issues = []
    
    if not config.PDFDEAL_API_KEY:
        issues.append("❌ PDFDEAL_API_KEY 未配置")
    else:
        print("✅ PDFDEAL_API_KEY 已配置")
    
    if not config.OPENAI_API_KEY:
        issues.append("⚠️  OPENAI_API_KEY 未配置 (论文分析需要)")
    else:
        print("✅ OPENAI_API_KEY 已配置")
    
    # 检查网络连接
    try:
        import requests
        response = requests.get("https://www.google.com", timeout=5)
        print("✅ 网络连接正常")
    except:
        issues.append("❌ 网络连接问题")
    
    if issues:
        print(f"\n⚠️  发现问题:")
        for issue in issues:
            print(f"   {issue}")
        print(f"\n💡 建议:")
        print(f"   1. 复制 .env.example 到 .env")
        print(f"   2. 在 .env 中添加你的API密钥")
        print(f"   3. 确保网络连接正常")
    
    return len(issues) == 0

async def main():
    """主函数"""
    print("🚀 PDF处理演示程序")
    print("=" * 60)
    
    # 检查环境
    env_ok = check_environment()
    
    try:
        # 初始化处理器
        processor = PDFProcessor()
        print("✅ PDF处理器初始化成功")
    except Exception as e:
        print(f"❌ PDF处理器初始化失败: {e}")
        print("💡 请检查PDFDEAL_API_KEY配置")
        return
    
    # 测试选项
    print(f"\n📋 可用测试:")
    print(f"   1. PDF下载测试 (不需要API密钥)")
    print(f"   2. PDF转TEX测试 (需要PDFDEAL_API_KEY)")
    print(f"   3. Git链接提取测试")
    print(f"   4. 运行所有测试")
    
    choice = "2"  # 默认运行所有测试
    
    if choice in ["1", "4"]:
        print(f"\n🧪 开始PDF下载测试...")
        success_count = 0
        for test_key in ["attention"]: 
            success = await test_pdf_download(processor, test_key)
            if success:
                success_count += 1
        
        print(f"\n📊 下载测试结果: {success_count}/2 成功")
    
    if choice in ["2", "4"] and config.PDFDEAL_API_KEY:
        print(f"\n🧪 开始PDF转TEX测试...")
        # 只测试简单PDF，避免消耗太多API配额
        await test_pdf_to_tex(processor, "attention")
    
    if choice in ["3", "4"]:
        await test_git_extraction()
    
    print(f"\n🎉 演示完成!")
    print(f"💡 提示:")
    print(f"   - 下载的PDF文件会自动清理")
    print(f"   - TEX转换结果保存在 output/ 目录")
    print(f"   - 如需测试大文件，请手动运行指定测试")

if __name__ == "__main__":
    asyncio.run(main())