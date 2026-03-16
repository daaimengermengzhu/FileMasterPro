"""
全能文件整理器 - 带后悔药版本（支持深度扫描 + 演习模式 + 回收站功能）
功能：
1. 运行时提示输入文件夹路径
2. 深度扫描所有子文件夹（可配置白名单）
3. 只移动文件，绝不移动文件夹
4. 移动前生成 organize_history.json 记录所有文件去向
5. 自动创建 undo_it.py 后悔药脚本
6. 统计展示扫描深度和移动数量
7. 演习模式：只预览不执行
8. 智能白名单：保护关键系统文件
9. 清理建议：识别大文件安装包
10. 垃圾文件回收站：将 .log, .tmp 等文件移动到回收站而不是直接删除
"""
import os
import shutil
import json
from datetime import datetime
import send2trash

# 全能文件整理器配置
CATEGORY_DICT = {
    '图片': ['jpg', 'jpeg', 'png', 'gif', 'webp', 'bmp', 'ico'],
    '文档': ['pdf', 'doc', 'docx', 'txt', 'ppt', 'pptx', 'xls', 'xlsx', 'csv'],
    '安装包': ['exe', 'msi', 'iso', 'dmg', 'apk'],
    '压缩包': ['zip', 'rar', '7z', 'tar', 'gz'],
    '视频': ['mp4', 'mkv', 'avi', 'mov', 'flv'],
    '音频': ['mp3', 'wav', 'flac', 'm4a'],
    '电子书': ['epub', 'mobi', 'azw3'],
    '代码相关': ['html', 'css', 'js', 'bat', 'sh'],
    '设计与字体': ['psd', 'ai', 'ttf', 'otf', 'svg'],
    '日志与临时文件': ['log', 'tmp', 'bak', 'old', 'temp', 'dmp']
}

# 安全白名单：禁止扫描的文件夹（防止破坏软件或游戏）
EXCLUDE_FOLDERS = {
    'node_modules',    # Node.js 依赖
    '.git',            # Git 仓库
    'venv',            # Python 虚拟环境
    '__pycache__',     # Python 缓存
    '.idea',           # IDE 配置
    '.vscode',         # VSCode 配置
    'dist',            # 构建输出
    'build',           # 构建输出
    'target',          # Maven 构建输出
    'bin',             # 二进制文件
    'obj',             # .NET 编译输出
    'Debug',           # 调试输出
    'Release',         # 发布输出
    'packages',        # NuGet 包
    'logs',            # 日志文件夹
    'temp',            # 临时文件夹
    'tmp',             # 临时文件夹,
    'Program Files',   # Windows 程序文件
    'Program Files (x86)',  # Windows 32位程序文件
    'Windows',         # Windows 系统文件夹
    'System32',        # Windows 系统文件
    'AppData',         # 应用程序数据
    'Local Settings',  # 本地设置
}

# 关键系统文件：绝对禁止移动的文件名关键词
CRITICAL_FILE_KEYWORDS = {
    'steam_api',       # Steam API 文件
    'dll',             # 动态链接库
    'manifest',        # 清单文件
    'node',            # Node.js 相关
    'cmd',             # 命令文件
    'exe',             # 可执行文件（系统级）
    'sys',             # 系统文件
    'drv',             # 驱动程序
    'ocx',             # ActiveX 控件
    'vxd',             # 虚拟设备驱动程序
    'ini',             # 配置文件
    'cfg',             # 配置文件
    'config',          # 配置文件
    'registry',        # 注册表文件
    'boot',            # 启动文件
    'kernel',          # 内核文件
    'system',          # 系统文件
    'windows',         # Windows 文件
    'mscore',          # .NET 核心文件
    'framework',       # 框架文件
    'runtime',         # 运行时文件
}

# 生成扩展名到类别的快速索引
EXT_TO_CATEGORY = {}
for category, exts in CATEGORY_DICT.items():
    for ext in exts:
        EXT_TO_CATEGORY[ext.lower()] = category

