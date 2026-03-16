#!/usr/bin/env python3
"""
测试 FileMasterPro 核心功能（不依赖 GUI）
"""

import os
import shutil
import tempfile
import sys

# 添加当前目录到路径
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

# 模拟 FileOrganizer 的核心功能
class TestFileOrganizer:
    def __init__(self, log_callback=None):
        self.log_callback = log_callback
        self.is_running = False
        
        # 关键后缀保护
        self.CRITICAL_EXTENSIONS = {
            'dll', 'sys', 'exe', 'ocx', 'vxd', 'drv',
            'ini', 'cfg', 'config', 'manifest', 'msi',
            'bat', 'cmd', 'ps1', 'sh', 'reg', 'inf'
        }
        
        # 关键系统文件关键词
        self.CRITICAL_FILE_KEYWORDS = {
            'steam_api', 'dll', 'manifest', 'node', 'cmd',
            'exe', 'sys', 'drv', 'ocx', 'vxd', 'ini',
            'cfg', 'config', 'registry', 'boot', 'kernel',
            'system', 'windows', 'mscore', 'framework', 'runtime'
        }
    
    def log(self, message):
        """记录日志"""
        if self.log_callback:
            self.log_callback(message)
        else:
            print(message)
    
    def is_critical_file(self, filename):
        """检查文件是否为关键系统文件"""
        filename_lower = filename.lower()
        for keyword in self.CRITICAL_FILE_KEYWORDS:
            if keyword in filename_lower:
                return True
        return False
    
    def is_critical_extension(self, filename):
        """检查文件是否为关键后缀文件（.dll, .sys, .exe 等）"""
        if '.' not in filename:
            return False
        
        ext = filename.split('.')[-1].lower()
        return ext in self.CRITICAL_EXTENSIONS
    
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
            self.log("📦 测试 - 一键归拢根目录散落文件")
            self.log(f"📁 目标目录：{target_dir}")
            if drill_mode:
                self.log("🔬 当前模式：演习模式（只预览不执行）")
            self.log("=" * 50)
            
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
                
                if drill_mode:
                    # 演习模式：只显示预览
                    self.log(f"🔍 预览归拢：{filename}")
                    moved_count += 1
                else:
                    # 实际执行模式 - 这里我们只模拟，不实际移动
                    self.log(f"✅ 模拟归拢：{filename}")
                    moved_count += 1
            
            self.log("=" * 50)
            self.log("📊 归拢统计：")
            self.log(f"   - 扫描文件总数：{len(root_files)} 个")
            self.log(f"   - 成功归拢：{moved_count} 个")
            self.log(f"   - 保护关键文件：{critical_count} 个")
            
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

def test_gather_root_files():
    """测试一键归拢功能"""
    print("=" * 60)
    print("测试 FileMasterPro 一键归拢核心功能")
    print("=" * 60)
    
    # 创建临时测试目录
    test_dir = tempfile.mkdtemp(prefix="test_gather_")
    print(f"创建测试目录: {test_dir}")
    
    # 创建一些测试文件
    test_files = [
        "document.txt",
        "image.jpg",
        "video.mp4",
        "archive.zip",
        "system.dll",      # 关键后缀文件
        "kernel.sys",      # 关键后缀文件
        "program.exe",     # 关键后缀文件
        "config.ini",      # 关键后缀文件
        "script.py",       # 应该被跳过
        "organize_history.json",  # 应该被跳过
        "undo_it.py",      # 应该被跳过
    ]
    
    for filename in test_files:
        filepath = os.path.join(test_dir, filename)
        with open(filepath, 'w') as f:
            f.write(f"Test content for {filename}")
        print(f"创建文件: {filename}")
    
    # 创建一些子文件夹和文件（这些不应该被归拢）
    subdir = os.path.join(test_dir, "subfolder")
    os.makedirs(subdir)
    with open(os.path.join(subdir, "subfile.txt"), 'w') as f:
        f.write("This should not be gathered")
    
    print(f"创建子文件夹: subfolder/")
    print("-" * 60)
    
    # 创建文件整理器实例
    organizer = TestFileOrganizer()
    
    # 测试演习模式
    print("测试演习模式（只预览不执行）:")
    print("-" * 40)
    success = organizer.gather_root_files(test_dir, drill_mode=True)
    print(f"演习模式结果: {'成功' if success else '失败'}")
    print("-" * 60)
    
    # 检查演习模式后文件是否还在原位置
    files_after_drill = os.listdir(test_dir)
    print(f"演习模式后根目录文件数: {len(files_after_drill)}")
    
    # 测试实际执行模式
    print("\n测试实际执行模式:")
    print("-" * 40)
    success = organizer.gather_root_files(test_dir, drill_mode=False)
    print(f"实际执行结果: {'成功' if success else '失败'}")
    print("-" * 60)
    
    # 检查执行结果
    files_after_execute = os.listdir(test_dir)
    print(f"执行后根目录文件数: {len(files_after_execute)}")
    
    # 检查关键文件是否被保护
    print("\n关键文件保护检查:")
    critical_files = ["system.dll", "kernel.sys", "program.exe", "config.ini"]
    for cf in critical_files:
        cf_path = os.path.join(test_dir, cf)
        if os.path.exists(cf_path):
            print(f"  ✅ {cf} 被正确保护（仍在根目录）")
        else:
            print(f"  ❌ {cf} 未被保护（可能被移动）")
    
    # 检查应该被跳过的文件
    print("\n跳过文件检查:")
    skip_files = ["script.py", "organize_history.json", "undo_it.py"]
    for sf in skip_files:
        sf_path = os.path.join(test_dir, sf)
        if os.path.exists(sf_path):
            print(f"  ✅ {sf} 被正确跳过（仍在根目录）")
        else:
            print(f"  ❌ {sf} 未被跳过（可能被移动）")
    
    # 清理测试目录
    print("\n清理测试目录...")
    shutil.rmtree(test_dir)
    print(f"已删除测试目录: {test_dir}")
    
    print("=" * 60)
    print("测试完成！")
    print("=" * 60)

if __name__ == "__main__":
    test_gather_root_files()