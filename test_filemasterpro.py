"""
FileMasterPro 测试脚本
用于验证 GUI 程序的基本功能
"""

import os
import tempfile
import shutil
from pathlib import Path

def create_test_environment():
    """创建测试环境"""
    # 创建临时目录
    test_dir = tempfile.mkdtemp(prefix="filemaster_test_")
    print(f"📁 创建测试目录: {test_dir}")
    
    # 创建各种类型的测试文件
    test_files = [
        ("test_image.jpg", "图片"),
        ("test_document.pdf", "文档"),
        ("test_installer.exe", "安装包"),
        ("test_archive.zip", "压缩包"),
        ("test_video.mp4", "视频"),
        ("test_audio.mp3", "音频"),
        ("test_ebook.epub", "电子书"),
        ("test_code.js", "代码相关"),
        ("test_design.psd", "设计与字体"),
        ("test_log.log", "日志与临时文件"),
        ("test_temp.tmp", "日志与临时文件"),
        ("unknown_file.xyz", "其它"),
    ]
    
    # 创建深层目录结构
    deep_dir = os.path.join(test_dir, "deep_folder", "subfolder1", "nested")
    os.makedirs(deep_dir, exist_ok=True)
    
    # 创建文件
    for filename, category in test_files:
        # 在根目录创建
        filepath = os.path.join(test_dir, filename)
        with open(filepath, 'w') as f:
            f.write(f"This is a test {category} file: {filename}")
        
        # 在深层目录也创建一份
        deep_filepath = os.path.join(deep_dir, f"deep_{filename}")
        with open(deep_filepath, 'w') as f:
            f.write(f"This is a deep test {category} file: {filename}")
    
    # 创建一些大文件（模拟安装包）
    large_file = os.path.join(test_dir, "large_installer.exe")
    with open(large_file, 'wb') as f:
        f.write(b'0' * 1024 * 1024)  # 1MB 文件
    
    print(f"✅ 创建了 {len(test_files)*2 + 1} 个测试文件")
    print(f"📁 目录结构:")
    print(f"  - {test_dir}")
    print(f"    ├── 各种测试文件")
    print(f"    └── deep_folder/subfolder1/nested/")
    print(f"        └── 深层测试文件")
    
    return test_dir

def test_organizer_logic():
    """测试整理器逻辑"""
    print("\n" + "="*50)
    print("🧪 测试 FileOrganizer 核心逻辑")
    print("="*50)
    
    from FileMasterPro import FileOrganizer
    
    # 创建测试目录
    test_dir = create_test_environment()
    
    try:
        # 创建整理器实例
        organizer = FileOrganizer()
        
        print("\n🔬 测试演习模式（预览）:")
        print("-"*30)
        success = organizer.organize_files(
            target_dir=test_dir,
            drill_mode=True,  # 演习模式
            deep_scan=True,   # 深度扫描
            user_exclude_folders=None
        )
        
        if success:
            print("✅ 演习模式测试通过")
        else:
            print("❌ 演习模式测试失败")
        
        print("\n🚀 测试实际执行模式:")
        print("-"*30)
        success = organizer.organize_files(
            target_dir=test_dir,
            drill_mode=False,  # 实际执行
            deep_scan=True,    # 深度扫描
            user_exclude_folders=None
        )
        
        if success:
            print("✅ 实际执行模式测试通过")
            
            # 检查分类目录是否创建
            categories = ['图片', '文档', '安装包', '压缩包', '视频', '音频', 
                         '电子书', '代码相关', '设计与字体', '日志与临时文件', '其它']
            
            created_dirs = []
            for category in categories:
                category_dir = os.path.join(test_dir, category)
                if os.path.exists(category_dir):
                    created_dirs.append(category)
            
            print(f"📁 创建的分类目录: {len(created_dirs)} 个")
            for dir_name in created_dirs:
                print(f"  - {dir_name}")
            
            # 检查后悔药脚本是否创建
            undo_script = os.path.join(test_dir, "undo_it.py")
            history_file = os.path.join(test_dir, "organize_history.json")
            
            if os.path.exists(undo_script):
                print(f"✅ 后悔药脚本已创建: {undo_script}")
            else:
                print(f"❌ 后悔药脚本未创建")
            
            if os.path.exists(history_file):
                print(f"✅ 历史记录文件已创建: {history_file}")
            else:
                print(f"❌ 历史记录文件未创建")
            
            # 测试撤销功能
            print("\n💊 测试撤销功能:")
            print("-"*30)
            undo_success = organizer.undo_last_operation(test_dir)
            
            if undo_success:
                print("✅ 撤销功能测试通过")
            else:
                print("❌ 撤销功能测试失败")
                
        else:
            print("❌ 实际执行模式测试失败")
            
    finally:
        # 清理测试目录
        print(f"\n🧹 清理测试目录: {test_dir}")
        shutil.rmtree(test_dir, ignore_errors=True)
        print("✅ 测试完成")

def test_gui_components():
    """测试 GUI 组件"""
    print("\n" + "="*50)
    print("🖥️  测试 GUI 组件")
    print("="*50)
    
    try:
        import customtkinter as ctk
        from tkinter import messagebox
        
        print("✅ customtkinter 导入成功")
        print("✅ tkinter 组件可用")
        
        # 测试颜色主题
        ctk.set_appearance_mode("dark")
        ctk.set_default_color_theme("blue")
        print("✅ 主题设置成功")
        
        return True
        
    except Exception as e:
        print(f"❌ GUI 组件测试失败: {e}")
        return False

def main():
    """主测试函数"""
    print("🧪 FileMasterPro 功能测试")
    print("="*50)
    
    # 测试 GUI 组件
    gui_ok = test_gui_components()
    
    if gui_ok:
        # 测试整理器逻辑
        test_organizer_logic()
    
    print("\n" + "="*50)
    print("🎉 所有测试完成！")
    print("="*50)
    print("\n💡 要运行完整的 GUI 程序，请执行:")
    print("   python FileMasterPro.py")
    print("\n💡 程序功能:")
    print("   - 现代化 dark 主题界面")
    print("   - 深度递归扫描")
    print("   - 演习模式（预览）")
    print("   - 白名单保护系统文件")
    print("   - 垃圾文件回收站")
    print("   - 一键撤销功能")
    print("   - 多线程处理，界面不卡顿")

if __name__ == "__main__":
    main()