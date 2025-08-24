#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
更新装备数据库中的addon_moli字段
从agg_added_attrs中提取魔力属性值并更新到addon_moli字段
"""

import sqlite3
import json
import re
import sys
import os
from typing import List, Dict, Any, Optional

# 添加项目根目录到Python路径
current_dir = os.path.dirname(os.path.abspath(__file__))
project_root = os.path.dirname(os.path.dirname(current_dir))  # 回到项目根目录
sys.path.insert(0, project_root)

from src.evaluator.constants.equipment_types import WEAPON_KINDIDS, ARMOR_KINDIDS
from src.evaluator.feature_extractor.equip_feature_extractor import EquipFeatureExtractor

class AddonMoliUpdater:
    """装备魔力属性更新器"""
    
    def __init__(self, db_path: str):
        self.db_path = db_path
        self.feature_extractor = EquipFeatureExtractor()
        self.conn = None
        self.cursor = None
        
    def connect(self):
        """连接数据库"""
        try:
            self.conn = sqlite3.connect(self.db_path)
            self.cursor = self.conn.cursor()
            print(f"✅ 成功连接到数据库: {self.db_path}")
        except Exception as e:
            print(f"❌ 连接数据库失败: {e}")
            raise
    
    def close(self):
        """关闭数据库连接"""
        if self.cursor:
            self.cursor.close()
        if self.conn:
            self.conn.close()
        print("✅ 数据库连接已关闭")
    
    def get_equipment_count(self) -> int:
        """获取装备总数"""
        self.cursor.execute("SELECT COUNT(*) FROM equipments")
        return self.cursor.fetchone()[0]
    
    def get_weapon_armor_count(self) -> int:
        """获取武器和防具装备数量"""
        weapon_armor_kindids = WEAPON_KINDIDS + ARMOR_KINDIDS
        placeholders = ','.join(['?' for _ in weapon_armor_kindids])
        query = f"SELECT COUNT(*) FROM equipments WHERE kindid IN ({placeholders})"
        self.cursor.execute(query, weapon_armor_kindids)
        return self.cursor.fetchone()[0]
    
    def get_equipment_data(self, batch_size: int = 1000) -> List[tuple]:
        """获取装备数据，分批处理"""
        weapon_armor_kindids = WEAPON_KINDIDS + ARMOR_KINDIDS
        placeholders = ','.join(['?' for _ in weapon_armor_kindids])
        
        query = f"""
        SELECT eid, kindid, agg_added_attrs, addon_moli 
        FROM equipments 
        WHERE kindid IN ({placeholders})
        ORDER BY eid
        LIMIT ? OFFSET ?
        """
        
        offset = 0
        while True:
            self.cursor.execute(query, weapon_armor_kindids + [batch_size, offset])
            batch = self.cursor.fetchall()
            
            if not batch:
                break
                
            yield batch
            offset += batch_size
    
    def extract_moli_from_agg_added_attrs(self, agg_added_attrs) -> int:
        """从agg_added_attrs中提取魔力属性值"""
        try:
            # 处理agg_added_attrs的不同格式
            if isinstance(agg_added_attrs, str):
                # 如果是字符串，尝试解析为JSON
                try:
                    attrs_list = json.loads(agg_added_attrs)
                except (json.JSONDecodeError, TypeError):
                    # 如果解析失败，尝试直接处理字符串
                    attrs_list = [agg_added_attrs]
            elif isinstance(agg_added_attrs, list):
                attrs_list = agg_added_attrs
            else:
                return 0

            # 遍历所有属性字符串，查找魔力属性
            for attr in attrs_list:
                if isinstance(attr, str) and "魔力" in attr:
                    # 使用正则表达式提取魔力数值，支持正负值
                    moli_match = re.search(r'魔力\s*([+-]?)\s*(\d+(?:\.\d+)?)', attr)
                    if moli_match:
                        value = int(moli_match.group(2))
                        # 如果是负值，取负
                        if moli_match.group(1) == '-':
                            value = -value
                        return value

            return 0

        except Exception as e:
            print(f"⚠️ 提取魔力属性时出错: {e}")
            return 0
    
    def update_addon_moli(self, eid: int, new_moli: int, old_moli: int) -> bool:
        """更新装备的addon_moli字段"""
        try:
            self.cursor.execute(
                "UPDATE equipments SET addon_moli = ? WHERE eid = ?",
                (new_moli, eid)
            )
            return True
        except Exception as e:
            print(f"❌ 更新装备 {eid} 失败: {e}")
            return False
    
    def process_equipment_batch(self, batch: List[tuple]) -> Dict[str, int]:
        """处理一批装备数据"""
        stats = {
            'processed': 0,
            'updated': 0,
            'errors': 0,
            'no_change': 0
        }
        
        for eid, kindid, agg_added_attrs, old_moli in batch:
            try:
                stats['processed'] += 1
                
                # 提取魔力属性
                new_moli = self.extract_moli_from_agg_added_attrs(agg_added_attrs)
                
                # 检查是否需要更新
                if new_moli != old_moli:
                    if self.update_addon_moli(eid, new_moli, old_moli):
                        stats['updated'] += 1
                        print(f"✅ 更新装备 {eid} (kindid:{kindid}): 魔力 {old_moli} -> {new_moli}")
                    else:
                        stats['errors'] += 1
                else:
                    stats['no_change'] += 1
                    
            except Exception as e:
                stats['errors'] += 1
                print(f"❌ 处理装备 {eid} 时出错: {e}")
        
        return stats
    
    def run_update(self, batch_size: int = 1000):
        """运行更新流程"""
        try:
            # 连接数据库
            self.connect()
            
            # 获取统计信息
            total_equipment = self.get_equipment_count()
            weapon_armor_count = self.get_weapon_armor_count()
            
            print(f"📊 数据库统计信息:")
            print(f"  总装备数量: {total_equipment}")
            print(f"  武器防具数量: {weapon_armor_count}")
            print(f"  批处理大小: {batch_size}")
            print()
            
            # 开始处理
            print("🔄 开始更新addon_moli字段...")
            
            total_stats = {
                'processed': 0,
                'updated': 0,
                'errors': 0,
                'no_change': 0
            }
            
            batch_num = 0
            for batch in self.get_equipment_data(batch_size):
                batch_num += 1
                print(f"📦 处理第 {batch_num} 批数据 ({len(batch)} 条)...")
                
                batch_stats = self.process_equipment_batch(batch)
                
                # 累加统计
                for key in total_stats:
                    total_stats[key] += batch_stats[key]
                
                print(f"   批次统计: 处理={batch_stats['processed']}, 更新={batch_stats['updated']}, 无变化={batch_stats['no_change']}, 错误={batch_stats['errors']}")
                print()
            
            # 提交事务
            self.conn.commit()
            
            # 输出最终统计
            print("🎉 更新完成！")
            print(f"📊 最终统计:")
            print(f"  总处理: {total_stats['processed']}")
            print(f"  成功更新: {total_stats['updated']}")
            print(f"  无变化: {total_stats['no_change']}")
            print(f"  错误: {total_stats['errors']}")
            
        except Exception as e:
            print(f"❌ 更新过程中出现错误: {e}")
            if self.conn:
                self.conn.rollback()
            raise
        finally:
            self.close()

def main():
    """主函数"""
    # 数据库路径 - 使用相对路径
    project_root = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
    db_path = os.path.join(project_root, "data", "202507", "cbg_equip_202507.db")
    
    # 检查数据库文件是否存在
    if not os.path.exists(db_path):
        print(f"❌ 数据库文件不存在: {db_path}")
        print(f"   请检查数据库文件路径是否正确")
        return
    
    # 创建更新器并运行
    updater = AddonMoliUpdater(db_path)
    
    try:
        updater.run_update(batch_size=1000)
    except KeyboardInterrupt:
        print("\n⚠️ 用户中断操作")
    except Exception as e:
        print(f"❌ 程序执行失败: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main() 