import sqlite3
import sys
import os
from typing import Dict, Any, List

# 添加项目根目录到Python路径
current_dir = os.path.dirname(__file__)
project_root = os.path.join(current_dir, '..', '..')
sys.path.insert(0, project_root)

from src.evaluator.feature_extractor.equip_feature_extractor import EquipFeatureExtractor


class FeatureExtractorComparisonTest:
    """特征提取器对比测试类"""
    
    def __init__(self):
        """初始化测试类"""
        self.db_path = os.path.join(os.path.dirname(__file__), '../../data/202506/cbg_equip_202506.db')
        self.extractor = EquipFeatureExtractor()
        
    def get_test_data(self, limit: int = 10) -> List[Dict[str, Any]]:
        """
        从数据库获取测试数据
        
        Args:
            limit: 限制返回的记录数量
            
        Returns:
            List[Dict[str, Any]]: 测试数据列表
        """
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            # 查询kindid非29/61/62/63/64的数据
            # AND equip_sn == '6mI0014kypP'
            # AND large_equip_desc LIKE '%熔炼效果%'

            query = """
            SELECT * FROM equipments 
            WHERE kindid NOT IN (29, 61, 62, 63, 64) 
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
            
            # 特殊处理：special_effect字段忽略顺序
            values_identical = False
            if key == 'special_effect':
                # 如果都是列表，比较内容是否相同（忽略顺序）
                if isinstance(value1, list) and isinstance(value2, list):
                    values_identical = sorted(value1) == sorted(value2)
                else:
                    values_identical = value1 == value2
            elif key == 'init_damage':
                # 特殊处理init_damage字段：误差在10以内视为一样
                if isinstance(value1, (int, float)) and isinstance(value2, (int, float)):
                    diff = abs(value1 - value2)
                    values_identical = diff <= 10
                else:
                    values_identical = value1 == value2
            elif key == 'init_damage_raw':
                # 特殊处理init_damage_raw字段：误差在80以内视为一样
                if isinstance(value1, (int, float)) and isinstance(value2, (int, float)):
                    diff = abs(value1 - value2)
                    values_identical = diff <= 80
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
            
            # 为init_damage字段添加误差信息
            if key == 'init_damage' and isinstance(value1, (int, float)) and isinstance(value2, (int, float)):
                field_comparison['difference'] = abs(value1 - value2)
                field_comparison['within_tolerance'] = abs(value1 - value2) <= 10
            
            # 为init_damage_raw字段添加误差信息
            if key == 'init_damage_raw' and isinstance(value1, (int, float)) and isinstance(value2, (int, float)):
                field_comparison['difference'] = abs(value1 - value2)
                field_comparison['within_tolerance'] = abs(value1 - value2) <= 80
            
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
    
    def log_detailed_differences(self, test_count: int = 10):
        """
        详细记录差异日志，只输出有差异的数据
        
        Args:
            test_count: 测试的装备数量
        """
        print(f"开始详细差异分析，测试数量: {test_count}")
        print("=" * 100)
        
        # 获取测试数据
        test_data = self.get_test_data(test_count)
        
        if not test_data:
            print("未获取到测试数据")
            return
        
        print(f"成功获取 {len(test_data)} 条测试数据")
        print()
        
        # 统计信息
        total_issues = 0
        issue_summary = {}
        identical_count = 0
        different_count = 0
        
        for i, equip_data in enumerate(test_data, 1):
            # 提取特征
            features_multi = self.extract_features_multi_params(equip_data)
            features_desc = self.extract_features_desc_only(equip_data)
            
            # 详细对比特征
            comparison = self.compare_features_detailed(features_multi, features_desc)
            
            if comparison['identical']:
                identical_count += 1
                # 不输出完全一致的数据
                continue
            else:
                different_count += 1
                total_issues += comparison['summary']['total_issues']
                
                # 只输出有差异的数据
                print(f"【装备 {i}/{len(test_data)}】")
                print(f"装备SN: {equip_data.get('equip_sn')}")
                print(f"装备名称: {equip_data.get('equip_name')}")
                print(f"kindid: {equip_data.get('kindid')}")
                print(f"equip_type: {equip_data.get('equip_type')}")
                print(f"large_equip_desc: {(equip_data.get('large_equip_desc', ''))}")
                print(f"agg_added_attrs: {(equip_data.get('agg_added_attrs', ''))}")
                print("❌ 特征提取结果存在差异")
                
                # 记录每个差异字段
                print("  差异详情:")
                for field_name, field_comp in comparison['field_comparisons'].items():
                    if not field_comp['values_identical'] or not field_comp['is_present_in_multi'] or not field_comp['is_present_in_desc']:
                        status = "✅" if field_comp['values_identical'] else "❌"
                        print(f"    {status} {field_name}:")
                        print(f"      多参数: {field_comp['multi_params_value']} ({field_comp['value_type_multi']})")
                        print(f"      单参数: {field_comp['desc_only_value']} ({field_comp['value_type_desc']})")
                        
                        # 为init_damage字段显示误差信息
                        if field_name == 'init_damage' and 'difference' in field_comp:
                            diff = field_comp['difference']
                            within_tolerance = field_comp['within_tolerance']
                            tolerance_status = "✅ 在误差范围内" if within_tolerance else "❌ 超出误差范围"
                            print(f"      误差: {diff} {tolerance_status}")
                        
                        # 为init_damage_raw字段显示误差信息
                        if field_name == 'init_damage_raw' and 'difference' in field_comp:
                            diff = field_comp['difference']
                            within_tolerance = field_comp['within_tolerance']
                            tolerance_status = "✅ 在误差范围内" if within_tolerance else "❌ 超出误差范围"
                            print(f"      误差: {diff} {tolerance_status}")
                        
                        # 统计问题类型
                        if not field_comp['is_present_in_multi']:
                            print(f"      ⚠️  多参数方式缺失此字段")
                            issue_summary[field_name] = issue_summary.get(field_name, 0) + 1
                        elif not field_comp['is_present_in_desc']:
                            print(f"      ⚠️  单参数方式缺失此字段")
                            issue_summary[field_name] = issue_summary.get(field_name, 0) + 1
                        else:
                            print(f"      🔄 值不匹配")
                            issue_summary[field_name] = issue_summary.get(field_name, 0) + 1
                
                print(f"  摘要: 总字段数={comparison['summary']['total_fields']}, "
                      f"一致={comparison['summary']['identical_fields']}, "
                      f"差异={comparison['summary']['different_fields']}, "
                      f"缺失={comparison['summary']['missing_in_multi'] + comparison['summary']['missing_in_desc']}")
                print("-" * 80)
        
        # 输出总体统计
        print("\n" + "=" * 100)
        print("【总体差异统计】")
        print(f"总测试数量: {len(test_data)}")
        print(f"完全一致: {identical_count}")
        print(f"存在差异: {different_count}")
        print(f"总问题数量: {total_issues}")
        
        if issue_summary:
            print("\n【问题字段统计】")
            sorted_issues = sorted(issue_summary.items(), key=lambda x: x[1], reverse=True)
            for field_name, count in sorted_issues:
                percentage = (count / len(test_data)) * 100
                print(f"  {field_name}: {count}次 ({percentage:.1f}%)")
        
        print("\n【建议改进】")
        print("1. 检查单参数模式下的数据解析逻辑")
        print("2. 验证iType到kindid的映射关系")
        print("3. 完善large_equip_desc的解析规则")
        print("4. 修复套装效果和宝石信息的提取")


def main():
    """主函数"""
    test = FeatureExtractorComparisonTest()
    
    # 运行详细差异分析
    test.log_detailed_differences(99999)


if __name__ == "__main__":
    main() 