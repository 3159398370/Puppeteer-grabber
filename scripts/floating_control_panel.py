#!/usr/bin/env python3.8
# -*- coding: utf-8 -*-
"""
浮动控制面板 - 用于标注页面的键盘快捷键控制
功能（已互换左右键和上下键）：
- 左方向键：调用API处理当前数据（需连续点击两次）
- 右方向键：点击跳过按钮（需连续点击两次）
- 上方向键：上传功能（需连续点击两次）
- 下方向键：提取功能（需连续点击两次）
- 空格键：提交功能（需连续点击两次）
- 自动保存页面源码到data目录用于调试分析
"""

import time
import threading
import os
import json
import requests
import sys
import pyperclip  # 用于剪贴板操作
import webbrowser  # 用于打开浏览器
import subprocess  # 用于执行系统命令
from urllib.parse import urlparse
from datetime import datetime
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException, NoSuchElementException

# 添加项目根目录到Python路径
script_dir = os.path.dirname(os.path.abspath(__file__))
project_root = os.path.dirname(script_dir)
sys.path.insert(0, project_root)

# 导入腾讯元宝自动化客户端
try:
    from src.automation.yuanbao_client import create_dual_browser_automation
    YUANBAO_AUTOMATION_AVAILABLE = True
    print("✅ 腾讯元宝自动化客户端已导入")
