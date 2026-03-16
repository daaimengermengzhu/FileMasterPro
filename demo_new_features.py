"""
新功能演示脚本
演示演习模式、智能白名单和清理建议
"""
import os
import sys
import tempfile
import shutil

def print_line():
    print("=" * 60)

def create_demo_structure():
    """创建演示目录结构"""
    # 创建临时目录
    demo_dir = tempfile.mkdtemp(prefix="demo_organize_")
    print(f"📁 创建演示目录：{demo_dir}")
    
    # 创建演示文件
    files_to_create = [
        ("普通文档.txt", "这是一个普通文档文件"),
        ("普通图片.jpg", "这是一个普通图片文件"),
        ("steam_api.dll", "Steam API 文件（关键系统文件）"),
        ("kernel32.dll", "Windows 内核文件（关键系统文件）"),
        ("node.exe", "Node.js 可执行文件（关键系统文件）"),
        ("big_installer.exe", "X" * 550 * 1024 * 1024),  # 550MB
        ("large_archive.zip", "Z" * 700 * 1024 * 1024),  # 700MB
        ("subfolder/深层文件.pdf", "深层文件夹中的文件"),
        ("node_modules/package.json", '{"name": "test-package"}'),
    ]
    
    for filepath, content in files_to_create:
        full_path = os.path.join(demo_dir, filepath)
        os.makedirs(os.path.dirname(full_path), exist_ok=True)
        
        if len(content) > 100:  # 大文件
            with open(full_path, "wb") as f:
                f.write(content.encode()[:100])  # 只写100字节用于演示
        else:
            with open(full_path, "w", encoding="utf-8") as f:
                f.write(content)
    
    return demo_dir

def demo_drill_mode():
    """演示演习模式"""
    print_line()
    print("🔬 演示演习模式")
    print_line()
    
    demo_dir = create_demo_structure()
    
    print("\n📋 演示目录内容：")
    for root, dirs, files in os.walk(demo_dir):
        level = root.replace(demo_dir, '').count(os.sep)
        indent = '  ' * level
        print(f"{indent}{os.path.basename(root)}/")
        subindent = '  ' * (level + 1)
        for file in files:
            filepath = os.path.join(root, file)
            size = os.path.getsize(filepath)
            human_size = f"{size/1024/1024:.1f}MB" if size > 1024*1024 else f"{size/1024:.1f}KB"
            print(f"{subindent}{file} ({human_size})")
    
    print("\n🚀 运行演习模式演示：")
    print(f"python clean_my_folder.py")
    print(f"输入路径：{demo_dir}")
    print(f"选择演习模式：y")
    print(f"额外排除文件夹：直接回车")
    
    print("\n📋 预期演示结果：")
    print("1. 🔬 演习模式已开启 - 只预览不执行")
    print("2. 🔍 预览移动：普通文档.txt ---> 文档")
    print("3. 🔍 预览移动：普通图片.jpg ---> 图片")
    print("4. 🛡️  保护关键系统文件：steam_api.dll")
    print("5. 🛡️  保护关键系统文件：kernel32.dll")
    print("6. 🛡️  保护关键系统文件：node.exe")
    print("7. 💡 [疑似安装包，建议安装后删除] big_installer.exe")
    print("8. 💡 [疑似安装包，建议安装后删除] large_archive.zip")
    print("9. 🔍 预览移动（深层）：subfolder/深层文件.pdf ---> 文档")
    print("10. ⏭️  跳过排除文件夹：node_modules")
    print("11. 🔬 演习模式完成！预览了 X 个文件的移动计划")
    
    return demo_dir

def demo_critical_protection():
    """演示关键系统文件保护"""
    print_line()
    print("🛡️  演示关键系统文件保护")
    print_line()
    
    demo_dir = create_demo_structure()
    
    print("\n📋 保护的关键文件类型：")
    critical_types = [
        "steam_api - Steam API 文件",
        "dll - 动态链接库文件",
        "manifest - 清单文件",
        "node - Node.js 相关文件",
        "cmd - 命令文件",
        "exe - 系统级可执行文件",
        "sys - 系统文件",
        "ini/cfg/config - 配置文件",
        "boot/kernel/system - 启动和内核文件"
    ]
    
    for i, desc in enumerate(critical_types, 1):
        print(f"{i:2}. {desc}")
    
    print("\n💡 保护机制：")
    print("✅ 绝对禁止移动关键系统文件")
    print("✅ 文件名包含关键词即被保护")
    print("✅ 演习模式和实际模式都保护")
    print("✅ 显示保护提示信息")
    
    return demo_dir

