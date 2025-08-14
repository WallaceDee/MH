#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
项目路径工具模块
统一管理项目根目录的获取方式
"""

import os
from typing import Optional

# 缓存项目根目录，避免重复计算
_PROJECT_ROOT = None

def get_project_root() -> str:
    """
    获取项目根目录的绝对路径
    
    Returns:
        str: 项目根目录的绝对路径
    """
    global _PROJECT_ROOT
    
    if _PROJECT_ROOT is not None:
        return _PROJECT_ROOT
    
    # 从当前文件位置开始，向上查找包含特定标识文件的目录
    current_dir = os.path.dirname(os.path.abspath(__file__))
    
    # 向上查找，直到找到项目根目录（包含README.md或requirements.txt等标识文件）
    while current_dir != os.path.dirname(current_dir):  # 避免到达文件系统根目录
        # 检查是否包含项目标识文件
        if any(os.path.exists(os.path.join(current_dir, identifier)) 
               for identifier in ['README.md', 'requirements.txt', 'start_dev.py', 'start_prod.py']):
            _PROJECT_ROOT = current_dir
            return _PROJECT_ROOT
        
        current_dir = os.path.dirname(current_dir)
    
    # 如果没找到标识文件，使用当前文件向上3级作为备选方案
    fallback_root = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
    _PROJECT_ROOT = fallback_root
    return _PROJECT_ROOT

def get_config_path() -> str:
    """
    获取config目录的绝对路径
    
    Returns:
        str: config目录的绝对路径
    """
    return os.path.join(get_project_root(), 'config')

def get_logs_path() -> str:
    """
    获取logs目录的绝对路径
    
    Returns:
        str: logs目录的绝对路径
    """
    return os.path.join(get_project_root(), 'logs')

def get_data_path() -> str:
    """
    获取data目录的绝对路径
    
    Returns:
        str: data目录的绝对路径
    """
    return os.path.join(get_project_root(), 'data')

def get_web_path() -> str:
    """
    获取web目录的绝对路径
    
    Returns:
        str: web目录的绝对路径
    """
    return os.path.join(get_project_root(), 'web')

def get_tests_path() -> str:
    """
    获取tests目录的绝对路径
    
    Returns:
        str: tests目录的绝对路径
    """
    return os.path.join(get_project_root(), 'tests')

def get_output_path() -> str:
    """
    获取output目录的绝对路径
    
    Returns:
        str: output目录的绝对路径
    """
    return os.path.join(get_project_root(), 'output')

def get_src_path() -> str:
    """
    获取src目录的绝对路径
    
    Returns:
        str: src目录的绝对路径
    """
    return os.path.join(get_project_root(), 'src')

def get_relative_path(relative_path: str) -> str:
    """
    获取相对于项目根目录的绝对路径
    
    Args:
        relative_path: 相对于项目根目录的路径
        
    Returns:
        str: 绝对路径
    """
    return os.path.join(get_project_root(), relative_path)

def ensure_dir_exists(path: str) -> str:
    """
    确保目录存在，如果不存在则创建
    
    Args:
        path: 目录路径
        
    Returns:
        str: 目录路径
    """
    os.makedirs(path, exist_ok=True)
    return path

# 为了向后兼容，提供别名
project_root = get_project_root 