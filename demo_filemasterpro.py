#!/usr/bin/env python3
"""
FileMasterPro 演示脚本
展示软件的主要功能和界面
"""

import os
import sys
import subprocess
import tempfile
import shutil

def create_test_environment():
    """创建测试环境"""
    print("=" * 60)
    print("创建 FileMasterPro 演示环境")
    print("=" * 60)
    
    # 创建临时测试目录
    test_dir = tempfile.mkdtemp(prefix="filemasterpro_demo_")
    print(f"📁 创建演示目录: {test_dir}")
    
    # 创建测试文件结构
    test_structure = {
        "图片": ["photo1.jpg", "photo2.png", "screenshot.gif"],
        "文档": ["report.pdf", "notes.txt", "presentation.pptx"],
        "压缩包": ["archive1.zip", "backup.rar", "data.7z"],
        "视频": ["movie.mp4", "tutorial.mkv", "clip.avi"],
        "音频": ["song.mp3", "podcast.wav", "sound.flac"],
        "安装包": ["setup.exe", "installer.msi", "app.dmg"],
        "日志与临时文件": ["error.log", "temp.tmp", "cache.bak"],
        "其它": ["unknown.xyz", "mystery.dat", "custom.ext"],
    }
    
    # 创建文件夹和文件
    for folder, files in test_structure.items():
        folder_path = os.path.join(test_dir, folder)
        os.makedirs(folder_path, exist_ok=True)
        
        for filename in files:
            filepath = os.path.join(folder_path, filename)
            with open(filepath, 'w') as f:
                f.write(f"演示文件: {filename}\n创建时间: 2026-03-16\n")
            print(f"  📄 创建文件: {folder}/{filename}")
    
    # 创建一些散落文件在根目录
    root_files = [
        "散落文档1.txt",
        "散落图片1.jpg",
        "散落视频1.mp4",
        "系统文件.dll",  # 关键文件，应该被保护
        "配置文件.ini",  # 关键文件，应该被保护
    ]
    
    for filename in root_files:
        filepath = os.path.join(test_dir, filename)
        with open(filepath, 'w') as f:
            f.write(f"根目录散落文件: {filename}\n")
        print(f"  📄 创建根目录文件: {filename}")
    
    print(f"\n📊 演示环境创建完成:")
    print(f"   - 总文件夹数: {len(test_structure)}")
    print(f"   - 总文件数: {sum(len(files) for files in test_structure.values()) + len(root_files)}")
    print(f"   - 根目录散落文件: {len(root_files)}")
    print("=" * 60)
    
    return test_dir

def run_demo_commands():
    """运行演示命令"""
    print("\n" + "=" * 60)
    print("FileMasterPro 演示命令")
    print("=" * 60)
    
    commands = [
        ("查看 Python 3.13 版本", "python3.13.exe --version"),
        ("检查依赖包安装", "python3.13.exe -m pip list | findstr customtkinter"),
        ("运行 FileMasterPro", "python3.13.exe FileMasterPro.py"),
        ("打包为可执行文件", "python3.13.exe -m PyInstaller --onefile --windowed --name FileMasterPro FileMasterPro.py"),
    ]
    
    for description, command in commands:
        print(f"\n🔧 {description}:")
        print(f"   $ {command}")
    
    print("\n💡 使用提示:")
    print("1. 直接运行 'python3.13.exe FileMasterPro.py' 启动软件")
    print("2. 选择测试文件夹进行整理")
    print("3. 先使用演习模式预览整理效果")
    print("4. 确认无误后关闭演习模式执行实际整理")
    print("5. 使用一键归拢功能整理根目录散落文件")
    print("6. 使用后悔药功能撤销操作")
    print("=" * 60)

def show_software_features():
    """展示软件功能"""
    print("\n" + "=" * 60)
    print("FileMasterPro 核心功能")
    print("=" * 60)
    
    features = [
        ("🎯 智能文件整理", "自动识别10+文件类型，智能分类整理"),
        ("🔍 深度递归扫描", "支持多层子文件夹扫描，不遗漏任何文件"),
        ("🔬 演习模式", "预览整理效果，不实际移动文件"),
        ("🛡️ 白名单保护", "自动保护系统文件和关键文件夹"),
        ("🗑️ 回收站功能", "安全删除垃圾文件，支持恢复"),
        ("💊 一键撤销", "后悔药功能，随时恢复原状"),
        ("📦 一键归拢", "快速整理根目录散落文件"),
        ("🎨 现代化界面", "使用 customtkinter 打造的现代 GUI"),
        ("⚡ 多线程处理", "界面不卡顿，实时显示进度"),
        ("📝 详细日志", "完整记录所有操作，便于排查问题"),
    ]
    
    for feature, description in features:
        print(f"{feature}: {description}")
    
    print("\n📊 安全保护机制:")
    print("   - 强力白名单: 保护 Windows、Program Files 等系统文件夹")
    print("   - 关键后缀保护: 保护 .dll、.sys、.exe 等关键文件")
    print("   - 文件夹保护: 绝对不移动文件夹，只整理文件")
    print("   - 演习模式: 新环境先预览，确认无误再执行")
    print("=" * 60)

def main():
    """主函数"""
    print("🚀 FileMasterPro - 商业级文件整理软件演示")
    print("=" * 60)
    
    # 创建演示环境
    test_dir = create_test_environment()
    
    # 展示软件功能
    show_software_features()
    
    # 运行演示命令
    run_demo_commands()
    
    print("\n📁 演示环境位置:")
    print(f"   {test_dir}")
    print("\n📋 演示步骤:")
    print("   1. 启动 FileMasterPro: python3.13.exe FileMasterPro.py")
    print("   2. 选择演示文件夹: {test_dir}")
    print("   3. 开启演习模式进行测试")
    print("   4. 体验一键归拢功能")
    print("   5. 查看整理效果")
    
    print("\n⚠️ 注意:")
    print("   - 演示环境为临时文件夹，演示结束后会自动清理")
    print("   - 实际使用时请先备份重要文件")
    print("   - 建议先使用演习模式熟悉操作")
    
    print("\n" + "=" * 60)
    print("🎉 演示准备完成！")
    print("=" * 60)
    
    # 询问是否清理演示环境
    input("\n按 Enter 键清理演示环境并退出...")
    
    # 清理演示环境
    print("\n🧹 清理演示环境...")
    try:
        shutil.rmtree(test_dir)
        print(f"✅ 已清理演示目录: {test_dir}")
    except Exception as e:
        print(f"⚠️ 清理失败: {e}")
    
    print("\n" + "=" * 60)
    print("演示结束！")
    print("=" * 60)

if __name__ == "__main__":
    main()