def demo_install_package_suggestions():
    """演示安装包清理建议"""
    print_line()
    print("💡 演示安装包清理建议")
    print_line()
    
    demo_dir = create_demo_structure()
    
    print("\n📋 识别的安装包类型：")
    package_types = [
        ".exe - 可执行安装包",
        ".zip - 压缩安装包",
        ".rar - 压缩安装包",
        ".7z - 压缩安装包",
        ".iso - 光盘镜像",
        ".dmg - Mac 磁盘镜像",
        ".msi - Windows 安装包"
    ]
    
    for i, desc in enumerate(package_types, 1):
        print(f"{i:2}. {desc}")
    
    print("\n📊 触发条件：")
    print("✅ 文件大小 ≥ 500MB")
    print("✅ 文件扩展名匹配安装包类型")
    print("✅ 显示黄色警告标注")
    print("✅ 显示文件大小（人类可读格式）")
    
    print("\n💡 使用建议：")
    print("1. 检查大文件是否真的需要保留")
    print("2. 安装包安装后可以考虑删除")
    print("3. 备份重要安装包到外部存储")
    print("4. 定期清理不需要的安装包")
    
    return demo_dir

def demo_full_workflow():
    """演示完整工作流程"""
    print_line()
    print("🚀 演示完整工作流程")
    print_line()
    
    demo_dir = create_demo_structure()
    
    print("\n📋 安全整理工作流程：")
    steps = [
        "1. 首次使用选择演习模式预览",
        "2. 检查关键文件是否被正确保护",
        "3. 查看安装包清理建议",
        "4. 确认预览结果无误",
        "5. 重新运行选择实际模式",
        "6. 执行文件整理",
        "7. 使用后悔药脚本随时还原"
    ]
    
    for step in steps:
        print(step)
    
    print("\n🛡️  安全特性：")
    print("✅ 演习模式：先预览后执行")
    print("✅ 智能白名单：保护系统文件")
    print("✅ 清理建议：识别大文件安装包")
    print("✅ 后悔药：一键还原所有文件")
    print("✅ 深度扫描：支持子文件夹")
    print("✅ 排除列表：跳过系统/开发文件夹")
    
    return demo_dir

def main():
    print("\n" + "🌟" * 30)
    print("       新功能演示")
    print("🌟" * 30 + "\n")
    
    print("全能文件整理器 - 升级版功能演示")
    print("版本：深度扫描版 + 演习模式 + 智能白名单 + 清理建议")
    
    print("\n选择演示项目：")
    print("1. 演习模式演示")
    print("2. 关键系统文件保护演示")
    print("3. 安装包清理建议演示")
    print("4. 完整工作流程演示")
    print("5. 全部演示")
    print("6. 退出")
    
    choice = input("\n请输入选择 (1-6): ").strip()
    
    demo_dirs = []
    
    try:
        if choice == "1" or choice == "5":
            demo_dir = demo_drill_mode()
            demo_dirs.append(demo_dir)
            print("\n✅ 演习模式演示完成")
        
        if choice == "2" or choice == "5":
            demo_dir = demo_critical_protection()
            demo_dirs.append(demo_dir)
            print("\n✅ 关键系统文件保护演示完成")
        
        if choice == "3" or choice == "5":
            demo_dir = demo_install_package_suggestions()
            demo_dirs.append(demo_dir)
            print("\n✅ 安装包清理建议演示完成")
        
        if choice == "4" or choice == "5":
            demo_dir = demo_full_workflow()
            demo_dirs.append(demo_dir)
            print("\n✅ 完整工作流程演示完成")
        
        if choice == "6":
            print("演示结束")
            return
        
        print_line()
        print("🎯 新功能总结")
        print_line()
        
        print("🔬 演习模式：")
        print("   • 运行时询问：'是否开启演习模式？(y/n)'")
        print("   • 选 y：只预览不执行，显示移动计划")
        print("   • 选 n：实际执行文件整理")
        
        print("\n🛡️  智能白名单：")
        print("   • 内置 CRITICAL_FILES 列表")
        print("   • 保护 steam_api、dll、manifest、node、cmd 等文件")
        print("   • 绝对禁止移动关键系统文件")
        
        print("\n💡 清理建议：")
        print("   • 扫描超过500MB的 .exe/.zip 文件")
        print("   • 黄色标注：'[疑似安装包，建议安装后删除]'")
        print("   • 显示文件大小（人类可读格式）")
        
        print("\n🛡️  安全增强：")
        print("   • 系统文件夹自动排除（Program Files, Windows等）")
        print("   • 开发文件夹自动排除（node_modules, .git等）")
        print("   • 用户自定义排除文件夹支持")
        print("   • 后悔药脚本支持深层还原")
        
        print_line()
        print("🎉 演示完成！")
        print_line()
        
        print("\n🚀 实际使用建议：")
        print("1. 首次整理 D 盘时使用演习模式预览")
        print("2. 检查关键系统文件是否被正确保护")
        print("3. 查看大文件安装包清理建议")
        print("4. 确认无误后再实际执行")
        print("5. 使用后悔药脚本随时还原")
        
    finally:
        # 清理演示目录
        for demo_dir in set(demo_dirs):
            if os.path.exists(demo_dir):
                try:
                    shutil.rmtree(demo_dir)
                    print(f"\n🧹 已清理演示目录：{demo_dir}")
                except Exception as e:
                    print(f"⚠️  清理目录失败：{demo_dir}, 错误：{e}")

if __name__ == '__main__':
    main()
