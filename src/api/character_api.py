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
    
    def get_characters(self, page: int = 1, page_size: int = 20, year: Optional[int] = None, month: Optional[int] = None) -> Dict:
        """
        获取分页的角色列表
        
        Args:
            page: 页码，从1开始
            page_size: 每页数量
            year: 年份，不传则使用当前年份
            month: 月份，不传则使用当前月份
            
        Returns:
            Dict: 包含角色列表和分页信息的字典
        """
        try:
            # 验证年月
            year, month = self._validate_year_month(year, month)
            db_file = self._get_db_file(year, month)
            
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
                
                # 获取总记录数
                cursor.execute("SELECT COUNT(*) FROM characters")
                total = cursor.fetchone()[0]
                
                # 计算分页
                total_pages = (total + page_size - 1) // page_size
                offset = (page - 1) * page_size
                
                # 为了解决字段名冲突，明确列出所有字段并为冲突字段使用别名
                cursor.execute("""
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
                    ORDER BY c.create_time DESC 
                    LIMIT ? OFFSET ?
                """, (page_size, offset))
                
                rows = cursor.fetchall()
                characters = [dict(row) for row in rows]
            
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