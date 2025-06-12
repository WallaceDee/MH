import sqlite3
import json
from feature_extractor import FeatureExtractor
import pandas as pd
from datetime import datetime
import logging
import traceback

# 配置日志
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def test_feature_extraction():
    # 创建特征提取器
    extractor = FeatureExtractor()
    
    # 连接数据库
    db_path = 'data/cbg_data_202506.db'
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
            FROM characters c
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
            character_data = dict(zip(columns, row))
            
            # 打印原始数据
            if i <= 1:  # 只打印第一个角色的原始数据
                logger.info("原始数据示例:")
                for key, value in list(character_data.items())[:5]:
                    logger.info(f"{key}: {value}")
            
            try:
                # 提取特征
                features = extractor.extract_features(character_data)
                all_features.append(features)
                
                # 打印角色基本信息
                print("\n" + "="*50)
                print(f"角色ID: {character_data.get('equip_id', 'N/A')}")
                print(f"服务器: {character_data.get('server_name', 'N/A')}")
                print(f"门派: {character_data.get('school', 'N/A')}")
                print(f"等级: {character_data.get('level', 'N/A')}")
                print(f"价格: {character_data.get('price', 'N/A')}")
                
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
    input("\n按回车键退出...")

if __name__ == "__main__":
    test_feature_extraction() 