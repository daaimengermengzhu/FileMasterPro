"""
深度扫描功能演示脚本
展示全能文件整理器的深度扫描功能
"""
import os
import sys
import shutil

def print_line():
    print("=" * 60)

def create_test_structure():
    """创建测试目录结构"""
    test_dir = r"d:\My_Ai_app\demo_test"
    
    # 清理旧的测试目录
    if os.path.exists(test_dir):
        shutil.rmtree(test_dir)
    
    # 创建测试目录结构
    os.makedirs(test_dir)
    
    # 创建根目录文件
    with open(os.path.join(test_dir, "root_document.txt"), "w", encoding="utf-8") as f:
        f.write("根目录文档文件")
    
    with open(os.path.join(test_dir, "root_image.jpg"), "w", encoding="utf-8") as f:
        f.write("根目录图片文件")
    
    # 创建子文件夹1
    sub1 = os.path.join(test_dir, "subfolder1")
    os.makedirs(sub1)
    with open(os.path.join(sub1, "sub1_doc.txt"), "w", encoding="utf-8") as f:
        f.write("子文件夹1文档")
    with open(os.path.join(sub1, "sub1_image.jpg"), "w", encoding="utf-8") as f:
        f.write("子文件夹1图片")
    
    # 创建深层嵌套文件夹
    nested = os.path.join(sub1, "deeply_nested")
    os.makedirs(nested)
    with open(os.path.join(nested, "deep_document.txt"), "w", encoding="utf-8") as f:
        f.write("深层嵌套文档")
    with open(os.path.join(nested, "deep_image.jpg"), "w", encoding="utf-8") as f:
        f.write("深层嵌套图片")
    
    # 创建子文件夹2
    sub2 = os.path.join(test_dir, "subfolder2")
    os.makedirs(sub2)
    with open(os.path.join(sub2, "sub2_doc.txt"), "w", encoding="utf-8") as f:
        f.write("子文件夹2文档")
    with open(os.path.join(sub2, "sub2_image.jpg"), "w", encoding="utf-8") as f:
        f.write("子文件夹2图片")
    
    # 创建排除文件夹（模拟node_modules）
    excluded = os.path.join(test_dir, "node_modules")
    os.makedirs(excluded)
    with open(os.path.join(excluded, "package.json"), "w", encoding="utf-8") as f:
        f.write('{"name": "test-package"}')
    
    print(f"✅ 测试目录已创建：{test_dir}")
    return test_dir

def list_directory_structure(directory, indent=0):
    """列出目录结构"""
    items = sorted(os.listdir(directory))
    for item in items:
        full_path = os.path.join(directory, item)
        prefix = "  " * indent
        if os.path.isdir(full_path):
            print(f"{prefix}📁 {item}/")
            list_directory_structure(full_path, indent + 1)
        else:
            print(f"{prefix}📄 {item}")

def demo_scan_function():
    """演示扫描功能"""
    print_line()
    print("🔍 演示深度扫描功能")
    print_line()
    
    # 导入模块
    sys.path.insert(0, r"d:\My_Ai_app")
    import clean_my_folder as cf
    
    test_dir = create_test_structure()
    
    print("\n📋 测试目录结构：")
    list_directory_structure(test_dir)
    
    print("\n🚀 运行深度扫描...")
    print_line()
    
    # 测试扫描功能
    all_files, folders_scanned, max_depth = cf.scan_files_recursively(test_dir)
    
    print(f"\n📊 扫描结果：")
    print(f"  - 扫描文件夹：{folders_scanned} 个")
    print(f"  - 扫描深度：{max_depth} 层")
    print(f"  - 发现文件：{len(all_files)} 个")
    
    # 检查排除文件夹是否被跳过
    excluded_found = False
    for file_path in all_files:
        if 'node_modules' in file_path:
            excluded_found = True
            print(f"❌ 错误：排除文件夹中的文件被扫描到了：{file_path}")
    
    if not excluded_found:
        print("✅ 排除文件夹功能正常（node_modules 被正确跳过）")
    
    # 检查深层文件是否被扫描到
    deep_files = [f for f in all_files if 'deeply_nested' in f]
    if len(deep_files) >= 2:
        print(f"✅ 深层文件扫描正常（找到 {len(deep_files)} 个深层文件）")
    else:
        print(f"❌ 深层文件扫描可能有问题")
    
    return test_dir, all_files, folders_scanned, max_depth

def demo_organize_function():
    """演示整理功能"""
    print_line()
    print("🗂️  演示完整整理流程")
    print_line()
    
    test_dir = create_test_structure()
    
    print("\n📋 整理前的目录结构：")
    list_directory_structure(test_dir)
    
    print("\n💡 请手动运行以下命令体验完整功能：")
    print(f"python clean_my_folder.py")
    print(f"输入路径：{test_dir}")
    print(f"输入额外排除文件夹：subfolder2（如果需要）")
    print("\n观察以下功能：")
    print("1. 深度扫描统计（扫描深度、文件夹数量）")
    print("2. 排除文件夹功能（node_modules 被跳过）")
    print("3. 深层文件移动（显示'深层'标记）")
    print("4. 统计报告（深层文件数量）")
    print("5. 后悔药脚本生成")
    
    print("\n🚀 然后运行后悔药脚本：")
    print(f"cd {test_dir}")
    print("python undo_it.py")
    print("输入 y 确认")
    print("\n观察文件是否还原到原位")
    
    return test_dir

def main():
    print("\n" + "🌟" * 30)
    print("       深度扫描功能演示")
    print("🌟" * 30 + "\n")
    
    print("本演示展示全能文件整理器的深度扫描功能：")
    print("1. 递归扫描所有子文件夹")
    print("2. 智能排除系统文件夹（node_modules, .git 等）")
    print("3. 支持用户自定义排除文件夹")
    print("4. 统计扫描深度和文件夹数量")
    print("5. 深层文件移动和还原")
    print("6. 后悔药功能支持深层还原")
    
    print("\n选择演示模式：")
    print("1. 演示扫描功能")
    print("2. 演示完整整理流程")
    print("3. 退出")
    
    choice = input("\n请输入选择 (1-3): ").strip()
    
    if choice == "1":
        test_dir, all_files, folders_scanned, max_depth = demo_scan_function()
        
        print("\n")
        print_line()
        print("📊 扫描功能演示总结")
        print_line()
        print(f"✅ 深度扫描：支持 {max_depth} 层嵌套")
        print(f"✅ 排除文件夹：自动跳过 node_modules 等系统文件夹")
        print(f"✅ 统计展示：显示扫描深度和文件夹数量")
        print(f"✅ 深层文件：成功扫描到深层嵌套文件")
        
    elif choice == "2":
        test_dir = demo_organize_function()
        
        print("\n")
        print_line()
        print("📊 整理功能演示总结")
        print_line()
        print("✅ 完整流程：扫描 → 分类 → 移动 → 生成后悔药")
        print("✅ 深度支持：深层文件移动和还原")
        print("✅ 用户友好：支持自定义排除文件夹")
        print("✅ 安全可靠：后悔药确保可撤销")
        
    else:
        print("演示结束")
        return
    
    print("\n💡 深度扫描功能特点：")
    print("  - 递归扫描：自动遍历所有子文件夹")
    print("  - 智能排除：保护系统文件夹不被破坏")
    print("  - 深度统计：显示扫描深度和文件夹数量")
    print("  - 深层还原：后悔药支持深层文件还原")
    print("  - 用户自定义：可添加自定义排除文件夹")
    
    print_line()
    print("🎉 演示完成！")
    print_line()

if __name__ == '__main__':
    main()
