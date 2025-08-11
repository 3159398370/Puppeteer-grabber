#!/usr/bin/env python3.8
# -*- coding: utf-8 -*-
"""
导航到指定URL的脚本
"""

import os
import time
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
from selenium.common.exceptions import TimeoutException, WebDriverException

def navigate_to_tencent_label():
    """导航到企鹅标注平台"""
    driver = None
    try:
        # 配置Chrome选项
        options = webdriver.ChromeOptions()
        options.add_argument('--no-sandbox')
        options.add_argument('--disable-dev-shm-usage')
        options.add_argument('--disable-blink-features=AutomationControlled')
        options.add_argument('--ignore-ssl-errors=yes')
        options.add_argument('--ignore-certificate-errors')
        options.add_argument('--allow-running-insecure-content')
        options.add_argument('--disable-web-security')
        options.add_experimental_option("excludeSwitches", ["enable-automation"])
        options.add_experimental_option('useAutomationExtension', False)
        
        # 使用本地chromedriver.exe
        chromedriver_path = os.path.join(os.getcwd(), 'chromedriver.exe')
        service = Service(chromedriver_path)
        
        # 启动浏览器
        print("正在启动Chrome浏览器...")
        driver = webdriver.Chrome(service=service, options=options)
        driver.execute_script("Object.defineProperty(navigator, 'webdriver', {get: () => undefined})")
        
        # 设置窗口大小
        driver.maximize_window()
        
        # 导航到目标URL
        target_url = "https://qlabel.tencent.com/v2/login?redirect=%2Fpersonal-center%2Fquestions-processing"
        print(f"正在导航到: {target_url}")
        driver.get(target_url)
        
        # 等待页面加载
        print("等待页面加载完成...")
        time.sleep(5)
        
        # 检查页面状态
        try:
            current_url = driver.current_url
            page_title = driver.title
            print(f"✓ 成功导航到企鹅标注平台")
            print(f"当前页面标题: {page_title}")
            print(f"当前页面URL: {current_url}")
            
            # 检查页面是否包含登录元素
            try:
                # 等待页面完全加载
                WebDriverWait(driver, 10).until(
                    lambda d: d.execute_script("return document.readyState") == "complete"
                )
                print("页面已完全加载")
                
                # 获取页面源码的前500个字符来确认页面内容
                page_source_preview = driver.page_source[:500]
                print(f"页面内容预览: {page_source_preview}...")
                
            except TimeoutException:
                print("页面加载超时，但浏览器已打开")
                
        except Exception as e:
            print(f"获取页面信息时出错: {e}")
        
        print("\n=== 浏览器已成功打开并导航到目标页面 ===")
        print("Chrome浏览器现在显示企鹅标注平台登录页面")
        print("请按照后续指令进行操作")
        print("浏览器将保持打开状态，等待您的下一步指令...")
        
        # 保持浏览器打开，等待用户指令
        while True:
            try:
                user_input = input("\n输入 'status' 查看当前状态，输入 'quit' 退出: ")
                if user_input.lower() == 'quit':
                    break
                elif user_input.lower() == 'status':
                    print(f"当前URL: {driver.current_url}")
                    print(f"页面标题: {driver.title}")
                else:
                    print("未知命令，请输入 'status' 或 'quit'")
            except KeyboardInterrupt:
                print("\n收到中断信号，准备退出...")
                break
        
    except WebDriverException as e:
        print(f"WebDriver错误: {e}")
    except Exception as e:
        print(f"其他错误: {e}")
    finally:
        if driver:
            print("关闭浏览器...")
            driver.quit()

if __name__ == "__main__":
    navigate_to_tencent_label()