#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
角色控制器
"""

import logging
from typing import Dict, List, Optional
from ..services.character_service import CharacterService

logger = logging.getLogger(__name__)


class CharacterController:
    """角色控制器"""
    
    def __init__(self):
        self.service = CharacterService()
    
    def get_characters(self, params: Dict) -> Dict:
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
            
            if equip_num is not None:
                equip_num = int(equip_num)
            if pet_num is not None:
                pet_num = int(pet_num)
            if pet_num_level is not None:
                pet_num_level = int(pet_num_level)
            
            # 排序参数
            sort_by = params.get('sort_by')
            sort_order = params.get('sort_order')
            
            # 调用服务层
            result = self.service.get_characters(
                page=page,
                page_size=page_size,
                year=year,
                month=month,
                level_min=level_min,
                level_max=level_max,
                school_skill_num=school_skill_num,
                school_skill_level=school_skill_level,
                expt_gongji=expt_gongji,
                expt_fangyu=expt_fangyu,
                expt_fashu=expt_fashu,
                expt_kangfa=expt_kangfa,
                expt_total=expt_total,
                max_expt_gongji=max_expt_gongji,
                max_expt_fangyu=max_expt_fangyu,
                max_expt_fashu=max_expt_fashu,
                max_expt_kangfa=max_expt_kangfa,
                expt_lieshu=expt_lieshu,
                bb_expt_gongji=bb_expt_gongji,
                bb_expt_fangyu=bb_expt_fangyu,
                bb_expt_fashu=bb_expt_fashu,
                bb_expt_kangfa=bb_expt_kangfa,
                bb_expt_total=bb_expt_total,
                skill_drive_pet=skill_drive_pet,
                equip_num=equip_num,
                pet_num=pet_num,
                pet_num_level=pet_num_level,
                sort_by=sort_by,
                sort_order=sort_order
            )
            
            return result
            
        except ValueError as e:
            logger.error(f"参数格式错误: {e}")
            return {"error": f"参数格式错误: {str(e)}"}
        except Exception as e:
            logger.error(f"获取角色列表时出错: {e}")
            return {"error": f"获取角色列表时出错: {str(e)}"}
    
    def get_character_details(self, equip_id: str, year: Optional[int] = None, month: Optional[int] = None) -> Optional[Dict]:
        """获取角色详情"""
        try:
            if not equip_id:
                return {"error": "角色装备ID不能为空"}
            
            result = self.service.get_character_details(equip_id, year, month)
            
            if result is None:
                return {"error": "未找到指定的角色"}
            
            return result
            
        except Exception as e:
            logger.error(f"获取角色详情时出错: {e}")
            return {"error": f"获取角色详情时出错: {str(e)}"}
    
    def export_characters_json(self, params: Dict) -> Dict:
        """导出角色JSON数据"""
        try:
            export_all = params.get('export_all', False)
            if isinstance(export_all, str):
                export_all = export_all.lower() in ['true', '1', 'yes']
            
            # 提取过滤参数（与get_characters相同的逻辑）
            filter_params = {}
            
            # 年月参数
            year = params.get('year')
            month = params.get('month')
            if year:
                filter_params['year'] = int(year)
            if month:
                filter_params['month'] = int(month)
            
            # 等级过滤
            level_min = params.get('level_min')
            level_max = params.get('level_max')
            if level_min is not None:
                filter_params['level_min'] = int(level_min)
            if level_max is not None:
                filter_params['level_max'] = int(level_max)
            
            # 调用服务层导出
            result_path = self.service.export_characters_json(
                export_all=export_all,
                **filter_params
            )
            
            if result_path:
                return {"file_path": result_path, "message": "导出成功"}
            else:
                return {"error": "导出失败"}
            
        except ValueError as e:
            logger.error(f"参数格式错误: {e}")
            return {"error": f"参数格式错误: {str(e)}"}
        except Exception as e:
            logger.error(f"导出角色JSON时出错: {e}")
            return {"error": f"导出角色JSON时出错: {str(e)}"}
    
    def export_single_character_json(self, equip_id: str, year: Optional[int] = None, month: Optional[int] = None) -> Dict:
        """导出单个角色JSON数据"""
        try:
            if not equip_id:
                return {"error": "角色装备ID不能为空"}
            
            result_path = self.service.export_single_character_json(equip_id, year, month)
            
            if result_path:
                return {"file_path": result_path, "message": "导出成功"}
            else:
                return {"error": "导出失败或未找到指定角色"}
            
        except Exception as e:
            logger.error(f"导出单个角色JSON时出错: {e}")
            return {"error": f"导出单个角色JSON时出错: {str(e)}"} 