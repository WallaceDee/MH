#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
系统控制器
"""

import os
import logging
import platform
from datetime import datetime
from src.utils.project_path import get_project_root, get_data_path, get_output_path

logger = logging.getLogger(__name__)


class SystemController:
    """系统控制器"""
    
    def __init__(self):
        self.project_root = get_project_root()
    
    def get_system_info(self):
        """获取系统信息"""
        return {
            "system": platform.system(),
            "python_version": platform.python_version(),
            "project_root": self.project_root,
            "current_time": datetime.now().isoformat()
        }
    
    def list_output_files(self):
        """递归列出output目录及所有子目录下的输出文件"""
        output_dir = get_output_path()
        files = []
        for root, dirs, filenames in os.walk(output_dir):
            for file in filenames:
                if file.endswith(('.log', '.json', '.xlsx', '.csv')):
                    file_path = os.path.join(root, file)
                    files.append({
                        "name": file,
                        "path": file_path,
                        "size": os.path.getsize(file_path),
                        "modified": datetime.fromtimestamp(os.path.getmtime(file_path)).isoformat(),
                        "directory": os.path.relpath(root, self.project_root)
                    })
        return files
    
    def get_file_path(self, filename):
        """获取文件路径"""
        # 在data和output目录中查找文件
        data_path = os.path.join(get_data_path(), filename)
        if os.path.exists(data_path):
            return data_path
            
        output_path = os.path.join(get_output_path(), filename)
        if os.path.exists(output_path):
            return output_path
        
        raise FileNotFoundError(f"文件 {filename} 不存在") 