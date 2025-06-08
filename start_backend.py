#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
CBG爬虫后端启动脚本
"""

import os
import sys

# 添加src目录到Python路径
project_root = os.path.dirname(os.path.abspath(__file__))
src_path = os.path.join(project_root, 'src')
sys.path.insert(0, src_path)

if __name__ == "__main__":
    from web_interface import main
    main() 