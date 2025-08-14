#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
智能版测试文件：使用多种模式检测宠物装备套装信息
"""

import sqlite3
import sys
import os
import re
import json

# 添加项目根目录到Python路径
current_dir = os.path.dirname(os.path.abspath(__file__))
project_root = os.path.dirname(os.path.dirname(current_dir))
sys.path.insert(0, project_root)

class SmartPetSuitDetector:
    """智能宠物套装检测器"""
    
    def __init__(self, db_path: str):
        self.db_path = db_path
        self.connection = None
        
        # 定义多种套装检测模式
        self.suit_patterns = [
            # 模式1：标准套装效果格式
            r'#c4DBAF4套装效果：附加状态#c4DBAF4\s*([^#\n]+)',
            # 模式2：套装效果：xxx
            r'套装效果[：:]\s*([^#\n]+)',
            # 模式3：附加状态：xxx
            r'附加状态[：:]\s*([^#\n]+)',
            # 模式4：包含"套装"关键词
            r'套装[^#\n]*?([^#\n]+)',
            # 模式5：高级技能模式
            r'高级([^#\n]+?)(?=\s|$)',
            # 模式6：特殊技能模式
            r'(善恶有报|力劈华山|死亡召唤|上古灵符|壁垒击破|嗜血追击|剑荡四方|夜舞倾城|惊心一剑)',
        ]
        
        # 套装效果关键词
        self.suit_keywords = [
            '高级必杀', '高级偷袭', '高级吸血', '高级连击', '高级进击必杀',
            '高级魔之心', '高级法术连击', '高级法术暴击', '高级法术波动', '高级进击法爆',
            '高级神佑', '高级鬼混术', '善恶有报', '力劈华山', '死亡召唤', 
            '上古灵符', '壁垒击破', '嗜血追击', '剑荡四方', '夜舞倾城', '惊心一剑'
        ]
        
    def connect_database(self):
        """连接数据库"""
        try:
            self.connection = sqlite3.connect(self.db_path)
            print(f"✅ 成功连接数据库: {self.db_path}")
            return True
        except Exception as e:
            print(f"❌ 连接数据库失败: {str(e)}")
            return False
    
    def detect_suit_info(self, desc: str) -> dict:
        """
        使用多种模式检测套装信息
        
        Args:
            desc: 装备描述文本
            
        Returns:
            dict: 检测结果
        """
        if not desc:
            return {
                'detected': False,
                'suit_effect': '',
                'confidence': 0,
                'matched_pattern': '',
                'raw_match': ''
            }
        
        best_match = None
        best_confidence = 0
        best_pattern = ''
        
        # 尝试所有模式
        for i, pattern in enumerate(self.suit_patterns):
            matches = re.findall(pattern, desc, re.IGNORECASE)
            if matches:
                for match in matches:
                    match = match.strip()
                    if match:
                        # 计算置信度
                        confidence = self._calculate_confidence(match, pattern, i)
                        if confidence > best_confidence:
                            best_confidence = confidence
                            best_match = match
                            best_pattern = f"模式{i+1}: {pattern}"
        
        if best_match:
            return {
                'detected': True,
                'suit_effect': best_match,
                'confidence': best_confidence,
                'matched_pattern': best_pattern,
                'raw_match': best_match
            }
        else:
            return {
                'detected': False,
                'suit_effect': '',
                'confidence': 0,
                'matched_pattern': '',
                'raw_match': ''
            }
    
    def _calculate_confidence(self, match: str, pattern: str, pattern_index: int) -> float:
        """计算匹配的置信度"""
        confidence = 0.0
        
        # 基础置信度：模式1-3的置信度更高
        if pattern_index < 3:
            confidence += 0.8
        elif pattern_index < 5:
            confidence += 0.6
        else:
            confidence += 0.4
        
        # 关键词匹配加分
        for keyword in self.suit_keywords:
            if keyword.lower() in match.lower():
                confidence += 0.3
                break
        
        # 长度合理性检查
        if 2 <= len(match) <= 20:
            confidence += 0.2
        
        # 包含"高级"关键词加分
        if '高级' in match:
            confidence += 0.1
        
        return min(confidence, 1.0)
    
    def get_sample_pet_data(self, limit: int = 20) -> list:
        """获取样本宠物数据"""
        try:
            cursor = self.connection.cursor()
            
            # 查询包含套装关键词的数据
            query = """
            SELECT eid, equip_name, large_equip_desc, desc
            FROM pets 
            WHERE (large_equip_desc LIKE '%套装%' 
               OR large_equip_desc LIKE '%高级%'
               OR large_equip_desc LIKE '%强力%'
               OR large_equip_desc LIKE '%反震%'
               OR large_equip_desc LIKE '%必杀%'
               OR large_equip_desc LIKE '%偷袭%'
               OR large_equip_desc LIKE '%吸血%')
            LIMIT ?
            """
            
            cursor.execute(query, (limit,))
            rows = cursor.fetchall()
            
            pets_data = []
            for row in rows:
                pet_dict = {
                    'eid': row[0],
                    'equip_name': row[1],
                    'large_equip_desc': row[2],
                    'desc': row[3]
                }
                pets_data.append(pet_dict)
            
            print(f"📈 获取到 {len(pets_data)} 条可能包含套装的宠物数据")
            return pets_data
            
        except Exception as e:
            print(f"❌ 获取宠物数据失败: {str(e)}")
            return []
    
    def analyze_suit_detection(self, pets_data: list):
        """分析套装检测结果"""
        print("\n🔍 开始智能套装检测分析...")
        
        detection_results = []
        successful_detections = 0
        
        for i, pet in enumerate(pets_data):
            print(f"\n{'='*60}")
            print(f"🔍 分析第 {i+1} 条数据:")
            print(f"EID: {pet['eid']}")
            print(f"装备名称: {pet['equip_name']}")
            
            if pet['large_equip_desc']:
                desc_length = len(pet['large_equip_desc'])
                print(f"large_equip_desc长度: {desc_length}")
                
                # 显示前300字符
                preview = pet['large_equip_desc'][:300]
                print(f"描述预览: {preview}...")
                
                # 检测套装信息
                suit_result = self.detect_suit_info(pet['large_equip_desc'])
                
                if suit_result['detected']:
                    successful_detections += 1
                    print(f"🎯 检测到套装信息!")
                    print(f"   套装效果: {suit_result['suit_effect']}")
                    print(f"   置信度: {suit_result['confidence']:.2f}")
                    print(f"   匹配模式: {suit_result['matched_pattern']}")
                else:
                    print(f"⚠️ 未检测到套装信息")
                
                detection_results.append({
                    'eid': pet['eid'],
                    'equip_name': pet['equip_name'],
                    'detected': suit_result['detected'],
                    'suit_effect': suit_result['suit_effect'],
                    'confidence': suit_result['confidence'],
                    'matched_pattern': suit_result['matched_pattern']
                })
            else:
                print("⚠️ large_equip_desc为空")
        
        # 统计结果
        print(f"\n{'='*60}")
        print("📊 套装检测统计结果:")
        print(f"总数据量: {len(pets_data)}")
        print(f"成功检测: {successful_detections}")
        print(f"检测成功率: {(successful_detections / len(pets_data) * 100):.1f}%")
        
        # 显示检测到的套装效果
        detected_suits = [r for r in detection_results if r['detected']]
        if detected_suits:
            print(f"\n🎯 检测到的套装效果:")
            suit_counter = {}
            for result in detected_suits:
                suit = result['suit_effect']
                suit_counter[suit] = suit_counter.get(suit, 0) + 1
            
            for suit, count in sorted(suit_counter.items(), key=lambda x: x[1], reverse=True):
                print(f"  {suit}: {count} 次")
        
        return detection_results
    
    def close_connection(self):
        """关闭数据库连接"""
        if self.connection:
            self.connection.close()
            print("🔒 数据库连接已关闭")

def main():
    """主函数"""
    print("🚀 开始智能宠物套装检测分析...")
    
    db_path = r".\data\202508\cbg_pets_202508.db"
    detector = SmartPetSuitDetector(db_path)
    
    try:
        if not detector.connect_database():
            return
        
        # 获取样本数据
        print(f"\n📥 获取可能包含套装的宠物数据...")
        pets_data = detector.get_sample_pet_data(limit=20)
        
        if not pets_data:
            print("❌ 没有获取到可能包含套装的宠物数据")
            return
        
        # 分析套装检测
        detection_results = detector.analyze_suit_detection(pets_data)
        
        print("\n🎉 智能套装检测分析完成！")
        
    except Exception as e:
        print(f"❌ 分析过程中出现错误: {str(e)}")
        import traceback
        traceback.print_exc()
    
    finally:
        detector.close_connection()

if __name__ == "__main__":
    main() 