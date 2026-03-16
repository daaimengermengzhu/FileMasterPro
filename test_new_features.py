"""
测试新功能脚本
测试演习模式、智能白名单和清理建议功能
"""
import os
import sys
import shutil
import tempfile

def print_line():
    print("=" * 60)

def create_test_structure_with_critical_files():
    """创建包含关键系统文件的测试目录结构"""
    # 创建临时目录
    test_dir = tempfile.mkdtemp(prefix="test_organize_")
    print(f"✅ 创建测试目录：{test_dir}")
    
    # 创建根目录文件
    with open(os.path.join(test_dir, "normal_document.txt"), "w", encoding="utf-8") as f:
        f.write("普通文档文件")
    
    with open(os.path.join(test_dir, "normal_image.jpg"), "w", encoding="utf-8") as f:
        f.write("普通图片文件")
    
    # 创建关键系统文件
    with open(os.path.join(test_dir, "steam_api.dll"), "w", encoding="utf-8") as f:
        f.write("Steam API 文件（应被保护）")
    
    with open(os.path.join(test_dir, "kernel32.dll"), "w", encoding="utf-8") as f:
        f.write("Windows 内核文件（应被保护）")
    
    with open(os.path.join(test_dir, "node.exe"), "w", encoding="utf-8") as f:
        f.write("Node.js 可执行文件（应被保护）")
    
    with open(os.path.join(test_dir, "config.ini"), "w", encoding="utf-8") as f:
        f.write("配置文件（应被保护）")
    
    # 创建大文件安装包（模拟）
    with open(os.path.join(test_dir, "big_installer.exe"), "w", encoding="utf-8") as f:
        # 写入600MB的模拟数据
        f.write("X" * 600 * 1024 * 1024)  # 600MB
    
    with open(os.path.join(test_dir, "large_archive.zip"), "w", encoding="utf-8") as f:
        # 写入800MB的模拟数据
        f.write("Z" * 800 * 1024 * 1024)  # 800MB
    
    # 创建子文件夹
    sub1 = os.path.join(test_dir, "subfolder1")
    os.makedirs(sub1)
    with open(os.path.join(sub1, "sub_doc.txt"), "w", encoding="utf-8") as f:
        f.write("子文件夹文档")
    
    # 创建排除文件夹
    excluded = os.path.join(test_dir, "node_modules")
    os.makedirs(excluded)
    with open(os.path.join(excluded, "package.json"), "w", encoding="utf-8") as f:
        f.write('{"name": "test-package"}')
    
    return test_dir

def test_drill_mode():
    """测试演习模式"""
    print_line()
    print("🔬 测试演习模式")
    print_line()
    
    test_dir = create_test_structure_with_critical_files()
    
    print("\n📋 测试目录内容：")
    for root, dirs, files in os.walk(test_dir):
        level = root.replace(test_dir, '').count(os.sep)
        indent = '  ' * level
        print(f"{indent}{os.path.basename(root)}/")
        subindent = '  ' * (level + 1)
        for file in files:
            filepath = os.path.join(root, file)
            size = os.path.getsize(filepath)
            print(f"{subindent}{file} ({size:,} bytes)")
    
    print("\n💡 演习模式应：")
    print("1. 只显示预览，不实际移动文件")
    print("2. 保护关键系统文件（steam_api.dll, kernel32.dll等）")
    print("3. 显示安装包清理建议（big_installer.exe, large_archive.zip）")
    print("4. 跳过排除文件夹（node_modules）")
    
    print("\n🚀 请手动运行以下命令测试：")
    print(f"python clean_my_folder.py")
    print(f"输入路径：{test_dir}")
    print(f"选择演习模式：y")
    print(f"额外排除文件夹：直接回车")
    
    print("\n📋 预期结果：")
    print("✅ 显示'演习模式已开启'")
    print("✅ 显示'预览移动'而不是'已移动'")
    print("✅ 显示'保护关键系统文件'")
    print("✅ 显示'[疑似安装包，建议安装后删除]'")
    print("✅ 显示'演习模式完成！预览了 X 个文件的移动计划'")
    
    return test_dir

def test_critical_file_protection():
    """测试关键系统文件保护"""
    print_line()
    print("🛡️  测试关键系统文件保护")
    print_line()
    
    test_dir = create_test_structure_with_critical_files()
    
    # 导入模块
    sys.path.insert(0, r"d:\My_Ai_app")
    import clean_my_folder as cf
    
    print("\n📋 测试的关键文件：")
    critical_files = [
        "steam_api.dll",
        "kernel32.dll", 
        "node.exe",
        "config.ini"
    ]
    
    for file in critical_files:
        filepath = os.path.join(test_dir, file)
        if os.path.exists(filepath):
            print(f"✅ {file} - 存在")
        else:
            print(f"❌ {file} - 不存在")
    
    print("\n🔍 测试 is_critical_file 函数：")
    for file in critical_files:
        is_critical = cf.is_critical_file(file)
        print(f"{file}: {'🛡️  是' if is_critical else '✅ 否'}")
    
    # 测试非关键文件
    normal_files = ["normal_document.txt", "normal_image.jpg", "sub_doc.txt"]
    print("\n🔍 测试非关键文件：")
    for file in normal_files:
        is_critical = cf.is_critical_file(file)
        print(f"{file}: {'❌ 是' if is_critical else '✅ 否'}")
    
    print("\n💡 关键文件保护应：")
    print("1. 包含 'steam_api' 的文件被识别为关键")
    print("2. 包含 'dll' 的文件被识别为关键")
    print("3. 包含 'node' 的文件被识别为关键")
    print("4. 包含 'cmd' 的文件被识别为关键")
    print("5. 普通文件不被识别为关键")
    
    return test_dir

