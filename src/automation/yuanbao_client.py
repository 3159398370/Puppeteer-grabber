#!/usr/bin/env python3.8
# -*- coding: utf-8 -*-
"""
腾讯元宝自动化客户端
用于自动上传图片和文字描述到腾讯元宝平台
支持双浏览器同时操作
"""

import os
import time
import json
import base64
from typing import Dict, Any, Optional, Tuple
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.service import Service
from selenium.common.exceptions import TimeoutException, NoSuchElementException
from PIL import Image
from datetime import datetime
import logging

class YuanBaoClient:
    """腾讯元宝自动化客户端"""
    
    def __init__(self, headless=False):
        """
        初始化腾讯元宝客户端
        
        Args:
            headless: 是否使用无头模式
        """
        self.headless = headless
        self.driver = None
        self.wait = None
        self.logger = self._setup_logging()
        self.yuanbao_url = "https://yuanbao.tencent.com/chat"
        
        # 元宝页面元素选择器
        self.selectors = {
            'chat_input': "//textarea[@placeholder='请输入您的问题']",
            'upload_button': "//button[contains(@class, 'upload-btn') or @title='上传文件']",
            'file_input': "//input[@type='file']",
            'send_button': "//button[contains(@class, 'send-btn') or contains(text(), '发送')]",
            'response_area': "//div[contains(@class, 'message-content')]",
            'image_preview': "//div[contains(@class, 'image-preview')]",
            'loading_indicator': "//div[contains(@class, 'loading')]",
            'generated_image': "//img[contains(@class, 'generated-image') or contains(@src, 'data:image')]",
            'download_button': "//button[contains(@class, 'download') or contains(text(), '下载')]",
            'save_button': "//button[contains(@class, 'save') or contains(text(), '保存')]"
        }
        
    def _setup_logging(self):
        """设置日志"""
        logging.basicConfig(
            level=logging.INFO,
            format='%(asctime)s - %(levelname)s - %(message)s',
            handlers=[
                logging.FileHandler('yuanbao_automation.log', encoding='utf-8'),
                logging.StreamHandler()
            ]
        )
        return logging.getLogger(__name__)
        
    def setup_driver(self):
        """初始化Chrome浏览器驱动"""
        try:
            options = webdriver.ChromeOptions()
            if self.headless:
                options.add_argument('--headless')
            options.add_argument('--no-sandbox')
            options.add_argument('--disable-dev-shm-usage')
            options.add_argument('--disable-blink-features=AutomationControlled')
            options.add_experimental_option("excludeSwitches", ["enable-automation"])
            options.add_experimental_option('useAutomationExtension', False)
            
            # 使用固定的用户数据目录以保持登录状态
            script_dir = os.path.dirname(os.path.abspath(__file__))
            project_root = os.path.dirname(os.path.dirname(script_dir))
            user_data_dir = os.path.join(project_root, 'chrome_user_data_yuanbao')
            
            # 确保用户数据目录存在
            os.makedirs(user_data_dir, exist_ok=True)
            
            options.add_argument(f'--user-data-dir={user_data_dir}')
            options.add_argument('--profile-directory=Default')
            
            # 使用本地chromedriver.exe
            chromedriver_path = os.path.join(project_root, 'chromedriver.exe')
            service = Service(chromedriver_path)
            
            self.driver = webdriver.Chrome(service=service, options=options)
            self.driver.execute_script("Object.defineProperty(navigator, 'webdriver', {get: () => undefined})")
            
            self.wait = WebDriverWait(self.driver, 10)
            self.logger.info(f"腾讯元宝浏览器驱动初始化成功，用户数据目录: {user_data_dir}")
            self.logger.info("💡 此配置将保持腾讯元宝登录状态，避免重复登录")
            
            return True
            
        except Exception as e:
            self.logger.error(f"浏览器驱动初始化失败: {e}")
            return False
    
    def navigate_to_yuanbao(self):
        """导航到腾讯元宝页面"""
        try:
            self.logger.info(f"导航到腾讯元宝: {self.yuanbao_url}")
            self.driver.get(self.yuanbao_url)
            time.sleep(3)  # 等待页面加载
            
            # 检查是否需要登录
            current_url = self.driver.current_url
            if "login" in current_url or "auth" in current_url:
                self.logger.warning("需要登录腾讯元宝，请手动完成登录")
                input("请在浏览器中完成登录，然后按回车继续...")
            
            return True
            
        except Exception as e:
            self.logger.error(f"导航到腾讯元宝失败: {e}")
            return False
    
    def upload_image(self, image_path: str) -> bool:
        """上传图片到腾讯元宝
        
        Args:
            image_path: 图片文件路径
            
        Returns:
            bool: 上传是否成功
        """
        try:
            if not os.path.exists(image_path):
                self.logger.error(f"图片文件不存在: {image_path}")
                return False
            
            self.logger.info(f"开始上传图片: {image_path}")
            
            # 查找文件上传按钮
            upload_btn = self.wait.until(
                EC.element_to_be_clickable((By.XPATH, self.selectors['upload_button']))
            )
            upload_btn.click()
            
            # 查找文件输入框
            file_input = self.wait.until(
                EC.presence_of_element_located((By.XPATH, self.selectors['file_input']))
            )
            file_input.send_keys(os.path.abspath(image_path))
            
            # 等待图片预览出现
            self.wait.until(
                EC.presence_of_element_located((By.XPATH, self.selectors['image_preview']))
            )
            
            self.logger.info("图片上传成功")
            return True
            
        except TimeoutException:
            self.logger.error("上传图片超时")
            return False
        except Exception as e:
            self.logger.error(f"上传图片失败: {e}")
            return False
    
    def send_message(self, message: str) -> bool:
        """发送文字消息
        
        Args:
            message: 要发送的消息内容
            
        Returns:
            bool: 发送是否成功
        """
        try:
            self.logger.info(f"发送消息: {message[:50]}...")
            
            # 查找输入框
            chat_input = self.wait.until(
                EC.element_to_be_clickable((By.XPATH, self.selectors['chat_input']))
            )
            
            # 清空输入框并输入消息
            chat_input.clear()
            chat_input.send_keys(message)
            
            # 点击发送按钮
            send_btn = self.wait.until(
                EC.element_to_be_clickable((By.XPATH, self.selectors['send_button']))
            )
            send_btn.click()
            
            self.logger.info("消息发送成功")
            return True
            
        except TimeoutException:
            self.logger.error("发送消息超时")
            return False
        except Exception as e:
            self.logger.error(f"发送消息失败: {e}")
            return False
    
    def upload_image_with_description(self, image_path: str, description: str) -> bool:
        """上传图片并发送描述
        
        Args:
            image_path: 图片文件路径
            description: 图片描述文字
            
        Returns:
            bool: 操作是否成功
        """
        try:
            # 先上传图片
            if not self.upload_image(image_path):
                return False
            
            time.sleep(1)  # 等待图片处理
            
            # 再发送描述
            if not self.send_message(description):
                return False
            
            # 等待响应
            self.wait_for_response()
            
            return True
            
        except Exception as e:
            self.logger.error(f"上传图片和描述失败: {e}")
            return False
    
    def wait_for_response(self, timeout: int = 30) -> Optional[str]:
        """等待腾讯元宝的响应
        
        Args:
            timeout: 超时时间（秒）
            
        Returns:
            str: 响应内容，如果超时返回None
        """
        try:
            self.logger.info("等待腾讯元宝响应...")
            
            # 等待加载指示器消失
            start_time = time.time()
            while time.time() - start_time < timeout:
                try:
                    loading = self.driver.find_element(By.XPATH, self.selectors['loading_indicator'])
                    if loading.is_displayed():
                        time.sleep(1)
                        continue
                    else:
                        break
                except NoSuchElementException:
                    break
            
            # 获取最新的响应
            response_elements = self.driver.find_elements(By.XPATH, self.selectors['response_area'])
            if response_elements:
                latest_response = response_elements[-1].text
                self.logger.info(f"收到响应: {latest_response[:100]}...")
                return latest_response
            
            return None
            
        except Exception as e:
            self.logger.error(f"等待响应失败: {e}")
            return None
    
    def get_generated_images(self) -> list:
        """获取生成的图片元素
        
        Returns:
            list: 图片元素列表
        """
        try:
            images = self.driver.find_elements(By.XPATH, self.selectors['generated_image'])
            self.logger.info(f"找到 {len(images)} 张生成的图片")
            return images
        except Exception as e:
            self.logger.error(f"获取生成图片失败: {e}")
            return []
    
    def download_image(self, image_element, save_path: str) -> bool:
        """下载图片到指定路径
        
        Args:
            image_element: 图片元素
            save_path: 保存路径
            
        Returns:
            bool: 下载是否成功
        """
        try:
            # 获取图片src
            img_src = image_element.get_attribute('src')
            
            if img_src.startswith('data:image'):
                # Base64编码的图片
                header, data = img_src.split(',', 1)
                img_data = base64.b64decode(data)
                
                with open(save_path, 'wb') as f:
                    f.write(img_data)
                
                self.logger.info(f"图片已保存到: {save_path}")
                return True
            else:
                # URL图片，需要下载
                import requests
                response = requests.get(img_src)
                if response.status_code == 200:
                    with open(save_path, 'wb') as f:
                        f.write(response.content)
                    
                    self.logger.info(f"图片已下载到: {save_path}")
                    return True
                else:
                    self.logger.error(f"下载图片失败，状态码: {response.status_code}")
                    return False
                    
        except Exception as e:
            self.logger.error(f"下载图片失败: {e}")
            return False
    
    def download_all_generated_images(self, save_dir: str) -> list:
        """下载所有生成的图片
        
        Args:
            save_dir: 保存目录
            
        Returns:
            list: 成功下载的图片路径列表
        """
        try:
            if not os.path.exists(save_dir):
                os.makedirs(save_dir)
            
            images = self.get_generated_images()
            downloaded_paths = []
            
            for i, img in enumerate(images):
                timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                filename = f"yuanbao_generated_{timestamp}_{i+1}.png"
                save_path = os.path.join(save_dir, filename)
                
                if self.download_image(img, save_path):
                    downloaded_paths.append(save_path)
            
            self.logger.info(f"成功下载 {len(downloaded_paths)} 张图片")
            return downloaded_paths
            
        except Exception as e:
            self.logger.error(f"批量下载图片失败: {e}")
            return []
    
    def close(self):
        """关闭浏览器"""
        if self.driver:
            self.driver.quit()
            self.logger.info("腾讯元宝客户端已关闭")

