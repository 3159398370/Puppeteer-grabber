#!/usr/bin/env python3.8
# -*- coding: utf-8 -*-
"""
使用示例脚本
展示如何使用自动化工具进行各种任务
"""

import os
import sys
import time

# 添加项目根目录到Python路径
project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if project_root not in sys.path:
    sys.path.insert(0, project_root)

from src.core.main import AutomationTool
from src.core.task_executor import TaskExecutor
from src.core.config import Config, XPathSelectors

def example_basic_automation():
    """示例1: 基础自动化操作"""
    print("=== 示例1: 基础自动化操作 ===")
    
    tool = AutomationTool()
    
    try:
        # 1. 导航到测试页面
        print("1. 导航到测试页面...")
        tool.navigate_to_url("https://httpbin.org/forms/post")
        
        # 2. 填写表单
        print("2. 填写表单...")
        tool.input_text("//input[@name='custname']", "测试用户")
        tool.input_text("//input[@name='custtel']", "13800138000")
        tool.input_text("//input[@name='custemail']", "test@example.com")
        
        # 3. 选择单选按钮
        print("3. 选择选项...")
        tool.click_element("//input[@value='large']")
        
        # 4. 获取页面文本
        print("4. 获取页面信息...")
        title = tool.get_text("//h1")
        print(f"页面标题: {title}")
        
        # 5. 提交表单（注释掉避免实际提交）
        # tool.click_element("//input[@type='submit']")
        
        print("基础操作演示完成！")
        
    except Exception as e:
        print(f"操作失败: {e}")
    finally:
        tool.close()

def example_image_processing():
    """示例2: 图片下载和背景处理"""
    print("\n=== 示例2: 图片处理 ===")
    
    tool = AutomationTool()
    
    try:
        # 确保下载目录存在
        Config.ensure_download_dir()
        
        # 1. 下载示例图片
        print("1. 下载示例图片...")
        image_url = "https://httpbin.org/image/jpeg"
        image_path = tool.download_image(image_url, "example_image.jpg")
        
        if image_path and os.path.exists(image_path):
            print(f"图片下载成功: {image_path}")
            
            # 2. 处理图片背景（需要配置API）
            if Config.TENCENT_API_KEY:
                print("2. 处理图片背景...")
                processed_path = tool.process_image_with_yuanbao(
                    image_path, "纯白色背景"
                )
                
                if processed_path:
                    print(f"背景处理成功: {processed_path}")
                else:
                    print("背景处理失败，可能是API配置问题")
            else:
                print("2. 跳过背景处理（未配置API密钥）")
        else:
            print("图片下载失败")
            
    except Exception as e:
        print(f"图片处理失败: {e}")
    finally:
        tool.close()

def example_custom_selectors():
    """示例3: 使用自定义选择器"""
    print("\n=== 示例3: 自定义选择器 ===")
    
    # 定义自定义选择器
    custom_selectors = {
        'search_input': "//input[@name='q']",
        'search_button': "//input[@type='submit']",
        'results': "//div[@class='result']"
    }
    
    tool = AutomationTool()
    
    try:
        # 1. 导航到搜索页面
        print("1. 导航到搜索页面...")
        tool.navigate_to_url("https://httpbin.org/forms/post")
        
        # 2. 使用自定义选择器进行操作
        print("2. 使用自定义选择器...")
        
        # 查找元素
        element = tool.find_element_by_xpath("//input[@name='custname']")
        if element:
            print("成功找到客户姓名输入框")
            tool.input_text("//input[@name='custname']", "自定义选择器测试")
        
        # 等待元素出现
        if tool.wait_for_element("//input[@name='custtel']"):
            print("电话输入框已就绪")
            tool.input_text("//input[@name='custtel']", "12345678900")
        
        print("自定义选择器演示完成！")
        
    except Exception as e:
        print(f"操作失败: {e}")
    finally:
        tool.close()

