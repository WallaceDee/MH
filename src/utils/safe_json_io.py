#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
安全的JSON文件读写工具
解决编码问题
"""

import json
import os
import logging
from typing import Any, Dict, List

logger = logging.getLogger(__name__)


def safe_write_json(data: Any, file_path: str, indent: int = 2) -> bool:
    """
    安全地写入JSON文件
    
    Args:
        data: 要写入的数据
        file_path: 文件路径
        indent: 缩进级别
        
    Returns:
        bool: 写入是否成功
    """
    try:
        # 确保目录存在
        directory = os.path.dirname(file_path)
        if directory and not os.path.exists(directory):
            os.makedirs(directory)
        
        # 使用明确的UTF-8编码写入
        with open(file_path, 'w', encoding='utf-8', newline='') as f:
            json.dump(data, f, ensure_ascii=False, indent=indent, separators=(',', ': '))
        
        logger.debug(f"成功写入JSON文件: {file_path}")
        return True
        
    except Exception as e:
        logger.error(f"写入JSON文件失败 {file_path}: {e}")
        return False


def safe_read_json(file_path: str) -> Any:
    """
    安全地读取JSON文件，支持多种编码
    
    Args:
        file_path: 文件路径
        
    Returns:
        Any: 解析后的JSON数据，失败时返回None
    """
    if not os.path.exists(file_path):
        logger.warning(f"JSON文件不存在: {file_path}")
        return None
    
    # 尝试多种编码方式
    encodings = ['utf-8', 'utf-8-sig', 'gbk', 'gb2312', 'cp1252', 'latin1']
    
    for encoding in encodings:
        try:
            with open(file_path, 'r', encoding=encoding) as f:
                content = f.read()
            
            # 解析JSON
            data = json.loads(content)
            logger.debug(f"使用编码 {encoding} 成功读取JSON文件: {file_path}")
            return data
            
        except UnicodeDecodeError:
            logger.debug(f"编码 {encoding} 无法读取文件: {file_path}")
            continue
        except json.JSONDecodeError as e:
            logger.error(f"JSON格式错误 {file_path} (编码 {encoding}): {e}")
            # JSON格式错误时不继续尝试其他编码
            break
        except Exception as e:
            logger.debug(f"读取文件失败 {file_path} (编码 {encoding}): {e}")
            continue
    
    # 如果所有编码都失败，尝试使用二进制模式读取并忽略错误
    try:
        logger.warning(f"尝试使用二进制模式读取文件: {file_path}")
        with open(file_path, 'rb') as f:
            raw_data = f.read()
        
        # 尝试UTF-8解码，忽略错误字符
        try:
            content = raw_data.decode('utf-8', errors='ignore')
            data = json.loads(content)
            logger.warning(f"使用UTF-8编码（忽略错误字符）成功读取: {file_path}")
            return data
        except json.JSONDecodeError:
            # 尝试Latin1编码
            content = raw_data.decode('latin1')
            data = json.loads(content)
            logger.warning(f"使用Latin1编码成功读取: {file_path}")
            return data
            
    except Exception as e:
        logger.error(f"所有读取方式都失败 {file_path}: {e}")
        
        # 最后的调试信息
        try:
            with open(file_path, 'rb') as f:
                raw_data = f.read()
            logger.error(f"文件大小: {len(raw_data)} 字节")
            logger.error(f"文件前100字节: {raw_data[:100]}")
        except:
            pass
    
    return None


def safe_json_loads(content: str) -> Any:
    """
    安全地解析JSON字符串
    
    Args:
        content: JSON字符串
        
    Returns:
        Any: 解析后的数据，失败时返回None
    """
    try:
        return json.loads(content)
    except json.JSONDecodeError as e:
        logger.error(f"JSON字符串格式错误: {e}")
        logger.error(f"内容前500字符: {content[:500]}")
        return None
    except Exception as e:
        logger.error(f"解析JSON字符串失败: {e}")
        return None


def safe_json_dumps(data: Any, indent: int = 2) -> str:
    """
    安全地序列化为JSON字符串
    
    Args:
        data: 要序列化的数据
        indent: 缩进级别
        
    Returns:
        str: JSON字符串，失败时返回空字符串
    """
    try:
        return json.dumps(data, ensure_ascii=False, indent=indent, separators=(',', ': '))
    except Exception as e:
        logger.error(f"序列化JSON失败: {e}")
        return ""


def validate_json_file(file_path: str) -> bool:
    """
    验证JSON文件是否有效
    
    Args:
        file_path: 文件路径
        
    Returns:
        bool: 文件是否有效
    """
    data = safe_read_json(file_path)
    return data is not None


def repair_json_file(file_path: str, backup: bool = True) -> bool:
    """
    尝试修复损坏的JSON文件
    
    Args:
        file_path: 文件路径
        backup: 是否创建备份
        
    Returns:
        bool: 修复是否成功
    """
    if not os.path.exists(file_path):
        logger.error(f"文件不存在: {file_path}")
        return False
    
    try:
        # 创建备份
        if backup:
            backup_path = f"{file_path}.backup"
            import shutil
            shutil.copy2(file_path, backup_path)
            logger.info(f"已创建备份: {backup_path}")
        
        # 尝试读取并重新写入
        data = safe_read_json(file_path)
        if data is not None:
            success = safe_write_json(data, file_path)
            if success:
                logger.info(f"JSON文件修复成功: {file_path}")
                return True
        
        logger.error(f"无法修复JSON文件: {file_path}")
        return False
        
    except Exception as e:
        logger.error(f"修复JSON文件失败 {file_path}: {e}")
        return False 