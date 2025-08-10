#!/usr/bin/env python3.8
# -*- coding: utf-8 -*-
"""
任务执行器模块
提供具体的自动化任务流程
"""

import os
import time
import json
from typing import List, Dict, Optional
from main import AutomationTool
from config import Config, XPathSelectors, TaskConfig, BACKGROUND_OPTIONS
import logging

class TaskExecutor:
    """任务执行器"""
    
    def __init__(self):
        self.tool = AutomationTool()
        self.logger = logging.getLogger(__name__)
        self.current_task = None
        self.task_results = []
        
    def execute_annotation_workflow(self, 
                                  site_url: str,
                                  task_count: int = 10,
                                  background_type: str = 'white',
                                  custom_selectors: Dict = None):
        """执行数据标注工作流
        
        Args:
            site_url: 标注平台URL
            task_count: 要处理的任务数量
            background_type: 背景类型
            custom_selectors: 自定义选择器
        """
        try:
            self.logger.info(f"开始执行标注工作流，目标任务数: {task_count}")
            
            # 导航到标注平台
            if not self.tool.navigate_to_url(site_url):
                raise Exception("无法访问标注平台")
            
            # 获取选择器
            selectors = custom_selectors or XPathSelectors.get_selectors('annotation')
            background_prompt = BACKGROUND_OPTIONS.get(background_type, '白色背景')
            
            completed_tasks = 0
            
            for i in range(task_count):
                self.logger.info(f"处理第 {i+1} 个任务")
                
                try:
                    # 执行单个任务
                    result = self._process_single_annotation_task(
                        selectors, background_prompt, i+1
                    )
                    
                    if result['success']:
                        completed_tasks += 1
                        self.task_results.append(result)
                        self.logger.info(f"任务 {i+1} 完成成功")
                    else:
                        self.logger.warning(f"任务 {i+1} 执行失败: {result.get('error')}")
                    
                    # 任务间延迟
                    time.sleep(TaskConfig.AUTOMATION['delay_between_tasks'])
                    
                except Exception as e:
                    self.logger.error(f"任务 {i+1} 执行异常: {e}")
                    continue
            
            self.logger.info(f"工作流完成，成功处理 {completed_tasks}/{task_count} 个任务")
            return {
                'total_tasks': task_count,
                'completed_tasks': completed_tasks,
                'success_rate': completed_tasks / task_count * 100,
                'results': self.task_results
            }
            
        except Exception as e:
            self.logger.error(f"工作流执行失败: {e}")
            return {'success': False, 'error': str(e)}
    
    def _process_single_annotation_task(self, selectors: Dict, background_prompt: str, task_id: int):
        """处理单个标注任务"""
        result = {
            'task_id': task_id,
            'success': False,
            'timestamp': time.time(),
            'steps': []
        }
        
        try:
            # 步骤1: 查找任务项
            task_element = self.tool.find_element_by_xpath(selectors['task_list'])
            if not task_element:
                result['error'] = '未找到任务列表'
                return result
            
            result['steps'].append('找到任务列表')
            
            # 步骤2: 获取任务标题
            title = self.tool.get_text(selectors['task_title'])
            if title:
                result['title'] = title
                result['steps'].append(f'获取任务标题: {title[:30]}...')
            
            # 步骤3: 处理图片
            image_processed = self._process_task_image(selectors, background_prompt, task_id)
            if image_processed:
                result['image_processed'] = True
                result['steps'].append('图片处理完成')
            
            # 步骤4: 复制和处理文本
            text_processed = self._process_task_text(selectors, task_id)
            if text_processed:
                result['text_processed'] = True
                result['steps'].append('文本处理完成')
            
            # 步骤5: 提交标注
            if self.tool.click_element(selectors['submit_annotation']):
                result['steps'].append('提交标注成功')
                result['success'] = True
            
            # 步骤6: 进入下一个任务
            if self.tool.click_element(selectors['next_task']):
                result['steps'].append('进入下一个任务')
            
        except Exception as e:
            result['error'] = str(e)
            self.logger.error(f"处理任务 {task_id} 时出错: {e}")
        
        return result
    
    def _process_task_image(self, selectors: Dict, background_prompt: str, task_id: int) -> bool:
        """处理任务中的图片"""
        try:
            # 查找图片元素
            image_element = self.tool.find_element_by_xpath(selectors['task_image'])
            if not image_element:
                return False
            
            # 获取图片URL
            image_url = image_element.get_attribute('src')
            if not image_url:
                return False
            
            # 下载图片
            filename = f"task_{task_id}_original.jpg"
            image_path = self.tool.download_image(image_url, filename)
            if not image_path:
                return False
            
            # 使用腾讯元宝API处理图片背景
            processed_path = self.tool.process_image_with_yuanbao(image_path, background_prompt)
            if not processed_path:
                self.logger.warning(f"图片背景处理失败，使用原图: {image_path}")
                processed_path = image_path
            
            # 上传处理后的图片（如果有上传区域）
            upload_input = self.tool.find_element_by_xpath(selectors.get('file_input', "//input[@type='file']"))
            if upload_input:
                return self.tool.upload_image(selectors['file_input'], processed_path)
            
            return True
            
        except Exception as e:
            self.logger.error(f"图片处理失败: {e}")
            return False
    
    def _process_task_text(self, selectors: Dict, task_id: int) -> bool:
        """处理任务中的文本"""
        try:
            # 查找并复制文本
            if 'copy_text_btn' in selectors:
                if self.tool.click_element(selectors['copy_text_btn']):
                    self.logger.info("文本复制成功")
            
            # 获取结果文本
            result_text = self.tool.get_text(selectors.get('result_text', "//div[@class='result']"))
            if result_text:
                # 保存文本到文件
                text_file = os.path.join(Config.ensure_download_dir(), f"task_{task_id}_text.txt")
                with open(text_file, 'w', encoding='utf-8') as f:
                    f.write(result_text)
                self.logger.info(f"文本保存到: {text_file}")
            
            # 在标注输入框中输入文本（如果需要）
            if 'annotation_input' in selectors and result_text:
                return self.tool.input_text(selectors['annotation_input'], result_text[:500])  # 限制长度
            
            return True
            
        except Exception as e:
            self.logger.error(f"文本处理失败: {e}")
            return False
    
    def execute_batch_upload(self, 
                           upload_url: str,
                           image_paths: List[str],
                           background_type: str = 'white',
                           descriptions: List[str] = None):
        """批量上传图片
        
        Args:
            upload_url: 上传页面URL
            image_paths: 图片路径列表
            background_type: 背景类型
            descriptions: 描述文本列表
        """
        try:
            self.logger.info(f"开始批量上传，共 {len(image_paths)} 张图片")
            
            if not self.tool.navigate_to_url(upload_url):
                raise Exception("无法访问上传页面")
            
            background_prompt = BACKGROUND_OPTIONS.get(background_type, '白色背景')
            upload_results = []
            
            for i, image_path in enumerate(image_paths):
                try:
                    self.logger.info(f"处理第 {i+1} 张图片: {image_path}")
                    
                    # 处理图片背景
                    processed_path = self.tool.process_image_with_yuanbao(image_path, background_prompt)
                    if not processed_path:
                        processed_path = image_path
                    
                    # 上传图片
                    if self.tool.upload_image("//input[@type='file']", processed_path):
                        # 添加描述（如果提供）
                        if descriptions and i < len(descriptions):
                            self.tool.input_text("//textarea[@name='description']", descriptions[i])
                        
                        # 提交
                        if self.tool.click_element("//button[@type='submit']"):
                            upload_results.append({
                                'index': i,
                                'original_path': image_path,
                                'processed_path': processed_path,
                                'success': True
                            })
                            self.logger.info(f"图片 {i+1} 上传成功")
                        else:
                            upload_results.append({'index': i, 'success': False, 'error': '提交失败'})
                    else:
                        upload_results.append({'index': i, 'success': False, 'error': '上传失败'})
                    
                    time.sleep(TaskConfig.AUTOMATION['delay_between_tasks'])
                    
                except Exception as e:
                    self.logger.error(f"处理图片 {i+1} 时出错: {e}")
                    upload_results.append({'index': i, 'success': False, 'error': str(e)})
            
            success_count = sum(1 for r in upload_results if r.get('success'))
            self.logger.info(f"批量上传完成，成功 {success_count}/{len(image_paths)} 张")
            
            return {
                'total': len(image_paths),
                'success': success_count,
                'results': upload_results
            }
            
        except Exception as e:
            self.logger.error(f"批量上传失败: {e}")
            return {'success': False, 'error': str(e)}
    
    def save_results(self, filename: str = None):
        """保存任务结果"""
        if not filename:
            filename = f"task_results_{int(time.time())}.json"
        
        filepath = os.path.join(Config.ensure_download_dir(), filename)
        
        try:
            with open(filepath, 'w', encoding='utf-8') as f:
                json.dump(self.task_results, f, ensure_ascii=False, indent=2)
            
            self.logger.info(f"任务结果已保存到: {filepath}")
            return filepath
        except Exception as e:
            self.logger.error(f"保存结果失败: {e}")
            return None
    
    def close(self):
        """关闭执行器"""
        if self.tool:
            self.tool.close()

def main():
    """示例用法"""
    executor = TaskExecutor()
    
    try:
        # 示例1: 执行标注工作流
        # result = executor.execute_annotation_workflow(
        #     site_url="https://your-annotation-platform.com",
        #     task_count=5,
        #     background_type='white'
        # )
        # print(f"工作流结果: {result}")
        
        # 示例2: 批量上传图片
        # image_paths = ["./downloads/image1.jpg", "./downloads/image2.jpg"]
        # descriptions = ["第一张图片描述", "第二张图片描述"]
        # upload_result = executor.execute_batch_upload(
        #     upload_url="https://your-upload-site.com",
        #     image_paths=image_paths,
        #     background_type='transparent',
        #     descriptions=descriptions
        # )
        # print(f"上传结果: {upload_result}")
        
        # 保存结果
        # executor.save_results()
        
        print("任务执行器初始化完成，请根据需要调用相应方法")
        
    except Exception as e:
        print(f"执行过程中出现错误: {e}")
    finally:
        executor.close()

if __name__ == "__main__":
    main()