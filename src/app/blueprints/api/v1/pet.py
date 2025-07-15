#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
宠物API蓝图
"""

from flask import Blueprint, request, jsonify
from src.app.controllers.pet_controller import PetController
from src.app.utils.response import success_response, error_response

pet_bp = Blueprint('pet', __name__)
controller = PetController()


@pet_bp.route('/', methods=['GET'])
def get_pets():
    """获取宠物列表"""
    try:
        # 获取查询参数
        params = {
            'page': request.args.get('page', 1),
            'page_size': request.args.get('page_size', 10),
            'year': request.args.get('year'),
            'month': request.args.get('month'),
            'level_min': request.args.get('level_min'),
            'level_max': request.args.get('level_max'),
            'price_min': request.args.get('price_min'),
            'price_max': request.args.get('price_max'),
            # 多选参数
            'pet_lx': request.args.get('pet_lx'),
            'pet_texing': request.args.getlist('pet_texing') or request.args.getlist('pet_texing[]') or None,
            'pet_skills': request.args.getlist('pet_skills') or request.args.getlist('pet_skills[]') or None,
            'pet_growth': request.args.get('pet_growth'),
            'pet_skill_count': request.args.get('pet_skill_count'),
            'sort_by': request.args.get('sort_by', 'price'),
            'sort_order': request.args.get('sort_order', 'asc')
        }
        
        # 过滤掉空值
        params = {k: v for k, v in params.items() if v is not None and v != '' and v != []}
        
        result = controller.get_pets(params)
        
        if "error" in result:
            return error_response(result["error"])
        
        return success_response(data=result, message="获取宠物列表成功")
        
    except Exception as e:
        return error_response(f"获取宠物列表失败: {str(e)}")


@pet_bp.route('/<string:pet_sn>', methods=['GET'])
def get_pet_details(pet_sn):
    """获取宠物详情"""
    try:
        year = request.args.get('year')
        month = request.args.get('month')
        
        if year:
            year = int(year)
        if month:
            month = int(month)
        
        result = controller.get_pet_details(pet_sn, year, month)
        
        if result is None:
            return error_response("未找到指定的宠物", code=404, http_code=404)
        
        if "error" in result:
            return error_response(result["error"])
        
        return success_response(data=result, message="获取宠物详情成功")
        
    except ValueError:
        return error_response("年月参数格式错误")
    except Exception as e:
        return error_response(f"获取宠物详情失败: {str(e)}")


@pet_bp.route('/anchors', methods=['POST'])
def find_pet_anchors():
    """寻找宠物市场锚点"""
    try:
        data = request.get_json()
        if not data:
            return error_response("请提供宠物数据")
        
        pet_data = data.get('pet_data')
        if not pet_data:
            return error_response("请提供宠物数据")
        
        params = {
            'similarity_threshold': data.get('similarity_threshold', 0.7),
            'max_anchors': data.get('max_anchors', 30)
        }
        
        result = controller.find_pet_anchors(pet_data, params)
        
        if "error" in result:
            return error_response(result["error"])
        
        return success_response(data=result, message="查找宠物锚点成功")
        
    except Exception as e:
        return error_response(f"查找宠物锚点失败: {str(e)}")


@pet_bp.route('/valuation', methods=['POST'])
def get_pet_valuation():
    """获取宠物估价"""
    try:
        data = request.get_json()
        if not data:
            return error_response("请提供宠物数据")
        
        pet_data = data.get('pet_data')
        if not pet_data:
            return error_response("请提供宠物数据")
        
        strategy = data.get('strategy', 'fair_value')
        similarity_threshold = data.get('similarity_threshold', 0.7)
        max_anchors = data.get('max_anchors', 30)
        
        result = controller.get_pet_valuation(
            pet_data, 
            strategy, 
            similarity_threshold, 
            max_anchors
        )
        
        if "error" in result:
            return error_response(result["error"])
        
        return success_response(data=result, message="获取宠物估价成功")
        
    except Exception as e:
        return error_response(f"获取宠物估价失败: {str(e)}")


@pet_bp.route('/anchors/<string:pet_sn>', methods=['GET'])
def find_anchors_by_sn(pet_sn):
    """通过宠物SN查找锚点（便捷接口）"""
    try:
        if not pet_sn:
            return error_response("宠物序列号不能为空")
        
        # 获取宠物详情
        year = request.args.get('year')
        month = request.args.get('month')
        
        if year:
            year = int(year)
        if month:
            month = int(month)
        
        pet_data = controller.get_pet_details(pet_sn, year, month)
        
        if not pet_data or "error" in pet_data:
            return error_response("未找到指定的宠物")
        
        # 获取锚点查找参数
        params = {
            'similarity_threshold': request.args.get('similarity_threshold', 0.7, type=float),
            'max_anchors': request.args.get('max_anchors', 30, type=int)
        }
        
        result = controller.find_pet_anchors(pet_data, params)
        
        if "error" in result:
            return error_response(result["error"])
        
        return success_response(data=result, message="查找宠物锚点成功")
        
    except ValueError:
        return error_response("参数格式错误")
    except Exception as e:
        return error_response(f"查找宠物锚点失败: {str(e)}")


@pet_bp.route('/valuation/<string:pet_sn>', methods=['GET'])
def get_valuation_by_sn(pet_sn):
    """通过宠物SN获取估价（便捷接口）"""
    try:
        if not pet_sn:
            return error_response("宠物序列号不能为空")
        
        # 获取宠物详情
        year = request.args.get('year')
        month = request.args.get('month')
        
        if year:
            year = int(year)
        if month:
            month = int(month)
        
        pet_data = controller.get_pet_details(pet_sn, year, month)
        
        if not pet_data or "error" in pet_data:
            return error_response("未找到指定的宠物")
        
        # 获取估价策略
        strategy = request.args.get('strategy', 'fair_value')
        
        result = controller.get_pet_valuation(pet_data, strategy)
        
        if "error" in result:
            return error_response(result["error"])
        
        return success_response(data=result, message="获取宠物估价成功")
        
    except ValueError:
        return error_response("参数格式错误")
    except Exception as e:
        return error_response(f"获取宠物估价失败: {str(e)}")


@pet_bp.route('/health', methods=['GET'])
def health_check():
    """健康检查"""
    return success_response(data={"status": "ok"}, message="宠物服务正常运行") 