#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
装备控制器
"""

import logging
from typing import Dict, List, Optional
from src.app.services.equipment_service import EquipmentService

logger = logging.getLogger(__name__)


class EquipmentController:
    """装备控制器"""
    
    def __init__(self):
        self.service = EquipmentService()
    
    def get_equipments(self, params: Dict) -> Dict:
        """获取装备列表"""
        try:
            # 添加调试日志
            logger.info(f"收到筛选参数: {params}")
            
            # 从请求参数中提取筛选条件
            page = int(params.get('page', 1))
            page_size = int(params.get('page_size', 10))
            year = params.get('year')
            month = params.get('month')
            
            # 验证分页参数
            if page < 1:
                page = 1
            if page_size < 1 or page_size > 100:
                page_size = 10
            
            # 类型转换
            if year:
                year = int(year)
            if month:
                month = int(month)
            
            # 筛选条件
            level_min = params.get('level_min')
            level_max = params.get('level_max')
            price_min = params.get('price_min')
            price_max = params.get('price_max')
            
            if level_min is not None:
                level_min = int(level_min)
            if level_max is not None:
                level_max = int(level_max)
            if price_min is not None:
                price_min = float(price_min)
            if price_max is not None:
                price_max = float(price_max)
            
            # 多选参数处理 - 修复处理逻辑
            kindid = params.get('kindid')
            if kindid:
                if isinstance(kindid, str):
                    # 如果是字符串，按逗号分割
                    kindid = [item.strip() for item in kindid.split(',') if item.strip()]
                elif isinstance(kindid, list):
                    # 如果已经是列表，直接使用
                    kindid = [str(item) for item in kindid if item]
                else:
                    kindid = None
            
            # 宠物装备类型参数（多选）
            equip_type = params.get('equip_type')
            if equip_type:
                if isinstance(equip_type, str):
                    # 如果是字符串，按逗号分割
                    equip_type = [item.strip() for item in equip_type.split(',') if item.strip()]
                elif isinstance(equip_type, list):
                    # 如果已经是列表，直接使用
                    equip_type = [int(item) for item in equip_type if item]
                else:
                    equip_type = None
            
            equip_special_skills = params.get('equip_special_skills')
            if equip_special_skills:
                if isinstance(equip_special_skills, str):
                    # 如果是字符串，按逗号分割
                    equip_special_skills = [item.strip() for item in equip_special_skills.split(',') if item.strip()]
                elif isinstance(equip_special_skills, list):
                    # 如果已经是列表，直接使用
                    equip_special_skills = [str(item) for item in equip_special_skills if item]
                else:
                    equip_special_skills = None
            
            equip_special_effect = params.get('equip_special_effect')
            if equip_special_effect:
                if isinstance(equip_special_effect, str):
                    # 如果是字符串，按逗号分割
                    equip_special_effect = [item.strip() for item in equip_special_effect.split(',') if item.strip()]
                elif isinstance(equip_special_effect, list):
                    # 如果已经是列表，直接使用
                    equip_special_effect = [str(item) for item in equip_special_effect if item]
                else:
                    equip_special_effect = None
            
            # 其他筛选条件
            suit_effect = params.get('suit_effect')
            suit_added_status = params.get('suit_added_status')
            suit_transform_skills = params.get('suit_transform_skills')
            suit_transform_charms = params.get('suit_transform_charms')
            gem_value = params.get('gem_value')
            
            gem_level = params.get('gem_level')
            if gem_level is not None:
                gem_level = int(gem_level)
            
            # 排序参数
            sort_by = params.get('sort_by', 'price')
            sort_order = params.get('sort_order', 'asc')
            
            # 添加处理后的参数日志
            filter_params = {
                'level_min': level_min,
                'level_max': level_max,
                'price_min': price_min,
                'price_max': price_max,
                'kindid': kindid,
                'equip_type': equip_type,
                'equip_special_skills': equip_special_skills,
                'equip_special_effect': equip_special_effect,
                'suit_effect': suit_effect,
                'suit_added_status': suit_added_status,
                'suit_transform_skills': suit_transform_skills,
                'suit_transform_charms': suit_transform_charms,
                'gem_value': gem_value,
                'gem_level': gem_level,
                'sort_by': sort_by,
                'sort_order': sort_order
            }
            logger.info(f"处理后的筛选参数: {filter_params}")
            
            # 调用服务层
            result = self.service.get_equipments(
                page=page,
                page_size=page_size,
                year=year,
                month=month,
                level_min=level_min,
                level_max=level_max,
                price_min=price_min,
                price_max=price_max,
                kindid=kindid,
                equip_type=equip_type,
                equip_special_skills=equip_special_skills,
                equip_special_effect=equip_special_effect,
                suit_effect=suit_effect,
                suit_added_status=suit_added_status,
                suit_transform_skills=suit_transform_skills,
                suit_transform_charms=suit_transform_charms,
                gem_value=gem_value,
                gem_level=gem_level,
                sort_by=sort_by,
                sort_order=sort_order
            )
            
            return result
            
        except ValueError as e:
            logger.error(f"参数格式错误: {e}")
            return {"error": f"参数格式错误: {str(e)}"}
        except Exception as e:
            logger.error(f"获取装备列表时出错: {e}")
            return {"error": f"获取装备列表时出错: {str(e)}"}
    
    def get_equipment_details(self, equip_sn: str, year: Optional[int] = None, month: Optional[int] = None) -> Optional[Dict]:
        """获取装备详情"""
        try:
            if not equip_sn:
                return {"error": "装备序列号不能为空"}
            
            result = self.service.get_equipment_details(equip_sn, year, month)
            
            if result is None:
                return {"error": "未找到指定的装备"}
            
            return result
            
        except Exception as e:
            logger.error(f"获取装备详情时出错: {e}")
            return {"error": f"获取装备详情时出错: {str(e)}"}
    
    def find_equipment_anchors(self, equipment_data: Dict, params: Dict) -> Dict:
        """寻找装备市场锚点"""
        try:
            # 提取参数
            similarity_threshold = float(params.get('similarity_threshold', 0.7))
            max_anchors = int(params.get('max_anchors', 30))
            
            # 参数验证
            if not 0.0 <= similarity_threshold <= 1.0:
                return {"error": "相似度阈值必须在0.0-1.0之间"}
            
            if not 1 <= max_anchors <= 100:
                return {"error": "最大锚点数量必须在1-100之间"}
            
            # 调用服务层
            result = self.service.find_equipment_anchors(
                equipment_data=equipment_data,
                similarity_threshold=similarity_threshold,
                max_anchors=max_anchors
            )
            
            return result
            
        except ValueError as e:
            logger.error(f"参数格式错误: {e}")
            return {"error": f"参数格式错误: {str(e)}"}
        except Exception as e:
            logger.error(f"查找装备锚点时出错: {e}")
            return {"error": f"查找装备锚点时出错: {str(e)}"}
    
    def get_equipment_valuation(self, equipment_data: Dict, strategy: str = 'fair_value', 
                               similarity_threshold: float = 0.7, max_anchors: int = 30) -> Dict:
        """获取装备估价"""
        try:
            # 验证策略参数
            valid_strategies = ['fair_value', 'competitive', 'premium']
            if strategy not in valid_strategies:
                return {"error": f"无效的估价策略: {strategy}，有效策略: {', '.join(valid_strategies)}"}
            
            # 验证相似度阈值
            if not 0.0 <= similarity_threshold <= 1.0:
                return {"error": "相似度阈值必须在0.0-1.0之间"}
            
            # 验证最大锚点数量
            if not 1 <= max_anchors <= 100:
                return {"error": "最大锚点数量必须在1-100之间"}
            
            # 调用服务层
            result = self.service.get_equipment_valuation(
                equipment_data=equipment_data,
                strategy=strategy,
                similarity_threshold=similarity_threshold,
                max_anchors=max_anchors
            )
            
            return result
            
        except Exception as e:
            logger.error(f"获取装备估价时出错: {e}")
            return {"error": f"获取装备估价时出错: {str(e)}"} 