# 后悔药脚本模板（升级版，支持深层还原）
UNDO_SCRIPT_TEMPLATE = '''"""
后悔药脚本 - 一键还原所有文件（支持深层还原）
自动生成于: {timestamp}
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
        print(f"读取历史记录失败：{{e}}")
        return
    
    moves = history.get('moves', [])
    if not moves:
        print("历史记录为空，没有文件需要还原。")
        return
    
    print_line()
    print(f"找到 {{len(moves)}} 条移动记录")
    print(f"整理时间：{{history.get('timestamp', '未知')}}")
    print(f"扫描深度：{{history.get('max_depth', 0)}} 层")
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
            print(f"跳过（文件不存在）：{{current_path}}")
            failed_count += 1
            continue
        
        # 确保原始目录存在（支持深层目录）
        original_dir = os.path.dirname(original_path)
        if original_dir and not os.path.exists(original_dir):
            try:
                os.makedirs(original_dir)
                print(f"📁 创建目录：{{original_dir}}")
            except Exception as e:
                print(f"创建目录失败：{{original_dir}}，错误：{{e}}")
                failed_count += 1
                continue
        
        try:
            shutil.move(current_path, original_path)
            print(f"✅ 已还原：{{os.path.basename(current_path)}}")
            restored_count += 1
        except Exception as e:
            print(f"❌ 还原失败：{{os.path.basename(current_path)}}，错误：{{e}}")
            failed_count += 1
    
    print_line()
    print(f"还原完成！成功：{{restored_count}} 个，失败：{{failed_count}} 个")
    
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
'''

# ========================
def print_line():
    print("=" * 50)

def safe_print(text):
    """安全打印，避免 Unicode 编码错误"""
    # 移除所有 Unicode 表情符号
    cleaned = text
    # 替换常见的 Unicode 表情符号为简单文本
    replacements = {
        '🗂️': '[文件夹]',
        '🔬': '[演习]',
        '📁': '[目录]',
        '🔍': '[扫描]',
        '📊': '[统计]',
        '🛡️': '[保护]',
        '💡': '[提示]',
        '🎉': '[完成]',
        '💊': '[后悔药]',
        '📝': '[历史]',
        '🗑️': '[回收站]',
        '⏭️': '[跳过]',
        '⚠️': '[警告]',
        '❌': '[错误]',
        '✅': '[成功]'
    }
    for emoji, replacement in replacements.items():
        cleaned = cleaned.replace(emoji, replacement)
    print(cleaned)

def get_destination_path(folder, filename):
    """
    智能处理命名冲突。如果目标文件夹下已存在同名文件，则在文件名结尾加_1, _2等数字。
    """
    base, ext = os.path.splitext(filename)
    counter = 1
    dest_path = os.path.join(folder, filename)
    while os.path.exists(dest_path):
        dest_path = os.path.join(folder, f"{base}_{counter}{ext}")
        counter += 1
    return dest_path

def get_category(ext):
    """根据扩展名获取类别"""
    return EXT_TO_CATEGORY.get(ext.lower())

def human_size(size):
    """将文件大小转换成更易读的形式"""
    for unit in ['B','KB','MB','GB','TB']:
        if size < 1024:
            return f"{size:.2f}{unit}"
        size /= 1024
    return f"{size:.2f}PB"

def is_excluded_folder(folder_name, full_path="", user_exclude_folders=None):
    """检查文件夹是否在排除列表中"""
    if user_exclude_folders is None:
        user_exclude_folders = set()
    
    # 合并默认排除和用户自定义排除
    all_exclude_folders = EXCLUDE_FOLDERS.union(user_exclude_folders)
    
    # 检查文件夹名是否在排除列表中
    if folder_name in all_exclude_folders:
        return True
    
    # 检查文件夹路径是否包含排除的父文件夹
    if full_path:
        for excluded in all_exclude_folders:
            if excluded in full_path:
                return True
    
    return False

def is_critical_file(filename):
    """检查文件是否为关键系统文件"""
    filename_lower = filename.lower()
    for keyword in CRITICAL_FILE_KEYWORDS:
        if keyword in filename_lower:
            return True
    return False