def example_batch_processing():
    """示例4: 批量处理任务"""
    print("\n=== 示例4: 批量处理 ===")
    
    executor = TaskExecutor()
    
    try:
        # 创建一些测试图片路径（实际使用时替换为真实路径）
        test_images = []
        download_dir = Config.ensure_download_dir()
        
        # 检查是否有现有图片
        for file in os.listdir(download_dir):
            if file.lower().endswith(('.jpg', '.jpeg', '.png')):
                test_images.append(os.path.join(download_dir, file))
        
        if test_images:
            print(f"找到 {len(test_images)} 张图片进行批量处理")
            
            # 模拟批量上传（使用测试URL）
            result = executor.execute_batch_upload(
                upload_url="https://httpbin.org/post",  # 测试URL
                image_paths=test_images[:3],  # 只处理前3张
                background_type='white'
            )
            
            print(f"批量处理结果:")
            print(f"- 总数: {result.get('total', 0)}")
            print(f"- 成功: {result.get('success', 0)}")
            
        else:
            print("未找到图片文件，跳过批量处理演示")
            
    except Exception as e:
        print(f"批量处理失败: {e}")
    finally:
        executor.close()

def example_error_handling():
    """示例5: 错误处理和重试机制"""
    print("\n=== 示例5: 错误处理 ===")
    
    tool = AutomationTool()
    
    try:
        # 1. 测试无效URL
        print("1. 测试错误处理...")
        success = tool.navigate_to_url("https://invalid-url-for-testing.com")
        if not success:
            print("正确处理了无效URL")
        
        # 2. 测试不存在的元素
        print("2. 测试元素查找...")
        tool.navigate_to_url("https://httpbin.org")
        
        element = tool.find_element_by_xpath("//div[@id='non-existent-element']", timeout=2)
        if not element:
            print("正确处理了不存在的元素")
        
        # 3. 测试重试机制
        print("3. 测试重试机制...")
        for attempt in range(3):
            try:
                # 尝试点击可能不存在的元素
                success = tool.click_element("//button[@id='maybe-exists']", timeout=1)
                if success:
                    break
                else:
                    print(f"尝试 {attempt + 1} 失败，准备重试...")
                    time.sleep(1)
            except Exception as e:
                print(f"尝试 {attempt + 1} 异常: {e}")
                if attempt == 2:
                    print("所有重试都失败了")
        
        print("错误处理演示完成！")
        
    except Exception as e:
        print(f"演示过程出错: {e}")
    finally:
        tool.close()

def example_configuration():
    """示例6: 配置使用"""
    print("\n=== 示例6: 配置管理 ===")
    
    # 1. 显示当前配置
    print("1. 当前配置:")
    print(f"   下载目录: {Config.DOWNLOAD_DIR}")
    print(f"   日志级别: {Config.LOG_LEVEL}")
    print(f"   等待超时: {Config.WAIT_TIMEOUT}秒")
    print(f"   API配置: {'已配置' if Config.TENCENT_API_KEY else '未配置'}")
    
    # 2. 获取选择器
    print("\n2. 可用选择器:")
    common_selectors = XPathSelectors.get_selectors('common')
    for name, xpath in common_selectors.items():
        print(f"   {name}: {xpath}")
    
    # 3. 确保目录存在
    print("\n3. 目录管理:")
    download_dir = Config.ensure_download_dir()
    print(f"   下载目录已确保存在: {download_dir}")
    
    # 4. 背景选项
    print("\n4. 可用背景选项:")
    from config import BACKGROUND_OPTIONS
    for key, desc in BACKGROUND_OPTIONS.items():
        print(f"   {key}: {desc}")

def main():
    """运行所有示例"""
    print("数据标注自动化工具 - 使用示例")
    print("=" * 50)
    
    examples = [
        ("基础自动化操作", example_basic_automation),
        ("图片处理", example_image_processing),
        ("自定义选择器", example_custom_selectors),
        ("批量处理", example_batch_processing),
        ("错误处理", example_error_handling),
        ("配置管理", example_configuration)
    ]
    
    print("\n可用示例:")
    for i, (name, _) in enumerate(examples, 1):
        print(f"{i}. {name}")
    print("0. 运行所有示例")
    
    try:
        choice = input("\n请选择要运行的示例 (0-6): ").strip()
        
        if choice == '0':
            # 运行所有示例
            for name, func in examples:
                print(f"\n{'='*20} {name} {'='*20}")
                func()
                time.sleep(2)  # 示例间延迟
        elif choice.isdigit() and 1 <= int(choice) <= len(examples):
            # 运行指定示例
            name, func = examples[int(choice) - 1]
            print(f"\n{'='*20} {name} {'='*20}")
            func()
        else:
            print("无效选择")
            
    except KeyboardInterrupt:
        print("\n\n示例被用户中断")
    except Exception as e:
        print(f"\n运行示例时出错: {e}")
    
    print("\n示例演示完成！")

if __name__ == "__main__":
    main()