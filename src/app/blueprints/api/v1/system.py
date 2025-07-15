#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
系统API蓝图
"""

from flask import Blueprint, send_file, request
from src.app.controllers.system_controller import SystemController
from src.app.utils.response import success_response, error_response

system_bp = Blueprint('system', __name__)
controller = SystemController()


@system_bp.route('/info', methods=['GET'])
def get_system_info():
    """获取系统信息"""
    try:
        info = controller.get_system_info()
        return success_response(data=info)
    except Exception as e:
        return error_response(f"获取系统信息失败: {str(e)}")


@system_bp.route('/files', methods=['GET'])
def list_files():
    """列出输出文件"""
    try:
        files = controller.list_output_files()
        return success_response(data=files)
    except Exception as e:
        return error_response(f"获取文件列表失败: {str(e)}")


@system_bp.route('/files/<filename>/download', methods=['GET'])
def download_file(filename):
    """下载文件"""
    try:
        file_path = controller.get_file_path(filename)
        return send_file(file_path, as_attachment=True)
    except FileNotFoundError:
        return error_response("文件不存在", code=404, http_code=404)
    except Exception as e:
        return error_response(f"下载失败: {str(e)}", http_code=500) 