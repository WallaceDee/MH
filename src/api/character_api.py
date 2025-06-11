#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
角色列表API模块
"""

import os
import json
import tempfile
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
                      bb_expt_total: Optional[int] = None, skill_drive_pet: Optional[int] = None,
                      # 其他参数
                      equip_num: Optional[int] = None, pet_num: Optional[int] = None,
                      pet_num_level: Optional[int] = None,
                      # 排序参数
                      sort_by: Optional[str] = None, sort_order: Optional[str] = None) -> Dict:
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
            equip_num: 物品数量上限
            pet_num: 宠物数量上限
            pet_num_level: 宠物等级下限
            sort_by: 排序字段
            sort_order: 排序方向(asc/desc)
            
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
                # 构建物品数量小于等于过滤条件
                if equip_num is not None:
                    if equip_num == 0:
                        # 当equip_num为0时,表示没有物品
                        level_conditions.append("(c.all_equip_json IS NULL OR c.all_equip_json = '{}' OR c.all_equip_json = '{\"物品总数\":0,\"人物装备\":[],\"召唤兽装备\":[],\"其他物品\":[],\"拆分销售装备\":[]}' OR json_extract(c.all_equip_json, '$.物品总数') = 0)")
                    else:
                        level_conditions.append("""
                            (SELECT json_extract(c.all_equip_json, '$.物品总数') AS total 
                            FROM characters c2 
                            WHERE c2.equip_id = c.equip_id) <= ?
                        """)
                        level_params.append(equip_num)
                # 构建宠物（大于pet_level）物数量小于等于pet_num过滤条件
                # 宠物列表中，level大于pet_num_level的宠物数量小于等于pet_num
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
                
                # 先检查一下数据库中的等级分布
                cursor.execute("SELECT level, COUNT(*) as count FROM characters GROUP BY level ORDER BY level")
                level_distribution = cursor.fetchall()
                print(f"Debug: 等级分布: {[dict(row) for row in level_distribution]}")
                
                # 获取总记录数
                count_query = f"SELECT COUNT(*) FROM characters c LEFT JOIN large_equip_desc_data l ON c.equip_id = l.equip_id WHERE {level_where}"
                print(f"\nDebug: 查询条件: {level_where}")
                print(f"Debug: 查询参数: {level_params}")
                cursor.execute(count_query, level_params)
                total = cursor.fetchone()[0]
                print(f"Debug: 符合条件的记录数: {total}")
                
                # 计算分页
                total_pages = (total + page_size - 1) // page_size
                offset = (page - 1) * page_size
                
                # 构建排序条件
                order_by = "c.create_time DESC"  # 默认按创建时间倒序
                if sort_by and sort_order:
                    # 解析排序参数
                    sort_fields = sort_by.split(',')
                    sort_orders = sort_order.split(',')
                    
                    # 构建排序条件
                    order_conditions = []
                    for field, order in zip(sort_fields, sort_orders):
                        if field == "price":
                            order_conditions.append(f"c.price {order}")
                    
                    if order_conditions:
                        order_by = ", ".join(order_conditions)
                
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
                    ORDER BY {order_by}
                    LIMIT ? OFFSET ?
                """
                cursor.execute(query, level_params + [page_size, offset])
                
                rows = cursor.fetchall()
                characters = [dict(row) for row in rows]
                print(f"Debug: 返回记录数: {len(characters)}")
                
                # 打印第一条记录的物品和宠物信息用于调试
                if characters:
                    first_char = characters[0]
                    print(f"\nDebug: 第一条记录:")
                    print(f"  equip_id: {first_char.get('equip_id')}")
                    print(f"  all_equip_json: {first_char.get('all_equip_json_desc')}")
                    print(f"  all_summon_json: {first_char.get('all_summon_json')}")
            
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
    
    def export_characters_json(self, export_all: bool = False, **kwargs) -> Optional[str]:
        """
        导出角色数据为JSON文件
        
        Args:
            export_all: 是否导出所有数据（不分页）
            **kwargs: 其他过滤参数（与get_characters相同）
            
        Returns:
            str: 临时JSON文件路径，失败时返回None
        """
        try:
            # 导入JSON导出器
            try:
                from ..exporter.json_exporter import CBGJSONExporter
            except ImportError:
                from exporter.json_exporter import CBGJSONExporter
            
            # 获取数据库文件路径
            year = kwargs.get('year')
            month = kwargs.get('month')
            year, month = self._validate_year_month(year, month)
            db_file = self._get_db_file(year, month)
            
            if not os.path.exists(db_file):
                return None
            
            # 创建临时输出目录
            temp_dir = tempfile.mkdtemp()
            
            # 创建JSON导出器
            json_exporter = CBGJSONExporter(db_file, temp_dir)
            
            # 生成CBG链接的回调函数
            def generate_cbg_link(equip_id):
                if not equip_id:
                    return None
                try:
                    if '-' in str(equip_id):
                        server_id = str(equip_id).split('-')[1]
                    else:
                        server_id = str(equip_id)[:12]
                    return f"https://xyq.cbg.163.com/equip?s={server_id}&eid={equip_id}"
                except Exception:
                    return None
            
            # 如果需要过滤数据，先获取符合条件的数据
            if any(v is not None for v in kwargs.values() if v != export_all):
                # 有过滤条件，使用现有的查询逻辑获取数据
                filtered_data = self.get_characters_for_export(**kwargs)
                if not filtered_data:
                    return None
                
                # 临时替换JSON导出器的准备数据方法
                original_prepare = json_exporter.prepare_export_data
                json_exporter.prepare_export_data = lambda generate_link_callback=None: filtered_data
            
            # 生成时间戳文件名
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            filename = f'cbg_characters_{year}{month:02d}_{timestamp}.json'
            
            # 执行导出
            json_path = json_exporter.export_to_json(filename, generate_cbg_link, pretty=True)
            
            return json_path
            
        except Exception as e:
            print(f"导出JSON时发生错误: {e}")
            return None
    
    def get_characters_for_export(self, **kwargs) -> List[Dict]:
        """
        获取用于导出的角色数据（不分页），使用JSON导出器的SQL格式
        
        Args:
            **kwargs: 过滤参数
            
        Returns:
            List[Dict]: 角色数据列表
        """
        try:
            year = kwargs.get('year')
            month = kwargs.get('month')
            year, month = self._validate_year_month(year, month)
            db_file = self._get_db_file(year, month)
            
            if not os.path.exists(db_file):
                return []
            
            # 导入JSON导出器以使用其SQL查询
            try:
                from ..exporter.json_exporter import CBGJSONExporter
            except ImportError:
                from exporter.json_exporter import CBGJSONExporter
            
            # 创建临时导出器实例以获取SQL查询
            temp_exporter = CBGJSONExporter(db_file, tempfile.mkdtemp())
            
            # 使用JSON导出器的SQL查询获取数据
            conn = sqlite3.connect(db_file)
            conn.row_factory = sqlite3.Row
            cursor = conn.cursor()
            
            # 构建过滤条件（复用现有逻辑）
            level_conditions = []
            level_params = []
            
            # 等级过滤
            level_min = kwargs.get('level_min')
            level_max = kwargs.get('level_max')
            if level_min is not None:
                level_conditions.append("COALESCE(l.character_level, c.level) >= ?")
                level_params.append(level_min)
            if level_max is not None:
                level_conditions.append("COALESCE(l.character_level, c.level) <= ?")
                level_params.append(level_max)
            
            # 构建完整的WHERE条件
            if level_conditions:
                where_clause = "WHERE " + " AND ".join(level_conditions)
            else:
                where_clause = ""
            
            # 使用JSON导出器的SQL查询，但添加过滤条件
            base_sql = temp_exporter.get_export_data_sql()
            if where_clause:
                # 在ORDER BY之前插入WHERE条件
                sql_parts = base_sql.split("ORDER BY")
                if len(sql_parts) == 2:
                    filtered_sql = sql_parts[0].strip() + " " + where_clause + " ORDER BY " + sql_parts[1]
                else:
                    filtered_sql = base_sql.strip() + " " + where_clause
            else:
                filtered_sql = base_sql
            
            # 执行查询
            cursor.execute(filtered_sql, level_params)
            rows = cursor.fetchall()
            
            # 转换为字典列表
            data_list = [dict(row) for row in rows]
            
            conn.close()
            
            print(f"Debug: 使用JSON导出器SQL查询，获取到 {len(data_list)} 条记录")
            
            return data_list
            
        except Exception as e:
            print(f"获取导出数据时发生错误: {e}")
            import traceback
            traceback.print_exc()
            return []

    def export_single_character_json(self, year: Optional[int] = None, month: Optional[int] = None, equip_id: str = None) -> Optional[str]:
        """
        导出单个角色数据为JSON文件
        
        Args:
            year: 年份
            month: 月份
            equip_id: 角色装备ID
            
        Returns:
            str: 临时JSON文件路径，失败时返回None
        """
        try:
            if not equip_id:
                return None
                
            # 导入JSON导出器
            try:
                from ..exporter.json_exporter import CBGJSONExporter
            except ImportError:
                from exporter.json_exporter import CBGJSONExporter
            
            # 获取数据库文件路径
            year, month = self._validate_year_month(year, month)
            db_file = self._get_db_file(year, month)
            
            if not os.path.exists(db_file):
                return None
            
            # 创建临时输出目录
            temp_dir = tempfile.mkdtemp()
            
            # 使用JSON导出器的SQL查询获取单个角色数据
            conn = sqlite3.connect(db_file)
            conn.row_factory = sqlite3.Row
            cursor = conn.cursor()
            
            # 创建临时导出器实例以获取SQL查询
            temp_exporter = CBGJSONExporter(db_file, temp_dir)
            
            # 获取基础SQL查询并添加equip_id过滤
            base_sql = temp_exporter.get_export_data_sql()
            filtered_sql = base_sql.replace(
                "ORDER BY c.price_desc DESC",
                "WHERE c.equip_id = ? ORDER BY c.price_desc DESC"
            )
            
            # 执行查询
            cursor.execute(filtered_sql, [equip_id])
            row = cursor.fetchone()
            
            if not row:
                conn.close()
                return None
            
            # 转换为字典
            character_data = dict(row)
            conn.close()
            
            # 创建JSON导出器
            json_exporter = CBGJSONExporter(db_file, temp_dir)
            
            # 生成CBG链接的回调函数
            def generate_cbg_link(equip_id):
                if not equip_id:
                    return None
                try:
                    if '-' in str(equip_id):
                        server_id = str(equip_id).split('-')[1]
                    else:
                        server_id = str(equip_id)[:12]
                    return f"https://xyq.cbg.163.com/equip?s={server_id}&eid={equip_id}"
                except Exception:
                    return None
            
            # 格式化单个角色数据
            formatted_data = json_exporter.format_export_data([character_data], generate_cbg_link)
            
            if not formatted_data:
                return None
            
            # 生成文件名
            character_name = character_data.get('角色名', '未知角色')
            server_info = character_data.get('服务器', '').replace('/', '_')
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            
            # 清理文件名中的非法字符
            safe_name = f"{character_name}_{server_info}_{timestamp}".replace('/', '_').replace('\\', '_').replace(':', '_').replace('*', '_').replace('?', '_').replace('"', '_').replace('<', '_').replace('>', '_').replace('|', '_')
            filename = f"{safe_name}.json"
            
            # 保存单个角色数据（只保存角色数据，不包装）
            json_path = os.path.join(temp_dir, filename)
            json_exporter.save_to_json(formatted_data, json_path, pretty=True)
            
            print(f"Debug: 单个角色JSON导出成功: {json_path}")
            return json_path
            
        except Exception as e:
            print(f"导出单个角色JSON时发生错误: {e}")
            import traceback
            traceback.print_exc()
            return None