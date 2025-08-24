#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
角色API蓝图
"""

from flask import Blueprint, request, jsonify, send_file
from ....controllers.role_controller import roleController
from ....utils.response import success_response, error_response
import os
import sys
import json

# 添加src目录到Python路径以便导入utils
current_dir = os.path.dirname(os.path.abspath(__file__))
src_root = os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(current_dir))))
if src_root not in sys.path:
    sys.path.append(src_root)

from utils.project_path import get_relative_path

role_bp = Blueprint('role', __name__)
controller = roleController()


@role_bp.route('/', methods=['GET'])
def get_roles():
    """获取角色列表"""
    try:
        # 获取查询参数
        params = {
            'page': request.args.get('page', 1),
            'page_size': request.args.get('page_size', 10),
            'year': request.args.get('year'),
            'month': request.args.get('month'),
            'level_min': request.args.get('level_min'),
            'level_max': request.args.get('level_max'),
            # 其他参数
            'equip_num': request.args.get('equip_num'),
            'pet_num': request.args.get('pet_num'),
            'pet_num_level': request.args.get('pet_num_level'),
            # 排序参数
            'sort_by': request.args.get('sort_by'),
            'sort_order': request.args.get('sort_order'),
            # 角色类型参数
            'role_type': request.args.get('role_type', 'normal')
        }
        
        result = controller.get_roles(params)
        
        if "error" in result:
            return error_response(result["error"])
        
        return success_response(data=result, message="获取角色列表成功")
        
    except Exception as e:
        return error_response(f"获取角色列表失败: {str(e)}")


@role_bp.route('/<string:eid>', methods=['GET'])
def get_role_detail(eid):
    """获取角色详情"""
    try:
        # 获取查询参数
        params = {
            'year': request.args.get('year'),
            'month': request.args.get('month'),
            'role_type': request.args.get('role_type', 'normal')
        }
        
        result = controller.get_role_details(eid, params.get('year'), params.get('month'), params.get('role_type'))
        
        if "error" in result:
            return error_response(result["error"])
        
        if result is None:
            return error_response("未找到指定的角色", code=404, http_code=404)
        
        return success_response(data=result, message="获取角色详情成功")
        
    except Exception as e:
        return error_response(f"获取角色详情失败: {str(e)}")


@role_bp.route('/<string:eid>', methods=['DELETE'])
def delete_role(eid):
    """删除角色"""
    try:
        # 获取查询参数
        params = {
            'year': request.args.get('year'),
            'month': request.args.get('month'),
            'role_type': request.args.get('role_type', 'normal')
        }
        
        result = controller.delete_role(eid, params)
        
        if "error" in result:
            return error_response(result["error"])
        
        return success_response(data=result, message="删除角色成功")
        
    except Exception as e:
        return error_response(f"删除角色失败: {str(e)}")


@role_bp.route('/<string:eid>/switch-type', methods=['POST'])
def switch_role_type(eid):
    """切换角色类型（数据迁移）"""
    try:
        data = request.get_json() or {}
        
        # 获取参数 - 修复参数获取逻辑
        params = {
            'year': request.args.get('year') or data.get('year'),
            'month': request.args.get('month') or data.get('month'),
            'current_role_type': data.get('role_type') or request.args.get('role_type', 'normal'),
            'target_role_type': data.get('target_role_type') or request.args.get('target_role_type')
        }
        
        if not params['target_role_type']:
            return error_response("请提供目标角色类型")
        
        if params['target_role_type'] not in ['normal', 'empty']:
            return error_response("目标角色类型必须是 normal、empty 之一")
        
        if params['current_role_type'] == params['target_role_type']:
            return error_response("当前角色类型与目标角色类型相同，无需迁移")
        
        result = controller.switch_role_type(eid, params)
        
        if "error" in result:
            return error_response(result["error"])
        
        return success_response(data=result, message="角色类型切换成功")
        
    except Exception as e:
        return error_response(f"切换角色类型失败: {str(e)}")


@role_bp.route('/feature/<string:year>/<string:month>/<string:eid>', methods=['GET'])
def get_role_feature(year, month, eid):
    """获取角色特征"""
    try:
        if year:
            year = int(year)
        if month:
            month = int(month)
        
        # 获取角色类型参数
        role_type = request.args.get('role_type', 'normal')
        
        result = controller.get_role_feature(eid, year, month, role_type)
        
        if result is None:
            return error_response("未找到指定的角色", code=404, http_code=404)
        
        if "error" in result:
            return error_response(result["error"])
        
        return success_response(data=result, message="获取角色特征成功")
        
    except ValueError:
        return error_response("年月参数格式错误")
    except Exception as e:
        return error_response(f"获取角色特征失败: {str(e)}")

@role_bp.route('/detail/<string:year>/<string:month>/<string:eid>', methods=['GET'])
def get_role_detail_by_eid(year, month, eid):
    """通过eid查找角色详情"""
    try:
        if year:
            year = int(year)
        if month:
            month = int(month)
        
        # 获取角色类型参数
        role_type = request.args.get('role_type', 'normal')
        
        result = controller.get_role_details(eid, year, month, role_type)
        
        if result is None:
            return error_response("未找到指定的角色", code=404, http_code=404)
        
        if "error" in result:
            return error_response(result["error"])
        
        return success_response(data=result, message="获取角色详情成功")
        
    except ValueError:
        return error_response("年月参数格式错误")
    except Exception as e:
        return error_response(f"获取角色详情失败: {str(e)}")


@role_bp.route('/health', methods=['GET'])
def health_check():
    """健康检查"""
    return success_response(data={"status": "healthy"}, message="角色API服务正常运行")


 