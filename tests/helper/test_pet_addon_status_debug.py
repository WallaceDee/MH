#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
调试版测试文件：检查宠物装备特征提取器是否能从large_equip_desc中提取套装信息
"""

import sqlite3
import sys
import os
import json

# 添加项目根目录到Python路径
current_dir = os.path.dirname(os.path.abspath(__file__))
project_root = os.path.dirname(os.path.dirname(current_dir))
sys.path.insert(0, project_root)

from src.evaluator.feature_extractor.pet_equip_feature_extractor import PetEquipFeatureExtractor

class PetAddonStatusDebugger:
    """宠物装备addon_status字段调试器"""
    
    def __init__(self, db_path: str):
        self.db_path = db_path
        self.feature_extractor = PetEquipFeatureExtractor()
        self.connection = None
        
    def connect_database(self):
        """连接数据库"""
        try:
            self.connection = sqlite3.connect(self.db_path)
            print(f"✅ 成功连接数据库: {self.db_path}")
            return True
        except Exception as e:
            print(f"❌ 连接数据库失败: {str(e)}")
            return False
    
    def get_sample_pet_data(self, limit: int = 10) -> list:
        """获取样本宠物数据"""
        try:
            cursor = self.connection.cursor()
            
            # 查询包含large_equip_desc的数据
            query = """
            SELECT eid, equip_name, large_equip_desc, desc
            FROM pets 
            WHERE large_equip_desc IS NOT NULL AND large_equip_desc != ''
            LIMIT ?
            """
            
            cursor.execute(query, (limit,))
            rows = cursor.fetchall()
            
            pets_data = []
            for row in rows:
                pet_dict = {
                    'eid': row[0],
                    'equip_name': row[1],
                    'large_equip_desc': row[2],
                    'desc': row[3]
                }
                pets_data.append(pet_dict)
            
            print(f"📈 获取到 {len(pets_data)} 条包含large_equip_desc的宠物数据")
            return pets_data
            
        except Exception as e:
            print(f"❌ 获取宠物数据失败: {str(e)}")
            return []
    
    def debug_feature_extraction(self, pets_data: list):
        """调试特征提取过程"""
        print("\n🔍 开始调试特征提取过程...")
        
        for i, pet in enumerate(pets_data):
            print(f"\n{'='*60}")
            print(f"🔍 调试第 {i+1} 条数据:")
            print(f"EID: {pet['eid']}")
            print(f"装备名称: {pet['equip_name']}")
            print(f"large_equip_desc长度: {len(pet['large_equip_desc']) if pet['large_equip_desc'] else 0}")
            
            if pet['large_equip_desc']:
                print(f"large_equip_desc前200字符: {pet['large_equip_desc'][:200]}...")
                
                # 尝试提取特征
                try:
                    features = self.feature_extractor.extract_features(pet)
                    print(f"✅ 特征提取成功")
                    print(f"提取的特征: {json.dumps(features, ensure_ascii=False, indent=2)}")
                    
                    # 检查addon_status字段
                    addon_status = features.get('addon_status', '')
                    if addon_status:
                        print(f"🎯 成功提取到addon_status: {addon_status}")
                    else:
                        print(f"⚠️ addon_status为空")
                        
                except Exception as e:
                    print(f"❌ 特征提取失败: {str(e)}")
                    import traceback
                    traceback.print_exc()
            else:
                print("⚠️ large_equip_desc为空")
    
    def check_large_equip_desc_content(self, limit: int = 100):
        """检查large_equip_desc字段的内容分布"""
        print(f"\n🔍 检查large_equip_desc字段内容分布 (样本数: {limit})...")
        
        try:
            cursor = self.connection.cursor()
            
            # 统计large_equip_desc字段的分布
            query = """
            SELECT 
                CASE 
                    WHEN large_equip_desc IS NULL THEN 'NULL'
                    WHEN large_equip_desc = '' THEN '空字符串'
                    ELSE '有内容'
                END as desc_status,
                COUNT(*) as count
            FROM pets 
            GROUP BY desc_status
            """
            
            cursor.execute(query)
            rows = cursor.fetchall()
            
            print("📊 large_equip_desc字段分布:")
            total = 0
            for row in rows:
                status, count = row
                total += count
                print(f"  {status}: {count:,} 条")
            
            print(f"  总计: {total:,} 条")
            
            # 检查是否有套装相关的描述
            query = """
            SELECT COUNT(*) as count
            FROM pets 
            WHERE large_equip_desc LIKE '%套装%' 
               OR large_equip_desc LIKE '%高级%'
               OR large_equip_desc LIKE '%强力%'
               OR large_equip_desc LIKE '%反震%'
            """
            
            cursor.execute(query)
            suit_count = cursor.fetchone()[0]
            print(f"  包含套装关键词的数据: {suit_count:,} 条")
            
        except Exception as e:
            print(f"❌ 检查large_equip_desc内容失败: {str(e)}")
    
    def close_connection(self):
        """关闭数据库连接"""
        if self.connection:
            self.connection.close()
            print("🔒 数据库连接已关闭")

def main():
    """主函数"""
    print("🚀 开始调试宠物装备addon_status字段提取...")
    
    db_path = r".\data\202508\cbg_pets_202508.db"
    debugger = PetAddonStatusDebugger(db_path)
    
    try:
        if not debugger.connect_database():
            return
        
        # 检查large_equip_desc字段内容分布
        debugger.check_large_equip_desc_content(100)
        
        # 获取样本数据
        print(f"\n📥 获取样本宠物数据...")
        pets_data = debugger.get_sample_pet_data(limit=5)
        
        if not pets_data:
            print("❌ 没有获取到包含large_equip_desc的宠物数据")
            return
        
        # 调试特征提取
        debugger.debug_feature_extraction(pets_data)
        
        print("\n🎉 调试完成！")
        
    except Exception as e:
        print(f"❌ 调试过程中出现错误: {str(e)}")
        import traceback
        traceback.print_exc()
    
    finally:
        debugger.close_connection()

if __name__ == "__main__":
    main() 