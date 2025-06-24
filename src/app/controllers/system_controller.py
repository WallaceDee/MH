#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
系统控制器
"""

import os
import logging
import platform
from datetime import datetime

logger = logging.getLogger(__name__)


class SystemController:
    """系统控制器"""
    
    def __init__(self):
        self.project_root = os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
    
    def get_system_info(self):
        """获取系统信息"""
        return {
            "system": platform.system(),
            "python_version": platform.python_version(),
            "project_root": self.project_root,
            "current_time": datetime.now().isoformat()
        }
    
    def list_output_files(self):
        """列出输出文件"""
        data_dir = os.path.join(self.project_root, "data")
        output_dir = os.path.join(self.project_root, "output")
        
        files = []
        
        # 检查data目录
        if os.path.exists(data_dir):
            for file in os.listdir(data_dir):
                if file.endswith(('.db', '.json', '.xlsx', '.csv')):
                    file_path = os.path.join(data_dir, file)
                    files.append({
                        "name": file,
                        "path": file_path,
                        "size": os.path.getsize(file_path),
                        "modified": datetime.fromtimestamp(os.path.getmtime(file_path)).isoformat(),
                        "directory": "data"
                    })
        
        # 检查output目录
        if os.path.exists(output_dir):
            for file in os.listdir(output_dir):
                if file.endswith(('.db', '.json', '.xlsx', '.csv')):
                    file_path = os.path.join(output_dir, file)
                    files.append({
                        "name": file,
                        "path": file_path,
                        "size": os.path.getsize(file_path),
                        "modified": datetime.fromtimestamp(os.path.getmtime(file_path)).isoformat(),
                        "directory": "output"
                    })
        
        return files
    
    def get_file_path(self, filename):
        """获取文件路径"""
        # 在data和output目录中查找文件
        for directory in ["data", "output"]:
            file_path = os.path.join(self.project_root, directory, filename)
            if os.path.exists(file_path):
                return file_path
        
        raise FileNotFoundError(f"文件 {filename} 不存在") 