#!/usr/bin/env python3.8
# -*- coding: utf-8 -*-
"""
腾讯元器API客户端
用于上传本地图片并发送标注指令，确保保持原图分辨率
"""

import os
import json
import base64
import requests
from typing import Dict, Any, Optional, Tuple
from PIL import Image
import hashlib
import time
from datetime import datetime

class YuanQiAPIClient:
    """腾讯元器API客户端"""
    
    def __init__(self, api_key: str, api_secret: str, endpoint: str, agent_id: str, token: str):
        """
        初始化API客户端
        
        Args:
            api_key: API密钥
            api_secret: API密钥
            endpoint: API端点
            agent_id: 智能体ID
            token: Token
        """
        self.api_key = api_key
        self.api_secret = api_secret
        self.endpoint = endpoint.rstrip('/')
        self.agent_id = agent_id
        self.token = token
        self.session = requests.Session()
        
        # 设置默认请求头
        self.session.headers.update({
            'User-Agent': 'YuanQi-API-Client/1.0',
            'Content-Type': 'application/json',
            'Authorization': f'Bearer {self.api_key}',
            'X-Source': 'openapi'
        })
    
    def get_image_info(self, image_path: str) -> Tuple[int, int, str]:
        """
        获取图片信息
        
        Args:
            image_path: 图片路径
            
        Returns:
            (width, height, format): 图片宽度、高度和格式
        """
        try:
            with Image.open(image_path) as img:
                width, height = img.size
                format_name = img.format or 'JPEG'
                return width, height, format_name
        except Exception as e:
            print(f"❌ 获取图片信息失败: {e}")
            return 0, 0, 'JPEG'
    
    def encode_image_to_base64(self, image_path: str) -> Optional[str]:
        """
        将图片编码为base64
        
        Args:
            image_path: 图片路径
            
        Returns:
            base64编码的图片数据
        """
        try:
            with open(image_path, 'rb') as image_file:
                encoded_string = base64.b64encode(image_file.read()).decode('utf-8')
                return encoded_string
        except Exception as e:
            print(f"❌ 图片编码失败: {e}")
            return None
    
    def upload_image(self, image_path: str, preserve_resolution: bool = True) -> Optional[str]:
        """
        将图片转换为base64编码的data URL（用于多模态智能体API）
        
        Args:
            image_path: 本地图片路径
            preserve_resolution: 是否保持原图分辨率
            
        Returns:
            base64编码的data URL字符串
        """
        if not os.path.exists(image_path):
            print(f"❌ 图片文件不存在: {image_path}")
            return None
        
        try:
            # 获取图片信息
            width, height, img_format = self.get_image_info(image_path)
            print(f"📷 图片信息: {width}x{height}, 格式: {img_format}")
            
            # 将图片转换为base64编码
            base64_image = self.encode_image_to_base64(image_path)
            if not base64_image:
                print("❌ 图片base64编码失败")
                return None
            
            # 构建data URL
            mime_type = f"image/{img_format.lower()}"
            if img_format.lower() == 'jpg':
                mime_type = "image/jpeg"
            
            data_url = f"data:{mime_type};base64,{base64_image}"
            print(f"✅ 图片已转换为data URL")
            print(f"📋 Data URL长度: {len(data_url)} 字符")
            
            return data_url
                
        except Exception as e:
            print(f"❌ 图片处理异常: {e}")
            return None
    
    def send_annotation_request(self, image_id: str, instruction: str, original_size: str) -> Optional[Dict[str, Any]]:
        """
        发送标注指令
        
        Args:
            image_id: 上传后的图片ID
            instruction: 标注指令
            original_size: 原图尺寸 (格式: "1920X1080")
            
        Returns:
            标注结果
        """
        try:
            # 解析原图尺寸
            if 'X' in original_size.upper():
                width, height = original_size.upper().split('X')
                width, height = int(width), int(height)
            else:
                width, height = 1920, 1080  # 默认尺寸
            
            # 构建聊天完成请求（标注指令）
            annotation_data = {
                'assistant_id': self.agent_id,
                'user_id': 'user_001',
                'stream': False,
                'messages': [
                    {
                        'role': 'user',
                        'content': [
                            {
                                'type': 'text',
                                'text': f'{instruction}。请保持原始分辨率{original_size}，图片ID: {image_id}'
                            }
                        ]
                    }
                ]
            }
            
            # 发送标注请求
            annotation_url = f"{self.endpoint}/v1/agent/chat/completions"
            print(f"🔄 发送标注请求到: {annotation_url}")
            print(f"📝 标注指令: {instruction}")
            print(f"📐 原图尺寸: {original_size}")
            
            # 确保请求头正确设置
            headers = {
                'X-Source': 'openapi',
                'Content-Type': 'application/json',
                'Authorization': f'Bearer {self.api_key}'
            }
            
            response = requests.post(annotation_url, headers=headers, json=annotation_data, timeout=120)
            
            if response.status_code == 200:
                result = response.json()
                print(f"✅ 标注请求发送成功")
                print(f"📋 任务ID: {result.get('task_id', 'N/A')}")
                return result
            else:
                print(f"❌ 标注请求失败: {response.status_code}")
                print(f"📄 响应内容: {response.text}")
                return None
                
        except Exception as e:
            print(f"❌ 标注请求异常: {e}")
            return None
    
    def check_task_status(self, task_id: str) -> Optional[Dict[str, Any]]:
        """
        检查任务状态（腾讯元器API直接返回结果，无需单独状态检查）
        
        Args:
            task_id: 任务ID（实际为响应结果）
            
        Returns:
            任务状态信息
        """
        print(f"📊 腾讯元器API直接返回结果，无需状态检查")
        return {'status': 'completed', 'message': '腾讯元器API直接返回结果'}
    
    def process_image_with_annotation(self, image_path: str, instruction: str, original_size: str) -> Optional[Dict[str, Any]]:
        """
        完整的图片处理流程：使用多模态智能体聊天API
        
        Args:
            image_path: 本地图片路径
            instruction: 标注指令（prompt）
            original_size: 原图尺寸
            
        Returns:
            处理结果
        """
        print(f"\n🚀 开始处理图片: {os.path.basename(image_path)}")
        print(f"📝 标注指令: {instruction}")
        print(f"📐 原图尺寸: {original_size}")
        
        try:
            # 将图片转换为data URL
            data_url = self.upload_image(image_path)
            if not data_url:
                print("❌ 图片处理失败")
                return None
            
            print(f"✅ 获取到图片data URL")
            
            # 调用多模态智能体聊天API
            chat_url = f"{self.endpoint}/v1/agent/chat/completions"
            print(f"🔄 调用多模态智能体API: {chat_url}")
            
            # 构建聊天请求数据（按照文档格式）
            chat_data = {
                "assistant_id": self.agent_id,
                "user_id": "user_001",
                "stream": False,
                "messages": [
                    {
                        "role": "user",
                        "content": [
                            {
                                "type": "text",
                                "text": instruction
                            },
                            {
                                "type": "image_url",
                                "image_url": {
                                    "url": data_url
                                }
                            }
                        ]
                    }
                ]
            }
            
            print(f"📋 发送的请求数据: {json.dumps(chat_data, indent=2, ensure_ascii=False)[:500]}...")
            
            # 设置请求头
            headers = {
                'X-Source': 'openapi',
                'Content-Type': 'application/json',
                'Authorization': f'Bearer {self.api_key}'
            }
            
            response = requests.post(chat_url, headers=headers, json=chat_data, timeout=120)
            
            if response.status_code == 200:
                result = response.json()
                print(f"✅ 多模态智能体API调用成功")
                
                # 处理API返回的图片并保存到原目录
                processed_image_path = self.save_processed_image(result, image_path)
                
                # 返回完整结果
                complete_result = {
                    'api_response': result,
                    'image_path': image_path,
                    'processed_image_path': processed_image_path,
                    'instruction': instruction,
                    'original_size': original_size,
                    'processed_at': datetime.now().isoformat()
                }
                
                return complete_result
            else:
                print(f"❌ 多模态智能体API调用失败: {response.status_code}")
                print(f"📄 响应内容: {response.text}")
                return None
                
        except Exception as e:
            print(f"❌ 图片处理异常: {e}")
            return None
    
    def save_processed_image(self, api_result: Dict[str, Any], original_image_path: str) -> Optional[str]:
        """
        保存API处理后的图片到原图片所在目录
        
        Args:
            api_result: API返回结果
            original_image_path: 原图片路径
            
        Returns:
            保存的图片路径
        """
        try:
            # 从API结果中提取图片URL
            # 根据多模态智能体API的返回格式
            image_url = None
            
            # 检查choices字段（多模态智能体API格式）
            if 'choices' in api_result and api_result['choices']:
                choices = api_result['choices']
                if isinstance(choices, list) and choices:
                    choice = choices[0]
                    if isinstance(choice, dict):
                        # 检查message中的steps字段
                        if 'message' in choice and 'steps' in choice['message']:
                            for step in choice['message']['steps']:
                                if step.get('role') == 'tool' and 'content' in step:
                                    # 检查tool调用是否成功且包含图片URL
                                    if not step.get('tool_call_error', False):
                                        try:
                                            # 尝试解析JSON格式的content
                                            if step['content'].startswith('{'):
                                                tool_content = json.loads(step['content'])
                                                if 'image_url' in tool_content:
                                                    image_url = tool_content['image_url']
                                                    break
                                                elif 'images' in tool_content and tool_content['images']:
                                                    image_info = tool_content['images'][0]
                                                    if 'image_url' in image_info:
                                                        image_url = image_info['image_url']
                                                        break
                                            else:
                                                # 直接检查content是否为URL
                                                if step['content'].startswith('http'):
                                                    image_url = step['content']
                                                    break
                                        except (json.JSONDecodeError, KeyError, IndexError):
                                            continue
                        
                        # 检查message content中的URL
                        if not image_url and 'message' in choice and 'content' in choice['message']:
                            content = choice['message']['content']
                            if isinstance(content, str):
                                # 从文本中提取URL（如果包含）
                                import re
                                url_pattern = r'https?://[^\s]+'
                                urls = re.findall(url_pattern, content)
                                for url in urls:
                                    # 检查是否为图片URL
                                    if any(ext in url.lower() for ext in ['.jpg', '.jpeg', '.png', '.gif', '.webp']):
                                        image_url = url
                                        break
            
            # 检查steps字段（如果在顶层）
            if not image_url and 'steps' in api_result:
                for step in api_result['steps']:
                    if step.get('role') == 'tool' and 'content' in step:
                        try:
                            tool_content = json.loads(step['content'])
                            if 'images' in tool_content and tool_content['images']:
                                image_info = tool_content['images'][0]
                                if 'image_url' in image_info:
                                    image_url = image_info['image_url']
                                    break
                        except (json.JSONDecodeError, KeyError, IndexError):
                            continue
            
            # 如果获取到了图片URL，下载并保存
            if image_url:
                print(f"📷 下载处理后的图片: {image_url}")
                
                # 下载图片
                response = requests.get(image_url, timeout=60)
                if response.status_code == 200:
                    # 生成新的文件名（在原文件名基础上添加-1）
                    original_dir = os.path.dirname(original_image_path)
                    original_filename = os.path.basename(original_image_path)
                    name_without_ext, ext = os.path.splitext(original_filename)
                    new_filename = f"{name_without_ext}-1{ext}"
                    new_image_path = os.path.join(original_dir, new_filename)
                    
                    # 保存图片
                    with open(new_image_path, 'wb') as f:
                        f.write(response.content)
                    
                    print(f"💾 处理后的图片已保存: {new_image_path}")
                    return new_image_path
                else:
                    print(f"❌ 下载图片失败: {response.status_code}")
                    return None
            
            print("⚠️  API返回结果中未找到图片数据")
            print(f"📋 API返回结果结构: {json.dumps(api_result, indent=2, ensure_ascii=False)[:500]}...")
            return None
            
        except Exception as e:
            print(f"❌ 保存处理后图片失败: {e}")
            return None


