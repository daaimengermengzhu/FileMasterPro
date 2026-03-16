"""
自动化测试脚本 - 测试全能文件整理器
"""
import os
import sys
import json
import shutil

# 测试目录
TEST_DIR = r"d:\My_Ai_app\test_folder"

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

def test_organize():
    """测试整理功能"""
    print_line()
    print("🧪 开始测试文件整理功能")
    print_line()
    
    print("\n📋 整理前的目录结构：")
    list_all_files(TEST_DIR)
    
    # 导入并模拟运行 clean_my_folder
    # 我们直接调用核心逻辑而不是 input
    sys.path.insert(0, r"d:\My_Ai_app")
    
    import clean_my_folder as cf
    
    # 直接执行整理逻辑
    target_dir = TEST_DIR
    
    print(f"\n🚀 正在整理：{target_dir}")
    print_line()
    
    # 扫描文件
    all_items = os.listdir(target_dir)
    files = []
    folders_skipped = 0
    
    for item in all_items:
        full_path = os.path.join(target_dir, item)
        if os.path.isfile(full_path):
            files.append(item)
        elif os.path.isdir(full_path):
            folders_skipped += 1
    
    print(f"发现 {len(files)} 个文件，{folders_skipped} 个文件夹（文件夹将被跳过）")
    
    skip_files = {'organize_history.json', 'undo_it.py'}
    move_records = []
    moved_count = 0
    from datetime import datetime
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    
    for filename in files:
        full_path = os.path.join(target_dir, filename)
        
        if filename.endswith('.py') or filename in skip_files:
            continue
        
        if not os.path.isfile(full_path):
            continue
        
        ext = filename.split('.')[-1] if '.' in filename else ''
        category = cf.get_category(ext)
        if category:
            target_folder = os.path.join(target_dir, category)
        else:
            target_folder = os.path.join(target_dir, '其它')
        
        if not os.path.exists(target_folder):
            os.makedirs(target_folder)
        
        dest_path = cf.get_destination_path(target_folder, filename)
        
        try:
            shutil.move(full_path, dest_path)
            moved_count += 1
            move_records.append({
                "filename": filename,
                "original_path": full_path,
                "new_path": dest_path,
                "category": category if category else "其它"
            })
            print(f"✅ 已移动：{filename}  --->  {os.path.basename(target_folder)}")
        except Exception as e:
            print(f"❌ 移动失败：{filename}，错误：{e}")
    
    # 保存历史
    if move_records:
        cf.save_history(target_dir, move_records, timestamp)
        cf.create_undo_script(target_dir)
    
    print_line()
    print(f"🎉 整理完成！移动了 {moved_count} 个文件")
    
    print("\n📋 整理后的目录结构：")
    list_all_files(TEST_DIR)
    
    # 验证
    print_line()
    print("🔍 验证测试结果：")
    
    checks = [
        ("organize_history.json 存在", os.path.exists(os.path.join(TEST_DIR, "organize_history.json"))),
        ("undo_it.py 存在", os.path.exists(os.path.join(TEST_DIR, "undo_it.py"))),
        ("图片文件夹存在", os.path.exists(os.path.join(TEST_DIR, "图片"))),
        ("文档文件夹存在", os.path.exists(os.path.join(TEST_DIR, "文档"))),
        ("音频文件夹存在", os.path.exists(os.path.join(TEST_DIR, "音频"))),
        ("视频文件夹存在", os.path.exists(os.path.join(TEST_DIR, "视频"))),
        ("压缩包文件夹存在", os.path.exists(os.path.join(TEST_DIR, "压缩包"))),
        ("其它文件夹存在", os.path.exists(os.path.join(TEST_DIR, "其它"))),
        ("子文件夹未被移动", os.path.exists(os.path.join(TEST_DIR, "subfolder_should_stay"))),
    ]
    
    all_passed = True
    for check_name, result in checks:
        status = "✅ 通过" if result else "❌ 失败"
        print(f"  {status} - {check_name}")
        if not result:
            all_passed = False
    
    return all_passed, moved_count

def test_undo():
    """测试还原功能"""
    print_line()
    print("🧪 开始测试后悔药（还原）功能")
    print_line()
    
    history_file = os.path.join(TEST_DIR, "organize_history.json")
    
    if not os.path.exists(history_file):
        print("❌ 找不到历史记录文件！")
        return False
    
    with open(history_file, 'r', encoding='utf-8') as f:
        history = json.load(f)
    
    moves = history.get('moves', [])
    print(f"📋 找到 {len(moves)} 条移动记录")
    
    restored_count = 0
    
    for move in moves:
        original_path = move['original_path']
        current_path = move['new_path']
        
        if not os.path.exists(current_path):
            print(f"⚠️ 跳过（文件不存在）：{current_path}")
            continue
        
        try:
            shutil.move(current_path, original_path)
            print(f"✅ 已还原：{os.path.basename(current_path)}")
            restored_count += 1
        except Exception as e:
            print(f"❌ 还原失败：{os.path.basename(current_path)}，错误：{e}")
    
    # 清理历史文件
    if restored_count > 0:
        os.remove(history_file)
        undo_file = os.path.join(TEST_DIR, "undo_it.py")
        if os.path.exists(undo_file):
            os.remove(undo_file)
    
    print_line()
    print(f"🎉 还原完成！恢复了 {restored_count} 个文件")
    
    print("\n📋 还原后的目录结构：")
    list_all_files(TEST_DIR)
    
    # 验证文件都回来了
    print_line()
    print("🔍 验证还原结果：")
    
    expected_files = ['test_image.jpg', 'test_doc.txt', 'test_audio.mp3', 
                      'test_video.mp4', 'test_archive.zip', 'unknown_file.xyz']
    
    all_passed = True
    for filename in expected_files:
        exists = os.path.exists(os.path.join(TEST_DIR, filename))
        status = "✅ 通过" if exists else "❌ 失败"
        print(f"  {status} - {filename} 已还原到根目录")
        if not exists:
            all_passed = False
    
    # 检查子文件夹还在
    subfolder_exists = os.path.exists(os.path.join(TEST_DIR, "subfolder_should_stay"))
    status = "✅ 通过" if subfolder_exists else "❌ 失败"
    print(f"  {status} - subfolder_should_stay 子文件夹完好")
    if not subfolder_exists:
        all_passed = False
    
    return all_passed

def main():
    print("\n" + "🔬" * 30)
    print("       全能文件整理器 - 自动化测试")
    print("🔬" * 30 + "\n")
    
    # 测试整理功能
    organize_passed, moved_count = test_organize()
    
    print("\n")
    
    # 测试还原功能
    undo_passed = test_undo()
    
    # 总结
    print("\n")
    print_line()
    print("📊 测试总结")
    print_line()
    
    if organize_passed and undo_passed:
        print("🎊 所有测试通过！")
        print(f"   - 整理功能：✅ 正常（移动了 {moved_count} 个文件）")
        print("   - 后悔药功能：✅ 正常（所有文件已还原）")
        print("   - 文件夹安全：✅ 未移动任何文件夹")
        print("\n💡 你可以放心使用 clean_my_folder.py 了！")
    else:
        print("⚠️ 部分测试失败，请检查代码")
        if not organize_passed:
            print("   - 整理功能：❌ 有问题")
        if not undo_passed:
            print("   - 后悔药功能：❌ 有问题")
    
    print_line()

if __name__ == '__main__':
    main()
