#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
最终版测试文件：完整的宠物装备addon_status字段分析报告
包含问题诊断和解决方案
"""

import sqlite3
import sys
import os
import re
import json
from collections import Counter

# 添加项目根目录到Python路径
current_dir = os.path.dirname(os.path.abspath(__file__))
project_root = os.path.dirname(os.path.dirname(current_dir))
sys.path.insert(0, project_root)

from src.evaluator.feature_extractor.pet_equip_feature_extractor import PetEquipFeatureExtractor

class FinalPetAddonStatusAnalyzer:
    """最终版宠物装备addon_status字段分析器"""
    
    def __init__(self, db_path: str):
        self.db_path = db_path
        self.feature_extractor = PetEquipFeatureExtractor()
        self.connection = None
        
        # 套装检测模式
        self.suit_pattern = r'#c4DBAF4套装效果：附加状态#c4DBAF4\s*([^#\n]+)'
        
    def connect_database(self):
        """连接数据库"""
        try:
            self.connection = sqlite3.connect(self.db_path)
            print(f"✅ 成功连接数据库: {self.db_path}")
            return True
        except Exception as e:
            print(f"❌ 连接数据库失败: {str(e)}")
            return False
    
    def get_database_info(self):
        """获取数据库基本信息"""
        try:
            cursor = self.connection.cursor()
            
            # 获取数据总数
            cursor.execute("SELECT COUNT(*) FROM pets")
            total_count = cursor.fetchone()[0]
            
            # 检查字段结构
            cursor.execute("PRAGMA table_info(pets);")
            columns = cursor.fetchall()
            column_names = [col[1] for col in columns]
            
            # 检查是否有addon_status字段
            has_addon_status = 'addon_status' in column_names
            
            print(f"📊 数据库信息:")
            print(f"  总数据量: {total_count:,} 条")
            print(f"  字段数量: {len(column_names)}")
            print(f"  包含addon_status字段: {'是' if has_addon_status else '否'}")
            
            return {
                'total_count': total_count,
                'column_count': len(column_names),
                'has_addon_status': has_addon_status
            }
            
        except Exception as e:
            print(f"❌ 获取数据库信息失败: {str(e)}")
            return None
    
    def analyze_suit_distribution(self, sample_size: int = 1000):
        """分析套装分布情况"""
        print(f"\n🔍 分析套装分布情况 (样本数: {sample_size:,})...")
        
        try:
            cursor = self.connection.cursor()
            
            # 获取样本数据
            query = """
            SELECT eid, equip_name, large_equip_desc
            FROM pets 
            LIMIT ?
            """
            
            cursor.execute(query, (sample_size,))
            rows = cursor.fetchall()
            
            # 分析套装信息
            suit_results = []
            successful_detections = 0
            
            for row in rows:
                eid, equip_name, large_equip_desc = row
                
                if large_equip_desc:
                    # 使用正则表达式检测套装
                    match = re.search(self.suit_pattern, large_equip_desc)
                    if match:
                        suit_effect = match.group(1).strip()
                        successful_detections += 1
                        suit_results.append({
                            'eid': eid,
                            'equip_name': equip_name,
                            'suit_effect': suit_effect
                        })
            
            # 统计套装分布
            if suit_results:
                suit_counter = Counter([r['suit_effect'] for r in suit_results])
                
                print(f"📊 套装检测结果:")
                print(f"  样本总数: {sample_size:,}")
                print(f"  检测成功: {successful_detections:,}")
                print(f"  检测成功率: {(successful_detections / sample_size * 100):.1f}%")
                
                print(f"\n🎯 套装效果分布 (Top 10):")
                for i, (suit, count) in enumerate(suit_counter.most_common(10), 1):
                    percentage = (count / successful_detections * 100)
                    print(f"  {i:2d}. {suit:<20} | 数量: {count:4,} | 占比: {percentage:5.1f}%")
                
                return suit_results
            else:
                print("⚠️ 未检测到任何套装信息")
                return []
                
        except Exception as e:
            print(f"❌ 分析套装分布失败: {str(e)}")
            return []
    
    def test_feature_extractor(self, sample_size: int = 100):
        """测试特征提取器"""
        print(f"\n🔍 测试特征提取器 (样本数: {sample_size})...")
        
        try:
            cursor = self.connection.cursor()
            
            # 获取包含套装的数据
            query = """
            SELECT eid, equip_name, large_equip_desc
            FROM pets 
            WHERE large_equip_desc LIKE '%套装效果%'
            LIMIT ?
            """
            
            cursor.execute(query, (sample_size,))
            rows = cursor.fetchall()
            
            print(f"📈 获取到 {len(rows)} 条包含套装效果的数据")
            
            # 测试特征提取
            extraction_results = []
            successful_extractions = 0
            
            for i, row in enumerate(rows):
                eid, equip_name, large_equip_desc = row
                
                print(f"\n🔍 测试第 {i+1} 条数据:")
                print(f"  EID: {eid}")
                print(f"  装备名称: {equip_name}")
                
                # 手动检测套装
                manual_match = re.search(self.suit_pattern, large_equip_desc)
                manual_suit = manual_match.group(1).strip() if manual_match else "未检测到"
                
                print(f"  手动检测套装: {manual_suit}")
                
                # 使用特征提取器
                try:
                    pet_data = {
                        'eid': eid,
                        'equip_name': equip_name,
                        'large_equip_desc': large_equip_desc
                    }
                    
                    features = self.feature_extractor.extract_features(pet_data)
                    extracted_suit = features.get('addon_status', '')
                    
                    print(f"  特征提取器结果: {extracted_suit}")
                    
                    if extracted_suit:
                        successful_extractions += 1
                        status = "✅ 成功"
                    else:
                        status = "❌ 失败"
                    
                    extraction_results.append({
                        'eid': eid,
                        'manual_suit': manual_suit,
                        'extracted_suit': extracted_suit,
                        'success': bool(extracted_suit)
                    })
                    
                    print(f"  状态: {status}")
                    
                except Exception as e:
                    print(f"  特征提取异常: {str(e)}")
                    extraction_results.append({
                        'eid': eid,
                        'manual_suit': manual_suit,
                        'extracted_suit': '提取异常',
                        'success': False
                    })
            
            # 统计结果
            print(f"\n📊 特征提取器测试结果:")
            print(f"  测试总数: {len(extraction_results)}")
            print(f"  提取成功: {successful_extractions}")
            print(f"  提取成功率: {(successful_extractions / len(extraction_results) * 100):.1f}%")
            
            return extraction_results
            
        except Exception as e:
            print(f"❌ 测试特征提取器失败: {str(e)}")
            return []
    
    def generate_report(self, db_info, suit_results, extraction_results):
        """生成完整分析报告"""
        print("\n" + "="*80)
        print("📊 宠物装备addon_status字段完整分析报告")
        print("="*80)
        
        print(f"\n🏗️ 数据库状态:")
        print(f"  总数据量: {db_info['total_count']:,} 条")
        print(f"  字段数量: {db_info['column_count']}")
        print(f"  包含addon_status字段: {'是' if db_info['has_addon_status'] else '否'}")
        
        if suit_results:
            print(f"\n🎯 套装检测结果:")
            print(f"  检测成功: {len(suit_results):,} 条")
            print(f"  检测成功率: {(len(suit_results) / min(1000, db_info['total_count']) * 100):.1f}%")
        
        if extraction_results:
            print(f"\n🔧 特征提取器状态:")
            successful = sum(1 for r in extraction_results if r['success'])
            print(f"  测试总数: {len(extraction_results)}")
            print(f"  提取成功: {successful}")
            print(f"  提取成功率: {(successful / len(extraction_results) * 100):.1f}%")
        
        print(f"\n🔍 问题诊断:")
        if not db_info['has_addon_status']:
            print("  ❌ 问题1: 数据库表中没有addon_status字段")
            print("     解决方案: 需要添加addon_status字段到pets表")
        
        if extraction_results and not any(r['success'] for r in extraction_results):
            print("  ❌ 问题2: 特征提取器无法提取addon_status信息")
            print("     解决方案: 检查特征提取器的解析逻辑")
        elif extraction_results and any(r['success'] for r in extraction_results):
            print("  ✅ 特征提取器工作正常")
        
        print(f"\n💡 建议:")
        print("  1. 如果数据库中没有addon_status字段，建议添加该字段")
        print("  2. 使用特征提取器提取套装信息并存储到addon_status字段")
        print("  3. 定期更新addon_status字段以保持数据同步")
        
        print(f"\n🎉 分析完成！")
    
    def close_connection(self):
        """关闭数据库连接"""
        if self.connection:
            self.connection.close()
            print("🔒 数据库连接已关闭")

def main():
    """主函数"""
    print("🚀 开始完整的宠物装备addon_status字段分析...")
    
    db_path = r".\data\202508\cbg_pets_202508.db"
    analyzer = FinalPetAddonStatusAnalyzer(db_path)
    
    try:
        if not analyzer.connect_database():
            return
        
        # 获取数据库信息
        db_info = analyzer.get_database_info()
        if not db_info:
            return
        
        # 分析套装分布
        suit_results = analyzer.analyze_suit_distribution(9999999)
        
        # 测试特征提取器
        extraction_results = analyzer.test_feature_extractor(20)
        
        # 生成完整报告
        analyzer.generate_report(db_info, suit_results, extraction_results)
        
    except Exception as e:
        print(f"❌ 分析过程中出现错误: {str(e)}")
        import traceback
        traceback.print_exc()
    
    finally:
        analyzer.close_connection()

if __name__ == "__main__":
    main() 