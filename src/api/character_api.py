#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
角色列表API模块
"""

import os
import json
from typing import Dict, List, Optional, Tuple
from datetime import datetime
import sqlite3

class CharacterAPI:
    def __init__(self):
        self.data_dir = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), 'data')
    
    def _validate_year_month(self, year: Optional[int], month: Optional[int]) -> Tuple[int, int]:
        """
        验证并获取有效的年月
        
        Args:
            year: 年份
            month: 月份
            
        Returns:
            Tuple[int, int]: (年份, 月份)
            
        Raises:
            ValueError: 当年月无效时抛出
        """
        now = datetime.now()
        current_year = now.year
        current_month = now.month
        
        # 如果没有提供年月，使用当前年月
        if year is None or month is None:
            return current_year, current_month
            
        # 验证月份范围
        if not 1 <= month <= 12:
            raise ValueError(f"无效的月份: {month}，月份必须在1-12之间")
            
        return year, month
    
    def _get_db_file(self, year: Optional[int] = None, month: Optional[int] = None) -> str:
        """
        获取指定年月的数据库文件路径
        
        Args:
            year: 年份，不传则使用当前年份
            month: 月份，不传则使用当前月份
            
        Returns:
            str: 数据库文件路径
        """
        year, month = self._validate_year_month(year, month)
        return os.path.join(self.data_dir, f'cbg_data_{year}{month:02d}.db')
    
    def get_characters(self, page: int = 1, page_size: int = 10, year: Optional[int] = None, month: Optional[int] = None,
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
                      bb_expt_total: Optional[int] = None, skill_drive_pet: Optional[int] = None) -> Dict:
        """
        获取分页的角色列表
        
        Args:
            page: 页码，从1开始
            page_size: 每页数量
            year: 年份，不传则使用当前年份
            month: 月份，不传则使用当前月份
            level_min: 最低等级（不包含）
            level_max: 最高等级（包含）
            school_skill_num: 师门技能数量
            school_skill_level: 师门技能等级
            expt_gongji: 攻击修炼
            expt_fangyu: 防御修炼
            expt_fashu: 法术修炼
            expt_kangfa: 抗法修炼
            expt_total: 修炼总和
            max_expt_gongji: 攻击上限
            max_expt_fangyu: 防御上限
            max_expt_fashu: 法术上限
            max_expt_kangfa: 抗法上限
            expt_lieshu: 猎术修炼
            bb_expt_gongji: 攻击控制
            bb_expt_fangyu: 防御控制
            bb_expt_fashu: 法术控制
            bb_expt_kangfa: 抗法控制
            bb_expt_total: 宠修总和
            skill_drive_pet: 育兽术
            
        Returns:
            Dict: 包含角色列表和分页信息的字典
        """
        try:
            # 验证年月
            year, month = self._validate_year_month(year, month)
            db_file = self._get_db_file(year, month)
            
            print(f"Debug: 数据库文件路径: {db_file}")
            print(f"Debug: 等级范围: min={level_min}, max={level_max}")
            print(f"Debug: 师门技能: num={school_skill_num}, level={school_skill_level}")
            print(f"Debug: 角色修炼: gongji={expt_gongji}, fangyu={expt_fangyu}, fashu={expt_fashu}, kangfa={expt_kangfa}, total={expt_total}")
            print(f"Debug: 修炼上限: gongji={max_expt_gongji}, fangyu={max_expt_fangyu}, fashu={max_expt_fashu}, kangfa={max_expt_kangfa}")
            print(f"Debug: 猎术修炼: {expt_lieshu}")
            print(f"Debug: 召唤兽修炼: gongji={bb_expt_gongji}, fangyu={bb_expt_fangyu}, fashu={bb_expt_fashu}, kangfa={bb_expt_kangfa}, total={bb_expt_total}")
            print(f"Debug: 育兽术: {skill_drive_pet}")
            
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
                    level_conditions.append("l.skill_drive_pet >= ?")
                    level_params.append(skill_drive_pet)
                
                level_where = " AND ".join(level_conditions) if level_conditions else "1=1"
                
                # 先检查一下数据库中的等级分布
                cursor.execute("SELECT level, COUNT(*) as count FROM characters GROUP BY level ORDER BY level")
                level_distribution = cursor.fetchall()
                print(f"Debug: 等级分布: {[dict(row) for row in level_distribution]}")
                
                # 获取总记录数
                count_query = f"SELECT COUNT(*) FROM characters c LEFT JOIN large_equip_desc_data l ON c.equip_id = l.equip_id WHERE {level_where}"
                print(f"Debug: 计数查询: {count_query}")
                print(f"Debug: 查询参数: {level_params}")
                cursor.execute(count_query, level_params)
                total = cursor.fetchone()[0]
                print(f"Debug: 符合条件的记录数: {total}")
                
                # 计算分页
                total_pages = (total + page_size - 1) // page_size
                offset = (page - 1) * page_size
                
                # 为了解决字段名冲突，明确列出所有字段并为冲突字段使用别名
                query = f"""
                    SELECT 
                        c.id, c.equip_id, c.server_name, c.seller_nickname, c.level, c.price,
                        c.price_desc, c.school AS school_desc, c.area_name, c.icon_index,
                        c.kindid, c.game_ordersn, c.pass_fair_show, c.fair_show_end_time,
                        c.accept_bargain, c.status_desc, c.onsale_expire_time_desc, c.expire_time,
                        c.race, c.fly_status, c.collect_num, c.life_skills, c.school_skills,
                        c.ju_qing_skills, c.all_pets_json, c.all_equip_json AS all_equip_json_desc,
                        c.all_shenqi_json, c.all_rider_json AS all_rider_json_desc,
                        c.ex_avt_json AS ex_avt_json_desc, c.create_time, c.update_time,
                        
                        l.*
                    FROM characters c
                    LEFT JOIN large_equip_desc_data l ON c.equip_id = l.equip_id
                    WHERE {level_where}
                    ORDER BY c.create_time DESC 
                    LIMIT ? OFFSET ?
                """
                print(f"Debug: 主查询: {query}")
                print(f"Debug: 查询参数: {level_params + [page_size, offset]}")
                
                cursor.execute(query, level_params + [page_size, offset])
                
                rows = cursor.fetchall()
                characters = [dict(row) for row in rows]
                print(f"Debug: 返回记录数: {len(characters)}")
            
            return {
                "total": total,
                "page": page,
                "page_size": page_size,
                "total_pages": total_pages,
                "data": characters,
                "year": year,
                "month": month,
                "message": f"成功获取 {year}年{month}月 的数据"
            }
            
        except ValueError as e:
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
            return {
                "error": f"获取数据时发生错误: {str(e)}",
                "total": 0,
                "page": page,
                "page_size": page_size,
                "total_pages": 0,
                "data": [],
                "year": year,
                "month": month
            } 