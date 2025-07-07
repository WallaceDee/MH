#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
数据修复脚本：从large_equip_desc字段中提取套装信息并更新addon_status字段
"""

import sqlite3
import os
import re
import logging
from datetime import datetime
import sys

class AddonStatusDataFixer:
    """addon_status数据修复器"""
    
    def __init__(self, db_path: str):
        self.db_path = db_path
        self.logger = self._setup_logger()
        
    def _setup_logger(self):
        """设置日志"""
        logger = logging.getLogger('AddonStatusDataFixer')
        logger.setLevel(logging.INFO)
        
        if not logger.handlers:
            handler = logging.StreamHandler()
            formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
            handler.setFormatter(formatter)
            logger.addHandler(handler)
        
        return logger
    
    def extract_suit_info(self, large_equip_desc: str) -> str:
        """
        从large_equip_desc中提取套装信息
        
        Args:
            large_equip_desc: 装备详细描述
            
        Returns:
            提取的套装信息，如果没有找到则返回空字符串
        """
        if not large_equip_desc:
            return ""
        
        # 移除颜色代码
        desc_clean = re.sub(r'#[A-Za-z0-9]{6}', '', large_equip_desc)
        desc_clean = re.sub(r'#[A-Z]', '', desc_clean)
        
        # 查找套装效果相关信息
        suit_patterns = [
            r'套装效果[：:]\s*([^#\n]+)',  # 套装效果：xxx
            r'附加状态[：:]\s*([^#\n]+)',  # 附加状态：xxx
            r'套装[：:]\s*([^#\n]+)',      # 套装：xxx
        ]
        
        for pattern in suit_patterns:
            match = re.search(pattern, desc_clean)
            if match:
                suit_info = match.group(1).strip()
                # 清理多余的空格和特殊字符
                suit_info = re.sub(r'\s+', ' ', suit_info)
                
                # 如果是"附加状态4高级强力"这样的格式，只保留"高级强力"部分
                if suit_info.startswith('附加状态'):
                    # 尝试提取"附加状态"后面的实际套装名
                    # 匹配"附加状态4高级强力"中的"高级强力"部分
                    suit_match = re.search(r'附加状态\d+(.+)', suit_info)
                    if suit_match:
                        suit_info = suit_match.group(1).strip()
                    else:
                        # 如果没有数字，直接去掉"附加状态"
                        suit_info = suit_info.replace('附加状态', '').strip()
                    # 清理多余的空格和特殊字符
                    suit_info = re.sub(r'\s+', ' ', suit_info)
                
                return suit_info
        
        return ""
    
    def fix_equipments_table(self) -> int:
        """修复equipments表中的addon_status数据"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                
                # 获取所有需要修复的记录
                cursor.execute("""
                    SELECT eid, kindid, large_equip_desc, addon_status 
                    FROM equipments 
                    WHERE large_equip_desc IS NOT NULL 
                    AND large_equip_desc != ''
                """)
                
                records = cursor.fetchall()
                print(f"找到 {len(records)} 条装备记录需要检查")
                
                updated_count = 0
                error_count = 0
                
                for record in records:
                    try:
                        eid, kindid, large_equip_desc, current_addon_status = record
                        
                        # 只有kindid=29（召唤兽装备）才提取套装信息
                        if kindid == 29:
                            # 提取套装信息
                            extracted_suit = self.extract_suit_info(large_equip_desc)
                            
                            # 对于kindid=29的装备，无论是否找到套装信息都要更新
                            if extracted_suit:
                                # 有套装信息
                                if current_addon_status != extracted_suit:
                                    cursor.execute(
                                        "UPDATE equipments SET addon_status = ? WHERE eid = ?",
                                        (extracted_suit, eid)
                                    )
                                    updated_count += 1
                                    print(f"更新装备 {eid} (kindid:{kindid}): {extracted_suit}")
                            else:
                                # 没有套装信息，设置为空字符串
                                if current_addon_status != "":
                                    cursor.execute(
                                        "UPDATE equipments SET addon_status = ? WHERE eid = ?",
                                        ("", eid)
                                    )
                                    updated_count += 1
                                    print(f"设置装备 {eid} (kindid:{kindid}) addon_status为空字符串")
                        else:
                            # 其他类型的装备设置为"0"
                            if current_addon_status != "0":
                                cursor.execute(
                                    "UPDATE equipments SET addon_status = ? WHERE eid = ?",
                                    ("0", eid)
                                )
                                updated_count += 1
                                print(f"设置装备 {eid} (kindid:{kindid}) addon_status为0")
                        
                    except Exception as e:
                        error_count += 1
                        print(f"处理装备 {record[0]} 时出错: {e}")
                
                conn.commit()
                print(f"equipments表修复完成: 更新 {updated_count} 条记录, 错误 {error_count} 条")
                return updated_count
                
        except Exception as e:
            print(f"修复equipments表失败: {e}")
            return 0
    
    def fix_pets_table(self) -> int:
        """修复pets表中的addon_status数据"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                
                # 检查pets表是否有addon_status字段
                cursor.execute("PRAGMA table_info(pets)")
                columns_info = cursor.fetchall()
                column_names = [col[1] for col in columns_info]
                
                if 'addon_status' not in column_names:
                    print("pets表中没有addon_status字段，跳过")
                    return 0
                
                # 获取所有需要修复的记录
                cursor.execute("""
                    SELECT eid, large_equip_desc, addon_status 
                    FROM pets 
                    WHERE large_equip_desc IS NOT NULL 
                    AND large_equip_desc != ''
                """)
                
                records = cursor.fetchall()
                print(f"找到 {len(records)} 条宠物记录需要检查")
                
                updated_count = 0
                error_count = 0
                
                for record in records:
                    try:
                        eid, large_equip_desc, current_addon_status = record
                        
                        # 提取套装信息
                        extracted_suit = self.extract_suit_info(large_equip_desc)
                        
                        if extracted_suit:
                            # 如果当前addon_status为空或者与提取的信息不同，则更新
                            if not current_addon_status or current_addon_status != extracted_suit:
                                cursor.execute(
                                    "UPDATE pets SET addon_status = ? WHERE eid = ?",
                                    (extracted_suit, eid)
                                )
                                updated_count += 1
                                print(f"更新宠物 {eid}: {extracted_suit}")
                        
                    except Exception as e:
                        error_count += 1
                        print(f"处理宠物 {record[0]} 时出错: {e}")
                
                conn.commit()
                print(f"pets表修复完成: 更新 {updated_count} 条记录, 错误 {error_count} 条")
                return updated_count
                
        except Exception as e:
            print(f"修复pets表失败: {e}")
            return 0
    
    def fix_all_tables(self) -> int:
        """修复equipments表的数据"""
        print("🔧 开始修复equipments表的addon_status数据...")
        
        # 只修复equipments表
        updated_count = self.fix_equipments_table()
        
        print(f"\n✅ 数据修复完成！总共更新 {updated_count} 条记录")
        return updated_count

def main():
    """主函数"""
    # 获取项目根目录
    project_root = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
    
    # 支持命令行参数指定数据库路径
    if len(sys.argv) > 1:
        equip_db_path = sys.argv[1]
        # 如果是相对路径，转换为绝对路径
        if not os.path.isabs(equip_db_path):
            equip_db_path = os.path.join(project_root, equip_db_path)
    else:
        # 获取当前月份
        current_month = datetime.now().strftime('%Y%m')
        db_filename = f"cbg_equip_{current_month}.db"
        equip_db_path = os.path.join(project_root, 'data', db_filename)
    
    print("🔧 开始修复addon_status数据...")
    print(f"📁 数据库路径: {equip_db_path}")
    
    # 检查数据库是否存在
    if not os.path.exists(equip_db_path):
        print(f"❌ 装备数据库不存在: {equip_db_path}")
        print("请先运行装备爬虫获取数据")
        return
    
    print(f"✅ 找到装备数据库: {equip_db_path}")
    
    # 创建修复器
    fixer = AddonStatusDataFixer(equip_db_path)
    
    # 执行修复
    print("🚀 开始执行数据修复...")
    total_updated = fixer.fix_all_tables()
    
    if total_updated > 0:
        print(f"✅ 数据修复完成！总共更新 {total_updated} 条记录")
    else:
        print("ℹ️ 没有需要修复的数据")

if __name__ == "__main__":
    main() 