def scan_files_recursively(root_dir, user_exclude_folders=None, current_depth=0, max_depth=0):
    """
    递归扫描所有文件，跳过排除的文件夹
    返回：(文件列表, 扫描的文件夹数量, 最大深度)
    """
    all_files = []
    folders_scanned = 0
    max_depth_reached = max(max_depth, current_depth)
    
    try:
        items = os.listdir(root_dir)
    except PermissionError:
        print(f"⚠️  权限不足，跳过目录：{root_dir}")
        return all_files, folders_scanned, max_depth_reached
    except Exception as e:
        print(f"⚠️  扫描目录失败：{root_dir}，错误：{e}")
        return all_files, folders_scanned, max_depth_reached
    
    for item in items:
        full_path = os.path.join(root_dir, item)
        
        if os.path.isfile(full_path):
            all_files.append(full_path)
        elif os.path.isdir(full_path):
            folders_scanned += 1
            
            # 检查是否在排除列表中
            if is_excluded_folder(item, full_path, user_exclude_folders):
                print(f"⏭️  跳过排除文件夹：{item}")
                continue
            
            # 递归扫描子文件夹
            sub_files, sub_folders, sub_max_depth = scan_files_recursively(
                full_path, user_exclude_folders, current_depth + 1, max_depth_reached
            )
            all_files.extend(sub_files)
            folders_scanned += sub_folders
            max_depth_reached = max(max_depth_reached, sub_max_depth)
    
    return all_files, folders_scanned, max_depth_reached

def create_undo_script(target_dir):
    """在目标目录创建后悔药脚本"""
    undo_path = os.path.join(target_dir, "undo_it.py")
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    script_content = UNDO_SCRIPT_TEMPLATE.format(timestamp=timestamp)
    
    try:
        with open(undo_path, 'w', encoding='utf-8') as f:
            f.write(script_content)
        return True
    except Exception as e:
        print(f"创建后悔药脚本失败：{e}")
        return False

def save_history(target_dir, moves, timestamp, max_depth):
    """保存移动历史到 JSON 文件"""
    history_path = os.path.join(target_dir, "organize_history.json")
    history_data = {
        "timestamp": timestamp,
        "total_moves": len(moves),
        "max_depth": max_depth,
        "moves": moves
    }
    
    try:
        with open(history_path, 'w', encoding='utf-8') as f:
            json.dump(history_data, f, ensure_ascii=False, indent=2)
        return True
    except Exception as e:
        print(f"保存历史记录失败：{e}")
        return False

