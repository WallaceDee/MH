import sys
import os

# 添加项目根目录到Python路径，解决模块导入问题
current_dir = os.path.dirname(os.path.abspath(__file__))
project_root = os.path.dirname(os.path.dirname(current_dir))  # 向上两级到项目根目录
sys.path.insert(0, project_root)

import sqlite3
import json
from src.evaluator.feature_extractor.feature_extractor import FeatureExtractor
from src.evaluator.feature_extractor.equip_feature_extractor import EquipFeatureExtractor
from src.evaluator.feature_extractor.lingshi_feature_extractor import LingshiFeatureExtractor
from src.evaluator.feature_extractor.pet_equip_feature_extractor import PetEquipFeatureExtractor
import pandas as pd
from datetime import datetime
import logging
import traceback

# 配置日志
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def test_equipment_feature_extraction():
    """测试装备特征提取"""
    # 创建装备特征提取器
    extractor = EquipFeatureExtractor()
    
    # 连接数据库
    project_root = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
    db_path = os.path.join(project_root, 'data', '202507', 'cbg_equip_202507.db')
    logger.info(f"正在连接数据库: {db_path}")
    
    try:
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        # 先查看表结构确认字段名
        cursor.execute("PRAGMA table_info(equipments)")
        columns_info = cursor.fetchall()
        available_fields = [col[1] for col in columns_info]
        logger.info(f"可用字段数量: {len(available_fields)}")
        
        # 获取装备数据 - 使用实际存在的字段
        logger.info("正在查询装备数据...")
        cursor.execute("""
            SELECT 
                eid as equip_id, equip_level, kindid, init_damage, all_damage, 
                init_wakan, init_defense, init_hp, init_dex, mingzhong, shanghai,
                agg_added_attrs, addon_tizhi, addon_liliang, addon_naili, 
                addon_minjie, addon_fali, addon_lingli, addon_total,
                gem_value, gem_level, special_skill, special_effect,
                suit_effect, suit_skill, large_equip_desc
            FROM equipments
            WHERE equip_level > 0
            LIMIT 20
        """)
        
        # 获取列名
        columns = [description[0] for description in cursor.description]
        logger.info(f"查询字段: {columns}")
        
        rows = cursor.fetchall()
        print(f"查询到装备数量: {len(rows)}")
        if not rows:
            print("没有查询到任何装备数据，请检查数据库内容和查询条件！")
            return
        
        # 存储所有特征
        all_features = []
        
        # 处理每个装备
        for i, row in enumerate(rows, 1):
            logger.info(f"\n处理第 {i} 个装备...")
            
            # 转换为字典
            equip_data = dict(zip(columns, row))
            
            # 打印原始数据
            if i <= 2:  # 只打印前两个装备的原始数据
                logger.info("原始数据示例:")
                for key, value in list(equip_data.items())[:8]:
                    logger.info(f"{key}: {value}")
            
            try:
                # 提取特征
                features = extractor.extract_features(equip_data)
                all_features.append(features)
                
                # 打印装备基本信息
                print("\n" + "="*50)
                print(f"装备ID: {equip_data.get('equip_id', 'N/A')}")
                print(f"装备等级: {equip_data.get('equip_level', 'N/A')}")
                print(f"装备类型: {equip_data.get('kindid', 'N/A')}")
                print(f"初始伤害: {equip_data.get('init_damage', 'N/A')}")
                print(f"总伤害: {equip_data.get('all_damage', 'N/A')}")
                print(f"宝石值: {equip_data.get('gem_value', 'N/A')}")
                print(f"特技: {equip_data.get('special_skill', 'N/A')}")
                print(f"特效: {equip_data.get('special_effect', 'N/A')}")
                
                # 打印提取的特征
                print("\n提取的装备特征:")
                for category, value in features.items():
                    if isinstance(value, list) and len(value) > 5:
                        print(f"  {category}: {value[:5]}... (共{len(value)}项)")
                    else:
                        print(f"  {category}: {value}")
                
                # 如果有前5个装备，停止显示详细信息
                if i >= 5:
                    print(f"... 继续处理剩余装备（不显示详细信息）")
                    break
                
            except Exception as e:
                print(f"处理装备数据时出错: {e}")
                traceback.print_exc()
                continue
        
        # 所有装备处理完后，一次性计算统计信息
        if all_features:
            df = pd.DataFrame(all_features)
            print("\n装备特征统计:")
            print(df.describe())
            
    except Exception as e:
        print(f"数据库操作出错: {e}")
        traceback.print_exc()
    finally:
        if 'conn' in locals():
            conn.close()
            logger.info("数据库连接已关闭")