def create_yuanqi_client_from_env() -> Optional[YuanQiAPIClient]:
    """
    从环境变量创建腾讯元器API客户端
    
    Returns:
        YuanQiAPIClient实例或None
    """
    from dotenv import load_dotenv
    import os
    
    # 获取项目根目录
    current_dir = os.path.dirname(os.path.abspath(__file__))
    project_root = os.path.dirname(os.path.dirname(current_dir))
    env_path = os.path.join(project_root, 'config', '.env')
    
    # 加载环境变量
    load_dotenv(env_path)
    print(f"📁 加载配置文件: {env_path}")
    
    api_key = os.getenv('TENCENT_API_KEY')
    api_secret = os.getenv('TENCENT_API_SECRET')
    endpoint = os.getenv('TENCENT_API_ENDPOINT', 'https://yuanqi.tencent.com/api')
    agent_id = os.getenv('AGENT_ID')
    token = os.getenv('TOKEN')
    
    if not all([api_key, api_secret, agent_id, token]):
        print("❌ 缺少必要的API配置信息")
        print(f"API Key: {'✓' if api_key else '✗'}")
        print(f"API Secret: {'✓' if api_secret else '✗'}")
        print(f"Agent ID: {'✓' if agent_id else '✗'}")
        print(f"Token: {'✓' if token else '✗'}")
        return None
    
    return YuanQiAPIClient(api_key, api_secret, endpoint, agent_id, token)


if __name__ == "__main__":
    # 测试代码
    client = create_yuanqi_client_from_env()
    if client:
        print("✅ 腾讯元器API客户端创建成功")
        print(f"📡 API端点: {client.endpoint}")
        print(f"🤖 智能体ID: {client.agent_id}")
    else:
        print("❌ 腾讯元器API客户端创建失败")