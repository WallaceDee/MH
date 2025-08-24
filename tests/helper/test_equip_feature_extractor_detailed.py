#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
详细对比测试：分析正常特征提取和large_equip_desc方式特征提取的具体差异
"""

import sys
import os
import sqlite3
import time
import json
from typing import Dict, List, Any, Tuple
import pandas as pd

# 添加项目根目录到Python路径
current_dir = os.path.dirname(__file__)
project_root = os.path.join(current_dir, '..', '..')
sys.path.insert(0, project_root)
sys.path.insert(0, os.path.join(project_root, 'src'))

from src.evaluator.feature_extractor.equip_feature_extractor import EquipFeatureExtractor


class DetailedComparisonTest:
    """详细对比测试类"""
    
    def __init__(self, db_path: str = None):
        if db_path is None:
            # 使用绝对路径
            current_dir = os.path.dirname(__file__)
            project_root = os.path.join(current_dir, '..', '..')
            db_path = os.path.join(project_root, 'data', '202508', 'cbg_equip_202508.db')
        
        self.db_path = db_path
        self.extractor = EquipFeatureExtractor()
        self.excluded_kindids = [29, 61, 62, 63, 64]  # 排除的装备类型ID
        
    def connect_database(self) -> sqlite3.Connection:
        """连接数据库"""
        try:
            conn = sqlite3.connect(self.db_path)
            print(f"✅ 成功连接到数据库: {self.db_path}")
            return conn
        except Exception as e:
            print(f"❌ 连接数据库失败: {e}")
            raise
    
    def get_test_data(self, conn: sqlite3.Connection, limit: int = 10) -> List[Dict[str, Any]]:
        """获取测试数据，排除指定kindid的装备"""
        try:
            # 构建排除条件
            excluded_conditions = " AND ".join([f"kindid != {kid}" for kid in self.excluded_kindids])
            
            query = f"""
            SELECT * FROM equipments 
            WHERE {excluded_conditions}
            AND large_equip_desc IS NOT NULL 
            AND large_equip_desc != ''
            AND kindid IS NOT NULL
            AND equip_level IS NOT NULL
            LIMIT {limit}
            """
            
            df = pd.read_sql_query(query, conn)
            print(f"✅ 获取到 {len(df)} 条测试数据")
            
            # 转换为字典列表
            data_list = df.to_dict('records')
            return data_list
            
        except Exception as e:
            print(f"❌ 获取测试数据失败: {e}")
            raise
    
    def extract_features_normal(self, equip_data: Dict[str, Any]) -> Dict[str, Any]:
        """正常方式特征提取"""
        try:
            return self.extractor.extract_features(equip_data)
        except Exception as e:
            print(f"❌ 正常特征提取失败: {e}")
            return {}
    
    def extract_features_desc_only(self, equip_data: Dict[str, Any]) -> Dict[str, Any]:
        """仅使用large_equip_desc的特征提取"""
        try:
            # 创建只有large_equip_desc的数据
            desc_only_data = {
                'cDesc': equip_data.get('large_equip_desc', ''),
                'iType': int(equip_data.get('equip_type', 0))
            }
            return self.extractor.extract_features(desc_only_data)
        except Exception as e:
            print(f"❌ desc_only特征提取失败: {e}")
            return {}
    
    def analyze_differences(self, normal_features: Dict[str, Any], desc_features: Dict[str, Any]) -> Dict[str, Any]:
        """详细分析两种特征提取结果的差异"""
        analysis = {
            'identical': True,
            'missing_in_normal': [],
            'missing_in_desc': [],
            'value_differences': {},
            'summary': {}
        }
        
        # 获取所有特征键
        all_keys = set(normal_features.keys()) | set(desc_features.keys())
        
        for key in all_keys:
            normal_value = normal_features.get(key)
            desc_value = desc_features.get(key)
            
            # 检查缺失
            if key not in normal_features:
                analysis['missing_in_normal'].append(key)
                analysis['identical'] = False
            elif key not in desc_features:
                analysis['missing_in_desc'].append(key)
                analysis['identical'] = False
            else:
                # 检查值差异
                if normal_value != desc_value:
                    # 对于列表类型，检查内容是否相同（忽略顺序）
                    if isinstance(normal_value, list) and isinstance(desc_value, list):
                        if sorted(normal_value) == sorted(desc_value):
                            # 内容相同但顺序不同，不算作差异
                            continue
                    
                    analysis['value_differences'][key] = {
                        'normal': normal_value,
                        'desc_only': desc_value,
                        'difference': self._calculate_difference(normal_value, desc_value)
                    }
                    analysis['identical'] = False
        
        # 生成摘要
        analysis['summary'] = {
            'total_features': len(all_keys),
            'identical_features': len(all_keys) - len(analysis['value_differences']) - len(analysis['missing_in_normal']) - len(analysis['missing_in_desc']),
            'different_features': len(analysis['value_differences']),
            'missing_features': len(analysis['missing_in_normal']) + len(analysis['missing_in_desc'])
        }
        
        return analysis
    
    def _calculate_difference(self, normal_value, desc_value):
        """计算两个值的差异"""
        try:
            if isinstance(normal_value, (int, float)) and isinstance(desc_value, (int, float)):
                return desc_value - normal_value
            elif isinstance(normal_value, str) and isinstance(desc_value, str):
                return f"字符串长度差异: {len(desc_value) - len(normal_value)}"
            elif isinstance(normal_value, list) and isinstance(desc_value, list):
                # 对于列表，检查内容是否相同（忽略顺序）
                if sorted(normal_value) == sorted(desc_value):
                    return "内容相同但顺序不同"
                else:
                    return f"列表内容不同: {normal_value} vs {desc_value}"
            else:
                return f"类型不同: {type(normal_value)} vs {type(desc_value)}"
        except:
            return "无法计算差异"
    
    def run_detailed_test(self, limit: int = 5) -> Dict[str, Any]:
        """运行详细对比测试"""
        print(f"\n🔍 开始详细对比测试 (限制 {limit} 条数据)")
        print("=" * 80)
        
        results = {
            'total_tested': 0,
            'successful_comparisons': 0,
            'identical_results': 0,
            'different_results': 0,
            'failed_extractions': 0,
            'detailed_analyses': [],
            'performance': {}
        }
        
        try:
            # 连接数据库
            conn = self.connect_database()
            
            # 获取测试数据
            test_data = self.get_test_data(conn, limit)
            results['total_tested'] = len(test_data)
            
            if not test_data:
                print("❌ 没有找到符合条件的测试数据")
                return results
            
            # 开始测试
            start_time = time.time()
            
            for i, equip_data in enumerate(test_data, 1):
                try:
                    # 正常特征提取
                    normal_start = time.time()
                    normal_features = self.extract_features_normal(equip_data)
                    normal_time = time.time() - normal_start
                    
                    # desc_only特征提取
                    desc_start = time.time()
                    desc_features = self.extract_features_desc_only(equip_data)
                    desc_time = time.time() - desc_start
                    
                    # 详细分析差异
                    analysis = self.analyze_differences(normal_features, desc_features)
                    
                    if analysis['identical']:
                        results['identical_results'] += 1
                        # 完全一致的数据不输出日志
                    else:
                        results['different_results'] += 1
                        print(f"\n📊 详细分析进度: {i}/{len(test_data)}")
                        print(f"装备ID: {equip_data.get('id', 'N/A')}, 类型: {equip_data.get('kindid', 'N/A')}")
                        print(f"装备名称: {equip_data.get('equip_name', 'N/A')}")
                        print("⚠️ 结果存在差异",equip_data.get('large_equip_desc', ''))
                        
                        # 打印详细差异
                        self._print_detailed_analysis(analysis, normal_time, desc_time)
                    
                    # 记录详细分析
                    detailed_analysis = {
                        'equip_id': equip_data.get('id'),
                        'kindid': equip_data.get('kindid'),
                        'equip_name': equip_data.get('equip_name'),
                        'analysis': analysis,
                        'normal_time': normal_time,
                        'desc_time': desc_time,
                        'large_equip_desc_preview': equip_data.get('large_equip_desc', '')[:200] + '...' if len(equip_data.get('large_equip_desc', '')) > 200 else equip_data.get('large_equip_desc', '')
                    }
                    results['detailed_analyses'].append(detailed_analysis)
                    
                    results['successful_comparisons'] += 1
                    
                except Exception as e:
                    results['failed_extractions'] += 1
                    print(f"❌ 特征提取失败: {e}")
                    continue
            
            total_time = time.time() - start_time
            results['performance'] = {
                'total_time': total_time,
                'avg_time_per_equip': total_time / len(test_data) if test_data else 0
            }
            
            # 关闭数据库连接
            conn.close()
            
        except Exception as e:
            print(f"❌ 测试过程中发生错误: {e}")
            results['performance'] = {
                'total_time': 0,
                'avg_time_per_equip': 0
            }
        
        return results
    
    def _print_detailed_analysis(self, analysis: Dict[str, Any], normal_time: float, desc_time: float):
        """打印详细分析结果"""
        print(f"  ⏱️ 性能对比: 正常={normal_time:.4f}s, desc_only={desc_time:.4f}s")
        print(f"  📊 摘要: 总特征={analysis['summary']['total_features']}, 一致={analysis['summary']['identical_features']}, 差异={analysis['summary']['different_features']}, 缺失={analysis['summary']['missing_features']}")
        
        if analysis['missing_in_normal']:
            print(f"  ❌ 正常方式缺失: {analysis['missing_in_normal']}")
        
        if analysis['missing_in_desc']:
            print(f"  ❌ desc_only方式缺失: {analysis['missing_in_desc']}")
        
        if analysis['value_differences']:
            print(f"  🔍 值差异 (前5个):")
            for i, (key, diff) in enumerate(list(analysis['value_differences'].items())[:5]):
                print(f"    {key}: 正常={diff['normal']}, desc_only={diff['desc_only']}, 差异={diff['difference']}")
    
    def print_summary(self, results: Dict[str, Any]):
        """打印测试总结"""
        print("\n" + "=" * 80)
        print("📊 详细对比测试总结")
        print("=" * 80)
        
        print(f"总测试数量: {results['total_tested']}")
        print(f"成功对比数量: {results['successful_comparisons']}")
        print(f"完全一致数量: {results['identical_results']}")
        print(f"存在差异数量: {results['different_results']}")
        print(f"提取失败数量: {results['failed_extractions']}")
        
        if results['successful_comparisons'] > 0:
            accuracy = (results['identical_results'] / results['successful_comparisons']) * 100
            print(f"一致率: {accuracy:.2f}%")
        
        print(f"\n⏱️ 性能统计:")
        print(f"总耗时: {results['performance']['total_time']:.3f}秒")
        print(f"平均每件装备: {results['performance']['avg_time_per_equip']:.4f}秒")
        
        # 分析差异模式
        if results['detailed_analyses']:
            print(f"\n🔍 差异模式分析:")
            
            # 统计最常见的差异字段
            diff_fields = {}
            for analysis in results['detailed_analyses']:
                for field in analysis['analysis']['value_differences'].keys():
                    diff_fields[field] = diff_fields.get(field, 0) + 1
            
            if diff_fields:
                print("最常见的差异字段:")
                sorted_fields = sorted(diff_fields.items(), key=lambda x: x[1], reverse=True)
                for field, count in sorted_fields[:10]:
                    print(f"  {field}: {count}次")
        
        print("\n" + "=" * 80)


def main():
    """主函数"""
    print("🚀 启动详细对比测试")
    
    # 创建测试实例
    test = DetailedComparisonTest()
    
    # 运行测试
    results = test.run_detailed_test(limit=50)
    
    # 打印总结
    test.print_summary(results)
    
    print("\n✅ 详细测试完成！")


if __name__ == "__main__":
    main() 