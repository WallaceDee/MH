#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
角色API蓝图
"""

from flask import Blueprint, request, jsonify, send_file
from ....controllers.character_controller import CharacterController
from ....utils.response import success_response, error_response
import os

character_bp = Blueprint('character', __name__)
controller = CharacterController()


@character_bp.route('/', methods=['GET'])
def get_characters():
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
        
        result = controller.get_characters(params)
        
        if "error" in result:
            return error_response(result["error"])
        
        return success_response(data=result, message="获取角色列表成功")
        
    except Exception as e:
        return error_response(f"获取角色列表失败: {str(e)}")


@character_bp.route('/<string:equip_id>', methods=['GET'])
def get_character_details(equip_id):
    """获取角色详情"""
    try:
        year = request.args.get('year')
        month = request.args.get('month')
        
        if year:
            year = int(year)
        if month:
            month = int(month)
        
        result = controller.get_character_details(equip_id, year, month)
        
        if result is None:
            return error_response("未找到指定的角色", code=404, http_code=404)
        
        if "error" in result:
            return error_response(result["error"])
        
        return success_response(data=result, message="获取角色详情成功")
        
    except ValueError:
        return error_response("年月参数格式错误")
    except Exception as e:
        return error_response(f"获取角色详情失败: {str(e)}")


@character_bp.route('/export/json', methods=['POST', 'GET'])
def export_characters_json():
    """导出角色数据为JSON"""
    try:
        # 支持GET和POST请求
        if request.method == 'POST':
            data = request.json or {}
            params = data
        else:
            params = dict(request.args)
        
        result = controller.export_characters_json(params)
        
        if "error" in result:
            return error_response(result["error"])
        
        file_path = result.get("file_path")
        if file_path and os.path.exists(file_path):
            # 获取文件名
            filename = os.path.basename(file_path)
            
            # 发送文件并自动删除
            return send_file(
                file_path,
                as_attachment=True,
                download_name=filename,
                mimetype='application/json'
            )
        else:
            return error_response("导出文件未找到")
        
    except Exception as e:
        return error_response(f"导出角色JSON失败: {str(e)}")


@character_bp.route('/<string:equip_id>/export/json', methods=['GET'])
def export_single_character_json(equip_id):
    """导出单个角色数据为JSON"""
    try:
        year = request.args.get('year')
        month = request.args.get('month')
        
        if year:
            year = int(year)
        if month:
            month = int(month)
        
        result = controller.export_single_character_json(equip_id, year, month)
        
        if "error" in result:
            return error_response(result["error"])
        
        file_path = result.get("file_path")
        if file_path and os.path.exists(file_path):
            # 获取文件名
            filename = os.path.basename(file_path)
            
            # 发送文件并自动删除
            return send_file(
                file_path,
                as_attachment=True,
                download_name=filename,
                mimetype='application/json'
            )
        else:
            return error_response("导出文件未找到")
        
    except ValueError:
        return error_response("参数格式错误")
    except Exception as e:
        return error_response(f"导出单个角色JSON失败: {str(e)}")


@character_bp.route('/health', methods=['GET'])
def health_check():
    """健康检查"""
    return success_response(data={"status": "healthy"}, message="角色API服务正常运行") 