#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
智能数据库操作助手
专门解决 "values跟columns不一致" 的问题
"""

import sqlite3
import json
import logging
from typing import Dict, List, Any, Optional, Union
from datetime import datetime

class SmartDBHelper:
    """智能数据库操作助手"""
    
    def __init__(self, db_path: str):
        self.db_path = db_path
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
        return sqlite3.connect(self.db_path)
    
    def get_table_columns(self, table_name: str) -> List[str]:
        """获取表的所有列名"""
        try:
            with self.get_connection() as conn:
                cursor = conn.cursor()
                cursor.execute(f"PRAGMA table_info({table_name})")
                columns_info = cursor.fetchall()
                # 返回列名列表，排除主键自增列
                columns = [col[1] for col in columns_info if not (col[5] == 1 and col[2].upper() == 'INTEGER')]
                return columns
        except Exception as e:
            self.logger.error(f"获取表{table_name}列名失败: {e}")
            return []
    
    def validate_data_types(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """验证和转换数据类型"""
        validated_data = {}
        
        for key, value in data.items():
            if value is None:
                validated_data[key] = None
            elif isinstance(value, (dict, list)):
                # 复杂数据类型转为JSON字符串
                validated_data[key] = json.dumps(value, ensure_ascii=False)
            elif isinstance(value, bool):
                # 布尔值转为整数
                validated_data[key] = 1 if value else 0
            elif isinstance(value, (int, float, str)):
                # 基本数据类型直接使用
                validated_data[key] = value
            else:
                # 其他类型转为字符串
                validated_data[key] = str(value)
        
        return validated_data
    
    def build_insert_sql(self, table_name: str, data: Dict[str, Any], 
                        on_conflict: str = "REPLACE") -> tuple:
        """构建INSERT SQL语句"""
        # 验证数据类型
        validated_data = self.validate_data_types(data)
        
        # 获取表的列名
        table_columns = self.get_table_columns(table_name)
        
        # 只使用表中实际存在的列
        filtered_data = {k: v for k, v in validated_data.items() if k in table_columns}
        
        if not filtered_data:
            raise ValueError(f"没有有效的列数据可插入到表 {table_name}")
        
        # 构建SQL语句
        columns = list(filtered_data.keys())
        placeholders = ['?' for _ in columns]  # 自动生成占位符
        values = tuple(filtered_data.values())
        
        # 根据冲突处理方式选择INSERT语句类型
        if on_conflict == "REPLACE":
            sql = f"INSERT OR REPLACE INTO {table_name} ({', '.join(columns)}) VALUES ({', '.join(placeholders)})"
        elif on_conflict == "IGNORE":
            sql = f"INSERT OR IGNORE INTO {table_name} ({', '.join(columns)}) VALUES ({', '.join(placeholders)})"
        else:
            sql = f"INSERT INTO {table_name} ({', '.join(columns)}) VALUES ({', '.join(placeholders)})"
        
        return sql, values
    
    def insert_data(self, table_name: str, data: Union[Dict[str, Any], List[Dict[str, Any]]], 
                   on_conflict: str = "REPLACE") -> bool:
        """插入数据"""
        try:
            with self.get_connection() as conn:
                cursor = conn.cursor()
                
                if isinstance(data, dict):
                    # 单条数据
                    sql, params = self.build_insert_sql(table_name, data, on_conflict)
                    cursor.execute(sql, params)
                    
                    # 检查是否实际插入了数据
                    if on_conflict == "IGNORE" and cursor.rowcount == 0:
                        self.logger.debug(f"数据已存在，跳过插入到表 {table_name}")
                        return False  # 返回False表示没有插入新数据
                    else:
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
                    first_data = self.validate_data_types(data[0])
                    columns = [k for k in first_data.keys() if k in table_columns]
                    
                    # 为所有数据构建参数列表
                    all_params = []
                    for item in data:
                        validated_item = self.validate_data_types(item)
                        # 按照相同的列顺序提取值
                        params = tuple(validated_item.get(col) for col in columns)
                        all_params.append(params)
                    
                    # 批量执行
                    cursor.executemany(sql_template, all_params)
                    inserted_count = cursor.rowcount
                    
                    if on_conflict == "IGNORE" and inserted_count < len(data):
                        self.logger.info(f"批量插入{inserted_count}/{len(data)}条数据到表 {table_name} (部分数据已存在)")
                    else:
                        self.logger.info(f"成功批量插入{inserted_count}条数据到表 {table_name}")
                
                conn.commit()
                return True
                
        except Exception as e:
            self.logger.error(f"插入数据到表 {table_name} 失败: {e}")
            return False

class CBGSmartDB:
    """CBG爬虫专用智能数据库管理器"""
    
    def __init__(self, db_path: str):
        self.db_helper = SmartDBHelper(db_path)
        self.logger = logging.getLogger('CBGSmartDB')
    
    def save_character(self, character_data: Dict[str, Any]) -> bool:
        """智能保存角色数据，使用REPLACE INTO实现完全覆盖"""
        # 添加更新时间
        character_data['update_time'] = datetime.now().isoformat()
        
        # 使用REPLACE INTO实现完全覆盖
        return self.db_helper.insert_data('characters', character_data, on_conflict="REPLACE")
    
    def save_characters_batch(self, characters_list: List[Dict[str, Any]]) -> bool:
        """批量保存角色数据，使用REPLACE INTO实现完全覆盖"""
        if not characters_list:
            return True
        
        # 为所有记录添加时间戳
        timestamp = datetime.now().isoformat()
        for char in characters_list:
            char['update_time'] = timestamp
        
        return self.db_helper.insert_data('characters', characters_list, on_conflict="REPLACE")
    
    def save_large_equip_data(self, equip_data: Dict[str, Any]) -> bool:
        """智能保存详细装备数据，使用REPLACE INTO实现完全覆盖"""
        # 添加更新时间
        equip_data['update_time'] = datetime.now().isoformat()
        
        return self.db_helper.insert_data('large_equip_desc_data', equip_data, on_conflict="REPLACE")
    
    def save_pet_data(self, pet_data: Dict[str, Any]) -> bool:
        """智能保存宠物数据"""
        return self.db_helper.insert_data('pets', pet_data)
    
    def save_api_log(self, log_data: Dict[str, Any]) -> bool:
        """智能保存API日志"""
        # 注意：API logs表的字段名是request_time，不是timestamp
        log_data['request_time'] = datetime.now().isoformat()
        return self.db_helper.insert_data('api_logs', log_data)

if __name__ == "__main__":
    # 简单测试
    print("🧪 测试智能数据库助手...")
    
    # 创建测试数据
    test_data = {
        'equip_id': 'test_001',
        'character_name': '测试角色',
        'level': 100,
        'price': 1234.56,
        'complex_data': {'skill': 'test', 'level': 5},  # 字典会自动转JSON
        'boolean_field': True,  # 布尔值会自动转整数
        'none_field': None,  # None值保持
        'extra_field_not_in_table': 'will_be_ignored'  # 不存在的字段会被忽略
    }
    
    try:
        smart_db = CBGSmartDB("test_smart_db.db")
        print("✅ 智能数据库助手创建成功")
        print(f"📊 测试数据: {test_data}")
        print("✨ 智能数据库助手会自动处理：")
        print("   • 字段类型转换（字典→JSON，布尔→整数）")
        print("   • 字段过滤（只保留表中存在的字段）")
        print("   • 自动生成SQL占位符（不需要手动写?）")
        print("   • 防止字段数量不匹配错误")
        
    except Exception as e:
        print(f"❌ 测试失败: {e}")
        import traceback
        traceback.print_exc()
    
    print("🏁 测试完成") 