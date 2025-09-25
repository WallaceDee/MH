#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
宠物控制器
"""

import logging
from typing import Dict, List, Optional
from ..services.pet_service import PetService

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
            start_date = params.get('start_date')
            end_date = params.get('end_date')
            
            # 验证分页参数
            if page < 1:
                page = 1
            if page_size < 1 or page_size > 100:
                page_size = 10
            
            # 日期参数验证在service层进行
            
            # 筛选条件
            level_min = params.get('level_min')
            level_max = params.get('level_max')
            price_min = params.get('price_min')
            price_max = params.get('price_max')
            pet_lx = params.get('pet_lx')
            equip_sn = params.get('equip_sn')
            warning_rate = params.get('warning_rate')
            
            # 召唤兽序列号列表参数 - 直接传递给服务层处理
            equip_sn_list = params.get('equip_sn_list')
            if level_min is not None:
                level_min = int(level_min)
            if level_max is not None:
                level_max = int(level_max)
            if price_min is not None:
                price_min = float(price_min)
            if price_max is not None:
                price_max = float(price_max)
            if warning_rate is not None:
                warning_rate = float(warning_rate)
            # 多选参数处理

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
            
            # 特性筛选（多选）
            pet_texing = params.get('pet_texing')
            if pet_texing:
                if isinstance(pet_texing, str):
                    # 如果是字符串，按逗号分割
                    pet_texing = [item.strip() for item in pet_texing.split(',') if item.strip()]
                elif isinstance(pet_texing, list):
                    # 如果已经是列表，直接使用
                    pet_texing = [str(item) for item in pet_texing if item]
                else:
                    pet_texing = None
            
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
            
            # 估价异常筛选
            equip_list_amount_warning = params.get('equip_list_amount_warning')
            logger.info(f"接收到 equip_list_amount_warning 参数: {equip_list_amount_warning}")
            if equip_list_amount_warning is not None:
                equip_list_amount_warning = int(equip_list_amount_warning)
                logger.info(f"转换后的 equip_list_amount_warning: {equip_list_amount_warning}")
            
            # 排序参数
            sort_by = params.get('sort_by', 'price')
            sort_order = params.get('sort_order', 'asc')
            
            # 添加处理后的参数日志
            filter_params = {
                'level_min': level_min,
                'level_max': level_max,
                'price_min': price_min,
                'price_max': price_max,
                'pet_skills': pet_skills,
                'pet_texing': pet_texing,
                'pet_lx': pet_lx,
                'warning_rate': warning_rate,
                'pet_special_effect': pet_special_effect,
                'pet_quality': pet_quality,
                'pet_growth': pet_growth,
                'pet_aptitude': pet_aptitude,
                'pet_skill_count': pet_skill_count,
                'equip_list_amount_warning': equip_list_amount_warning,
                'sort_by': sort_by,
                'sort_order': sort_order
            }
            logger.info(f"处理后的筛选参数: {filter_params}")
            
            # 调用服务层
            result = self.service.get_pets(
                page=page,
                page_size=page_size,
                start_date=start_date,
                end_date=end_date,
                level_min=level_min,
                level_max=level_max,
                price_min=price_min,
                price_max=price_max,
                pet_skills=pet_skills,
                pet_texing=pet_texing,
                pet_lx=pet_lx,
                pet_growth=pet_growth,
                pet_skill_count=pet_skill_count,
                equip_list_amount_warning=equip_list_amount_warning,
                warning_rate=warning_rate,
                equip_sn=equip_sn,
                equip_sn_list=equip_sn_list,
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
    
    def get_pet_details(self, pet_sn: str) -> Optional[Dict]:
        """获取宠物详情"""
        try:
            if not pet_sn:
                return {"error": "宠物序列号不能为空"}
            
            result = self.service.get_pet_details(pet_sn)
            
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
            if not pet_data:
                return {
                    "error": "宠物数据不能为空",
                    "estimated_price": 0,
                    "estimated_price_yuan": 0.0,
                    "strategy": strategy,
                    "anchor_count": 0,
                    "anchors": [],
                    "confidence": 0.0,
                    "similarity_threshold": similarity_threshold,
                    "max_anchors": max_anchors,
                    "price_range": {},
                    "equip_valuations": [],
                    "equip_estimated_price": 0,
                    "skip_reason": "",
                    "invalid_item": False
                }
            
            if strategy not in ['fair_value', 'market_price', 'weighted_average']:
                return {
                    "error": "不支持的估价策略",
                    "estimated_price": 0,
                    "estimated_price_yuan": 0.0,
                    "strategy": strategy,
                    "anchor_count": 0,
                    "anchors": [],
                    "confidence": 0.0,
                    "similarity_threshold": similarity_threshold,
                    "max_anchors": max_anchors,
                    "price_range": {},
                    "equip_valuations": [],
                    "equip_estimated_price": 0,
                    "skip_reason": "",
                    "invalid_item": False
                }
            
            if not 0.0 <= similarity_threshold <= 1.0:
                return {
                    "error": "相似度阈值必须在0.0到1.0之间",
                    "estimated_price": 0,
                    "estimated_price_yuan": 0.0,
                    "strategy": strategy,
                    "anchor_count": 0,
                    "anchors": [],
                    "confidence": 0.0,
                    "similarity_threshold": similarity_threshold,
                    "max_anchors": max_anchors,
                    "price_range": {},
                    "equip_valuations": [],
                    "equip_estimated_price": 0,
                    "skip_reason": "",
                    "invalid_item": False
                }
            
            if max_anchors < 1 or max_anchors > 100:
                return {
                    "error": "最大锚点数量必须在1到100之间",
                    "estimated_price": 0,
                    "estimated_price_yuan": 0.0,
                    "strategy": strategy,
                    "anchor_count": 0,
                    "anchors": [],
                    "confidence": 0.0,
                    "similarity_threshold": similarity_threshold,
                    "max_anchors": max_anchors,
                    "price_range": {},
                    "equip_valuations": [],
                    "equip_estimated_price": 0,
                    "skip_reason": "",
                    "invalid_item": False
                }
            
            # 调用服务层
            result = self.service.get_pet_valuation(pet_data, strategy, similarity_threshold, max_anchors)
            
            return result
            
        except Exception as e:
            logger.error(f"获取宠物估价时出错: {e}")
            return {
                "error": f"获取宠物估价时出错: {str(e)}",
                "estimated_price": 0,
                "estimated_price_yuan": 0.0,
                "strategy": strategy,
                "anchor_count": 0,
                "anchors": [],
                "confidence": 0.0,
                "similarity_threshold": similarity_threshold,
                "max_anchors": max_anchors,
                "price_range": {},
                "equip_valuations": [],
                "equip_estimated_price": 0,
                "skip_reason": "",
                "invalid_item": False
            }

    def batch_pet_valuation(self, pet_list: List[Dict], strategy: str = 'fair_value',
                           similarity_threshold: float = 0.7, max_anchors: int = 30, verbose: bool = False) -> Dict:
        """批量宠物估价"""
        try:
            logger.info(f"开始批量宠物估价，宠物数量: {len(pet_list)}，策略: {strategy}，详细日志: {verbose}")
            
            # 验证策略参数
            valid_strategies = ['fair_value', 'market_price', 'weighted_average']
            if strategy not in valid_strategies:
                return {"error": f"无效的估价策略: {strategy}，有效策略: {', '.join(valid_strategies)}"}
            
            # 验证相似度阈值
            if not 0.0 <= similarity_threshold <= 1.0:
                return {"error": "相似度阈值必须在0.0-1.0之间"}
            
            # 验证最大锚点数量
            if not 1 <= max_anchors <= 100:
                return {"error": "最大锚点数量必须在1-100之间"}
            
            # 验证宠物列表
            if not pet_list or not isinstance(pet_list, list):
                return {"error": "宠物列表不能为空且必须是列表格式"}
            
            # 调用服务层
            result = self.service.batch_pet_valuation(
                pet_list=pet_list,
                strategy=strategy,
                similarity_threshold=similarity_threshold,
                max_anchors=max_anchors,
                verbose=verbose
            )
            
            return result
            
        except Exception as e:
            logger.error(f"批量宠物估价失败: {e}")
            return {
                "error": f"批量宠物估价失败: {str(e)}",
                "results": []
            }

    def update_pet_equipments_price(self, equip_sn: str, price: float) -> Dict:
        """更新召唤兽装备价格"""
        try:
            # 修复参数传递：price作为equip_list_amount，equip_list_amount_warning设为0
            success = self.service.update_pet_equip_amount(equip_sn, int(price), 0)
            if success:
                return {"message": "更新召唤兽装备价格成功"}
            else:
                return {"error": "更新召唤兽装备价格失败"}
        except Exception as e:
            logger.error(f"更新召唤兽装备价格失败: {e}")
            return {"error": f"更新召唤兽装备价格失败: {str(e)}"}
    
    def get_unvalued_pets_count(self) -> Dict:
        """获取当前年月携带装备但未估价的召唤兽数量"""
        try:
            result = self.service.get_unvalued_pets_count()
            return result
        except Exception as e:
            logger.error(f"获取未估价召唤兽数量失败: {e}")
            return {"error": f"获取未估价召唤兽数量失败: {str(e)}"}
    
    def batch_update_unvalued_pets_equipment(self) -> Dict:
        """批量更新未估价召唤兽的装备价格"""
        try:
            result = self.service.batch_update_unvalued_pets_equipment()
            return result
        except Exception as e:
            logger.error(f"批量更新未估价召唤兽装备失败: {e}")
            return {"error": f"批量更新未估价召唤兽装备失败: {str(e)}"}
    
    def get_task_status(self, task_id: str) -> Dict:
        """获取任务状态"""
        try:
            result = self.service.get_task_status(task_id)
            if result:
                return result
            else:
                return {"error": "任务不存在"}
        except Exception as e:
            logger.error(f"获取任务状态失败: {e}")
            return {"error": f"获取任务状态失败: {str(e)}"}
    
    def get_active_tasks(self) -> Dict:
        """获取活跃任务列表"""
        try:
            result = self.service.get_active_tasks()
            return result
        except Exception as e:
            logger.error(f"获取活跃任务失败: {e}")
            return {"error": f"获取活跃任务失败: {str(e)}"}
    
    def stop_task(self, task_id: str) -> Dict:
        """停止任务"""
        try:
            result = self.service.stop_task(task_id)
            return result
        except Exception as e:
            logger.error(f"停止任务失败: {e}")
            return {"error": f"停止任务失败: {str(e)}"}

    def delete_pet(self, pet_sn: str) -> Dict:
        """删除宠物"""
        try:
            result = self.service.delete_pet(pet_sn)
            return result
        except Exception as e:
            logger.error(f"删除宠物失败: {e}")
            return {"error": f"删除宠物失败: {str(e)}"}
        
    def get_pet_by_equip_sn(self, equip_sn: str) -> Optional[Dict]:
        """通过equip_sn获取召唤兽详情"""
        try:
            result = self.service.get_pet_by_equip_sn(equip_sn)
            return result
        except Exception as e:
            logger.error(f"通过equip_sn获取召唤兽详情失败: {e}")
            return {"error": f"通过equip_sn获取召唤兽详情失败: {str(e)}"}

