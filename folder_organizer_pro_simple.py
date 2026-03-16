"""
全能文件夹整理大师 Pro - 简化版（使用标准 tkinter）
整合了 clean_my_folder.py 和 undo_it.py 的核心功能
深色极简风格，兼容 Python 3.6+
"""

import os
import json
import shutil
import threading
from datetime import datetime
import tkinter as tk
from tkinter import filedialog, messagebox, scrolledtext
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

# 安全白名单：禁止扫描的文件夹
EXCLUDE_FOLDERS = {
    'node_modules', '.git', 'venv', '__pycache__', '.idea', '.vscode',
    'dist', 'build', 'target', 'bin', 'obj', 'Debug', 'Release',
    'packages', 'logs', 'temp', 'tmp', 'Program Files', 'Program Files (x86)',
    'Windows', 'System32', 'AppData', 'Local Settings'
}

# 关键系统文件：绝对禁止移动的文件名关键词
CRITICAL_FILE_KEYWORDS = {
    'steam_api', 'dll', 'manifest', 'node', 'cmd', 'exe', 'sys', 'drv',
    'ocx', 'vxd', 'ini', 'cfg', 'config', 'registry', 'boot', 'kernel',
    'system', 'windows', 'mscore', 'framework', 'runtime'
}

# 生成扩展名到类别的快速索引
EXT_TO_CATEGORY = {}
for category, exts in CATEGORY_DICT.items():
    for ext in exts:
        EXT_TO_CATEGORY[ext.lower()] = category

# 工具函数
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
    
    all_exclude_folders = EXCLUDE_FOLDERS.union(user_exclude_folders)
    
    if folder_name in all_exclude_folders:
        return True
    
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
    """智能处理命名冲突"""
    base, ext = os.path.splitext(filename)
    counter = 1
    dest_path = os.path.join(folder, filename)
    while os.path.exists(dest_path):
        dest_path = os.path.join(folder, f"{base}_{counter}{ext}")
        counter += 1
    return dest_path

def scan_files_recursively(root_dir, user_exclude_folders=None, current_depth=0, max_depth=0):
    """递归扫描所有文件，跳过排除的文件夹"""
    all_files = []
    folders_scanned = 0
    max_depth_reached = max(max_depth, current_depth)
    
    try:
        items = os.listdir(root_dir)
    except (PermissionError, Exception):
        return all_files, folders_scanned, max_depth_reached
    
    for item in items:
        full_path = os.path.join(root_dir, item)
        
        if os.path.isfile(full_path):
            all_files.append(full_path)
        elif os.path.isdir(full_path):
            folders_scanned += 1
            
            if is_excluded_folder(item, full_path, user_exclude_folders):
                continue
            
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
        
        original_dir = os.path.dirname(original_path)
        if original_dir and not os.path.exists(original_dir):
            try:
                os.makedirs(original_dir)
                print(f"创建目录：{{original_dir}}")
            except Exception as e:
                print(f"创建目录失败：{{original_dir}}，错误：{{e}}")
                failed_count += 1
                continue
        
        try:
            shutil.move(current_path, original_path)
            print(f"已还原：{{os.path.basename(current_path)}}")
            restored_count += 1
        except Exception as e:
            print(f"还原失败：{{os.path.basename(current_path)}}，错误：{{e}}")
            failed_count += 1
    
    print_line()
    print(f"还原完成！成功：{{restored_count}} 个，失败：{{failed_count}} 个")
    
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
    except Exception:
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
    except Exception:
        return False

# ======================== GUI 应用程序 ========================

