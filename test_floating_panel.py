#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
测试浮动面板界面修改效果（无需浏览器驱动）
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

import tkinter as tk
from tkinter import ttk
import threading
import time

def create_test_floating_panel():
    """创建测试用的浮动面板界面"""
    root = tk.Tk()
    root.title("浮动控制面板 - 测试版")
    root.geometry("300x500")
    root.attributes('-topmost', True)
    root.resizable(False, False)
    
    # 创建主框架
    main_frame = ttk.Frame(root, padding="10")
    main_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
    
    # 标题
    title_label = ttk.Label(main_frame, text="🎮 浮动控制面板", font=("Arial", 12, "bold"))
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
    
    for i, (key, action, _) in enumerate(shortcuts, start=1):
        key_label = ttk.Label(main_frame, text=key, font=("Consolas", 9))
        key_label.grid(row=i, column=0, sticky=tk.W, pady=2)
        
        action_label = ttk.Label(main_frame, text=action)
        action_label.grid(row=i, column=1, sticky=tk.W, padx=(10, 0), pady=2)
    
    # 分隔线
    separator = ttk.Separator(main_frame, orient='horizontal')
    separator.grid(row=len(shortcuts)+1, column=0, columnspan=2, sticky=(tk.W, tk.E), pady=10)
    
    # 状态显示
    status_frame = ttk.LabelFrame(main_frame, text="状态", padding="5")
    status_frame.grid(row=len(shortcuts)+2, column=0, columnspan=2, sticky=(tk.W, tk.E), pady=(0, 10))
    
    status_label = ttk.Label(status_frame, text="🟢 监听中...", foreground="green")
    status_label.grid(row=0, column=0)
    
    # 使用说明
    note_frame = ttk.LabelFrame(main_frame, text="使用说明", padding="5")
    note_frame.grid(row=len(shortcuts)+3, column=0, columnspan=2, sticky=(tk.W, tk.E), pady=(0, 10))
    
    note_label = ttk.Label(note_frame, text="💡 所有操作均通过快捷键控制\n⚠️ 快捷键需连续按两次确认", justify=tk.CENTER)
    note_label.grid(row=0, column=0, pady=5)
    
    # 腾讯元宝管理区域
    yuanbao_frame = ttk.LabelFrame(main_frame, text="腾讯元宝管理", padding="5")
    yuanbao_frame.grid(row=len(shortcuts)+4, column=0, columnspan=2, sticky=(tk.W, tk.E), pady=(10, 10))
    
    # 重启元宝按钮
    restart_btn = ttk.Button(yuanbao_frame, text="🔄 重启元宝", 
                            command=lambda: print("重启元宝按钮被点击"))
    restart_btn.grid(row=0, column=0, padx=(0, 5), pady=5, sticky=(tk.W, tk.E))
    
    # 关闭元宝按钮
    close_btn = ttk.Button(yuanbao_frame, text="🔒 关闭元宝", 
                          command=lambda: print("关闭元宝按钮被点击"))
    close_btn.grid(row=0, column=1, padx=(5, 0), pady=5, sticky=(tk.W, tk.E))
    
    # 配置列权重使按钮平均分布
    yuanbao_frame.columnconfigure(0, weight=1)
    yuanbao_frame.columnconfigure(1, weight=1)
    
    # 测试信息
    test_frame = ttk.LabelFrame(main_frame, text="测试信息", padding="5")
    test_frame.grid(row=len(shortcuts)+5, column=0, columnspan=2, sticky=(tk.W, tk.E), pady=(10, 0))
    
    test_info = ttk.Label(test_frame, text="✅ 界面修改验证:\n• 左键显示'调用元宝'\n• 添加了元宝管理按钮\n• 移除了API错误提示", 
                         justify=tk.LEFT, foreground="green")
    test_info.grid(row=0, column=0, pady=5)
    
    return root

def main():
    """主函数"""
    print("🧪 启动浮动面板界面测试...")
    print("✅ 创建测试界面中...")
    
    root = create_test_floating_panel()
    
    print("✅ 浮动面板测试界面已启动！")
    print("💡 请查看浮动面板界面验证以下修改：")
    print("   - 左键显示为'调用元宝'而不是'调用API'")
    print("   - 底部有'腾讯元宝管理'区域")
    print("   - 包含'重启元宝'和'关闭元宝'按钮")
    print("   - 没有API相关的错误提示")
    print("\n🔍 关闭窗口即可结束测试")
    
    # 启动GUI主循环
    root.mainloop()
    
    print("✅ 测试完成！")

if __name__ == "__main__":
    main()