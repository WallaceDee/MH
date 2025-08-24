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

    def _get_db_file(self, year: Optional[int] = None, month: Optional[int] = None, role_type: str = 'normal') -> str:
        """获取指定年月的数据库文件路径
        
        Args:
            year: 年份
            month: 月份  
            role_type: 角色类型，'normal' 表示正常角色，'empty' 表示空号角色
        """
        year, month = self._validate_year_month(year, month)
        
        if role_type == 'empty':
            db_filename = f'cbg_empty_roles_{year}{month:02d}.db'
        else:
            db_filename = f'cbg_roles_{year}{month:02d}.db'
            
        return os.path.join(self.data_dir, f'{year}{month:02d}', db_filename)

    def get_roles(self, page: int = 1, page_size: int = 10, year: Optional[int] = None, month: Optional[int] = None,
                  level_min: Optional[int] = None, level_max: Optional[int] = None,
                  # 其他参数
                  equip_num: Optional[int] = None, pet_num: Optional[int] = None,
                  pet_num_level: Optional[int] = None,
                  # 排序参数
                  sort_by: Optional[str] = None, sort_order: Optional[str] = None,
                  # 角色类型参数
                  role_type: str = 'normal') -> Dict:
        """获取分页的角色列表
        
        Args:
            page: 页码
            page_size: 每页大小
            year: 年份
            month: 月份
            level_min: 最低等级
            level_max: 最高等级
            equip_num: 装备数量限制
            pet_num: 宠物数量限制
            pet_num_level: 宠物等级限制
            sort_by: 排序字段
            sort_order: 排序方向
            role_type: 角色类型，'normal' 表示正常角色，'empty' 表示空号角色
        """
        try:
            # 验证年月
            year, month = self._validate_year_month(year, month)
            db_file = self._get_db_file(year, month, role_type)

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

                # 根据all_equip_json构建物品数量小于等于过滤条件
                if equip_num is not None:
                    if equip_num == 0:
                        # 当equip_num为0时,表示没有物品
                        level_conditions.append(
                            "(l.all_equip_json IS NULL OR l.all_equip_json = '' OR l.all_equip_json = '{}')")
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
                        level_conditions.append(
                            "(l.all_summon_json IS NULL OR l.all_summon_json = '[]')")
                    else:
                        level_conditions.append("""
                            (SELECT COUNT(*) FROM json_each(l.all_summon_json) 
                            WHERE CAST(json_extract(value, '$.iGrade') AS INTEGER) > ?) <= ?
                        """)
                        level_params.extend([pet_num_level, pet_num])

                level_where = " AND ".join(
                    level_conditions) if level_conditions else "1=1"

                # 获取总记录数
                count_query = f"SELECT COUNT(*) FROM roles c LEFT JOIN large_equip_desc_data l ON c.eid = l.eid WHERE {level_where}"
                cursor.execute(count_query, level_params)
                total = cursor.fetchone()[0]

                # 计算分页
                total_pages = (total + page_size - 1) // page_size
                offset = (page - 1) * page_size

                # 构建排序条件
                order_by = "c.update_time DESC"  # 默认按更新时间倒序，最近更新的在最前
                if sort_by and sort_order:
                    # 验证排序字段
                    allowed_sort_by = [
                        'highlight', 'dynamic_tags', 'price', 'level', 'collect_num',
                        'create_time', 'update_time', 'accept_bargain', 'history_price'
                    ]

                    # 解析排序参数
                    sort_fields = sort_by.split(',')
                    sort_orders = sort_order.split(',')

                    # 构建排序条件
                    order_conditions = []
                    for field, order in zip(sort_fields, sort_orders):
                        if field in allowed_sort_by and order.lower() in ['asc', 'desc']:
                            # 根据字段名确定表别名
                            order_conditions.append(f"c.{field} {order}")

                    if order_conditions:
                        order_by = ", ".join(order_conditions)

                # 为了解决字段名冲突，明确列出所有字段并为冲突字段使用别名
                query = f"""
                    SELECT l.all_equip_json,l.all_summon_json,l.sum_exp,c.serverid,c.server_name,c.eid,c.seller_nickname,c.level,c.school,c.price,c.accept_bargain,c.history_price,c.dynamic_tags,c.highlight,c.create_time,c.update_time,c.is_split_independent_role,c.is_split_main_role,c.collect_num,c.other_info,c.large_equip_desc FROM roles c
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

    def get_role_details(self, eid: str, year: Optional[int] = None, month: Optional[int] = None, role_type: str = 'normal') -> Optional[Dict]:
        """获取单个角色的详细信息
        
        Args:
            eid: 角色ID
            year: 年份
            month: 月份
            role_type: 角色类型，'normal' 表示正常角色，'empty' 表示空号角色
        """
        try:
            if not eid:
                return None

            year, month = self._validate_year_month(year, month)
            db_file = self._get_db_file(year, month, role_type)

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

    def get_role_feature(self, eid: str, year: Optional[int] = None, month: Optional[int] = None, role_type: str = 'normal') -> Optional[Dict]:
        """获取角色详情并提取特征
        
        Args:
            eid: 角色ID
            year: 年份
            month: 月份
            role_type: 角色类型，'normal' 表示正常角色，'empty' 表示空号角色
        """
        try:
            # 先获取角色基础数据
            role_data = self.get_role_details(eid, year, month, role_type)
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

    def delete_role(self, eid: str, year: Optional[int] = None, month: Optional[int] = None, role_type: str = 'normal') -> Dict:
        """删除指定角色
        
        Args:
            eid: 角色ID
            year: 年份
            month: 月份
            role_type: 角色类型，'normal' 表示正常角色，'empty' 表示空号角色
            
        Returns:
            Dict: 包含删除结果的字典
        """
        try:
            if not eid:
                return {"error": "角色eid不能为空"}

            # 验证年月
            year, month = self._validate_year_month(year, month)
            db_file = self._get_db_file(year, month, role_type)

            if not os.path.exists(db_file):
                return {"error": f"未找到 {year}年{month}月 的数据文件"}

            with sqlite3.connect(db_file) as conn:
                cursor = conn.cursor()
                
                # 首先检查角色是否存在
                cursor.execute("SELECT COUNT(*) FROM roles WHERE eid = ?", (eid,))
                role_exists = cursor.fetchone()[0]
                
                if role_exists == 0:
                    return {"error": "未找到指定的角色"}
                
                # 删除角色相关的装备数据
                cursor.execute("DELETE FROM large_equip_desc_data WHERE eid = ?", (eid,))
                equip_deleted = cursor.rowcount
                
                # 删除角色数据
                cursor.execute("DELETE FROM roles WHERE eid = ?", (eid,))
                role_deleted = cursor.rowcount
                
                # 提交事务
                conn.commit()
                
                logger.info(f"成功删除角色 {eid}，删除了 {role_deleted} 条角色记录和 {equip_deleted} 条装备记录")
                
                return {
                    "success": True,
                    "eid": eid,
                    "role_deleted": role_deleted,
                    "equip_deleted": equip_deleted,
                    "message": f"成功删除角色 {eid}",
                    "year": year,
                    "month": month
                }

        except Exception as e:
            logger.error(f"删除角色时出错: {e}")
            return {"error": f"删除角色时出错: {str(e)}"}

    def switch_role_type(self, eid: str, year: Optional[int] = None, month: Optional[int] = None, 
                        current_role_type: str = 'normal', target_role_type: str = 'normal') -> Dict:
        """切换角色类型（数据迁移）
        TODO: 需要优化，目前只支持normal和empty两种角色类型
        Args:
            eid: 角色ID
            year: 年份
            month: 月份
            current_role_type: 当前角色类型
            target_role_type: 目标角色类型
            
        Returns:
            Dict: 包含迁移结果的字典
        """
        try:
            if not eid:
                return {"error": "角色eid不能为空"}

            # 验证年月
            year, month = self._validate_year_month(year, month)
            
            # 获取源数据库和目标数据库文件路径
            source_db_file = self._get_db_file(year, month, current_role_type)
            target_db_file = self._get_db_file(year, month, target_role_type)
            
            # 检查源数据库是否存在
            if not os.path.exists(source_db_file):
                return {"error": f"未找到源数据库文件: {source_db_file}"}
            
            # 确保目标数据库目录存在
            target_db_dir = os.path.dirname(target_db_file)
            os.makedirs(target_db_dir, exist_ok=True)
            
            # 执行数据迁移
            with sqlite3.connect(source_db_file) as source_conn, \
                 sqlite3.connect(target_db_file) as target_conn:
                
                source_cursor = source_conn.cursor()
                target_cursor = target_conn.cursor()
                
                # 开始事务
                source_conn.execute("BEGIN TRANSACTION")
                target_conn.execute("BEGIN TRANSACTION")
                
                try:
                    # 1. 从源数据库读取角色数据
                    source_cursor.execute("SELECT * FROM roles WHERE eid = ?", (eid,))
                    role_data = source_cursor.fetchone()
                    
                    if not role_data:
                        return {"error": "在源数据库中未找到指定的角色"}
                    
                    # 2. 从源数据库读取装备数据
                    source_cursor.execute("SELECT * FROM large_equip_desc_data WHERE eid = ?", (eid,))
                    equip_data = source_cursor.fetchall()
                    
                    # 3. 检查目标数据库中是否已存在该角色
                    target_cursor.execute("SELECT COUNT(*) FROM roles WHERE eid = ?", (eid,))
                    if target_cursor.fetchone()[0] > 0:
                        return {"error": "目标数据库中已存在该角色，无法迁移"}
                    
                    # 4. 插入数据到目标数据库
                    # 获取表结构信息
                    source_cursor.execute("PRAGMA table_info(roles)")
                    roles_columns = [col[1] for col in source_cursor.fetchall()]
                    
                    source_cursor.execute("PRAGMA table_info(large_equip_desc_data)")
                    equip_columns = [col[1] for col in source_cursor.fetchall()]
                    
                    # 构建动态的INSERT语句
                    roles_placeholders = ', '.join(['?' for _ in roles_columns])
                    roles_columns_str = ', '.join(roles_columns)
                    
                    equip_placeholders = ', '.join(['?' for _ in equip_columns])
                    equip_columns_str = ', '.join(equip_columns)
                    
                    # 插入角色数据 - 使用动态字段
                    target_cursor.execute(f"""
                        INSERT INTO roles ({roles_columns_str}) 
                        VALUES ({roles_placeholders})
                    """, role_data)
                    
                    # 插入装备数据 - 使用动态字段
                    for equip_row in equip_data:
                        target_cursor.execute(f"""
                            INSERT INTO large_equip_desc_data ({equip_columns_str}) 
                            VALUES ({equip_placeholders})
                        """, equip_row)
                    
                    # 5. 从源数据库中删除数据
                    source_cursor.execute("DELETE FROM large_equip_desc_data WHERE eid = ?", (eid,))
                    source_cursor.execute("DELETE FROM roles WHERE eid = ?", (eid,))
                    
                    # 提交事务
                    source_conn.commit()
                    target_conn.commit()
                    
                    logger.info(f"成功将角色 {eid} 从 {current_role_type} 迁移到 {target_role_type}")
                    
                    return {
                        "success": True,
                        "eid": eid,
                        "current_role_type": current_role_type,
                        "target_role_type": target_role_type,
                        "role_migrated": True,
                        "equip_migrated": len(equip_data),
                        "message": f"成功将角色 {eid} 从 {current_role_type} 迁移到 {target_role_type}",
                        "year": year,
                        "month": month
                    }
                    
                except Exception as e:
                    # 回滚事务
                    source_conn.rollback()
                    target_conn.rollback()
                    raise e

        except Exception as e:
            logger.error(f"切换角色类型时出错: {e}")
            return {"error": f"切换角色类型时出错: {str(e)}"}
