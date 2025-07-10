#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
宠物控制器
"""

import logging
from typing import Dict, List, Optional
from app.services.pet_service import PetService

logger = logging.getLogger(__name__)


class PetController:
    """宠物控制器"""
    
    def __init__(self):
        self.service = PetService()
    
    def get_pets(self, params: Dict) -> Dict:
        """获取宠物列表"""
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
            
            # 多选参数处理
            pet_type = params.get('pet_type')
            if pet_type:
                if isinstance(pet_type, str):
                    # 如果是字符串，按逗号分割
                    pet_type = [item.strip() for item in pet_type.split(',') if item.strip()]
                elif isinstance(pet_type, list):
                    # 如果已经是列表，直接使用
                    pet_type = [str(item) for item in pet_type if item]
                else:
                    pet_type = None
            
            pet_skills = params.get('pet_skills')
            if pet_skills:
                if isinstance(pet_skills, str):
                    # 如果是字符串，按逗号分割
                    pet_skills = [item.strip() for item in pet_skills.split(',') if item.strip()]
                elif isinstance(pet_skills, list):
                    # 如果已经是列表，直接使用
                    pet_skills = [str(item) for item in pet_skills if item]
                else:
                    pet_skills = None
            
            pet_special_effect = params.get('pet_special_effect')
            if pet_special_effect:
                if isinstance(pet_special_effect, str):
                    # 如果是字符串，按逗号分割
                    pet_special_effect = [item.strip() for item in pet_special_effect.split(',') if item.strip()]
                elif isinstance(pet_special_effect, list):
                    # 如果已经是列表，直接使用
                    pet_special_effect = [str(item) for item in pet_special_effect if item]
                else:
                    pet_special_effect = None
            
            pet_quality = params.get('pet_quality')
            if pet_quality:
                if isinstance(pet_quality, str):
                    # 如果是字符串，按逗号分割
                    pet_quality = [item.strip() for item in pet_quality.split(',') if item.strip()]
                elif isinstance(pet_quality, list):
                    # 如果已经是列表，直接使用
                    pet_quality = [str(item) for item in pet_quality if item]
                else:
                    pet_quality = None
            
            # 其他筛选条件
            pet_growth = params.get('pet_growth')
            pet_aptitude = params.get('pet_aptitude')
            
            pet_skill_count = params.get('pet_skill_count')
            if pet_skill_count is not None:
                pet_skill_count = int(pet_skill_count)
            
            # 排序参数
            sort_by = params.get('sort_by', 'price')
            sort_order = params.get('sort_order', 'asc')
            
            # 添加处理后的参数日志
            filter_params = {
                'level_min': level_min,
                'level_max': level_max,
                'price_min': price_min,
                'price_max': price_max,
                'pet_type': pet_type,
                'pet_skills': pet_skills,
                'pet_special_effect': pet_special_effect,
                'pet_quality': pet_quality,
                'pet_growth': pet_growth,
                'pet_aptitude': pet_aptitude,
                'pet_skill_count': pet_skill_count,
                'sort_by': sort_by,
                'sort_order': sort_order
            }
            logger.info(f"处理后的筛选参数: {filter_params}")
            
            # 调用服务层
            result = self.service.get_pets(
                page=page,
                page_size=page_size,
                year=year,
                month=month,
                level_min=level_min,
                level_max=level_max,
                price_min=price_min,
                price_max=price_max,
                pet_type=pet_type,
                pet_skills=pet_skills,
                pet_special_effect=pet_special_effect,
                pet_quality=pet_quality,
                pet_growth=pet_growth,
                pet_aptitude=pet_aptitude,
                pet_skill_count=pet_skill_count,
                sort_by=sort_by,
                sort_order=sort_order
            )
            
            return result
            
        except ValueError as e:
            logger.error(f"参数格式错误: {e}")
            return {"error": f"参数格式错误: {str(e)}"}
        except Exception as e:
            logger.error(f"获取宠物列表时出错: {e}")
            return {"error": f"获取宠物列表时出错: {str(e)}"}
    
    def get_pet_details(self, pet_sn: str, year: Optional[int] = None, month: Optional[int] = None) -> Optional[Dict]:
        """获取宠物详情"""
        try:
            if not pet_sn:
                return {"error": "宠物序列号不能为空"}
            
            result = self.service.get_pet_details(pet_sn, year, month)
            
            if result is None:
                return {"error": "未找到指定的宠物"}
            
            return result
            
        except Exception as e:
            logger.error(f"获取宠物详情时出错: {e}")
            return {"error": f"获取宠物详情时出错: {str(e)}"}
    
    def find_pet_anchors(self, pet_data: Dict, params: Dict) -> Dict:
        """寻找宠物市场锚点"""
        try:
            # 提取参数
            similarity_threshold = float(params.get('similarity_threshold', 0.7))
            max_anchors = int(params.get('max_anchors', 30))
            
            # 参数验证
            if not 0.0 <= similarity_threshold <= 1.0:
                return {"error": "相似度阈值必须在0.0到1.0之间"}
            
            if max_anchors < 1 or max_anchors > 100:
                return {"error": "最大锚点数量必须在1到100之间"}
            
            # 调用服务层
            result = self.service.find_pet_anchors(pet_data, similarity_threshold, max_anchors)
            
            return result
            
        except ValueError as e:
            logger.error(f"参数格式错误: {e}")
            return {"error": f"参数格式错误: {str(e)}"}
        except Exception as e:
            logger.error(f"查找宠物锚点时出错: {e}")
            return {"error": f"查找宠物锚点时出错: {str(e)}"}
    
    def get_pet_valuation(self, pet_data: Dict, strategy: str = 'fair_value', 
                         similarity_threshold: float = 0.7, max_anchors: int = 30) -> Dict:
        """获取宠物估价"""
        try:
            # 参数验证
            if not pet_data:
                return {"error": "宠物数据不能为空"}
            
            if strategy not in ['fair_value', 'market_price', 'weighted_average']:
                return {"error": "不支持的估价策略"}
            
            if not 0.0 <= similarity_threshold <= 1.0:
                return {"error": "相似度阈值必须在0.0到1.0之间"}
            
            if max_anchors < 1 or max_anchors > 100:
                return {"error": "最大锚点数量必须在1到100之间"}
            
            # 调用服务层
            result = self.service.get_pet_valuation(pet_data, strategy, similarity_threshold, max_anchors)
            
            return result
            
        except Exception as e:
            logger.error(f"获取宠物估价时出错: {e}")
            return {"error": f"获取宠物估价时出错: {str(e)}"} 