class FolderOrganizerPro:
    """全能文件夹整理大师 Pro - 主窗口类"""
    
    def __init__(self):
        self.root = tk.Tk()
        self.root.title("全能文件夹整理大师 Pro")
        self.root.geometry("800x600")
        self.root.minsize(700, 500)
        
        # 深色主题颜色
        self.bg_color = "#1e1e1e"
        self.fg_color = "#ffffff"
        self.entry_bg = "#2d2d2d"
        self.button_green = "#2ecc71"
        self.button_orange = "#e67e22"
        self.log_bg = "#0a0a0a"
        
        self.root.configure(bg=self.bg_color)
        
        # 初始化变量
        self.target_dir = ""
        self.deep_scan_var = tk.BooleanVar(value=True)
        self.drill_mode_var = tk.BooleanVar(value=True)
        self.is_organizing = False
        self.is_undoing = False
        
        # 创建界面
        self.create_widgets()
        
    def create_widgets(self):
        """创建所有界面组件"""
        
        # 标题
        title_label = tk.Label(
            self.root,
            text="全能文件夹整理大师 Pro",
            font=("Arial", 24, "bold"),
            fg=self.fg_color,
            bg=self.bg_color
        )
        title_label.pack(pady=20)
        
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
        path_frame = tk.Frame(self.root, bg=self.bg_color)
        path_frame.pack(fill="x", padx=20, pady=(0, 15))
        
        path_label = tk.Label(
            path_frame,
            text="目标文件夹路径：",
            font=("Arial", 12),
            fg=self.fg_color,
            bg=self.bg_color
        )
        path_label.pack(anchor="w", pady=(0, 5))
        
        input_frame = tk.Frame(path_frame, bg=self.bg_color)
        input_frame.pack(fill="x")
        
        self.path_entry = tk.Entry(
            input_frame,
            font=("Arial", 10),
            bg=self.entry_bg,
            fg=self.fg_color,
            insertbackground=self.fg_color
        )
        self.path_entry.pack(side="left", fill="x", expand=True, padx=(0, 10))
        
        browse_btn = tk.Button(
            input_frame,
            text="📁 浏览文件夹",
            command=self.browse_folder,
            font=("Arial", 10),
            bg="#3498db",
            fg="white",
            activebackground="#2980b9"
        )
        browse_btn.pack(side="right")
        
    def create_config_section(self):
        """创建功能配置区域"""
        config_frame = tk.Frame(self.root, bg=self.bg_color)
        config_frame.pack(fill="x", padx=20, pady=(0, 15))
        
        config_label = tk.Label(
            config_frame,
            text="功能配置：",
            font=("Arial", 12),
            fg=self.fg_color,
            bg=self.bg_color
        )
        config_label.pack(anchor="w", pady=(0, 5))
        
        self.deep_scan_cb = tk.Checkbutton(
            config_frame,
            text="开启深度扫描（扫描所有子文件夹）",
            variable=self.deep_scan_var,
            font=("Arial", 10),
            fg=self.fg_color,
            bg=self.bg_color,
            selectcolor=self.bg_color
        )
        self.deep_scan_cb.pack(anchor="w", pady=2)
        
        self.drill_mode_cb = tk.Checkbutton(
            config_frame,
            text="开启安全演习（只预览不真删）",
            variable=self.drill_mode_var,
            font=("Arial", 10),
            fg=self.fg_color,
            bg=self.bg_color,
            selectcolor=self.bg_color
        )
        self.drill_mode_cb.pack(anchor="w", pady=2)
        
    def create_action_section(self):
        """创建核心操作区域"""
        action_frame = tk.Frame(self.root, bg=self.bg_color)
        action_frame.pack(fill="x", padx=20, pady=(0, 15))
        
        button_frame = tk.Frame(action_frame, bg=self.bg_color)
        button_frame.pack(fill="x", pady=10)
        
        # 一键智能整理按钮
        self.organize_btn = tk.Button(
            button_frame,
            text="🚀 一键智能整理",
            command=self.start_organize,
            font=("Arial", 14, "bold"),
            bg=self.button_green,
            fg="white",
            activebackground="#27ae60",
            height=2,
            width=20
        )
        self.organize_btn.pack(side="left", expand=True, padx=(0, 10))
        
        # 撤销上次操作按钮
        self.undo_btn = tk.Button(
            button_frame,
            text="💊 撤销上次操作",
            command=self.start_undo,
            font=("Arial", 14, "bold"),
            bg=self.button_orange,
            fg="white",
            activebackground="#d35400",
            height=2,
            width=20
        )
        self.undo_btn.pack(side="right", expand=True, padx=(10, 0))
        
    def create_log_section(self):
        """创建可视化日志区域"""
        log_frame = tk.Frame(self.root, bg=self.bg_color)
        log_frame.pack(fill="both", expand=True, padx=20, pady=(0, 20))
        
        log_label = tk.Label(
            log_frame,
            text="操作日志：",
            font=("Arial", 12),
            fg=self.fg_color,
            bg=self.bg_color
        )
        log_label.pack(anchor="w", pady=(0, 5))
        
        # 滚动文本框
        self.log_text = scrolledtext.ScrolledText(
            log_frame,
            font=("Consolas", 10),
            bg=self.log_bg,
            fg=self.fg_color,
            insertbackground=self.fg_color,
            wrap="word",
            height=10
        )
        self.log_text.pack(fill="both", expand=True)
        self.log_text.configure(state="disabled")
        
    def browse_folder(self):
        """浏览文件夹对话框"""
        folder_path = filedialog.askdirectory(title="选择要整理的文件夹")
        if folder_path:
            self.path_entry.delete(0, tk.END)
            self.path_entry.insert(0, folder_path)
            self.target_dir = folder_path
            self.log_message(f"✅ 已选择文件夹：{folder_path}")
    
    def log_message(self, message):
        """向日志文本框添加消息"""
        timestamp = datetime.now().strftime("%H:%M:%S")
        log_line = f"[{timestamp}] {message}\n"
        
        self.log_text.configure(state="normal")
        self.log_text.insert(tk.END, log_line)
        self.log_text.see(tk.END)
        self.log_text.configure(state="disabled")
        
        # 限制日志大小
        lines = self.log_text.get("1.0", tk.END).split('\n')
        if len(lines) > 200:
            self.log_text.configure(state="normal")
            self.log_text.delete("1.0", f"{len(lines)-150}.0")
            self.log_text.configure(state="disabled")
    
    def clear_log(self):
        """清空日志"""
        self.log_text.configure(state="normal")
        self.log_text.delete("1.0", tk.END)
        self.log_text.configure(state="disabled")
    
    def start_organize(self):
        """开始整理（多线程）"""
        if self.is_organizing:
            self.log_message("⚠️ 正在整理中，请稍候...")
            return
        
        self.target_dir = self.path_entry.get().strip()
        if not self.target_dir:
            messagebox.showwarning("警告", "请先选择要整理的文件夹！")
            return
        
        if not os.path.exists(self.target_dir):
            messagebox.showerror("错误", f"文件夹不存在：{self.target_dir}")
            return
        
        if not os.path.isdir(self.target_dir):
            messagebox.showerror("