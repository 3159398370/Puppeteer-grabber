#!/usr/bin/env python3.8
# -*- coding: utf-8 -*-
"""
浮动控制面板 - 用于标注页面的键盘快捷键控制
功能（已互换左右键和上下键）：
- 左方向键：点击选中按钮（需连续点击两次）
- 右方向键：点击跳过按钮（需连续点击两次）
- 上方向键：上传功能（需连续点击两次）
- 下方向键：提取功能（需连续点击两次）
- 空格键：提交功能（需连续点击两次）
- 自动保存页面源码到data目录用于调试分析
"""

import time
import threading
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException, NoSuchElementException
# 全局变量声明
KEYBOARD_AVAILABLE = False

try:
    import keyboard
    KEYBOARD_AVAILABLE = True
    print("✅ keyboard库已成功导入")
except ImportError:
    KEYBOARD_AVAILABLE = False
    print("⚠️  keyboard库不可用，将使用GUI按钮模式")

import tkinter as tk
from tkinter import ttk

class FloatingControlPanel:
    def __init__(self, driver):
        self.driver = driver
        self.running = False
        self.root = None
        self.status_label = None
        
        # 连续点击检测
        self.last_key_time = {}
        self.double_click_interval = 1.0  # 1秒内连续点击两次才生效
        
        # 按钮XPath配置
        self.button_xpaths = {
            'skip': "//button[contains(@class, 'mrm ivu-btn ivu-btn-default ivu-btn-large')]//span[text()='跳过']/parent::button",
            'select': "//button[contains(@class, 'ivu-btn') and contains(., '选中')]",
            'extract': "//button[contains(@class, 'ivu-btn') and contains(., '提取')]",
            'upload': "//button[contains(@class, 'ivu-btn') and contains(., '上传')]",
            'submit': "//button[contains(@class, 'ivu-btn') and contains(., '提交')]"
        }
        
        # 创建浮动窗口
        self.create_floating_window()
        
        # 启动键盘监听
        self.start_keyboard_listener()
    
    def create_floating_window(self):
        """创建浮动控制面板窗口"""
        self.root = tk.Tk()
        self.root.title("标注控制面板")
        self.root.geometry("300x400")
        self.root.attributes('-topmost', True)  # 窗口置顶
        self.root.attributes('-alpha', 0.9)  # 半透明
        
        # 设置窗口位置（右上角）
        self.root.geometry("+{}+{}".format(self.root.winfo_screenwidth() - 320, 50))
        
        # 创建主框架
        main_frame = ttk.Frame(self.root, padding="10")
        main_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        # 标题
        title_label = ttk.Label(main_frame, text="🎯 标注快捷键控制", font=('Arial', 12, 'bold'))
        title_label.grid(row=0, column=0, columnspan=2, pady=(0, 10))
        
        # 快捷键说明
        shortcuts = [
            ("← 左键", "选中", "left"),
            ("→ 右键", "跳过", "right"),
            ("↑ 上键", "上传", "up"),
            ("↓ 下键", "提取", "down"),
            ("空格键", "提交", "space")
        ]
        
        for i, (key, action, _) in enumerate(shortcuts, 1):
            key_label = ttk.Label(main_frame, text=key, font=('Arial', 10, 'bold'))
            key_label.grid(row=i, column=0, sticky=tk.W, pady=2)
            
            action_label = ttk.Label(main_frame, text=action)
            action_label.grid(row=i, column=1, sticky=tk.W, padx=(10, 0), pady=2)
        
        # 分隔线
        separator = ttk.Separator(main_frame, orient='horizontal')
        separator.grid(row=len(shortcuts)+1, column=0, columnspan=2, sticky=(tk.W, tk.E), pady=10)
        
        # 状态显示
        status_frame = ttk.LabelFrame(main_frame, text="状态", padding="5")
        status_frame.grid(row=len(shortcuts)+2, column=0, columnspan=2, sticky=(tk.W, tk.E), pady=(0, 10))
        
        self.status_label = ttk.Label(status_frame, text="🟢 监听中...", foreground="green")
        self.status_label.grid(row=0, column=0)
        
        # 操作按钮区域
        action_frame = ttk.LabelFrame(main_frame, text="手动操作", padding="5")
        action_frame.grid(row=len(shortcuts)+3, column=0, columnspan=2, sticky=(tk.W, tk.E), pady=(0, 10))
        
        # 第一行按钮
        btn_row1 = ttk.Frame(action_frame)
        btn_row1.grid(row=0, column=0, columnspan=2, pady=2)
        
        ttk.Button(btn_row1, text="跳过", command=lambda: self.manual_action('skip', '跳过')).grid(row=0, column=0, padx=2)
        ttk.Button(btn_row1, text="选中", command=lambda: self.manual_action('select', '选中')).grid(row=0, column=1, padx=2)
        ttk.Button(btn_row1, text="提取", command=lambda: self.manual_action('extract', '提取')).grid(row=0, column=2, padx=2)
        
        # 第二行按钮
        btn_row2 = ttk.Frame(action_frame)
        btn_row2.grid(row=1, column=0, columnspan=2, pady=2)
        
        ttk.Button(btn_row2, text="上传", command=lambda: self.manual_action('upload', '上传')).grid(row=0, column=0, padx=2)
        ttk.Button(btn_row2, text="提交", command=lambda: self.manual_action('submit', '提交')).grid(row=0, column=1, padx=2)
        
        # 控制按钮
        control_frame = ttk.Frame(main_frame)
        control_frame.grid(row=len(shortcuts)+4, column=0, columnspan=2, pady=(0, 10))
        
        self.start_button = ttk.Button(control_frame, text="开始监听", command=self.start_listening)
        self.start_button.grid(row=0, column=0, padx=(0, 5))
        
        self.stop_button = ttk.Button(control_frame, text="停止监听", command=self.stop_listening)
        self.stop_button.grid(row=0, column=1, padx=(5, 0))
        
        # 退出按钮
        exit_button = ttk.Button(main_frame, text="退出面板", command=self.close_panel)
        exit_button.grid(row=len(shortcuts)+5, column=0, columnspan=2, pady=(10, 0))
        
        # 绑定窗口关闭事件
        self.root.protocol("WM_DELETE_WINDOW", self.close_panel)
    
    def update_status(self, message, color="black"):
        """更新状态显示"""
        if self.status_label:
            self.status_label.config(text=message, foreground=color)
    
    def click_button_by_xpath(self, xpath, button_name):
        """根据XPath点击按钮"""
        try:
            # 先尝试查找按钮
            button = WebDriverWait(self.driver, 2).until(
                EC.element_to_be_clickable((By.XPATH, xpath))
            )
            button.click()
            self.update_status(f"✅ {button_name}成功", "green")
            print(f"✅ 成功点击{button_name}按钮")
            return True
        except TimeoutException:
            # 检查是否在标注界面
            current_url = self.driver.current_url
            print(f"🔍 当前URL: {current_url}")
            # 修改判断条件：检查是否包含标注相关的URL特征
            is_annotation_page = (
                "pack_key" in current_url or 
                "annotation" in current_url.lower() or
                "label" in current_url.lower() or
                "/workbench/" in current_url
            )
            if not is_annotation_page:
                self.update_status(f"💡 请先进入标注界面", "orange")
                print(f"💡 请先点击'开始标注'按钮进入标注界面，然后再使用快捷键")
            else:
                # 如果找不到按钮，尝试调试查看页面上的按钮
                self.debug_find_buttons(button_name)
                self.update_status(f"❌ 未找到{button_name}按钮", "red")
                print(f"❌ 未找到{button_name}按钮")
            return False
        except Exception as e:
            self.update_status(f"❌ {button_name}失败", "red")
            print(f"❌ 点击{button_name}按钮时出错: {e}")
            return False
    
    def debug_find_buttons(self, button_name):
        """调试方法：查找页面上的按钮元素并保存完整页面源码"""
        try:
            # 强制刷新页面状态以获取最新URL
            try:
                # 获取所有窗口句柄，确保使用最新的窗口
                all_windows = self.driver.window_handles
                current_window = self.driver.current_window_handle
                
                # 如果有多个窗口，切换到最后一个（通常是最新的）
                if len(all_windows) > 1:
                    self.driver.switch_to.window(all_windows[-1])
                    print(f"🔄 切换到最新窗口: {all_windows[-1]}")
                else:
                    self.driver.switch_to.window(current_window)
                
                # 执行JavaScript来强制刷新页面状态
                self.driver.execute_script("return document.readyState")
                actual_url = self.driver.execute_script("return window.location.href")
                time.sleep(1.0)  # 增加等待时间确保状态完全同步
                
                print(f"🔄 JavaScript获取的URL: {actual_url}")
            except Exception as e:
                print(f"⚠️  页面状态同步失败: {e}")
                
            # 获取当前页面信息
            current_url = self.driver.current_url
            page_title = self.driver.title
            
            # 通过JavaScript再次验证URL
            try:
                js_url = self.driver.execute_script("return window.location.href")
                if js_url != current_url:
                    print(f"⚠️  WebDriver URL与JavaScript URL不一致:")
                    print(f"    WebDriver URL: {current_url}")
                    print(f"    JavaScript URL: {js_url}")
                    current_url = js_url  # 使用JavaScript获取的URL
            except:
                pass
            print(f"\n🔍 实时页面检查:")
            print(f"🔍 当前页面URL: {current_url}")
            print(f"🔍 页面标题: {page_title}")
            
            # 检查页面是否已经变化到标注界面
            if "pack_key" in current_url:
                print(f"✅ 检测到已进入标注界面！")
            else:
                print(f"⚠️  仍在任务详情页面，需要点击'开始标注'按钮")
                print(f"💡 请在浏览器中手动点击页面上的'开始标注'按钮，然后再按左方向键测试跳过功能")
            
            # 获取完整页面源码并保存到本地
            try:
                page_source = self.driver.page_source
                print(f"\n🔍 开始分析页面源码...")
                
                # 保存完整页面源码到本地文件
                import os
                from datetime import datetime
                
                # 创建保存目录
                save_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', 'data')
                os.makedirs(save_dir, exist_ok=True)
                
                # 生成文件名（包含时间戳）
                timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                filename = f"page_source_{timestamp}.html"
                filepath = os.path.join(save_dir, filename)
                
                # 保存页面源码
                with open(filepath, 'w', encoding='utf-8') as f:
                    f.write(f"<!-- 页面信息 -->\n")
                    f.write(f"<!-- URL: {current_url} -->\n")
                    f.write(f"<!-- 标题: {page_title} -->\n")
                    f.write(f"<!-- 保存时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')} -->\n")
                    f.write(f"<!-- 查找按钮: {button_name} -->\n")
                    f.write("\n")
                    f.write(page_source)
                
                print(f"✅ 页面源码已保存到: {filepath}")
                print(f"📄 文件大小: {len(page_source)} 字符")
                
                # 查找footer区域
                footer_start = page_source.lower().find('<footer')
                if footer_start != -1:
                    footer_end = page_source.find('</footer>', footer_start) + 9
                    if footer_end > footer_start:
                        footer_html = page_source[footer_start:footer_end]
                        print(f"\n🔍 Footer区域HTML:")
                        print("=" * 50)
                        print(footer_html)
                        print("=" * 50)
                    else:
                        print(f"\n🔍 找到footer开始但未找到结束标签")
                else:
                    print(f"\n🔍 页面中未找到footer标签")
                    
                # 查找包含跳过的HTML片段
                if "跳过" in page_source:
                    print(f"\n🔍 页面源码中包含'跳过'文本")
                    skip_index = page_source.find("跳过")
                    start = max(0, skip_index - 300)
                    end = min(len(page_source), skip_index + 300)
                    snippet = page_source[start:end]
                    print(f"\n跳过按钮相关HTML片段:")
                    print("-" * 50)
                    print(snippet)
                    print("-" * 50)
                else:
                    print(f"\n🔍 页面源码中未找到'跳过'文本")
                    
            except Exception as e:
                print(f"🔍 页面源码分析出错: {e}")
            
            # 查找所有按钮
            all_buttons = self.driver.find_elements(By.TAG_NAME, "button")
            print(f"\n🔍 页面上共找到 {len(all_buttons)} 个按钮:")
            
            for i, btn in enumerate(all_buttons[:15]):  # 显示前15个
                try:
                    btn_class = btn.get_attribute("class") or "无class"
                    btn_text = btn.text or "无文本"
                    btn_id = btn.get_attribute("id") or "无id"
                    print(f"  按钮{i+1}: class='{btn_class}', text='{btn_text}', id='{btn_id}'")
                except:
                    print(f"  按钮{i+1}: 无法获取信息")
            
            # 特别查找包含'跳过'文本的元素
            if button_name == "跳过":
                skip_elements = self.driver.find_elements(By.XPATH, "//*[contains(text(),'跳过')]")
                print(f"\n🔍 包含'跳过'文本的元素共 {len(skip_elements)} 个:")
                for i, elem in enumerate(skip_elements):
                    try:
                        tag_name = elem.tag_name
                        elem_class = elem.get_attribute("class") or "无class"
                        elem_text = elem.text or "无文本"
                        print(f"  元素{i+1}: <{tag_name}> class='{elem_class}', text='{elem_text}'")
                    except:
                        print(f"  元素{i+1}: 无法获取信息")
                
        except Exception as e:
            print(f"🔍 调试查找按钮时出错: {e}")
    
    def on_key_press(self, event):
        """键盘按键事件处理"""
        if not self.running:
            return
        
        # 修改后的按键映射（左右互换，上下互换）
        key_actions = {
            'left': ('select', '选中'),
            'right': ('skip', '跳过'),
            'up': ('upload', '上传'),
            'down': ('extract', '提取'),
            'space': ('submit', '提交')
        }
        
        if event.name in key_actions:
            action_key, action_name = key_actions[event.name]
            
            # 所有按键都需要连续点击两次确认
            current_time = time.time()
            last_time = self.last_key_time.get(event.name, 0)
            
            if current_time - last_time <= self.double_click_interval:
                # 连续点击两次，执行操作
                print(f"\n🎯 检测到连续点击: {event.name} -> 执行{action_name}操作")
                self.update_status(f"🎯 执行{action_name}...", "blue")
                xpath = self.button_xpaths[action_key]
                threading.Thread(target=self.click_button_by_xpath, args=(xpath, action_name), daemon=True).start()
                # 重置时间，避免三次点击
                self.last_key_time[event.name] = 0
            else:
                # 第一次点击，记录时间
                print(f"\n🎯 检测到{action_name}按键，请在1秒内再次按下确认")
                self.update_status(f"🎯 {action_name}待确认...", "orange")
                self.last_key_time[event.name] = current_time
    
    def manual_action(self, action_type, action_name):
        """手动执行操作（通过GUI按钮）"""
        xpath = self.button_xpaths[action_type]
        print(f"\n🎯 手动执行{action_name}操作")
        self.update_status(f"🎯 执行{action_name}...", "blue")
        
        # 在新线程中执行点击操作
        threading.Thread(target=self.click_button_by_xpath, args=(xpath, action_name), daemon=True).start()
    
    def start_keyboard_listener(self):
        """启动键盘监听"""
        self.running = True
        
        if KEYBOARD_AVAILABLE:
            # 注册按键事件
            keyboard.on_press(self.on_key_press)
            
            print("\n🎯 浮动控制面板已启动")
            print("快捷键说明:")
            print("  ← 左键: 选中（需连续点击两次）")
            print("  → 右键: 跳过（需连续点击两次）")
            print("  ↑ 上键: 上传（需连续点击两次）")
            print("  ↓ 下键: 提取（需连续点击两次）")
            print("  空格键: 提交（需连续点击两次）")
            print("\n⚠️  请确保浏览器窗口处于活动状态以接收按键事件")
            print("💡 所有按键都需要在1秒内连续点击两次才会执行，避免误触")
        else:
            print("\n🎯 浮动控制面板已启动（GUI按钮模式）")
            print("⚠️  keyboard库不可用，请使用面板上的按钮进行操作")
    
    def start_listening(self):
        """开始监听"""
        self.running = True
        self.update_status("🟢 监听中...", "green")
        self.start_button.config(state='disabled')
        self.stop_button.config(state='normal')
        print("🟢 开始键盘监听")
    
    def stop_listening(self):
        """停止监听"""
        self.running = False
        self.update_status("🔴 已停止", "red")
        self.start_button.config(state='normal')
        self.stop_button.config(state='disabled')
        print("🔴 停止键盘监听")
    
    def close_panel(self):
        """关闭面板"""
        self.running = False
        keyboard.unhook_all()  # 移除所有键盘钩子
        if self.root:
            self.root.destroy()
        print("\n👋 浮动控制面板已关闭")
    
    def run(self):
        """运行面板"""
        if self.root:
            self.root.mainloop()

def create_floating_panel(driver):
    """创建并运行浮动控制面板"""
    try:
        panel = FloatingControlPanel(driver)
        panel.run()
    except KeyboardInterrupt:
        print("\n用户中断，关闭面板")
    except Exception as e:
        print(f"\n❌ 面板运行出错: {e}")

if __name__ == "__main__":
    print("⚠️  此脚本需要与现有的浏览器驱动配合使用")
    print("请在task_search.py中调用create_floating_panel(driver)函数")