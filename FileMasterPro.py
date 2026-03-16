"""
FileMasterPro - 商业级文件整理软件
现代化 GUI 界面，整合深度扫描、演习模式、白名单保护、回收站和一键撤销功能
"""

import os
import shutil
import json
import threading
import queue
import time
from datetime import datetime
from pathlib import Path
import send2trash
import customtkinter as ctk
from tkinter import filedialog, messagebox, scrolledtext
import tkinter as tk

# ======================== 配置常量 ========================
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

# 强力白名单：绝对不处理的文件夹（包含以下关键词的文件夹）
POWERFUL_EXCLUDE_KEYWORDS = {
    'SteamLibrary',    # Steam 游戏库
    'Windows',         # Windows 系统文件夹
    'Program Files',   # Windows 程序文件
    'Program Files (x86)',  # Windows 32位程序文件
    'Users',           # 用户文件夹
    'anaconda',        # Anaconda 环境
    'node_modules',    # Node.js 依赖
    '.git',            # Git 仓库
    'AppData',         # 应用程序数据
    'System32',        # Windows 系统文件
    'Local Settings',  # 本地设置
    'ProgramData',     # 程序数据
    'WindowsApps',     # Windows 应用
    'Microsoft',       # Microsoft 相关
    'Intel',           # Intel 相关
    'AMD',             # AMD 相关
    'NVIDIA',          # NVIDIA 相关
    'Temp',            # 临时文件夹
    'TEMP',            # 临时文件夹
    'tmp',             # 临时文件夹
    'temp',            # 临时文件夹
}

# 安全白名单：禁止扫描的文件夹
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

