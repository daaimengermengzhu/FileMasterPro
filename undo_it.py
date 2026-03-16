"""
后悔药脚本 - 一键还原所有文件（支持深层还原）
自动生成于: 2026-03-16 09:53:56
"""
import os
import json
import shutil

def print_line():
    print("=" * 50)

def main():
    # 获取本脚本所在目录
    base_dir = os.path.dirname(os.path.abspath(__file__))
    history_file = os.path.join(base_dir, "organize_history.json")
    
    if not os.path.exists(history_file):
        print("错误：找不到 organize_history.json 文件！")
        print("没有可以还原的记录。")
        return
    
    try:
        with open(history_file, 'r', encoding='utf-8') as f:
            history = json.load(f)
    except Exception as e:
        print(f"读取历史记录失败：{e}")
        return
    
    moves = history.get('moves', [])
    if not moves:
        print("历史记录为空，没有文件需要还原。")
        return
    
    print_line()
    print(f"找到 {len(moves)} 条移动记录")
    print(f"整理时间：{history.get('timestamp', '未知')}")
    print(f"扫描深度：{history.get('max_depth', 0)} 层")
    print_line()
    
    confirm = input("确定要还原所有文件吗？(y/n): ").strip().lower()
    if confirm != 'y':
        print("操作已取消。")
        return
    
    restored_count = 0
    failed_count = 0
    
    for move in moves:
        original_path = move['original_path']
        current_path = move['new_path']
        
        if not os.path.exists(current_path):
            print(f"跳过（文件不存在）：{current_path}")
            failed_count += 1
            continue
        
        # 确保原始目录存在（支持深层目录）
        original_dir = os.path.dirname(original_path)
        if original_dir and not os.path.exists(original_dir):
            try:
                os.makedirs(original_dir)
                print(f"📁 创建目录：{original_dir}")
            except Exception as e:
                print(f"创建目录失败：{original_dir}，错误：{e}")
                failed_count += 1
                continue
        
        try:
            shutil.move(current_path, original_path)
            print(f"✅ 已还原：{os.path.basename(current_path)}")
            restored_count += 1
        except Exception as e:
            print(f"❌ 还原失败：{os.path.basename(current_path)}，错误：{e}")
            failed_count += 1
    
    print_line()
    print(f"还原完成！成功：{restored_count} 个，失败：{failed_count} 个")
    
    # 删除历史记录文件
    if restored_count > 0 and failed_count == 0:
        try:
            os.remove(history_file)
            print("已清理历史记录文件。")
        except:
            pass
    
    print_line()

if __name__ == '__main__':
    main()
