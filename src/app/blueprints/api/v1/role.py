#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
角色API蓝图
"""

from flask import Blueprint, request, jsonify, send_file
from ....controllers.role_controller import roleController
from ....utils.response import success_response, error_response
import os

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
            'school_skill_num': request.args.get('school_skill_num'),
            'school_skill_level': request.args.get('school_skill_level'),
            # 角色修炼参数
            'expt_gongji': request.args.get('expt_gongji'),
            'expt_fangyu': request.args.get('expt_fangyu'),
            'expt_fashu': request.args.get('expt_fashu'),
            'expt_kangfa': request.args.get('expt_kangfa'),
            'expt_total': request.args.get('expt_total'),
            'max_expt_gongji': request.args.get('max_expt_gongji'),
            'max_expt_fangyu': request.args.get('max_expt_fangyu'),
            'max_expt_fashu': request.args.get('max_expt_fashu'),
            'max_expt_kangfa': request.args.get('max_expt_kangfa'),
            'expt_lieshu': request.args.get('expt_lieshu'),
            # 召唤兽修炼参数
            'bb_expt_gongji': request.args.get('bb_expt_gongji'),
            'bb_expt_fangyu': request.args.get('bb_expt_fangyu'),
            'bb_expt_fashu': request.args.get('bb_expt_fashu'),
            'bb_expt_kangfa': request.args.get('bb_expt_kangfa'),
            'bb_expt_total': request.args.get('bb_expt_total'),
            'skill_drive_pet': request.args.get('skill_drive_pet'),
            # 其他参数
            'equip_num': request.args.get('equip_num'),
            'pet_num': request.args.get('pet_num'),
            'pet_num_level': request.args.get('pet_num_level'),
            # 排序参数
            'sort_by': request.args.get('sort_by'),
            'sort_order': request.args.get('sort_order')
        }
        
        result = controller.get_roles(params)
        
        if "error" in result:
            return error_response(result["error"])
        
        return success_response(data=result, message="获取角色列表成功")
        
    except Exception as e:
        return error_response(f"获取角色列表失败: {str(e)}")


@role_bp.route('/feature/<string:year>/<string:month>/<string:eid>', methods=['GET'])
def get_role_feature(year, month, eid):
    """获取角色特征"""
    try:
        if year:
            year = int(year)
        if month:
            month = int(month)
        
        result = controller.get_role_feature(eid, year, month)
        
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
        
        result = controller.get_role_details(eid, year, month)
        
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