#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
测试装备数据字段数量
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.app import create_app
from src.database import db
from src.models.equipment import Equipment
from src.evaluator.constants.equipment_types import EQUIPMENT_CACHE_REQUIRED_FIELDS

def test_field_count():
    """测试字段数量"""
    app = create_app()
    
    with app.app_context():
        print("=== 字段数量测试 ===")
        print(f"EQUIPMENT_CACHE_REQUIRED_FIELDS 字段数量: {len(EQUIPMENT_CACHE_REQUIRED_FIELDS)}")
        print("字段列表:")
        for i, field in enumerate(EQUIPMENT_CACHE_REQUIRED_FIELDS, 1):
            print(f"  {i:2d}. {field}")
        
        print("\n=== 检查数据库模型中字段是否存在 ===")
        missing_fields = []
        for field in EQUIPMENT_CACHE_REQUIRED_FIELDS:
            if not hasattr(Equipment, field):
                missing_fields.append(field)
                print(f"❌ {field} - 不存在")
            else:
                print(f"✅ {field} - 存在")
        
        if missing_fields:
            print(f"\n缺少的字段: {missing_fields}")
        else:
            print("\n✅ 所有字段都存在")
        
        print("\n=== 测试查询 ===")
        try:
            # 构建查询字段
            required_fields = [getattr(Equipment, field) for field in EQUIPMENT_CACHE_REQUIRED_FIELDS]
            print(f"查询字段数量: {len(required_fields)}")
            
            # 执行查询（限制1条记录）
            query = db.session.query(*required_fields).limit(1)
            result = query.first()
            
            if result:
                print(f"查询结果字段数量: {len(result)}")
                print("查询结果字段:")
                for i, (field, value) in enumerate(zip(EQUIPMENT_CACHE_REQUIRED_FIELDS, result), 1):
                    print(f"  {i:2d}. {field}: {value}")
            else:
                print("❌ 查询结果为空")
                
        except Exception as e:
            print(f"❌ 查询失败: {e}")
            import traceback
            traceback.print_exc()

if __name__ == "__main__":
    test_field_count()
