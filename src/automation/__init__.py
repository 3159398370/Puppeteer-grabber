#!/usr/bin/env python3.8
# -*- coding: utf-8 -*-
"""
自动化模块
包含基于Selenium的浏览器自动化功能
"""

from .yuanbao_client import YuanBaoClient, DualBrowserAutomation, create_dual_browser_automation

__all__ = [
    'YuanBaoClient',
    'DualBrowserAutomation', 
    'create_dual_browser_automation'
]