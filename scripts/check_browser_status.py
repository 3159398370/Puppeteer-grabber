#!/usr/bin/env python3.8
# -*- coding: utf-8 -*-
"""
检查浏览器状态的脚本
"""

import os
import time
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.support.ui import WebDriverWait
from selenium.common.exceptions import TimeoutException, WebDriverException

def check_browser_and_navigate():
    """检查浏览器并导航到企鹅标注平台"""
    driver = None
    try:
        # 配置Chrome选项 - 静默模式
        options = webdriver.ChromeOptions()
        options.add_argument('--no-sandbox')
        options.add_argument('--disable-dev-shm-usage')
        options.add_argument('--disable-blink-features=AutomationControlled')
        options.add_argument('--ignore-ssl-errors=yes')
        options.add_argument('--ignore-certificate-errors')
        options.add_argument('--allow-running-insecure-content')
        options.add_argument('--disable-web-security')
        options.add_argument('--log-level=3')  # 只显示致命错误
        options.add_argument('--silent')
        options.add_experimental_option("excludeSwitches", ["enable-automation", "enable-logging"])
        options.add_experimental_option('useAutomationExtension', False)
        
        # 使用本地chromedriver.exe
        # 获取脚本所在目录的上级目录（项目根目录）
        script_dir = os.path.dirname(os.path.abspath(__file__))
        project_root = os.path.dirname(script_dir)
        chromedriver_path = os.path.join(project_root, 'chromedriver.exe')
        service = Service(chromedriver_path)
        service.log_path = os.devnull  # 禁用日志
        
        print("=== 启动Chrome浏览器 ===")
        driver = webdriver.Chrome(service=service, options=options)
        driver.execute_script("Object.defineProperty(navigator, 'webdriver', {get: () => undefined})")
        
        # 设置窗口大小
        driver.maximize_window()
        
        # 导航到目标URL
        target_url = "https://qlabel.tencent.com/v2/login?redirect=%2Fpersonal-center%2Fquestions-processing"
        print(f"导航到: {target_url}")
        driver.get(target_url)
        
        # 等待页面加载
        print("等待页面加载...")
        time.sleep(5)
        
        # 等待页面完全加载
        try:
            WebDriverWait(driver, 15).until(
                lambda d: d.execute_script("return document.readyState") == "complete"
            )
        except TimeoutException:
            print("页面加载超时，但继续检查状态")
        
        # 获取页面信息
        current_url = driver.current_url
        page_title = driver.title
        
        print("\n=== 页面状态信息 ===")
        print(f"✓ 当前URL: {current_url}")
        print(f"✓ 页面标题: {page_title}")
        
        # 检查页面内容
        try:
            page_source = driver.page_source
            if "企鹅标注" in page_source or "腾讯" in page_source or "tencent" in page_source.lower() or "login" in page_source.lower():
                print("✓ 页面内容确认: 已成功加载企鹅标注平台页面")
            else:
                print("⚠ 页面内容可能未完全加载")
                
            # 显示页面源码的前200个字符
            preview = page_source[:200].replace('\n', ' ').replace('\t', ' ')
            print(f"页面内容预览: {preview}...")
            
        except Exception as e:
            print(f"获取页面内容时出错: {e}")
        
        print("\n=== 浏览器已成功打开并导航到目标页面 ===")
        print("Chrome浏览器现在显示企鹅标注平台登录页面")
        print("请在浏览器中进行后续操作，或等待进一步指令")
        
        # 简单的状态检查循环
        print("\n输入命令:")
        print("- 'url' : 显示当前URL")
        print("- 'title' : 显示页面标题")
        print("- 'refresh' : 刷新页面")
        print("- 'quit' : 退出程序")
        
        while True:
            try:
                cmd = input("\n> ").strip().lower()
                if cmd == 'quit':
                    break
                elif cmd == 'url':
                    print(f"当前URL: {driver.current_url}")
                elif cmd == 'title':
                    print(f"页面标题: {driver.title}")
                elif cmd == 'refresh':
                    driver.refresh()
                    time.sleep(3)
                    print("页面已刷新")
                elif cmd == '':
                    continue
                else:
                    print("未知命令，请输入 'url', 'title', 'refresh' 或 'quit'")
            except KeyboardInterrupt:
                print("\n收到中断信号，退出程序")
                break
                
    except WebDriverException as e:
        print(f"WebDriver错误: {e}")
    except Exception as e:
        print(f"其他错误: {e}")
    finally:
        if driver:
            print("\n关闭浏览器...")
            driver.quit()
            print("浏览器已关闭")

if __name__ == "__main__":
    check_browser_and_navigate()