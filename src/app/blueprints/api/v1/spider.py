#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
爬虫API蓝图
"""

from flask import Blueprint, request
from app.controllers.spider_controller import SpiderController
from app.utils.response import success_response, error_response

spider_bp = Blueprint('spider', __name__)
controller = SpiderController()


@spider_bp.route('/status', methods=['GET'])
def get_status():
    """获取当前任务状态"""
    try:
        status = controller.get_task_status()
        return success_response(data=status)
    except Exception as e:
        return error_response(f"获取状态失败: {str(e)}")


@spider_bp.route('/basic/start', methods=['POST'])
def start_basic_spider():
    """启动基础爬虫"""
    try:
        data = request.json or {}
        result = controller.start_basic_spider(
            max_pages=data.get('pages', 5),
            export_excel=data.get('export_excel', True),
            export_json=data.get('export_json', True)
        )
        return success_response(data=result, message="爬虫已启动")
    except Exception as e:
        return error_response(f"启动爬虫失败: {str(e)}")


@spider_bp.route('/proxy/start', methods=['POST'])
def start_proxy_spider():
    """启动代理爬虫"""
    try:
        data = request.json or {}
        result = controller.start_proxy_spider(
            max_pages=data.get('pages', 5)
        )
        return success_response(data=result, message="代理爬虫已启动")
    except Exception as e:
        return error_response(f"启动代理爬虫失败: {str(e)}")


@spider_bp.route('/proxies/manage', methods=['POST'])
def manage_proxies():
    """管理代理IP"""
    try:
        result = controller.manage_proxies()
        return success_response(data=result, message="代理管理器已启动")
    except Exception as e:
        return error_response(f"代理管理失败: {str(e)}") 