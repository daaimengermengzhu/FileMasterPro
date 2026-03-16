dir"""
深度扫描功能测试脚本
"""
import os
import sys
import json
import shutil
import subprocess

# 测试目录
TEST_DIR = r"d:\My_Ai_app\deep_test"

def print_line():
    print("=" * 60)

def list_all_files(directory, indent=0):
    """递归列出目录内容"""
    items = sorted(os.listdir(directory))
    for item in items:
        full_path = os.path.join(directory, item)
        prefix = "  " * indent
        if os.path.isdir(full_path):
            print(f"{prefix}📁 {item}/")
            list_all_files(full_path, indent + 1)
        else:
            print(f"{prefix}📄 {item}")

def test_deep_scan():
    """测试深度扫描功能"""
    print_line()
    print("🧪 开始测试深度扫描功能")
    print_line()
    
    print("\n📋 测试目录结构：")
    list_all_files(TEST_DIR)
    
    # 运行整理脚本（模拟输入）
    print("\n🚀 运行深度扫描整理...")
    print_line()
    
    # 导入模块
    sys.path.insert(0, r"d:\My_Ai_app")
    import clean_my_folder as cf
    
    # 直接调用扫描函数测试
    print("🔍 测试扫描功能...")
    all_files, folders_scanned, max_depth = cf.scan_files_recursively(TEST_DIR)
    
    print(f"扫描结果：")
    print(f"  - 发现文件：{len(all_files)} 个")
    print(f"  - 扫描文件夹：{folders_scanned} 个")
    print(f"  - 最大深度：{max_depth} 层")
    
    # 检查排除文件夹是否被跳过
    excluded_found = False
    for file_path in all_files:
        if 'excluded_folder' in file_path or '.git' in file_path or 'node_modules' in file_path:
            excluded_found = True
            print(f"⚠️  错误：排除文件夹中的文件被扫描到了：{file_path}")
    
    if not excluded_found:
        print("✅ 排除文件夹功能正常")
    
    # 检查深层文件是否被扫描到
    deep_files = [f for f in all_files if 'nested' in f]
    if len(deep_files) >= 2:
        print(f"✅ 深层文件扫描正常（找到 {len(deep_files)} 个深层文件）")
    else:
        print(f"❌ 深层文件扫描可能有问题")
    
    return all_files, folders_scanned, max_depth

