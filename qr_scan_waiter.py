#!/usr/bin/env python3.8
# -*- coding: utf-8 -*-
"""
等待二维码扫描并自动进入主页面的脚本
"""

import os
import time
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
from selenium.common.exceptions import TimeoutException, WebDriverException, NoSuchElementException

def wait_for_qr_scan_and_enter_main():
    """等待二维码扫描并进入企鹅标注平台主页面"""
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
        chromedriver_path = os.path.join(os.getcwd(), 'chromedriver.exe')
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
        
        print("\n=== 企鹅标注平台二维码扫描等待 ===")
        print("✓ 页面已加载，请使用手机扫描页面上的二维码")
        print("✓ 系统将自动检测扫描状态并进入主页面")
        print("✓ 请保持浏览器窗口打开...")
        
        # 开始监控二维码扫描状态
        scan_timeout = 300  # 5分钟超时
        check_interval = 3  # 每3秒检查一次
        start_time = time.time()
        
        print(f"\n开始监控二维码扫描状态（超时时间: {scan_timeout}秒）...")
        
        while True:
            current_time = time.time()
            elapsed_time = current_time - start_time
            
            # 检查是否超时
            if elapsed_time > scan_timeout:
                print("\n⚠ 等待超时，请重新扫描二维码")
                break
            
            try:
                # 检查当前URL是否已经跳转
                current_url = driver.current_url
                
                # 如果URL发生变化，说明扫描成功
                if "login" not in current_url or "personal-center" in current_url:
                    print("\n✅ 检测到二维码扫描成功！")
                    print(f"当前URL: {current_url}")
                    print(f"页面标题: {driver.title}")
                    
                    # 等待主页面完全加载
                    print("等待主页面加载...")
                    time.sleep(5)
                    
                    try:
                        WebDriverWait(driver, 10).until(
                            lambda d: d.execute_script("return document.readyState") == "complete"
                        )
                        print("✅ 主页面加载完成")
                    except TimeoutException:
                        print("主页面加载超时，但继续")
                    
                    # 检查页面内容
                    try:
                        page_source = driver.page_source
                        if "个人中心" in page_source or "questions-processing" in current_url:
                            print("✅ 成功进入企鹅标注平台主页面")
                        else:
                            print("⚠ 页面可能还在加载中")
                    except Exception as e:
                        print(f"检查页面内容时出错: {e}")
                    
                    print("\n=== 成功进入企鹅标注平台主页面 ===")
                    print("您现在可以开始使用平台功能")
                    break
                
                # 检查是否有错误信息
                try:
                    error_elements = driver.find_elements(By.XPATH, "//*[contains(text(), '错误') or contains(text(), 'error') or contains(text(), '失败')]")
                    if error_elements:
                        print("\n⚠ 检测到页面错误信息，请检查网络连接或重新扫描")
                except:
                    pass
                
                # 显示等待进度
                remaining_time = scan_timeout - elapsed_time
                print(f"\r等待扫描中... 剩余时间: {int(remaining_time)}秒", end="", flush=True)
                
            except Exception as e:
                print(f"\n检查状态时出错: {e}")
            
            # 等待下次检查
            time.sleep(check_interval)
        
        # 扫描完成后的交互
        print("\n\n输入命令:")
        print("- 'status' : 显示当前页面状态")
        print("- 'url' : 显示当前URL")
        print("- 'title' : 显示页面标题")
        print("- 'refresh' : 刷新页面")
        print("- 'quit' : 退出程序")
        
        while True:
            try:
                cmd = input("\n> ").strip().lower()
                if cmd == 'quit':
                    break
                elif cmd == 'status':
                    print(f"当前URL: {driver.current_url}")
                    print(f"页面标题: {driver.title}")
                    print(f"页面状态: {'已登录' if 'login' not in driver.current_url else '未登录'}")
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
                    print("未知命令，请输入 'status', 'url', 'title', 'refresh' 或 'quit'")
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
    wait_for_qr_scan_and_enter_main()