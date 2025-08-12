#!/usr/bin/env python3.8
# -*- coding: utf-8 -*-
"""
基础功能测试脚本
用于验证工具的基本功能是否正常
"""

import os
import sys
import time
from pathlib import Path

# 添加项目根目录到Python路径
project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if project_root not in sys.path:
    sys.path.insert(0, project_root)

def test_imports():
    """测试模块导入"""
    print("=== 测试模块导入 ===")
    
    try:
        from src.core.main import AutomationTool
        print("✓ main.py 导入成功")
    except Exception as e:
        print(f"✗ main.py 导入失败: {e}")
        return False
    
    try:
        from src.core.task_executor import TaskExecutor
        print("✓ task_executor.py 导入成功")
    except Exception as e:
        print(f"✗ task_executor.py 导入失败: {e}")
        return False
    
    try:
        from src.core.config import Config, XPathSelectors, BACKGROUND_OPTIONS
        print("✓ config.py 导入成功")
    except Exception as e:
        print(f"✗ config.py 导入失败: {e}")
        return False
    
    try:
        from src.utils import cli
        print("✓ cli.py 导入成功")
    except Exception as e:
        print(f"✗ cli.py 导入失败: {e}")
        return False
    
    return True

def test_python_version():
    """测试Python版本"""
    print("\n=== 测试Python版本 ===")
    
    # 检查Python版本
    python_version = sys.version_info
    if python_version >= (3, 8):
        print(f"✓ Python版本: {python_version.major}.{python_version.minor}.{python_version.micro}")
        if python_version[:3] == (3, 8, 10):
            print("  ✓ 使用推荐的系统自带版本 3.8.10")
    else:
        print(f"✗ Python版本过低: {python_version.major}.{python_version.minor}.{python_version.micro}")
        print("  需要Python 3.8.10或更高版本")
        return False
    
    return True

def check_environment():
    """检查环境"""
    print("\n=== 环境检查 ===")
    
    # 检查Python版本
    if not test_python_version():
        return False
    
    return True

def test_dependencies():
    """测试依赖包"""
    print("\n=== 测试依赖包 ===")
    
    dependencies = [
        ('selenium', 'Selenium WebDriver'),
        ('requests', 'HTTP请求库'),
        ('PIL', 'Pillow图像处理'),
        ('dotenv', 'python-dotenv环境变量'),
        ('webdriver_manager', 'WebDriver管理器')
    ]
    
    all_ok = True
    for module, desc in dependencies:
        try:
            __import__(module)
            print(f"✓ {desc} 可用")
        except ImportError:
            print(f"✗ {desc} 未安装")
            all_ok = False
    
    return all_ok

def test_config():
    """测试配置"""
    print("\n=== 测试配置 ===")
    
    try:
        from config import Config
        
        # 测试配置属性
        print(f"下载目录: {Config.DOWNLOAD_DIR}")
        print(f"日志级别: {Config.LOG_LEVEL}")
        print(f"等待超时: {Config.WAIT_TIMEOUT}")
        print(f"API密钥: {'已配置' if Config.TENCENT_API_KEY else '未配置'}")
        
        # 测试目录创建
        download_dir = Config.ensure_download_dir()
        if os.path.exists(download_dir):
            print(f"✓ 下载目录创建成功: {download_dir}")
        else:
            print(f"✗ 下载目录创建失败: {download_dir}")
            return False
        
        return True
        
    except Exception as e:
        print(f"✗ 配置测试失败: {e}")
        return False

def test_selectors():
    """测试选择器配置"""
    print("\n=== 测试选择器配置 ===")
    
    try:
        from config import XPathSelectors, BACKGROUND_OPTIONS
        
        # 测试通用选择器
        common = XPathSelectors.get_selectors('common')
        print(f"✓ 通用选择器数量: {len(common)}")
        
        # 测试标注平台选择器
        annotation = XPathSelectors.get_selectors('annotation')
        print(f"✓ 标注平台选择器数量: {len(annotation)}")
        
        # 测试背景选项
        print(f"✓ 背景选项数量: {len(BACKGROUND_OPTIONS)}")
        
        return True
        
    except Exception as e:
        print(f"✗ 选择器测试失败: {e}")
        return False

