"""
全能文件夹整理大师 Pro - 现代化图形界面版本（使用标准 tkinter）
整合了 clean_my_folder.py 和 undo_it.py 的核心功能
采用 tkinter 库，深色极简风格
"""

import os
import json
import shutil
import threading
import time
from datetime import datetime
import tkinter as tk
from tkinter import filedialog, messagebox, ttk
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

# ======================== 工具函数 ========================

def human_size(size):
    """将文件大小转换成更易读的形式"""
    for unit in ['B','KB','MB','GB','TB']:
        if size < 1024:
            return f"{size:.2f}{unit}"
        size /= 1024
    return f"{size:.2f}PB"

def get_category(ext):
    """根据扩展名获取类别"""
    return EXT_TO_CATEGORY.get(ext.lower())

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
        return all_files, folders_scanned, max_depth_reached
    except Exception as e:
        return all_files, folders_scanned, max_depth_reached
    
    for item in items:
        full_path = os.path.join(root_dir, item)
        
        if os.path.isfile(full_path):
            all_files.append(full_path)
        elif os.path.isdir(full_path):
            folders_scanned += 1
            
            # 检查是否在排除列表中
            if is_excluded_folder(item, full_path, user_exclude_folders):
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
        return False

# ======================== GUI 应用程序 ========================

class FolderOrganizerPro(tk.Tk):
    """全能文件夹整理大师 Pro - 主窗口类"""
    
    def __init__(self):
        super().__init__()
        
        # 配置窗口
        self.title("全能文件夹整理大师 Pro")
        self.geometry("800x600")
        self.minsize(700, 500)
        
        # 设置深色主题颜色
        self.bg_color = "#1e1e1e"
        self.fg_color = "#ffffff"
        self.entry_bg = "#2d2d2d"
        self.button_green = "#2ecc71"
        self.button_orange = "#e67e22"
        self.log_bg = "#0a0a0a"
        
        self.configure(bg=self.bg_color)
        
        # 设置图标（如果有的话）
        try:
            self.iconbitmap("icon.ico")
        except:
            pass
        
        # 初始化变量
        self.target_dir = ""
        self.deep_scan_var = tk.BooleanVar(value=True)  # 默认开启深度扫描
        self.drill_mode_var = tk.BooleanVar(value=True)  # 默认开启安全演习
        self.is_organizing = False  # 是否正在整理
        self.is_undoing = False     # 是否正在撤销
        
        # 创建界面
        self.create_widgets()
        
        # 日志缓冲区
        self.log_buffer = []
        
    def create_widgets(self):
        """创建所有界面组件"""
        
        # 主容器
        self.main_container = tk.Frame(self, bg=self.bg_color)
        self.main_container.pack(fill="both", expand=True, padx=20, pady=20)
        
        # 标题区域
        self.title_label = tk.Label(
            self.main_container,
            text="全能文件夹整理大师 Pro",
            font=("Arial", 24, "bold"),
            fg=self.fg_color,
            bg=self.bg_color
        )
        self.title_label.pack(pady=(0, 20))
        
        # 路径选择区域
        self.create_path_section()
        
        # 功能配置区域
        self.create_config_section()
        
        # 核心操作区域
        self.create_action_section()
        
        # 日志区域
        self.create_log_section()
        
    def create_path_section(self):
        """创建路径选择区域"""
        path_frame = tk.Frame(self.main_container, bg=self.bg_color)
        path_frame.pack(fill="x", pady=(0, 15))
        
        # 路径标签
        path_label = tk.Label(
            path_frame,
            text="目标文件夹路径：",
            font=("Arial", 12),
            fg=self.fg_color,
            bg=self.bg_color
        )
        path_label.pack(anchor="w", padx=10, pady=(10, 5))
        
        # 路径输入框和浏览按钮容器
        path_input_frame = tk.Frame(path_frame, bg=self.bg_color)
        path_input_frame.pack(fill="x", padx=10, pady=(0, 10))
        
        # 路径输入框
        self.path_entry = tk.Entry(
            path_input_frame,
            font=("Arial", 10),
            bg=self.entry_bg,
            fg=self.fg_color,
            insertbackground=self.fg_color,
            relief="flat"
        )
        self.path_entry.pack(side="left", fill="x", expand=True, padx=(0, 10))
        
        # 浏览按钮
        browse_button = tk.Button(
            path_input_frame,
            text="📁 浏览文件夹",
            width=15,
            command=self.browse_folder,
            font=("Arial", 10),
            bg="#3498db",
            fg="white",
            activebackground="#2980b9",
            activeforeground="white",
            relief="flat",
            cursor="hand2"
        )
        browse_button.pack(side="right")
        
    def create_config_section(self):
        """创建功能配置区域"""
        config_frame = tk.Frame(self.main_container, bg=self.bg_color)
        config_frame.pack(fill="x", pady=(0, 15))
        
        # 配置标题
        config_label = tk.Label(
            config_frame,
            text="功能配置：",
            font=("Arial", 12),
            fg=self.fg_color,
            bg=self.bg_color
        )
        config_label.pack(anchor="w", padx=10, pady=(10, 5))
        
        # 复选框容器
        checkbox_frame = tk.Frame(config_frame, bg=self.bg_color)
        checkbox_frame.pack(fill="x", padx=10, pady=(0, 10))
        
        # 深度扫描复选框
        self.deep_scan_checkbox = tk.Checkbutton(
            checkbox_frame,
            text="开启深度扫描（扫描所有子文件夹）",
            variable=self.deep_scan_var,
            font=("Arial", 10),
            fg=self.fg_color,
            bg=self.bg_color,
            selectcolor=self.bg_color,
            activebackground=self.bg_color,
            activeforeground=self.fg_color
        )
        self.deep_scan_checkbox.pack(anchor="w", pady=(0, 5))
        
        # 安全演习复选框
        self.drill_mode_checkbox = tk.Checkbutton(
            checkbox_frame,
            text="开启安全演习（只预览不真删）",
            variable=self.drill_mode_var,
            font=("Arial", 10),
            fg=self.fg_color,
            bg=self.bg_color,
            selectcolor=self.bg_color,
            activebackground=self.bg_color,
            activeforeground=self.fg_color
        )
        self.drill_mode_checkbox.pack(anchor="w")
        
    def create_action_section(self):
        """创建核心操作区域"""
        action_frame = tk.Frame(self.main_container, bg=self.bg_color)
        action_frame.pack(fill="x", pady=(0, 15))
        
        # 操作按钮容器
        button_frame = tk.Frame(action_frame, bg=self.bg_color)
        button_frame.pack(fill="x", padx=20, pady=