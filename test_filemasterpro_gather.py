#!/usr/bin/env python3
"""
测试 FileMasterPro 的一键归拢功能
"""

import os
import shutil
import tempfile
from FileMasterPro import FileOrganizer

def test_gather_root_files():
    """测试一键归拢功能"""
    print("=" * 60)
    print("测试 FileMasterPro 一键归拢功能")
    print("=" * 60)
    
    # 创建临时测试目录
    test_dir = tempfile.mkdtemp(prefix="test_gather_")
    print(f"创建测试目录: {test_dir}")
    
    # 创建一些测试文件
    test_files = [
        "document.txt",
        "image.jpg",
        "video.mp4",
        "archive.zip",
        "system.dll",      # 关键后缀文件
        "kernel.sys",      # 关键后缀文件
        "program.exe",     # 关键后缀文件
        "config.ini",      # 关键后缀文件
        "script.py",       # 应该被跳过
        "organize_history.json",  # 应该被跳过
        "undo_it.py",      # 应该被跳过
    ]
    
    for filename in test_files:
        filepath = os.path.join(test_dir, filename)
        with open(filepath, 'w') as f:
            f.write(f"Test content for {filename}")
        print(f"创建文件: {filename}")
    
    # 创建一些子文件夹和文件（这些不应该被归拢）
    subdir = os.path.join(test_dir, "subfolder")
    os.makedirs(subdir)
    with open(os.path.join(subdir, "subfile.txt"), 'w') as f:
        f.write("This should not be gathered")
    
    print(f"创建子文件夹: subfolder/")
    print("-" * 60)
    
    # 创建文件整理器实例
    organizer = FileOrganizer()
    
    # 测试演习模式
    print("测试演习模式（只预览不执行）:")
    print("-" * 40)
    success = organizer.gather_root_files(test_dir, drill_mode=True)
    print(f"演习模式结果: {'成功' if success else '失败'}")
    print("-" * 60)
    
    # 检查演习模式后文件是否还在原位置
    files_after_drill = os.listdir(test_dir)
    print(f"演习模式后根目录文件数: {len(files_after_drill)}")
    
    # 测试实际执行模式
    print("\n测试实际执行模式:")
    print("-" * 40)
    success = organizer.gather_root_files(test_dir, drill_mode=False)
    print(f"实际执行结果: {'成功' if success else '失败'}")
    print("-" * 60)
    
    # 检查执行结果
    files_after_execute = os.listdir(test_dir)
    print(f"执行后根目录文件数: {len(files_after_execute)}")
    print("执行后根目录内容:")
    for item in files_after_execute:
        full_path = os.path.join(test_dir, item)
        if os.path.isdir(full_path):
            print(f"  📁 {item}/")
        else:
            print(f"  📄 {item}")
    
    # 检查归拢文件夹
    gather_folders = [f for f in files_after_execute if f.startswith("根目录待处理_")]
    if gather_folders:
        gather_folder = gather_folders[0]
        gather_path = os.path.join(test_dir, gather_folder)
        print(f"\n归拢文件夹: {gather_folder}")
        gather_contents = os.listdir(gather_path)
        print(f"归拢文件夹内文件数: {len(gather_contents)}")
        print("归拢文件夹内容:")
        for item in gather_contents:
            print(f"  📄 {item}")
    
    # 检查关键文件是否被保护
    print("\n关键文件保护检查:")
    critical_files = ["system.dll", "kernel.sys", "program.exe", "config.ini"]
    for cf in critical_files:
        cf_path = os.path.join(test_dir, cf)
        if os.path.exists(cf_path):
            print(f"  ✅ {cf} 被正确保护（仍在根目录）")
        else:
            print(f"  ❌ {cf} 未被保护（可能被移动）")
    
    # 检查应该被跳过的文件
    print("\n跳过文件检查:")
    skip_files = ["script.py", "organize_history.json", "undo_it.py"]
    for sf in skip_files:
        sf_path = os.path.join(test_dir, sf)
        if os.path.exists(sf_path):
            print(f"  ✅ {sf} 被正确跳过（仍在根目录）")
        else:
            print(f"  ❌ {sf} 未被跳过（可能被移动）")
    
    # 清理测试目录
    print("\n清理测试目录...")
    shutil.rmtree(test_dir)
    print(f"已删除测试目录: {test_dir}")
    
    print("=" * 60)
    print("测试完成！")
    print("=" * 60)

if __name__ == "__main__":
    test_gather_root_files()