def test_feature_extraction():
    # 创建特征提取器
    extractor = FeatureExtractor()
    
    # 连接数据库
    project_root = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
    db_path = os.path.join(project_root, 'data', '202506', 'cbg_roles_202506.db')
    logger.info(f"正在连接数据库: {db_path}")
    
    try:
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        # 获取角色数据
        logger.info("正在查询角色数据...")
        cursor.execute("""
            SELECT 
                c.id, c.equip_id, c.server_name, c.seller_nickname, c.level, c.price,
                c.price_desc, c.school AS school_desc, c.area_name, c.icon_index,
                c.kindid, c.game_ordersn, c.pass_fair_show, c.fair_show_end_time,
                c.accept_bargain, c.status_desc, c.onsale_expire_time_desc, c.expire_time,
                c.race, c.fly_status, c.collect_num, c.life_skills, c.school_skills,
                c.ju_qing_skills,c.yushoushu_skill, c.all_pets_json, c.all_equip_json AS all_equip_json_desc,
                c.all_shenqi_json, c.all_rider_json AS all_rider_json_desc, c.all_fabao_json,
                c.ex_avt_json AS ex_avt_json_desc, c.create_time, c.update_time,
                
                l.*
            FROM roles c
            LEFT JOIN large_equip_desc_data l ON c.equip_id = l.equip_id
            WHERE c.price > 0 AND l.pet != '[]'
            limit 100
        """)
        
        # 获取列名
        columns = [description[0] for description in cursor.description]
        logger.info(f"数据库列名: {columns}")
        
        rows = cursor.fetchall()
        print(f"查询到角色数量: {len(rows)}")
        if not rows:
            print("没有查询到任何角色数据，请检查数据库内容和查询条件！")
            return
        
        # 存储所有特征
        all_features = []
        
        # 处理每个角色
        for i, row in enumerate(rows, 1):
            logger.info(f"\n处理第 {i} 个角色...")
            
            # 转换为字典
            role_data = dict(zip(columns, row))
            
            # 打印原始数据
            if i <= 1:  # 只打印第一个角色的原始数据
                logger.info("原始数据示例:")
                for key, value in list(role_data.items())[:5]:
                    logger.info(f"{key}: {value}")
            
            try:
                # 提取特征
                features = extractor.extract_features(role_data)
                all_features.append(features)
                
                # 打印角色基本信息
                print("\n" + "="*50)
                print(f"角色ID: {role_data.get('equip_id', 'N/A')}")
                print(f"服务器: {role_data.get('server_name', 'N/A')}")
                print(f"门派: {role_data.get('school', 'N/A')}")
                print(f"等级: {role_data.get('level', 'N/A')}")
                print(f"价格: {role_data.get('price', 'N/A')}")
                
                # 打印提取的特征
                print("\n提取的特征:")
                for category, value in features.items():
                    print(f"{category}: {value}")
                
            except Exception as e:
                print(f"处理角色数据时出错: {e}")
                traceback.print_exc()
                continue
        
        # 所有角色处理完后，一次性计算统计信息
        if all_features:
            df = pd.DataFrame(all_features)
            print("\n所有角色的特征统计:")
            print(df.describe())
            
    except Exception as e:
        print(f"数据库操作出错: {e}")
        traceback.print_exc()
    finally:
        if 'conn' in locals():
            conn.close()
            logger.info("数据库连接已关闭")

