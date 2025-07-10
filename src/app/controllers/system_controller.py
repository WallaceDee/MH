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
        """递归列出output目录及所有子目录下的输出文件"""
        output_dir = os.path.join(self.project_root, "output")
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
        for directory in ["data", "output"]:
            file_path = os.path.join(self.project_root, directory, filename)
            if os.path.exists(file_path):
                return file_path
        
        raise FileNotFoundError(f"文件 {filename} 不存在") 