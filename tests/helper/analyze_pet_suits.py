import sqlite3
import json
import sys
import os

# 添加src目录到Python路径
sys.path.append(os.path.join(os.path.dirname(__file__), '..', '..', 'src'))

from evaluator.feature_extractor.pet_equip_feature_extractor import PetEquipFeatureExtractor

def analyze_pet_suits():
    """分析召唤兽数据库中的装备套装类型统计 - 全量分析"""
    db_path = os.path.join(os.path.dirname(__file__), '..', '..', 'data', '202508', 'cbg_pets_202508.db')
    
    try:
        # 初始化特征提取器
        extractor = PetEquipFeatureExtractor()
        
        # 连接数据库
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        print("开始全量分析召唤兽装备套装类型...")
        print("=" * 60)
        
        # 统计有装备的召唤兽数量（通过equip_list列）
        cursor.execute("SELECT COUNT(*) FROM pets WHERE equip_list IS NOT NULL AND equip_list != '' AND equip_list != '[]'")
        total_with_equipment = cursor.fetchone()[0]
        print(f"有装备的召唤兽总数: {total_with_equipment}")
        
        # 查看equip_list列的数据样例
        print(f"\n查看equip_list列的数据样例:")
        cursor.execute("SELECT equip_list FROM pets WHERE equip_list IS NOT NULL AND equip_list != '' AND equip_list != '[]' LIMIT 3")
        sample_equip_lists = cursor.fetchall()
        
        for i, (equip_list,) in enumerate(sample_equip_lists):
            print(f"  样例{i+1}: {equip_list[:200]}...")
        
        # 分析large_equip_desc列中的套装信息
        print(f"\n分析large_equip_desc列中的套装信息:")
        
        # 查找包含套装关键词的记录
        cursor.execute("SELECT large_equip_desc FROM pets WHERE large_equip_desc IS NOT NULL AND large_equip_desc != '' AND large_equip_desc LIKE '%套装%' LIMIT 5")
        suit_descs = cursor.fetchall()
        
        if suit_descs:
            print(f"  包含'套装'关键词的装备描述数量: {len(suit_descs)}")
            print("  前3个包含套装的描述:")
            for i, (desc,) in enumerate(suit_descs[:3]):
                print(f"    套装描述{i+1}: {desc[:300]}...")
        else:
            print("  未找到包含'套装'关键词的描述")
        
        # 使用特征提取器分析套装信息 - 全量分析
        print(f"\n使用特征提取器进行全量分析套装信息...")
        
        # 获取所有有装备的召唤兽的large_equip_desc - 全量
        cursor.execute("SELECT large_equip_desc FROM pets WHERE large_equip_desc IS NOT NULL AND large_equip_desc != '' AND large_equip_desc != '[]'")
        equip_descs = cursor.fetchall()
        
        print(f"  开始分析 {len(equip_descs)} 条记录...")
        
        suit_stats = {}
        suit_categories = {}
        total_analyzed = 0
        
        # 分批处理，每1000条显示一次进度
        batch_size = 1000
        
        for i, (desc,) in enumerate(equip_descs):
            try:
                # 构造装备数据
                equip_data = {
                    'desc': desc,
                    'large_equip_desc': desc
                }
                
                # 提取特征
                features = extractor.extract_features(equip_data)
                
                # 统计套装类型
                suit_effect = features.get('suit_effect', '')
                suit_category = features.get('suit_category', '无套装')
                
                if suit_effect:
                    suit_stats[suit_effect] = suit_stats.get(suit_effect, 0) + 1
                
                suit_categories[suit_category] = suit_categories.get(suit_category, 0) + 1
                total_analyzed += 1
                
                # 显示前几个的分析结果
                if i < 5:
                    print(f"  分析结果{i+1}:")
                    print(f"    套装效果: {suit_effect}")
                    print(f"    套装分类: {suit_category}")
                    print(f"    基础属性: 速度{features.get('speed', 0)}, 气血{features.get('qixue', 0)}, 防御{features.get('fangyu', 0)}, 伤害{features.get('shanghai', 0)}")
                    print()
                
                # 显示进度
                if (i + 1) % batch_size == 0:
                    print(f"  已分析 {i + 1}/{len(equip_descs)} 条记录...")
                
            except Exception as e:
                print(f"  分析第{i+1}条记录时出错: {e}")
                continue
        
        print(f"  全量分析完成！共分析 {total_analyzed} 条记录")
        
        # 显示套装类型统计
        print(f"\n套装类型统计 (全量分析结果):")
        print("套装效果".ljust(30) + "数量".ljust(10) + "占比")
        print("-" * 50)
        
        for suit_type, count in sorted(suit_stats.items(), key=lambda x: x[1], reverse=True):
            percentage = (count / total_analyzed * 100) if total_analyzed > 0 else 0
            print(f"{str(suit_type).ljust(30)}{str(count).ljust(10)}{percentage:.2f}%")
        
        # 显示套装分类统计
        print(f"\n套装分类统计:")
        print("套装分类".ljust(20) + "数量".ljust(10) + "占比")
        print("-" * 40)
        
        for category, count in sorted(suit_categories.items(), key=lambda x: x[1], reverse=True):
            percentage = (count / total_analyzed * 100) if total_analyzed > 0 else 0
            print(f"{str(category).ljust(20)}{str(count).ljust(10)}{percentage:.2f}%")
        
        # 统计套装个数分布
        print(f"\n套装个数分布分析:")
        cursor.execute("SELECT large_equip_desc FROM pets WHERE large_equip_desc IS NOT NULL AND large_equip_desc != '' AND large_equip_desc LIKE '%套装%'")
        all_suit_descs = cursor.fetchall()
        
        suit_count_distribution = {}
        for desc, in all_suit_descs:
            try:
                equip_data = {'desc': desc, 'large_equip_desc': desc}
                features = extractor.extract_features(equip_data)
                suit_effect = features.get('suit_effect', '')
                
                if suit_effect:
                    # 计算套装个数（通过分析装备描述中的套装信息）
                    suit_count = 1  # 默认至少1个套装
                    if '套装效果：附加状态' in desc:
                        # 如果有套装效果，说明有套装
                        suit_count = 1
                    else:
                        suit_count = 0
                    
                    suit_count_distribution[suit_count] = suit_count_distribution.get(suit_count, 0) + 1
            except:
                continue
        
        print("套装个数".ljust(15) + "召唤兽数量".ljust(15) + "占比")
        print("-" * 45)
        
        total_suit_pets = sum(suit_count_distribution.values())
        for suit_count, count in sorted(suit_count_distribution.items()):
            percentage = (count / total_suit_pets * 100) if total_suit_pets > 0 else 0
            print(f"{str(suit_count).ljust(15)}{str(count).ljust(15)}{percentage:.2f}%")
        
        # 分析装备数量分布
        print(f"\n装备数量分布分析:")
        cursor.execute("SELECT equip_list FROM pets WHERE equip_list IS NOT NULL AND equip_list != '' AND equip_list != '[]'")
        all_equip_lists = cursor.fetchall()
        
        equip_count_distribution = {}
        for equip_list, in all_equip_lists:
            try:
                # 解析equip_list JSON
                if equip_list.startswith('[') and equip_list.endswith(']'):
                    equip_items = json.loads(equip_list)
                    # 过滤掉null值
                    valid_equips = [item for item in equip_items if item is not None]
                    equip_count = len(valid_equips)
                    equip_count_distribution[equip_count] = equip_count_distribution.get(equip_count, 0) + 1
                else:
                    # 如果不是JSON格式，尝试其他解析方式
                    equip_count = 1
                    equip_count_distribution[equip_count] = equip_count_distribution.get(equip_count, 0) + 1
            except:
                # 解析失败，默认为1个装备
                equip_count_distribution[1] = equip_count_distribution.get(1, 0) + 1
        
        print("装备数量".ljust(15) + "召唤兽数量".ljust(15) + "占比")
        print("-" * 45)
        
        total_pets_with_equip = sum(equip_count_distribution.values())
        for equip_count, count in sorted(equip_count_distribution.items()):
            percentage = (count / total_pets_with_equip * 100) if total_pets_with_equip > 0 else 0
            print(f"{str(equip_count).ljust(15)}{str(count).ljust(15)}{percentage:.2f}%")
        
        # 总结报告
        print(f"\n" + "="*60)
        print(f"全量分析总结报告")
        print(f"="*60)
        print(f"数据库总记录数: {total_with_equipment}")
        print(f"实际分析记录数: {total_analyzed}")
        print(f"套装类型总数: {len(suit_stats)}")
        print(f"套装分类总数: {len(suit_categories)}")
        print(f"有套装效果召唤兽数: {sum(suit_stats.values())}")
        print(f"无套装效果召唤兽数: {total_analyzed - sum(suit_stats.values())}")
        
        conn.close()
        
    except Exception as e:
        print(f"分析数据库时出错: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    analyze_pet_suits() 