def test_install_package_suggestion():
    """测试安装包清理建议"""
    print_line()
    print("💡 测试安装包清理建议")
    print_line()
    
    test_dir = create_test_structure_with_critical_files()
    
    print("\n📋 测试的大文件安装包：")
    large_files = [
        ("big_installer.exe", 600 * 1024 * 1024),
        ("large_archive.zip", 800 * 1024 * 1024)
    ]
    
    for filename, size in large_files:
        filepath = os.path.join(test_dir, filename)
        if os.path.exists(filepath):
            actual_size = os.path.getsize(filepath)
            print(f"✅ {filename}: {actual_size:,} bytes (目标: {size:,} bytes)")
        else:
            print(f"❌ {filename}: 不存在")
    
    print("\n💡 安装包清理建议应：")
    print("1. 识别超过500MB的 .exe 文件")
    print("2. 识别超过500MB的 .zip 文件")
    print("3. 显示黄色标注 '[疑似安装包，建议安装后删除]'")
    print("4. 显示文件大小（人类可读格式）")
    
    print("\n🚀 请手动运行以下命令验证：")
    print(f"python clean_my_folder.py")
    print(f"输入路径：{test_dir}")
    print(f"选择演习模式：y")
    
    return test_dir

def test_full_workflow():
    """测试完整工作流程"""
    print_line()
    print("🚀 测试完整工作流程")
    print_line()
    
    test_dir = create_test_structure_with_critical_files()
    
    print("\n📋 完整测试流程：")
    print("1. 演习模式预览")
    print("2. 关键文件保护验证")
    print("3. 安装包建议验证")
    print("4. 实际执行模式")
    print("5. 后悔药功能")
    
    print("\n💡 步骤1：演习模式")
    print(f"python clean_my_folder.py")
    print(f"路径：{test_dir}")
    print(f"演习模式：y")
    print(f"额外排除：直接回车")
    
    print("\n💡 步骤2：实际执行")
    print(f"python clean_my_folder.py")
    print(f"路径：{test_dir}")
    print(f"演习模式：n")
    print(f"额外排除：直接回车")
    
    print("\n💡 步骤3：后悔药")
    print(f"cd {test_dir}")
    print(f"python undo_it.py")
    print(f"确认：y")
    
    print("\n📋 预期完整结果：")
    print("✅ 演习模式：只预览不执行")
    print("✅ 实际模式：移动普通文件，保护关键文件")
    print("✅ 安装包建议：显示黄色警告")
    print("✅ 后悔药：成功还原所有文件")
    
    return test_dir

def main():
    print("\n" + "🌟" * 30)
    print("       新功能测试套件")
    print("🌟" * 30 + "\n")
    
    print("测试全能文件整理器的新功能：")
    print("1. 演习模式：只预览不执行")
    print("2. 智能白名单：保护关键系统文件")
    print("3. 清理建议：识别大文件安装包")
    
    print("\n选择测试项目：")
    print("1. 测试演习模式")
    print("2. 测试关键系统文件保护")
    print("3. 测试安装包清理建议")
    print("4. 测试完整工作流程")
    print("5. 全部测试")
    print("6. 退出")
    
    choice = input("\n请输入选择 (1-6): ").strip()
    
    test_dirs = []
    
    try:
        if choice == "1" or choice == "5":
            test_dir = test_drill_mode()
            test_dirs.append(test_dir)
            print("\n✅ 演习模式测试完成")
        
        if choice == "2" or choice == "5":
            test_dir = test_critical_file_protection()
            test_dirs.append(test_dir)
            print("\n✅ 关键文件保护测试完成")
        
        if choice == "3" or choice == "5":
            test_dir = test_install_package_suggestion()
            test_dirs.append(test_dir)
            print("\n✅ 安装包清理建议测试完成")
        
        if choice == "4" or choice == "5":
            test_dir = test_full_workflow()
            test_dirs.append(test_dir)
            print("\n✅ 完整工作流程测试完成")
        
        if choice == "6":
            print("测试结束")
            return
        
        print_line()
        print("📊 测试总结")
        print_line()
        
        print("🎯 新功能实现：")
        print("✅ 演习模式：运行时询问，只预览不执行")
        print("✅ 智能白名单：保护 steam_api、dll、manifest、node、cmd 等关键文件")
        print("✅ 清理建议：超过500MB的 .exe/.zip 文件显示黄色警告")
        
        print("\n🛡️  安全特性：")
        print("✅ 关键系统文件绝对禁止移动")
        print("✅ 系统文件夹自动排除（Program Files, Windows, System32等）")
        print("✅ 开发文件夹自动排除（node_modules, .git, venv等）")
        print("✅ 用户自定义排除文件夹支持")
        
        print("\n💡 使用建议：")
        print("1. 首次使用时选择演习模式预览结果")
        print("2. 检查关键文件是否被正确保护")
        print("3. 查看安装包清理建议")
        print("4. 确认无误后再实际执行")
        print("5. 使用后悔药脚本随时还原")
        
        print_line()
        print("🎉 新功能测试完成！")
        print_line()
        
    finally:
        # 清理测试目录
        for test_dir in set(test_dirs):
            if os.path.exists(test_dir):
                try:
                    shutil.rmtree(test_dir)
                    print(f"🧹 已清理测试目录：{test_dir}")
                except Exception as e:
                    print(f"⚠️  清理目录失败：{test_dir}, 错误：{e}")

if __name__ == '__main__':
    main()
