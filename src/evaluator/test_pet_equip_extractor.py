#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
召唤兽装备特征提取器测试脚本
"""

import sys
import os

# 添加项目根目录到Python路径
current_dir = os.path.dirname(os.path.abspath(__file__))
project_root = os.path.dirname(os.path.dirname(current_dir))
sys.path.insert(0, project_root)

import sqlite3
from src.evaluator.feature_extractor.pet_equip_feature_extractor import PetEquipFeatureExtractor

def test_pet_equip_extractor():
    """测试召唤兽装备特征提取器"""
    print("="*60)
    print("召唤兽装备特征提取器测试")
    print("="*60)
    
    # 创建提取器
    extractor = PetEquipFeatureExtractor()
    
    # 连接数据库
    project_root = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
    db_path = os.path.join(project_root, 'data', '202507', 'cbg_equip_202507.db')
    print(f"连接数据库: {db_path}")
    
    try:
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        # 查询召唤兽装备数据
        cursor.execute("""
            SELECT 
                eid as equip_id, equip_level, kindid, 
                mingzhong, speed, qixue, fangyu, shanghai,
                addon_fali, addon_lingli, addon_liliang, addon_minjie, addon_naili,
                xiang_qian_level, addon_status, large_equip_desc
            FROM equipments
            from src.evaluator.constants.equipment_types import PET_EQUIP_KINDID
WHERE equip_level > 0 AND kindid = {PET_EQUIP_KINDID} AND fangyu > 0
            LIMIT 5
        """)
        
        columns = [description[0] for description in cursor.description]
        rows = cursor.fetchall()
        
        print(f"查询到 {len(rows)} 个召唤兽装备")
        
        for i, row in enumerate(rows, 1):
            print(f"\n{'='*50}")
            print(f"测试装备 {i}:")
            
            # 转换为字典
            equip_data = dict(zip(columns, row))
            
            # 显示基本信息
            print(f"装备ID: {equip_data.get('equip_id', 'N/A')}")
            print(f"等级: {equip_data.get('equip_level', 'N/A')}")
            print(f"命中: {equip_data.get('mingzhong', 'N/A')}")
            print(f"速度: {equip_data.get('speed', 'N/A')}")
            print(f"气血: {equip_data.get('qixue', 'N/A')}")
            print(f"防御: {equip_data.get('fangyu', 'N/A')}")
            print(f"伤害: {equip_data.get('shanghai', 'N/A')}")
            print(f"宝石等级: {equip_data.get('xiang_qian_level', 'N/A')}")
            print(f"套装效果: {equip_data.get('addon_status', 'N/A')}")
            
            # 显示装备描述
            large_desc = equip_data.get('large_equip_desc', '')
            if large_desc:
                print(f"装备描述: {large_desc[:150]}...")
            
            try:
                # 提取特征
                features = extractor.extract_features(equip_data)
                
                print("\n提取的特征:")
                for key, value in features.items():
                    print(f"  {key}: {value}")
                    
            except Exception as e:
                print(f"特征提取失败: {e}")
                import traceback
                traceback.print_exc()
        
        conn.close()
        print(f"\n{'='*60}")
        print("测试完成！")
        
    except Exception as e:
        print(f"测试失败: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    test_pet_equip_extractor() 