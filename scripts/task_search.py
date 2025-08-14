#!/usr/bin/env python3.8
# -*- coding: utf-8 -*-
"""
在企鹅标注平台我的任务页面输入任务编号并查询的脚本
"""

import os
import sys
import time
import json 
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
from selenium.common.exceptions import TimeoutException, WebDriverException, NoSuchElementException
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.common.keys import Keys


def search_task_by_number():
    """在企鹅标注平台我的任务页面输入任务编号并查询"""
    driver = None
    
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
    options.add_argument('--disable-gpu')
    options.add_argument('--disable-software-rasterizer')
    options.add_argument('--disable-background-timer-throttling')
    options.add_argument('--disable-backgrounding-occluded-windows')
    options.add_argument('--disable-renderer-backgrounding')
    options.add_argument('--disable-features=TranslateUI')
    options.add_argument('--disable-ipc-flooding-protection')
    options.add_experimental_option("excludeSwitches", ["enable-automation", "enable-logging"])
    options.add_experimental_option('useAutomationExtension', False)

    # 使用固定的用户数据目录以保持登录状态
    script_dir = os.path.dirname(os.path.abspath(__file__))
    project_root = os.path.dirname(script_dir)
    user_data_dir = os.path.join(project_root, 'chrome_user_data')
    
    # 确保用户数据目录存在
    os.makedirs(user_data_dir, exist_ok=True)
    
    options.add_argument(f'--user-data-dir={user_data_dir}')
    options.add_argument('--profile-directory=Default')
    
    print(f"📁 使用用户数据目录: {user_data_dir}")
    print("💡 此配置将保持登录状态，避免重复登录")

    # 使用本地chromedriver.exe
    # 适配PyInstaller打包环境
    if getattr(sys, 'frozen', False):
        # 如果是打包后的exe文件
        application_path = sys._MEIPASS
        chromedriver_path = os.path.join(application_path, 'chromedriver.exe')
    else:
        # 如果是开发环境
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

    # 首先检查是否已经登录
    print("检查登录状态...")

    # 先尝试直接访问任务页面
    task_url = "https://qlabel.tencent.com/v2/personal-center/questions-processing"
    print(f"尝试直接访问任务页面: {task_url}")
    driver.get(task_url)

    # 等待页面加载
    time.sleep(5)

    # 检查是否已经登录（如果没有重定向到登录页面）
    current_url = driver.current_url
    if "login" not in current_url:
        print("✅ 检测到已登录状态，直接进入任务页面")
        print(f"当前URL: {current_url}")
        # 跳过登录流程，直接进入任务编号输入
    else:
        print("❌ 未登录，需要扫描二维码")
        # 导航到登录页面
        target_url = "https://qlabel.tencent.com/v2/login?redirect=%2Fpersonal-center%2Fquestions-processing"
        print(f"导航到登录页面: {target_url}")
        driver.get(target_url)

        # 等待页面加载
        print("等待登录页面加载...")
        time.sleep(5)

    # 等待页面完全加载
    try:
        WebDriverWait(driver, 15).until(
            lambda d: d.execute_script("return document.readyState") == "complete"
        )
    except TimeoutException:
        print("页面加载超时，但继续检查状态")

    # 只有在需要登录时才进行二维码扫描
    if "login" in current_url:
        print("\n=== 企鹅标注平台二维码扫描等待 ===")
        print("✓ 页面已加载，请使用手机扫描页面上的二维码")
        print("✓ 系统将自动检测扫描状态并进入我的任务页面")
        print("✓ 请保持浏览器窗口打开...")

        # 开始监控二维码扫描状态
        scan_timeout = 300  # 5分钟超时
        check_interval = 3  # 每3秒检查一次
        start_time = time.time()

        print(f"\n开始监控二维码扫描状态（超时时间: {scan_timeout}秒）...")
    else:
        print("\n=== 已登录，跳过二维码扫描 ===")

    # 如果已经登录，直接跳到任务编号输入
    if "login" not in current_url:
        print("✅ 已登录，直接进入任务编号输入流程")
        # 直接跳到任务编号输入部分
    else:
        # 需要登录的情况下进行二维码扫描监控
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
                    break  # 跳出二维码扫描循环

            except Exception as e:
                print(f"检查扫描状态时出错: {e}")

            # 等待一段时间再检查
            time.sleep(check_interval)

    # 等待主页面完全加载
    print("等待主页面加载...")
    time.sleep(5)

    try:
        WebDriverWait(driver, 10).until(
            lambda d: d.execute_script("return document.readyState") == "complete"
        )
        print("✅ 主页面加载完成")
    except (TimeoutException, WebDriverException) as e:
        print(f"主页面加载超时或浏览器连接断开: {e}")
        print("尝试重新启动浏览器...")
        if driver:
            try:
                driver.quit()
            except:
                pass
        return

    # 点击我的任务
    print("\n=== 导航到我的任务页面 ===")
    my_tasks_xpath = "/html/body/div[1]/div/div[1]/div[2]/div[1]/ul/a[2]"

    try:
        # 等待元素可见并点击
        print(f"查找我的任务按钮: {my_tasks_xpath}")
        my_tasks_element = WebDriverWait(driver, 15).until(
            EC.element_to_be_clickable((By.XPATH, my_tasks_xpath))
        )

        print("✅ 找到我的任务按钮")

        # 多重点击策略
        click_success = False

        # 策略1: 直接点击
        try:
            my_tasks_element.click()
            print("✅ 成功点击我的任务（直接点击）")
            click_success = True
        except Exception as e1:
            print(f"直接点击失败: {e1}")

            # 策略2: JavaScript点击
            try:
                driver.execute_script("arguments[0].click();", my_tasks_element)
                print("✅ 成功点击我的任务（JavaScript点击）")
                click_success = True
            except Exception as e2:
                print(f"JavaScript点击失败: {e2}")

                # 策略3: ActionChains点击
                try:
                    ActionChains(driver).move_to_element(my_tasks_element).click().perform()
                    print("✅ 成功点击我的任务（ActionChains点击）")
                    click_success = True
                except Exception as e3:
                    print(f"ActionChains点击失败: {e3}")

        if click_success:
            # 等待任务页面加载
            time.sleep(5)

            # 检查是否成功进入任务页面
            new_url = driver.current_url
            print(f"当前页面URL: {new_url}")

            if "task" in new_url.lower() or "workbench" in new_url:
                print("✅ 成功进入我的任务页面")
            else:
                print("⚠ 可能还未完全进入任务页面")
        else:
            print("❌ 所有点击策略都失败了")

    except TimeoutException:
        print("❌ 超时：未找到我的任务按钮")
        print("⚠ 尝试BeautifulSoup备用方案...")

        # BeautifulSoup备用方案
        try:
            from bs4 import BeautifulSoup
            page_source = driver.page_source
            soup = BeautifulSoup(page_source, 'html.parser')

            # 查找包含"我的任务"或"任务"文本的链接或按钮
            my_tasks_elements = []

            # 方案1: 查找包含"我的任务"文本的a标签
            nav_links = soup.find_all('a', class_=['nav-link', 'menu-item', 'sidebar-link'])
            for link in nav_links:
                if link.get_text() and ('我的任务' in link.get_text() or '任务' in link.get_text()):
                    my_tasks_elements.append(link)

            if my_tasks_elements:
                print(f"✅ BS4找到 {len(my_tasks_elements)} 个可能的我的任务元素")
                # 尝试点击第一个找到的元素
                first_element = my_tasks_elements[0]

                # 获取元素的href或其他属性来定位
                href = first_element.get('href')
                if href:
                    # 如果有href，直接导航
                    if href.startswith('/'):
                        full_url = driver.current_url.split('/')[0] + '//' + driver.current_url.split('/')[2] + href
                    else:
                        full_url = href

                    print(f"导航到: {full_url}")
                    driver.get(full_url)
                    print("✅ BS4备用方案成功导航到我的任务页面")
                else:
                    print("❌ BS4找到的元素没有有效的href")
            else:
                print("❌ BS4未找到我的任务相关元素")

        except ImportError:
            print("❌ BeautifulSoup4未安装，无法使用备用方案")
        except Exception as bs_e:
            print(f"❌ BS4备用方案失败: {bs_e}")

        print("⚠ 假设您已经在正确的页面上，继续任务编号输入流程...")

    except Exception as e:
        print(f"❌ 点击我的任务时出错: {e}")
        print("⚠ 假设您已经在正确的页面上，继续任务编号输入流程...")
        # 不要break，继续执行任务编号输入

    # 开始任务编号输入流程
    print("\n=== 任务编号输入 ===")

    # 历史记录文件路径
    history_file = "task_history.json"


    # 加载历史记录
    def load_history():
        try:
            if os.path.exists(history_file):
                with open(history_file, 'r', encoding='utf-8') as f:
                    return json.load(f)
        except Exception as e:
            print(f"加载历史记录失败: {e}")
        return []


    # 保存历史记录
    def save_history(history):
        try:
            with open(history_file, 'w', encoding='utf-8') as f:
                json.dump(history, f, ensure_ascii=False, indent=2)
        except Exception as e:
            print(f"保存历史记录失败: {e}")


    # 获取用户输入的任务编号
    while True:
        try:
            # 加载历史记录,如果加载失败则返回空列表
            history = load_history()

            if history:
                print("\n历史任务编号:")
                for i, task_num in enumerate(history, 1):
                    print(f"{i}. {task_num}")
                print(f"{len(history) + 1}. 输入新的任务编号")

                choice = input("\n请选择 (输入数字): ").strip()

                if choice.isdigit():
                    choice_num = int(choice)
                    if 1 <= choice_num <= len(history):
                        task_number = history[choice_num - 1]
                        print(f"您选择的任务编号是: {task_number}")
                        confirm = input("确认使用吗？(y/n): ").strip().lower()
                        if confirm in ['y', 'yes', '是', '确认']:
                            # 将选中的任务编号移到历史记录最前面
                            history.remove(task_number)
                            history.insert(0, task_number)
                            save_history(history)
                            break
                        else:
                            continue
                    elif choice_num == len(history) + 1:
                        # 输入新的任务编号
                        pass
                    else:
                        print("无效的选择，请重新输入")
                        continue
                else:
                    print("请输入有效的数字")
                    continue

            # 输入新的任务编号
            task_number = input("\n请输入当天的任务编号: ").strip()
            if task_number:
                print(f"您输入的任务编号是: {task_number}")
                confirm = input("确认输入吗？(y/n): ").strip().lower()
                if confirm in ['y', 'yes', '是', '确认']:
                    # 保存到历史记录
                    if task_number not in history:
                        history.insert(0, task_number)
                        # 只保留最近10个记录
                        history = history[:10]
                        save_history(history)
                    else:
                        # 将已存在的任务编号移到最前面
                        history.remove(task_number)
                        history.insert(0, task_number)
                        save_history(history)
                    break
                else:
                    print("请重新输入任务编号")
            else:
                print("任务编号不能为空，请重新输入")
        except KeyboardInterrupt:
            print("\n用户取消输入")
            return

    print(f"\n开始在页面中输入任务编号: {task_number}")

    # 查找输入框
    input_xpath = "/html/body/div[1]/div/div[2]/div/div[2]/div/div/div[1]/div[1]/div[1]/form/div/div[1]/div/div/div/input"

    try:
        print(f"查找输入框: {input_xpath}")

        # 等待输入框可见
        input_element = WebDriverWait(driver, 15).until(
            EC.element_to_be_clickable((By.XPATH, input_xpath))
        )

        print("✅ 找到任务编号输入框")

        # 清空输入框并输入任务编号
        input_element.clear()
        time.sleep(0.5)
        input_element.send_keys(task_number)

        print(f"✅ 成功输入任务编号: {task_number}")

        # 等待一下确保输入完成
        time.sleep(1)

        # 查找并点击查询按钮
        search_button_xpath = "/html/body/div[1]/div/div[2]/div/div[2]/div/div/div[1]/div[1]/div[2]/div/div/div[1]/button"

        print(f"查找查询按钮: {search_button_xpath}")

        search_button = WebDriverWait(driver, 10).until(
            EC.element_to_be_clickable((By.XPATH, search_button_xpath))
        )

        print("✅ 找到查询按钮")

        # 尝试多种方式点击查询按钮
        try:
            # 方法1: 直接点击
            search_button.click()
            print("✅ 成功点击查询按钮")
        except Exception as click_error:
            print(f"直接点击失败: {click_error}")
            try:
                # 方法2: JavaScript点击
                driver.execute_script("arguments[0].click();", search_button)
                print("✅ 使用JavaScript成功点击查询按钮")
            except Exception as js_error:
                print(f"JavaScript点击失败: {js_error}")
                try:
                    # 方法3: ActionChains点击
                    ActionChains(driver).move_to_element(search_button).click().perform()
                    print("✅ 使用ActionChains成功点击查询按钮")
                except Exception as action_error:
                    print(f"ActionChains点击失败: {action_error}")
                    # 方法4: 使用BS4定位备用方案
                    print("尝试使用BeautifulSoup备用定位方案...")
                    try:
                        from bs4 import BeautifulSoup

                        page_source = driver.page_source
                        soup = BeautifulSoup(page_source, 'html.parser')

                        # 查找查询按钮
                        query_buttons = soup.find_all('button', {
                            'class': lambda x: x and 't-button' in x and 't-button--theme-primary' in x})
                        print(f"BS4找到 {len(query_buttons)} 个可能的查询按钮")

                        for i, btn in enumerate(query_buttons):
                            btn_text = btn.get_text(strip=True)
                            print(f"  按钮{i + 1}: '{btn_text}'")
                            if '查询' in btn_text:
                                # 尝试通过按钮文本重新定位
                                alt_buttons = driver.find_elements(By.XPATH, "//button[contains(text(), '查询')]")
                                if alt_buttons:
                                    alt_button = alt_buttons[0]
                                    driver.execute_script("arguments[0].click();", alt_button)
                                    print("✅ 使用BS4备用方案成功点击查询按钮")
                                    break
                        else:
                            # 最后尝试：按回车键
                            input_element.send_keys(Keys.RETURN)
                            print("✅ 使用回车键提交查询")
                    except ImportError:
                        print("❌ BeautifulSoup未安装，使用回车键提交")
                        input_element.send_keys(Keys.RETURN)
                    except Exception as bs4_error:
                        print(f"BS4备用方案失败: {bs4_error}")
                        print("使用回车键作为最后尝试")
                        input_element.send_keys(Keys.RETURN)

        # 等待查询结果加载
        print("等待查询结果加载...")
        time.sleep(5)

        print("\n✅ 任务查询完成！")
        print(f"当前页面URL: {driver.current_url}")
        print(f"页面标题: {driver.title}")

        # 等待查询结果显示并点击详情按钮
        print("\n=== 查找并点击详情按钮 ===")
        details_button_xpath = "//*[@id='app']/div/div[2]/div/div[2]/div/div/div[2]/div[1]/div[2]/table/tbody/tr/td[11]/div/div"

        try:
            print(f"查找详情按钮: {details_button_xpath}")

            # 等待页面加载完成，确保没有遮罩层
            print("等待页面完全加载...")
            time.sleep(3)
            
            # 等待可能的加载遮罩消失
            try:
                WebDriverWait(driver, 10).until(
                    EC.invisibility_of_element_located((By.CLASS_NAME, "ivu-spin-fix"))
                )
                print("✅ 加载遮罩已消失")
            except:
                print("⚠ 未检测到加载遮罩或已消失")

            # 等待详情按钮可见并可点击
            details_button = WebDriverWait(driver, 15).until(
                EC.element_to_be_clickable((By.XPATH, details_button_xpath)))

            print("✅ 找到详情按钮")

            # 滚动到按钮位置
            driver.execute_script("arguments[0].scrollIntoView(true);", details_button)
            time.sleep(2)

            # 获取按钮文本
            button_text = details_button.text
            print(f"按钮文本: {button_text}")

            # 多种点击策略
            click_success = False
            
            # 方法1: 直接点击
            try:
                details_button.click()
                print("✅ 成功点击详情按钮（直接点击）")
                click_success = True
            except Exception as e:
                print(f"直接点击失败: {e}")
                
                # 方法2: JavaScript点击
                try:
                    driver.execute_script("arguments[0].click();", details_button)
                    print("✅ 成功点击详情按钮（JavaScript点击）")
                    click_success = True
                except Exception as js_e:
                    print(f"JavaScript点击失败: {js_e}")
                    
                    # 方法3: ActionChains点击
                    try:
                        ActionChains(driver).move_to_element(details_button).pause(1).click().perform()
                        print("✅ 成功点击详情按钮（ActionChains点击）")
                        click_success = True
                    except Exception as ac_e:
                        print(f"ActionChains点击失败: {ac_e}")
            
            if not click_success:
                print("❌ 所有点击方法都失败了")
                return

            # 等待详情页面加载
            time.sleep(3)

            # 检查是否成功跳转到详情页面
            details_url = driver.current_url
            details_title = driver.title

            print("\n✅ 成功进入任务详情页面！")
            print(f"详情页面URL: {details_url}")
            print(f"详情页面标题: {details_title}")

            print("\n✅ 已成功进入任务详情页面！")
            print("📝 请手动点击页面上的'开始标注'按钮来开始标注任务。")
            print("💡 脚本将保持浏览器打开状态，您可以继续进行标注工作。")
            
            # 询问是否启动浮动控制面板
            print("\n🎯 是否启动浮动控制面板？(y/n)")
            print("浮动面板提供以下快捷键功能：")
            print("  ← 左键: 调用API")
            print("  → 右键: 跳过")
            print("  ↑ 上键: 上传")
            print("  ↓ 下键: 提取")
            print("  空格键: 提交")
            
            panel_choice = input("启动浮动面板? (y/n): ").strip().lower()
            if panel_choice in ['y', 'yes', '是']:
                try:
                    # 尝试不同的导入路径以适应打包环境
                    try:
                        from floating_control_panel import create_floating_panel
                    except ImportError:
                        from scripts.floating_control_panel import create_floating_panel
                    print("\n🚀 启动浮动控制面板...")
                    print("⚠️  面板将在新窗口中打开，请保持浏览器窗口活动状态")
                    create_floating_panel(driver)
                except ImportError:
                    print("❌ 无法导入浮动控制面板模块，请确保floating_control_panel.py文件存在")
                except Exception as e:
                    print(f"❌ 启动浮动控制面板失败: {e}")
            else:
                print("跳过浮动面板启动")

        except TimeoutException:
            print("❌ 超时：未找到详情按钮")
            print("尝试查找页面中的所有按钮...")

    except TimeoutException:
        print("❌ 超时：未找到查询按钮")
        print("尝试查找页面中的所有按钮...")

    # 操作完成后的交互
    print("\n\n=== 操作完成 ===")
    print("请选择操作:")
    print("0 - 显示当前页面状态")
    print("1 - 显示当前URL")
    print("2 - 显示页面标题")
    print("3 - 刷新页面")
    print("4 - 返回上一页")
    print("5 - 重新搜索任务")
    print("9 - 退出程序")

    print("\n操作完成！输入 'h' 查看帮助菜单，输入 'q' 退出程序")
    
    while True:
        try:
            cmd = input("\n> ").strip().lower()
            if cmd == 'q':
                break
            elif cmd == 'h':
                print("\n=== 控制面板 ===")
                print("0 - 查看当前页面状态")
                print("1 - 显示当前URL")
                print("2 - 显示页面标题")
                print("3 - 刷新页面")
                print("4 - 返回上一页")
                print("5 - 重新搜索任务")
                print("h - 显示此帮助菜单")
                print("q - 退出程序")
                print("==================")
            elif cmd == '0':
                print(f"\n当前页面状态:")
                print(f"URL: {driver.current_url}")
                print(f"标题: {driver.title}")
                print(f"状态: {'已登录' if 'login' not in driver.current_url else '未登录'}")
            elif cmd == '1':
                print(f"\n当前URL: {driver.current_url}")
            elif cmd == '2':
                print(f"\n页面标题: {driver.title}")
            elif cmd == '3':
                print("\n刷新页面...")
                driver.refresh()
                time.sleep(3)
                print("✅ 页面已刷新")
            elif cmd == '4':
                print("\n返回上一页...")
                driver.back()
                time.sleep(3)
                print("✅ 已返回上一页")
            elif cmd == '5':
                # 重新搜索任务
                task_number = input("\n请输入新的任务编号: ").strip()
                if task_number:
                    try:
                        input_xpath = "/html/body/div[1]/div/div[2]/div/div[2]/div/div/div[1]/div[1]/div[1]/form/div/div[1]/div/div/div/input"
                        input_element = driver.find_element(By.XPATH, input_xpath)
                        input_element.clear()
                        input_element.send_keys(task_number)

                        search_button_xpath = "/html/body/div[1]/div/div[2]/div/div[2]/div/div/div[1]/div[1]/div[2]/div/div/div[1]/button"
                        search_button = driver.find_element(By.XPATH, search_button_xpath)
                        search_button.click()

                        print(f"✅ 重新搜索任务编号: {task_number}")
                        time.sleep(3)
                    except Exception as e:
                        print(f"❌ 重新搜索时出错: {e}")
            elif cmd == '':
                continue
            else:
                print("❌ 无效输入，输入 'h' 查看帮助菜单")
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
    search_task_by_number()
        