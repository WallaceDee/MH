#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
角色服务
"""

import os
import json
import tempfile
from typing import Dict, List, Optional, Tuple
from datetime import datetime
import sqlite3
import logging

from src.utils.project_path import get_project_root, get_data_path

logger = logging.getLogger(__name__)


class roleService:
    def __init__(self):
        # 获取项目根目录
        self.project_root = get_project_root()
        self.data_dir = get_data_path()
    
    def _validate_year_month(self, year: Optional[int], month: Optional[int]) -> Tuple[int, int]:
        """验证并获取有效的年月"""
        now = datetime.now()
        current_year = now.year
        current_month = now.month
        
        if year is None or month is None:
            return current_year, current_month
            
        if not 1 <= month <= 12:
            raise ValueError(f"无效的月份: {month}，月份必须在1-12之间")
            
        return year, month
    
    def _get_db_file(self, year: Optional[int] = None, month: Optional[int] = None) -> str:
        """获取指定年月的数据库文件路径"""
        year, month = self._validate_year_month(year, month)
        return os.path.join(self.data_dir, f'{year}{month:02d}', f'cbg_roles_{year}{month:02d}.db')
    
    def get_roles(self, page: int = 1, page_size: int = 10, year: Optional[int] = None, month: Optional[int] = None,
                      level_min: Optional[int] = None, level_max: Optional[int] = None,
                      school_skill_num: Optional[int] = None, school_skill_level: Optional[int] = None,
                      # 角色修炼参数
                      expt_gongji: Optional[int] = None, expt_fangyu: Optional[int] = None,
                      expt_fashu: Optional[int] = None, expt_kangfa: Optional[int] = None,
                      expt_total: Optional[int] = None, max_expt_gongji: Optional[int] = None,
                      max_expt_fangyu: Optional[int] = None, max_expt_fashu: Optional[int] = None,
                      max_expt_kangfa: Optional[int] = None, expt_lieshu: Optional[int] = None,
                      # 召唤兽修炼参数
                      bb_expt_gongji: Optional[int] = None, bb_expt_fangyu: Optional[int] = None,
                      bb_expt_fashu: Optional[int] = None, bb_expt_kangfa: Optional[int] = None,
                      bb_expt_total: Optional[int] = None, skill_drive_pet: Optional[int] = None,
                      # 其他参数
                      equip_num: Optional[int] = None, pet_num: Optional[int] = None,
                      pet_num_level: Optional[int] = None,
                      # 排序参数
                      sort_by: Optional[str] = None, sort_order: Optional[str] = None) -> Dict:
        """获取分页的角色列表"""
        try:
            # 验证年月
            year, month = self._validate_year_month(year, month)
            db_file = self._get_db_file(year, month)
            
            logger.info(f"数据库文件路径: {db_file}")
            
            if not os.path.exists(db_file):
                return {
                    "total": 0,
                    "page": page,
                    "page_size": page_size,
                    "total_pages": 0,
                    "data": [],
                    "year": year,
                    "month": month,
                    "message": f"未找到 {year}年{month}月 的数据文件"
                }
            
            with sqlite3.connect(db_file) as conn:
                conn.row_factory = sqlite3.Row
                cursor = conn.cursor()
                
                # 构建等级过滤条件
                level_conditions = []
                level_params = []
                if level_min is not None:
                    level_conditions.append("c.level >= ?")
                    level_params.append(level_min)
                if level_max is not None:
                    level_conditions.append("c.level <= ?")
                    level_params.append(level_max)
                
                # 构建师门技能过滤条件
                if school_skill_num is not None and school_skill_level is not None:
                    level_conditions.append("""
                        (SELECT COUNT(*) FROM json_each(c.school_skills) 
                        WHERE CAST(json_extract(value, '$') AS INTEGER) >= ?) >= ?
                    """)
                    level_params.extend([school_skill_level, school_skill_num])
                
                # 构建角色修炼过滤条件
                if expt_gongji is not None:
                    level_conditions.append("l.expt_ski1 >= ?")
                    level_params.append(expt_gongji)
                if expt_fangyu is not None:
                    level_conditions.append("l.expt_ski2 >= ?")
                    level_params.append(expt_fangyu)
                if expt_fashu is not None:
                    level_conditions.append("l.expt_ski3 >= ?")
                    level_params.append(expt_fashu)
                if expt_kangfa is not None:
                    level_conditions.append("l.expt_ski4 >= ?")
                    level_params.append(expt_kangfa)
                if expt_total is not None:
                    level_conditions.append("(COALESCE(l.expt_ski1, 0) + COALESCE(l.expt_ski2, 0) + COALESCE(l.expt_ski3, 0) + COALESCE(l.expt_ski4, 0)) >= ?")
                    level_params.append(expt_total)
                if max_expt_gongji is not None:
                    level_conditions.append("l.max_expt1 >= ?")
                    level_params.append(max_expt_gongji)
                if max_expt_fangyu is not None:
                    level_conditions.append("l.max_expt2 >= ?")
                    level_params.append(max_expt_fangyu)
                if max_expt_fashu is not None:
                    level_conditions.append("l.max_expt3 >= ?")
                    level_params.append(max_expt_fashu)
                if max_expt_kangfa is not None:
                    level_conditions.append("l.max_expt4 >= ?")
                    level_params.append(max_expt_kangfa)
                if expt_lieshu is not None:
                    level_conditions.append("l.expt_ski5 >= ?")
                    level_params.append(expt_lieshu)
                
                # 构建召唤兽修炼过滤条件
                if bb_expt_gongji is not None:
                    level_conditions.append("l.beast_ski1 >= ?")
                    level_params.append(bb_expt_gongji)
                if bb_expt_fangyu is not None:
                    level_conditions.append("l.beast_ski2 >= ?")
                    level_params.append(bb_expt_fangyu)
                if bb_expt_fashu is not None:
                    level_conditions.append("l.beast_ski3 >= ?")
                    level_params.append(bb_expt_fashu)
                if bb_expt_kangfa is not None:
                    level_conditions.append("l.beast_ski4 >= ?")
                    level_params.append(bb_expt_kangfa)
                if bb_expt_total is not None:
                    level_conditions.append("(COALESCE(l.beast_ski1, 0) + COALESCE(l.beast_ski2, 0) + COALESCE(l.beast_ski3, 0) + COALESCE(l.beast_ski4, 0)) >= ?")
                    level_params.append(bb_expt_total)
                if skill_drive_pet is not None:
                    level_conditions.append("c.yushoushu_skill >= ?")
                    level_params.append(skill_drive_pet)
                
                # 根据all_equip_json构建物品数量小于等于过滤条件
                if equip_num is not None:
                    if equip_num == 0:
                        # 当equip_num为0时,表示没有物品
                        level_conditions.append("(l.all_equip_json IS NULL OR l.all_equip_json = '' OR l.all_equip_json = '{}')")
                    else:
                        # 当equip_num大于0时，使用SQL字符串匹配来统计装备数量
                        # 通过计算JSON中"iType"出现的次数来估算装备数量
                        level_conditions.append("""
                            (CASE 
                                WHEN l.all_equip_json IS NULL OR l.all_equip_json = '' OR l.all_equip_json = '{}' THEN 0
                                ELSE (LENGTH(l.all_equip_json) - LENGTH(REPLACE(l.all_equip_json, 'iType', ''))) / LENGTH('iType')
                            END) <= ?
                        """)
                        level_params.append(equip_num)

                # 构建宠物（大于pet_level）物数量小于等于pet_num过滤条件
                if pet_num is not None and pet_num_level is not None:
                    if pet_num == 0:
                        # 当pet_num为0时,表示没有宠物
                        level_conditions.append("(l.all_summon_json IS NULL OR l.all_summon_json = '[]')")
                    else:
                        level_conditions.append("""
                            (SELECT COUNT(*) FROM json_each(l.all_summon_json) 
                            WHERE CAST(json_extract(value, '$.iGrade') AS INTEGER) > ?) <= ?
                        """)
                        level_params.extend([pet_num_level, pet_num])

                level_where = " AND ".join(level_conditions) if level_conditions else "1=1"
                
                # 获取总记录数
                count_query = f"SELECT COUNT(*) FROM roles c LEFT JOIN large_equip_desc_data l ON c.eid = l.eid WHERE {level_where}"
                cursor.execute(count_query, level_params)
                total = cursor.fetchone()[0]
                
                # 计算分页
                total_pages = (total + page_size - 1) // page_size
                offset = (page - 1) * page_size
                
                # 构建排序条件
                order_by = "c.create_time DESC"  # 默认按创建时间倒序
                if sort_by and sort_order:
                    # 验证排序字段
                    allowed_sort_by = [
                        'highlight', 'dynamic_tags', 'price', 'level','all_equip_json', 'collect_num',
                        'expt_ski1', 'expt_ski2', 'expt_ski3', 'expt_ski4', 'expt_ski5',
                        'max_expt1', 'max_expt2', 'max_expt3', 'max_expt4',
                        'beast_ski1', 'beast_ski2', 'beast_ski3', 'beast_ski4',
                        'create_time', 'update_time'
                    ]
                    
                    # 解析排序参数
                    sort_fields = sort_by.split(',')
                    sort_orders = sort_order.split(',')
                    
                    # 构建排序条件
                    order_conditions = []
                    for field, order in zip(sort_fields, sort_orders):
                        if field in allowed_sort_by and order.lower() in ['asc', 'desc']:
                            # 根据字段名确定表别名
                            if field in ['price', 'level', 'collect_num', 'create_time', 'update_time']:
                                order_conditions.append(f"c.{field} {order}")
                            else:
                                # 修炼相关字段在l表中
                                order_conditions.append(f"l.{field} {order}")
                    
                    if order_conditions:
                        order_by = ", ".join(order_conditions)
                
                # 为了解决字段名冲突，明确列出所有字段并为冲突字段使用别名
                query = f"""
                    SELECT  l.*,c.*  FROM roles c
                    LEFT JOIN large_equip_desc_data l ON c.eid = l.eid
                    WHERE {level_where}
                    ORDER BY {order_by}
                    LIMIT ? OFFSET ?
                """
                cursor.execute(query, level_params + [page_size, offset])
                
                rows = cursor.fetchall()
                roles = [dict(row) for row in rows]
                
                return {
                    "total": total,
                    "page": page,
                    "page_size": page_size,
                    "total_pages": total_pages,
                    "data": roles,
                    "year": year,
                    "month": month,
                    "message": f"成功获取 {year}年{month}月 的数据"
                }
            
        except ValueError as e:
            logger.error(f"参数验证错误: {e}")
            return {
                "error": str(e),
                "total": 0,
                "page": page,
                "page_size": page_size,
                "total_pages": 0,
                "data": [],
                "year": year,
                "month": month
            }
        except Exception as e:
            logger.error(f"获取角色列表时出错: {e}")
            return {"error": str(e)}
    
    def get_role_details(self, eid: str, year: Optional[int] = None, month: Optional[int] = None) -> Optional[Dict]:
        """获取单个角色的详细信息"""
        try:
            if not eid:
                return None
                
            year, month = self._validate_year_month(year, month)
            db_file = self._get_db_file(year, month)

            if not os.path.exists(db_file):
                return None
            
            with sqlite3.connect(db_file) as conn:
                conn.row_factory = sqlite3.Row
                cursor = conn.cursor()
                
                # 使用联接查询获取完整信息
                query = """
                    SELECT  l.*,c.*  FROM roles c
                    LEFT JOIN large_equip_desc_data l ON c.eid = l.eid
                    WHERE c.eid = ?
                """
                role = cursor.execute(query, (eid,)).fetchone()
                
                return dict(role) if role else None

        except Exception as e:
            logger.error(f"获取角色详情时出错: {e}")
            return None

    def get_role_feature(self, eid: str, year: Optional[int] = None, month: Optional[int] = None) -> Optional[Dict]:
        """获取角色详情并提取特征"""
        try:
            # 先获取角色基础数据
            role_data = self.get_role_details(eid, year, month)
            if not role_data:
                return None
            
            # 导入特征提取器
            from src.evaluator.feature_extractor.feature_extractor import FeatureExtractor
            
            # 创建特征提取器实例
            extractor = FeatureExtractor()
            
            # 提取特征
            features = extractor.extract_features(role_data)
            
            # 将原始角色数据和提取的特征合并返回
            result = {
                'role_data': role_data,
                'features': features,
                'eid': eid
            }
            
            return result
            
        except Exception as e:
            logger.error(f"获取角色特征时出错: {e}")
            return None


            