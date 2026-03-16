#!/usr/bin/env python3
"""
演示回收站功能
"""
import os
import sys
import time

def demo_recycle_bin():
    """演示回收站功能"""
    print("=" * 60)
    print("回收站功能演示")
    print("=" * 60)
    
    # 测试目录
    test_dir = os.path.join(os.getcwd(), "test_recycle_bin")
    
    if not os.path.exists(test_dir):
        print(f"❌ 测试目录不存在：{test_dir}")
        return
    
    print(f"📁 测试目录：{test_dir}")
    print()
    
    # 列出测试目录中的文件
    print("📄 测试文件列表：")
    files = []
    for item in os.listdir(test_dir):
        item_path = os.path.join(test_dir, item)
        if os.path.isfile(item_path):
            files.append(item)
            ext = item.split('.')[-1] if '.' in item else ''
            print(f"   - {item} (扩展名: .{ext})")
    
    print()
    print("🔍 垃圾文件识别测试：")
    print("-" * 40)
    
    # 导入脚本中的函数
    sys.path.insert(0, '.')
    from clean_my_folder import get_category
    
    trash_files = []
    normal_files = []
    
    for filename in files:
        ext = filename.split('.')[-1] if '.' in filename else ''
        category = get_category(ext)
        is_trash = category == '日志与临时文件'
        
        if is_trash:
            trash_files.append(filename)
            print(f"   🗑️  {filename} -> 识别为垃圾文件（类别：{category}）")
        else:
            normal_files.append(filename)
            print(f"   📄  {filename} -> 识别为普通文件（类别：{category}）")
    
    print()
    print("📊 识别结果统计：")
    print(f"   - 垃圾文件：{len(trash_files)} 个")
    print(f"   - 普通文件：{len(normal_files)} 个")
    
    print()
    print("💡 功能说明：")
    print("1. 垃圾文件（.log, .tmp, .bak 等）会被移动到 Windows 回收站")
    print("2. 普通文件会被分类到相应的文件夹（图片、文档等）")
    print("3. 演习模式可以预览整理结果而不实际执行")
    print("4. 实际执行时，垃圾文件通过 send2trash 库发送到回收站")
    print("5. 老板可以从回收站恢复误删的文件")
    
    print()
    print("🔄 运行脚本测试：")
    print("-" * 40)
    print("要测试完整功能，请运行：")
    print("  python clean_my_folder.py")
    print()
    print("测试步骤：")
    print("1. 输入 'y' 开启演习模式")
    print("2. 输入 'test_recycle_bin' 作为目标目录")
    print("3. 直接回车跳过自定义排除")
    print("4. 查看预览结果")
    
    print()
    print("=" * 60)
    print("演示完成！")
    print("=" * 60)

if __name__ == "__main__":
    demo_recycle_bin()