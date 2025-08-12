#!/usr/bin/env python3.8
# -*- coding: utf-8 -*-
"""
快速启动脚本
提供简单的启动选项
"""

import os
import sys
import subprocess
from pathlib import Path

# 全局变量存储Python路径
PYTHON_PATH = sys.executable

def check_requirements():
    """检查依赖是否安装"""
    try:
        import selenium
        import requests
        import PIL
        from dotenv import load_dotenv
        return True
    except ImportError as e:
        print(f"缺少依赖包: {e}")
        return False

def install_requirements():
    """安装依赖包"""
    print("正在安装依赖包...")
    try:
        subprocess.check_call([PYTHON_PATH, "-m", "pip", "install", "-r", "requirements.txt"])
        print("依赖包安装完成！")
        return True
    except subprocess.CalledProcessError:
        print(f"依赖包安装失败，请手动运行: {PYTHON_PATH} -m pip install -r requirements.txt")
        return False

def check_chrome():
    """检查Chrome浏览器"""
    try:
        from selenium import webdriver
        from selenium.webdriver.chrome.service import Service
        # from webdriver_manager.chrome import ChromeDriverManager  # 不再需要，使用本地chromedriver.exe
        
        # 尝试初始化Chrome驱动
        options = webdriver.ChromeOptions()
        options.add_argument('--headless')
        options.add_argument('--no-sandbox')
        options.add_argument('--disable-dev-shm-usage')
        
        # 使用本地chromedriver.exe
        chromedriver_path = os.path.join(os.getcwd(), 'chromedriver.exe')
        service = Service(chromedriver_path)
        driver = webdriver.Chrome(service=service, options=options)
        driver.quit()
        
        print("✓ Chrome浏览器检查通过")
        return True
    except Exception as e:
        print(f"✗ Chrome浏览器检查失败: {e}")
        print("请确保已安装Chrome浏览器")
        return False

def check_env_config():
    """检查环境配置"""
    env_file = Path('.env')
    env_example = Path('.env.example')
    
    if not env_file.exists():
        if env_example.exists():
            print("未找到.env文件，正在创建...")
            try:
                import shutil
                shutil.copy(env_example, env_file)
                print("✓ 已创建.env文件，请编辑其中的API配置")
            except Exception as e:
                print(f"✗ 创建.env文件失败: {e}")
                return False
        else:
            print("✗ 未找到.env.example文件")
            return False
    
    # 检查API配置
    try:
        from dotenv import load_dotenv
        load_dotenv()
        
        api_key = os.getenv('TENCENT_API_KEY')
        if api_key and api_key != 'your_api_key_here':
            print("✓ API配置已设置")
        else:
            print("⚠️  API配置未设置，部分功能将不可用")
            print("   请编辑.env文件中的TENCENT_API_KEY和TENCENT_API_SECRET")
    except Exception as e:
        print(f"✗ 配置检查失败: {e}")
        return False
    
    return True

def show_startup_menu():
    """显示启动菜单"""
    print("\n" + "="*60)
    print("    数据标注自动化工具 - 快速启动")
    print("="*60)
    print("\n请选择启动方式:")
    print("1. 启动命令行界面 (推荐)")
    print("2. 运行使用示例")
    print("3. 检查系统环境")
    print("4. 安装/更新依赖")
    print("5. 配置API密钥")
    print("0. 退出")
    print("-" * 40)

def run_cli():
    """启动命令行界面"""
    try:
        subprocess.run([PYTHON_PATH, "src/utils/cli.py"])
    except Exception as e:
        print(f"启动CLI失败: {e}")

def run_examples():
    """运行示例"""
    try:
        subprocess.run([PYTHON_PATH, "examples/example.py"])
    except Exception as e:
        print(f"运行示例失败: {e}")

def check_python():
    """检查Python版本"""
    python_paths = [
        "C:\\Users\\a3159\\AppData\\Local\\Programs\\Python\\Python38\\python.exe",
        "python",
        "python3",
        "python3.8"
    ]
    
    for python_path in python_paths:
        try:
            result = subprocess.run([python_path, "--version"], capture_output=True, text=True)
            if result.returncode == 0:
                version = result.stdout.strip()
                print(f"✓ 找到Python: {version} ({python_path})")
                if "3.8.10" in version:
                    print("  ✓ 使用推荐的Python 3.8.10版本")
                    global PYTHON_PATH
                    PYTHON_PATH = python_path
                return True
        except FileNotFoundError:
            continue
    
    print("✗ 未找到Python")
    return False

def check_environment():
    """检查环境"""
    print("\n=== 环境检查 ===")
    
    # 检查Python版本
    if not check_python():
        return False
    
    # 检查依赖
    if check_requirements():
        print("✓ 依赖包检查通过")
    else:
        print("✗ 依赖包检查失败")
        if input("是否现在安装依赖包? (y/n): ").lower() == 'y':
            if not install_requirements():
                return False
    
    # 检查Chrome
    check_chrome()
    
    # 检查配置
    check_env_config()
    
    print("\n环境检查完成！")
    return True

def setup_api_config():
    """配置API"""
    print("\n=== API配置 ===")
    print("请访问腾讯元宝开放平台获取API密钥:")
    print("https://yuanbao.tencent.com")
    print()
    
    api_key = input("请输入API Key: ").strip()
    api_secret = input("请输入API Secret: ").strip()
    agent_id = input("请输入智能体ID (默认: NpqYVYeG7vTS): ").strip()
    token = input("请输入Token (默认: wAyiMAgWBaEg7eKroh406ncUnXYBDlez): ").strip()
    
    if api_key and api_secret:
        env_content = f"""# 腾讯元宝API配置
TENCENT_API_KEY={api_key}
TENCENT_API_SECRET={api_secret}
TENCENT_API_ENDPOINT=https://api.yuanbao.tencent.com

# 智能体配置
AGENT_ID={agent_id or 'NpqYVYeG7vTS'}
TOKEN={token or 'wAyiMAgWBaEg7eKroh406ncUnXYBDlez'}

# 其他配置
DOWNLOAD_DIR=./downloads
LOG_LEVEL=INFO
BROWSER_HEADLESS=false
WAIT_TIMEOUT=10"""
        
        try:
            with open('.env', 'w', encoding='utf-8') as f:
                f.write(env_content)
            print("\n✓ API配置已保存到.env文件")
            print("配置完成！")
        except Exception as e:
            print(f"✗ 保存配置失败: {e}")
    else:
        print("API密钥不能为空")

def main():
    """主函数"""
    # 切换到脚本目录
    script_dir = Path(__file__).parent
    os.chdir(script_dir)
    
    try:
        while True:
            show_startup_menu()
            choice = input("请选择 (0-5): ").strip()
            
            if choice == '0':
                print("\n再见！")
                break
            elif choice == '1':
                print("\n启动命令行界面...")
                run_cli()
            elif choice == '2':
                print("\n运行使用示例...")
                run_examples()
            elif choice == '3':
                check_environment()
            elif choice == '4':
                if not check_requirements():
                    install_requirements()
                else:
                    print("依赖包已安装")
            elif choice == '5':
                setup_api_config()
            else:
                print("无效选择，请重新输入")
            
            if choice != '0':
                input("\n按回车键继续...")
                
    except KeyboardInterrupt:
        print("\n\n程序被用户中断")
    except Exception as e:
        print(f"\n程序运行出错: {e}")

if __name__ == "__main__":
    main()