"""
全能文件夹整理大师 Pro - 现代化图形界面版本
整合了 clean_my_folder.py 和 undo_it.py 的核心功能
采用 customtkinter 库，深色极简风格
"""

import os
import json
import shutil
import threading
import time
from datetime import datetime
from tkinter import filedialog, messagebox
import customtkinter as ctk
import send2trash

# 设置 customtkinter 主题
ctk.set_appearance_mode("dark")  # 深色主题
ctk.set_default_color_theme("dark-blue")  # 深蓝色主题

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
    """检查文件夹是否在排除列表中（仅按目录名精确匹配）"""
    if user_exclude_folders is None:
        user_exclude_folders = set()

    # 合并默认排除和用户自定义排除
    all_exclude_folders = EXCLUDE_FOLDERS.union(user_exclude_folders)

    # 仅检查当前文件夹名是否精确匹配排除列表
    if folder_name in all_exclude_folders:
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

class FolderOrganizerPro(ctk.CTk):
    """全能文件夹整理大师 Pro - 主窗口类"""
    
    def __init__(self):
        super().__init__()
        
        # 配置窗口
        self.title("全能文件夹整理大师 Pro")
        self.geometry("800x600")
        self.minsize(700, 500)
        
        # 设置图标（如果有的话）
        try:
            self.iconbitmap("icon.ico")
        except:
            pass
        
        # 初始化变量
        self.target_dir = ""
        self.deep_scan = ctk.BooleanVar(value=True)  # 默认开启深度扫描
        self.drill_mode = ctk.BooleanVar(value=True)  # 默认开启安全演习
        self.is_organizing = False  # 是否正在整理
        self.is_undoing = False     # 是否正在撤销
        
        # 创建界面
        self.create_widgets()
        
        # 日志缓冲区
        self.log_buffer = []
        
    def create_widgets(self):
        """创建所有界面组件"""
        
        # 主容器
        self.main_container = ctk.CTkFrame(self)
        self.main_container.pack(fill="both", expand=True, padx=20, pady=20)
        
        # 标题区域
        self.title_label = ctk.CTkLabel(
            self.main_container,
            text="全能文件夹整理大师 Pro",
            font=ctk.CTkFont(size=24, weight="bold")
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
        path_frame = ctk.CTkFrame(self.main_container)
        path_frame.pack(fill="x", pady=(0, 15))
        
        # 路径标签
        path_label = ctk.CTkLabel(
            path_frame,
            text="目标文件夹路径：",
            font=ctk.CTkFont(size=14)
        )
        path_label.pack(anchor="w", padx=10, pady=(10, 5))
        
        # 路径输入框和浏览按钮容器
        path_input_frame = ctk.CTkFrame(path_frame, fg_color="transparent")
        path_input_frame.pack(fill="x", padx=10, pady=(0, 10))
        
        # 路径输入框
        self.path_entry = ctk.CTkEntry(
            path_input_frame,
            placeholder_text="请选择或输入文件夹路径...",
            font=ctk.CTkFont(size=12)
        )
        self.path_entry.pack(side="left", fill="x", expand=True, padx=(0, 10))
        
        # 浏览按钮
        browse_button = ctk.CTkButton(
            path_input_frame,
            text="📁 浏览文件夹",
            width=120,
            command=self.browse_folder,
            font=ctk.CTkFont(size=12)
        )
        browse_button.pack(side="right")
        
    def create_config_section(self):
        """创建功能配置区域"""
        config_frame = ctk.CTkFrame(self.main_container)
        config_frame.pack(fill="x", pady=(0, 15))
        
        # 配置标题
        config_label = ctk.CTkLabel(
            config_frame,
            text="功能配置：",
            font=ctk.CTkFont(size=14)
        )
        config_label.pack(anchor="w", padx=10, pady=(10, 5))
        
        # 复选框容器
        checkbox_frame = ctk.CTkFrame(config_frame, fg_color="transparent")
        checkbox_frame.pack(fill="x", padx=10, pady=(0, 10))
        
        # 深度扫描复选框
        self.deep_scan_checkbox = ctk.CTkCheckBox(
            checkbox_frame,
            text="开启深度扫描（扫描所有子文件夹）",
            variable=self.deep_scan,
            font=ctk.CTkFont(size=12)
        )
        self.deep_scan_checkbox.pack(anchor="w", pady=(0, 5))
        
        # 安全演习复选框
        self.drill_mode_checkbox = ctk.CTkCheckBox(
            checkbox_frame,
            text="开启安全演习（只预览不真删）",
            variable=self.drill_mode,
            font=ctk.CTkFont(size=12)
        )
        self.drill_mode_checkbox.pack(anchor="w")
        
    def create_action_section(self):
        """创建核心操作区域"""
        action_frame = ctk.CTkFrame(self.main_container)
        action_frame.pack(fill="x", pady=(0, 15))
        
        # 操作按钮容器
        button_frame = ctk.CTkFrame(action_frame, fg_color="transparent")
        button_frame.pack(fill="x", padx=20, pady=20)
        
        # 一键智能整理按钮（绿色）
        self.organize_button = ctk.CTkButton(
            button_frame,
            text="🚀 一键智能整理",
            command=self.start_organize,
            font=ctk.CTkFont(size=16, weight="bold"),
            fg_color="#2ecc71",  # 绿色
            hover_color="#27ae60",
            height=50,
            corner_radius=15
        )
        self.organize_button.pack(side="left", expand=True, padx=(0, 10))
        
        # 撤销上次操作按钮（橙色）
        self.undo_button = ctk.CTkButton(
            button_frame,
            text="💊 撤销上次操作（后悔药）",
            command=self.start_undo,
            font=ctk.CTkFont(size=16, weight="bold"),
            fg_color="#e67e22",  # 橙色
            hover_color="#d35400",
            height=50,
            corner_radius=15
        )
        self.undo_button.pack(side="right", expand=True, padx=(10, 0))
        
    def create_log_section(self):
        """创建可视化日志区域"""
        log_frame = ctk.CTkFrame(self.main_container)
        log_frame.pack(fill="both", expand=True)
        
        # 日志标题
        log_label = ctk.CTkLabel(
            log_frame,
            text="操作日志：",
            font=ctk.CTkFont(size=14)
        )
        log_label.pack(anchor="w", padx=10, pady=(10, 5))
        
        # 日志文本框
        self.log_textbox = ctk.CTkTextbox(
            log_frame,
            font=ctk.CTkFont(family="Consolas", size=11),
            fg_color="#1a1a1a",  # 深黑色背景
            text_color="#ffffff",  # 白色文字
            wrap="word"
        )
        self.log_textbox.pack(fill="both", expand=True, padx=10, pady=(0, 10))
        
        # 添加滚动条
        self.log_textbox.configure(state="disabled")
        
    def browse_folder(self):
        """浏览文件夹对话框"""
        folder_path = filedialog.askdirectory(title="选择要整理的文件夹")
        if folder_path:
            self.path_entry.delete(0, "end")
            self.path_entry.insert(0, folder_path)
            self.target_dir = folder_path
            self.log_message(f"✅ 已选择文件夹：{folder_path}")
    
    def log_message(self, message):
        """向日志文本框添加消息"""
        timestamp = datetime.now().strftime("%H:%M:%S")
        log_line = f"[{timestamp}] {message}\n"
        
        # 添加到缓冲区
        self.log_buffer.append(log_line)
        
        # 如果缓冲区太大，清空一部分
        if len(self.log_buffer) > 100:
            self.log_buffer = self.log_buffer[-50:]
        
        # 更新文本框
        self.log_textbox.configure(state="normal")
        self.log_textbox.insert("end", log_line)
        self.log_textbox.see("end")  # 滚动到底部
        self.log_textbox.configure(state="disabled")
        
        # 更新界面
        self.update()
    
    def clear_log(self):
        """清空日志"""
        self.log_textbox.configure(state="normal")
        self.log_textbox.delete("1.0", "end")
        self.log_textbox.configure(state="disabled")
        self.log_buffer = []
    
    def start_organize(self):
        """开始整理（多线程）"""
        if self.is_organizing:
            self.log_message("⚠️ 正在整理中，请稍候...")
            return
        
        # 获取目标目录
        self.target_dir = self.path_entry.get().strip()
        if not self.target_dir:
            messagebox.showwarning("警告", "请先选择要整理的文件夹！")
            return
        
        if not os.path.exists(self.target_dir):
            messagebox.showerror("错误", f"文件夹不存在：{self.target_dir}")
            return
        
        if not os.path.isdir(self.target_dir):
            messagebox.showerror("错误", f"这不是一个文件夹：{self.target_dir}")
            return
        
        # 禁用按钮，防止重复点击
        self.is_organizing = True
        self.organize_button.configure(state="disabled", text="整理中...")
        self.undo_button.configure(state="disabled")
        
        # 清空日志
        self.clear_log()
        
        # 显示开始信息
        self.log_message("=" * 60)
        self.log_message("🚀 开始智能整理...")
        self.log_message(f"目标文件夹：{self.target_dir}")
        self.log_message(f"深度扫描：{'开启' if self.deep_scan.get() else '关闭'}")
        self.log_message(f"安全演习：{'开启' if self.drill_mode.get() else '关闭'}")
        self.log_message("=" * 60)
        
        # 在新线程中执行整理
        thread = threading.Thread(target=self.organize_files, daemon=True)
        thread.start()
    
    def start_undo(self):
        """开始撤销操作（多线程）"""
        if self.is_undoing:
            self.log_message("⚠️ 正在撤销中，请稍候...")
            return
        
        # 获取目标目录
        self.target_dir = self.path_entry.get().strip()
        if not self.target_dir:
            messagebox.showwarning("警告", "请先选择文件夹！")
            return
        
        # 检查历史文件是否存在
        history_file = os.path.join(self.target_dir, "organize_history.json")
        if not os.path.exists(history_file):
            messagebox.showwarning("警告", "找不到历史记录文件，无法撤销！")
            return
        
        # 确认对话框
        confirm = messagebox.askyesno("确认", "确定要撤销上次的整理操作吗？")
        if not confirm:
            return
        
        # 禁用按钮，防止重复点击
        self.is_undoing = True
        self.undo_button.configure(state="disabled", text="撤销中...")
        self.organize_button.configure(state="disabled")
        
        # 清空日志
        self.clear_log()
        
        # 显示开始信息
        self.log_message("=" * 60)
        self.log_message("💊 开始撤销操作...")
        self.log_message(f"目标文件夹：{self.target_dir}")
        self.log_message("=" * 60)
        
        # 在新线程中执行撤销
        thread = threading.Thread(target=self.undo_operation, daemon=True)
        thread.start()
    
    def organize_files(self):
        """整理文件的核心逻辑"""
        try:
            # 获取配置
            drill_mode = self.drill_mode.get()
            deep_scan = self.deep_scan.get()
            
            # 扫描文件
            self.log_message("🔍 正在扫描文件...")
            
            if deep_scan:
                # 深度扫描
                all_files, folders_scanned, max_depth = scan_files_recursively(self.target_dir)
                self.log_message(f"📊 扫描统计：")
                self.log_message(f"   - 扫描文件夹：{folders_scanned} 个")
                self.log_message(f"   - 扫描深度：{max_depth} 层")
                self.log_message(f"   - 发现文件：{len(all_files)} 个")
            else:
                # 只扫描当前目录
                all_files = []
                folders_scanned = 0
                max_depth = 0
                try:
                    for item in os.listdir(self.target_dir):
                        full_path = os.path.join(self.target_dir, item)
                        if os.path.isfile(full_path):
                            all_files.append(full_path)
                    self.log_message(f"📊 扫描统计：发现 {len(all_files)} 个文件")
                except Exception as e:
                    self.log_message(f"❌ 扫描失败：{e}")
                    self.finish_organize()
                    return
            
            if not all_files:
                self.log_message("📭 没有需要整理的文件。")
                self.finish_organize()
                return
            
            # 跳过的特殊文件
            skip_files = {'organize_history.json', 'undo_it.py'}
            
            # 统计数据
            large_files = []
            critical_files = []  # 关键系统文件
            install_package_suggestions = []  # 安装包清理建议
            move_records = []  # 记录所有移动操作
            trash_files = []  # 记录移动到回收站的文件
            moved_count = 0
            deep_moved_count = 0  # 深层文件计数
            trash_count = 0  # 移动到回收站的文件计数
            timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            
            self.log_message("🔄 开始整理文件...")
            
            for file_path in all_files:
                filename = os.path.basename(file_path)
                relative_path = os.path.relpath(file_path, self.target_dir)
                
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
                    self.log_message(f"⚠️ 无法读取文件大小：{relative_path}，错误：{e}")
                    continue
                
                # 检查是否为关键系统文件
                if is_critical_file(filename):
                    critical_files.append((relative_path, file_size))
                    if not drill_mode:
                        self.log_message(f"🛡️ 保护关键系统文件：{relative_path}")
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
                    target_folder = os.path.join(self.target_dir, category)
                else:
                    target_folder = os.path.join(self.target_dir, '其它')
                
                # 创建目标目录（演习模式下不创建，垃圾文件不需要创建目录）
                if not drill_mode and not is_trash_file and not os.path.exists(target_folder):
                    try:
                        os.makedirs(target_folder)
                    except Exception as e:
                        self.log_message(f"❌ 创建文件夹失败：{target_folder}, 错误：{e}")
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
                            self.log_message(f"🗑️ 预览删除（回收站）：{filename}")
                        else:
                            self.log_message(f"🗑️ 预览删除（回收站，深层）：{relative_path}")
                    else:
                        # 普通文件预览：移动到分类文件夹
                        if os.path.dirname(relative_path) == '.':
                            self.log_message(f"🔍 预览移动：{filename}  --->  {os.path.basename(target_folder)}")
                        else:
                            self.log_message(f"🔍 预览移动（深层）：{relative_path}  --->  {os.path.basename(target_folder)}")
                    
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
                                self.log_message(f"🗑️ 已删除（回收站）：{filename}")
                            else:
                                self.log_message(f"🗑️ 已删除（回收站，深层）：{relative_path}")
                        except Exception as e:
                            self.log_message(f"❌ 移动到回收站失败：{relative_path}，错误：{e}")
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
                                self.log_message(f"✅ 已移动：{filename}  --->  {os.path.basename(target_folder)}")
                            else:
                                self.log_message(f"✅ 已移动（深层）：{relative_path}  --->  {os.path.basename(target_folder)}")
                        except Exception as e:
                            self.log_message(f"❌ 移动文件失败：{relative_path}，错误：{e}")
            
            self.log_message("=" * 60)
            
            # 保存历史记录（演习模式下不保存）
            if move_records and not drill_mode:
                if save_history(self.target_dir, move_records, timestamp, max_depth):
                    self.log_message("📝 已生成移动历史：organize_history.json")
                
                # 创建后悔药脚本
                if create_undo_script(self.target_dir):
                    self.log_message("💊 已创建后悔药脚本：undo_it.py")
            
            self.log_message("📊 统计报告：")
            self.log_message(f"   - 扫描文件夹：{folders_scanned} 个")
            self.log_message(f"   - 扫描深度：{max_depth} 层")
            self.log_message(f"   - 移动文件总数：{moved_count} 个")
            self.log_message(f"   - 其中深层文件：{deep_moved_count} 个")
            self.log_message(f"   - 移动到回收站：{trash_count} 个")
            
            # 显示关键系统文件保护情况
            if critical_files:
                self.log_message("🛡️ 关键系统文件保护：")
                self.log_message(f"   - 保护了 {len(critical_files)} 个关键系统文件")
                for fname, fsize in critical_files[:3]:  # 只显示前3个
                    self.log_message(f"   {fname}   |   大小: {human_size(fsize)}")
                if len(critical_files) > 3:
                    self.log_message(f"   ... 还有 {len(critical_files) - 3} 个关键文件被保护")
            
            # 显示安装包清理建议
            if install_package_suggestions:
                self.log_message("💡 安装包清理建议（超过500MB）：")
                for fname, fsize, ext in install_package_suggestions:
                    self.log_message(f"   [疑似安装包，建议安装后删除] {fname}   |   大小: {human_size(fsize)}")
            
            self.log_message("📊 超过100MB的大文件：")
            if large_files:
                for fname, fsize in large_files:
                    self.log_message(f"   {fname}   |   大小: {human_size(fsize)}")
            else:
                self.log_message("   无")
            
            self.log_message("=" * 60)
            if drill_mode:
                self.log_message(f"🔬 演习模式完成！预览了 {moved_count} 个文件的移动计划")
                self.log_message(f"💡 提示：如需实际执行，请取消勾选'安全演习'选项")
            else:
                self.log_message(f"🎉 整理完成！")
                if moved_count > 0:
                    self.log_message(f"\n💡 提示：如需撤销，请点击'撤销上次操作'按钮")
            
            self.log_message("=" * 60)
            
        except Exception as e:
            self.log_message(f"❌ 整理过程中出现错误：{e}")
            import traceback
            self.log_message(traceback.format_exc())
        
        finally:
            self.finish_organize()
    
    def undo_operation(self):
        """撤销操作的核心逻辑"""
        try:
            history_file = os.path.join(self.target_dir, "organize_history.json")
            
            if not os.path.exists(history_file):
                self.log_message("❌ 错误：找不到 organize_history.json 文件！")
                self.log_message("没有可以还原的记录。")
                self.finish_undo()
                return
            
            try:
                with open(history_file, 'r', encoding='utf-8') as f:
                    history = json.load(f)
            except Exception as e:
                self.log_message(f"❌ 读取历史记录失败：{e}")
                self.finish_undo()
                return
            
            moves = history.get('moves', [])
            if not moves:
                self.log_message("📭 历史记录为空，没有文件需要还原。")
                self.finish_undo()
                return
            
            self.log_message(f"📊 找到 {len(moves)} 条移动记录")
            self.log_message(f"📅 整理时间：{history.get('timestamp', '未知')}")
            self.log_message(f"📏 扫描深度：{history.get('max_depth', 0)} 层")
            self.log_message("🔄 开始还原文件...")
            
            restored_count = 0
            failed_count = 0
            
            for move in moves:
                original_path = move['original_path']
                current_path = move['new_path']
                
                if not os.path.exists(current_path):
                    self.log_message(f"⏭️ 跳过（文件不存在）：{os.path.basename(current_path)}")
                    failed_count += 1
                    continue
                
                # 确保原始目录存在（支持深层目录）
                original_dir = os.path.dirname(original_path)
                if original_dir and not os.path.exists(original_dir):
                    try:
                        os.makedirs(original_dir)
                        self.log_message(f"📁 创建目录：{original_dir}")
                    except Exception as e:
                        self.log_message(f"❌ 创建目录失败：{original_dir}，错误：{e}")
                        failed_count += 1
                        continue
                
                try:
                    shutil.move(current_path, original_path)
                    self.log_message(f"✅ 已还原：{os.path.basename(current_path)}")
                    restored_count += 1
                except Exception as e:
                    self.log_message(f"❌ 还原失败：{os.path.basename(current_path)}，错误：{e}")
                    failed_count += 1
            
            self.log_message("=" * 60)
            self.log_message(f"📊 还原完成！成功：{restored_count} 个，失败：{failed_count} 个")
            
            # 删除历史记录文件
            if restored_count > 0 and failed_count == 0:
                try:
                    os.remove(history_file)
                    self.log_message("🗑️ 已清理历史记录文件。")
                except Exception as e:
                    self.log_message(f"⚠️ 清理历史记录文件失败：{e}")
            
            self.log_message("=" * 60)
            
        except Exception as e:
            self.log_message(f"❌ 撤销过程中出现错误：{e}")
            import traceback
            self.log_message(traceback.format_exc())
        
        finally:
            self.finish_undo()
    
    def finish_organize(self):
        """整理完成后的清理工作"""
        self.is_organizing = False
        self.organize_button.configure(state="normal", text="🚀 一键智能整理")
        self.undo_button.configure(state="normal")
    
    def finish_undo(self):
        """撤销完成后的清理工作"""
        self.is_undoing = False
        self.undo_button.configure(state="normal", text="💊 撤销上次操作（后悔药）")
        self.organize_button.configure(state="normal")

# ======================== 主程序入口 ========================

def main():
    """主函数"""
    app = FolderOrganizerPro()
    app.mainloop()

if __name__ == "__main__":
    main()
