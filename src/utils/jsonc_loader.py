import json
import os
import logging
from typing import Dict, Any


def load_jsonc(file_path: str, encoding: str = 'utf-8') -> Dict[str, Any]:
    """
    加载JSONC文件（带注释的JSON）
    
    Args:
        file_path (str): JSONC文件路径，可以是绝对路径或相对路径
        encoding (str): 文件编码，默认为'utf-8'
        
    Returns:
        Dict[str, Any]: 解析后的JSON数据
        
    Raises:
        FileNotFoundError: 文件不存在
        json.JSONDecodeError: JSON格式错误
        Exception: 其他读取错误
    """
    logger = logging.getLogger(__name__)
    
    try:
        # 检查文件是否存在
        if not os.path.exists(file_path):
            raise FileNotFoundError(f"JSONC文件不存在: {file_path}")
            
        # 读取文件内容
        with open(file_path, 'r', encoding=encoding) as f:
            content = f.read()
            
        # 简单处理JSONC注释（移除//注释）
        lines = content.split('\n')
        cleaned_lines = []
        for line in lines:
            # 移除行内注释
            if '//' in line:
                line = line[:line.index('//')]
            cleaned_lines.append(line)
        
        cleaned_content = '\n'.join(cleaned_lines)
        
        # 解析JSON
        return json.loads(cleaned_content)
        
    except FileNotFoundError:
        logger.error(f"JSONC文件不存在: {file_path}")
        raise
    except json.JSONDecodeError as e:
        logger.error(f"JSONC文件格式错误: {file_path}, 错误: {e}")
        raise
    except Exception as e:
        logger.error(f"加载JSONC文件失败: {file_path}, 错误: {e}")
        raise


def load_jsonc_relative_to_file(base_file: str, relative_path: str, encoding: str = 'utf-8') -> Dict[str, Any]:
    """
    基于某个文件的位置，加载相对路径的JSONC文件
    
    Args:
        base_file (str): 基准文件的路径（通常是__file__）
        relative_path (str): 相对于基准文件目录的路径
        encoding (str): 文件编码，默认为'utf-8'
        
    Returns:
        Dict[str, Any]: 解析后的JSON数据
    """
    # 构建绝对路径
    base_dir = os.path.dirname(base_file)
    absolute_path = os.path.join(base_dir, relative_path)
    
    return load_jsonc(absolute_path, encoding)


def load_jsonc_from_config_dir(config_file_name: str, base_file: str, encoding: str = 'utf-8') -> Dict[str, Any]:
    """
    从config目录加载JSONC文件（常用的配置文件加载方式）
    
    Args:
        config_file_name (str): 配置文件名（例如：'rule_setting.jsonc'）
        base_file (str): 基准文件的路径（通常是__file__）
        encoding (str): 文件编码，默认为'utf-8'
        
    Returns:
        Dict[str, Any]: 解析后的JSON数据
    """
    relative_path = os.path.join('config', config_file_name)
    return load_jsonc_relative_to_file(base_file, relative_path, encoding) 