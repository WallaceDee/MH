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

# 尝试导入估价器相关模块
try:
    from src.evaluator.market_anchor_evaluator import MarketAnchorEvaluator
    from src.evaluator.feature_extractor.feature_extractor import FeatureExtractor
except ImportError as e:
    MarketAnchorEvaluator = None
    FeatureExtractor = None
    logger.warning(f"无法导入角色估价器相关模块: {e}")


class roleService:
    def __init__(self):
        # 获取项目根目录
        self.project_root = get_project_root()
        self.data_dir = get_data_path()

        # 初始化特征提取器
        self.feature_extractor = None
        if FeatureExtractor:
            try:
                self.feature_extractor = FeatureExtractor()
                logger.info("角色特征提取器初始化成功")
            except Exception as e:
                logger.error(f"角色特征提取器初始化失败: {e}")

        # 初始化市场锚定估价器
        self.market_evaluator = None
        if MarketAnchorEvaluator:
            try:
                self.market_evaluator = MarketAnchorEvaluator()
                logger.info("角色市场锚定估价器初始化成功")
            except Exception as e:
                logger.error(f"角色市场锚定估价器初始化失败: {e}")

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

    def update_role_equip_price(self, eid: str, equip_price: float, year: Optional[int] = None, month: Optional[int] = None) -> bool:
        """更新角色的装备估价价格
        
        Args:
            eid: 角色唯一标识符
            equip_price: 装备估价价格（分）
            year: 年份
            month: 月份
            
        Returns:
            bool: 更新是否成功
        """
        try:
            year, month = self._validate_year_month(year, month)
            db_file = self._get_db_file(year, month)
            
            if not os.path.exists(db_file):
                logger.warning(f"数据库文件不存在: {db_file}")
                return False
                
            with sqlite3.connect(db_file) as conn:
                cursor = conn.cursor()
                
                # 更新装备估价价格
                sql = "UPDATE roles SET equip_price = ? WHERE eid = ?"
                cursor.execute(sql, [equip_price, eid])
                
                if cursor.rowcount > 0:
                    logger.info(f"更新角色装备估价价格成功: {eid} = {equip_price}分")
                    return True
                else:
                    logger.warning(f"未找到角色记录: {eid}")
                    return False
                    
        except Exception as e:
            logger.error(f"更新角色装备估价价格失败: {e}")
            return False

    def update_role_pet_price(self, eid: str, pet_price: float, year: Optional[int] = None, month: Optional[int] = None) -> bool:
        """更新角色的宠物估价价格
        
        Args:
            eid: 角色唯一标识符
            pet_price: 宠物估价价格（分）
            year: 年份
            month: 月份
            
        Returns:
            bool: 更新是否成功
        """
        try:
            year, month = self._validate_year_month(year, month)
            db_file = self._get_db_file(year, month)
            
            if not os.path.exists(db_file):
                logger.warning(f"数据库文件不存在: {db_file}")
                return False
                
            with sqlite3.connect(db_file) as conn:
                cursor = conn.cursor()
                
                # 更新宠物估价价格
                sql = "UPDATE roles SET pet_price = ? WHERE eid = ?"
                cursor.execute(sql, [pet_price, eid])
                
                if cursor.rowcount > 0:
                    logger.info(f"更新角色宠物估价价格成功: {eid} = {pet_price}分")
                    return True
                else:
                    logger.warning(f"未找到角色记录: {eid}")
                    return False
                    
        except Exception as e:
            logger.error(f"更新角色宠物估价价格失败: {e}")
            return False

    def update_role_base_price(self, eid: str, base_price: float, year: Optional[int] = None, month: Optional[int] = None) -> bool:
        """更新角色的总估价价格
        
        Args:
            eid: 角色唯一标识符
            base_price: 总估价价格（分）
            year: 年份
            month: 月份
            
        Returns:
            bool: 更新是否成功
        """
        try:
            year, month = self._validate_year_month(year, month)
            db_file = self._get_db_file(year, month)
            
            if not os.path.exists(db_file):
                logger.warning(f"数据库文件不存在: {db_file}")
                return False
                
            with sqlite3.connect(db_file) as conn:
                cursor = conn.cursor()
                
                # 更新裸号估价价格（使用base_price字段）
                sql = "UPDATE roles SET base_price = ? WHERE eid = ?"
                cursor.execute(sql, [base_price, eid])
                
                if cursor.rowcount > 0:
                    logger.info(f"更新角色总估价价格成功: {eid} = {base_price}分")
                    return True
                else:
                    logger.warning(f"未找到角色记录: {eid}")
                    return False
                    
        except Exception as e:
            logger.error(f"更新角色总估价价格失败: {e}")
            return False

    def get_roles(self, page: int = 1, page_size: int = 15, year: Optional[int] = None, 
                  month: Optional[int] = None, level_min: Optional[int] = None, 
                  level_max: Optional[int] = None, sort_by: Optional[str] = None, 
                  sort_order: Optional[str] = None, role_type: str = 'normal',
                  equip_num: Optional[int] = None, pet_num: Optional[int] = None,
                  pet_num_level: Optional[int] = None, accept_bargain: Optional[int] = None) -> Dict:
        """获取角色列表
        
        Args:
            page: 页码
            page_size: 每页数量
            year: 年份
            month: 月份
            level_min: 最小等级
            level_max: 最大等级
            sort_by: 排序字段
            sort_order: 排序方向
            role_type: 角色类型，'normal' 表示正常角色，'empty' 表示空号角色
            equip_num: 物品数量上限（小于等于）
            pet_num: 召唤兽数量上限（小于等于）
            pet_num_level: 召唤兽等级下限（大于）
            accept_bargain: 是否接受还价，1表示接受还价
        """
        return self.get_role_list(
            page=page,
            page_size=page_size,
            year=year,
            month=month,
            level_min=level_min,
            level_max=level_max,
            sort_by=sort_by,
            sort_order=sort_order,
            role_type=role_type,
            equip_num=equip_num,
            pet_num=pet_num,
            pet_num_level=pet_num_level,
            accept_bargain=accept_bargain
        )

    def get_role_list(self, page: int = 1, page_size: int = 15, year: Optional[int] = None, 
                      month: Optional[int] = None, level_min: Optional[int] = None, 
                      level_max: Optional[int] = None, sort_by: Optional[str] = None, 
                      sort_order: Optional[str] = None, role_type: str = 'normal',
                      equip_num: Optional[int] = None, pet_num: Optional[int] = None,
                      pet_num_level: Optional[int] = None, accept_bargain: Optional[int] = None) -> Dict:
        """获取角色列表
        
        Args:
            page: 页码
            page_size: 每页数量
            year: 年份
            month: 月份
            level_min: 最小等级
            level_max: 最大等级
            sort_by: 排序字段
            sort_order: 排序方向
            role_type: 角色类型，'normal' 表示正常角色，'empty' 表示空号角色
            equip_num: 物品数量上限（小于等于）
            pet_num: 召唤兽数量上限（小于等于）
            pet_num_level: 召唤兽等级下限（大于）
            accept_bargain: 是否接受还价，1表示接受还价
        """
        try:
            # 验证页码和每页数量
            if page < 1:
                page = 1
            if page_size < 1 or page_size > 100:
                page_size = 15
                
            # 验证年月
            year, month = self._validate_year_month(year, month)
            
            # 获取数据库文件路径
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
                    
                # 添加接受还价过滤条件
                if accept_bargain is not None:
                    level_conditions.append("c.accept_bargain = ?")
                    level_params.append(accept_bargain)
                
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

                # 构建召唤兽（大于pet_level）物数量小于等于pet_num过滤条件
                if pet_num is not None and pet_num_level is not None:
                    if pet_num == 0:
                        # 当pet_num为0时,表示没有召唤兽
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
                    SELECT l.all_equip_json,l.all_summon_json,l.sum_exp,c.serverid,c.server_name,c.eid,
                    c.seller_nickname,c.level,c.school,c.price,c.accept_bargain,c.history_price,c.dynamic_tags,
                    c.highlight,c.create_time,c.update_time,c.is_split_independent_role,c.is_split_main_role,c.collect_num,
                    c.other_info,c.large_equip_desc,c.split_price_desc,c.base_price,c.equip_price,c.pet_price
                    FROM roles c
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
                    SELECT 
                        c.eid, c.serverid, c.server_name, c.seller_nickname, c.level, c.school,
                        c.price, c.accept_bargain, c.history_price, c.dynamic_tags,
                        c.highlight, c.create_time, c.update_time, c.collect_num,
                        c.other_info, c.base_price, c.equip_price, c.pet_price,
                        c.is_split_independent_role, c.is_split_main_role,
                        c.large_equip_desc, c.split_price_desc,
                        c.yushoushu_skill, c.school_skills, c.life_skills, c.expire_time,
                        l.sum_exp, l.three_fly_lv, l.all_new_point,
                        l.jiyuan_amount, l.packet_page, l.xianyu_amount, l.learn_cash,
                        l.sum_amount, l.role_icon,
                        l.expt_ski1, l.expt_ski2, l.expt_ski3, l.expt_ski4, l.expt_ski5,
                        l.beast_ski1, l.beast_ski2, l.beast_ski3, l.beast_ski4,
                        l.changesch_json, l.ex_avt_json, l.huge_horse_json, l.shenqi_json,
                        l.all_equip_json, l.all_summon_json, l.all_rider_json
                    FROM roles c
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

    def get_role_valuation(self, eid: str, year: Optional[int] = None, month: Optional[int] = None,
                          role_type: str = 'normal', strategy: str = 'fair_value',
                          similarity_threshold: float = 0.7, max_anchors: int = 30) -> Dict:
        """获取角色估价 - 使用市场锚定法"""
        try:
            if not self.market_evaluator:
                return {
                    "error": "角色市场锚定估价器未初始化",
                    "estimated_price": 0,
                    "estimated_price_yuan": 0
                }
            
            if not self.feature_extractor:
                return {
                    "error": "角色特征提取器未初始化",
                    "estimated_price": 0,
                    "estimated_price_yuan": 0
                }
            
            # 先查询角色数据
            role_data = self.get_role_details(eid, year, month, role_type)
            if not role_data:
                return {
                    "error": f"未找到角色 {eid} 的数据",
                    "estimated_price": 0,
                    "estimated_price_yuan": 0
                }
            
            # 使用特征提取器提取特征
            try:
                role_features = self.feature_extractor.extract_features(role_data)
            except Exception as e:
                return {
                    "error": f"特征提取失败: {str(e)}",
                    "estimated_price": 0,
                    "estimated_price_yuan": 0
                }
            
            # 验证策略参数
            valid_strategies = ['fair_value', 'competitive', 'premium']
            if strategy not in valid_strategies:
                return {
                    "error": f"无效的估价策略: {strategy}，有效策略: {', '.join(valid_strategies)}",
                    "estimated_price": 0,
                    "estimated_price_yuan": 0
                }
            
            # 验证相似度阈值和最大锚点数量
            if not 0.0 <= similarity_threshold <= 1.0:
                return {
                    "error": "相似度阈值必须在0.0-1.0之间",
                    "estimated_price": 0,
                    "estimated_price_yuan": 0
                }
            
            if not 1 <= max_anchors <= 100:
                return {
                    "error": "最大锚点数量必须在1-100之间",
                    "estimated_price": 0,
                    "estimated_price_yuan": 0
                }
            
            # 调用市场锚定估价器
            try:
                result = self.market_evaluator.calculate_value(
                    target_features=role_features,
                    strategy=strategy,
                    similarity_threshold=similarity_threshold,
                    max_anchors=max_anchors,
                    verbose=False
                )
                
                # 格式化返回结果
                estimated_price = result.get('estimated_price', 0)
                estimated_price_yuan = estimated_price / 100.0  # 转换为元
                
                # 估价成功后自动更新数据库中的base_price
                if estimated_price > 0:
                    try:
                        update_success = self.update_role_base_price(eid, int(estimated_price), year, month)
                        if update_success:
                            logger.info(f"自动更新角色 {eid} 的估价价格: {estimated_price}分")
                        else:
                            logger.warning(f"自动更新角色 {eid} 的估价价格失败")
                    except Exception as update_error:
                        logger.error(f"自动更新角色 {eid} 估价价格时出错: {update_error}")
                        # 不影响估价结果的返回，只记录错误
                
                return {
                    "estimated_price": int(estimated_price),
                    "estimated_price_yuan": round(estimated_price_yuan, 2),
                    "confidence": result.get('confidence', 0.0),
                    "market_value": int(estimated_price),  # 市场锚定估价即为最终价值
                    "anchor_count": result.get('anchor_count', 0),
                    "feature": role_features,
                    "eid": eid,
                    "strategy": strategy,
                    "similarity_threshold": similarity_threshold,
                    "max_anchors": max_anchors
                }
                
            except Exception as e:
                return {
                    "error": f"估价计算失败: {str(e)}",
                    "estimated_price": 0,
                    "estimated_price_yuan": 0,
                    "feature": role_features,
                    "eid": eid
                }
            
        except Exception as e:
            logger.error(f"获取角色估价时出错: {e}")
            return {
                "error": f"获取角色估价时出错: {str(e)}",
                "estimated_price": 0,
                "estimated_price_yuan": 0
            }

    def find_role_anchors(self, eid: str, year: Optional[int] = None, month: Optional[int] = None,
                         role_type: str = 'normal', similarity_threshold: float = 0.7, max_anchors: int = 30) -> Dict:
        """查找相似角色锚点"""
        try:
            # 先查询角色数据
            role_data = self.get_role_details(eid, year, month, role_type)
            if not role_data:
                return {
                    "error": f"未找到角色 {eid} 的数据",
                    "anchors": [],
                    "anchor_count": 0
                }
            
            # 使用特征提取器提取特征
            try:
                role_features = self.feature_extractor.extract_features(role_data)
            except Exception as e:
                return {
                    "error": f"特征提取失败: {str(e)}",
                    "anchors": [],
                    "anchor_count": 0
                }
            
            # 获取市场锚定评估器
            if not self.market_evaluator:
                return {
                    "error": "市场锚定评估器未初始化",
                    "anchors": [],
                    "anchor_count": 0
                }
            
            market_evaluator = self.market_evaluator
            
            # 查找相似角色锚点
            try:
                anchors = market_evaluator.find_market_anchors(
                    target_features=role_features,
                    similarity_threshold=similarity_threshold,
                    max_anchors=max_anchors,
                    verbose=False
                )
                
                if not anchors:
                    return {
                        "anchors": [],
                        "anchor_count": 0,
                        "statistics": None,
                        "message": "未找到相似角色"
                    }
                
                # 格式化锚点数据中的相似度，保留三位小数并获取完整角色信息
                result_anchors = []
                for anchor in anchors:
                    # 从空号数据库获取完整的角色信息
                    anchor_eid = anchor.get('eid')
                    full_role_info = self.get_role_details(anchor_eid, year, month, role_type='empty')
                    
                    if full_role_info:
                        # 组合锚点信息和完整角色信息
                        anchor_info = {
                            **full_role_info,  # 包含所有角色基础信息
                            'eid': anchor_eid,
                            'similarity': round(float(anchor.get('similarity', 0)), 3),
                            'price': float(anchor.get('price', 0))
                        }
                    else:
                        # 如果无法获取完整信息，使用基础信息
                        anchor_info = {
                            'eid': anchor_eid,
                            'similarity': round(float(anchor.get('similarity', 0)), 3),
                            'price': float(anchor.get('price', 0)),
                            'nickname': '未知角色',
                            'server_name': '未知服务器',
                            'level': 0,
                            'school': '未知门派'
                        }
                    result_anchors.append(anchor_info)
                
                # 计算统计信息
                prices = [anchor.get('price', 0) for anchor in result_anchors]
                similarities = [anchor.get('similarity', 0) for anchor in result_anchors]
                
                statistics = {
                    "price_range": {
                        "min": min(prices) if prices else 0,
                        "max": max(prices) if prices else 0,
                        "avg": sum(prices) / len(prices) if prices else 0
                    },
                    "similarity_range": {
                        "min": round(min(similarities), 3) if similarities else 0,
                        "max": round(max(similarities), 3) if similarities else 0,
                        "avg": round(sum(similarities) / len(similarities), 3) if similarities else 0
                    }
                }
                
                return {
                    "anchors": result_anchors,
                    "anchor_count": len(result_anchors),
                    "statistics": statistics,
                    "similarity_threshold": similarity_threshold,
                    "max_anchors": max_anchors,
                    "target_features": role_features
                }
                
            except Exception as e:
                return {
                    "error": f"查找锚点失败: {str(e)}",
                    "anchors": [],
                    "anchor_count": 0
                }
            
        except Exception as e:
            logger.error(f"查找相似角色锚点时出错: {e}")
            return {
                "error": f"查找相似角色锚点时出错: {str(e)}",
                "anchors": [],
                "anchor_count": 0
            }

    def batch_role_valuation(self, eid_list: List[str], year: Optional[int] = None, month: Optional[int] = None,
                            role_type: str = 'normal', strategy: str = 'fair_value',
                            similarity_threshold: float = 0.7, max_anchors: int = 30, verbose: bool = False) -> Dict:
        """批量角色估价 - 使用市场锚定法"""
        try:
            if not eid_list:
                return {"error": "角色eid列表不能为空"}
            
            if not self.market_evaluator:
                return {"error": "角色市场锚定估价器未初始化"}
            
            if not self.feature_extractor:
                return {"error": "角色特征提取器未初始化"}
            
            results = []
            total_value = 0
            success_count = 0
            error_count = 0
            
            for i, eid in enumerate(eid_list):
                try:
                    if verbose:
                        logger.info(f"正在估价第 {i+1}/{len(eid_list)} 个角色: {eid}")
                    
                    # 单个角色估价
                    result = self.get_role_valuation(
                        eid=eid,
                        year=year,
                        month=month,
                        role_type=role_type,
                        strategy=strategy,
                        similarity_threshold=similarity_threshold,
                        max_anchors=max_anchors
                    )
                    
                    if "error" not in result:
                        success_count += 1
                        total_value += result.get("estimated_price", 0)
                        results.append({
                            "index": i,
                            "eid": eid,
                            "success": True,
                            "data": result
                        })
                    else:
                        error_count += 1
                        results.append({
                            "index": i,
                            "eid": eid,
                            "success": False,
                            "error": result.get("error", "估价失败"),
                            "data": result
                        })
                        
                except Exception as e:
                    error_count += 1
                    logger.error(f"第 {i+1} 个角色 {eid} 估价失败: {e}")
                    results.append({
                        "index": i,
                        "eid": eid,
                        "success": False,
                        "error": f"估价异常: {str(e)}",
                        "data": None
                    })
            
            # 构建返回结果
            return {
                "total_roles": len(eid_list),
                "success_count": success_count,
                "error_count": error_count,
                "total_value": total_value,
                "total_value_yuan": round(total_value / 100.0, 2),
                "strategy": strategy,
                "similarity_threshold": similarity_threshold,
                "max_anchors": max_anchors,
                "results": results
            }
            
        except Exception as e:
            logger.error(f"批量角色估价失败: {e}")
            return {
                "error": f"批量角色估价失败: {str(e)}",
                "total_roles": len(eid_list) if 'eid_list' in locals() else 0,
                "success_count": 0,
                "error_count": len(eid_list) if 'eid_list' in locals() else 0,
                "total_value": 0,
                "total_value_yuan": 0,
                "results": []
            }
