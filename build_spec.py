#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
PyInstaller打包配置脚本
使用task_search.py作为主入口文件
"""

import os
import sys
from PyInstaller.building.build_main import Analysis, PYZ, EXE, COLLECT

# 项目根目录
project_root = os.path.dirname(os.path.abspath(__file__))

# 主入口文件 - 使用task_search.py作为主入口
main_script = os.path.join(project_root, 'scripts', 'task_search.py')

# 数据文件列表 (需要包含在打包中的文件)
datas = [
    # Chrome驱动
    (os.path.join(project_root, 'chromedriver.exe'), '.'),
    
    # 配置文件示例
    (os.path.join(project_root, 'config', '.env.example'), 'config'),
    
    # 脚本目录中的其他Python文件
    (os.path.join(project_root, 'scripts', 'floating_control_panel.py'), 'scripts'),
    (os.path.join(project_root, 'scripts', '__init__.py'), 'scripts'),
]

# 隐藏导入 (PyInstaller可能无法自动检测的模块)
hiddenimports = [
    'selenium',
    'selenium.webdriver',
    'selenium.webdriver.chrome',
    'selenium.webdriver.chrome.service',
    'selenium.webdriver.support',
    'selenium.webdriver.support.ui',
    'selenium.webdriver.support.expected_conditions',
    'selenium.webdriver.common.by',
    'selenium.webdriver.common.action_chains',
    'selenium.webdriver.common.keys',
    'selenium.common.exceptions',
    'requests',
    'PIL',
    'PIL.Image',
    'PIL.ImageTk',
    'tkinter',
    'tkinter.ttk',
    'json',
    'time',
    'os',
    'sys',
    'threading',
    'queue',
    'datetime',
    'base64',
    'io',
    'urllib.parse',
    'bs4',
    'BeautifulSoup4',
    'python-dotenv',
    'dotenv',
]

# 排除的模块 (减少打包体积)
excludes = [
    'matplotlib',
    'numpy',
    'pandas',
    'scipy',
    'IPython',
    'jupyter',
    'notebook',
    'pytest',
    'unittest',
    'doctest',
]

# 分析配置
a = Analysis(
    [main_script],
    pathex=[project_root],
    binaries=[],
    datas=datas,
    hiddenimports=hiddenimports,
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=excludes,
    win_no_prefer_redirects=False,
    win_private_assemblies=False,
    cipher=None,
    noarchive=False,
)

# 过滤不需要的文件
a.datas = [x for x in a.datas if not any([
    x[0].endswith('.md'),           # 排除markdown文档
    x[0].endswith('.txt') and 'requirements' not in x[0],  # 排除txt文件但保留requirements.txt
    x[0].endswith('.log'),          # 排除日志文件
    x[0].endswith('.png'),          # 排除图片文件
    x[0].endswith('.jpg'),
    x[0].endswith('.jpeg'),
    x[0].endswith('.gif'),
    x[0].endswith('.pdf'),
    'test' in x[0].lower(),         # 排除测试文件
    '__pycache__' in x[0],          # 排除缓存文件
    '.git' in x[0],                 # 排除git文件
    'node_modules' in x[0],         # 排除node模块
])]

# PYZ配置
pyz = PYZ(a.pure, a.zipped_data, cipher=None)

# EXE配置
exe = EXE(
    pyz,
    a.scripts,
    a.binaries,
    a.zipfiles,
    a.datas,
    [],
    name='TaskSearchTool',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    upx_exclude=[],
    runtime_tmpdir=None,
    console=True,
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
    icon=None,
)

# 如果需要创建目录结构，使用COLLECT
# collect = COLLECT(
#     exe,
#     a.binaries,
#     a.zipfiles,
#     a.datas,
#     strip=False,
#     upx=True,
#     upx_exclude=[],
#     name='TaskSearchTool'
# )

if __name__ == '__main__':
    print("PyInstaller打包配置")
    print(f"主入口文件: {main_script}")
    print(f"项目根目录: {project_root}")
    print("\n要开始打包，请运行:")
    print(f"pyinstaller {__file__}")
    print("\n或者使用以下命令进行一键打包:")
    print(f"pyinstaller --onefile --console --name TaskSearchTool {main_script}")