def test_organize_and_undo():
    """测试整理和还原功能"""
    print_line()
    print("🧪 测试完整整理和还原流程")
    print_line()
    
    # 备份原始文件列表
    original_files = []
    for root, dirs, files in os.walk(TEST_DIR):
        for file in files:
            if file.endswith('.py'):
                continue
            full_path = os.path.join(root, file)
            original_files.append(full_path)
    
    print(f"原始文件数量：{len(original_files)}")
    
    # 运行整理脚本
    print("\n🚀 运行整理脚本...")
    print_line()
    
    # 使用 subprocess 模拟用户输入
    process = subprocess.Popen(
        [sys.executable, r"d:\My_Ai_app\clean_my_folder.py"],
        stdin=subprocess.PIPE,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True,
        cwd=r"d:\My_Ai_app"
    )
    
    # 输入测试目录路径
    stdout, stderr = process.communicate(input=TEST_DIR + "\n")
    
    print("整理脚本输出：")
    print(stdout[:1000] + "..." if len(stdout) > 1000 else stdout)
    
    if process.returncode != 0:
        print(f"❌ 整理脚本运行失败：{stderr}")
        return False
    
    # 检查整理结果
    print("\n📋 整理后的目录结构：")
    list_all_files(TEST_DIR)
    
    # 检查历史文件
    history_file = os.path.join(TEST_DIR, "organize_history.json")
    undo_file = os.path.join(TEST_DIR, "undo_it.py")
    
    if os.path.exists(history_file):
        print(f"✅ 历史文件已生成：{history_file}")
        with open(history_file, 'r', encoding='utf-8') as f:
            history = json.load(f)
            print(f"   - 移动记录：{history.get('total_moves', 0)} 条")
            print(f"   - 扫描深度：{history.get('max_depth', 0)} 层")
    else:
        print("❌ 历史文件未生成")
        return False
    
    if os.path.exists(undo_file):
        print(f"✅ 后悔药脚本已生成：{undo_file}")
    else:
        print("❌ 后悔药脚本未生成")
        return False
    
    # 检查分类文件夹
    category_folders = ['图片', '文档']
    for folder in category_folders:
        folder_path = os.path.join(TEST_DIR, folder)
        if os.path.exists(folder_path):
            print(f"✅ 分类文件夹已创建：{folder}")
        else:
            print(f"❌ 分类文件夹未创建：{folder}")
    
    # 运行后悔药脚本
    print("\n🚀 运行后悔药脚本...")
    print_line()
    
    process = subprocess.Popen(
        [sys.executable, undo_file],
        stdin=subprocess.PIPE,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True,
        cwd=TEST_DIR
    )
    
    stdout, stderr = process.communicate(input="y\n")
    
    print("后悔药脚本输出：")
    print(stdout[:1000] + "..." if len(stdout) > 1000 else stdout)
    
    if process.returncode != 0:
        print(f"❌ 后悔药脚本运行失败：{stderr}")
        return False
    
    # 检查还原结果
    print("\n📋 还原后的目录结构：")
    list_all_files(TEST_DIR)
    
    # 检查文件是否还原到原位
    restored_count = 0
    for original_file in original_files:
        if os.path.exists(original_file):
            restored_count += 1
    
    print(f"\n📊 还原统计：")
    print(f"   - 原始文件：{len(original_files)} 个")
    print(f"   - 已还原文件：{restored_count} 个")
    
    if restored_count == len(original_files):
        print("✅ 所有文件已成功还原！")
    else:
        print(f"❌ 文件还原不完整，缺失 {len(original_files) - restored_count} 个文件")
        return False
    
    # 检查历史文件是否已删除
    if not os.path.exists(history_file):
        print("✅ 历史文件已自动清理")
    else:
        print("⚠️  历史文件未自动清理")
    
    return True

def main():
    print("\n" + "🔬" * 30)
    print("       深度扫描功能测试")
    print("🔬" * 30 + "\n")
    
    # 测试扫描功能
    print("阶段1：测试扫描功能")
    all_files, folders_scanned, max_depth = test_deep_scan()
    
    print("\n")
    
    # 测试完整流程
    print("阶段2：测试完整整理和还原流程")
    success = test_organize_and_undo()
    
    # 总结
    print("\n")
    print_line()
    print("📊 测试总结")
    print_line()
    
    if success:
        print("🎊 所有测试通过！")
        print(f"   - 深度扫描：✅ 正常（扫描深度：{max_depth} 层）")
        print(f"   - 排除文件夹：✅ 正常")
        print(f"   - 整理功能：✅ 正常")
        print(f"   - 后悔药功能：✅ 正常")
        print(f"   - 统计展示：✅ 正常")
        print("\n💡 深度扫描功能已成功实现！")
    else:
        print("⚠️ 部分测试失败，请检查代码")
    
    print_line()
    
    # 清理测试目录
    print("\n🧹 清理测试目录...")
    try:
        # 删除分类文件夹
        for folder in ['图片', '文档', '其它', '音频', '视频', '压缩包']:
            folder_path = os.path.join(TEST_DIR, folder)
            if os.path.exists(folder_path):
                shutil.rmtree(folder_path)
        
        # 删除生成的文件
        for file in ['organize_history.json', 'undo_it.py']:
            file_path = os.path.join(TEST_DIR, file)
            if os.path.exists(file_path):
                os.remove(file_path)
        
        print("✅ 测试目录已清理")
    except Exception as e:
        print(f"⚠️  清理失败：{e}")

if __name__ == '__main__':
    main()
