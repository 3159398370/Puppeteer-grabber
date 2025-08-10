#!/usr/bin/env python3.8
# -*- coding: utf-8 -*-
"""
配置管理模块
"""

import os
from dotenv import load_dotenv

# 加载环境变量
load_dotenv()

class Config:
    """配置类"""
    
    # API配置
    TENCENT_API_KEY = os.getenv('TENCENT_API_KEY')
    TENCENT_API_SECRET = os.getenv('TENCENT_API_SECRET')
    TENCENT_API_ENDPOINT = os.getenv('TENCENT_API_ENDPOINT', 'https://api.yuanbao.tencent.com')
    
    # 智能体配置
    AGENT_ID = os.getenv('AGENT_ID')
    TOKEN = os.getenv('TOKEN')
    
    # 文件路径配置
    DOWNLOAD_DIR = os.getenv('DOWNLOAD_DIR', './downloads')
    LOG_LEVEL = os.getenv('LOG_LEVEL', 'INFO')
    
    # 浏览器配置
    BROWSER_HEADLESS = os.getenv('BROWSER_HEADLESS', 'false').lower() == 'true'
    WAIT_TIMEOUT = int(os.getenv('WAIT_TIMEOUT', '10'))
    
    # 确保下载目录存在
    @classmethod
    def ensure_download_dir(cls):
        os.makedirs(cls.DOWNLOAD_DIR, exist_ok=True)
        return cls.DOWNLOAD_DIR

class XPathSelectors:
    """XPath选择器配置类
    
    根据不同网站配置相应的XPath选择器
    """
    
    # 通用选择器
    COMMON = {
        'file_input': "//input[@type='file']",
        'submit_button': "//button[@type='submit']",
        'upload_button': "//button[contains(text(), '上传') or contains(text(), 'Upload')]",
        'download_link': "//a[contains(@href, 'download') or contains(text(), '下载')]",
        'image_element': "//img",
        'text_input': "//input[@type='text'] | //textarea",
        'copy_button': "//button[contains(text(), '复制') or contains(text(), 'Copy')]"
    }
    
    # 示例：某个具体网站的选择器
    EXAMPLE_SITE = {
        'login_username': "//input[@name='username']",
        'login_password': "//input[@name='password']",
        'login_button': "//button[@id='login-btn']",
        'upload_area': "//div[@class='upload-area']",
        'image_preview': "//div[@class='image-preview']//img",
        'description_input': "//textarea[@name='description']",
        'tags_input': "//input[@name='tags']",
        'save_button': "//button[@class='save-btn']",
        'result_text': "//div[@class='result-content']"
    }
    
    # 数据标注平台选择器（可根据实际平台调整）
    ANNOTATION_PLATFORM = {
        'task_list': "//div[@class='task-list']//div[@class='task-item']",
        'task_title': ".//h3[@class='task-title']",
        'task_image': ".//img[@class='task-image']",
        'annotation_input': "//textarea[@class='annotation-text']",
        'category_select': "//select[@name='category']",
        'submit_annotation': "//button[@class='submit-annotation']",
        'next_task': "//button[contains(text(), '下一个') or contains(text(), 'Next')]",
        'copy_text_btn': "//button[@class='copy-text']",
        'paste_area': "//div[@class='paste-area']"
    }
    
    @classmethod
    def get_selectors(cls, site_type='common'):
        """获取指定类型的选择器"""
        selector_map = {
            'common': cls.COMMON,
            'example': cls.EXAMPLE_SITE,
            'annotation': cls.ANNOTATION_PLATFORM
        }
        return selector_map.get(site_type, cls.COMMON)

class TaskConfig:
    """任务配置类"""
    
    # 图片处理配置
    IMAGE_PROCESSING = {
        'supported_formats': ['.jpg', '.jpeg', '.png', '.bmp', '.webp'],
        'max_file_size': 10 * 1024 * 1024,  # 10MB
        'default_background': '白色背景',
        'quality': 95
    }
    
    # 自动化任务配置
    AUTOMATION = {
        'retry_times': 3,
        'retry_delay': 2,  # 秒
        'page_load_timeout': 30,
        'element_wait_timeout': 10,
        'batch_size': 10,  # 批处理大小
        'delay_between_tasks': 1  # 任务间延迟
    }
    
    # 文本处理配置
    TEXT_PROCESSING = {
        'max_length': 1000,
        'encoding': 'utf-8',
        'auto_copy': True,
        'format_text': True
    }

# 预定义的背景替换选项
BACKGROUND_OPTIONS = {
    'white': '纯白色背景',
    'transparent': '透明背景',
    'black': '纯黑色背景',
    'blue': '蓝色背景',
    'green': '绿色背景',
    'office': '办公室背景',
    'nature': '自然风景背景',
    'studio': '摄影棚背景'
}

# 常用的用户代理字符串
USER_AGENTS = [
    'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
    'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/119.0.0.0 Safari/537.36',
    'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'
]