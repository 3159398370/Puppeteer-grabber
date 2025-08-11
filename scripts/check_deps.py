#!/usr/bin/env python3.8
# -*- coding: utf-8 -*-

import pkg_resources
import sys

def check_requirements():
    """检查requirements.txt中的依赖包状态"""
    try:
        with open('requirements.txt', 'r') as f:
            requirements = f.read().strip().split('\n')
        
        installed_packages = {pkg.key: pkg.version for pkg in pkg_resources.working_set}
        
        missing = []
        outdated = []
        satisfied = []
        
        for req in requirements:
            if '==' in req:
                name, version = req.split('==')
                name_key = name.lower().replace('-', '_')
                name_lower = name.lower()
                
                if name_key in installed_packages:
                    installed_version = installed_packages[name_key]
                    if installed_version == version:
                        satisfied.append(f'{name}: {version} ✓')
                    else:
                        outdated.append(f'{name}: 已安装 {installed_version}, 需要 {version}')
                elif name_lower in installed_packages:
                    installed_version = installed_packages[name_lower]
                    if installed_version == version:
                        satisfied.append(f'{name}: {version} ✓')
                    else:
                        outdated.append(f'{name}: 已安装 {installed_version}, 需要 {version}')
                else:
                    missing.append(req)
        
        print("=== 依赖包检查结果 ===")
        print(f"Python版本: {sys.version}")
        print(f"Python路径: {sys.executable}")
        print()
        
        if satisfied:
            print("✓ 已满足的依赖:")
            for pkg in satisfied:
                print(f"  {pkg}")
            print()
        
        if missing:
            print("✗ 缺少的依赖:")
            for pkg in missing:
                print(f"  {pkg}")
            print()
        
        if outdated:
            print("⚠ 版本不匹配的依赖:")
            for pkg in outdated:
                print(f"  {pkg}")
            print()
        
        if not missing and not outdated:
            print("🎉 所有依赖都已正确安装!")
        else:
            print("💡 建议运行以下命令安装/更新依赖:")
            print(f"  {sys.executable} -m pip install -r requirements.txt")
    
    except Exception as e:
        print(f"检查依赖时出错: {e}")

if __name__ == '__main__':
    check_requirements()