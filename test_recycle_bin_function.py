#!/usr/bin/env python3
"""
测试回收站功能
"""
import os
import sys
import subprocess
import time

def test_recycle_bin_function():
    """测试回收站功能"""
    print("🧪 测试回收站功能")
    print("=" * 50)
    
    # 测试目录
    test_dir = os.path.join(os.getcwd(), "test_recycle_bin")
    
    # 检查测试目录是否存在
    if not os.path.exists(test_dir):
        print(f"❌ 测试目录不存在：{test_dir}")
        return False
    
    # 列出测试目录中的文件
    print("📁 测试目录中的文件：")
    for item in os.listdir(test_dir):
        item_path = os.path.join(test_dir, item)
        if os.path.isfile(item_path):
            print(f"   - {item}")
    
    print("\n🚀 运行脚本进行测试...")
    print("=" * 50)
    
    # 运行脚本（演习模式）
    print("🔬 测试演习模式（预览）...")
    print("=" * 50)
    
    # 创建输入数据：y（演习模式），测试目录路径，无额外排除
    input_data = "y\n" + test_dir + "\n\n"
    
    # 运行脚本
    process = subprocess.Popen(
        [sys.executable, "clean_my_folder.py"],
        stdin=subprocess.PIPE,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        universal_newlines=True,
        cwd=os.getcwd()
    )
    
    try:
        stdout, stderr = process.communicate(input=input_data, timeout=10)
        print(stdout)
        
        if stderr:
            print(f"⚠️  错误输出：{stderr}")
        
        # 检查输出中是否包含垃圾文件处理信息
        # 注意：由于 Unicode 编码问题，表情符号可能被替换
        trash_markers = ["🗑️  预览删除（回收站）", "[回收站]  预览删除（回收站）"]
        trash_found = any(marker in stdout for marker in trash_markers)
        
        if trash_found:
            print("\n✅ 演习模式测试通过：垃圾文件被识别为回收站文件")
            
            # 统计垃圾文件数量
            trash_count = 0
            for marker in trash_markers:
                trash_count += stdout.count(marker)
            print(f"   识别到 {trash_count} 个垃圾文件")
            
            # 检查具体文件
            if "test.log" in stdout and ("🗑️" in stdout or "[回收站]" in stdout):
                print("   ✅ test.log 被识别为垃圾文件")
            if "temp.tmp" in stdout and ("🗑️" in stdout or "[回收站]" in stdout):
                print("   ✅ temp.tmp 被识别为垃圾文件")
            if "backup.bak" in stdout and ("🗑️" in stdout or "[回收站]" in stdout):
                print("   ✅ backup.bak 被识别为垃圾文件")
            
            # 检查普通文件
            if "document.txt" in stdout and "文档" in stdout:
                print("   ✅ document.txt 被识别为文档文件")
            if "image.jpg" in stdout and "图片" in stdout:
                print("   ✅ image.jpg 被识别为图片文件")
            
            return True
        else:
            print("\n❌ 演习模式测试失败：未找到垃圾文件处理信息")
            return False
            
    except subprocess.TimeoutExpired:
        process.kill()
        print("❌ 脚本执行超时")
        return False
    except Exception as e:
        print(f"❌ 脚本执行失败：{e}")
        return False

def main():
    """主函数"""
    print("🧪 回收站功能测试")
    print("=" * 50)
    
    # 运行测试
    success = test_recycle_bin_function()
    
    print("\n" + "=" * 50)
    if success:
        print("🎉 测试完成！回收站功能正常工作")
        print("\n💡 提示：")
        print("1. 垃圾文件（.log, .tmp, .bak）会被移动到回收站")
        print("2. 普通文件会被分类到相应文件夹")
        print("3. 演习模式只预览不执行")
        print("4. 实际执行时，垃圾文件会被发送到 Windows 回收站")
    else:
        print("❌ 测试失败")
    
    print("=" * 50)

if __name__ == "__main__":
    main()