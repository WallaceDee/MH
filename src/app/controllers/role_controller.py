#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
角色控制器
"""

import logging
from typing import Dict, List, Optional
from ..services.role_service import roleService

logger = logging.getLogger(__name__)


class roleController:
    """角色控制器"""
    
    def __init__(self):
        self.service = roleService()
    
    def get_roles(self, params: Dict) -> Dict:
        """获取角色列表"""
        try:
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
            
            # 基本筛选条件
            level_min = params.get('level_min')
            level_max = params.get('level_max')
            
            if level_min is not None:
                level_min = int(level_min)
            if level_max is not None:
                level_max = int(level_max)
            
            # 师门技能筛选
            school_skill_num = params.get('school_skill_num')
            school_skill_level = params.get('school_skill_level')
            
            if school_skill_num is not None:
                school_skill_num = int(school_skill_num)
            if school_skill_level is not None:
                school_skill_level = int(school_skill_level)
            
            # 角色修炼参数
            expt_gongji = params.get('expt_gongji')
            expt_fangyu = params.get('expt_fangyu')
            expt_fashu = params.get('expt_fashu')
            expt_kangfa = params.get('expt_kangfa')
            expt_total = params.get('expt_total')
            max_expt_gongji = params.get('max_expt_gongji')
            max_expt_fangyu = params.get('max_expt_fangyu')
            max_expt_fashu = params.get('max_expt_fashu')
            max_expt_kangfa = params.get('max_expt_kangfa')
            expt_lieshu = params.get('expt_lieshu')
            
            if expt_gongji is not None:
                expt_gongji = int(expt_gongji)
            if expt_fangyu is not None:
                expt_fangyu = int(expt_fangyu)
            if expt_fashu is not None:
                expt_fashu = int(expt_fashu)
            if expt_kangfa is not None:
                expt_kangfa = int(expt_kangfa)
            if expt_total is not None:
                expt_total = int(expt_total)
            if max_expt_gongji is not None:
                max_expt_gongji = int(max_expt_gongji)
            if max_expt_fangyu is not None:
                max_expt_fangyu = int(max_expt_fangyu)
            if max_expt_fashu is not None:
                max_expt_fashu = int(max_expt_fashu)
            if max_expt_kangfa is not None:
                max_expt_kangfa = int(max_expt_kangfa)
            if expt_lieshu is not None:
                expt_lieshu = int(expt_lieshu)
            
            # 召唤兽修炼参数
            bb_expt_gongji = params.get('bb_expt_gongji')
            bb_expt_fangyu = params.get('bb_expt_fangyu')
            bb_expt_fashu = params.get('bb_expt_fashu')
            bb_expt_kangfa = params.get('bb_expt_kangfa')
            bb_expt_total = params.get('bb_expt_total')
            skill_drive_pet = params.get('skill_drive_pet')
            
            if bb_expt_gongji is not None:
                bb_expt_gongji = int(bb_expt_gongji)
            if bb_expt_fangyu is not None:
                bb_expt_fangyu = int(bb_expt_fangyu)
            if bb_expt_fashu is not None:
                bb_expt_fashu = int(bb_expt_fashu)
            if bb_expt_kangfa is not None:
                bb_expt_kangfa = int(bb_expt_kangfa)
            if bb_expt_total is not None:
                bb_expt_total = int(bb_expt_total)
            if skill_drive_pet is not None:
                skill_drive_pet = int(skill_drive_pet)
            
            # 其他参数
            equip_num = params.get('equip_num')
            pet_num = params.get('pet_num')
            pet_num_level = params.get('pet_num_level')
            accept_bargain = params.get('accept_bargain')
            
            if equip_num is not None:
                equip_num = int(equip_num)
            if pet_num is not None:
                pet_num = int(pet_num)
            if pet_num_level is not None:
                pet_num_level = int(pet_num_level)
            if accept_bargain is not None:
                accept_bargain = int(accept_bargain)
            
            # 排序参数
            sort_by = params.get('sort_by')
            sort_order = params.get('sort_order')
            
            # 角色类型参数
            role_type = params.get('role_type', 'normal')
            
            # 调用服务层
            result = self.service.get_roles(
                page=page,
                page_size=page_size,
                year=year,
                month=month,
                level_min=level_min,
                level_max=level_max,
                equip_num=equip_num,
                pet_num=pet_num,
                pet_num_level=pet_num_level,
                accept_bargain=accept_bargain,
                sort_by=sort_by,
                sort_order=sort_order,
                role_type=role_type
            )
            
            return result
            
        except ValueError as e:
            logger.error(f"参数格式错误: {e}")
            return {"error": f"参数格式错误: {str(e)}"}
        except Exception as e:
            logger.error(f"获取角色列表时出错: {e}")
            return {"error": f"获取角色列表时出错: {str(e)}"}
    
    def get_role_details(self, eid: str, year: Optional[int] = None, month: Optional[int] = None, role_type: str = 'normal') -> Optional[Dict]:
        """获取角色详情"""
        try:
            if not eid:
                return {"error": "角色eid不能为空"}
            
            result = self.service.get_role_details(eid, year, month, role_type)
            
            if result is None:
                return {"error": "未找到指定的角色"}
            
            return result
            
        except Exception as e:
            logger.error(f"获取角色详情时出错: {e}")
            return {"error": f"获取角色详情时出错: {str(e)}"}
 
    def get_role_feature(self, eid: str, year: Optional[int] = None, month: Optional[int] = None, role_type: str = 'normal') -> Optional[Dict]:
        """获取角色特征"""
        try:
            result = self.service.get_role_feature(eid, year, month, role_type)
            return result
        except Exception as e:
            logger.error(f"获取角色特征时出错: {e}")
            return {"error": f"获取角色特征时出错: {str(e)}"}

    def get_role_valuation(self, eid: str, year: Optional[int] = None, month: Optional[int] = None, 
                          role_type: str = 'normal', strategy: str = 'fair_value', 
                          similarity_threshold: float = 0.7, max_anchors: int = 30) -> Dict:
        """获取角色估价"""
        try:
            if not eid:
                return {"error": "角色eid不能为空"}
            
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
            result = self.service.get_role_valuation(
                eid=eid,
                year=year,
                month=month,
                role_type=role_type,
                strategy=strategy,
                similarity_threshold=similarity_threshold,
                max_anchors=max_anchors
            )
            
            return result
            
        except Exception as e:
            logger.error(f"获取角色估价时出错: {e}")
            return {"error": f"获取角色估价时出错: {str(e)}"}

    def find_role_anchors(self, eid: str, year: Optional[int] = None, month: Optional[int] = None, 
                         role_type: str = 'normal', similarity_threshold: float = 0.7, max_anchors: int = 30) -> Dict:
        """查找相似角色锚点"""
        try:
            if not eid:
                return {"error": "角色eid不能为空"}
            
            # 验证相似度阈值
            if not 0.0 <= similarity_threshold <= 1.0:
                return {"error": "相似度阈值必须在0.0-1.0之间"}
            
            # 验证最大锚点数量
            if not 1 <= max_anchors <= 100:
                return {"error": "最大锚点数量必须在1-100之间"}
            
            # 调用服务层查找锚点
            result = self.service.find_role_anchors(
                eid=eid,
                year=year,
                month=month,
                role_type=role_type,
                similarity_threshold=similarity_threshold,
                max_anchors=max_anchors
            )
            
            return result
            
        except Exception as e:
            logger.error(f"查找相似角色锚点时出错: {e}")
            return {"error": f"查找相似角色锚点时出错: {str(e)}"}

    def batch_role_valuation(self, eid_list: List[str], year: Optional[int] = None, month: Optional[int] = None,
                            role_type: str = 'normal', strategy: str = 'fair_value',
                            similarity_threshold: float = 0.7, max_anchors: int = 30, verbose: bool = False) -> Dict:
        """批量角色估价"""
        try:
            logger.info(f"开始批量角色估价，角色数量: {len(eid_list)}，策略: {strategy}，详细日志: {verbose}")
            
            if not eid_list:
                return {"error": "角色eid列表不能为空"}
            
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
            result = self.service.batch_role_valuation(
                eid_list=eid_list,
                year=year,
                month=month,
                role_type=role_type,
                strategy=strategy,
                similarity_threshold=similarity_threshold,
                max_anchors=max_anchors,
                verbose=verbose
            )
            
            return result
            
        except Exception as e:
            logger.error(f"批量角色估价失败: {e}")
            return {
                "error": f"批量角色估价失败: {str(e)}",
                "results": []
            }

    def delete_role(self, eid: str, params: Dict) -> Dict:
        """删除角色"""
        try:
            if not eid:
                return {"error": "角色eid不能为空"}
            
            # 从参数中提取年月和角色类型
            year = params.get('year')
            month = params.get('month')
            role_type = params.get('role_type', 'normal')
            
            # 类型转换
            if year:
                year = int(year)
            if month:
                month = int(month)
            
            result = self.service.delete_role(eid, year, month, role_type)
            
            if "error" in result:
                return result
            
            return result
            
        except ValueError as e:
            logger.error(f"参数格式错误: {e}")
            return {"error": f"参数格式错误: {str(e)}"}
        except Exception as e:
            logger.error(f"删除角色时出错: {e}")
            return {"error": f"删除角色时出错: {str(e)}"}

    def switch_role_type(self, eid: str, params: Dict) -> Dict:
        """切换角色类型（数据迁移）"""
        try:
            if not eid:
                return {"error": "角色eid不能为空"}
            
            # 从参数中提取年月和角色类型
            year = params.get('year')
            month = params.get('month')
            current_role_type = params.get('current_role_type', 'normal')
            target_role_type = params.get('target_role_type')
            
            if not target_role_type:
                return {"error": "目标角色类型不能为空"}
            
            # 类型转换
            if year:
                year = int(year)
            if month:
                month = int(month)
            
            result = self.service.switch_role_type(eid, year, month, current_role_type, target_role_type)
            
            if "error" in result:
                return result
            
            return result
            
        except ValueError as e:
            logger.error(f"参数格式错误: {e}")
            return {"error": f"参数格式错误: {str(e)}"}
        except Exception as e:
            logger.error(f"切换角色类型时出错: {e}")
            return {"error": f"切换角色类型时出错: {str(e)}"}

    def update_role_base_price(self, eid: str, base_price: float, year: Optional[int] = None, month: Optional[int] = None, role_type: str = 'normal') -> bool:
        """更新角色裸号价格"""
        try:
            if not eid:
                logger.error("角色eid不能为空")
                return False
            
            if base_price is None or base_price < 0:
                logger.error("裸号价格不能为空或负数")
                return False
            
            # 调用服务层更新价格
            success = self.service.update_role_base_price(eid, base_price, year, month, role_type)
            
            if success:
                logger.info(f"成功更新角色 {eid} 的裸号价格: {base_price}分")
            else:
                logger.warning(f"更新角色 {eid} 的裸号价格失败")
            
            return success
            
        except Exception as e:
            logger.error(f"更新角色裸号价格时出错: {e}")
            return False

