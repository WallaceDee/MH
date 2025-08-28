#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
装备控制器
"""

import logging
from typing import Dict, List, Optional
from ..services.equipment_service import EquipmentService

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
            equip_sn = params.get('equip_sn')
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
                'equip_sn': equip_sn,
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
                equip_sn=equip_sn,
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

    def batch_equipment_valuation(self, equipment_list: List[Dict], strategy: str = 'fair_value',
                                 similarity_threshold: float = 0.7, max_anchors: int = 30, verbose: bool = False) -> Dict:
        """批量装备估价"""
        try:
            logger.info(f"开始批量装备估价，装备数量: {len(equipment_list)}，策略: {strategy}，详细日志: {verbose}")
            
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
            
            # 验证装备列表
            if not equipment_list or not isinstance(equipment_list, list):
                return {"error": "装备列表不能为空且必须是列表格式"}
            
            # 调用服务层
            result = self.service.batch_equipment_valuation(
                equipment_list=equipment_list,
                strategy=strategy,
                similarity_threshold=similarity_threshold,
                max_anchors=max_anchors,
                verbose=verbose
            )
            
            return result
            
        except Exception as e:
            logger.error(f"批量装备估价失败: {e}")
            return {
                "error": f"批量装备估价失败: {str(e)}",
                "results": []
            }
    
    def extract_features(self, equipment_data: Dict, data_type: str = 'equipment') -> Dict:
        """提取装备特征"""
        try:
            result = self.service.extract_features(equipment_data, data_type)
            return result
        except Exception as e:
            logger.error(f"提取装备特征时出错: {e}")
            return {"error": f"提取装备特征时出错: {str(e)}"}
    
    def extract_features_batch(self, equipment_list: List[Dict], data_type: str = 'equipment') -> Dict:
        """批量提取装备特征"""
        try:
            result = self.service.extract_features_batch(equipment_list, data_type)
            return result
        except Exception as e:
            logger.error(f"批量提取装备特征时出错: {e}")
            return {"error": f"批量提取装备特征时出错: {str(e)}"}
    
    def get_extractor_info(self, kindid: int) -> Dict:
        """获取指定kindid的提取器信息"""
        try:
            result = self.service.get_extractor_info(kindid)
            return result
        except Exception as e:
            logger.error(f"获取提取器信息时出错: {e}")
            return {"error": f"获取提取器信息时出错: {str(e)}"}
    
    def get_supported_kindids(self) -> Dict:
        """获取支持的kindid列表"""
        try:
            result = self.service.get_supported_kindids()
            return result
        except Exception as e:
            logger.error(f"获取支持的kindid列表时出错: {e}")
            return {"error": f"获取支持的kindid列表时出错: {str(e)}"}
    
    def delete_equipment(self, equip_sn: str, year: Optional[int] = None, month: Optional[int] = None) -> Dict:
        """删除指定装备"""
        try:
            if not equip_sn:
                return {"error": "装备序列号不能为空", "deleted": False}
            
            # 类型转换
            if year:
                year = int(year)
            if month:
                month = int(month)
            
            # 调用服务层
            result = self.service.delete_equipment(equip_sn, year, month)
            return result
            
        except ValueError as e:
            logger.error(f"参数格式错误: {e}")
            return {"error": f"参数格式错误: {str(e)}", "deleted": False}
        except Exception as e:
            logger.error(f"删除装备时出错: {e}")
            return {"error": f"删除装备时出错: {str(e)}", "deleted": False}
    
    def mark_equipment_as_abnormal(self, equipment_data: Dict, reason: str = "标记异常", notes: str = None) -> Dict:
        """标记装备为异常"""
        try:
            if not equipment_data:
                return {"error": "装备数据不能为空"}
            
            result = self.service.mark_equipment_as_abnormal(equipment_data, reason, notes)
            return result
            
        except Exception as e:
            logger.error(f"标记装备异常失败: {e}")
            return {"error": f"标记装备异常失败: {str(e)}"}
    
    def get_abnormal_equipment_list(self, params: Dict) -> Dict:
        """获取异常装备列表"""
        try:
            page = int(params.get('page', 1))
            page_size = int(params.get('page_size', 20))
            status = params.get('status')
            
            # 验证分页参数
            if page < 1:
                page = 1
            if page_size < 1 or page_size > 100:
                page_size = 20
            
            result = self.service.get_abnormal_equipment_list(page, page_size, status)
            return result
            
        except Exception as e:
            logger.error(f"获取异常装备列表失败: {e}")
            return {"error": f"获取异常装备列表失败: {str(e)}"}
    
    def update_abnormal_equipment_status(self, equip_sn: str, status: str, notes: str = None) -> Dict:
        """更新异常装备状态"""
        try:
            if not equip_sn:
                return {"error": "装备序列号不能为空"}
            
            result = self.service.update_abnormal_equipment_status(equip_sn, status, notes)
            return result
            
        except Exception as e:
            logger.error(f"更新异常装备状态失败: {e}")
            return {"error": f"更新异常装备状态失败: {str(e)}"}
    
    def delete_abnormal_equipment(self, equip_sn: str) -> Dict:
        """删除异常装备记录"""
        try:
            if not equip_sn:
                return {"error": "装备序列号不能为空"}
            
            result = self.service.delete_abnormal_equipment(equip_sn)
            return result
            
        except Exception as e:
            logger.error(f"删除异常装备记录失败: {e}")
            return {"error": f"删除异常装备记录失败: {str(e)}"}

    def get_lingshi_config(self) -> Dict:
        """获取灵饰数据"""
        try:
            result = self.service.get_lingshi_config()
            
            if "error" in result:
                return result
            
            return result
            
        except Exception as e:
            logger.error(f"获取灵饰数据失败: {str(e)}")
            return {"error": f"获取灵饰数据失败: {str(e)}"}

    def get_weapon_config(self) -> Dict:
        """获取武器数据"""
        try:
            result = self.service.get_weapon_config()
            return result
        except Exception as e:
            logger.error(f"获取武器数据失败: {str(e)}")
            return {"error": f"获取武器数据失败: {str(e)}"}
        
    def get_pet_equip_config(self) -> Dict:
        """获取宠物装备数据"""
        try:
            result = self.service.get_pet_equip_config()
            return result
        except Exception as e:
            logger.error(f"获取宠物装备数据失败: {str(e)}")
            return {"error": f"获取宠物装备数据失败: {str(e)}"}
    
    def get_equip_config(self) -> Dict:
        """获取装备数据"""
        try:
            result = self.service.get_equip_config()
            return result
        except Exception as e:
            logger.error(f"获取装备数据失败: {str(e)}")
            return {"error": f"获取装备数据失败: {str(e)}"}