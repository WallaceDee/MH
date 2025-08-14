#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
增强版测试文件：分析宠物装备addon_status字段分布情况
"""

import sqlite3
import pandas as pd
import sys
import os
from collections import Counter
import matplotlib.pyplot as plt

# 添加项目根目录到Python路径
current_dir = os.path.dirname(os.path.abspath(__file__))
project_root = os.path.dirname(os.path.dirname(current_dir))
sys.path.insert(0, project_root)

from src.evaluator.feature_extractor.pet_equip_feature_extractor import PetEquipFeatureExtractor

class EnhancedPetAddonStatusAnalyzer:
    """增强版宠物装备addon_status字段分析器"""
    
    def __init__(self, db_path: str):
        self.db_path = db_path
        self.feature_extractor = PetEquipFeatureExtractor()
        self.connection = None
        
    def connect_database(self):
        """连接数据库"""
        try:
            self.connection = sqlite3.connect(self.db_path)
            print(f"✅ 成功连接数据库: {self.db_path}")
            
            cursor = self.connection.cursor()
            cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
            tables = cursor.fetchall()
            print(f"📊 数据库中的表: {[table[0] for table in tables]}")
            
            if ('pets',) in tables:
                cursor.execute("PRAGMA table_info(pets);")
                columns = cursor.fetchall()
                column_names = [col[1] for col in columns]
                print(f"🐾 pets表字段数量: {len(column_names)}")
                
                if 'addon_status' in column_names:
                    print("✅ 发现addon_status字段")
                else:
                    print("⚠️ 未发现addon_status字段")
            
            return True
        except Exception as e:
            print(f"❌ 连接数据库失败: {str(e)}")
            return False
    
    def get_total_pet_count(self) -> int:
        """获取宠物数据总数"""
        try:
            cursor = self.connection.cursor()
            cursor.execute("SELECT COUNT(*) FROM pets")
            total_count = cursor.fetchone()[0]
            print(f"📊 数据库中共有 {total_count:,} 条宠物数据")
            return total_count
        except Exception as e:
            print(f"❌ 获取数据总数失败: {str(e)}")
            return 0
    
    def get_pet_data(self, limit: int = None, offset: int = 0) -> list:
        """获取宠物数据"""
        try:
            cursor = self.connection.cursor()
            
            query = "SELECT * FROM pets"
            if limit:
                query += f" LIMIT {limit}"
            if offset:
                query += f" OFFSET {offset}"
            
            cursor.execute(query)
            columns = [description[0] for description in cursor.description]
            rows = cursor.fetchall()
            
            pets_data = []
            for row in rows:
                pet_dict = dict(zip(columns, row))
                pets_data.append(pet_dict)
            
            print(f"📈 获取到 {len(pets_data)} 条宠物数据 (offset: {offset})")
            return pets_data
            
        except Exception as e:
            print(f"❌ 获取宠物数据失败: {str(e)}")
            return []
    
    def check_original_addon_status(self, pets_data: list) -> dict:
        """检查原始数据中的addon_status字段"""
        print("🔍 检查原始数据中的addon_status字段...")
        
        original_addon_status_values = []
        for pet in pets_data:
            addon_status = pet.get('addon_status', '')
            if addon_status is None:
                addon_status = ''
            original_addon_status_values.append(str(addon_status))
        
        original_counter = Counter(original_addon_status_values)
        total_count = len(original_addon_status_values)
        
        check_result = {
            'total_count': total_count,
            'unique_values': len(original_counter),
            'distribution': {},
            'top_values': [],
            'empty_count': 0,
            'non_empty_count': 0
        }
        
        for status, count in original_counter.most_common():
            percentage = (count / total_count) * 100
            check_result['distribution'][status] = {
                'count': count,
                'percentage': percentage
            }
            
            if status == '' or status == 'None':
                check_result['empty_count'] += count
            else:
                check_result['non_empty_count'] += count
        
        check_result['empty_percentage'] = (check_result['empty_count'] / total_count) * 100
        check_result['non_empty_count_percentage'] = (check_result['non_empty_count'] / total_count) * 100
        check_result['top_values'] = original_counter.most_common(10)
        
        return check_result
    
    def extract_features_for_pets(self, pets_data: list) -> list:
        """为宠物数据提取特征"""
        print("🔍 开始提取宠物装备特征...")
        
        features_data = []
        total = len(pets_data)
        
        for i, pet in enumerate(pets_data):
            try:
                features = self.feature_extractor.extract_features(pet)
                pet_with_features = {**pet, **features}
                features_data.append(pet_with_features)
                
                if (i + 1) % 100 == 0 or (i + 1) == total:
                    print(f"📊 特征提取进度: {i + 1}/{total} ({((i + 1) / total * 100):.1f}%)")
                    
            except Exception as e:
                print(f"⚠️ 提取宠物 {pet.get('eid', 'unknown')} 特征失败: {str(e)}")
                pet_with_features = {**pet, 'addon_status': '提取失败'}
                features_data.append(pet_with_features)
        
        print(f"✅ 特征提取完成，共处理 {len(features_data)} 条数据")
        return features_data
    
    def analyze_addon_status_distribution(self, features_data: list) -> dict:
        """分析addon_status字段的分布情况"""
        print("📊 开始分析addon_status字段分布...")
        
        addon_status_values = []
        for pet in features_data:
            addon_status = pet.get('addon_status', '')
            if addon_status is None:
                addon_status = ''
            addon_status_values.append(str(addon_status))
        
        status_counter = Counter(addon_status_values)
        total_count = len(addon_status_values)
        
        analysis_result = {
            'total_count': total_count,
            'unique_values': len(status_counter),
            'distribution': {},
            'top_values': [],
            'empty_count': 0,
            'non_empty_count': 0
        }
        
        for status, count in status_counter.most_common():
            percentage = (count / total_count) * 100
            analysis_result['distribution'][status] = {
                'count': count,
                'percentage': percentage
            }
            
            if status == '' or status == 'None' or status == '提取失败':
                analysis_result['empty_count'] += count
            else:
                analysis_result['non_empty_count'] += count
        
        analysis_result['empty_percentage'] = (analysis_result['empty_count'] / total_count) * 100
        analysis_result['non_empty_percentage'] = (analysis_result['non_empty_count'] / total_count) * 100
        analysis_result['top_values'] = status_counter.most_common(10)
        
        return analysis_result
    
    def print_comparison_results(self, original_result: dict, extracted_result: dict):
        """打印对比分析结果"""
        print("\n" + "="*80)
        print("📊 宠物装备addon_status字段对比分析结果")
        print("="*80)
        
        print(f"📈 总数据量: {original_result['total_count']:,}")
        print(f"🔍 唯一值数量: {original_result['unique_values']} (原始) vs {extracted_result['unique_values']} (提取后)")
        
        print(f"\n📝 原始数据:")
        print(f"   非空值数量: {original_result['non_empty_count']:,} ({original_result['non_empty_count_percentage']:.2f}%)")
        print(f"   空值数量: {original_result['empty_count']:,} ({original_result['empty_percentage']:.2f}%)")
        
        print(f"\n📝 特征提取后:")
        print(f"   非空值数量: {extracted_result['non_empty_count']:,} ({extracted_result['non_empty_percentage']:.2f}%)")
        print(f"   空值数量: {extracted_result['empty_count']:,} ({extracted_result['empty_percentage']:.2f}%)")
        
        print("\n🏆 原始数据 Top 10 addon_status值:")
        print("-" * 60)
        for i, (status, count) in enumerate(original_result['top_values'], 1):
            percentage = (count / original_result['total_count']) * 100
            status_display = status if status else "空值"
            print(f"{i:2d}. {status_display:<25} | 数量: {count:6,} | 占比: {percentage:6.2f}%")
        
        print("\n🏆 特征提取后 Top 10 addon_status值:")
        print("-" * 60)
        for i, (status, count) in enumerate(extracted_result['top_values'], 1):
            percentage = (count / extracted_result['total_count']) * 100
            status_display = status if status else "空值"
            print(f"{i:2d}. {status_display:<25} | 数量: {count:6,} | 占比: {percentage:6.2f}%")
    
    def close_connection(self):
        """关闭数据库连接"""
        if self.connection:
            self.connection.close()
            print("🔒 数据库连接已关闭")

def main():
    """主函数"""
    print("🚀 开始增强版宠物装备addon_status字段分布分析...")
    
    db_path = r".\data\202508\cbg_pets_202508.db"
    analyzer = EnhancedPetAddonStatusAnalyzer(db_path)
    
    try:
        if not analyzer.connect_database():
            return
        
        total_count = analyzer.get_total_pet_count()
        
        if total_count > 10000:
            print(f"📊 数据量较大({total_count:,}条)，采用分批分析策略")
            sample_size = 5000
        else:
            sample_size = total_count
        
        print(f"\n📥 获取宠物数据样本 (样本大小: {sample_size:,})...")
        pets_data = analyzer.get_pet_data(limit=sample_size)
        
        if not pets_data:
            print("❌ 没有获取到宠物数据")
            return
        
        print("\n🔍 检查原始数据中的addon_status字段...")
        original_result = analyzer.check_original_addon_status(pets_data)
        
        print("\n🔍 提取宠物装备特征...")
        features_data = analyzer.extract_features_for_pets(pets_data)
        
        if not features_data:
            print("❌ 特征提取失败")
            return
        
        print("\n📊 分析特征提取后的addon_status字段分布...")
        extracted_result = analyzer.analyze_addon_status_distribution(features_data)
        
        analyzer.print_comparison_results(original_result, extracted_result)
        
        print("\n🎉 增强版分析完成！")
        
    except Exception as e:
        print(f"❌ 分析过程中出现错误: {str(e)}")
        import traceback
        traceback.print_exc()
    
    finally:
        analyzer.close_connection()

if __name__ == "__main__":
    main() 