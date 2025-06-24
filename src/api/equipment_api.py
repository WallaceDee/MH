#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
装备列表API模块
"""

import os
import json
import sys
from typing import Dict, List, Optional, Tuple
from datetime import datetime
import sqlite3

# 添加项目根目录到Python路径
current_dir = os.path.dirname(os.path.abspath(__file__))
project_root = os.path.dirname(os.path.dirname(current_dir))
sys.path.insert(0, project_root)

try:
    from src.evaluator.mark_anchor.equip.index import EquipAnchorEvaluator
    from src.evaluator.feature_extractor.equip_feature_extractor import EquipFeatureExtractor
except ImportError:
    EquipAnchorEvaluator = None
    EquipFeatureExtractor = None
    print("警告: 无法导入装备锚点估价器或特征提取器")

class EquipmentAPI:
    def __init__(self):
        self.data_dir = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), 'data')
        
        # 初始化特征提取器
        self.feature_extractor = None
        if EquipFeatureExtractor:
            try:
                self.feature_extractor = EquipFeatureExtractor()
                print("装备特征提取器初始化成功")
            except Exception as e:
                print(f"装备特征提取器初始化失败: {e}")
        
        # 初始化装备锚点估价器
        self.evaluator = None
        if EquipAnchorEvaluator:
            try:
                self.evaluator = EquipAnchorEvaluator()
                print("装备锚点估价器初始化成功")
            except Exception as e:
                print(f"装备锚点估价器初始化失败: {e}")
    
    def _validate_year_month(self, year: Optional[int], month: Optional[int]) -> Tuple[int, int]:
        """
        验证并获取有效的年月
        """
        now = datetime.now()
        current_year = now.year
        current_month = now.month
        
        if year is None or month is None:
            return current_year, current_month
            
        if not 1 <= month <= 12:
            raise ValueError(f"无效的月份: {month}，月份必须在1-12之间")
            
        return year, month
    
    def _get_db_file(self, year: Optional[int] = None, month: Optional[int] = None) -> str:
        """
        获取指定年月的装备数据库文件路径
        """
        year, month = self._validate_year_month(year, month)
        return os.path.join(self.data_dir, f'cbg_equip_{year}{month:02d}.db')
    
    def get_equipments(self, page: int = 1, page_size: int = 10, year: Optional[int] = None, month: Optional[int] = None,
                      level_min: Optional[int] = None, level_max: Optional[int] = None,
                      price_min: Optional[int] = None, price_max: Optional[int] = None,
                      kindid: Optional[List[str]] = None, 
                      equip_special_skills: Optional[List[str]] = None,
                      equip_special_effect: Optional[List[str]] = None,
                      suit_effect: Optional[str] = None,
                      suit_added_status: Optional[str] = None,
                      suit_transform_skills: Optional[str] = None, 
                      suit_transform_charms: Optional[str] = None,
                      gem_value: Optional[str] = None,
                      gem_level: Optional[int] = None,
                      sort_by: Optional[str] = 'price', sort_order: Optional[str] = 'asc') -> Dict:
        """
        获取分页的装备列表
        """
        try:
            year, month = self._validate_year_month(year, month)
            db_file = self._get_db_file(year, month)
            
            if not os.path.exists(db_file):
                return {
                    "total": 0, "page": page, "page_size": page_size, "total_pages": 0, "data": [],
                    "year": year, "month": month, "message": f"未找到 {year}年{month}月 的装备数据文件"
                }
            
            with sqlite3.connect(db_file) as conn:
                conn.row_factory = sqlite3.Row
                cursor = conn.cursor()
                
                conditions = []
                params = []
                
                # 基础筛选条件
                if level_min is not None:
                    conditions.append("level >= ?")
                    params.append(level_min)
                if level_max is not None:
                    conditions.append("level <= ?")
                    params.append(level_max)
                if price_min is not None:
                    conditions.append("price >= ?")
                    params.append(price_min * 100) # 前端传元，后端存分
                if price_max is not None:
                    conditions.append("price <= ?")
                    params.append(price_max * 100)
                
                # 装备类型筛选（多选）
                if kindid and len(kindid) > 0:
                    type_placeholders = ','.join(['?' for _ in kindid])
                    conditions.append(f"kindid IN ({type_placeholders})")
                    params.extend(kindid)
                
                # 特技筛选（多选）
                if equip_special_skills and len(equip_special_skills) > 0:
                    skill_placeholders = ','.join(['?' for _ in equip_special_skills])
                    conditions.append(f"special_skill IN ({skill_placeholders})")
                    params.extend(equip_special_skills)
                
                # 特效筛选（多选，JSON数组格式）
                if equip_special_effect and len(equip_special_effect) > 0:
                    effect_conditions = []
                    for effect in equip_special_effect:
                        # 使用精确的JSON数组匹配，避免数字包含关系的误匹配
                        # 匹配模式：[6], [6,x], [x,6], [x,6,y] 等，但不匹配16, 26等包含6的数字
                        effect_conditions.append("(special_effect LIKE ? OR special_effect LIKE ? OR special_effect LIKE ? OR special_effect LIKE ?)")
                        # 四种匹配模式：单独存在、开头、中间、结尾
                        params.extend([
                            f'[{effect}]',        # 只有这一个特效：[6]
                            f'[{effect},%',       # 在开头：[6,x,...]
                            f'%,{effect},%',      # 在中间：[x,6,y,...]  
                            f'%,{effect}]'        # 在结尾：[x,y,6]
                        ])
                    conditions.append(f"({' OR '.join(effect_conditions)})")
                
                # 套装筛选
                if suit_effect:
                    conditions.append("suit_effect = ?")
                    params.append(suit_effect)
                    
                if suit_added_status:
                    conditions.append("suit_effect = ?")
                    params.append(suit_added_status)
                    
                if suit_transform_skills:
                    conditions.append("suit_effect = ?")
                    params.append(suit_transform_skills)
                    
                if suit_transform_charms:
                    conditions.append("suit_effect = ?")
                    params.append(suit_transform_charms)
                
                # 宝石筛选
                if gem_value:
                    # 宝石数据格式为JSON数组，如 [6] 或 [4, 6]
                    # 使用精确的JSON数组匹配，类似特效查询的逻辑
                    conditions.append("(gem_value LIKE ? OR gem_value LIKE ? OR gem_value LIKE ? OR gem_value LIKE ?)")
                    params.extend([
                        f'[{gem_value}]',        # 只有这一个宝石：[6]
                        f'[{gem_value},%',       # 在开头：[6,x,...]
                        f'%,{gem_value},%',      # 在中间：[x,6,y,...]  
                        f'%,{gem_value}]'        # 在结尾：[x,y,6]
                    ])
                    
                if gem_level is not None:
                    conditions.append("gem_level >= ?")
                    params.append(gem_level)
              
                where_clause = f"WHERE {' AND '.join(conditions)}" if conditions else ""
                
                # 获取总数
                count_sql = f"SELECT COUNT(*) FROM equipments {where_clause}"
                total = cursor.execute(count_sql, params).fetchone()[0]
                
                total_pages = (total + page_size - 1) // page_size
                
                # 排序
                order_by_clause = ""
                if sort_by and sort_order:
                    # 防止SQL注入 - 扩展支持的排序字段
                    allowed_sort_by = [
                        'price',           # 价格
                        'level',           # 等级
                        'all_damage',      # 总伤
                        'init_damage',     # 初伤
                        'init_wakan',      # 初灵
                        'init_defense',    # 初防
                        'init_hp',         # 初血
                        'init_dex',        # 初敏
                        'create_time_equip', # 创建时间
                        'selling_time',    # 上架时间
                        'gem_level',       # 宝石等级
                        'special_effect',  # 特效
                        'special_skill',   # 特技
                        'suit_effect',     # 套装
                        'server_name',     # 服务器
                        'equip_name',      # 装备名称
                        'seller_nickname', # 卖家昵称
                        'zongshang'        # 总伤（备用字段名）
                    ]
                    if sort_by in allowed_sort_by and sort_order.lower() in ['asc', 'desc']:
                        order_by_clause = f"ORDER BY {sort_by} {sort_order.upper()}"

                # 分页查询
                offset = (page - 1) * page_size
                query_sql = f"SELECT * FROM equipments {where_clause} {order_by_clause} LIMIT ? OFFSET ?"
                
                equipments = cursor.execute(query_sql, params + [page_size, offset]).fetchall()
                
                return {
                    "total": total,
                    "page": page,
                    "page_size": page_size,
                    "total_pages": total_pages,
                    "data": [dict(row) for row in equipments],
                    "year": year,
                    "month": month,
                }

        except Exception as e:
            return {"error": str(e)}

    def get_equipment_details(self, equip_sn: str, year: Optional[int] = None, month: Optional[int] = None) -> Optional[Dict]:
        """获取单个装备的详细信息"""
        try:
            year, month = self._validate_year_month(year, month)
            db_file = self._get_db_file(year, month)

            if not os.path.exists(db_file):
                return None
            
            with sqlite3.connect(db_file) as conn:
                conn.row_factory = sqlite3.Row
                cursor = conn.cursor()
                
                sql = "SELECT * FROM equipments WHERE equip_sn = ?"
                equipment = cursor.execute(sql, (equip_sn,)).fetchone()
                
                return dict(equipment) if equipment else None

        except Exception as e:
            print(f"获取装备详情时出错: {e}")
            return None

    def _get_equipment_by_eid(self, eid: str) -> Optional[Dict]:
        """
        通过eid查询完整的装备信息
        """
        try:
            # 从当前月份和上月份的数据库中查找
            current_time = datetime.now()
            
            # 尝试当前月份和前几个月份的数据库
            for month_offset in range(3):  # 查找当前月和前2个月
                target_month = current_time.month - month_offset
                target_year = current_time.year
                
                # 处理跨年情况
                while target_month <= 0:
                    target_month += 12
                    target_year -= 1
                
                db_file = self._get_db_file(target_year, target_month)
                
                if not os.path.exists(db_file):
                    continue
                
                with sqlite3.connect(db_file) as conn:
                    conn.row_factory = sqlite3.Row
                    cursor = conn.cursor()
                    
                    sql = "SELECT * FROM equipments WHERE eid = ?"
                    equipment = cursor.execute(sql, (eid,)).fetchone()
                    
                    if equipment:
                        return dict(equipment)
            
            return None
            
        except Exception as e:
            print(f"通过eid获取装备信息时出错: {e}")
            return None

    def find_equipment_anchors(self, equipment_data: Dict, 
                              similarity_threshold: float = 0.7,
                              max_anchors: int = 30) -> Dict:
        """
        寻找装备市场锚点
        
        Args:
            equipment_data: 装备原始数据字典
            similarity_threshold: 相似度阈值 (0.0-1.0)
            max_anchors: 最大锚点数量
            
        Returns:
            包含锚点信息的字典
        """
        try:
            if not self.evaluator:
                return {
                    "error": "装备锚点估价器未初始化",
                    "anchors": [],
                    "anchor_count": 0
                }
            
            if not self.feature_extractor:
                return {
                    "error": "装备特征提取器未初始化",
                    "anchors": [],
                    "anchor_count": 0
                }
            
            # 使用特征提取器提取特征
            try:
                equipment_features = self.feature_extractor.extract_features(equipment_data)
            except Exception as e:
                return {
                    "error": f"特征提取失败: {str(e)}",
                    "anchors": [],
                    "anchor_count": 0
                }
            
            # 验证必要的特征字段
            required_fields = ['equip_level', 'kindid']
            missing_fields = [field for field in required_fields if field not in equipment_features]
            if missing_fields:
                return {
                    "error": f"提取的特征缺少必要字段: {', '.join(missing_fields)}",
                    "anchors": [],
                    "anchor_count": 0
                }
            
            # 验证参数范围
            if not 0.0 <= similarity_threshold <= 1.0:
                return {
                    "error": "相似度阈值必须在0.0-1.0之间",
                    "anchors": [],
                    "anchor_count": 0
                }
            
            if not 1 <= max_anchors <= 100:
                return {
                    "error": "最大锚点数量必须在1-100之间",
                    "anchors": [],
                    "anchor_count": 0
                }
            
            # 调用锚点查找方法
            anchors = self.evaluator.find_market_anchors(
                target_features=equipment_features,
                similarity_threshold=similarity_threshold,
                max_anchors=max_anchors
            )
            
            # 格式化返回结果
            result = {
                "anchor_count": len(anchors),
                "similarity_threshold": similarity_threshold,
                "anchors": []
            }
            
            # 处理锚点数据，添加友好的显示信息
            for anchor in anchors:
                # 获取锚点的eid
                anchor_eid = anchor.get("eid")
                
                # 通过eid查询完整的装备信息
                full_equipment_info = None
                if anchor_eid:
                    full_equipment_info = self._get_equipment_by_eid(anchor_eid)
                
                # 组合锚点信息和完整装备信息
                if full_equipment_info:
                    anchor_info = {
                        **full_equipment_info,
                        "eid": anchor_eid,
                        "similarity": round(anchor.get("similarity", 0), 3),
                        # 移除features字段，因为它包含pandas对象，无法JSON序列化
                    }
                else:
                    # 如果无法获取完整信息，使用基础信息
                    anchor_info = {
                        "eid": anchor_eid,
                        "similarity": round(anchor.get("similarity", 0), 3),
                        "price": anchor.get("price", 0),
                        "equip_name": "未知装备",
                        "server_name": "未知服务器",
                        "equip_level": 0,
                        "special_skill": 0,
                        "suit_effect": 0,
                        # 移除features字段，因为它包含pandas对象，无法JSON序列化
                    }
                result["anchors"].append(anchor_info)
            
            # 添加统计信息
            if anchors:
                prices = [anchor["price"] for anchor in anchors]
                similarities = [anchor["similarity"] for anchor in anchors]
                
                result["statistics"] = {
                    "price_range": {
                        "min": min(prices),
                        "max": max(prices)
                    },
                    "similarity_range": {
                        "min": round(min(similarities), 3),
                        "max": round(max(similarities), 3),
                        "avg": round(sum(similarities) / len(similarities), 3)
                    }
                }
            else:
                result["statistics"] = {
                    "price_range": {"min": 0, "max": 0},
                    "similarity_range": {"min": 0, "max": 0, "avg": 0}
                }
                result["message"] = "未找到符合条件的市场锚点，建议降低相似度阈值"
            
            return result
            
        except Exception as e:
            return {
                "error": f"查找锚点时发生错误: {str(e)}",
                "anchors": [],
                "anchor_count": 0
            }

    def get_equipment_valuation(self, equipment_data: Dict,
                               strategy: str = 'fair_value') -> Dict:
        """
        获取装备估价
        
        Args:
            equipment_data: 装备原始数据字典
            strategy: 估价策略 ('fair_value', 'competitive', 'premium')
            
        Returns:
            包含估价信息的字典
        """
        try:
            if not self.evaluator:
                return {
                    "error": "装备锚点估价器未初始化",
                    "estimated_price": 0,
                    "estimated_price_yuan": 0
                }
            
            if not self.feature_extractor:
                return {
                    "error": "装备特征提取器未初始化",
                    "estimated_price": 0,
                    "estimated_price_yuan": 0
                }
            
            # 使用特征提取器提取特征
            try:
                equipment_features = self.feature_extractor.extract_features(equipment_data)
            except Exception as e:
                return {
                    "error": f"特征提取失败: {str(e)}",
                    "estimated_price": 0,
                    "estimated_price_yuan": 0
                }
            
            # 验证策略参数
            valid_strategies = ['fair_value', 'competitive', 'premium']
            if strategy not in valid_strategies:
                return {
                    "error": f"无效的估价策略: {strategy}，有效策略: {', '.join(valid_strategies)}",
                    "estimated_price": 0,
                    "estimated_price_yuan": 0
                }
            
            # 调用估价方法
            result = self.evaluator.calculate_value(
                target_features=equipment_features,
                strategy=strategy
            )
            
            # 格式化返回结果
            if "error" in result:
                return {
                    "error": result["error"],
                    "estimated_price": 0,
                    "estimated_price_yuan": 0
                }
            
            estimated_price = result.get("estimated_price", 0)
            
            return {
                "estimated_price": estimated_price,
                "estimated_price_yuan": round(estimated_price / 100, 2),
                "strategy": strategy,
                "anchor_count": result.get("anchor_count", 0),
                "confidence": result.get("confidence", 0),
                "anchors_preview": result.get("anchors", [])[:5]  # 只返回前5个锚点作为预览
            }
            
        except Exception as e:
            return {
                "error": f"估价时发生错误: {str(e)}",
                "estimated_price": 0,
                "estimated_price_yuan": 0
            }

def main():
    api = EquipmentAPI()
    
    print("--- 测试获取装备列表 ---")
    equipments_data = api.get_equipments(page=1, page_size=5, level_min=60)
    if "error" not in equipments_data:
        print(f"总数: {equipments_data['total']}, 当前页: {equipments_data['page']}")
        for equip in equipments_data['data']:
            print(f"  - {equip['equip_name']} (Lvl: {equip['equip_level']}, Price: {equip['price']/100:.1f}元, SN: {equip['equip_sn']})")
    else:
        print(f"错误: {equipments_data['error']}")
    
    print("\n--- 测试装备锚点查找接口 ---")
    # 构造测试装备特征
    test_features = {
        'equip_level': 80,
        'kindid': 20,
        'init_damage': 300,
        'all_damage': 350,
        'addon_total': 40,
        'gem_level': 8,
        'special_skill': 0,
        'suit_effect': 0
    }
    
    print(f"测试装备特征: {test_features}")
    anchors_result = api.find_equipment_anchors(
        equipment_features=test_features,
        similarity_threshold=0.6,
        max_anchors=10
    )
    
    if "error" not in anchors_result:
        print(f"找到 {anchors_result['anchor_count']} 个锚点")
        if anchors_result['anchors']:
            print("前3个锚点:")
            for i, anchor in enumerate(anchors_result['anchors'][:3]):
                print(f"  {i+1}. {anchor['equip_name']} - {anchor['price_yuan']}万 (相似度: {anchor['similarity']})")
            
            if 'statistics' in anchors_result:
                stats = anchors_result['statistics']
                print(f"价格范围: {round(stats['price_range']['min'] / 100, 2)}元 - {round(stats['price_range']['max'] / 100, 2)}元")
                print(f"平均相似度: {stats['similarity_range']['avg']}")
    else:
        print(f"锚点查找错误: {anchors_result['error']}")
    
    print("\n--- 测试装备估价接口 ---")
    valuation_result = api.get_equipment_valuation(
        equipment_features=test_features,
        strategy='fair_value'
    )
    
    if "error" not in valuation_result:
        print(f"估价结果: {valuation_result['estimated_price_yuan']}万")
        print(f"基于 {valuation_result['anchor_count']} 个锚点，置信度: {valuation_result['confidence']:.2f}")
    else:
        print(f"估价错误: {valuation_result['error']}")
    
    print("\n--- 测试获取单个装备详情 ---")
    if "error" not in equipments_data and equipments_data['data']:
        test_sn = equipments_data['data'][0]['equip_sn']
        details = api.get_equipment_details(equip_sn=test_sn)
        if details:
            print(f"成功获取装备详情 (SN: {test_sn}): {details['equip_name']}")
        else:
            print(f"未找到SN为 {test_sn} 的装备")

if __name__ == '__main__':
    main() 