def test_chrome_driver():
    """测试Chrome驱动（可选）"""
    print("\n=== 测试Chrome驱动 ===")
    
    try:
        from selenium import webdriver
        from selenium.webdriver.chrome.service import Service
        # from webdriver_manager.chrome import ChromeDriverManager  # 不再需要，使用本地chromedriver.exe
        
        print("正在下载/检查Chrome驱动...")
        
        options = webdriver.ChromeOptions()
        options.add_argument('--headless')
        options.add_argument('--no-sandbox')
        options.add_argument('--disable-dev-shm-usage')
        options.add_argument('--disable-gpu')
        
        # 使用本地chromedriver.exe
        chromedriver_path = os.path.join(os.getcwd(), 'chromedriver.exe')
        service = Service(chromedriver_path)
        driver = webdriver.Chrome(service=service, options=options)
        
        # 简单测试
        driver.get("data:text/html,<html><body><h1>Test</h1></body></html>")
        title = driver.title
        driver.quit()
        
        print("✓ Chrome驱动测试成功")
        return True
        
    except Exception as e:
        print(f"✗ Chrome驱动测试失败: {e}")
        print("  这可能是因为Chrome浏览器未安装或网络问题")
        return False

def test_automation_tool_init():
    """测试自动化工具初始化"""
    print("\n=== 测试自动化工具初始化 ===")
    
    try:
        from main import AutomationTool
        
        print("正在初始化自动化工具...")
        tool = AutomationTool()
        
        if tool.driver:
            print("✓ 自动化工具初始化成功")
            tool.close()
            return True
        else:
            print("✗ 自动化工具初始化失败")
            return False
            
    except Exception as e:
        print(f"✗ 自动化工具初始化失败: {e}")
        return False

def test_file_structure():
    """测试文件结构"""
    print("\n=== 测试文件结构 ===")
    
    required_files = [
        'main.py',
        'task_executor.py',
        'config.py',
        'cli.py',
        'requirements.txt',
        '.env.example',
        'README.md',
        'run.py',
        'example.py'
    ]
    
    all_ok = True
    for file in required_files:
        if os.path.exists(file):
            print(f"✓ {file} 存在")
        else:
            print(f"✗ {file} 缺失")
            all_ok = False
    
    return all_ok

def run_all_tests():
    """运行所有测试"""
    print("数据标注自动化工具 - 基础功能测试")
    print("=" * 50)
    
    tests = [
        ("Python版本", test_python_version),
        ("文件结构", test_file_structure),
        ("模块导入", test_imports),
        ("依赖包", test_dependencies),
        ("配置", test_config),
        ("选择器", test_selectors),
    ]
    
    # 可选测试（可能失败但不影响基本功能）
    optional_tests = [
        ("Chrome驱动", test_chrome_driver),
        ("工具初始化", test_automation_tool_init),
    ]
    
    results = []
    
    # 运行必需测试
    for name, test_func in tests:
        try:
            result = test_func()
            results.append((name, result, True))  # True表示必需测试
        except Exception as e:
            print(f"\n✗ {name} 测试异常: {e}")
            results.append((name, False, True))
    
    # 运行可选测试
    for name, test_func in optional_tests:
        try:
            result = test_func()
            results.append((name, result, False))  # False表示可选测试
        except Exception as e:
            print(f"\n⚠️  {name} 测试异常: {e}")
            results.append((name, False, False))
    
    # 显示测试结果
    print("\n" + "=" * 50)
    print("测试结果汇总:")
    print("=" * 50)
    
    required_passed = 0
    required_total = 0
    optional_passed = 0
    optional_total = 0
    
    for name, passed, required in results:
        status = "✓" if passed else "✗"
        test_type = "必需" if required else "可选"
        print(f"{status} {name} ({test_type})")
        
        if required:
            required_total += 1
            if passed:
                required_passed += 1
        else:
            optional_total += 1
            if passed:
                optional_passed += 1
    
    print("\n" + "-" * 30)
    print(f"必需测试: {required_passed}/{required_total} 通过")
    print(f"可选测试: {optional_passed}/{optional_total} 通过")
    
    if required_passed == required_total:
        print("\n🎉 所有必需测试都通过了！工具基本功能正常。")
        if optional_passed < optional_total:
            print("⚠️  部分可选功能可能需要额外配置（如Chrome浏览器、API密钥等）")
    else:
        print("\n❌ 部分必需测试失败，请检查安装和配置。")
        print("建议运行: pip install -r requirements.txt")
    
    return required_passed == required_total

def main():
    """主函数"""
    # 切换到脚本目录
    script_dir = Path(__file__).parent
    os.chdir(script_dir)
    
    try:
        success = run_all_tests()
        
        print("\n" + "=" * 50)
        if success:
            print("测试完成！可以开始使用工具了。")
            print("\n快速开始:")
            print("1. 运行 'python run.py' 使用快速启动")
            print("2. 运行 'python cli.py' 使用命令行界面")
            print("3. 运行 'python example.py' 查看使用示例")
        else:
            print("测试发现问题，请先解决后再使用。")
            
    except KeyboardInterrupt:
        print("\n\n测试被用户中断")
    except Exception as e:
        print(f"\n测试过程出错: {e}")

if __name__ == "__main__":
    main()