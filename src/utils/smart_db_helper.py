#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
智能数据库操作助手
专门解决 "values跟columns不一致" 的问题
支持MySQL数据库

冲突处理模式说明：
- REPLACE: 完全替换记录（删除旧记录，插入新记录）
- IGNORE: 忽略新数据，保留现有记录
- UPDATE: 更新现有记录，但保留create_time字段
"""

import json
import logging
from typing import Dict, List, Any, Optional, Union
from datetime import datetime
from sqlalchemy import create_engine, text, MetaData, Table, Column, String, Integer, Text, DateTime, Float
from sqlalchemy.orm import sessionmaker
from sqlalchemy.exc import SQLAlchemyError

class SmartDBHelper:
    """智能数据库操作助手 - MySQL版本"""
    
    def __init__(self, db_url: str):
        self.db_url = db_url
        self.engine = create_engine(
            db_url, 
            pool_pre_ping=True, 
            pool_recycle=3600, 
            echo=False
        )
        self.Session = sessionmaker(bind=self.engine)
        self.logger = self._setup_logger()
        
    def _setup_logger(self):
        """设置日志"""
        logger = logging.getLogger('SmartDBHelper')
        logger.setLevel(logging.INFO)
        
        if not logger.handlers:
            handler = logging.StreamHandler()
            formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
            handler.setFormatter(formatter)
            logger.addHandler(handler)
        
        return logger
    
    def get_connection(self):
        """获取数据库连接"""
        return self.engine.connect()
    
    def get_session(self):
        """获取数据库会话"""
        return self.Session()
    
    def get_table_columns(self, table_name: str) -> List[str]:
        """获取表的所有列名"""
        try:
            with self.get_connection() as conn:
                # 使用MySQL的INFORMATION_SCHEMA查询列信息，包含主键
                query = text("""
                    SELECT COLUMN_NAME 
                    FROM INFORMATION_SCHEMA.COLUMNS 
                    WHERE TABLE_SCHEMA = DATABASE() 
                    AND TABLE_NAME = :table_name 
                    ORDER BY ORDINAL_POSITION
                """)
                result = conn.execute(query, {'table_name': table_name})
                columns = [row[0] for row in result.fetchall()]
                return columns
        except Exception as e:
            self.logger.error(f"获取表{table_name}列名失败: {e}")
            return []
    
    def get_field_type(self, field_name: str, table_name: str = 'large_equip_desc_data') -> str:
        """获取字段类型（已废弃，使用get_table_field_types）"""
        # 为了向后兼容，调用新的方法
        field_types = self.get_table_field_types(table_name)
        return field_types.get(field_name, 'TEXT')
    
    def get_table_field_types(self, table_name: str) -> Dict[str, str]:
        """一次性获取表的所有字段类型，提高性能"""
        cache_key = f"field_types_{table_name}"
        
        # 检查缓存
        if hasattr(self, '_field_types_cache') and cache_key in self._field_types_cache:
            return self._field_types_cache[cache_key]
        
        if not hasattr(self, '_field_types_cache'):
            self._field_types_cache = {}
        
        try:
            with self.get_connection() as conn:
                query = text("""
                    SELECT COLUMN_NAME, DATA_TYPE 
                    FROM INFORMATION_SCHEMA.COLUMNS 
                    WHERE TABLE_SCHEMA = DATABASE() 
                    AND TABLE_NAME = :table_name
                """)
                result = conn.execute(query, {'table_name': table_name})
                
                field_types = {}
                for row in result.fetchall():
                    field_types[row[0]] = row[1].upper()
                
                # 缓存结果
                self._field_types_cache[cache_key] = field_types
                return field_types
                
        except Exception as e:
            self.logger.error(f"获取表 {table_name} 字段类型失败: {e}")
            return {}
    
    def validate_data_types(self, data: Dict[str, Any], table_name: str = 'large_equip_desc_data') -> Dict[str, Any]:
        """验证并转换数据类型 - 简化版本，基于字段名推断类型"""
        validated_data = {}
        
        # 定义常见的数字字段模式
        integer_fields = {
            'id', 'serverid', 'level', 'price', 'equip_level', 'equip_type', 
            'seller_roleid', 'time_lock_days', 'role_level', 'role_school', 'role_icon',
            'hp_max', 'mp_max', 'att_all', 'def_all', 'spe_all', 'mag_all', 
            'damage_all', 'mag_dam_all', 'mag_def_all', 'dod_all', 'cor_all',
            'str_all', 'res_all', 'dex_all', 'up_exp', 'sum_exp',
            'expt_ski1', 'expt_ski2', 'expt_ski3', 'expt_ski4', 'expt_ski5',
            'max_expt1', 'max_expt2', 'max_expt3', 'max_expt4',
            'beast_ski1', 'beast_ski2', 'beast_ski3', 'beast_ski4',
            'all_new_point', 'skill_point', 'attribute_point', 'potential', 'max_potential',
            'cash', 'saving', 'learn_cash', 'zhuan_zhi', 'three_fly_lv', 
            'nine_fight_level', 'goodness', 'yushoushu_skill'
        }
        
        # 定义布尔字段模式  
        boolean_fields = {
            'accept_bargain', 'pass_fair_show', 'has_collect', 'allow_cross_buy',
            'joined_seller_activity', 'is_split_sale', 'is_split_main_role',
            'is_split_independent_role', 'is_split_independent_equip',
            'split_equip_sold_happen', 'show_split_equip_sold_remind',
            'is_onsale_protection_period', 'is_vip_protection', 'is_time_lock',
            'equip_in_test_server', 'buyer_in_test_server',
            'equip_in_allow_take_away_server', 'is_weijianding',
            'is_show_alipay_privilege', 'is_seller_redpacket_flag',
            'is_show_expert_desc', 'is_show_special_highlight',
            'is_xyq_game_role_kunpeng_reach_limit'
        }
        
        for key, value in data.items():
            if value is None:
                validated_data[key] = value
                continue
            
            # 基于字段名推断类型并转换
            if key in integer_fields:
                try:
                    validated_data[key] = int(float(value)) if value != '' else 0
                except (ValueError, TypeError):
                    validated_data[key] = 0
            elif key in boolean_fields:
                # 处理布尔值
                if isinstance(value, bool):
                    validated_data[key] = value
                elif isinstance(value, (int, float)):
                    validated_data[key] = bool(value) if value not in [-1, 0] else (None if value == -1 else False)
                else:
                    validated_data[key] = bool(value) if value else False
            else:
                # 字符串字段直接使用
                validated_data[key] = str(value) if value is not None else ''
        
        return validated_data
    
    def build_insert_sql(self, table_name: str, data: Dict[str, Any], 
                        on_conflict: str = "REPLACE") -> tuple:
        """构建INSERT SQL语句 - MySQL版本"""
        # 验证数据类型，传递正确的表名
        validated_data = self.validate_data_types(data, table_name)
        
        # 获取表的列名
        table_columns = self.get_table_columns(table_name)
        
        # 添加调试信息
        self.logger.debug(f"表 {table_name} 的列名: {table_columns}")
        self.logger.debug(f"输入数据的字段: {list(validated_data.keys())}")
        
        # 只使用表中实际存在的列
        filtered_data = {k: v for k, v in validated_data.items() if k in table_columns}
        
        # 添加详细的调试信息
        if not filtered_data:
            self.logger.error(f"没有有效的列数据可插入到表 {table_name}")
            self.logger.error(f"表 {table_name} 的列名: {table_columns}")
            self.logger.error(f"输入数据的字段: {list(validated_data.keys())}")
            
            # 找出不匹配的字段
            missing_fields = [k for k in validated_data.keys() if k not in table_columns]
            extra_fields = [k for k in table_columns if k not in validated_data.keys() and k != 'id']
            
            if missing_fields:
                self.logger.error(f"输入数据中存在但表中不存在的字段: {missing_fields}")
            if extra_fields:
                self.logger.error(f"表中存在但输入数据中没有的字段: {extra_fields}")
            
            raise ValueError(f"没有有效的列数据可插入到表 {table_name}")
        
        # 构建SQL语句，对保留关键字使用反引号
        columns = list(filtered_data.keys())
        # 对MySQL保留关键字使用反引号包围
        mysql_reserved_words = {
            'desc', 'order', 'group', 'select', 'from', 'where', 'insert', 'update', 'delete',
            'create', 'drop', 'alter', 'table', 'index', 'database', 'schema', 'user', 'password',
            'primary', 'key', 'foreign', 'references', 'constraint', 'check', 'default', 'null',
            'not', 'and', 'or', 'in', 'like', 'between', 'is', 'as', 'distinct', 'union', 'join',
            'inner', 'left', 'right', 'outer', 'on', 'having', 'limit', 'offset', 'asc', 'desc'
        }
        
        # 对列名进行转义处理
        escaped_columns = []
        for col in columns:
            if col.lower() in mysql_reserved_words:
                escaped_columns.append(f'`{col}`')
            else:
                escaped_columns.append(col)
        
        placeholders = [f':{col}' for col in columns]  # MySQL使用命名占位符
        values = filtered_data
        
        # 根据冲突处理方式选择INSERT语句类型
        if on_conflict == "REPLACE":
            # MySQL使用REPLACE INTO
            sql = f"REPLACE INTO {table_name} ({', '.join(escaped_columns)}) VALUES ({', '.join(placeholders)})"
        elif on_conflict == "IGNORE":
            # MySQL使用INSERT IGNORE
            sql = f"INSERT IGNORE INTO {table_name} ({', '.join(escaped_columns)}) VALUES ({', '.join(placeholders)})"
        elif on_conflict == "UPDATE":
            # 构建UPDATE冲突处理，保留create_time
            update_columns = [col for col in columns if col != 'create_time']
            if update_columns:
                # 对更新字段也进行转义处理
                escaped_update_columns = []
                for col in update_columns:
                    if col.lower() in mysql_reserved_words:
                        escaped_update_columns.append(f"`{col}` = VALUES(`{col}`)")
                    else:
                        escaped_update_columns.append(f"{col} = VALUES({col})")
                
                set_clause = ', '.join(escaped_update_columns)
                
                # 根据表名确定主键列名
                if table_name == 'roles':
                    conflict_column = 'eid'
                elif table_name == 'equipments':
                    conflict_column = 'equip_sn'
                elif table_name == 'pets':
                    conflict_column = 'equip_sn'
                elif table_name == 'large_equip_desc_data':
                    conflict_column = 'eid'
                else:
                    # 默认使用第一个字段作为主键
                    conflict_column = columns[0] if columns else 'id'
                
                sql = f"INSERT INTO {table_name} ({', '.join(escaped_columns)}) VALUES ({', '.join(placeholders)}) ON DUPLICATE KEY UPDATE {set_clause}"
            else:
                # 如果没有可更新的字段，使用IGNORE
                sql = f"INSERT IGNORE INTO {table_name} ({', '.join(escaped_columns)}) VALUES ({', '.join(placeholders)})"
        else:
            sql = f"INSERT INTO {table_name} ({', '.join(escaped_columns)}) VALUES ({', '.join(placeholders)})"
        
        return sql, values
    
    def insert_data(self, table_name: str, data: Union[Dict[str, Any], List[Dict[str, Any]]], 
                   on_conflict: str = "REPLACE") -> bool:
        """插入数据 - MySQL版本，使用事务确保数据一致性"""
        try:
            self.logger.debug(f"开始插入数据到表 {table_name}，数据类型: {type(data)}")
            
            with self.get_connection() as conn:
                self.logger.debug("获取数据库连接成功")
                
                # 开始事务
                trans = conn.begin()
                self.logger.debug("事务开始")
                
                try:
                    if isinstance(data, dict):
                        # 单条数据
                        self.logger.debug("处理单条数据...")
                        sql, params = self.build_insert_sql(table_name, data, on_conflict)
                        result = conn.execute(text(sql), params)
                        
                        # 检查是否实际插入了数据
                        if on_conflict == "IGNORE" and result.rowcount == 0:
                            self.logger.debug(f"数据已存在，跳过插入到表 {table_name}")
                            trans.rollback()
                            return False  # 返回False表示没有插入新数据
                        else:
                            trans.commit()  # 提交事务
                            self.logger.debug(f"单条数据已提交到表 {table_name}")
                            return True
                        
                    elif isinstance(data, list):
                        # 批量数据
                        self.logger.debug(f"处理批量数据，共 {len(data)} 条...")
                        
                        if not data:
                            self.logger.warning("数据列表为空，没有数据可插入")
                            trans.rollback()
                            return True
                        
                        # 使用第一条数据构建SQL模板
                        self.logger.debug("构建SQL模板...")
                        sql_template, _ = self.build_insert_sql(table_name, data[0], on_conflict)
                        self.logger.debug(f"SQL模板: {sql_template[:200]}...")
                        
                        # 获取表的列名（基于第一条数据）
                        self.logger.debug("获取表列名...")
                        table_columns = self.get_table_columns(table_name)
                        self.logger.debug(f"表 {table_name} 列数: {len(table_columns)}")
                        
                        self.logger.debug("验证第一条数据类型...")
                        first_data = self.validate_data_types(data[0], table_name)
                        columns = [k for k in first_data.keys() if k in table_columns]
                        self.logger.debug(f"有效列数: {len(columns)}")
                        
                        # 为所有数据构建参数列表
                        self.logger.debug("构建参数列表...")
                        all_params = []
                        for item in data:
                            validated_item = self.validate_data_types(item, table_name)
                            # 按照相同的列顺序提取值
                            params = {col: validated_item.get(col) for col in columns}
                            all_params.append(params)
                        
                        self.logger.debug(f"参数列表构建完成，共 {len(all_params)} 条")
                        
                        # 批量执行
                        self.logger.debug("开始执行批量插入...")
                        result = conn.execute(text(sql_template), all_params)
                        inserted_count = result.rowcount
                        self.logger.debug(f"批量插入执行完成，影响行数: {inserted_count}")
                        
                        if on_conflict == "IGNORE" and inserted_count < len(data):
                            self.logger.info(f"批量插入{inserted_count}/{len(data)}条数据到表 {table_name} (部分数据已存在)")
                        else:
                            self.logger.info(f"成功批量插入{inserted_count}条数据到表 {table_name}")
                        
                        self.logger.debug("开始提交事务...")
                        trans.commit()  # 提交事务
                        self.logger.debug(f"批量数据已提交到表 {table_name}")
                        return True
                        
                except Exception as e:
                    # 发生异常时回滚事务
                    self.logger.debug("发生异常，开始回滚事务...")
                    trans.rollback()
                    self.logger.error(f"插入数据到表 {table_name} 时发生异常，已回滚: {e}")
                    raise e
                
        except SQLAlchemyError as e:
            self.logger.error(f"插入数据到表 {table_name} 失败: {e}")
            return False

class CBGSmartDB:
    """CBG爬虫专用智能数据库管理器 - MySQL版本"""
    
    def __init__(self, db_url: str):
        self.db_helper = SmartDBHelper(db_url)
        self.logger = logging.getLogger('CBGSmartDB')
    
    def save_role(self, role_data: Dict[str, Any]) -> bool:
        """智能保存角色数据，冲突时保留create_time并记录价格变化"""
        # 添加更新时间，使用MySQL标准格式
        role_data['update_time'] = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        
        # 确保有create_time字段
        if 'create_time' not in role_data:
            role_data['create_time'] = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        
        # 检查是否存在冲突，如果存在则处理价格历史
        if self._should_update_price_history(role_data):
            return self._save_role_with_price_history(role_data)
        else:
            # 使用REPLACE冲突处理，简单有效
            return self.db_helper.insert_data('roles', role_data, on_conflict="UPDATE")
    
    def _should_update_price_history(self, role_data: Dict[str, Any]) -> bool:
        """检查是否需要更新价格历史"""
        eid = role_data.get('eid')
        current_price = role_data.get('price')
        
        if not eid or current_price is None:
            return False
        
        try:
            with self.db_helper.get_connection() as conn:
                query = text("SELECT price, history_price FROM roles WHERE eid = :eid")
                result = conn.execute(query, {'eid': eid}).fetchone()
                
                if result:
                    old_price, history_price_json = result
                    # 如果价格没有变化，不需要更新历史
                    if old_price == current_price:
                        return False
                    return True
                else:
                    # 新记录，不需要更新历史
                    return False
        except Exception as e:
            self.logger.error(f"检查价格历史失败: {e}")
            return False
    
    def _save_role_with_price_history(self, role_data: Dict[str, Any]) -> bool:
        """保存角色数据并更新价格历史"""
        eid = role_data.get('eid')
        current_price = role_data.get('price')
        current_time = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        
        try:
            with self.db_helper.get_connection() as conn:
                # 开始事务
                trans = conn.begin()
                try:
                    # 获取现有数据
                    query = text("SELECT price, history_price FROM roles WHERE eid = :eid")
                    result = conn.execute(query, {'eid': eid}).fetchone()
                    
                    if result:
                        old_price, history_price_json = result
                        
                        # 解析现有的价格历史
                        try:
                            if history_price_json and history_price_json != '[]':
                                history_list = json.loads(history_price_json)
                            else:
                                history_list = []
                        except (json.JSONDecodeError, TypeError):
                            history_list = []
                        
                        # 添加新的价格记录
                        new_price_record = {
                            'price': old_price,
                            'timestamp': current_time,
                            'action': 'price_change'
                        }
                        history_list.append(new_price_record)
                        
                        # 限制历史记录数量，保留最近100条
                        if len(history_list) > 100:
                            history_list = history_list[-100:]
                        
                        # 更新role_data中的history_price
                        role_data['history_price'] = json.dumps(history_list, ensure_ascii=False)
                        
                        self.logger.info(f"角色 {eid} 价格从 {old_price} 变更为 {current_price}，已记录到价格历史")
                    
                    # 构建并执行UPDATE语句
                    sql, params = self.db_helper.build_insert_sql('roles', role_data, "UPDATE")
                    result = conn.execute(text(sql), params)
                    
                    trans.commit()  # 提交事务
                    self.logger.debug(f"角色价格历史数据已提交到表 roles")
                    return True
                    
                except Exception as e:
                    # 发生异常时回滚事务
                    trans.rollback()
                    self.logger.error(f"保存角色价格历史时发生异常，已回滚: {e}")
                    raise e
                
        except Exception as e:
            self.logger.error(f"保存角色价格历史失败: {e}")
            # 如果更新历史失败，回退到普通保存
            return self.db_helper.insert_data('roles', role_data, on_conflict="UPDATE")
    
    def save_roles_batch(self, roles_list: List[Dict[str, Any]]) -> bool:
        """批量保存角色数据 - 使用ORM方式"""
        if not roles_list:
            self.logger.debug("角色列表为空，跳过保存")
            return True
        
        self.logger.info(f"开始批量保存 {len(roles_list)} 条角色数据 (ORM方式)...")
        
        try:
            from src.models.role import Role
            from sqlalchemy.orm import sessionmaker
            from sqlalchemy import inspect
            
            # 获取Role模型的所有列名
            inspector = inspect(Role)
            valid_columns = set(column.key for column in inspector.columns)
            
            # 创建Session
            Session = sessionmaker(bind=self.db_helper.engine)
            session = Session()
            
            try:
                # 为所有记录添加时间戳
                timestamp = datetime.now()
                
                # 批量创建ORM对象
                role_objects = []
                for role_data in roles_list:
                    # 过滤掉不存在的字段
                    filtered_data = {}
                    invalid_fields = []
                    
                    for key, value in role_data.items():
                        if key in valid_columns:
                            filtered_data[key] = value
                        else:
                            invalid_fields.append(key)
                    
                    if invalid_fields:
                        self.logger.debug(f"过滤掉无效字段: {invalid_fields}")
                    
                    # 添加时间戳
                    filtered_data['update_time'] = timestamp
                    if 'create_time' not in filtered_data:
                        filtered_data['create_time'] = timestamp
                    
                    # 创建Role对象，ORM会自动处理数据类型转换
                    role_obj = Role(**filtered_data)
                    role_objects.append(role_obj)
                
                # 批量插入/更新
                for role_obj in role_objects:
                    session.merge(role_obj)  # merge会自动处理插入/更新
                
                # 提交事务
                session.commit()
                
                self.logger.info(f"ORM批量保存角色数据成功: {len(roles_list)} 条")
                return True
                
            except Exception as e:
                session.rollback()
                self.logger.error(f"ORM批量保存失败，已回滚: {e}")
                raise e
            finally:
                session.close()
                
        except Exception as e:
            self.logger.error(f"ORM批量保存角色数据时发生异常: {e}")
            return False
    
    def save_large_equip_data(self, equip_data: Dict[str, Any]) -> bool:
        """智能保存详细装备数据，冲突时保留create_time"""
        # 添加更新时间，使用MySQL标准格式
        equip_data['update_time'] = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        equip_data['create_time'] = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        return self.db_helper.insert_data('large_equip_desc_data', equip_data, on_conflict="UPDATE")
    
    def save_large_equip_batch(self, equip_list: List[Dict[str, Any]]) -> bool:
        """批量保存详细装备数据 - 使用ORM方式"""
        if not equip_list:
            return True
        
        self.logger.info(f"开始批量保存 {len(equip_list)} 条详细装备数据 (ORM方式)...")
        
        try:
            from src.models.role import LargeEquipDescData
            from sqlalchemy.orm import sessionmaker
            from sqlalchemy import inspect
            
            # 获取LargeEquipDescData模型的所有列名
            inspector = inspect(LargeEquipDescData)
            valid_columns = set(column.key for column in inspector.columns)
            
            # 创建Session
            Session = sessionmaker(bind=self.db_helper.engine)
            session = Session()
            
            try:
                # 为所有记录添加时间戳
                timestamp = datetime.now()
                
                # 批量创建ORM对象
                equip_objects = []
                for equip_data in equip_list:
                    # 过滤掉不存在的字段
                    filtered_data = {}
                    invalid_fields = []
                    
                    for key, value in equip_data.items():
                        if key in valid_columns:
                            filtered_data[key] = value
                        else:
                            invalid_fields.append(key)
                    
                    if invalid_fields:
                        self.logger.debug(f"过滤掉无效字段: {invalid_fields}")
                    
                    # 添加时间戳
                    filtered_data['update_time'] = timestamp
                    filtered_data['create_time'] = timestamp
                    
                    # 创建LargeEquipDescData对象，ORM会自动处理数据类型转换
                    equip_obj = LargeEquipDescData(**filtered_data)
                    equip_objects.append(equip_obj)
                
                # 批量插入/更新
                for equip_obj in equip_objects:
                    session.merge(equip_obj)  # merge会自动处理插入/更新
                
                # 提交事务
                session.commit()
                
                self.logger.info(f"ORM批量保存详细装备数据成功: {len(equip_list)} 条")
                return True
                
            except Exception as e:
                session.rollback()
                self.logger.error(f"ORM批量保存详细装备数据失败，已回滚: {e}")
                raise e
            finally:
                session.close()
                
        except Exception as e:
            self.logger.error(f"ORM批量保存详细装备数据时发生异常: {e}")
            return False
    
    def save_equipment(self, equipment_data: Dict[str, Any]) -> bool:
        """智能保存装备数据，冲突时保留create_time"""
        # 添加更新时间，使用MySQL标准格式
        equipment_data['update_time'] = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        
        # 使用UPDATE冲突处理，保留create_time
        return self.db_helper.insert_data('equipments', equipment_data, on_conflict="UPDATE")
    
    def save_equipments_batch(self, equipments_list: List[Dict[str, Any]]) -> bool:
        """批量保存装备数据，冲突时保留create_time"""
        if not equipments_list:
            return True
        
        # 为所有记录添加时间戳，使用MySQL标准格式
        timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        for equip in equipments_list:
            equip['update_time'] = timestamp
        
        return self.db_helper.insert_data('equipments', equipments_list, on_conflict="UPDATE")
    
    def save_pet_data(self, pet_data: Dict[str, Any]) -> bool:
        """智能保存召唤兽数据，冲突时保留create_time"""
        # 添加更新时间，使用MySQL标准格式
        pet_data['update_time'] = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        
        return self.db_helper.insert_data('pets', pet_data, on_conflict="UPDATE")
    
    def save_pets_batch(self, pets_list: List[Dict[str, Any]]) -> bool:
        """批量保存召唤兽数据，冲突时保留create_time"""
        if not pets_list:
            return True
        
        # 为所有记录添加时间戳，使用MySQL标准格式
        timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        for pet in pets_list:
            pet['update_time'] = timestamp
        
        return self.db_helper.insert_data('pets', pets_list, on_conflict="UPDATE")

    def check_role_exists_by_eid(self, eid: str) -> bool:
        """检查角色是否存在"""
        try:
            with self.db_helper.get_connection() as conn:
                query = text("SELECT COUNT(*) FROM roles WHERE eid = :eid")
                result = conn.execute(query, {'eid': eid}).fetchone()
                return result[0] > 0
        except Exception as e:
            self.logger.error(f"检查角色是否存在失败: {e}")
            return False