class DualBrowserAutomation:
    """双浏览器自动化管理器"""
    
    def __init__(self):
        self.source_driver = None  # 用于数据标注平台的浏览器
        self.yuanbao_client = None  # 用于腾讯元宝的客户端
        self.logger = self._setup_logging()
        
    def _setup_logging(self):
        """设置日志"""
        logging.basicConfig(
            level=logging.INFO,
            format='%(asctime)s - %(levelname)s - %(message)s'
        )
        return logging.getLogger(__name__)
    
    def setup_source_browser(self):
        """设置数据标注平台浏览器"""
        try:
            options = webdriver.ChromeOptions()
            options.add_argument('--no-sandbox')
            options.add_argument('--disable-dev-shm-usage')
            options.add_argument('--disable-blink-features=AutomationControlled')
            options.add_experimental_option("excludeSwitches", ["enable-automation"])
            options.add_experimental_option('useAutomationExtension', False)
            
            # 使用本地chromedriver.exe
            script_dir = os.path.dirname(os.path.abspath(__file__))
            project_root = os.path.dirname(os.path.dirname(script_dir))
            chromedriver_path = os.path.join(project_root, 'chromedriver.exe')
            service = Service(chromedriver_path)
            
            self.source_driver = webdriver.Chrome(service=service, options=options)
            self.source_driver.execute_script("Object.defineProperty(navigator, 'webdriver', {get: () => undefined})")
            
            self.logger.info("数据标注平台浏览器初始化成功")
            return True
            
        except Exception as e:
            self.logger.error(f"数据标注平台浏览器初始化失败: {e}")
            return False
    
    def setup_yuanbao_client(self):
        """设置腾讯元宝客户端"""
        try:
            self.yuanbao_client = YuanBaoClient()
            if self.yuanbao_client.setup_driver():
                return self.yuanbao_client.navigate_to_yuanbao()
            return False
            
        except Exception as e:
            self.logger.error(f"腾讯元宝客户端设置失败: {e}")
            return False
    
    def initialize(self):
        """初始化双浏览器环境"""
        self.logger.info("初始化双浏览器自动化环境...")
        
        # 设置数据标注平台浏览器
        if not self.setup_source_browser():
            return False
        
        # 设置腾讯元宝客户端
        if not self.setup_yuanbao_client():
            return False
        
        self.logger.info("双浏览器环境初始化完成")
        return True
    
    def process_task_data(self, image_path: str, description: str) -> bool:
        """处理任务数据：将图片和描述发送到腾讯元宝
        
        Args:
            image_path: 图片文件路径
            description: 图片描述
            
        Returns:
            bool: 处理是否成功
        """
        if not self.yuanbao_client:
            self.logger.error("腾讯元宝客户端未初始化")
            return False
        
        return self.yuanbao_client.upload_image_with_description(image_path, description)
    
    def process_task(self, image_path: str, description: str, download_results: bool = True) -> bool:
        """处理任务：兼容浮动控制面板的调用接口
        
        Args:
            image_path: 图片文件路径
            description: 图片描述
            download_results: 是否自动下载处理结果
            
        Returns:
            bool: 处理是否成功
        """
        try:
            # 上传图片和描述
            if not self.process_task_data(image_path, description):
                return False
            
            if download_results:
                # 等待处理完成
                time.sleep(5)
                
                # 自动下载生成的图片
                return self.download_generated_images(image_path)
            
            return True
            
        except Exception as e:
            self.logger.error(f"处理任务失败: {e}")
            return False
    
    def download_generated_images(self, original_image_path: str) -> bool:
        """下载生成的图片
        
        Args:
            original_image_path: 原始图片路径，用于确定保存目录
            
        Returns:
            bool: 下载是否成功
        """
        try:
            if not self.yuanbao_client:
                self.logger.error("腾讯元宝客户端未初始化")
                return False
            
            # 确定保存目录
            base_dir = os.path.dirname(original_image_path)
            save_dir = os.path.join(base_dir, 'yuanbao_results')
            
            # 下载所有生成的图片
            downloaded_paths = self.yuanbao_client.download_all_generated_images(save_dir)
            
            if downloaded_paths:
                self.logger.info(f"成功下载 {len(downloaded_paths)} 张处理结果图片")
                for path in downloaded_paths:
                    self.logger.info(f"已保存: {path}")
                return True
            else:
                self.logger.warning("未找到可下载的处理结果图片")
                return False
                
        except Exception as e:
            self.logger.error(f"下载生成图片失败: {e}")
            return False
    
    def close_all(self):
        """关闭所有浏览器"""
        if self.source_driver:
            self.source_driver.quit()
            self.logger.info("数据标注平台浏览器已关闭")
        
        if self.yuanbao_client:
            self.yuanbao_client.close()
        
        self.logger.info("所有浏览器已关闭")

def create_dual_browser_automation() -> Optional[DualBrowserAutomation]:
    """创建双浏览器自动化实例"""
    try:
        automation = DualBrowserAutomation()
        if automation.initialize():
            return automation
        return None
    except Exception as e:
        print(f"创建双浏览器自动化失败: {e}")
        return None

if __name__ == "__main__":
    # 测试代码
    automation = create_dual_browser_automation()
    if automation:
        print("✅ 双浏览器自动化环境创建成功")
        # 这里可以添加测试代码
        automation.close_all()
    else:
        print("❌ 双浏览器自动化环境创建失败")