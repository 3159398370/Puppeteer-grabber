#!/usr/bin/env python3.8
# -*- coding: utf-8 -*-
"""
命令行界面模块
提供用户友好的交互界面
"""

import os
import sys
import argparse
import json
from typing import List
from task_executor import TaskExecutor
from config import Config, BACKGROUND_OPTIONS
import logging

class CLI:
    """命令行界面类"""
    
    def __init__(self):
        self.executor = None
        self.setup_logging()
        
    def setup_logging(self):
        """设置日志"""
        logging.basicConfig(
            level=getattr(logging, Config.LOG_LEVEL),
            format='%(asctime)s - %(levelname)s - %(message)s'
        )
    
    def show_welcome(self):
        """显示欢迎信息"""
        print("\n" + "="*60)
        print("    数据标注自动化工具 v1.0")
        print("    支持图片下载、背景替换、文本复制等功能")
        print("="*60 + "\n")
    
    def show_menu(self):
        """显示主菜单"""
        print("请选择操作:")
        print("1. 执行数据标注工作流")
        print("2. 批量上传图片")
        print("3. 单张图片背景替换")
        print("4. 配置管理")
        print("5. 查看帮助")
        print("0. 退出程序")
        print("-" * 40)
    
    def get_user_input(self, prompt: str, default: str = None) -> str:
        """获取用户输入"""
        if default:
            prompt += f" (默认: {default})"
        prompt += ": "
        
        user_input = input(prompt).strip()
        return user_input if user_input else default
    
    def get_background_choice(self) -> str:
        """获取背景选择"""
        print("\n可用的背景选项:")
        for i, (key, desc) in enumerate(BACKGROUND_OPTIONS.items(), 1):
            print(f"{i}. {key} - {desc}")
        
        while True:
            try:
                choice = int(input("请选择背景类型 (输入数字): "))
                if 1 <= choice <= len(BACKGROUND_OPTIONS):
                    return list(BACKGROUND_OPTIONS.keys())[choice - 1]
                else:
                    print("无效选择，请重新输入")
            except ValueError:
                print("请输入有效数字")
    
    def execute_annotation_workflow(self):
        """执行标注工作流"""
        print("\n=== 数据标注工作流 ===")
        
        site_url = self.get_user_input("请输入标注平台URL")
        if not site_url:
            print("URL不能为空")
            return
        
        try:
            task_count = int(self.get_user_input("请输入要处理的任务数量", "10"))
        except ValueError:
            print("任务数量必须是数字")
            return
        
        background_type = self.get_background_choice()
        
        print(f"\n开始执行工作流...")
        print(f"目标URL: {site_url}")
        print(f"任务数量: {task_count}")
        print(f"背景类型: {BACKGROUND_OPTIONS[background_type]}")
        
        if not self.executor:
            self.executor = TaskExecutor()
        
        try:
            result = self.executor.execute_annotation_workflow(
                site_url=site_url,
                task_count=task_count,
                background_type=background_type
            )
            
            print("\n=== 执行结果 ===")
            print(f"总任务数: {result.get('total_tasks', 0)}")
            print(f"完成任务数: {result.get('completed_tasks', 0)}")
            print(f"成功率: {result.get('success_rate', 0):.1f}%")
            
            # 询问是否保存结果
            if input("\n是否保存详细结果到文件? (y/n): ").lower() == 'y':
                filename = self.executor.save_results()
                if filename:
                    print(f"结果已保存到: {filename}")
            
        except Exception as e:
            print(f"执行失败: {e}")
    
    def execute_batch_upload(self):
        """批量上传图片"""
        print("\n=== 批量图片上传 ===")
        
        upload_url = self.get_user_input("请输入上传页面URL")
        if not upload_url:
            print("URL不能为空")
            return
        
        # 获取图片路径
        image_dir = self.get_user_input("请输入图片目录路径", Config.DOWNLOAD_DIR)
        if not os.path.exists(image_dir):
            print(f"目录不存在: {image_dir}")
            return
        
        # 查找图片文件
        image_extensions = ['.jpg', '.jpeg', '.png', '.bmp', '.webp']
        image_paths = []
        
        for file in os.listdir(image_dir):
            if any(file.lower().endswith(ext) for ext in image_extensions):
                image_paths.append(os.path.join(image_dir, file))
        
        if not image_paths:
            print(f"在目录 {image_dir} 中未找到图片文件")
            return
        
        print(f"找到 {len(image_paths)} 张图片")
        
        # 显示前几张图片路径
        for i, path in enumerate(image_paths[:5]):
            print(f"  {i+1}. {os.path.basename(path)}")
        if len(image_paths) > 5:
            print(f"  ... 还有 {len(image_paths) - 5} 张图片")
        
        if input("\n确认上传这些图片? (y/n): ").lower() != 'y':
            return
        
        background_type = self.get_background_choice()
        
        if not self.executor:
            self.executor = TaskExecutor()
        
        try:
            result = self.executor.execute_batch_upload(
                upload_url=upload_url,
                image_paths=image_paths,
                background_type=background_type
            )
            
            print("\n=== 上传结果 ===")
            print(f"总图片数: {result.get('total', 0)}")
            print(f"成功上传: {result.get('success', 0)}")
            print(f"成功率: {result.get('success', 0) / result.get('total', 1) * 100:.1f}%")
            
        except Exception as e:
            print(f"上传失败: {e}")
    
    def process_single_image(self):
        """处理单张图片"""
        print("\n=== 单张图片背景替换 ===")
        
        image_path = self.get_user_input("请输入图片路径")
        if not image_path or not os.path.exists(image_path):
            print("图片文件不存在")
            return
        
        background_type = self.get_background_choice()
        background_prompt = BACKGROUND_OPTIONS[background_type]
        
        print(f"\n处理图片: {image_path}")
        print(f"背景类型: {background_prompt}")
        
        if not self.executor:
            self.executor = TaskExecutor()
        
        try:
            processed_path = self.executor.tool.process_image_with_yuanbao(
                image_path, background_prompt
            )
            
            if processed_path:
                print(f"\n处理成功!")
                print(f"原图片: {image_path}")
                print(f"处理后: {processed_path}")
            else:
                print("图片处理失败，请检查API配置")
                
        except Exception as e:
            print(f"处理失败: {e}")
    
    def manage_config(self):
        """配置管理"""
        print("\n=== 配置管理 ===")
        print("1. 查看当前配置")
        print("2. 设置腾讯元宝API")
        print("3. 返回主菜单")
        
        choice = input("请选择: ")
        
        if choice == '1':
            self.show_current_config()
        elif choice == '2':
            self.setup_api_config()
        elif choice == '3':
            return
        else:
            print("无效选择")
    
    def show_current_config(self):
        """显示当前配置"""
        print("\n当前配置:")
        print(f"下载目录: {Config.DOWNLOAD_DIR}")
        print(f"日志级别: {Config.LOG_LEVEL}")
        print(f"等待超时: {Config.WAIT_TIMEOUT}秒")
        print(f"API密钥: {'已配置' if Config.TENCENT_API_KEY else '未配置'}")
        print(f"API端点: {Config.TENCENT_API_ENDPOINT}")
    
    def setup_api_config(self):
        """设置API配置"""
        print("\n=== 腾讯元宝API配置 ===")
        print("请访问腾讯元宝开放平台获取API密钥")
        
        api_key = self.get_user_input("请输入API Key")
        api_secret = self.get_user_input("请输入API Secret")
        agent_id = self.get_user_input("请输入智能体ID")
        token = self.get_user_input("请输入Token")
        
        if api_key and api_secret:
            # 更新.env文件
            env_file = '.env'
            env_content = f"""TENCENT_API_KEY={api_key}
TENCENT_API_SECRET={api_secret}
TENCENT_API_ENDPOINT=https://api.yuanbao.tencent.com

AGENT_ID={agent_id or 'NpqYVYeG7vTS'}
TOKEN={token or 'wAyiMAgWBaEg7eKroh406ncUnXYBDlez'}

DOWNLOAD_DIR=./downloads
LOG_LEVEL=INFO
BROWSER_HEADLESS=false
WAIT_TIMEOUT=10"""
            
            try:
                with open(env_file, 'w', encoding='utf-8') as f:
                    f.write(env_content)
                print(f"\nAPI配置已保存到 {env_file}")
                print("请重启程序以使配置生效")
            except Exception as e:
                print(f"保存配置失败: {e}")
        else:
            print("API密钥不能为空")
    
    def show_help(self):
        """显示帮助信息"""
        help_text = """
=== 使用帮助 ===

1. 数据标注工作流:
   - 自动访问标注平台
   - 下载任务图片并替换背景
   - 复制和处理文本内容
   - 提交标注结果

2. 批量图片上传:
   - 批量处理指定目录中的图片
   - 自动替换图片背景
   - 批量上传到指定平台

3. 单张图片处理:
   - 使用腾讯元宝API替换图片背景
   - 支持多种背景类型

4. 配置要求:
   - 需要配置腾讯元宝API密钥
   - 确保Chrome浏览器已安装
   - 网络连接正常

5. 支持的图片格式:
   - JPG, JPEG, PNG, BMP, WebP

6. 注意事项:
   - 首次使用需要配置API密钥
   - 建议在稳定网络环境下使用
   - 大批量任务建议分批处理
"""
        print(help_text)
    
    def run(self):
        """运行CLI界面"""
        self.show_welcome()
        
        # 检查API配置
        if not Config.TENCENT_API_KEY:
            print("⚠️  检测到腾讯元宝API未配置")
            if input("是否现在配置? (y/n): ").lower() == 'y':
                self.setup_api_config()
                print("\n请重启程序以使配置生效")
                return
        
        try:
            while True:
                self.show_menu()
                choice = input("请选择操作 (0-5): ").strip()
                
                if choice == '0':
                    print("\n感谢使用，再见!")
                    break
                elif choice == '1':
                    self.execute_annotation_workflow()
                elif choice == '2':
                    self.execute_batch_upload()
                elif choice == '3':
                    self.process_single_image()
                elif choice == '4':
                    self.manage_config()
                elif choice == '5':
                    self.show_help()
                else:
                    print("无效选择，请重新输入")
                
                input("\n按回车键继续...")
                
        except KeyboardInterrupt:
            print("\n\n程序被用户中断")
        except Exception as e:
            print(f"\n程序运行出错: {e}")
        finally:
            if self.executor:
                self.executor.close()

def main():
    """主函数"""
    parser = argparse.ArgumentParser(description='数据标注自动化工具')
    parser.add_argument('--config', help='配置文件路径')
    parser.add_argument('--headless', action='store_true', help='无头模式运行')
    parser.add_argument('--log-level', choices=['DEBUG', 'INFO', 'WARNING', 'ERROR'], 
                       default='INFO', help='日志级别')
    
    args = parser.parse_args()
    
    # 设置日志级别
    if args.log_level:
        os.environ['LOG_LEVEL'] = args.log_level
    
    # 设置无头模式
    if args.headless:
        os.environ['BROWSER_HEADLESS'] = 'true'
    
    # 运行CLI
    cli = CLI()
    cli.run()

if __name__ == "__main__":
    main()