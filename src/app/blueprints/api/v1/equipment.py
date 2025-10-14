#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
装备API蓝图
"""

import logging
from flask import Blueprint, request, jsonify
from ....controllers.equipment_controller import EquipmentController
from ....utils.response import success_response, error_response

logger = logging.getLogger(__name__)

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
            'start_date': request.args.get('start_date'),
            'end_date': request.args.get('end_date'),
            'level_min': request.args.get('level_min'),
            'level_max': request.args.get('level_max'),
            'price_min': request.args.get('price_min'),
            'price_max': request.args.get('price_max'),
            # 修复多选参数 - 使用getlist获取数组参数
            'equip_sn': request.args.get('equip_sn'),
            'kindid': request.args.getlist('kindid') or request.args.getlist('kindid[]') or None,
            'equip_type': request.args.getlist('equip_type') or request.args.getlist('equip_type[]') or None,  # 召唤兽装备类型（多选）
            'equip_special_skills': request.args.getlist('equip_special_skills') or request.args.getlist('equip_special_skills[]') or None,
            'equip_special_effect': request.args.getlist('equip_special_effect') or request.args.getlist('equip_special_effect[]') or None,
            'suit_effect': request.args.get('suit_effect'),
            'suit_added_status': request.args.get('suit_added_status'),
            'suit_transform_skills': request.args.get('suit_transform_skills'),
            'suit_transform_charms': request.args.get('suit_transform_charms'),
            'gem_value': request.args.get('gem_value'),
            'gem_level': request.args.get('gem_level'),
            'equip_sn_list': request.args.getlist('equip_sn_list[]') or request.args.getlist('equip_sn_list') or None,
            'sort_by': request.args.get('sort_by', ''),
            'sort_order': request.args.get('sort_order', '')
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
        result = controller.get_equipment_details(equip_sn)
        
        if result is None:
            return error_response("未找到指定的装备", code=404, http_code=404)
        
        if "error" in result:
            return error_response(result["error"])
        
        return success_response(data=result, message="获取装备详情成功")
        
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
            # 估价失败时，返回400状态码，但将完整结果放在data字段中
            return error_response(result["error"], code=400, http_code=400, data=result)
        
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
        equipment_data = controller.get_equipment_details(equip_sn)
        
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
        equipment_data = controller.get_equipment_details(equip_sn)
        
        if not equipment_data or "error" in equipment_data:
            return error_response("未找到指定的装备")
        
        # 获取估价策略
        strategy = request.args.get('strategy', 'fair_value')
        
        result = controller.get_equipment_valuation(equipment_data, strategy)
        
        if "error" in result:
            # 估价失败时，返回400状态码，但将完整结果放在data字段中
            return error_response(result["error"], code=400, http_code=400, data=result)
        
        return success_response(data=result, message="获取装备估价成功")
        
    except ValueError:
        return error_response("参数格式错误")
    except Exception as e:
        return error_response(f"获取装备估价失败: {str(e)}")


@equipment_bp.route('/extract-features', methods=['POST'])
def extract_equipment_features():
    """提取装备特征"""
    try:
        data = request.get_json()
        if not data:
            return error_response("请提供装备数据")
        
        equipment_data = data.get('equipment_data')
        if not equipment_data:
            return error_response("请提供装备数据")
        
        data_type = data.get('data_type', 'equipment')  # 'equipment' 或 'pet'
        
        result = controller.extract_features(equipment_data, data_type)
        
        if "error" in result:
            return error_response(result["error"])
        
        return success_response(data=result, message="特征提取成功")
        
    except Exception as e:
        return error_response(f"特征提取失败: {str(e)}")


@equipment_bp.route('/extract-features-batch', methods=['POST'])
def extract_equipment_features_batch():
    """批量提取装备特征"""
    try:
        data = request.get_json()
        if not data:
            return error_response("请提供装备数据")
        
        equipment_list = data.get('equipment_list')
        if not equipment_list or not isinstance(equipment_list, list):
            return error_response("请提供有效的装备列表")
        
        data_type = data.get('data_type', 'equipment')  # 'equipment' 或 'pet'
        
        result = controller.extract_features_batch(equipment_list, data_type)
        
        if "error" in result:
            return error_response(result["error"])
        
        return success_response(data=result, message="批量特征提取成功")
        
    except Exception as e:
        return error_response(f"批量特征提取失败: {str(e)}")


@equipment_bp.route('/extractor-info/<int:kindid>', methods=['GET'])
def get_extractor_info(kindid):
    """获取指定kindid的提取器信息"""
    try:
        result = controller.get_extractor_info(kindid)
        return success_response(data=result, message="获取提取器信息成功")
    except Exception as e:
        return error_response(f"获取提取器信息失败: {str(e)}")


@equipment_bp.route('/supported-kindids', methods=['GET'])
def get_supported_kindids():
    """获取支持的kindid列表"""
    try:
        result = controller.get_supported_kindids()
        return success_response(data=result, message="获取支持的kindid列表成功")
    except Exception as e:
        return error_response(f"获取支持的kindid列表失败: {str(e)}")


@equipment_bp.route('/health', methods=['GET'])
def health_check():
    """健康检查"""
    return success_response(data={"status": "ok"}, message="装备服务正常运行")


@equipment_bp.route('/batch-valuation', methods=['POST'])
def batch_equipment_valuation():
    """批量装备估价"""
    try:
        data = request.get_json()
        if not data:
            return error_response("请提供装备数据")
        
        equipment_list = data.get('equipment_list')
        if not equipment_list or not isinstance(equipment_list, list):
            return error_response("请提供有效的装备列表")
        
        # 获取估价参数
        strategy = data.get('strategy', 'fair_value')
        similarity_threshold = float(data.get('similarity_threshold', 0.8))
        max_anchors = int(data.get('max_anchors', 30))
        
        # 获取角色eid参数（可选）
        eid = data.get('eid')
        
        # 调用批量估价
        result = controller.batch_equipment_valuation(
            equipment_list=equipment_list,
            strategy=strategy,
            similarity_threshold=similarity_threshold,
            max_anchors=max_anchors
        )
        
        if "error" in result:
            # 批量估价失败时，返回400状态码，但将完整结果放在data字段中
            return error_response(result["error"], code=400, http_code=400, data=result)
        
        # 如果有eid参数，更新角色的装备估价价格
        if eid:
            try:
                # 计算装备总价值
                total_equip_price = 0
                for item in result.get('results', []):
                    total_equip_price += item.get('estimated_price', 0)
                
                # 更新角色数据库中的装备估价价格
                from ....services.role_service import RoleService
                role_service = RoleService()
                success = role_service.update_role_equip_price(eid, total_equip_price)
                result["equip_price"] = total_equip_price
                if success:
                    logger.info(f"成功更新角色 {eid} 的装备估价价格: {total_equip_price}分")
                else:
                    logger.warning(f"更新角色 {eid} 的装备估价价格失败")
                    
            except Exception as e:
                logger.error(f"更新角色装备估价价格时出错: {e}")
                # 不影响估价结果的返回，只记录错误日志
        
        return success_response(data=result, message="批量装备估价完成")
        
    except ValueError:
        return error_response("参数格式错误")
    except Exception as e:
        return error_response(f"批量装备估价失败: {str(e)}")


@equipment_bp.route('/<string:equip_sn>', methods=['DELETE'])
def delete_equipment(equip_sn):
    """删除指定装备"""
    try:
        if not equip_sn:
            return error_response("装备序列号不能为空")
        
        result = controller.delete_equipment(equip_sn)
        
        if "error" in result:
            return error_response(result["error"])
        
        if result.get("deleted", False):
            return success_response(data=result, message="装备删除成功")
        else:
            return error_response(result.get("error", "删除失败"))
        
    except Exception as e:
        return error_response(f"删除装备失败: {str(e)}") 

@equipment_bp.route('/lingshi-config', methods=['GET'])
def get_lingshi_config():
    """获取灵饰数据"""
    try:
        result = controller.get_lingshi_config()
        
        if "error" in result:
            return error_response(result["error"])
        
        return success_response(data=result["data"], message="获取灵饰数据成功")
        
    except Exception as e:
        return error_response(f"获取灵饰数据失败: {str(e)}") 

@equipment_bp.route('/weapon-config', methods=['GET'])
def get_weapon_config():
    """获取武器数据"""
    try:
        result = controller.get_weapon_config()
        if "error" in result:
            return error_response(result["error"])
        
        return success_response(data=result["data"], message="获取武器数据成功")
    except Exception as e:
        return error_response(f"获取武器数据失败: {str(e)}")

@equipment_bp.route('/mark-abnormal', methods=['POST'])
def mark_equipment_as_abnormal():
    """标记装备为异常"""
    try:
        data = request.get_json()
        if not data:
            return error_response("请提供装备数据")
        
        equipment_data = data.get('equipment_data')
        if not equipment_data:
            return error_response("请提供装备数据")
        
        reason = data.get('reason', '标记异常')
        notes = data.get('notes')
        
        result = controller.mark_equipment_as_abnormal(equipment_data, reason, notes)
        
        if "error" in result:
            return error_response(result["error"])
        
        return success_response(data=result, message=result.get("message", "装备标记异常成功"))
        
    except Exception as e:
        return error_response(f"标记装备异常失败: {str(e)}")

@equipment_bp.route('/abnormal', methods=['GET'])
def get_abnormal_equipment_list():
    """获取异常装备列表"""
    try:
        params = {
            'page': request.args.get('page', 1, type=int),
            'page_size': request.args.get('page_size', 20, type=int),
            'status': request.args.get('status')
        }
        
        result = controller.get_abnormal_equipment_list(params)
        
        if "error" in result:
            return error_response(result["error"])
        
        return success_response(data=result, message="获取异常装备列表成功")
        
    except Exception as e:
        return error_response(f"获取异常装备列表失败: {str(e)}")

@equipment_bp.route('/abnormal/<string:equip_sn>', methods=['PUT'])
def update_abnormal_equipment_status(equip_sn):
    """更新异常装备状态"""
    try:
        if not equip_sn:
            return error_response("装备序列号不能为空")
        
        data = request.get_json()
        if not data:
            return error_response("请提供更新数据")
        
        status = data.get('status')
        notes = data.get('notes')
        
        if not status:
            return error_response("状态不能为空")
        
        result = controller.update_abnormal_equipment_status(equip_sn, status, notes)
        
        if "error" in result:
            return error_response(result["error"])
        
        return success_response(data=result, message=result.get("message", "异常装备状态更新成功"))
        
    except Exception as e:
        return error_response(f"更新异常装备状态失败: {str(e)}")

@equipment_bp.route('/abnormal/<string:equip_sn>', methods=['DELETE'])
def delete_abnormal_equipment(equip_sn):
    """删除异常装备记录"""
    try:
        if not equip_sn:
            return error_response("装备序列号不能为空")
        
        result = controller.delete_abnormal_equipment(equip_sn)
        
        if "error" in result:
            return error_response(result["error"])
        
        return success_response(data=result, message=result.get("message", "异常装备记录删除成功"))
        
    except Exception as e:
        return error_response(f"删除异常装备记录失败: {str(e)}") 

@equipment_bp.route('/pet-equip-config', methods=['GET'])
def get_pet_equip_config():
    """获取召唤兽装备数据"""
    try:
        result = controller.get_pet_equip_config()
        return success_response(data=result["data"], message="获取召唤兽装备数据成功")
    except Exception as e:
        return error_response(f"获取召唤兽装备数据失败: {str(e)}")
    
@equipment_bp.route('/equip-config', methods=['GET'])
def get_equip_config():
    """获取装备数据"""
    try:
        result = controller.get_equip_config()
        return success_response(data=result["data"], message="获取装备数据成功")
    except Exception as e:
        return error_response(f"获取装备数据失败: {str(e)}")


@equipment_bp.route('/cache/refresh-lingshi', methods=['POST'])
def refresh_lingshi_cache():
    """强制刷新灵饰数据缓存"""
    try:
        result = controller.refresh_lingshi_cache()
        
        if "error" in result:
            return error_response(result["error"])
        
        return success_response(data=result, message="灵饰缓存刷新成功")
        
    except Exception as e:
        return error_response(f"刷新灵饰缓存失败: {str(e)}")

@equipment_bp.route('/cache/refresh-memory', methods=['POST'])
def refresh_memory_cache():
    """刷新内存缓存"""
    try:
        result = controller.refresh_memory_cache()
        
        if "error" in result:
            return error_response(result["error"])
        
        return success_response(data=result, message="内存缓存刷新成功")
        
    except Exception as e:
        return error_response(f"内存缓存刷新失败: {str(e)}")