#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
装备列表API模块
"""

import os
import json
from typing import Dict, List, Optional, Tuple
from datetime import datetime
import sqlite3

class EquipmentAPI:
    def __init__(self):
        self.data_dir = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), 'data')
    
    def _validate_year_month(self, year: Optional[int], month: Optional[int]) -> Tuple[int, int]:
        """
        验证并获取有效的年月
        """
        now = datetime.now()
        current_year = now.year
        current_month = now.month
        
        if year is None or month is None:
            return current_year, current_month
            
        if not 1 <= month <= 12:
            raise ValueError(f"无效的月份: {month}，月份必须在1-12之间")
            
        return year, month
    
    def _get_db_file(self, year: Optional[int] = None, month: Optional[int] = None) -> str:
        """
        获取指定年月的装备数据库文件路径
        """
        year, month = self._validate_year_month(year, month)
        return os.path.join(self.data_dir, f'cbg_equip_{year}{month:02d}.db')
    
    def get_equipments(self, page: int = 1, page_size: int = 10, year: Optional[int] = None, month: Optional[int] = None,
                      level_min: Optional[int] = None, level_max: Optional[int] = None,
                      price_min: Optional[int] = None, price_max: Optional[int] = None,
                      equip_type: Optional[List[str]] = None, 
                      equip_special_skills: Optional[List[str]] = None,
                      equip_special_effect: Optional[List[str]] = None,
                      suit_effect: Optional[str] = None,
                      suit_added_status: Optional[str] = None,
                      suit_transform_skills: Optional[str] = None, 
                      suit_transform_charms: Optional[str] = None,
                      gem_value: Optional[str] = None,
                      gem_level: Optional[int] = None,
                      sort_by: Optional[str] = 'price', sort_order: Optional[str] = 'asc') -> Dict:
        """
        获取分页的装备列表
        """
        try:
            year, month = self._validate_year_month(year, month)
            db_file = self._get_db_file(year, month)
            
            if not os.path.exists(db_file):
                return {
                    "total": 0, "page": page, "page_size": page_size, "total_pages": 0, "data": [],
                    "year": year, "month": month, "message": f"未找到 {year}年{month}月 的装备数据文件"
                }
            
            with sqlite3.connect(db_file) as conn:
                conn.row_factory = sqlite3.Row
                cursor = conn.cursor()
                
                conditions = []
                params = []
                
                # 基础筛选条件
                if level_min is not None:
                    conditions.append("level >= ?")
                    params.append(level_min)
                if level_max is not None:
                    conditions.append("level <= ?")
                    params.append(level_max)
                if price_min is not None:
                    conditions.append("price >= ?")
                    params.append(price_min * 100) # 前端传元，后端存分
                if price_max is not None:
                    conditions.append("price <= ?")
                    params.append(price_max * 100)
                
                # 装备类型筛选（多选）
                if equip_type and len(equip_type) > 0:
                    type_placeholders = ','.join(['?' for _ in equip_type])
                    conditions.append(f"kindid IN ({type_placeholders})")
                    params.extend(equip_type)
                
                # 特技筛选（多选）
                if equip_special_skills and len(equip_special_skills) > 0:
                    skill_placeholders = ','.join(['?' for _ in equip_special_skills])
                    conditions.append(f"special_skill IN ({skill_placeholders})")
                    params.extend(equip_special_skills)
                
                # 特效筛选（多选，JSON数组格式）
                if equip_special_effect and len(equip_special_effect) > 0:
                    effect_conditions = []
                    for effect in equip_special_effect:
                        # 使用精确的JSON数组匹配，避免数字包含关系的误匹配
                        # 匹配模式：[6], [6,x], [x,6], [x,6,y] 等，但不匹配16, 26等包含6的数字
                        effect_conditions.append("(special_effect LIKE ? OR special_effect LIKE ? OR special_effect LIKE ? OR special_effect LIKE ?)")
                        # 四种匹配模式：单独存在、开头、中间、结尾
                        params.extend([
                            f'[{effect}]',        # 只有这一个特效：[6]
                            f'[{effect},%',       # 在开头：[6,x,...]
                            f'%,{effect},%',      # 在中间：[x,6,y,...]  
                            f'%,{effect}]'        # 在结尾：[x,y,6]
                        ])
                    conditions.append(f"({' OR '.join(effect_conditions)})")
                
                # 套装筛选
                if suit_effect:
                    conditions.append("suit_effect = ?")
                    params.append(suit_effect)
                    
                if suit_added_status:
                    conditions.append("suit_effect = ?")
                    params.append(suit_added_status)
                    
                if suit_transform_skills:
                    conditions.append("suit_effect = ?")
                    params.append(suit_transform_skills)
                    
                if suit_transform_charms:
                    conditions.append("suit_effect = ?")
                    params.append(suit_transform_charms)
                
                # 宝石筛选
                if gem_value:
                    conditions.append("JSON_EXTRACT(gem_value, '$') LIKE ?")
                    params.append(f'%"{gem_value}"%')
                    
                if gem_level is not None:
                    conditions.append("gem_level >= ?")
                    params.append(gem_level)
              
                where_clause = f"WHERE {' AND '.join(conditions)}" if conditions else ""
                
                # 获取总数
                count_sql = f"SELECT COUNT(*) FROM equipments {where_clause}"
                total = cursor.execute(count_sql, params).fetchone()[0]
                
                total_pages = (total + page_size - 1) // page_size
                
                # 排序
                order_by_clause = ""
                if sort_by and sort_order:
                    # 防止SQL注入 - 扩展支持的排序字段
                    allowed_sort_by = [
                        'price',           # 价格
                        'level',           # 等级
                        'all_damage',      # 总伤
                        'init_damage',     # 初伤
                        'init_wakan',      # 初灵
                        'init_defense',    # 初防
                        'init_hp',         # 初血
                        'init_dex',        # 初敏
                        'create_time_equip', # 创建时间
                        'selling_time',    # 上架时间
                        'gem_level',       # 宝石等级
                        'special_effect',  # 特效
                        'special_skill',   # 特技
                        'suit_effect',     # 套装
                        'server_name',     # 服务器
                        'equip_name',      # 装备名称
                        'seller_nickname', # 卖家昵称
                        'zongshang'        # 总伤（备用字段名）
                    ]
                    if sort_by in allowed_sort_by and sort_order.lower() in ['asc', 'desc']:
                        order_by_clause = f"ORDER BY {sort_by} {sort_order.upper()}"

                # 分页查询
                offset = (page - 1) * page_size
                query_sql = f"SELECT * FROM equipments {where_clause} {order_by_clause} LIMIT ? OFFSET ?"
                
                equipments = cursor.execute(query_sql, params + [page_size, offset]).fetchall()
                
                return {
                    "total": total,
                    "page": page,
                    "page_size": page_size,
                    "total_pages": total_pages,
                    "data": [dict(row) for row in equipments],
                    "year": year,
                    "month": month,
                }

        except Exception as e:
            return {"error": str(e)}

    def get_equipment_details(self, equip_sn: str, year: Optional[int] = None, month: Optional[int] = None) -> Optional[Dict]:
        """获取单个装备的详细信息"""
        try:
            year, month = self._validate_year_month(year, month)
            db_file = self._get_db_file(year, month)

            if not os.path.exists(db_file):
                return None
            
            with sqlite3.connect(db_file) as conn:
                conn.row_factory = sqlite3.Row
                cursor = conn.cursor()
                
                sql = "SELECT * FROM equipments WHERE equip_sn = ?"
                equipment = cursor.execute(sql, (equip_sn,)).fetchone()
                
                return dict(equipment) if equipment else None

        except Exception as e:
            print(f"获取装备详情时出错: {e}")
            return None

def main():
    api = EquipmentAPI()
    
    print("--- 测试获取装备列表 ---")
    equipments_data = api.get_equipments(page=1, page_size=5, level_min=100)
    if "error" not in equipments_data:
        print(f"总数: {equipments_data['total']}, 当前页: {equipments_data['page']}")
        for equip in equipments_data['data']:
            print(f"  - {equip['equip_name']} (Lvl: {equip['level']}, Price: {equip['price']/100}元, SN: {equip['equip_sn']})")
    else:
        print(f"错误: {equipments_data['error']}")
    
    print("\n--- 测试获取单个装备详情 ---")
    if "error" not in equipments_data and equipments_data['data']:
        test_sn = equipments_data['data'][0]['equip_sn']
        details = api.get_equipment_details(equip_sn=test_sn)
        if details:
            print(f"成功获取装备详情 (SN: {test_sn}):")
            print(json.dumps(details, indent=2, ensure_ascii=False))
        else:
            print(f"未找到SN为 {test_sn} 的装备")

if __name__ == '__main__':
    main() 