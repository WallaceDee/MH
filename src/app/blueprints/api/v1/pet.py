#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
宠物API蓝图
"""

import logging
from flask import Blueprint, request, jsonify
from ....controllers.pet_controller import PetController
from ....utils.response import success_response, error_response
from src.app.utils.auth import require_auth
from .admin import require_admin
logger = logging.getLogger(__name__)

pet_bp = Blueprint('pet', __name__)
controller = PetController()


@pet_bp.route('/', methods=['GET'])
@require_auth
def get_pets():
    """获取宠物列表"""
    try:
        # 获取查询参数
        params = {
            'page': request.args.get('page', 1),
            'page_size': request.args.get('page_size', 10),
            'start_date': request.args.get('start_date'),
            'end_date': request.args.get('end_date'),
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
            'equip_list_amount_warning': request.args.get('equip_list_amount_warning'),
            'equip_sn': request.args.get('equip_sn'),
            'equip_sn_list': request.args.getlist('equip_sn_list[]') or request.args.getlist('equip_sn_list') or None,
            'warning_rate': request.args.get('warning_rate'),
            'sort_by': request.args.get('sort_by', 'update_time'),
            'sort_order': request.args.get('sort_order', 'desc')
        }
        
        # 过滤掉空值
        params = {k: v for k, v in params.items() if v is not None and v != '' and v != []}
        
        result = controller.get_pets(params)
        
        if "error" in result:
            return error_response(result["error"])
        
        return success_response(data=result, message="获取宠物列表成功")
        
    except Exception as e:
        return error_response(f"获取宠物列表失败: {str(e)}")


@pet_bp.route('/<string:equip_sn>', methods=['GET'])
@require_auth
def get_pet_by_equip_sn(equip_sn):
    """通过equip_sn查找召唤兽详情"""
    try:
        result = controller.get_pet_by_equip_sn(equip_sn)
        
        if result is None:
            return error_response("未找到指定的召唤兽", code=404, http_code=404)
        
        if "error" in result:
            return error_response(result["error"])
        
        return success_response(data=result, message="获取召唤兽详情成功")
        
    except Exception as e:
        return error_response(f"获取召唤兽详情失败: {str(e)}")


@pet_bp.route('/anchors', methods=['POST'])
@require_auth
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
@require_auth
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
            # 估价失败时，返回400状态码，但将完整结果放在data字段中
            return error_response(result["error"], code=400, http_code=400, data=result)
        
        return success_response(data=result, message="获取宠物估价成功")
        
    except Exception as e:
        return error_response(f"获取宠物估价失败: {str(e)}")


@pet_bp.route('/unvalued-count', methods=['GET'])
@require_admin
def get_unvalued_pets_count():
    """获取当前年月携带装备但未估价的召唤兽数量"""
    try:
        result = controller.get_unvalued_pets_count()
        
        if "error" in result:
            return error_response(result["error"])
        
        return success_response(data=result, message="获取未估价召唤兽数量成功")
        
    except Exception as e:
        return error_response(f"获取未估价召唤兽数量失败: {str(e)}")


@pet_bp.route('/batch-update-unvalued', methods=['POST'])
@require_admin
def batch_update_unvalued_pets_equipment():
    """批量更新未估价召唤兽的装备价格"""
    try:
        result = controller.batch_update_unvalued_pets_equipment()
        
        if "error" in result:
            return error_response(result["error"])
        
        return success_response(data=result, message="批量更新未估价召唤兽装备成功")
        
    except Exception as e:
        return error_response(f"批量更新未估价召唤兽装备失败: {str(e)}")


@pet_bp.route('/task-status/<string:task_id>', methods=['GET'])
@require_admin
def get_task_status(task_id):
    """获取任务状态"""
    try:
        result = controller.get_task_status(task_id)
        
        if "error" in result:
            return error_response(result["error"])
        
        return success_response(data=result, message="获取任务状态成功")
        
    except Exception as e:
        return error_response(f"获取任务状态失败: {str(e)}")


@pet_bp.route('/stop-task/<string:task_id>', methods=['POST'])
@require_admin
def stop_task(task_id):
    """停止任务"""
    try:
        result = controller.stop_task(task_id)
        
        if "error" in result:
            return error_response(result["error"])
        
        return success_response(data=result, message="停止任务成功")
        
    except Exception as e:
        return error_response(f"停止任务失败: {str(e)}")


@pet_bp.route('/active-tasks', methods=['GET'])
@require_admin
def get_active_tasks():
    """获取活跃任务列表"""
    try:
        result = controller.get_active_tasks()
        
        if "error" in result:
            return error_response(result["error"])
        
        return success_response(data=result, message="获取活跃任务成功")
        
    except Exception as e:
        return error_response(f"获取活跃任务失败: {str(e)}")


@pet_bp.route('/update-equipments-price', methods=['POST'])
@require_admin
def update_pet_equipments_price():
    """更新召唤兽装备价格"""
    try:
        data = request.get_json()
        if not data:
            return error_response("请提供召唤兽数据")
        
        # 获取召唤兽信息
        equip_sn = data.get('equip_sn')
        year = data.get('year')
        month = data.get('month')
        
        if not equip_sn:
            return error_response("请提供召唤兽序列号")
        
        if not year or not month:
            return error_response("请提供年月参数")
        
        # 首先获取召唤兽详情
        pet_details = controller.get_pet_details(equip_sn, int(year), int(month))
        
        if not pet_details or "error" in pet_details:
            return error_response(f"获取召唤兽详情失败: {pet_details.get('error', '未知错误')}")
        
        # 从召唤兽详情中提取装备列表
        equip_list_json = pet_details.get('equip_list', '[]')
        if isinstance(equip_list_json, str):
            import json
            equip_list = json.loads(equip_list_json)
        else:
            equip_list = equip_list_json
        
        if not equip_list:
            return success_response(data={
                "results": [],
                "total_estimated_price": 0,
                "total_estimated_price_yuan": 0,
                "equipment_count": 0,
                "successful_count": 0,
                "strategy": data.get('strategy', 'fair_value'),
                "similarity_threshold": float(data.get('similarity_threshold', 0.8)),
                "max_anchors": int(data.get('max_anchors', 30)),
                "pet_info": {
                    "equip_sn": equip_sn,
                    "pet_name": pet_details.get('equip_name', ''),
                    "level": pet_details.get('level', 0),
                    "year": int(year),
                    "month": int(month)
                }
            }, message="该召唤兽没有携带装备")
        
        # 构建装备数据列表
        equipment_list = []
        for equip_info in equip_list:
            if not equip_info or not equip_info.get('desc'):
                continue
            
            # 构建装备数据
            equipment_data = {
                'kindid': 29,  # 宠物装备的kindid
                'desc': equip_info.get('desc', '')
            }
            
            equipment_list.append(equipment_data)
        
        # 只取前三个
        equipment_list = equipment_list[:3]
        
        if not equipment_list:
            return success_response(data={
                "results": [],
                "total_estimated_price": 0,
                "total_estimated_price_yuan": 0,
                "equipment_count": 0,
                "successful_count": 0,
                "strategy": data.get('strategy', 'fair_value'),
                "similarity_threshold": float(data.get('similarity_threshold', 0.8)),
                "max_anchors": int(data.get('max_anchors', 30)),
                "pet_info": {
                    "equip_sn": equip_sn,
                    "pet_name": pet_details.get('equip_name', ''),
                    "level": pet_details.get('level', 0),
                    "year": int(year),
                    "month": int(month)
                }
            }, message="该召唤兽没有有效的装备可以估价")
        
        # 获取估价参数
        strategy = data.get('strategy', 'fair_value')
        similarity_threshold = float(data.get('similarity_threshold', 0.8))
        max_anchors = int(data.get('max_anchors', 30))
        
        # 调用装备控制器的批量估价方法
        from ....controllers.equipment_controller import EquipmentController
        equipment_controller = EquipmentController()
        
        result = equipment_controller.batch_equipment_valuation(
            equipment_list=equipment_list,
            strategy=strategy,
            similarity_threshold=similarity_threshold,
            max_anchors=max_anchors
        )

        if "error" in result:
            return error_response(result["error"])

        # 计算装备总价值
        equip_list_amount = 0
        for item in result.get('results', []):
            equip_list_amount += item.get('estimated_price', 0)

        # 更新召唤兽装备价格
        controller.update_pet_equipments_price(equip_sn, equip_list_amount, int(year), int(month))

        # 添加召唤兽信息到结果中
        result["pet_info"] = {
            "equip_sn": equip_sn,
            "pet_name": pet_details.get('equip_name', ''),
            "level": pet_details.get('level', 0),
            "year": int(year),
            "month": int(month)
        }
        
        return success_response(data=result, message="召唤兽装备价格更新完成")
        
    except ValueError:
        return error_response("参数格式错误")
    except Exception as e:
        return error_response(f"更新召唤兽装备价格失败: {str(e)}")


@pet_bp.route('/batch-valuation', methods=['POST'])
@require_auth
def batch_pet_valuation():
    """批量宠物估价"""
    try:
        data = request.get_json()
        if not data:
            return error_response("请提供宠物数据")
        
        pet_list = data.get('pet_list')
        if not pet_list or not isinstance(pet_list, list):
            return error_response("请提供有效的宠物列表")
        
        # 获取估价参数
        strategy = data.get('strategy', 'fair_value')
        similarity_threshold = float(data.get('similarity_threshold', 0.8))
        max_anchors = int(data.get('max_anchors', 30))
        
        # 获取角色eid参数（可选）
        eid = data.get('eid')
        
        # 调用批量估价
        result = controller.batch_pet_valuation(
            pet_list=pet_list,
            strategy=strategy,
            similarity_threshold=similarity_threshold,
            max_anchors=max_anchors
        )
        
        if "error" in result:
            return error_response(result["error"])
        
        # 如果有eid参数，更新角色的宠物估价价格
        if eid:
            try:
                # 计算宠物总价值（包括宠物本身和装备）
                total_pet_price = 0
                for item in result.get('results', []):
                    total_pet_price += item.get('estimated_price', 0)
                    total_pet_price += item.get('equip_estimated_price', 0)
                
                # 更新角色数据库中的宠物估价价格
                from ....services.role_service import RoleService
                role_service = RoleService()
                success = role_service.update_role_pet_price(eid, total_pet_price)
                result["pet_price"] = total_pet_price
                if success:
                    logger.info(f"成功更新角色 {eid} 的宠物估价价格: {total_pet_price}分")
                else:
                    logger.warning(f"更新角色 {eid} 的宠物估价价格失败")
                    
            except Exception as e:
                logger.error(f"更新角色宠物估价价格时出错: {e}")
                # 不影响估价结果的返回，只记录错误日志
        
        return success_response(data=result, message="批量宠物估价完成")
        
    except ValueError:
        return error_response("参数格式错误")
    except Exception as e:
        return error_response(f"批量宠物估价失败: {str(e)}")


@pet_bp.route('/<string:pet_sn>', methods=['DELETE'])
@require_admin
def delete_pet(pet_sn):
    """删除宠物"""
    try:
        result = controller.delete_pet(pet_sn)
        
        if "error" in result:
            return error_response(result["error"])
        
        return success_response(message="宠物删除成功")
        
    except Exception as e:
        return error_response(f"删除宠物失败: {str(e)}")


@pet_bp.route('/stats', methods=['GET'])
def get_pet_stats():
    """获取召唤兽统计数据"""
    try:
        from datetime import datetime
        import os
        import glob
        
        # 获取召唤兽数据总数
        total_count = 0
        try:
            # 尝试从数据库获取总数
            result = controller.get_pets({
                'page': 1,
                'page_size': 1,
                'count_only': True
            })
            if result and 'total' in result:
                total_count = result['total']
        except Exception as e:
            logger.warning(f"从数据库获取召唤兽总数失败: {e}")
        
        # 获取最后更新时间
        last_update = "未知"
        try:
            # 查找最新的召唤兽数据文件
            pet_files = glob.glob('data/**/cbg_pets_*.db', recursive=True)
            if pet_files:
                latest_file = max(pet_files, key=os.path.getmtime)
                last_update = datetime.fromtimestamp(os.path.getmtime(latest_file)).strftime('%Y-%m-%d %H:%M:%S')
        except Exception as e:
            logger.warning(f"获取召唤兽最后更新时间失败: {e}")
        
        stats_data = {
            "total": total_count,
            "lastUpdate": last_update
        }
        
        return success_response(data=stats_data, message="获取召唤兽统计成功")
        
    except Exception as e:
        logger.error(f"获取召唤兽统计失败: {e}")
        return error_response(f"获取召唤兽统计失败: {str(e)}") 