# 关键后缀保护：需要二次确认或默认不移动的文件后缀
CRITICAL_EXTENSIONS = {
    'dll',             # 动态链接库
    'sys',             # 系统文件
    'exe',             # 可执行文件
    'ocx',             # ActiveX 控件
    'vxd',             # 虚拟设备驱动程序
    'drv',             # 驱动程序
    'ini',             # 配置文件
    'cfg',             # 配置文件
    'config',          # 配置文件
    'manifest',        # 清单文件
    'msi',             # Windows 安装程序
    'bat',             # 批处理文件
    'cmd',             # 命令文件
    'ps1',             # PowerShell 脚本
    'sh',              # Shell 脚本
    'reg',             # 注册表文件
    'inf',             # 安装信息文件
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

# ======================== 核心功能类 ========================
class FileOrganizer:
    def __init__(self, log_callback=None):
        self.log_callback = log_callback
        self.is_running = False
        self.current_task = None
        self.move_records = []
        self.trash_files = []
        self.critical_files = []
        self.large_files = []
        self.install_package_suggestions = []
        
    def log(self, message):
        """记录日志"""
        if self.log_callback:
            self.log_callback(message)
        else:
            print(message)
    
    def get_category(self, ext):
        """根据扩展名获取类别"""
        return EXT_TO_CATEGORY.get(ext.lower())
    
    def human_size(self, size):
        """将文件大小转换成更易读的形式"""
        for unit in ['B','KB','MB','GB','TB']:
            if size < 1024:
                return f"{size:.2f}{unit}"
            size /= 1024
        return f"{size:.2f}PB"
    
    def is_excluded_folder(self, folder_name, full_path="", user_exclude_folders=None):
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
    
    def is_powerful_excluded_folder(self, folder_name, full_path=""):
        """检查文件夹是否在强力白名单中（包含关键词的文件夹）"""
        folder_name_lower = folder_name.lower()
        full_path_lower = full_path.lower() if full_path else ""
        
        # 检查文件夹名是否包含强力白名单关键词
        for keyword in POWERFUL_EXCLUDE_KEYWORDS:
            keyword_lower = keyword.lower()
            if keyword_lower in folder_name_lower:
                return True
        
        # 检查完整路径是否包含强力白名单关键词
        if full_path:
            for keyword in POWERFUL_EXCLUDE_KEYWORDS:
                keyword_lower = keyword.lower()
                if keyword_lower in full_path_lower:
                    return True
        
        return False
    
    def is_critical_extension(self, filename):
        """检查文件是否为关键后缀文件（.dll, .sys, .exe 等）"""
        if '.' not in filename:
            return False
        
        ext = filename.split('.')[-1].lower()
        return ext in CRITICAL_EXTENSIONS
    
    def is_critical_file(self, filename):
        """检查文件是否为关键系统文件"""
        filename_lower = filename.lower()
        for keyword in CRITICAL_FILE_KEYWORDS:
            if keyword in filename_lower:
                return True
        return False
    
    def get_destination_path(self, folder, filename):
        """智能处理命名冲突"""
        base, ext = os.path.splitext(filename)
        counter = 1
        dest_path = os.path.join(folder, filename)
        while os.path.exists(dest_path):
            dest_path = os.path.join(folder, f"{base}_{counter}{ext}")
            counter += 1
        return dest_path
    
    def scan_files_recursively(self, root_dir, user_exclude_folders=None, current_depth=0, max_depth=0):
        """递归扫描所有文件，跳过排除的文件夹"""
        all_files = []
        folders_scanned = 0
        max_depth_reached = max(max_depth, current_depth)
        
        try:
            items = os.listdir(root_dir)
        except PermissionError:
            self.log(f"⚠️ 权限不足，跳过目录：{root_dir}")
            return all_files, folders_scanned, max_depth_reached
        except Exception as e:
            self.log(f"⚠️ 扫描目录失败：{root_dir}，错误：{e}")
            return all_files, folders_scanned, max_depth_reached
        
        for item in items:
            full_path = os.path.join(root_dir, item)
            
            if os.path.isfile(full_path):
                all_files.append(full_path)
            elif os.path.isdir(full_path):
                folders_scanned += 1
                
                # 检查是否在排除列表中
                if self.is_excluded_folder(item, full_path, user_exclude_folders):
                    self.log(f"⏭️ 跳过排除文件夹：{item}")
                    continue
                
                # 递归扫描子文件夹
                sub_files, sub_folders, sub_max_depth = self.scan_files_recursively(
                    full_path, user_exclude_folders, current_depth + 1, max_depth_reached
                )
                all_files.extend(sub_files)
                folders_scanned += sub_folders
                max_depth_reached = max(max_depth_reached, sub_max_depth)
        
        return all_files, folders_scanned, max_depth_reached
    
    def create_undo_script(self, target_dir):
        """在目标目录创建后悔药脚本"""
        undo_path = os.path.join(target_dir, "undo_it.py")
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        
        script_content = f'''"""
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
        
        try:
            with open(undo_path, 'w', encoding='utf-8') as f:
                f.write(script_content)
            return True
        except Exception as e:
            self.log(f"创建后悔药脚本失败：{e}")
            return False
    
    def save_history(self, target_dir, moves, timestamp, max_depth):
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
            self.log(f"保存历史记录失败：{e}")
            return False
    
    def organize_files(self, target_dir, drill_mode=False, deep_scan=True, user_exclude_folders=None):
        """整理文件的核心方法"""
        if self.is_running:
            self.log("⚠️ 已有任务正在运行，请等待完成")
            return False
        
        self.is_running = True
        self.move_records = []
        self.trash_files = []
        self.critical_files = []
        self.large_files = []
        self.install_package_suggestions = []
        
        try:
            # 验证路径
            if not target_dir or not os.path.exists(target_dir):
                self.log("❌ 错误：路径不存在或为空")
                return False
            
            if not os.path.isdir(target_dir):
                self.log("❌ 错误：这不是一个文件夹")
                return False
            
            self.log("=" * 50)
            self.log("🚀 FileMasterPro - 开始智能整理")
            self.log(f"📁 整理目录：{target_dir}")
            if drill_mode:
                self.log("🔬 当前模式：演习模式（只预览不执行）")
            if deep_scan:
                self.log("🔍 深度扫描模式：开启")
            self.log("=" * 50)
            
            # 深度扫描所有文件
            self.log("🔍 正在深度扫描文件...")
            all_files, folders_scanned, max_depth = self.scan_files_recursively(
                target_dir, user_exclude_folders
            )
            
            self.log(f"📊 扫描统计：")
            self.log(f"   - 扫描文件夹：{folders_scanned} 个")
            self.log(f"   - 扫描深度：{max_depth} 层")
            self.log(f"   - 发现文件：{len(all_files)} 个")
            
            if not all_files:
                self.log("📭 没有需要整理的文件。")
                return True
            
            # 跳过的特殊文件
            skip_files = {'organize_history.json', 'undo_it.py'}
            
            moved_count = 0
            deep_moved_count = 0
            trash_count = 0
            timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            
            for file_path in all_files:
                if not self.is_running:
                    self.log("⏹️ 任务被用户中断")
                    break
                
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
                    self.log(f"⚠️ 无法读取文件大小：{relative_path}，错误：{e}")
                    continue
                
                # 检查是否为关键系统文件
                if self.is_critical_file(filename):
                    self.critical_files.append((relative_path, file_size))
                    if not drill_mode:
                        self.log(f"🛡️ 保护关键系统文件：{relative_path}")
                    continue
                
                # 检查大文件安装包（超过500MB的.exe或.zip文件）
                if file_size >= 500*1024*1024:
                    ext = filename.split('.')[-1].lower() if '.' in filename else ''
                    if ext in ['exe', 'zip', 'rar', '7z', 'iso', 'dmg']:
                        self.install_package_suggestions.append((relative_path, file_size, ext))
                
                if file_size >= 100*1024*1024:
                    self.large_files.append((relative_path, file_size))
                
                # 获取扩展名和目标类别
                ext = filename.split('.')[-1] if '.' in filename else ''
                category = self.get_category(ext)
                
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
                        self.log(f"❌ 创建文件夹失败：{target_folder}, 错误：{e}")
                        continue
                
                # 处理目标目录同名文件（仅对非垃圾文件）
                dest_filename = filename
                # 如果文件来自深层目录，保留部分路径信息避免重名
                if os.path.dirname(relative_path) != '.':
                    # 使用下划线替换路径分隔符
                    safe_name = relative_path.replace('\\', '_').replace('/', '_')
                    dest_filename = safe_name
                
                dest_path = self.get_destination_path(target_folder, dest_filename) if not is_trash_file else None
                
                if drill_mode:
                    # 演习模式：只显示预览
                    if is_trash_file:
                        # 垃圾文件预览：移动到回收站
                        if os.path.dirname(relative_path) == '.':
                            self.log(f"🗑️ 预览删除（回收站）：{filename}")
                        else:
                            self.log(f"🗑️ 预览删除（回收站，深层）：{relative_path}")
                    else:
                        # 普通文件预览：移动到分类文件夹
                        if os.path.dirname(relative_path) == '.':
                            self.log(f"🔍 预览移动：{filename}  --->  {os.path.basename(target_folder)}")
                        else:
                            self.log(f"🔍 预览移动（深层）：{relative_path}  --->  {os.path.basename(target_folder)}")
                    
                    # 演习模式下也记录移动操作（用于统计）
                    if not is_trash_file:
                        self.move_records.append({
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
                        self.trash_files.append({
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
                            self.trash_files.append({
                                "filename": filename,
                                "original_path": file_path,
                                "relative_path": relative_path,
                                "size": file_size
                            })
                            
                            # 显示删除信息
                            if os.path.dirname(relative_path) == '.':
                                self.log(f"🗑️ 已删除（回收站）：{filename}")
                            else:
                                self.log(f"🗑️ 已删除（回收站，深层）：{relative_path}")
                        except Exception as e:
                            self.log(f"❌ 移动到回收站失败：{relative_path}，错误：{e}")
                    else:
                        # 普通文件：移动到分类文件夹
                        try:
                            shutil.move(file_path, dest_path)
                            moved_count += 1
                            
                            # 统计深层文件
                            if os.path.dirname(relative_path) != '.':
                                deep_moved_count += 1
                            
                            # 记录移动操作
                            self.move_records.append({
                                "filename": filename,
                                "original_path": file_path,
                                "new_path": dest_path,
                                "category": category if category else "其它",
                                "relative_path": relative_path,
                                "drill_mode": False
                            })
                            
                            # 显示移动信息
                            if os.path.dirname(relative_path) == '.':
                                self.log(f"✅ 已移动：{filename}  --->  {os.path.basename(target_folder)}")
                            else:
                                self.log(f"✅ 已移动（深层）：{relative_path}  --->  {os.path.basename(target_folder)}")
                        except Exception as e:
                            self.log(f"❌ 移动文件失败：{relative_path}，错误：{e}")
            
            self.log("=" * 50)
            
            # 保存历史记录（演习模式下不保存）
            if self.move_records and not drill_mode:
                if self.save_history(target_dir, self.move_records, timestamp, max_depth):
                    self.log("📝 已生成移动历史：organize_history.json")
                
                # 创建后悔药脚本
                if self.create_undo_script(target_dir):
                    self.log("💊 已创建后悔药脚本：undo_it.py")
            
            self.log("=" * 50)
            self.log("📊 统计报告：")
            self.log(f"   - 扫描文件夹：{folders_scanned} 个")
            self.log(f"   - 扫描深度：{max_depth} 层")
            self.log(f"   - 移动文件总数：{moved_count} 个")
            self.log(f"   - 其中深层文件：{deep_moved_count} 个")
            self.log(f"   - 移动到回收站：{trash_count} 个")
            
            # 显示关键系统文件保护情况
            if self.critical_files:
                self.log("=" * 50)
                self.log("🛡️ 关键系统文件保护：")
                self.log(f"   - 保护了 {len(self.critical_files)} 个关键系统文件")
                for fname, fsize in self.critical_files[:5]:  # 只显示前5个
                    self.log(f"   {fname}   |   大小: {self.human_size(fsize)}")
                if len(self.critical_files) > 5:
                    self.log(f"   ... 还有 {len(self.critical_files) - 5} 个关键文件被保护")
            
            # 显示安装包清理建议
            if self.install_package_suggestions:
                self.log("=" * 50)
                self.log("💡 安装包清理建议（超过500MB）：")
                for fname, fsize, ext in self.install_package_suggestions:
                    self.log(f"   [疑似安装包，建议安装后删除] {fname}   |   大小: {self.human_size(fsize)}")
            
            self.log("=" * 50)
            self.log("📊 超过100MB的大文件：")
            if self.large_files:
                for fname, fsize in self.large_files:
                    self.log(f"   {fname}   |   大小: {self.human_size(fsize)}")
            else:
                self.log("   无")
            
            self.log("=" * 50)
            if drill_mode:
                self.log(f"🔬 演习模式完成！预览了 {moved_count} 个文件的移动计划")
                self.log(f"💡 提示：如需实际执行，请重新运行并选择关闭演习模式")
            else:
                self.log(f"🎉 整理完成！")
                if moved_count > 0:
                    self.log(f"\n💡 提示：如需撤销，请运行 {target_dir}\\undo_it.py")
            
            self.log("=" * 50)
            
            return True
            
        except Exception as e:
            self.log(f"❌ 整理过程中发生错误：{e}")
            return False
        finally:
            self.is_running = False
    
    def stop(self):
        """停止当前任务"""
        self.is_running = False
        self.log("⏹️ 正在停止任务...")
    
    def gather_root_files(self, target_dir, drill_mode=False):
        """一键归拢功能：识别根目录下的散落文件，统一移动到'根目录待处理_日期'文件夹"""
        if self.is_running:
            self.log("⚠️ 已有任务正在运行，请等待完成")
            return False
        
        self.is_running = True
        
        try:
            # 验证路径
            if not target_dir or not os.path.exists(target_dir):
                self.log("❌ 错误：路径不存在或为空")
                return False
            
            if not os.path.isdir(target_dir):
                self.log("❌ 错误：这不是一个文件夹")
                return False
            
            self.log("=" * 50)
            self.log("📦 FileMasterPro - 一键归拢根目录散落文件")
            self.log(f"📁 目标目录：{target_dir}")
            if drill_mode:
                self.log("🔬 当前模式：演习模式（只预览不执行）")
            self.log("=" * 50)
            
            # 创建归拢文件夹
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            gather_folder_name = f"根目录待处理_{timestamp}"
            gather_folder_path = os.path.join(target_dir, gather_folder_name)
            
            if not drill_mode:
                try:
                    os.makedirs(gather_folder_path, exist_ok=True)
                    self.log(f"📁 创建归拢文件夹：{gather_folder_name}")
                except Exception as e:
                    self.log(f"❌ 创建归拢文件夹失败：{e}")
                    return False
            
            # 扫描根目录下的文件（不包括子文件夹）
            try:
                items = os.listdir(target_dir)
            except PermissionError:
                self.log(f"⚠️ 权限不足，跳过目录：{target_dir}")
                return False
            except Exception as e:
                self.log(f"⚠️ 扫描目录失败：{target_dir}，错误：{e}")
                return False
            
            root_files = []
            for item in items:
                full_path = os.path.join(target_dir, item)
                if os.path.isfile(full_path):
                    root_files.append(full_path)
            
            self.log(f"📊 发现根目录文件：{len(root_files)} 个")
            
            if not root_files:
                self.log("📭 根目录没有散落文件需要归拢。")
                return True
            
            # 跳过的特殊文件
            skip_files = {'organize_history.json', 'undo_it.py'}
            
            moved_count = 0
            critical_count = 0
            
            for file_path in root_files:
                if not self.is_running:
                    self.log("⏹️ 任务被用户中断")
                    break
                
                filename = os.path.basename(file_path)
                
                # 跳过 .py 文件和特殊文件
                if filename.endswith('.py') or filename in skip_files:
                    continue
                
                # 检查是否为关键系统文件
                if self.is_critical_file(filename):
                    self.log(f"🛡️ 保护关键系统文件：{filename}")
                    critical_count += 1
                    continue
                
                # 检查是否为关键后缀文件（.dll, .sys, .exe 等）
                if self.is_critical_extension(filename):
                    self.log(f"🛡️ 保护关键后缀文件：{filename}")
                    critical_count += 1
                    continue
                
                # 检查文件大小
                try:
                    file_size = os.stat(file_path).st_size
                except Exception as e:
                    self.log(f"⚠️ 无法读取文件大小：{filename}，错误：{e}")
                    continue
                
                # 目标路径
                dest_path = os.path.join(gather_folder_path, filename)
                
                if drill_mode:
                    # 演习模式：只显示预览
                    self.log(f"🔍 预览归拢：{filename}  --->  {gather_folder_name}")
                    moved_count += 1
                else:
                    # 实际执行模式
                    try:
                        shutil.move(file_path, dest_path)
                        self.log(f"✅ 已归拢：{filename}  --->  {gather_folder_name}")
                        moved_count += 1
                    except Exception as e:
                        self.log(f"❌ 归拢文件失败：{filename}，错误：{e}")
            
            self.log("=" * 50)
            self.log("📊 归拢统计：")
            self.log(f"   - 扫描文件总数：{len(root_files)} 个")
            self.log(f"   - 成功归拢：{moved_count} 个")
            self.log(f"   - 保护关键文件：{critical_count} 个")
            
            if not drill_mode and moved_count > 0:
                self.log(f"📁 归拢文件夹：{gather_folder_path}")
                self.log(f"💡 提示：请手动检查归拢文件夹中的文件，确认无误后可删除或进一步整理")
            
            self.log("=" * 50)
            if drill_mode:
                self.log(f"🔬 演习模式完成！预览了 {moved_count} 个文件的归拢计划")
            else:
                self.log(f"🎉 一键归拢完成！")
            
            self.log("=" * 50)
            return True
            
        except Exception as e:
            self.log(f"❌ 归拢过程中发生错误：{e}")
            return False
        finally:
            self.is_running = False
    
    def undo_last_operation(self, target_dir):
        """执行撤销操作"""
        undo_script = os.path.join(target_dir, "undo_it.py")
        history_file = os.path.join(target_dir, "organize_history.json")
        
        if not os.path.exists(undo_script):
            self.log("❌ 找不到后悔药脚本：undo_it.py")
            return False
        
        if not os.path.exists(history_file):
            self.log("❌ 找不到历史记录文件：organize_history.json")
            return False
        
        try:
            # 读取历史记录
            with open(history_file, 'r', encoding='utf-8') as f:
                history = json.load(f)
            
            moves = history.get('moves', [])
            if not moves:
                self.log("📭 没有可撤销的操作记录")
                return True
            
            self.log("=" * 50)
            self.log("💊 开始撤销上次操作...")
            self.log(f"找到 {len(moves)} 条移动记录")
            self.log(f"整理时间：{history.get('timestamp', '未知')}")
            self.log(f"扫描深度：{history.get('max_depth', 0)} 层")
            self.log("=" * 50)
            
            restored_count = 0
            failed_count = 0
            
            for move in moves:
                original_path = move['original_path']
                current_path = move['new_path']
                
                if not os.path.exists(current_path):
                    self.log(f"⏭️ 跳过（文件不存在）：{os.path.basename(current_path)}")
                    failed_count += 1
                    continue
                
                # 确保原始目录存在（支持深层目录）
                original_dir = os.path.dirname(original_path)
                if original_dir and not os.path.exists(original_dir):
                    try:
                        os.makedirs(original_dir)
                        self.log(f"📁 创建目录：{original_dir}")
                    except Exception as e:
                        self.log(f"❌ 创建目录失败：{original_dir}，错误：{e}")
                        failed_count += 1
                        continue
                
                try:
                    shutil.move(current_path, original_path)
                    self.log(f"✅ 已还原：{os.path.basename(current_path)}")
                    restored_count += 1
                except Exception as e:
                    self.log(f"❌ 还原失败：{os.path.basename(current_path)}，错误：{e}")
                    failed_count += 1
            
            self.log("=" * 50)
            self.log(f"撤销完成！成功：{restored_count} 个，失败：{failed_count} 个")
            
            # 删除历史记录文件
            if restored_count > 0 and failed_count == 0:
                try:
                    os.remove(history_file)
                    os.remove(undo_script)
                    self.log("已清理历史记录文件和后悔药脚本。")
                except:
                    pass
            
            self.log("=" * 50)
            return True
            
        except Exception as e:
            self.log(f"❌ 撤销过程中发生错误：{e}")
            return False

# ======================== GUI 界面类 ========================
class FileMasterProGUI:
    def __init__(self):
        # 设置主题
        ctk.set_appearance_mode("dark")
        ctk.set_default_color_theme("blue")
        
        # 创建主窗口
        self.root = ctk.CTk()
        self.root.title("FileMasterPro - 商业级文件整理软件")
        self.root.geometry("900x700")
        
        # 文件整理器实例
        self.organizer = FileOrganizer(self.log_message)
        
        # 任务队列和线程
        self.task_queue = queue.Queue()
        self.worker_thread = None
        
        # 创建界面
        self.create_widgets()
        
        # 启动任务处理线程
        self.start_worker_thread()
    
    def log_message(self, message):
        """将日志消息添加到队列中"""
        self.task_queue.put(("log", message))
    
    def start_worker_thread(self):
        """启动后台工作线程"""
        def worker():
            while True:
                try:
                    task_type, data = self.task_queue.get(timeout=0.1)
                    if task_type == "log":
                        self.update_log(data)
                    elif task_type == "task_done":
                        self.on_task_done(data)
                except queue.Empty:
                    continue
        
        self.worker_thread = threading.Thread(target=worker, daemon=True)
        self.worker_thread.start()
    
    def update_log(self, message):
        """更新日志文本框（必须在主线程中调用）"""
        self.root.after(0, self._update_log_ui, message)
    
    def _update_log_ui(self, message):
        """更新日志文本框的UI部分"""
        self.log_text.insert(tk.END, message + "\n")
        self.log_text.see(tk.END)
        self.root.update_idletasks()
    
    def on_task_done(self, success):
        """任务完成回调（必须在主线程中调用）"""
        self.root.after(0, self._on_task_done_ui, success)
    
    def _on_task_done_ui(self, success):
        """任务完成回调的UI部分"""
        self.start_button.configure(state="normal")
        self.gather_button.configure(state="normal")
        self.stop_button.configure(state="disabled")
        self.undo_button.configure(state="normal")
        
        if success:
            messagebox.showinfo("完成", "任务已完成！")
        else:
            messagebox.showwarning("警告", "任务执行过程中出现问题，请查看日志。")
    
    def create_widgets(self):
        """创建所有界面组件"""
        # 主框架
        main_frame = ctk.CTkFrame(self.root)
        main_frame.pack(fill="both", expand=True, padx=20, pady=20)
        
        # 标题
        title_label = ctk.CTkLabel(
            main_frame,
            text="FileMasterPro - 商业级文件整理软件",
            font=("Arial", 24, "bold")
        )
        title_label.pack(pady=(0, 20))
        
        # 路径选择区域
        path_frame = ctk.CTkFrame(main_frame)
        path_frame.pack(fill="x", padx=10, pady=(0, 15))
        
        path_label = ctk.CTkLabel(
            path_frame,
            text="目标文件夹：",
            font=("Arial", 14)
        )
        path_label.pack(side="left", padx=(10, 5), pady=10)
        
        self.path_entry = ctk.CTkEntry(
            path_frame,
            placeholder_text="请选择或输入文件夹路径",
            width=500
        )
        self.path_entry.pack(side="left", padx=5, pady=10, fill="x", expand=True)
        
        browse_button = ctk.CTkButton(
            path_frame,
            text="📁 浏览",
            width=80,
            command=self.browse_folder
        )
        browse_button.pack(side="right", padx=(5, 10), pady=10)
        
        # 选项区域
        options_frame = ctk.CTkFrame(main_frame)
        options_frame.pack(fill="x", padx=10, pady=(0, 15))
        
        # 深度扫描开关
        self.deep_scan_var = tk.BooleanVar(value=True)
        deep_scan_switch = ctk.CTkSwitch(
            options_frame,
            text="🔍 深度扫描模式（递归扫描所有子文件夹）",
            variable=self.deep_scan_var,
            font=("Arial", 13)
        )
        deep_scan_switch.pack(side="left", padx=(20, 40), pady=15)
        
        # 演习模式开关
        self.drill_mode_var = tk.BooleanVar(value=False)
        drill_mode_switch = ctk.CTkSwitch(
            options_frame,
            text="🔬 演习模式（只预览不执行）",
            variable=self.drill_mode_var,
            font=("Arial", 13)
        )
        drill_mode_switch.pack(side="left", padx=(0, 20), pady=15)
        
        # 按钮区域
        button_frame = ctk.CTkFrame(main_frame)
        button_frame.pack(fill="x", padx=10, pady=(0, 15))
        
        # 开始按钮
        self.start_button = ctk.CTkButton(
            button_frame,
            text="🚀 开始智能整理",
            font=("Arial", 16, "bold"),
            height=50,
            width=180,
            fg_color="#2E7D32",
            hover_color="#1B5E20",
            command=self.start_organize
        )
        self.start_button.pack(side="left", padx=(20, 10), pady=10)
        
        # 一键归拢按钮
        self.gather_button = ctk.CTkButton(
            button_frame,
            text="📦 一键归拢",
            font=("Arial", 14, "bold"),
            height=40,
            width=120,
            fg_color="#FF9800",
            hover_color="#F57C00",
            command=self.start_gather
        )
        self.gather_button.pack(side="left", padx=10, pady=10)
        
        # 停止按钮
        self.stop_button = ctk.CTkButton(
            button_frame,
            text="⏹️ 停止任务",
            font=("Arial", 14),
            height=40,
            width=100,
            fg_color="#D32F2F",
            hover_color="#B71C1C",
            command=self.stop_organize,
            state="disabled"
        )
        self.stop_button.pack(side="left", padx=10, pady=10)
        
        # 撤销按钮
        self.undo_button = ctk.CTkButton(
            button_frame,
            text="💊 撤回上次操作",
            font=("Arial", 16, "bold"),
            height=50,
            width=180,
            fg_color="#7B1FA2",
            hover_color="#4A148C",
            command=self.undo_operation
        )
        self.undo_button.pack(side="right", padx=(10, 20), pady=10)
        
        # 日志区域
        log_frame = ctk.CTkFrame(main_frame)
        log_frame.pack(fill="both", expand=True, padx=10, pady=(0, 10))
        
        log_label = ctk.CTkLabel(
            log_frame,
            text="📝 操作日志",
            font=("Arial", 14, "bold")
        )
        log_label.pack(anchor="w", padx=10, pady=(10, 5))
        
        # 日志文本框
        self.log_text = scrolledtext.ScrolledText(
            log_frame,
            bg="#1E1E1E",
            fg="#FFFFFF",
            font=("Consolas", 10),
            wrap=tk.WORD,
            height=15
        )
        self.log_text.pack(fill="both", expand=True, padx=10, pady=(0, 10))
    
    def browse_folder(self):
        """浏览文件夹"""
        folder_path = filedialog.askdirectory(title="选择要整理的文件夹")
        if folder_path:
            self.path_entry.delete(0, tk.END)
            self.path_entry.insert(0, folder_path)
    
    def start_organize(self):
        """开始整理文件"""
        target_dir = self.path_entry.get().strip()
        
        if not target_dir:
            messagebox.showerror("错误", "请先选择要整理的文件夹！")
            return
        
        # 禁用开始按钮，启用停止按钮
        self.start_button.configure(state="disabled")
        self.stop_button.configure(state="normal")
        self.undo_button.configure(state="disabled")
        
        # 清空日志
        self.log_text.delete(1.0, tk.END)
        
        # 在新线程中执行整理任务
        def organize_task():
            try:
                success = self.organizer.organize_files(
                    target_dir=target_dir,
                    drill_mode=self.drill_mode_var.get(),
                    deep_scan=self.deep_scan_var.get(),
                    user_exclude_folders=None
                )
                self.task_queue.put(("task_done", success))
            except Exception as e:
                self.log_message(f"❌ 任务执行异常：{e}")
                self.task_queue.put(("task_done", False))
        
        thread = threading.Thread(target=organize_task, daemon=True)
        thread.start()
    
    def stop_organize(self):
        """停止整理任务"""
        self.organizer.stop()
        self.log_message("⏹️ 用户请求停止任务...")
    
    def start_gather(self):
        """开始一键归拢"""
        target_dir = self.path_entry.get().strip()
        
        if not target_dir:
            messagebox.showerror("错误", "请先选择要归拢的文件夹！")
            return
        
        # 确认对话框
        confirm = messagebox.askyesno("确认", "确定要归拢根目录的散落文件吗？\n\n此操作将：\n1. 扫描根目录下的所有文件\n2. 创建'根目录待处理_日期'文件夹\n3. 将散落文件移动到该文件夹\n4. 自动保护关键系统文件（.dll, .sys, .exe等）")
        if not confirm:
            return
        
        # 禁用按钮，启用停止按钮
        self.start_button.configure(state="disabled")
        self.gather_button.configure(state="disabled")
        self.stop_button.configure(state="normal")
        self.undo_button.configure(state="disabled")
        
        # 清空日志
        self.log_text.delete(1.0, tk.END)
        
        # 在新线程中执行归拢任务
        def gather_task():
            try:
                success = self.organizer.gather_root_files(
                    target_dir=target_dir,
                    drill_mode=self.drill_mode_var.get()
                )
                self.task_queue.put(("task_done", success))
            except Exception as e:
                self.log_message(f"❌ 归拢任务执行异常：{e}")
                self.task_queue.put(("task_done", False))
        
        thread = threading.Thread(target=gather_task, daemon=True)
        thread.start()
    
    def undo_operation(self):
        """执行撤销操作"""
        target_dir = self.path_entry.get().strip()
        
        if not target_dir:
            messagebox.showerror("错误", "请先选择要撤销的文件夹！")
            return
        
        # 确认对话框
        confirm = messagebox.askyesno("确认", "确定要撤销上次的文件整理操作吗？")
        if not confirm:
            return
        
        # 禁用按钮
        self.start_button.configure(state="disabled")
        self.undo_button.configure(state="disabled")
        
        # 清空日志
        self.log_text.delete(1.0, tk.END)
        
        # 在新线程中执行撤销任务
        def undo_task():
            try:
                success = self.organizer.undo_last_operation(target_dir)
                self.task_queue.put(("task_done", success))
            except Exception as e:
                self.log_message(f"❌ 撤销操作异常：{e}")
                self.task_queue.put(("task_done", False))
        
        thread = threading.Thread(target=undo_task, daemon=True)
        thread.start()
    
    def run(self):
        """运行应用程序"""
        self.root.mainloop()

# ======================== 主程序入口 ========================
def main():
    """主函数"""
    try:
        app = FileMasterProGUI()
        app.run()
    except Exception as e:
        print(f"应用程序启动失败：{e}")
        messagebox.showerror("错误", f"应用程序启动失败：{e}")

if __name__ == "__main__":
    main()
