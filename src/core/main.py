#!/usr/bin/env python3.8
# -*- coding: utf-8 -*-
"""
数据标注自动化工具
功能：自动化下载、上传图片，复制文字，并使用腾讯元宝API进行图片背景替换
"""

import os
import time
import requests
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.service import Service
# from webdriver_manager.chrome import ChromeDriverManager  # 不再需要，使用本地chromedriver.exe
from PIL import Image
import base64
from dotenv import load_dotenv
import json
import logging

# 加载环境变量
load_dotenv()

class AutomationTool:
    def __init__(self):
        self.driver = None
        self.wait = None
        self.setup_logging()
        self.setup_driver()
        
        # 腾讯元宝API配置
        self.api_key = os.getenv('TENCENT_API_KEY')
        self.api_secret = os.getenv('TENCENT_API_SECRET')
        self.api_endpoint = os.getenv('TENCENT_API_ENDPOINT', 'https://api.yuanbao.tencent.com')
        
        # 智能体配置
        self.agent_id = os.getenv('AGENT_ID')
        self.token = os.getenv('TOKEN')
        
    def setup_logging(self):
        """设置日志"""
        logging.basicConfig(
            level=logging.INFO,
            format='%(asctime)s - %(levelname)s - %(message)s',
            handlers=[
                logging.FileHandler('automation.log', encoding='utf-8'),
                logging.StreamHandler()
            ]
        )
        self.logger = logging.getLogger(__name__)
        
    def setup_driver(self):
        """初始化Chrome浏览器驱动"""
        try:
            options = webdriver.ChromeOptions()
            options.add_argument('--no-sandbox')
            options.add_argument('--disable-dev-shm-usage')
            options.add_argument('--disable-blink-features=AutomationControlled')
            options.add_experimental_option("excludeSwitches", ["enable-automation"])
            options.add_experimental_option('useAutomationExtension', False)
            
            # 设置下载目录
            download_dir = os.path.join(os.getcwd(), 'downloads')
            os.makedirs(download_dir, exist_ok=True)
            
            prefs = {
                "download.default_directory": download_dir,
                "download.prompt_for_download": False,
                "download.directory_upgrade": True,
                "safebrowsing.enabled": True
            }
            options.add_experimental_option("prefs", prefs)
            
            # 使用本地chromedriver.exe
            chromedriver_path = os.path.join(os.getcwd(), 'chromedriver.exe')
            service = Service(chromedriver_path)
            self.driver = webdriver.Chrome(service=service, options=options)
            self.driver.execute_script("Object.defineProperty(navigator, 'webdriver', {get: () => undefined})")
            
            self.wait = WebDriverWait(self.driver, 10)
            self.logger.info("浏览器驱动初始化成功")
            
        except Exception as e:
            self.logger.error(f"浏览器驱动初始化失败: {e}")
            raise
    
    def find_element_by_xpath(self, xpath, timeout=10):
        """通过XPath查找元素"""
        try:
            element = WebDriverWait(self.driver, timeout).until(
                EC.presence_of_element_located((By.XPATH, xpath))
            )
            return element
        except Exception as e:
            self.logger.error(f"无法找到元素 {xpath}: {e}")
            return None
    
    def click_element(self, xpath, timeout=10):
        """点击元素"""
        try:
            element = WebDriverWait(self.driver, timeout).until(
                EC.element_to_be_clickable((By.XPATH, xpath))
            )
            element.click()
            self.logger.info(f"成功点击元素: {xpath}")
            return True
        except Exception as e:
            self.logger.error(f"点击元素失败 {xpath}: {e}")
            return False
    
    def input_text(self, xpath, text, timeout=10):
        """输入文本"""
        try:
            element = self.find_element_by_xpath(xpath, timeout)
            if element:
                element.clear()
                element.send_keys(text)
                self.logger.info(f"成功输入文本到 {xpath}")
                return True
        except Exception as e:
            self.logger.error(f"输入文本失败 {xpath}: {e}")
        return False
    
    def get_text(self, xpath, timeout=10):
        """获取元素文本"""
        try:
            element = self.find_element_by_xpath(xpath, timeout)
            if element:
                text = element.text
                self.logger.info(f"成功获取文本: {text[:50]}...")
                return text
        except Exception as e:
            self.logger.error(f"获取文本失败 {xpath}: {e}")
        return None
    
    def download_image(self, image_url, filename=None):
        """下载图片"""
        try:
            if not filename:
                filename = f"image_{int(time.time())}.jpg"
            
            download_dir = os.path.join(os.getcwd(), 'downloads')
            filepath = os.path.join(download_dir, filename)
            
            response = requests.get(image_url, stream=True)
            response.raise_for_status()
            
            with open(filepath, 'wb') as f:
                for chunk in response.iter_content(chunk_size=8192):
                    f.write(chunk)
            
            self.logger.info(f"图片下载成功: {filepath}")
            return filepath
        except Exception as e:
            self.logger.error(f"图片下载失败: {e}")
            return None
    
    def upload_image(self, xpath, image_path, timeout=10):
        """上传图片"""
        try:
            element = self.find_element_by_xpath(xpath, timeout)
            if element and os.path.exists(image_path):
                element.send_keys(image_path)
                self.logger.info(f"图片上传成功: {image_path}")
                return True
        except Exception as e:
            self.logger.error(f"图片上传失败: {e}")
        return False
    
    def process_image_with_yuanbao(self, image_path, background_prompt="白色背景"):
        """使用腾讯元宝API处理图片背景"""
        try:
            if not self.api_key or not self.api_secret:
                self.logger.error("腾讯元宝API密钥未配置")
                return None
            
            # 读取图片并转换为base64
            with open(image_path, 'rb') as f:
                image_data = base64.b64encode(f.read()).decode('utf-8')
            
            # 构建API请求
            headers = {
                'Content-Type': 'application/json',
                'Authorization': f'Bearer {self.api_key}'
            }
            
            payload = {
                'model': 'yuanbao-image-edit',
                'image': image_data,
                'prompt': f"将图片背景替换为{background_prompt}",
                'response_format': 'b64_json'
            }
            
            response = requests.post(
                f"{self.api_endpoint}/v1/images/edit",
                headers=headers,
                json=payload,
                timeout=30
            )
            
            if response.status_code == 200:
                result = response.json()
                if 'data' in result and len(result['data']) > 0:
                    processed_image_data = base64.b64decode(result['data'][0]['b64_json'])
                    
                    # 保存处理后的图片
                    output_path = image_path.replace('.', '_processed.')
                    with open(output_path, 'wb') as f:
                        f.write(processed_image_data)
                    
                    self.logger.info(f"图片背景替换成功: {output_path}")
                    return output_path
            
            self.logger.error(f"API请求失败: {response.status_code} - {response.text}")
            return None
            
        except Exception as e:
            self.logger.error(f"图片处理失败: {e}")
            return None
    
    def navigate_to_url(self, url):
        """导航到指定URL"""
        try:
            self.driver.get(url)
            self.logger.info(f"成功导航到: {url}")
            time.sleep(2)  # 等待页面加载
            return True
        except Exception as e:
            self.logger.error(f"导航失败: {e}")
            return False
    
    def wait_for_element(self, xpath, timeout=10):
        """等待元素出现"""
        try:
            WebDriverWait(self.driver, timeout).until(
                EC.presence_of_element_located((By.XPATH, xpath))
            )
            return True
        except Exception as e:
            self.logger.error(f"等待元素超时 {xpath}: {e}")
            return False
    
    def close(self):
        """关闭浏览器"""
        if self.driver:
            self.driver.quit()
            self.logger.info("浏览器已关闭")

def main():
    """主函数示例"""
    tool = AutomationTool()
    
    try:
        # 示例：自动化流程
        # 1. 导航到目标网站
        # tool.navigate_to_url("https://example.com")
        
        # 2. 查找并点击元素
        # tool.click_element("//button[@id='upload-btn']")
        
        # 3. 输入文本
        # tool.input_text("//input[@name='description']", "这是描述文本")
        
        # 4. 获取文本
        # text = tool.get_text("//div[@class='content']")
        
        # 5. 下载图片
        # image_path = tool.download_image("https://example.com/image.jpg")
        
        # 6. 处理图片背景
        # if image_path:
        #     processed_path = tool.process_image_with_yuanbao(image_path, "纯白色背景")
        
        # 7. 上传处理后的图片
        # if processed_path:
        #     tool.upload_image("//input[@type='file']", processed_path)
        
        print("自动化工具初始化完成，请根据具体需求调用相应方法")
        
    except Exception as e:
        print(f"执行过程中出现错误: {e}")
    finally:
        tool.close()

if __name__ == "__main__":
    main()