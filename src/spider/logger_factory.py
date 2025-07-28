#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
爬虫日志工厂
统一所有爬虫的日志格式和文件结构
"""

import logging
import os
from datetime import datetime
from typing import Tuple


def get_spider_logger(spider_type: str, output_dir: str = None) -> Tuple[logging.Logger, str]:
    """
    获取爬虫日志器
    
    Args:
        spider_type: 爬虫类型 (role, equip, pet, proxy, test等)
        output_dir: 输出目录，如果为None则自动创建
    
    Returns:
        Tuple[logging.Logger, str]: (日志器, 日志文件路径)
    """
    # 创建输出目录
    if output_dir is None:
        current_date = datetime.now()
        year_month = current_date.strftime('%Y%m')
        output_dir = os.path.join('output', year_month)
    
    os.makedirs(output_dir, exist_ok=True)
    
    # 生成日志文件名
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    log_file = os.path.join(output_dir, f'cbg_spider_{spider_type}_{timestamp}.log')
    
    # 创建日志器
    logger = logging.getLogger(f'CBGSpider_{spider_type}_{id(logging)}')
    logger.setLevel(logging.INFO)
    
    # 清除可能存在的处理器，避免重复日志
    if logger.handlers:
        logger.handlers.clear()
    
    # 创建文件处理器
    file_handler = logging.FileHandler(log_file, encoding='utf-8', mode='w')
    file_handler.setLevel(logging.INFO)
    
    # 创建控制台处理器
    console_handler = logging.StreamHandler()
    console_handler.setLevel(logging.INFO)
    
    # 创建格式器
    formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
    file_handler.setFormatter(formatter)
    console_handler.setFormatter(formatter)
    
    # 添加处理器到日志器
    logger.addHandler(file_handler)
    logger.addHandler(console_handler)
    
    # 防止日志传播到根日志器，避免重复输出
    logger.propagate = False
    
    # 输出初始化信息
    logger.info("日志系统初始化完成")
    logger.info(f"日志文件路径: {log_file}")
    
    return logger, log_file


def log_progress(logger: logging.Logger, current_page: int, total_pages: int = None, message: str = None):
    """
    记录进度信息，带进度百分比
    """
    percent_str = ''
    if total_pages:
        try:
            percent = int((current_page-1) / total_pages * 100)
        except Exception:
            percent = 0
        percent_str = f" 进度[{percent}%]"
        if message:
            logger.info(f"正在爬取第 {current_page}/{total_pages} 页...{percent_str} {message}")
        else:
            logger.info(f"正在爬取第 {current_page}/{total_pages} 页...{percent_str}")
    else:
        if message:
            logger.info(f"正在爬取第 {current_page} 页... {message}")
        else:
            logger.info(f"正在爬取第 {current_page} 页...")


def log_page_complete(logger: logging.Logger, page_num: int, data_count: int, saved_count: int, current_page: int = None, total_pages: int = None):
    """
    记录页面完成信息，带进度百分比（如有）
    """
    percent_str = ''
    if current_page is not None and total_pages is not None:
        try:
            percent = int(current_page / total_pages * 100)
        except Exception:
            percent = 0
        percent_str = f" 进度[{percent}%]"
    logger.info(f"第 {page_num} 页完成，获取 {data_count} 条数据，保存 {saved_count} 条{percent_str}")


def log_task_complete(logger: logging.Logger, success_pages: int, total_pages: int, total_data: int, data_type: str = "数据"):
    """
    记录任务完成信息
    
    Args:
        logger: 日志器
        success_pages: 成功页数
        total_pages: 总页数
        total_data: 总数据数
        data_type: 数据类型 (角色/装备/宠物等)
    """
    logger.info(f"爬取完成！成功页数: {success_pages}/{total_pages}, 总{data_type}数: {total_data}")


def log_error(logger: logging.Logger, error_message: str):
    """
    记录错误信息
    
    Args:
        logger: 日志器
        error_message: 错误消息
    """
    logger.error(f"错误: {error_message}")


def log_warning(logger: logging.Logger, warning_message: str):
    """
    记录警告信息
    
    Args:
        logger: 日志器
        warning_message: 警告消息
    """
    logger.warning(f"警告: {warning_message}")


def log_info(logger: logging.Logger, info_message: str):
    """
    记录一般信息
    
    Args:
        logger: 日志器
        info_message: 信息消息
    """
    logger.info(info_message)


def log_total_pages(logger: logging.Logger, total_pages: int):
    """
    记录总页数信息
    
    Args:
        logger: 日志器
        total_pages: 总页数
    """
    logger.info(f"总页数: {total_pages}") 