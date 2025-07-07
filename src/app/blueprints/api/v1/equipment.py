#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
装备API蓝图
"""

from flask import Blueprint, request, jsonify
from app.controllers.equipment_controller import EquipmentController
from app.utils.response import success_response, error_response

equipment_bp = Blueprint('equipment', __name__)
controller = EquipmentController()


@equipment_bp.route('/', methods=['GET'])
def get_equipments():
    """获取装备列表"""
    try:
        # 获取查询参数 - 修复多选参数的获取逻辑
        params = {
            'page': request.args.get('page', 1),
            'page_size': request.args.get('page_size', 10),
            'year': request.args.get('year'),
            'month': request.args.get('month'),
            'level_min': request.args.get('level_min'),
            'level_max': request.args.get('level_max'),
            'price_min': request.args.get('price_min'),
            'price_max': request.args.get('price_max'),
            # 修复多选参数 - 使用getlist获取数组参数
            'kindid': request.args.getlist('kindid') or request.args.getlist('kindid[]') or None,
            'equip_type': request.args.getlist('equip_type') or request.args.getlist('equip_type[]') or None,  # 宠物装备类型（多选）
            'equip_special_skills': request.args.getlist('equip_special_skills') or request.args.getlist('equip_special_skills[]') or None,
            'equip_special_effect': request.args.getlist('equip_special_effect') or request.args.getlist('equip_special_effect[]') or None,
            'suit_effect': request.args.get('suit_effect'),
            'suit_added_status': request.args.get('suit_added_status'),
            'suit_transform_skills': request.args.get('suit_transform_skills'),
            'suit_transform_charms': request.args.get('suit_transform_charms'),
            'gem_value': request.args.get('gem_value'),
            'gem_level': request.args.get('gem_level'),
            'sort_by': request.args.get('sort_by', 'price'),
            'sort_order': request.args.get('sort_order', 'asc')
        }
        
        # 过滤掉空值
        params = {k: v for k, v in params.items() if v is not None and v != '' and v != []}
        
        result = controller.get_equipments(params)
        
        if "error" in result:
            return error_response(result["error"])
        
        return success_response(data=result, message="获取装备列表成功")
        
    except Exception as e:
        return error_response(f"获取装备列表失败: {str(e)}")


@equipment_bp.route('/<string:equip_sn>', methods=['GET'])
def get_equipment_details(equip_sn):
    """获取装备详情"""
    try:
        year = request.args.get('year')
        month = request.args.get('month')
        
        if year:
            year = int(year)
        if month:
            month = int(month)
        
        result = controller.get_equipment_details(equip_sn, year, month)
        
        if result is None:
            return error_response("未找到指定的装备", code=404, http_code=404)
        
        if "error" in result:
            return error_response(result["error"])
        
        return success_response(data=result, message="获取装备详情成功")
        
    except ValueError:
        return error_response("年月参数格式错误")
    except Exception as e:
        return error_response(f"获取装备详情失败: {str(e)}")


@equipment_bp.route('/anchors', methods=['POST'])
def find_equipment_anchors():
    """寻找装备市场锚点"""
    try:
        data = request.get_json()
        if not data:
            return error_response("请提供装备数据")
        
        equipment_data = data.get('equipment_data')
        if not equipment_data:
            return error_response("请提供装备数据")
        
        params = {
            'similarity_threshold': data.get('similarity_threshold', 0.7),
            'max_anchors': data.get('max_anchors', 30)
        }
        
        result = controller.find_equipment_anchors(equipment_data, params)
        
        if "error" in result:
            return error_response(result["error"])
        
        return success_response(data=result, message="查找装备锚点成功")
        
    except Exception as e:
        return error_response(f"查找装备锚点失败: {str(e)}")


@equipment_bp.route('/valuation', methods=['POST'])
def get_equipment_valuation():
    """获取装备估价"""
    try:
        data = request.get_json()
        if not data:
            return error_response("请提供装备数据")
        
        equipment_data = data.get('equipment_data')
        if not equipment_data:
            return error_response("请提供装备数据")
        
        strategy = data.get('strategy', 'fair_value')
        similarity_threshold = data.get('similarity_threshold', 0.7)
        max_anchors = data.get('max_anchors', 30)
        
        result = controller.get_equipment_valuation(
            equipment_data, 
            strategy, 
            similarity_threshold, 
            max_anchors
        )
        
        if "error" in result:
            return error_response(result["error"])
        
        return success_response(data=result, message="获取装备估价成功")
        
    except Exception as e:
        return error_response(f"获取装备估价失败: {str(e)}")


@equipment_bp.route('/anchors/<string:equip_sn>', methods=['GET'])
def find_anchors_by_sn(equip_sn):
    """通过装备SN查找锚点（便捷接口）"""
    try:
        if not equip_sn:
            return error_response("装备序列号不能为空")
        
        # 获取装备详情
        year = request.args.get('year')
        month = request.args.get('month')
        
        if year:
            year = int(year)
        if month:
            month = int(month)
        
        equipment_data = controller.get_equipment_details(equip_sn, year, month)
        
        if not equipment_data or "error" in equipment_data:
            return error_response("未找到指定的装备")
        
        # 获取锚点查找参数
        params = {
            'similarity_threshold': request.args.get('similarity_threshold', 0.7, type=float),
            'max_anchors': request.args.get('max_anchors', 30, type=int)
        }
        
        result = controller.find_equipment_anchors(equipment_data, params)
        
        if "error" in result:
            return error_response(result["error"])
        
        return success_response(data=result, message="查找装备锚点成功")
        
    except ValueError:
        return error_response("参数格式错误")
    except Exception as e:
        return error_response(f"查找装备锚点失败: {str(e)}")


@equipment_bp.route('/valuation/<string:equip_sn>', methods=['GET'])
def get_valuation_by_sn(equip_sn):
    """通过装备SN获取估价（便捷接口）"""
    try:
        if not equip_sn:
            return error_response("装备序列号不能为空")
        
        # 获取装备详情
        year = request.args.get('year')
        month = request.args.get('month')
        
        if year:
            year = int(year)
        if month:
            month = int(month)
        
        equipment_data = controller.get_equipment_details(equip_sn, year, month)
        
        if not equipment_data or "error" in equipment_data:
            return error_response("未找到指定的装备")
        
        # 获取估价策略
        strategy = request.args.get('strategy', 'fair_value')
        
        result = controller.get_equipment_valuation(equipment_data, strategy)
        
        if "error" in result:
            return error_response(result["error"])
        
        return success_response(data=result, message="获取装备估价成功")
        
    except ValueError:
        return error_response("参数格式错误")
    except Exception as e:
        return error_response(f"获取装备估价失败: {str(e)}")


@equipment_bp.route('/health', methods=['GET'])
def health_check():
    """健康检查"""
    return success_response(data={"status": "ok"}, message="装备服务正常运行") 