except ImportError as e:
    YUANBAO_AUTOMATION_AVAILABLE = False
    print(f"⚠️  腾讯元宝自动化客户端不可用: {e}")
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
        
        # 腾讯元宝自动化客户端
        self.yuanbao_automation = None
        # 延迟初始化，避免启动时立即创建浏览器实例
        # self.init_yuanbao_automation()
        
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
        
        # 图片下载XPath
        self.image_xpath = "//div[@class='safe-image image-item']//img[@class='img']"
        
        # 标注内容XPath（图片处理指令）
        self.annotation_xpath = "//div[@class='text-item']//div[@class='text-content']//div"
        # 标注内容备用XPath
        self.annotation_xpath_backup = "//div[@class='text-content']//div[contains(@style, 'font-size')]"
        
        # 原图大小描述XPath
        self.original_size_xpath = "/html/body/div[1]/div/div[1]/div[2]/div/div/div[1]/form/div[3]/div[2]/div[2]/div/div/div[2]"
        # 原图大小备用XPath
        self.original_size_xpath_backup = "//div[@class='customInput horizontalLtr disabledStyle']"
        
        # 初始化腾讯元宝自动化客户端
        self.yuanbao_automation = None
        
        # 创建浮动窗口
        self.create_floating_window()
        
        # 启动键盘监听
        self.start_keyboard_listener()
    
    def init_yuanbao_automation(self):
        """初始化腾讯元宝自动化客户端"""
        if YUANBAO_AUTOMATION_AVAILABLE:
            try:
                self.yuanbao_automation = create_dual_browser_automation()
                if self.yuanbao_automation:
                    print("✅ 腾讯元宝自动化客户端初始化成功")
                else:
                    print("❌ 腾讯元宝自动化客户端初始化失败")
            except Exception as e:
                print(f"❌ 腾讯元宝自动化客户端初始化异常: {e}")
                self.yuanbao_automation = None
        else:
            print("⚠️  腾讯元宝自动化不可用")
            self.yuanbao_automation = None
    
    def create_floating_window(self):
        """创建浮动控制面板窗口"""
        self.root = tk.Tk()
        self.root.title("标注控制面板")
        self.root.geometry("320x700")  # 增加窗口高度以容纳指令编辑区域
        self.root.attributes('-topmost', True)  # 窗口置顶
        self.root.attributes('-alpha', 0.9)  # 半透明
        
        # 设置窗口位置（右上角）
        self.root.geometry("+{}+{}".format(self.root.winfo_screenwidth() - 340, 30))
        
        # 创建滚动框架
        canvas = tk.Canvas(self.root)
        scrollbar = ttk.Scrollbar(self.root, orient="vertical", command=canvas.yview)
        scrollable_frame = ttk.Frame(canvas)
        
        scrollable_frame.bind(
            "<Configure>",
            lambda e: canvas.configure(scrollregion=canvas.bbox("all"))
        )
        
        canvas.create_window((0, 0), window=scrollable_frame, anchor="nw")
        canvas.configure(yscrollcommand=scrollbar.set)
        
        canvas.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")
        
        # 创建主框架
        main_frame = ttk.Frame(scrollable_frame, padding="10")
        main_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        # 绑定鼠标滚轮事件
        def _on_mousewheel(event):
            canvas.yview_scroll(int(-1*(event.delta/120)), "units")
        canvas.bind_all("<MouseWheel>", _on_mousewheel)
        
        # 标题
        title_label = ttk.Label(main_frame, text="🎯 标注快捷键控制", font=('Arial', 12, 'bold'))
        title_label.grid(row=0, column=0, columnspan=2, pady=(0, 10))
        
        # 快捷键说明
        shortcuts = [
            ("← 左键", "调用元宝", "left"),
            ("→ 右键", "跳过", "right"),
            ("↑ 上键", "上传", "up"),
            ("↓ 下键", "提取", "down"),
            ("空格键", "复制JSON", "space"),
            ("PgDn键", "提交", "page_down"),
            ("Ins键", "全自动处理", "insert"),
            ("Home键", "打开元宝", "home"),
            ("PgUp键", "下载结果", "page_up"),
            ("Del键", "删除任务", "delete"),
            ("End键", "刷新指令", "end")
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
        
        # 简化说明
        note_frame = ttk.LabelFrame(main_frame, text="使用说明", padding="5")
        note_frame.grid(row=len(shortcuts)+3, column=0, columnspan=2, sticky=(tk.W, tk.E), pady=(0, 10))
        
        note_label = ttk.Label(note_frame, text="💡 所有操作均通过快捷键控制\n⚠️ 快捷键需连续按两次确认", justify=tk.CENTER)
        note_label.grid(row=0, column=0, pady=5)
        
        # 腾讯元宝管理区域
        yuanbao_frame = ttk.LabelFrame(main_frame, text="腾讯元宝管理", padding="5")
        yuanbao_frame.grid(row=len(shortcuts)+4, column=0, columnspan=2, sticky=(tk.W, tk.E), pady=(10, 10))
        
        # 重启元宝按钮
        restart_btn = ttk.Button(yuanbao_frame, text="🔄 重启元宝", 
                                command=lambda: threading.Thread(target=self.restart_yuanbao_browser, daemon=True).start())
        restart_btn.grid(row=0, column=0, padx=(0, 5), pady=5, sticky=(tk.W, tk.E))
        
        # 关闭元宝按钮
        close_btn = ttk.Button(yuanbao_frame, text="🔒 关闭元宝", 
                              command=lambda: threading.Thread(target=self.close_yuanbao_browser_safely, daemon=True).start())
        close_btn.grid(row=0, column=1, padx=(5, 0), pady=5, sticky=(tk.W, tk.E))
        
        # 配置列权重使按钮平均分布
        yuanbao_frame.columnconfigure(0, weight=1)
        yuanbao_frame.columnconfigure(1, weight=1)
        
        # 创建隐藏的指令文本框（用于内部逻辑）
        self.instruction_text = tk.Text(main_frame, height=1, width=1)
        self.instruction_text.grid_remove()  # 隐藏但保留对象
        
        # 设置默认指令
        default_instruction = "移除舞台上穿黑白条纹衣服的人物"
        self.instruction_text.insert(tk.END, default_instruction)
        
        # 移除了控制按钮和退出按钮，简化界面
        
        # 绑定窗口关闭事件
        self.root.protocol("WM_DELETE_WINDOW", self.close_panel)
    
    def update_status(self, message, color="black"):
        """更新状态显示"""
        if self.status_label:
            self.status_label.config(text=message, foreground=color)
    
    def extract_filename_from_url(self, url):
        """从URL中提取原始文件名"""
        try:
            parsed_url = urlparse(url)
            filename = os.path.basename(parsed_url.path)
            return filename if filename else 'image.jpg'
        except:
            return 'image.jpg'
    
    def get_next_folder_number(self, base_dir):
        """获取下一个可用的文件夹编号"""
        if not os.path.exists(base_dir):
            return 1
        
        existing_folders = []
        for item in os.listdir(base_dir):
            item_path = os.path.join(base_dir, item)
            if os.path.isdir(item_path) and item.isdigit():
                existing_folders.append(int(item))
        
        if not existing_folders:
            return 1
        
        return max(existing_folders) + 1
    
    def get_current_folder_number(self, base_dir):
        """获取当前最新的文件夹编号"""
        if not os.path.exists(base_dir):
            return 1
        
        existing_folders = []
        for item in os.listdir(base_dir):
            item_path = os.path.join(base_dir, item)
            if os.path.isdir(item_path) and item.isdigit():
                existing_folders.append(int(item))
        
        if not existing_folders:
            return 1
        
        return max(existing_folders)
    

    
    def extract_current_data(self):
        """提取当前页面的数据（图片、标注内容、原图大小）"""
        try:
            self.update_status("🔍 提取数据中...", "blue")
            print("\n🔍 开始提取当前页面数据...")
            
            # 等待页面加载
            WebDriverWait(self.driver, 5).until(
                lambda d: d.execute_script("return document.readyState") == "complete"
            )
            
            # 查找图片元素
            img_element = WebDriverWait(self.driver, 5).until(
                EC.presence_of_element_located((By.XPATH, self.image_xpath))
            )
            
            # 获取图片URL
            img_url = img_element.get_attribute('src')
            
            if not img_url or img_url.startswith('data:'):
                self.update_status("❌ 无效图片URL", "red")
                print("❌ 无效的图片URL")
                return
            
            print(f"📷 图片URL: {img_url}")
            
            # 检查是否已经提取过相同的图片
            if self.is_image_already_extracted(img_url):
                self.update_status("⚠️ 图片已存在", "orange")
                print("⚠️ 该图片已经提取过，跳过重复提取")
                return
            
            # 创建下载目录结构
            script_dir = os.path.dirname(os.path.abspath(__file__))
            project_root = os.path.dirname(script_dir)
            
            # 获取当前日期 (月.日格式)
            now = datetime.now()
            date_folder = f"{now.month}.{now.day}"
            
            # 构建基础路径: downloads/downloaded_images/月.日/
            base_download_dir = os.path.join(project_root, 'downloads', 'downloaded_images', date_folder)
            
            # 获取当前最新的文件夹编号（用于本次下载）
            current_folder_number = self.get_current_folder_number(base_download_dir)
            
            # 当前下载目录: downloads/downloaded_images/月.日/编号/
            current_download_dir = os.path.join(base_download_dir, str(current_folder_number))
            
            # 确保当前下载目录存在
            if not os.path.exists(current_download_dir):
                os.makedirs(current_download_dir)
            
            # 提取文件名
            filename = self.extract_filename_from_url(img_url)
            filepath = os.path.join(current_download_dir, filename)
            
            self.update_status(f"⬇️ 提取图片中...", "blue")
            print(f"⬇️ 提取图片: {filename}")
            print(f"📁 保存路径: {current_download_dir}")
            
            # 下载图片
            headers = {
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
            }
            
            # 创建session并完全禁用代理
            session = requests.Session()
            session.proxies = {}
            session.trust_env = False
            
            response = session.get(img_url, headers=headers, timeout=30, proxies={})
            response.raise_for_status()
            
            # 保存图片
            with open(filepath, 'wb') as f:
                f.write(response.content)
            
            print(f"✅ 图片下载成功: {filepath}")
            
            # 提取标注内容
            annotation_text = ""
            try:
                annotation_element = self.driver.find_element(By.XPATH, self.annotation_xpath)
                annotation_text = annotation_element.text.strip()
                print(f"📝 标注内容: {annotation_text}")
            except Exception as e:
                print(f"⚠️  主XPath标注内容提取失败，尝试备用XPath: {e}")
                try:
                    annotation_element = self.driver.find_element(By.XPATH, self.annotation_xpath_backup)
                    annotation_text = annotation_element.text.strip()
                    print(f"📝 标注内容（备用XPath）: {annotation_text}")
                except Exception as e2:
                    print(f"⚠️  备用XPath标注内容提取也失败: {e2}")
            
            # 提取原图大小描述
            original_size_text = ""
            try:
                size_element = self.driver.find_element(By.XPATH, self.original_size_xpath)
                original_size_text = size_element.text.strip()
                print(f"📏 原图大小: {original_size_text}")
            except Exception as e:
                print(f"⚠️  主XPath原图大小提取失败，尝试备用XPath: {e}")
                try:
                    size_element = self.driver.find_element(By.XPATH, self.original_size_xpath_backup)
                    original_size_text = size_element.text.strip()
                    print(f"📏 原图大小（备用XPath）: {original_size_text}")
                except Exception as e2:
                    print(f"⚠️  备用XPath原图大小提取也失败: {e2}")
            
            # 保存提取的数据到文本文件
            data_filename = f"data_{current_folder_number}.txt"
            data_filepath = os.path.join(current_download_dir, data_filename)
            
            with open(data_filepath, 'w', encoding='utf-8') as f:
                f.write(f"提取时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
                f.write(f"图片文件: {filename}\n")
                f.write(f"图片URL: {img_url}\n")
                f.write(f"标注内容: {annotation_text}\n")
                f.write(f"原图大小: {original_size_text}\n")
            
            # 保存JSON格式数据（用于API集成）
            json_filename = f"task_data_{current_folder_number}.json"
            json_filepath = os.path.join(current_download_dir, json_filename)
            
            task_data = {
                "timestamp": datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
                "task_id": str(current_folder_number),
                "image": {
                    "filename": filename,
                    "url": img_url,
                    "local_path": f"downloads/downloaded_images/{date_folder}/{current_folder_number}/{filename}",
                    "original_size": original_size_text
                },
                "annotation": {
                    "instruction": annotation_text,
                    "type": "image_editing"
                },
                "status": "extracted",
                "api_ready": True
            }
            
            with open(json_filepath, 'w', encoding='utf-8') as f:
                json.dump(task_data, f, ensure_ascii=False, indent=2)
            
            # 更新全局API任务文件
            self.update_global_api_tasks(task_data)
            
            print(f"📄 数据文件已保存: {data_filename}")
            print(f"📋 JSON数据已保存: {json_filename}")
            print(f"🌐 全局API任务列表已更新")
            
            # 提取成功后，为下次提取准备新文件夹
            next_folder_number = current_folder_number + 1
            next_download_dir = os.path.join(base_download_dir, str(next_folder_number))
            if not os.path.exists(next_download_dir):
                os.makedirs(next_download_dir)
                print(f"📁 已为下次提取创建新文件夹: {next_folder_number}")
            
            self.update_status(f"✅ 数据提取完成", "green")
            print(f"✅ 图片提取成功: {filepath}")
            print(f"📁 完整路径: downloads/downloaded_images/{date_folder}/{current_folder_number}/{filename}")
            
            # 数据提取完成后，立即更新指令内容
            print("🔄 数据提取完成，正在更新指令内容...")
            self.update_instruction_from_latest_data()
            
        except TimeoutException:
            self.update_status("❌ 提取失败", "red")
            print("❌ 未找到指定的图片元素")
            print("💡 提取失败，将继续使用当前文件夹")
        except Exception as e:
            self.update_status("❌ 提取失败", "red")
            print(f"❌ 数据提取失败: {e}")
            print("💡 提取失败，将继续使用当前文件夹")
    
    def update_global_api_tasks(self, task_data):
        """更新全局API任务文件"""
        try:
            script_dir = os.path.dirname(os.path.abspath(__file__))
            project_root = os.path.dirname(script_dir)
            data_dir = os.path.join(project_root, 'data')
            
            # 确保data目录存在
            if not os.path.exists(data_dir):
                os.makedirs(data_dir)
            
            api_tasks_file = os.path.join(data_dir, 'api_tasks.json')
            
            # 读取现有任务列表
            if os.path.exists(api_tasks_file):
                with open(api_tasks_file, 'r', encoding='utf-8') as f:
                    api_tasks = json.load(f)
            else:
                api_tasks = {
                    "created_at": datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
                    "total_tasks": 0,
                    "tasks": []
                }
            
            # 添加新任务
            api_tasks["tasks"].append(task_data)
            api_tasks["total_tasks"] = len(api_tasks["tasks"])
            api_tasks["last_updated"] = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            
            # 保存更新后的任务列表
            with open(api_tasks_file, 'w', encoding='utf-8') as f:
                json.dump(api_tasks, f, ensure_ascii=False, indent=2)
            
            print(f"📊 全局API任务文件已更新，当前共有 {api_tasks['total_tasks']} 个任务")
            
        except Exception as e:
            print(f"⚠️  更新全局API任务文件失败: {e}")
    
    def call_yuanbao_automation(self):
        """调用腾讯元宝自动化处理当前提取的数据（包含复制JSON功能）"""
        # 如果还未初始化，则进行初始化
        if not self.yuanbao_automation:
            print("🔄 首次使用，正在初始化腾讯元宝自动化客户端...")
            self.init_yuanbao_automation()
            
        if not self.yuanbao_automation:
            self.update_status("❌ 元宝自动化不可用", "red")
            print("❌ 腾讯元宝自动化客户端初始化失败")
            return
        
        try:
            self.update_status("🔄 提取当前数据...", "blue")
            print("\n🔄 开始提取当前页面数据并调用元宝自动化...")
            
            # 先提取当前数据
            self.extract_current_data()
            
            # 复制JSON到剪贴板
            print("📋 复制JSON数据到剪贴板...")
            self.copy_json_to_clipboard()
            
            # 获取最新的任务数据
            latest_task = self.get_latest_task_data()
            if not latest_task:
                self.update_status("❌ 未找到任务数据", "red")
                print("❌ 未找到可处理的任务数据")
                return
            
            # 调用元宝自动化处理
            self.process_task_with_yuanbao(latest_task)
            
        except Exception as e:
            self.update_status("❌ 元宝自动化调用失败", "red")
            print(f"❌ 元宝自动化调用异常: {e}")
            
            # 确保面板保持可见和活跃
            self.ensure_panel_visible()
        
        finally:
            # 恢复面板到正常监听状态
            if self.running:
                self.update_status("🟢 监听中...", "green")
    
    def process_latest_task(self):
        """处理最新的任务数据"""
        # 如果还未初始化，则进行初始化
        if not self.yuanbao_automation:
            print("🔄 首次使用，正在初始化腾讯元宝自动化客户端...")
            self.init_yuanbao_automation()
            
        if not self.yuanbao_automation:
            self.update_status("❌ 元宝自动化不可用", "red")
            print("❌ 腾讯元宝自动化客户端初始化失败")
            return
        
        try:
            self.update_status("🔄 处理最新任务...", "blue")
            print("\n🔄 开始处理最新任务...")
            
            # 获取最新的任务数据
            latest_task = self.get_latest_task_data()
            if not latest_task:
                self.update_status("❌ 未找到任务数据", "red")
                print("❌ 未找到可处理的任务数据")
                return
            
            # 调用元宝自动化处理
            self.process_task_with_yuanbao(latest_task)
            
        except Exception as e:
            self.update_status("❌ 处理失败", "red")
            print(f"❌ 处理最新任务异常: {e}")
            
            # 确保面板保持可见和活跃
            self.ensure_panel_visible()
        
        finally:
            # 恢复面板到正常监听状态
            if self.running:
                self.update_status("🟢 监听中...", "green")
    
    def get_latest_task_data(self):
        """获取最新的任务数据"""
        try:
            # 从全局API任务文件获取最新任务
            script_dir = os.path.dirname(os.path.abspath(__file__))
            project_root = os.path.dirname(script_dir)
            api_tasks_file = os.path.join(project_root, 'data', 'api_tasks.json')
            
            if os.path.exists(api_tasks_file):
                with open(api_tasks_file, 'r', encoding='utf-8') as f:
                    api_tasks = json.load(f)
                
                if api_tasks.get('tasks'):
                    latest_task = api_tasks['tasks'][-1]  # 获取最新任务
                    print(f"📋 找到最新任务: {latest_task.get('task_id', 'N/A')}")
                    return latest_task
            
            print("❌ 未找到任务数据文件或任务为空")
            return None
            
        except Exception as e:
            print(f"❌ 获取最新任务数据失败: {e}")
            return None
    
    def get_user_instruction(self):
        """获取用户在文本框中编辑的指令，优先从最新data文件读取"""
        try:
            # 首先尝试从最新的data文件读取标注内容
            latest_annotation = self.get_latest_annotation_from_data_file()
            if latest_annotation:
                # 如果找到最新标注内容，更新文本框并返回
                self.instruction_text.delete("1.0", tk.END)
                self.instruction_text.insert(tk.END, latest_annotation)
                print(f"📝 已从最新data文件更新指令: {latest_annotation}")
                return latest_annotation
            
            # 如果没有找到data文件中的内容，使用文本框中的内容
            user_instruction = self.instruction_text.get("1.0", tk.END).strip()
            if not user_instruction:
                return "移除舞台上穿黑白条纹衣服的人物"  # 默认指令
            return user_instruction
        except:
            return "移除舞台上穿黑白条纹衣服的人物"  # 默认指令
    
    def get_latest_annotation_from_data_file(self):
        """从最新的data文件中读取标注内容（优先读取JSON文件）"""
        try:
            script_dir = os.path.dirname(os.path.abspath(__file__))
            project_root = os.path.dirname(script_dir)
            
            # 获取当前日期 (月.日格式)
            now = datetime.now()
            date_folder = f"{now.month}.{now.day}"
            
            # 构建基础路径: downloads/downloaded_images/月.日/
            base_download_dir = os.path.join(project_root, 'downloads', 'downloaded_images', date_folder)
            
            print(f"🔍 查找data文件路径: {base_download_dir}")
            
            if not os.path.exists(base_download_dir):
                print(f"⚠️  日期文件夹不存在: {base_download_dir}")
                return None
            
            # 获取所有数字文件夹
            folders = []
            for item in os.listdir(base_download_dir):
                item_path = os.path.join(base_download_dir, item)
                if os.path.isdir(item_path) and item.isdigit():
                    folders.append(int(item))
            
            print(f"🔍 找到的数字文件夹: {folders}")
            
            if not folders:
                print(f"⚠️  没有找到数字文件夹")
                return None
            
            # 找到最新有内容的文件夹（优先选择有JSON或txt文件的文件夹）
            latest_folder = None
            for folder_num in sorted(folders, reverse=True):  # 从大到小检查
                folder_path = os.path.join(base_download_dir, str(folder_num))
                # 检查是否有JSON或txt文件
                json_file = os.path.join(folder_path, f"task_data_{folder_num}.json")
                txt_file = os.path.join(folder_path, f"data_{folder_num}.txt")
                if os.path.exists(json_file) or os.path.exists(txt_file):
                    latest_folder = folder_num
                    break
            
            if latest_folder is None:
                print(f"⚠️  没有找到包含数据文件的文件夹")
                return None
                
            latest_folder_path = os.path.join(base_download_dir, str(latest_folder))
            print(f"📁 选择的文件夹: {latest_folder} (包含数据文件)")
            
            # 优先查找JSON文件
            json_file = os.path.join(latest_folder_path, f"task_data_{latest_folder}.json")
            json_file = os.path.normpath(json_file)
            print(f"🔍 优先查找JSON文件: {json_file}")
            
            if os.path.exists(json_file):
                try:
                    with open(json_file, 'r', encoding='utf-8') as f:
                        task_data = json.load(f)
                        annotation = task_data.get('annotation', {}).get('instruction', '')
                        if annotation:
                            print(f"✅ 从JSON文件找到标注内容: {annotation[:30]}...")
                            return annotation
                except Exception as e:
                    print(f"⚠️  读取JSON文件失败: {e}")
            
            # 备用方案：查找txt文件
            data_file = os.path.join(latest_folder_path, f"data_{latest_folder}.txt")
            data_file = os.path.normpath(data_file)
            print(f"🔍 备用查找txt文件: {data_file}")
            
            if os.path.exists(data_file):
                with open(data_file, 'r', encoding='utf-8') as f:
                    lines = f.readlines()
                    for line in lines:
                        if line.startswith('标注内容: '):
                            annotation = line.replace('标注内容: ', '').strip()
                            if annotation:
                                print(f"✅ 从txt文件找到标注内容: {annotation[:30]}...")
                                return annotation
                print(f"⚠️  txt文件中没有找到标注内容")
            else:
                print(f"⚠️  txt文件不存在: {data_file}")
            
            return None
            
        except Exception as e:
            print(f"⚠️  读取最新data文件失败: {e}")
            return None
    
    def is_image_already_extracted(self, img_url):
        """检查图片是否已经提取过"""
        try:
            script_dir = os.path.dirname(os.path.abspath(__file__))
            project_root = os.path.dirname(script_dir)
            
            # 获取当前日期 (月.日格式)
            now = datetime.now()
            date_folder = f"{now.month}.{now.day}"
            
            # 构建基础路径: downloads/downloaded_images/月.日/
            base_download_dir = os.path.join(project_root, 'downloads', 'downloaded_images', date_folder)
            
            if not os.path.exists(base_download_dir):
                return False
            
            # 遍历所有数字文件夹
            for item in os.listdir(base_download_dir):
                item_path = os.path.join(base_download_dir, item)
                if os.path.isdir(item_path) and item.isdigit():
                    # 检查该文件夹中的data文件
                    data_file = os.path.join(item_path, f"data_{item}.txt")
                    if os.path.exists(data_file):
                        with open(data_file, 'r', encoding='utf-8') as f:
                            content = f.read()
                            if f"图片URL: {img_url}" in content:
                                print(f"🔍 发现重复图片，已存在于文件夹: {item}")
                                return True
            
            return False
            
        except Exception as e:
            print(f"⚠️  检查重复图片时出错: {e}")
            return False
    
    def format_instruction_with_constraints(self, user_instruction, original_size):
        """格式化指令，添加保持原有尺寸和其他元素不变的约束"""
        formatted_instruction = f"{user_instruction}，请保持图片的原有尺寸{original_size}，保持其他元素不变，确保编辑后的图片与原图在构图和风格上保持一致。"
        return formatted_instruction
    
    def process_task_with_api(self, task_data):
        """使用API处理任务数据"""
        try:
            # 提取任务信息
            image_info = task_data.get('image', {})
            annotation_info = task_data.get('annotation', {})
            
            image_path = image_info.get('local_path', '')
            original_size = image_info.get('original_size', '1920X1080')
            
            # 获取用户编辑的指令
            user_instruction = self.get_user_instruction()
            
            # 格式化指令，添加约束条件
            formatted_instruction = self.format_instruction_with_constraints(user_instruction, original_size)
            
            if not image_path:
                self.update_status("❌ 任务数据不完整", "red")
                print("❌ 任务数据不完整，缺少图片路径")
                return
            
            # 检查图片文件是否存在
            script_dir = os.path.dirname(os.path.abspath(__file__))
            project_root = os.path.dirname(script_dir)
            full_image_path = os.path.join(project_root, image_path)
            
            if not os.path.exists(full_image_path):
                self.update_status("❌ 图片文件不存在", "red")
                print(f"❌ 图片文件不存在: {full_image_path}")
                return
            
            self.update_status("🚀 调用腾讯元器API...", "blue")
            print(f"\n🚀 开始调用腾讯元器API...")
            print(f"📷 图片路径: {full_image_path}")
            print(f"📝 用户指令: {user_instruction}")
            print(f"📝 完整指令: {formatted_instruction}")
            print(f"📐 原图尺寸: {original_size}")
            
            # 调用API处理图片
            # 注意：这是旧的API处理方法，现在应该使用process_task_with_yuanbao
            # 这里保留是为了兼容性，但建议使用新的元宝自动化方法
            result = None
            print("⚠️  此方法已弃用，请使用process_task_with_yuanbao方法")
            
            if result:
                self.update_status("✅ API调用成功", "green")
                print("\n✅ 腾讯元器API调用成功！")
                
                # 保存API调用结果
                self.save_api_result(task_data, result)
                
                # 确保面板保持可见和活跃
                self.ensure_panel_visible()
            else:
                self.update_status("❌ API调用失败", "red")
                print("❌ 腾讯元器API调用失败")
                
                # 确保面板保持可见和活跃
                self.ensure_panel_visible()
                
        except Exception as e:
            self.update_status("❌ API处理异常", "red")
            print(f"❌ API处理异常: {e}")
            
            # 确保面板保持可见和活跃
            self.ensure_panel_visible()
        
        finally:
            # 恢复面板到正常监听状态
            if self.running:
                self.update_status("🟢 监听中...", "green")
                print("🔄 面板已恢复到监听状态")
    
    def process_task_with_yuanbao(self, task_data):
        """使用腾讯元宝自动化处理任务数据"""
        try:
            # 提取任务信息
            image_info = task_data.get('image', {})
            annotation_info = task_data.get('annotation', {})
            
            image_path = image_info.get('local_path', '')
            original_size = image_info.get('original_size', '1920X1080')
            
            # 获取用户编辑的指令
            user_instruction = self.get_user_instruction()
            
            if not image_path:
                self.update_status("❌ 任务数据不完整", "red")
                print("❌ 任务数据不完整，缺少图片路径")
                return
            
            # 检查图片文件是否存在
            script_dir = os.path.dirname(os.path.abspath(__file__))
            project_root = os.path.dirname(script_dir)
            full_image_path = os.path.join(project_root, image_path)
            
            if not os.path.exists(full_image_path):
                self.update_status("❌ 图片文件不存在", "red")
                print(f"❌ 图片文件不存在: {full_image_path}")
                return
            
            self.update_status("🚀 调用腾讯元宝自动化...", "blue")
            print(f"\n🚀 开始调用腾讯元宝自动化...")
            print(f"📷 图片路径: {full_image_path}")
            print(f"📝 用户指令: {user_instruction}")
            print(f"📐 原图尺寸: {original_size}")
            
            # 调用元宝自动化处理
            result = self.yuanbao_automation.process_task(
                image_path=full_image_path,
                description=user_instruction
            )
            
            if result:
                self.update_status("✅ 元宝自动化成功", "green")
                print("\n✅ 腾讯元宝自动化处理成功！")
                
                # 确保面板保持可见和活跃
                self.ensure_panel_visible()
            else:
                self.update_status("❌ 元宝自动化失败", "red")
                print("❌ 腾讯元宝自动化处理失败")
                
                # 确保面板保持可见和活跃
                self.ensure_panel_visible()
                
        except Exception as e:
            self.update_status("❌ 元宝自动化异常", "red")
            print(f"❌ 元宝自动化处理异常: {e}")
            
            # 确保面板保持可见和活跃
            self.ensure_panel_visible()
        
        finally:
            # 恢复面板到正常监听状态
            if self.running:
                self.update_status("🟢 监听中...", "green")
                print("🔄 面板已恢复到监听状态")
    
    def copy_json_to_clipboard(self):
        """将最新任务的JSON数据复制到剪贴板"""
        try:
            self.update_status("📋 复制JSON中...", "blue")
            print("\n📋 开始复制JSON数据到剪贴板...")
            
            # 先提取当前数据（如果页面有新数据）
            self.extract_current_data()
            
            # 获取最新的任务数据
            latest_task = self.get_latest_task_data()
            if not latest_task:
                self.update_status("❌ 未找到任务数据", "red")
                print("❌ 未找到可复制的任务数据")
                return
            
            # 获取用户编辑的指令
            user_instruction = self.get_user_instruction()
            
            # 构建用于腾讯元宝的JSON数据
            yuanbao_data = {
                "task_id": latest_task.get('task_id', ''),
                "instruction": user_instruction,
                "image_info": {
                    "filename": latest_task.get('image', {}).get('filename', ''),
                    "local_path": latest_task.get('image', {}).get('local_path', ''),
                    "original_size": latest_task.get('image', {}).get('original_size', ''),
                    "url": latest_task.get('image', {}).get('url', '')
                },
                "timestamp": datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
                "ready_for_processing": True
            }
            
            # 转换为格式化的JSON字符串
            json_string = json.dumps(yuanbao_data, ensure_ascii=False, indent=2)
            
            # 复制到剪贴板
            pyperclip.copy(json_string)
            
            self.update_status("✅ JSON已复制", "green")
            print("✅ JSON数据已成功复制到剪贴板")
            print(f"📋 复制的数据: {json_string[:100]}...")
            
        except Exception as e:
            self.update_status("❌ 复制失败", "red")
            print(f"❌ 复制JSON到剪贴板失败: {e}")
    
    def open_yuanbao_browser(self):
        """打开腾讯元宝浏览器页面"""
        try:
            self.update_status("🌐 打开元宝中...", "blue")
            print("\n🌐 正在打开腾讯元宝浏览器...")
            
            yuanbao_url = "https://yuanbao.tencent.com/chat"
            webbrowser.open(yuanbao_url)
            
            self.update_status("✅ 元宝已打开", "green")
            print(f"✅ 腾讯元宝已在浏览器中打开: {yuanbao_url}")
            print("💡 提示: 您现在可以在腾讯元宝中粘贴JSON数据并上传对应的图片")
            
        except Exception as e:
            self.update_status("❌ 打开失败", "red")
            print(f"❌ 打开腾讯元宝失败: {e}")
    
    def one_click_process(self):
        """一键处理：提取数据 -> 复制JSON -> 打开元宝"""
        try:
            self.update_status("🚀 一键处理中...", "blue")
            print("\n🚀 开始一键处理流程...")
            
            # 步骤1: 提取当前数据
            print("📋 步骤1: 提取当前页面数据...")
            self.extract_current_data()
            
            # 步骤2: 复制JSON到剪贴板
            print("📋 步骤2: 复制JSON数据到剪贴板...")
            self.copy_json_to_clipboard()
            
            # 步骤3: 打开腾讯元宝
            print("🌐 步骤3: 打开腾讯元宝浏览器...")
            self.open_yuanbao_browser()
            
            # 步骤4: 显示操作指引
            print("\n✅ 一键处理完成！请按以下步骤操作:")
            print("1. 在腾讯元宝页面中粘贴JSON数据 (Ctrl+V)")
            print("2. 上传对应的图片文件")
            print("3. 等待处理完成后，点击'📥 下载结果'按钮")
            
            self.update_status("✅ 一键处理完成", "green")
            
        except Exception as e:
            self.update_status("❌ 一键处理失败", "red")
            print(f"❌ 一键处理失败: {e}")
    
    def download_processed_image(self):
        """下载腾讯元宝处理后的图片"""
        try:
            self.update_status("📥 准备下载...", "blue")
            print("\n📥 开始下载处理后的图片...")
            
            # 获取最新任务数据
            latest_task = self.get_latest_task_data()
            if not latest_task:
                self.update_status("❌ 未找到任务数据", "red")
                print("❌ 未找到任务数据")
                return
            
            # 创建处理结果目录
            script_dir = os.path.dirname(os.path.abspath(__file__))
            project_root = os.path.dirname(script_dir)
            
            # 获取当前日期 (月.日格式)
            now = datetime.now()
            date_folder = f"{now.month}.{now.day}"
            
            # 构建处理结果保存路径
            processed_dir = os.path.join(project_root, 'downloads', 'processed_images', date_folder)
            task_id = latest_task.get('task_id', 'unknown')
            task_processed_dir = os.path.join(processed_dir, str(task_id))
            
            if not os.path.exists(task_processed_dir):
                os.makedirs(task_processed_dir)
            
            print(f"📁 处理结果将保存到: {task_processed_dir}")
            print("💡 提示: 请手动从腾讯元宝下载处理后的图片到上述目录")
            
            self.update_status("✅ 目录已准备", "green")
            
        except Exception as e:
            self.update_status("❌ 下载失败", "red")
            print(f"❌ 下载处理失败: {e}")
    
    def refresh_instruction(self):
        """手动刷新指令内容"""
        try:
            self.update_status("🔄 刷新指令...", "blue")
            print("\n🔄 手动刷新指令内容...")
            
            # 强制更新指令
            self.update_instruction_from_latest_data()
            
            self.update_status("✅ 指令已刷新", "green")
            print("✅ 指令刷新完成")
            
        except Exception as e:
            self.update_status("❌ 刷新失败", "red")
            print(f"❌ 刷新指令失败: {e}")
    
    def delete_current_task(self):
        """删除当前任务文件夹（用于清理不满意的AI生成结果）"""
        try:
            self.update_status("🗑️ 准备删除...", "blue")
            print("\n🗑️ 准备删除当前任务文件夹...")
            
            script_dir = os.path.dirname(os.path.abspath(__file__))
            project_root = os.path.dirname(script_dir)
            
            # 获取当前日期 (月.日格式)
            now = datetime.now()
            date_folder = f"{now.month}.{now.day}"
            
            # 构建基础路径
            base_download_dir = os.path.join(project_root, 'downloads', 'downloaded_images', date_folder)
            
            if not os.path.exists(base_download_dir):
                self.update_status("❌ 文件夹不存在", "red")
                print(f"❌ 日期文件夹不存在: {base_download_dir}")
                return
            
            # 获取最新的任务文件夹
            folders = []
            for item in os.listdir(base_download_dir):
                item_path = os.path.join(base_download_dir, item)
                if os.path.isdir(item_path) and item.isdigit():
                    folders.append(int(item))
            
            if not folders:
                self.update_status("❌ 无任务文件夹", "red")
                print("❌ 没有找到任务文件夹")
                return
            
            # 找到最新有内容的文件夹（优先选择有JSON或txt文件的文件夹）
            latest_folder = None
            for folder_num in sorted(folders, reverse=True):  # 从大到小检查
                folder_path = os.path.join(base_download_dir, str(folder_num))
                # 检查是否有JSON或txt文件
                json_file = os.path.join(folder_path, f"task_data_{folder_num}.json")
                txt_file = os.path.join(folder_path, f"data_{folder_num}.txt")
                if os.path.exists(json_file) or os.path.exists(txt_file):
                    latest_folder = folder_num
                    break
            
            if latest_folder is None:
                self.update_status("❌ 无有效任务", "red")
                print("❌ 没有找到包含数据文件的任务文件夹")
                return
                
            latest_folder_path = os.path.join(base_download_dir, str(latest_folder))
            print(f"📁 准备删除文件夹: {latest_folder} (包含数据文件)")
            
            # 确认删除
            import tkinter.messagebox as msgbox
            result = msgbox.askyesno(
                "确认删除", 
                f"确定要删除任务文件夹 {latest_folder} 吗？\n\n这将删除该任务的所有文件，包括：\n- 图片文件\n- JSON数据文件\n- txt数据文件\n\n此操作不可撤销！"
            )
            
            if result:
                import shutil
                shutil.rmtree(latest_folder_path)
                self.update_status("✅ 删除成功", "green")
                print(f"✅ 已删除任务文件夹: {latest_folder_path}")
                print("💡 提示: 可以重新提取当前页面的数据")
            else:
                self.update_status("❌ 取消删除", "orange")
                print("❌ 用户取消删除操作")
                
        except Exception as e:
            self.update_status("❌ 删除失败", "red")
            print(f"❌ 删除任务文件夹失败: {e}")
            print("💡 或者提供处理后图片的URL以便自动下载")
            
            # 询问用户是否有处理后的图片URL
            print("\n如果您有处理后图片的URL，请在控制台输入:")
            
            self.update_status("✅ 下载目录已准备", "green")
            
            # 保存下载信息到任务数据
            download_info = {
                "task_id": task_id,
                "processed_dir": task_processed_dir,
                "download_time": datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
                "status": "ready_for_download"
            }
            
            # 更新任务状态
            self.update_task_status(task_id, "processing_completed", download_info)
            
        except Exception as e:
            self.update_status("❌ 下载准备失败", "red")
            print(f"❌ 下载准备失败: {e}")
    
    def update_task_status(self, task_id, status, additional_info=None):
        """更新任务状态"""
        try:
            script_dir = os.path.dirname(os.path.abspath(__file__))
            project_root = os.path.dirname(script_dir)
            api_tasks_file = os.path.join(project_root, 'data', 'api_tasks.json')
            
            if os.path.exists(api_tasks_file):
                with open(api_tasks_file, 'r', encoding='utf-8') as f:
                    api_tasks = json.load(f)
                
                # 查找并更新对应的任务
                for task in api_tasks.get('tasks', []):
                    if task.get('task_id') == str(task_id):
                        task['status'] = status
                        task['last_updated'] = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
                        if additional_info:
                            task.update(additional_info)
                        break
                
                # 保存更新后的数据
                with open(api_tasks_file, 'w', encoding='utf-8') as f:
                    json.dump(api_tasks, f, ensure_ascii=False, indent=2)
                
                print(f"✅ 任务 {task_id} 状态已更新为: {status}")
                
        except Exception as e:
            print(f"❌ 更新任务状态失败: {e}")
    
    def save_api_result(self, task_data, api_result):
        """保存API调用结果"""
        try:
            # 创建API结果保存目录
            script_dir = os.path.dirname(os.path.abspath(__file__))
            project_root = os.path.dirname(script_dir)
            results_dir = os.path.join(project_root, 'data', 'api_results')
            
            if not os.path.exists(results_dir):
                os.makedirs(results_dir)
            
            # 生成结果文件名
            task_id = task_data.get('task_id', 'unknown')
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            result_filename = f"api_result_{task_id}_{timestamp}.json"
            result_filepath = os.path.join(results_dir, result_filename)
            
            # 组合完整结果数据
            complete_result = {
                'task_data': task_data,
                'api_result': api_result,
                'processed_at': datetime.now().isoformat(),
                'status': 'completed'
            }
            
            # 如果有处理后的图片路径，添加到结果中
            if 'processed_image_path' in api_result:
                complete_result['processed_image_path'] = api_result['processed_image_path']
                print(f"📷 处理后的图片: {api_result['processed_image_path']}")
            
            # 保存结果
            with open(result_filepath, 'w', encoding='utf-8') as f:
                json.dump(complete_result, f, ensure_ascii=False, indent=2)
            
            print(f"💾 API调用结果已保存: {result_filename}")
            
        except Exception as e:
            print(f"⚠️  保存API结果失败: {e}")
    
    def ensure_panel_visible(self):
        """确保面板保持可见和活跃状态"""
        try:
            if self.root and self.root.winfo_exists():
                # 将窗口置于最前
                self.root.lift()
                self.root.attributes('-topmost', True)
                
                # 短暂闪烁以引起注意
                original_alpha = self.root.attributes('-alpha')
                self.root.attributes('-alpha', 1.0)
                self.root.after(200, lambda: self.root.attributes('-alpha', original_alpha))
                
                print("✅ 浮动面板已确保可见")
        except Exception as e:
            print(f"⚠️  确保面板可见时出错: {e}")
    
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
        
        # 扩展的按键映射
        key_actions = {
            'left': ('yuanbao_call', '调用元宝'),
            'right': ('skip', '跳过'),
            'up': ('upload', '上传'),
            'down': ('extract', '提取'),
            'space': ('copy_json', '复制JSON'),
            'page_down': ('submit', '提交'),
            'insert': ('auto_process', '全自动处理'),
            'home': ('open_yuanbao', '打开元宝'),
            'page_up': ('download_result', '下载结果'),
            'delete': ('delete_task', '删除任务'),
            'end': ('refresh_instruction', '刷新指令')
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
                
                if action_key == 'extract':
                    # 提取操作
                    threading.Thread(target=self.extract_current_data, daemon=True).start()
                elif action_key == 'copy_json':
                    # 复制JSON到剪贴板
                    threading.Thread(target=self.copy_json_to_clipboard, daemon=True).start()
                elif action_key == 'yuanbao_call':
                    # 元宝自动化调用操作
                    threading.Thread(target=self.call_yuanbao_automation, daemon=True).start()
                elif action_key == 'auto_process':
                    # 全自动处理（与api_call相同）
                    threading.Thread(target=self.call_yuanbao_automation, daemon=True).start()
                elif action_key == 'open_yuanbao':
                    # 打开元宝浏览器
                    threading.Thread(target=self.open_yuanbao_browser, daemon=True).start()
                elif action_key == 'download_result':
                    # 下载结果
                    threading.Thread(target=self.download_processed_image, daemon=True).start()
                elif action_key == 'delete_task':
                    # 删除任务
                    threading.Thread(target=self.delete_current_task, daemon=True).start()
                elif action_key == 'refresh_instruction':
                    # 刷新指令
                    threading.Thread(target=self.refresh_instruction, daemon=True).start()
                elif action_key == 'one_click_process':
                    # 一键处理
                    threading.Thread(target=self.one_click_process, daemon=True).start()
                else:
                    # 其他按钮操作
                    xpath = self.button_xpaths[action_key]
                    threading.Thread(target=self.click_button_by_xpath, args=(xpath, action_name), daemon=True).start()
                
                # 重置时间，避免三次点击
                self.last_key_time[event.name] = 0
            else:
                # 第一次点击，记录时间
                print(f"\n🎯 检测到{action_name}按键，请在1秒内再次按下确认")
                self.update_status(f"🎯 {action_name}待确认...", "orange")
                self.last_key_time[event.name] = current_time
    

    
    def start_page_monitor(self):
        """启动页面监听线程，自动更新指令"""
        def monitor_page():
            last_url = ""
            last_image_src = ""
            while self.running:
                try:
                    current_url = self.driver.current_url
                    
                    # 检测当前页面的图片元素，用于判断是否切换到新图片
                    current_image_src = ""
                    try:
                        img_element = self.driver.find_element(By.XPATH, "//img[contains(@class, 'image-item') or contains(@src, 'http')]")
                        current_image_src = img_element.get_attribute('src') or ""
                    except:
                        pass
                    
                    # URL变化或图片变化时更新指令
                    if current_url != last_url or current_image_src != last_image_src:
                        if current_url != last_url:
                            print(f"🔄 检测到页面URL变化: {current_url}")
                        if current_image_src != last_image_src and current_image_src:
                            print(f"🔄 检测到图片变化: {current_image_src[:50]}...")
                        
                        last_url = current_url
                        last_image_src = current_image_src
                        
                        # 页面或图片发生变化，更新指令
                        self.update_instruction_from_latest_data()
                    
                    time.sleep(3)  # 每3秒检查一次变化
                except Exception as e:
                    print(f"⚠️  页面监听出错: {e}")
                    time.sleep(5)  # 出错时等待更长时间
        
        monitor_thread = threading.Thread(target=monitor_page, daemon=True)
        monitor_thread.start()
        print("🔄 页面监听线程已启动（监听URL和图片变化）")
    
    def update_instruction_from_latest_data(self):
        """从最新数据文件更新指令内容"""
        try:
            latest_annotation = self.get_latest_annotation_from_data_file()
            if latest_annotation:
                # 获取当前指令内容
                current_instruction = self.instruction_text.get(1.0, tk.END).strip()
                
                # 只有当指令内容真的不同时才更新
                if latest_annotation != current_instruction:
                    # 使用root.after确保UI更新在主线程中执行
                    def update_ui():
                        try:
                            self.instruction_text.delete(1.0, tk.END)
                            self.instruction_text.insert(1.0, latest_annotation)
                            print(f"✅ 指令已更新: {latest_annotation[:50]}...")
                        except Exception as e:
                            print(f"⚠️  UI更新失败: {e}")
                    
                    if self.root:
                        self.root.after(0, update_ui)
                    else:
                        update_ui()
                else:
                    print(f"ℹ️  指令内容无变化，跳过更新")
            else:
                print(f"⚠️  未找到最新的标注内容，保持当前指令")
        except Exception as e:
            print(f"⚠️  更新指令失败: {e}")
    
    def start_keyboard_listener(self):
        """启动键盘监听"""
        self.running = True
        
        # 启动页面监听线程，自动更新指令
        self.start_page_monitor()
        
        if KEYBOARD_AVAILABLE:
            # 注册按键事件
            keyboard.on_press(self.on_key_press)
            
            print("\n🎯 浮动控制面板已启动")
            print("快捷键说明:")
            print("  ← 左键: 调用API（需连续点击两次）")
            print("  → 右键: 跳过（需连续点击两次）")
            print("  ↑ 上键: 上传（需连续点击两次）")
            print("  ↓ 下键: 提取（需连续点击两次）")
            print("  空格键: 复制JSON（需连续点击两次）")
            print("  PgDn键: 提交（需连续点击两次）")
            print("\n⚠️  请确保浏览器窗口处于活动状态以接收按键事件")
            print("💡 所有按键都需要在1秒内连续点击两次才会执行，避免误触")
            print("🔄 面板将自动监听页面变化并更新指令")
        else:
            print("\n🎯 浮动控制面板已启动（GUI按钮模式）")
            print("⚠️  keyboard库不可用，请使用面板上的按钮进行操作")
            print("🔄 面板将自动监听页面变化并更新指令")
    
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
        
        # 安全地移除键盘钩子
        if KEYBOARD_AVAILABLE:
            try:
                keyboard.unhook_all()  # 移除所有键盘钩子
            except Exception as e:
                print(f"⚠️  移除键盘钩子时出错: {e}")
        
        # 重要：不关闭腾讯元宝浏览器，保持其运行状态
        if hasattr(self, 'yuanbao_automation') and self.yuanbao_automation:
            print("⚠️  腾讯元宝浏览器将保持开启状态，请勿手动关闭")
            print("💡 如需关闭腾讯元宝浏览器，请使用专门的关闭方法")
        
        if self.root:
            self.root.destroy()
        print("\n👋 浮动控制面板已关闭")
        print("🔄 腾讯元宝浏览器继续运行中...")
    
    def close_yuanbao_browser_safely(self):
        """安全关闭腾讯元宝浏览器"""
        try:
            if hasattr(self, 'yuanbao_automation') and self.yuanbao_automation:
                print("🔄 正在安全关闭腾讯元宝浏览器...")
                self.yuanbao_automation.close_all()
                self.yuanbao_automation = None
                print("✅ 腾讯元宝浏览器已安全关闭")
                self.update_status("腾讯元宝浏览器已关闭", "orange")
            else:
                print("ℹ️  腾讯元宝浏览器未运行")
                self.update_status("腾讯元宝浏览器未运行", "gray")
        except Exception as e:
            print(f"❌ 关闭腾讯元宝浏览器时出错: {e}")
            self.update_status("关闭腾讯元宝浏览器失败", "red")
    
    def restart_yuanbao_browser(self):
        """重启腾讯元宝浏览器"""
        try:
            print("🔄 正在重启腾讯元宝浏览器...")
            self.update_status("重启腾讯元宝浏览器中...", "blue")
            
            # 先安全关闭
            self.close_yuanbao_browser_safely()
            
            # 等待一秒
            time.sleep(1)
            
            # 重新初始化
            self.init_yuanbao_automation()
            
            if self.yuanbao_automation:
                print("✅ 腾讯元宝浏览器重启成功")
                self.update_status("腾讯元宝浏览器已重启", "green")
            else:
                print("❌ 腾讯元宝浏览器重启失败")
                self.update_status("腾讯元宝浏览器重启失败", "red")
                
        except Exception as e:
            print(f"❌ 重启腾讯元宝浏览器时出错: {e}")
            self.update_status("重启腾讯元宝浏览器失败", "red")
    
    def run(self):
        """运行面板"""
        if self.root:
            self.root.mainloop()

def create_floating_panel(driver):
    """创建并运行浮动控制面板"""
    panel = None
    try:
        panel = FloatingControlPanel(driver)
        print("✅ 浮动控制面板初始化成功")
        panel.run()
    except KeyboardInterrupt:
        print("\n用户中断，关闭面板")
        if panel:
            panel.close_panel()
    except Exception as e:
        print(f"\n❌ 面板运行出错: {e}")
        print(f"错误详情: {type(e).__name__}: {str(e)}")
        if panel:
            try:
                panel.close_panel()
            except:
                pass  # 忽略关闭时的错误

if __name__ == "__main__":
    print("⚠️  此脚本需要与现有的浏览器驱动配合使用")
    print("请在task_search.py中调用create_floating_panel(driver)函数")