def test_lingshi_feature_extraction():
    """测试灵饰特征提取"""
    # 创建灵饰特征提取器
    extractor = LingshiFeatureExtractor()
    
    # 连接数据库
    project_root = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
    db_path = os.path.join(project_root, 'data', '202507', 'cbg_equip_202507.db')
    logger.info(f"正在连接数据库: {db_path}")
    
    try:
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        # 先查看表结构确认字段名
        cursor.execute("PRAGMA table_info(equipments)")
        columns_info = cursor.fetchall()
        available_fields = [col[1] for col in columns_info]
        logger.info(f"可用字段数量: {len(available_fields)}")
        
        # 获取灵饰装备数据 - 只查询灵饰类型（kindid 61-64）
        logger.info("正在查询灵饰装备数据...")
        cursor.execute("""
            SELECT 
                eid as equip_id, equip_level, kindid, 
                gem_value, gem_level, special_skill, special_effect,
                suit_effect, suit_skill, large_equip_desc
            FROM equipments
            WHERE equip_level > 0 AND kindid IN (61, 62, 63, 64)
            LIMIT 20
        """)
        
        # 获取列名
        columns = [description[0] for description in cursor.description]
        logger.info(f"查询字段: {columns}")
        
        rows = cursor.fetchall()
        print(f"查询到灵饰装备数量: {len(rows)}")
        if not rows:
            print("没有查询到任何灵饰装备数据，请检查数据库内容和查询条件！")
            return
        
        # 存储所有特征
        all_features = []
        
        # 处理每个灵饰装备
        for i, row in enumerate(rows, 1):
            logger.info(f"\n处理第 {i} 个灵饰装备...")
            
            # 转换为字典
            equip_data = dict(zip(columns, row))
            
            # 打印原始数据
            if i <= 2:  # 只打印前两个装备的原始数据
                logger.info("原始数据示例:")
                for key, value in list(equip_data.items())[:8]:
                    logger.info(f"{key}: {value}")
            
            try:
                # 提取特征
                features = extractor.extract_features(equip_data)
                all_features.append(features)
                
                # 打印装备基本信息
                print("\n" + "="*50)
                print(f"灵饰装备ID: {equip_data.get('equip_id', 'N/A')}")
                print(f"装备等级: {equip_data.get('equip_level', 'N/A')}")
                print(f"装备类型: {equip_data.get('kindid', 'N/A')}")
                
                # 根据kindid显示装备类型名称
                kindid = equip_data.get('kindid', 0)
                kindid_names = {61: "戒指", 62: "耳饰", 63: "手镯", 64: "佩饰"}
                print(f"装备类型名称: {kindid_names.get(kindid, '未知')}")
                
                print(f"large_equip_desc: {equip_data.get('large_equip_desc', 'N/A')[:200]}...")
                
                # 打印提取的特征
                print("\n提取的灵饰特征:")
                for category, value in features.items():
                    if isinstance(value, list) and len(value) > 5:
                        print(f"  {category}: {value[:5]}... (共{len(value)}项)")
                    else:
                        print(f"  {category}: {value}")
                
                # 如果有前5个装备，停止显示详细信息
                if i >= 5:
                    print(f"... 继续处理剩余灵饰装备（不显示详细信息）")
                    break
                
            except Exception as e:
                print(f"处理灵饰装备数据时出错: {e}")
                traceback.print_exc()
                continue
        
        # 所有装备处理完后，一次性计算统计信息
        if all_features:
            df = pd.DataFrame(all_features)
            print("\n灵饰装备特征统计:")
            print(df.describe())
            
    except Exception as e:
        print(f"数据库操作出错: {e}")
        traceback.print_exc()
    finally:
        if 'conn' in locals():
            conn.close()
            logger.info("数据库连接已关闭")

