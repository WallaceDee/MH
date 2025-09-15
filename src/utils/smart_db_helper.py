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
        """从数据库schema中获取字段类型"""
        try:
            with self.get_connection() as conn:
                query = text("""
                    SELECT DATA_TYPE 
                    FROM INFORMATION_SCHEMA.COLUMNS 
                    WHERE TABLE_SCHEMA = DATABASE() 
                    AND TABLE_NAME = :table_name 
                    AND COLUMN_NAME = :field_name
                """)
                result = conn.execute(query, {
                    'table_name': table_name,
                    'field_name': field_name
                })
                row = result.fetchone()
                if row:
                    return row[0].upper()
                return 'TEXT'  # 如果找不到字段，默认返回TEXT类型
        except Exception as e:
            self.logger.error(f"获取字段 {field_name} 类型失败: {e}")
            return 'TEXT'
    
    def validate_data_types(self, data: Dict[str, Any], table_name: str = 'large_equip_desc_data') -> Dict[str, Any]:
        """验证并转换数据类型"""
        validated_data = {}
        for key, value in data.items():
            if value is None:
                validated_data[key] = value
                continue
                
            # 获取字段类型
            field_type = self.get_field_type(key, table_name)
            
            # 根据字段类型进行转换
            if field_type in ['INT', 'INTEGER', 'BIGINT', 'TINYINT', 'SMALLINT', 'MEDIUMINT']:
                try:
                    validated_data[key] = int(float(value))
                except (ValueError, TypeError):
                    validated_data[key] = 0
            elif field_type in ['FLOAT', 'DOUBLE', 'DECIMAL', 'NUMERIC']:
                try:
                    validated_data[key] = float(value)
                except (ValueError, TypeError):
                    validated_data[key] = 0.0
            else:
                validated_data[key] = value
        
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
        """插入数据 - MySQL版本"""
        try:
            with self.get_connection() as conn:
                if isinstance(data, dict):
                    # 单条数据
                    sql, params = self.build_insert_sql(table_name, data, on_conflict)
                    result = conn.execute(text(sql), params)
                    conn.commit()  # 直接提交
                    
                    # 检查是否实际插入了数据
                    if on_conflict == "IGNORE" and result.rowcount == 0:
                        self.logger.debug(f"数据已存在，跳过插入到表 {table_name}")
                        return False  # 返回False表示没有插入新数据
                    else:
                        self.logger.debug(f"单条数据已提交到表 {table_name}")
                        return True
                    
                elif isinstance(data, list):
                    # 批量数据
                    if not data:
                        self.logger.warning("数据列表为空，没有数据可插入")
                        return True
                    
                    # 使用第一条数据构建SQL模板
                    sql_template, _ = self.build_insert_sql(table_name, data[0], on_conflict)
                    
                    # 获取表的列名（基于第一条数据）
                    table_columns = self.get_table_columns(table_name)
                    first_data = self.validate_data_types(data[0], table_name)
                    columns = [k for k in first_data.keys() if k in table_columns]
                    
                    # 为所有数据构建参数列表
                    all_params = []
                    for item in data:
                        validated_item = self.validate_data_types(item, table_name)
                        # 按照相同的列顺序提取值
                        params = {col: validated_item.get(col) for col in columns}
                        all_params.append(params)
                    
                    # 批量执行
                    result = conn.execute(text(sql_template), all_params)
                    conn.commit()  # 直接提交
                    inserted_count = result.rowcount
                    
                    if on_conflict == "IGNORE" and inserted_count < len(data):
                        self.logger.info(f"批量插入{inserted_count}/{len(data)}条数据到表 {table_name} (部分数据已存在)")
                    else:
                        self.logger.info(f"成功批量插入{inserted_count}条数据到表 {table_name}")
                    
                    self.logger.debug(f"批量数据已提交到表 {table_name}")
                    return True
                
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
            return self.db_helper.insert_data('roles', role_data, on_conflict="REPLACE")
    
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
                
                # 使用UPDATE冲突处理，保留create_time
                return self.db_helper.insert_data('roles', role_data, on_conflict="UPDATE")
                
        except Exception as e:
            self.logger.error(f"保存角色价格历史失败: {e}")
            # 如果更新历史失败，回退到普通保存
            return self.db_helper.insert_data('roles', role_data, on_conflict="UPDATE")
    
    def save_roles_batch(self, roles_list: List[Dict[str, Any]]) -> bool:
        """批量保存角色数据，使用REPLACE INTO实现完全覆盖"""
        if not roles_list:
            return True
        
        # 为所有记录添加时间戳，使用MySQL标准格式
        timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        for char in roles_list:
            char['update_time'] = timestamp
        
        return self.db_helper.insert_data('roles', roles_list, on_conflict="REPLACE")
    
    def save_large_equip_data(self, equip_data: Dict[str, Any]) -> bool:
        """智能保存详细装备数据，冲突时保留create_time"""
        # 添加更新时间，使用MySQL标准格式
        equip_data['update_time'] = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        equip_data['create_time'] = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        return self.db_helper.insert_data('large_equip_desc_data', equip_data, on_conflict="UPDATE")
    
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