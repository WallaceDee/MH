#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
测试文件：分析宠物装备addon_status字段分布情况
连接数据库，使用特征提取器提取特征，统计addon_status字段的分布
"""

import sqlite3
import pandas as pd
import sys
import os
from collections import Counter
import matplotlib.pyplot as plt
import seaborn as sns

# 添加项目根目录到Python路径
current_dir = os.path.dirname(os.path.abspath(__file__))
project_root = os.path.dirname(os.path.dirname(current_dir))
sys.path.insert(0, project_root)

from src.evaluator.feature_extractor.pet_equip_feature_extractor import PetEquipFeatureExtractor

class PetAddonStatusAnalyzer:
    """宠物装备addon_status字段分析器"""
    
    def __init__(self, db_path: str):
        """
        初始化分析器
        
        Args:
            db_path: 数据库文件路径
        """
        self.db_path = db_path
        self.feature_extractor = PetEquipFeatureExtractor()
        self.connection = None
        
    def connect_database(self):
        """连接数据库"""
        try:
            self.connection = sqlite3.connect(self.db_path)
            print(f"✅ 成功连接数据库: {self.db_path}")
            
            # 检查数据库表结构
            cursor = self.connection.cursor()
            cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
            tables = cursor.fetchall()
            print(f"📊 数据库中的表: {[table[0] for table in tables]}")
            
            # 检查pets表结构
            if ('pets',) in tables:
                cursor.execute("PRAGMA table_info(pets);")
                columns = cursor.fetchall()
                print(f"🐾 pets表字段: {[col[1] for col in columns]}")
            
            return True
        except Exception as e:
            print(f"❌ 连接数据库失败: {str(e)}")
            return False
    
    def get_pet_data(self, limit: int = None) -> list:
        """
        获取宠物数据
        
        Args:
            limit: 限制返回的记录数量，None表示全部
            
        Returns:
            list: 宠物数据列表
        """
        try:
            cursor = self.connection.cursor()
            
            # 构建查询语句
            query = "SELECT * FROM pets"
            if limit:
                query += f" LIMIT {limit}"
            
            cursor.execute(query)
            columns = [description[0] for description in cursor.description]
            rows = cursor.fetchall()
            
            # 转换为字典列表
            pets_data = []
            for row in rows:
                pet_dict = dict(zip(columns, row))
                pets_data.append(pet_dict)
            
            print(f"📈 获取到 {len(pets_data)} 条宠物数据")
            return pets_data
            
        except Exception as e:
            print(f"❌ 获取宠物数据失败: {str(e)}")
            return []
    
    def extract_features_for_pets(self, pets_data: list) -> list:
        """
        为宠物数据提取特征
        
        Args:
            pets_data: 宠物数据列表
            
        Returns:
            list: 提取特征后的数据列表
        """
        print("🔍 开始提取宠物装备特征...")
        
        features_data = []
        total = len(pets_data)
        
        for i, pet in enumerate(pets_data):
            try:
                # 提取特征
                features = self.feature_extractor.extract_features(pet)
                
                # 合并原始数据和特征
                pet_with_features = {**pet, **features}
                features_data.append(pet_with_features)
                
                # 显示进度
                if (i + 1) % 100 == 0 or (i + 1) == total:
                    print(f"📊 特征提取进度: {i + 1}/{total} ({((i + 1) / total * 100):.1f}%)")
                    
            except Exception as e:
                print(f"⚠️ 提取宠物 {pet.get('eid', 'unknown')} 特征失败: {str(e)}")
                # 添加默认特征
                pet_with_features = {**pet, 'addon_status': '提取失败'}
                features_data.append(pet_with_features)
        
        print(f"✅ 特征提取完成，共处理 {len(features_data)} 条数据")
        return features_data
    
    def analyze_addon_status_distribution(self, features_data: list) -> dict:
        """
        分析addon_status字段的分布情况
        
        Args:
            features_data: 包含特征的数据列表
            
        Returns:
            dict: 分析结果
        """
        print("📊 开始分析addon_status字段分布...")
        
        # 统计addon_status字段值
        addon_status_values = []
        for pet in features_data:
            addon_status = pet.get('addon_status', '')
            if addon_status is None:
                addon_status = ''
            addon_status_values.append(str(addon_status))
        
        # 使用Counter统计
        status_counter = Counter(addon_status_values)
        
        # 计算总数
        total_count = len(addon_status_values)
        
        # 构建分析结果
        analysis_result = {
            'total_count': total_count,
            'unique_values': len(status_counter),
            'distribution': {},
            'top_values': [],
            'empty_count': 0,
            'non_empty_count': 0
        }
        
        # 计算每个值的数量和占比
        for status, count in status_counter.most_common():
            percentage = (count / total_count) * 100
            analysis_result['distribution'][status] = {
                'count': count,
                'percentage': percentage
            }
            
            # 统计空值和非空值
            if status == '' or status == 'None' or status == '提取失败':
                analysis_result['empty_count'] += count
            else:
                analysis_result['non_empty_count'] += count
        
        # 计算空值和非空值的占比
        analysis_result['empty_percentage'] = (analysis_result['empty_count'] / total_count) * 100
        analysis_result['non_empty_percentage'] = (analysis_result['non_empty_count'] / total_count) * 100
        
        # 获取前10个最常见的值
        analysis_result['top_values'] = status_counter.most_common(10)
        
        return analysis_result
    
    def print_analysis_results(self, analysis_result: dict):
        """打印分析结果"""
        print("\n" + "="*60)
        print("📊 宠物装备addon_status字段分布分析结果")
        print("="*60)
        
        print(f"📈 总数据量: {analysis_result['total_count']:,}")
        print(f"🔍 唯一值数量: {analysis_result['unique_values']}")
        print(f"📝 非空值数量: {analysis_result['non_empty_count']:,} ({analysis_result['non_empty_percentage']:.2f}%)")
        print(f"🚫 空值数量: {analysis_result['empty_count']:,} ({analysis_result['empty_percentage']:.2f}%)")
        
        print("\n🏆 Top 10 最常见的addon_status值:")
        print("-" * 50)
        for i, (status, count) in enumerate(analysis_result['top_values'], 1):
            percentage = (count / analysis_result['total_count']) * 100
            status_display = status if status else "空值"
            print(f"{i:2d}. {status_display:<20} | 数量: {count:6,} | 占比: {percentage:6.2f}%")
        
        print("\n📊 详细分布情况:")
        print("-" * 50)
        for status, info in analysis_result['distribution'].items():
            status_display = status if status else "空值"
            print(f"{status_display:<25} | {info['count']:6,} | {info['percentage']:6.2f}%")
    
    def create_visualization(self, analysis_result: dict, output_dir: str = "tests/output"):
        """创建可视化图表"""
        try:
            # 创建输出目录
            os.makedirs(output_dir, exist_ok=True)
            
            # 设置中文字体
            plt.rcParams['font.sans-serif'] = ['SimHei', 'Microsoft YaHei']
            plt.rcParams['axes.unicode_minus'] = False
            
            # 1. 饼图：空值vs非空值
            plt.figure(figsize=(12, 5))
            
            plt.subplot(1, 2, 1)
            labels = ['非空值', '空值']
            sizes = [analysis_result['non_empty_count'], analysis_result['empty_count']]
            colors = ['#ff9999', '#66b3ff']
            
            plt.pie(sizes, labels=labels, colors=colors, autopct='%1.1f%%', startangle=90)
            plt.title('addon_status字段空值分布')
            
            # 2. 柱状图：Top 10值
            plt.subplot(1, 2, 2)
            top_values = analysis_result['top_values'][:10]
            statuses = [status if status else "空值" for status, _ in top_values]
            counts = [count for _, count in top_values]
            
            plt.bar(range(len(statuses)), counts, color='skyblue')
            plt.xlabel('addon_status值')
            plt.ylabel('数量')
            plt.title('Top 10 addon_status值分布')
            plt.xticks(range(len(statuses)), statuses, rotation=45, ha='right')
            
            plt.tight_layout()
            plt.savefig(f"{output_dir}/pet_addon_status_analysis.png", dpi=300, bbox_inches='tight')
            print(f"📊 可视化图表已保存到: {output_dir}/pet_addon_status_analysis.png")
            
        except Exception as e:
            print(f"⚠️ 创建可视化图表失败: {str(e)}")
    
    def export_to_csv(self, features_data: list, analysis_result: dict, output_dir: str = "tests/output"):
        """导出数据到CSV文件"""
        try:
            os.makedirs(output_dir, exist_ok=True)
            
            # 导出特征数据
            df_features = pd.DataFrame(features_data)
            csv_path = f"{output_dir}/pet_features_with_addon_status.csv"
            df_features.to_csv(csv_path, index=False, encoding='utf-8-sig')
            print(f"📄 特征数据已导出到: {csv_path}")
            
            # 导出分布统计
            distribution_data = []
            for status, info in analysis_result['distribution'].items():
                distribution_data.append({
                    'addon_status': status if status else "空值",
                    'count': info['count'],
                    'percentage': info['percentage']
                })
            
            df_distribution = pd.DataFrame(distribution_data)
            csv_path = f"{output_dir}/addon_status_distribution.csv"
            df_distribution.to_csv(csv_path, index=False, encoding='utf-8-sig')
            print(f"📄 分布统计已导出到: {csv_path}")
            
        except Exception as e:
            print(f"⚠️ 导出CSV失败: {str(e)}")
    
    def close_connection(self):
        """关闭数据库连接"""
        if self.connection:
            self.connection.close()
            print("🔒 数据库连接已关闭")

def main():
    """主函数"""
    print("🚀 开始分析宠物装备addon_status字段分布...")
    
    # 数据库路径
    db_path = r".\data\202508\cbg_pets_202508.db"
    
    # 创建分析器
    analyzer = PetAddonStatusAnalyzer(db_path)
    
    try:
        # 连接数据库
        if not analyzer.connect_database():
            return
        
        # 获取宠物数据（限制数量以加快测试）
        print("\n📥 获取宠物数据...")
        pets_data = analyzer.get_pet_data(limit=1000)  # 限制1000条用于测试
        
        if not pets_data:
            print("❌ 没有获取到宠物数据")
            return
        
        # 提取特征
        print("\n🔍 提取宠物装备特征...")
        features_data = analyzer.extract_features_for_pets(pets_data)
        
        if not features_data:
            print("❌ 特征提取失败")
            return
        
        # 分析addon_status分布
        print("\n📊 分析addon_status字段分布...")
        analysis_result = analyzer.analyze_addon_status_distribution(features_data)
        
        # 打印分析结果
        analyzer.print_analysis_results(analysis_result)
        
        # 创建可视化图表
        print("\n📈 创建可视化图表...")
        analyzer.create_visualization(analysis_result)
        
        # 导出数据到CSV
        print("\n📄 导出数据到CSV...")
        analyzer.export_to_csv(features_data, analysis_result)
        
        print("\n🎉 分析完成！")
        
    except Exception as e:
        print(f"❌ 分析过程中出现错误: {str(e)}")
        import traceback
        traceback.print_exc()
    
    finally:
        # 关闭数据库连接
        analyzer.close_connection()

if __name__ == "__main__":
    main()