def test_pet_equipment_feature_extraction():
    """测试宠物装备特征提取"""
    # 创建宠物装备特征提取器
    extractor = PetEquipFeatureExtractor()
    
    # 连接数据库
    project_root = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
    db_path = os.path.join(project_root, 'data', '202507', 'cbg_equip_202507.db')
    logger.info(f"正在连接数据库: {db_path}")
    
    try:
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        # 先查看表结构确认字段名
        cursor.execute("PRAGMA table_info(equipments)")
        columns_info = cursor.fetchall()
        available_fields = [col[1] for col in columns_info]
        logger.info(f"可用字段数量: {len(available_fields)}")
        
        # 获取宠物装备数据 - 只查询宠物装备类型（kindid = PET_EQUIP_KINDID）
        logger.info("正在查询宠物装备数据...")
        cursor.execute("""
            SELECT 
                eid as equip_id, equip_level, kindid, 
                mingzhong, speed, qixue, fangyu, shanghai,
                addon_fali, addon_lingli, addon_liliang, addon_minjie, addon_naili,
                xiang_qian_level, addon_status, large_equip_desc
            FROM equipments
            from src.evaluator.constants.equipment_types import PET_EQUIP_KINDID
            WHERE equip_level > 0 AND kindid = {PET_EQUIP_KINDID}
            LIMIT 20
        """)
        
        # 获取列名
        columns = [description[0] for description in cursor.description]
        logger.info(f"查询字段: {columns}")
        
        rows = cursor.fetchall()
        print(f"查询到宠物装备数量: {len(rows)}")
        if not rows:
            print("没有查询到任何宠物装备数据，请检查数据库内容和查询条件！")
            return
        
        # 存储所有特征
        all_features = []
        
        # 处理每个宠物装备
        for i, row in enumerate(rows, 1):
            logger.info(f"\n处理第 {i} 个宠物装备...")
            
            # 转换为字典
            equip_data = dict(zip(columns, row))
            
            # 打印原始数据
            if i <= 2:  # 只打印前两个装备的原始数据
                logger.info("原始数据示例:")
                for key, value in list(equip_data.items())[:8]:
                    logger.info(f"{key}: {value}")
            
            try:
                # 提取特征
                features = extractor.extract_features(equip_data)
                all_features.append(features)
                
                # 打印装备基本信息
                print("\n" + "="*50)
                print(f"宠物装备ID: {equip_data.get('equip_id', 'N/A')}")
                print(f"装备等级: {equip_data.get('equip_level', 'N/A')}")
                print(f"装备类型: {equip_data.get('kindid', 'N/A')}")
                print(f"命中: {equip_data.get('mingzhong', 'N/A')}")
                print(f"速度: {equip_data.get('speed', 'N/A')}")
                print(f"气血: {equip_data.get('qixue', 'N/A')}")
                print(f"防御: {equip_data.get('fangyu', 'N/A')}")
                print(f"伤害: {equip_data.get('shanghai', 'N/A')}")
                print(f"宝石等级: {equip_data.get('xiang_qian_level', 'N/A')}")
                print(f"套装效果: {equip_data.get('addon_status', 'N/A')}")
                
                # 打印large_equip_desc的前200个字符
                large_desc = equip_data.get('large_equip_desc', '')
                if large_desc:
                    print(f"装备描述: {large_desc[:200]}...")
                
                # 打印提取的特征
                print("\n提取的宠物装备特征:")
                for category, value in features.items():
                    if isinstance(value, list) and len(value) > 5:
                        print(f"  {category}: {value[:5]}... (共{len(value)}项)")
                    else:
                        print(f"  {category}: {value}")
                
                # 如果有前5个装备，停止显示详细信息
                if i >= 5:
                    print(f"... 继续处理剩余宠物装备（不显示详细信息）")
                    break
                
            except Exception as e:
                print(f"处理宠物装备数据时出错: {e}")
                traceback.print_exc()
                continue
        
        # 所有装备处理完后，一次性计算统计信息
        if all_features:
            df = pd.DataFrame(all_features)
            print("\n宠物装备特征统计:")
            print(df.describe())
            
            # 显示特征列的数据类型
            print("\n特征数据类型:")
            for col in df.columns:
                print(f"  {col}: {df[col].dtype}")
            
    except Exception as e:
        print(f"数据库操作出错: {e}")
        traceback.print_exc()
    finally:
        if 'conn' in locals():
            conn.close()
            logger.info("数据库连接已关闭")

def main():
    """主函数，提供选择菜单"""
    print("="*60)
    print("特征提取测试工具")
    print("="*60)
    print("1. 测试装备特征提取")
    print("2. 测试角色特征提取")
    print("3. 测试灵饰特征提取")
    print("4. 测试宠物装备特征提取")
    print("5. 同时测试所有特征提取")
    print("="*60)
    
    choice = input("请选择测试类型 (1/2/3/4/5): ").strip()
    
    if choice == "1":
        print("\n开始测试装备特征提取...")
        test_equipment_feature_extraction()
    elif choice == "2":
        print("\n开始测试角色特征提取...")
        test_feature_extraction()
    elif choice == "3":
        print("\n开始测试灵饰特征提取...")
        test_lingshi_feature_extraction()
    elif choice == "4":
        print("\n开始测试宠物装备特征提取...")
        test_pet_equipment_feature_extraction()
    elif choice == "5":
        print("\n开始测试装备特征提取...")
        test_equipment_feature_extraction()
        print("\n" + "="*60)
        print("开始测试角色特征提取...")
        test_feature_extraction()
        print("\n" + "="*60)
        print("开始测试灵饰特征提取...")
        test_lingshi_feature_extraction()
        print("\n" + "="*60)
        print("开始测试宠物装备特征提取...")
        test_pet_equipment_feature_extraction()
    else:
        print("无效选择，默认测试宠物装备特征提取...")
        test_pet_equipment_feature_extraction()
    
    input("\n按回车键退出...")

if __name__ == "__main__":
    main() 