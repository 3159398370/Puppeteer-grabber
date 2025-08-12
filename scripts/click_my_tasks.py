#!/usr/bin/env python3.8
# -*- coding: utf-8 -*-
"""
在企鹅标注平台主页面点击"我的任务"的脚本
"""

import os
import time
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
from selenium.common.exceptions import TimeoutException, WebDriverException, NoSuchElementException
from selenium.webdriver.common.action_chains import ActionChains

def click_my_tasks():
    """在企鹅标注平台主页面点击我的任务"""
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
        
        print("\n=== 企鹅标注平台二维码扫描等待 ===")
        print("✓ 页面已加载，请使用手机扫描页面上的二维码")
        print("✓ 系统将自动检测扫描状态并点击我的任务")
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
                    
                    print("\n=== 开始查找并点击我的任务 ===")
                    
                    # 查找"我的任务"按钮
                    my_tasks_xpath = "/html/body/div[1]/div/div[1]/div[2]/div[1]/ul/a[2]"
                    
                    try:
                        # 等待元素可见
                        print(f"查找元素: {my_tasks_xpath}")
                        my_tasks_element = WebDriverWait(driver, 15).until(
                            EC.element_to_be_clickable((By.XPATH, my_tasks_xpath))
                        )
                        
                        print("✅ 找到我的任务按钮")
                        
                        # 滚动到元素位置
                        driver.execute_script("arguments[0].scrollIntoView(true);", my_tasks_element)
                        time.sleep(1)
                        
                        # 获取元素文本
                        element_text = my_tasks_element.text
                        print(f"按钮文本: {element_text}")
                        
                        # 点击元素
                        print("正在点击我的任务...")
                        my_tasks_element.click()
                        
                        # 等待页面跳转
                        time.sleep(3)
                        
                        # 检查是否成功跳转
                        new_url = driver.current_url
                        new_title = driver.title
                        
                        print("\n✅ 成功点击我的任务！")
                        print(f"新页面URL: {new_url}")
                        print(f"新页面标题: {new_title}")
                        
                        # 验证是否进入了正确的页面
                        if "task" in new_url.lower() or "任务" in new_title:
                            print("✅ 确认已进入我的任务页面")
                        else:
                            print("⚠ 页面可能还在加载或跳转中")
                        
                    except TimeoutException:
                        print("❌ 超时：未找到我的任务按钮")
                        print("尝试查找页面中的所有链接...")
                        
                        # 尝试查找所有可能的链接
                        try:
                            links = driver.find_elements(By.TAG_NAME, "a")
                            print(f"找到 {len(links)} 个链接:")
                            for i, link in enumerate(links[:10]):  # 只显示前10个
                                try:
                                    link_text = link.text.strip()
                                    link_href = link.get_attribute("href")
                                    if link_text:
                                        print(f"  {i+1}. {link_text} -> {link_href}")
                                except:
                                    pass
                        except Exception as e:
                            print(f"查找链接时出错: {e}")
                        
                    except NoSuchElementException:
                        print("❌ 未找到我的任务按钮")
                        
                    except Exception as e:
                        print(f"❌ 点击我的任务时出错: {e}")
                    
                    break
                
                # 显示等待进度
                remaining_time = scan_timeout - elapsed_time
                print(f"\r等待扫描中... 剩余时间: {int(remaining_time)}秒", end="", flush=True)
                
            except Exception as e:
                print(f"\n检查状态时出错: {e}")
            
            # 等待下次检查
            time.sleep(check_interval)
        
        # 操作完成后的交互
        print("\n\n=== 操作完成 ===")
        print("输入命令:")
        print("- 'status' : 显示当前页面状态")
        print("- 'url' : 显示当前URL")
        print("- 'title' : 显示页面标题")
        print("- 'refresh' : 刷新页面")
        print("- 'back' : 返回上一页")
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
                elif cmd == 'back':
                    driver.back()
                    time.sleep(3)
                    print("已返回上一页")
                elif cmd == '':
                    continue
                else:
                    print("未知命令，请输入 'status', 'url', 'title', 'refresh', 'back' 或 'quit'")
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
    click_my_tasks()