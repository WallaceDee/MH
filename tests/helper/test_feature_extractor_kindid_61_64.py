import sqlite3
import sys
import os
from typing import Dict, Any, List

# 添加项目根目录到Python路径
current_dir = os.path.dirname(__file__)
project_root = os.path.join(current_dir, '..', '..')
sys.path.insert(0, project_root)

from src.evaluator.feature_extractor.lingshi_feature_extractor import LingshiFeatureExtractor


class KindId61_64FeatureExtractorTest:
    """kindid为61/62/63/64装备的特征提取器对比测试类"""
    
    def __init__(self):
        """初始化测试类"""
        self.db_path = os.path.join(os.path.dirname(__file__), '../../data/202507/cbg_equip_202507.db')
        self.extractor = LingshiFeatureExtractor()
        
    def get_test_data(self, limit: int = 100) -> List[Dict[str, Any]]:
        """
        从数据库获取kindid为61/62/63/64的测试数据
        
        Args:
            limit: 限制返回的记录数量
            
        Returns:
            List[Dict[str, Any]]: 测试数据列表
        """
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            # 查询kindid为61/62/63/64的数据
            query = """
            SELECT * FROM equipments 
            WHERE kindid IN (61, 62, 63, 64) 
            AND (desc IS NOT NULL AND desc != '' OR large_equip_desc IS NOT NULL AND large_equip_desc != '')
            LIMIT ?
            """
            
            cursor.execute(query, (limit,))
            rows = cursor.fetchall()
            
            # 获取列名
            columns = [description[0] for description in cursor.description]
            
            # 转换为字典列表
            data = []
            for row in rows:
                row_dict = dict(zip(columns, row))
                data.append(row_dict)
                
            conn.close()
            return data
            
        except Exception as e:
            print(f"获取测试数据失败: {e}")
            return []
    
    def extract_features_multi_params(self, equip_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        使用多参数方式提取特征
        
        Args:
            equip_data: 完整的装备数据
            
        Returns:
            Dict[str, Any]: 提取的特征
        """
        try:
            return self.extractor.extract_features(equip_data)
        except Exception as e:
            print(f"多参数特征提取失败: {e}")
            return {}
    
    def extract_features_desc_only(self, equip_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        使用单cDesc和iType方式提取特征
        
        Args:
            equip_data: 装备数据，只包含cDesc和equip_type
            
        Returns:
            Dict[str, Any]: 提取的特征
        """
        try:
            # 使用large_equip_desc作为cDesc，equip_type作为iType
            # equip_type是字符串，需要转换为整数
            equip_type_str = equip_data.get('equip_type', '0')
            try:
                equip_type_int = int(equip_type_str)
            except (ValueError, TypeError):
                equip_type_int = 0
            
            desc_only_data = {
                'cDesc': equip_data.get('large_equip_desc', ''),
                'iType': equip_type_int
            }
            return self.extractor.extract_features(desc_only_data)
        except Exception as e:
            print(f"单参数特征提取失败: {e}")
            return {}
    
    def compare_features_detailed(self, features1: Dict[str, Any], features2: Dict[str, Any]) -> Dict[str, Any]:
        """
        详细对比两个特征字典的差异，对比每个字段是否相同
        
        Args:
            features1: 第一个特征字典（多参数方式）
            features2: 第二个特征字典（单参数方式）
            
        Returns:
            Dict[str, Any]: 详细差异分析结果
        """
        comparison = {
            'identical': True,
            'field_comparisons': {},
            'missing_in_1': [],
            'missing_in_2': [],
            'summary': {}
        }
        
        # 获取所有键
        all_keys = set(features1.keys()) | set(features2.keys())
        
        # 详细对比每个字段
        for key in all_keys:
            value1 = features1.get(key)
            value2 = features2.get(key)
            
            # 特殊处理：attrs字段忽略顺序
            values_identical = False
            if key == 'attrs':
                # 如果都是列表，比较内容是否相同（忽略顺序）
                if isinstance(value1, list) and isinstance(value2, list):
                    # 对每个属性对象进行排序比较
                    if len(value1) == len(value2):
                        # 按属性类型和值排序后比较
                        sorted1 = sorted(value1, key=lambda x: (x.get('attr_type', ''), x.get('attr_value', 0)))
                        sorted2 = sorted(value2, key=lambda x: (x.get('attr_type', ''), x.get('attr_value', 0)))
                        values_identical = sorted1 == sorted2
                    else:
                        values_identical = False
                else:
                    values_identical = value1 == value2
            else:
                values_identical = value1 == value2
            
            field_comparison = {
                'key': key,
                'multi_params_value': value1,
                'desc_only_value': value2,
                'is_present_in_multi': key in features1,
                'is_present_in_desc': key in features2,
                'values_identical': values_identical,
                'value_type_multi': type(value1).__name__ if value1 is not None else 'None',
                'value_type_desc': type(value2).__name__ if value2 is not None else 'None'
            }
            
            comparison['field_comparisons'][key] = field_comparison
            
            # 检查是否缺失
            if key not in features1:
                comparison['missing_in_1'].append(key)
                comparison['identical'] = False
            elif key not in features2:
                comparison['missing_in_2'].append(key)
                comparison['identical'] = False
            elif not values_identical:
                comparison['identical'] = False
        
        # 生成摘要
        identical_fields = sum(1 for fc in comparison['field_comparisons'].values() 
                             if fc['is_present_in_multi'] and fc['is_present_in_desc'] and fc['values_identical'])
        different_fields = sum(1 for fc in comparison['field_comparisons'].values() 
                             if fc['is_present_in_multi'] and fc['is_present_in_desc'] and not fc['values_identical'])
        
        comparison['summary'] = {
            'total_fields': len(all_keys),
            'identical_fields': identical_fields,
            'different_fields': different_fields,
            'missing_in_multi': len(comparison['missing_in_1']),
            'missing_in_desc': len(comparison['missing_in_2']),
            'total_issues': different_fields + len(comparison['missing_in_1']) + len(comparison['missing_in_2'])
        }
        
        return comparison
    
    def analyze_by_kindid(self, test_count: int = 100):
        """
        按kindid分组分析差异
        
        Args:
            test_count: 测试的装备数量
        """
        print(f"开始kindid 61/62/63/64灵饰装备特征提取对比分析")
        print("=" * 100)
        
        # 获取测试数据
        test_data = self.get_test_data(test_count)
        
        if not test_data:
            print("未获取到测试数据")
            return
        
        print(f"成功获取 {len(test_data)} 条测试数据")
        print()
        
        # 按kindid分组
        kindid_groups = {}
        for equip_data in test_data:
            kindid = equip_data.get('kindid')
            if kindid not in kindid_groups:
                kindid_groups[kindid] = []
            kindid_groups[kindid].append(equip_data)
        
        # 统计信息
        total_stats = {
            'total_equipments': len(test_data),
            'identical_count': 0,
            'different_count': 0,
            'total_issues': 0,
            'issue_summary': {},
            'kindid_stats': {}
        }
        
        # 按kindid分析
        for kindid in sorted(kindid_groups.keys()):
            print(f"【kindid {kindid} 分析】")
            print(f"装备数量: {len(kindid_groups[kindid])}")
            
            kindid_stats = {
                'count': len(kindid_groups[kindid]),
                'identical_count': 0,
                'different_count': 0,
                'total_issues': 0,
                'issue_summary': {}
            }
            
            for i, equip_data in enumerate(kindid_groups[kindid], 1):
                # 提取特征
                features_multi = self.extract_features_multi_params(equip_data)
                features_desc = self.extract_features_desc_only(equip_data)
                
                # 详细对比特征
                comparison = self.compare_features_detailed(features_multi, features_desc)
                
                if comparison['identical']:
                    kindid_stats['identical_count'] += 1
                    total_stats['identical_count'] += 1
                else:
                    kindid_stats['different_count'] += 1
                    total_stats['different_count'] += 1
                    kindid_stats['total_issues'] += comparison['summary']['total_issues']
                    total_stats['total_issues'] += comparison['summary']['total_issues']
                    
                    # 记录问题字段
                    for field_name, field_comp in comparison['field_comparisons'].items():
                        if not field_comp['values_identical'] or not field_comp['is_present_in_multi'] or not field_comp['is_present_in_desc']:
                            if field_name not in kindid_stats['issue_summary']:
                                kindid_stats['issue_summary'][field_name] = 0
                            kindid_stats['issue_summary'][field_name] += 1
                            
                            if field_name not in total_stats['issue_summary']:
                                total_stats['issue_summary'][field_name] = 0
                            total_stats['issue_summary'][field_name] += 1
                
                # 输出有差异的装备详情
                if not comparison['identical']:
                    print(f"  【装备 {i}/{len(kindid_groups[kindid])}】")
                    print(f"  装备SN: {equip_data.get('equip_sn')}")
                    print(f"  装备名称: {equip_data.get('equip_name')}")
                    print(f"  equip_type: {equip_data.get('equip_type')}")
                    print(f"  large_equip_desc: {(equip_data.get('large_equip_desc', ''))[:100]}...")
                    print(f"  agg_added_attrs: {(equip_data.get('agg_added_attrs', ''))[:100]}...")
                    
                    # 显示主要差异字段
                    print("  主要差异字段:")
                    for field_name, field_comp in comparison['field_comparisons'].items():
                        if not field_comp['values_identical'] or not field_comp['is_present_in_multi'] or not field_comp['is_present_in_desc']:
                            status = "✅" if field_comp['values_identical'] else "❌"
                            print(f"    {status} {field_name}:")
                            print(f"      多参数: {field_comp['multi_params_value']}")
                            print(f"      单参数: {field_comp['desc_only_value']}")
                    
                    print("  " + "-" * 60)
            
            # kindid统计
            print(f"  kindid {kindid} 统计:")
            print(f"    总装备数: {kindid_stats['count']}")
            print(f"    完全一致: {kindid_stats['identical_count']}")
            print(f"    存在差异: {kindid_stats['different_count']}")
            print(f"    总问题数: {kindid_stats['total_issues']}")
            
            if kindid_stats['issue_summary']:
                print(f"    问题字段:")
                sorted_issues = sorted(kindid_stats['issue_summary'].items(), key=lambda x: x[1], reverse=True)
                for field_name, count in sorted_issues:
                    percentage = (count / kindid_stats['count']) * 100
                    print(f"      {field_name}: {count}次 ({percentage:.1f}%)")
            
            total_stats['kindid_stats'][kindid] = kindid_stats
            print()
        
        # 输出总体统计
        print("\n" + "=" * 100)
        print("【总体分析报告】")
        print(f"总测试数量: {total_stats['total_equipments']}")
        print(f"完全一致: {total_stats['identical_count']} ({total_stats['identical_count']/total_stats['total_equipments']*100:.1f}%)")
        print(f"存在差异: {total_stats['different_count']} ({total_stats['different_count']/total_stats['total_equipments']*100:.1f}%)")
        print(f"总问题数量: {total_stats['total_issues']}")
        
        # 按kindid统计
        print("\n【按kindid统计】")
        for kindid in sorted(total_stats['kindid_stats'].keys()):
            stats = total_stats['kindid_stats'][kindid]
            consistency_rate = (stats['identical_count'] / stats['count']) * 100
            print(f"  kindid {kindid}: {stats['count']}件, 一致率 {consistency_rate:.1f}%, 问题数 {stats['total_issues']}")
        
        if total_stats['issue_summary']:
            print("\n【问题字段统计】")
            sorted_issues = sorted(total_stats['issue_summary'].items(), key=lambda x: x[1], reverse=True)
            for field_name, count in sorted_issues:
                percentage = (count / total_stats['total_equipments']) * 100
                print(f"  {field_name}: {count}次 ({percentage:.1f}%)")
        
        print("\n【分析结论】")
        print("1. kindid 61/62/63/64灵饰装备的特征提取一致性分析")
        print("2. 单参数模式与多参数模式的差异主要集中在:")
        if total_stats['issue_summary']:
            sorted_issues = sorted(total_stats['issue_summary'].items(), key=lambda x: x[1], reverse=True)
            for field_name, count in sorted_issues[:5]:  # 显示前5个最常见问题
                print(f"   - {field_name}: {count}次")
        print("3. 建议针对灵饰装备的特殊属性优化特征提取逻辑")
        print("4. 重点关注主属性、附加属性和套装效果的提取准确性")


def main():
    """主函数"""
    test = KindId61_64FeatureExtractorTest()
    
    # 运行kindid 61/62/63/64装备分析
    test.analyze_by_kindid(9999)


if __name__ == "__main__":
    main() 