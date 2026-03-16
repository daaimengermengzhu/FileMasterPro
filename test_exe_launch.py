#!/usr/bin/env python3
"""
测试打包后的可执行文件
"""

import os
import subprocess
import time
import sys

def test_executable():
    """测试可执行文件"""
    print("=" * 60)
    print("测试打包后的可执行文件")
    print("=" * 60)
    
    exe_path = os.path.join("dist", "全能文件整理大师Pro.exe")
    
    if not os.path.exists(exe_path):
        print(f"❌ 可执行文件不存在: {exe_path}")
        return False
    
    print(f"✅ 找到可执行文件: {exe_path}")
    print(f"📊 文件大小: {os.path.getsize(exe_path) / 1024 / 1024:.2f} MB")
    
    # 检查文件属性
    import stat
    st = os.stat(exe_path)
    print(f"📅 最后修改时间: {time.ctime(st.st_mtime)}")
    
    # 尝试运行程序（短暂运行后关闭）
    print("\n🚀 尝试启动程序...")
    print("注意：由于使用了 --noconsole 参数，程序将在后台运行")
    print("请查看任务管理器或桌面是否有程序窗口出现")
    
    try:
        # 使用 subprocess 启动程序
        process = subprocess.Popen(
            [exe_path],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            universal_newlines=True  # 替代 text=True
        )
        
        print("✅ 程序启动成功！")
        print(f"📊 进程ID: {process.pid}")
        
        # 等待几秒钟让程序初始化
        print("⏳ 等待程序初始化...")
        time.sleep(3)
        
        # 检查进程是否还在运行
        if process.poll() is None:
            print("✅ 程序仍在运行中")
            
            # 尝试终止进程
            print("🛑 终止测试进程...")
            process.terminate()
            time.sleep(1)
            
            if process.poll() is None:
                process.kill()
                print("⚠️ 需要强制终止进程")
            else:
                print("✅ 进程已正常终止")
        else:
            print("⚠️ 程序已自行退出")
            stdout, stderr = process.communicate()
            if stdout:
                print(f"📝 标准输出: {stdout[:200]}...")
            if stderr:
                print(f"⚠️ 错误输出: {stderr[:200]}...")
        
        return True
        
    except Exception as e:
        print(f"❌ 启动程序失败: {e}")
        return False

def create_shortcut_script():
    """创建快捷启动脚本"""
    print("\n" + "=" * 60)
    print("创建快捷启动脚本")
    print("=" * 60)
    
    shortcut_content = """@echo off
echo 启动 全能文件整理大师Pro...
echo.
echo 软件功能：
echo   - 🎯 智能文件整理（10+文件类型）
echo   - 🔍 深度递归扫描
echo   - 🔬 演习模式（预览效果）
echo   - 🛡️ 白名单保护（系统文件保护）
echo   - 🗑️ 回收站功能（安全删除）
echo   - 💊 一键撤销（后悔药）
echo   - 📦 一键归拢（整理散落文件）
echo.
echo 正在启动主程序...
start "" "%~dp0全能文件整理大师Pro.exe"
echo.
echo 程序已启动！请查看桌面窗口。
pause
"""
    
    shortcut_path = "启动全能文件整理大师Pro.bat"
    
    with open(shortcut_path, "w", encoding="gbk") as f:
        f.write(shortcut_content)
    
    print(f"✅ 已创建启动脚本: {shortcut_path}")
    print("💡 使用方法:")
    print(f"   1. 将 {shortcut_path} 和 dist/全能文件整理大师Pro.exe 一起复制")
    print(f"   2. 双击 {shortcut_path} 即可启动程序")
    print(f"   3. 或直接双击 全能文件整理大师Pro.exe")
    
    return shortcut_path

def main():
    """主函数"""
    print("🚀 全能文件整理大师Pro - 打包验证测试")
    print("=" * 60)
    
    # 测试可执行文件
    success = test_executable()
    
    if success:
        # 创建快捷启动脚本
        shortcut = create_shortcut_script()
        
        print("\n" + "=" * 60)
        print("🎉 打包验证完成！")
        print("=" * 60)
        print("\n📋 生成的文件:")
        print(f"   1. dist/全能文件整理大师Pro.exe (主程序)")
        print(f"   2. {shortcut} (启动脚本)")
        print(f"   3. 全能文件整理大师Pro.spec (打包配置文件)")
        
        print("\n🚀 发布准备:")
        print("   1. 复制 dist/全能文件整理大师Pro.exe 到任意位置")
        print("   2. 双击即可运行（无需安装Python）")
        print("   3. 程序将在后台运行，无控制台窗口")
        
        print("\n⚠️ 注意事项:")
        print("   - 首次运行可能需要几秒钟初始化")
        print("   - 确保有足够的磁盘空间进行文件整理")
        print("   - 建议先使用演习模式熟悉操作")
        
    else:
        print("\n" + "=" * 60)
        print("❌ 打包验证失败")
        print("=" * 60)
    
    print("\n" + "=" * 60)
    print("测试完成！")
    print("=" * 60)

if __name__ == "__main__":
    main()