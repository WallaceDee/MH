#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
日志配置工具
"""

import logging
import os
from datetime import datetime


def setup_logging(app):
    """配置应用日志"""
    
    # 创建日志目录
    from src.utils.project_path import get_logs_path
    log_dir = get_logs_path()
    if not os.path.exists(log_dir):
        os.makedirs(log_dir)
    
    # 配置日志格式
    formatter = logging.Formatter(
        '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )
    
    # 文件处理器
    log_file = os.path.join(log_dir, f'app_{datetime.now().strftime("%Y%m%d")}.log')
    file_handler = logging.FileHandler(log_file, encoding='utf-8')
    file_handler.setFormatter(formatter)
    file_handler.setLevel(logging.INFO)
    
    # 控制台处理器
    console_handler = logging.StreamHandler()
    console_handler.setFormatter(formatter)
    console_handler.setLevel(logging.DEBUG)
    
    # 获取根日志器
    root_logger = logging.getLogger()
    
    # 检查是否已经配置过日志处理器
    # 使用一个标记来避免重复配置
    if not hasattr(root_logger, '_cbg_configured'):
        # 清除现有的处理器，确保干净的配置
        root_logger.handlers.clear()
        
        # 配置根日志器（只配置一次）
        root_logger.setLevel(logging.INFO)
        root_logger.addHandler(file_handler)
        root_logger.addHandler(console_handler)
        
        # 标记已配置
        root_logger._cbg_configured = True
        
        print(f"日志配置完成 - 文件: {log_file}")
        print(f"根日志器处理器数量: {len(root_logger.handlers)}")
    
    # 配置Flask应用日志器（总是设置，确保正确配置）
    app.logger.setLevel(logging.INFO)
    # 清除Flask应用日志器的处理器，避免重复
    app.logger.handlers.clear()
    # 启用传播，让消息传递到根日志器
    app.logger.propagate = True 