def main():
    print_line()
    safe_print("🗂️  全能文件整理器 - 深度扫描版 + 演习模式")
    print_line()
    
    # 询问是否开启演习模式
    safe_print("💡 演习模式：只预览整理结果，不实际移动文件")
    drill_mode_input = input("是否开启演习模式？(y/n): ").strip().lower()
    drill_mode = drill_mode_input == 'y'
    
    if drill_mode:
        safe_print("🔬 演习模式已开启 - 只预览不执行")
    
    # 提示用户输入文件夹路径
    target_dir = input("请输入要整理的文件夹完整路径：").strip()
    
    # 去除可能的引号
    target_dir = target_dir.strip('"').strip("'")
    
    # 验证路径
    if not target_dir:
        print("错误：路径不能为空！")
        return
    
    if not os.path.exists(target_dir):
        print(f"错误：路径不存在 - {target_dir}")
        return
    
    if not os.path.isdir(target_dir):
        print(f"错误：这不是一个文件夹 - {target_dir}")
        return
    
    # 询问是否要添加自定义排除文件夹
    safe_print("\n💡 默认排除的文件夹：node_modules, .git, venv, __pycache__ 等")
    custom_exclude = input("请输入要额外排除的文件夹名（多个用逗号分隔，直接回车跳过）：").strip()
    
    # 处理自定义排除
    user_exclude_folders = set()
    if custom_exclude:
        for folder in custom_exclude.split(','):
            folder = folder.strip()
            if folder:
                user_exclude_folders.add(folder)
        
        if user_exclude_folders:
            safe_print(f"✅ 已添加排除文件夹：{', '.join(user_exclude_folders)}")
    
    print_line()
    safe_print(f"📁 整理目录：{target_dir}")
    if drill_mode:
        safe_print("🔬 当前模式：演习模式（只预览不执行）")
    print_line()
    
    # 深度扫描所有文件
    safe_print("🔍 正在深度扫描文件...")
    all_files, folders_scanned, max_depth = scan_files_recursively(target_dir, user_exclude_folders)
    
    safe_print(f"📊 扫描统计：")
    safe_print(f"   - 扫描文件夹：{folders_scanned} 个")
    safe_print(f"   - 扫描深度：{max_depth} 层")
    safe_print(f"   - 发现文件：{len(all_files)} 个")
    
    if not all_files:
        safe_print("没有需要整理的文件。")
        return
    
    # 跳过的特殊文件
    skip_files = {'organize_history.json', 'undo_it.py'}
    
    large_files = []
    critical_files = []  # 关键系统文件
    install_package_suggestions = []  # 安装包清理建议
    move_records = []  # 记录所有移动操作
    trash_files = []  # 记录移动到回收站的文件
    moved_count = 0
    deep_moved_count = 0  # 深层文件计数
    trash_count = 0  # 移动到回收站的文件计数
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    
    for file_path in all_files:
        filename = os.path.basename(file_path)
        relative_path = os.path.relpath(file_path, target_dir)
        
        # 跳过 .py 文件和特殊文件
        if filename.endswith('.py') or filename in skip_files:
            continue
        
        # 再次确认是文件（安全白名单：绝对不移动文件夹！）
        if not os.path.isfile(file_path):
            continue
        
        # 超大文件分析
        try:
            file_size = os.stat(file_path).st_size
        except Exception as e:
            print(f"⚠️  无法读取文件大小：{relative_path}，错误：{e}")
            continue
        
        # 检查是否为关键系统文件
        if is_critical_file(filename):
            critical_files.append((relative_path, file_size))
            if not drill_mode:
                print(f"🛡️  保护关键系统文件：{relative_path}")
            continue
        
        # 检查大文件安装包（超过500MB的.exe或.zip文件）
        if file_size >= 500*1024*1024:
            ext = filename.split('.')[-1].lower() if '.' in filename else ''
            if ext in ['exe', 'zip', 'rar', '7z', 'iso', 'dmg']:
                install_package_suggestions.append((relative_path, file_size, ext))
        
        if file_size >= 100*1024*1024:
            large_files.append((relative_path, file_size))
        
        # 获取扩展名和目标类别
        ext = filename.split('.')[-1] if '.' in filename else ''
        category = get_category(ext)
        
        # 检查是否为垃圾文件（日志与临时文件）
        is_trash_file = category == '日志与临时文件'
        
        if category and not is_trash_file:
            target_folder = os.path.join(target_dir, category)
        else:
            target_folder = os.path.join(target_dir, '其它')
        
        # 创建目标目录（演习模式下不创建，垃圾文件不需要创建目录）
        if not drill_mode and not is_trash_file and not os.path.exists(target_folder):
            try:
                os.makedirs(target_folder)
            except Exception as e:
                print(f"❌ 创建文件夹失败：{target_folder}, 错误：{e}")
                continue
        
        # 处理目标目录同名文件（仅对非垃圾文件）
        dest_filename = filename
        # 如果文件来自深层目录，保留部分路径信息避免重名
        if os.path.dirname(relative_path) != '.':
            # 使用下划线替换路径分隔符
            safe_name = relative_path.replace('\\', '_').replace('/', '_')
            dest_filename = safe_name
        
        dest_path = get_destination_path(target_folder, dest_filename) if not is_trash_file else None
        
        if drill_mode:
            # 演习模式：只显示预览
            if is_trash_file:
                # 垃圾文件预览：移动到回收站
                if os.path.dirname(relative_path) == '.':
                    print(f"🗑️  预览删除（回收站）：{filename}")
                else:
                    print(f"🗑️  预览删除（回收站，深层）：{relative_path}")
            else:
                # 普通文件预览：移动到分类文件夹
                if os.path.dirname(relative_path) == '.':
                    print(f"🔍 预览移动：{filename}  --->  {os.path.basename(target_folder)}")
                else:
                    print(f"🔍 预览移动（深层）：{relative_path}  --->  {os.path.basename(target_folder)}")
            
            # 演习模式下也记录移动操作（用于统计）
            if not is_trash_file:
                move_records.append({
                    "filename": filename,
                    "original_path": file_path,
                    "new_path": dest_path,
                    "category": category if category else "其它",
                    "relative_path": relative_path,
                    "drill_mode": True
                })
                moved_count += 1
            else:
                trash_count += 1
                trash_files.append({
                    "filename": filename,
                    "original_path": file_path,
                    "relative_path": relative_path,
                    "size": file_size
                })
            
            # 统计深层文件
            if os.path.dirname(relative_path) != '.':
                if is_trash_file:
                    # 深层垃圾文件已计入 trash_count
                    pass
                else:
                    deep_moved_count += 1
        else:
            # 实际执行模式
            if is_trash_file:
                # 垃圾文件：移动到回收站
                try:
                    send2trash.send2trash(file_path)
                    trash_count += 1
                    trash_files.append({
                        "filename": filename,
                        "original_path": file_path,
                        "relative_path": relative_path,
                        "size": file_size
                    })
                    
                    # 显示删除信息
                    if os.path.dirname(relative_path) == '.':
                        print(f"🗑️  已删除（回收站）：{filename}")
                    else:
                        print(f"🗑️  已删除（回收站，深层）：{relative_path}")
                except Exception as e:
                    print(f"❌ 移动到回收站失败：{relative_path}，错误：{e}")
            else:
                # 普通文件：移动到分类文件夹
                try:
                    shutil.move(file_path, dest_path)
                    moved_count += 1
                    
                    # 统计深层文件
                    if os.path.dirname(relative_path) != '.':
                        deep_moved_count += 1
                    
                    # 记录移动操作
                    move_records.append({
                        "filename": filename,
                        "original_path": file_path,
                        "new_path": dest_path,
                        "category": category if category else "其它",
                        "relative_path": relative_path,
                        "drill_mode": False
                    })
                    
                    # 显示移动信息
                    if os.path.dirname(relative_path) == '.':
                        print(f"✅ 已移动：{filename}  --->  {os.path.basename(target_folder)}")
                    else:
                        print(f"✅ 已移动（深层）：{relative_path}  --->  {os.path.basename(target_folder)}")
                except Exception as e:
                    print(f"❌ 移动文件失败：{relative_path}，错误：{e}")
    
    print_line()
    
    # 保存历史记录（演习模式下不保存）
    if move_records and not drill_mode:
        if save_history(target_dir, move_records, timestamp, max_depth):
            print("📝 已生成移动历史：organize_history.json")
        
        # 创建后悔药脚本
        if create_undo_script(target_dir):
            print("💊 已创建后悔药脚本：undo_it.py")
    
    print_line()
    print("📊 统计报告：")
    print(f"   - 扫描文件夹：{folders_scanned} 个")
    print(f"   - 扫描深度：{max_depth} 层")
    print(f"   - 移动文件总数：{moved_count} 个")
    print(f"   - 其中深层文件：{deep_moved_count} 个")
    print(f"   - 移动到回收站：{trash_count} 个")
    
    # 显示关键系统文件保护情况
    if critical_files:
        print_line()
        print("🛡️  关键系统文件保护：")
        print(f"   - 保护了 {len(critical_files)} 个关键系统文件")
        for fname, fsize in critical_files[:5]:  # 只显示前5个
            print(f"   {fname}   |   大小: {human_size(fsize)}")
        if len(critical_files) > 5:
            print(f"   ... 还有 {len(critical_files) - 5} 个关键文件被保护")
    
    # 显示安装包清理建议
    if install_package_suggestions:
        print_line()
        print("💡 安装包清理建议（超过500MB）：")
        for fname, fsize, ext in install_package_suggestions:
            print(f"   \033[93m[疑似安装包，建议安装后删除]\033[0m {fname}   |   大小: {human_size(fsize)}")
    
    print_line()
    print("📊 超过100MB的大文件：")
    if large_files:
        for fname, fsize in large_files:
            print(f"   {fname}   |   大小: {human_size(fsize)}")
    else:
        print("   无")
    
    print_line()
    if drill_mode:
        print(f"🔬 演习模式完成！预览了 {moved_count} 个文件的移动计划")
        print(f"💡 提示：如需实际执行，请重新运行脚本并选择 'n' 关闭演习模式")
    else:
        print(f"🎉 整理完成！")
        if moved_count > 0:
            print(f"\n💡 提示：如需撤销，请运行 {target_dir}\\undo_it.py")
    
    print_line()

if __name__ == '__main__':
    main()
