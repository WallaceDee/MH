#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
装备服务
"""

import os
import json
import sys
from typing import Dict, List, Optional, Tuple
from datetime import datetime
import sqlite3
import logging

logger = logging.getLogger(__name__)

# 动态导入评估器，避免循环导入
try:
    from evaluator.mark_anchor.equip.index import EquipAnchorEvaluator
    from evaluator.feature_extractor.equip_feature_extractor import EquipFeatureExtractor
    from evaluator.feature_extractor.lingshi_feature_extractor import LingshiFeatureExtractor
    from evaluator.feature_extractor.pet_equip_feature_extractor import PetEquipFeatureExtractor
except ImportError:
    EquipAnchorEvaluator = None
    EquipFeatureExtractor = None
    LingshiFeatureExtractor = None
    PetEquipFeatureExtractor = None
    logger.warning("无法导入装备锚点估价器或特征提取器")


class EquipmentService:
    def __init__(self):
        # 获取项目根目录
        self.project_root = os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
        self.data_dir = os.path.join(self.project_root, 'data')
        
        # 初始化特征提取器
        self.equip_feature_extractor = None
        self.lingshi_feature_extractor = None
        self.pet_equip_feature_extractor = None
        
        if EquipFeatureExtractor:
            try:
                self.equip_feature_extractor = EquipFeatureExtractor()
                logger.info("装备特征提取器初始化成功")
            except Exception as e:
                logger.error(f"装备特征提取器初始化失败: {e}")
        
        if LingshiFeatureExtractor:
            try:
                self.lingshi_feature_extractor = LingshiFeatureExtractor()
                logger.info("灵饰特征提取器初始化成功")
            except Exception as e:
                logger.error(f"灵饰特征提取器初始化失败: {e}")
        
        if PetEquipFeatureExtractor:
            try:
                self.pet_equip_feature_extractor = PetEquipFeatureExtractor()
                logger.info("宠物装备特征提取器初始化成功")
            except Exception as e:
                logger.error(f"宠物装备特征提取器初始化失败: {e}")

        # 初始化装备锚点估价器
        self.evaluator = None
        if EquipAnchorEvaluator:
            try:
                self.evaluator = EquipAnchorEvaluator()
                logger.info("装备锚点估价器初始化成功")
            except Exception as e:
                logger.error(f"装备锚点估价器初始化失败: {e}")
    
    def _get_feature_extractor(self, kindid: int):
        """根据装备类型获取对应的特征提取器"""
        # 灵饰装备：kindid=61,62,63,64
        if kindid in [61, 62, 63, 64]:
            return self.lingshi_feature_extractor
        elif kindid in [29]:
            return self.pet_equip_feature_extractor
        else:
            # 普通装备
            return self.equip_feature_extractor
    

    
    def _validate_year_month(self, year: Optional[int], month: Optional[int]) -> Tuple[int, int]:
        """验证并获取有效的年月"""
        now = datetime.now()
        current_year = now.year
        current_month = now.month
        
        if year is None or month is None:
            return current_year, current_month
            
        if not 1 <= month <= 12:
            raise ValueError(f"无效的月份: {month}，月份必须在1-12之间")
            
        return year, month
    
    def _get_db_file(self, year: Optional[int] = None, month: Optional[int] = None) -> str:
        """获取指定年月的装备数据库文件路径"""
        year, month = self._validate_year_month(year, month)
        return os.path.join(self.data_dir, f'cbg_equip_{year}{month:02d}.db')
    
    def get_equipments(self, page: int = 1, page_size: int = 10, year: Optional[int] = None, month: Optional[int] = None,
                      level_min: Optional[int] = None, level_max: Optional[int] = None,
                      price_min: Optional[int] = None, price_max: Optional[int] = None,
                      kindid: Optional[List[str]] = None, 
                      equip_type: Optional[List[int]] = None,  # 宠物装备类型（多选）
                      equip_special_skills: Optional[List[str]] = None,
                      equip_special_effect: Optional[List[str]] = None,
                      suit_effect: Optional[str] = None,
                      suit_added_status: Optional[str] = None,
                      suit_transform_skills: Optional[str] = None, 
                      suit_transform_charms: Optional[str] = None,
                      gem_value: Optional[str] = None,
                      gem_level: Optional[int] = None,
                      sort_by: Optional[str] = 'price', sort_order: Optional[str] = 'asc') -> Dict:
        """获取分页的装备列表"""
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
                
                # 添加调试日志
                logger.info(f"开始处理筛选条件，参数: level_min={level_min}, level_max={level_max}, price_min={price_min}, price_max={price_max}")
                logger.info(f"多选参数: kindid={kindid}, equip_special_skills={equip_special_skills}, equip_special_effect={equip_special_effect}")
                
                conditions = []
                params = []
                
                # 基础筛选条件 - 修复字段名
                if level_min is not None:
                    # 数据库字段可能是 level 或 equip_level
                    conditions.append("(level >= ? OR equip_level >= ?)")
                    params.extend([level_min, level_min])
                if level_max is not None:
                    conditions.append("(level <= ? OR equip_level <= ?)")
                    params.extend([level_max, level_max])
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
                    logger.info(f"添加装备类型筛选: kindid IN ({type_placeholders}), 值: {kindid}")
                
                # 宠物装备类型筛选（多选）
                if equip_type and len(equip_type) > 0:
                    type_placeholders = ','.join(['?' for _ in equip_type])
                    conditions.append(f"equip_type IN ({type_placeholders})")
                    params.extend(equip_type)
                    logger.info(f"添加宠物装备类型筛选: equip_type IN ({type_placeholders}), 值: {equip_type}")
                
                # 特技筛选（多选）
                if equip_special_skills and len(equip_special_skills) > 0:
                    skill_placeholders = ','.join(['?' for _ in equip_special_skills])
                    conditions.append(f"special_skill IN ({skill_placeholders})")
                    params.extend(equip_special_skills)
                    logger.info(f"添加特技筛选: special_skill IN ({skill_placeholders}), 值: {equip_special_skills}")
                
                # 特效筛选（多选，JSON数组格式）
                if equip_special_effect and len(equip_special_effect) > 0:
                    effect_conditions = []
                    for effect in equip_special_effect:
                        effect_conditions.append("(special_effect LIKE ? OR special_effect LIKE ? OR special_effect LIKE ? OR special_effect LIKE ?)")
                        params.extend([
                            f'[{effect}]',        # 只有这一个特效：[6]
                            f'[{effect},%',       # 在开头：[6,x,...]
                            f'%,{effect},%',      # 在中间：[x,6,y,...]  
                            f'%,{effect}]'        # 在结尾：[x,y,6]
                        ])
                    conditions.append(f"({' OR '.join(effect_conditions)})")
                    logger.info(f"添加特效筛选: {equip_special_effect}")
                
                # 套装筛选
                if suit_effect:
                    conditions.append("suit_effect = ?")
                    params.append(suit_effect)
                    logger.info(f"添加套装筛选: suit_effect = {suit_effect}")
                    
                if suit_added_status:
                    conditions.append("suit_effect = ?")
                    params.append(suit_added_status)
                    logger.info(f"添加套装附加状态筛选: suit_effect = {suit_added_status}")
                    
                if suit_transform_skills:
                    conditions.append("suit_effect = ?")
                    params.append(suit_transform_skills)
                    logger.info(f"添加套装变身术筛选: suit_effect = {suit_transform_skills}")
                    
                if suit_transform_charms:
                    conditions.append("suit_effect = ?")
                    params.append(suit_transform_charms)
                    logger.info(f"添加套装变化咒筛选: suit_effect = {suit_transform_charms}")
                
                # 宝石筛选
                if gem_value:
                    conditions.append("(gem_value LIKE ? OR gem_value LIKE ? OR gem_value LIKE ? OR gem_value LIKE ?)")
                    params.extend([
                        f'[{gem_value}]',        # 只有这一个宝石：[6]
                        f'[{gem_value},%',       # 在开头：[6,x,...]
                        f'%,{gem_value},%',      # 在中间：[x,6,y,...]  
                        f'%,{gem_value}]'        # 在结尾：[x,y,6]
                    ])
                    logger.info(f"添加宝石筛选: gem_value = {gem_value}")
                    
                if gem_level is not None:
                    conditions.append("gem_level >= ?")
                    params.append(gem_level)
                    logger.info(f"添加宝石等级筛选: gem_level >= {gem_level}")
              
                where_clause = f"WHERE {' AND '.join(conditions)}" if conditions else ""
                
                # 添加完整SQL调试日志
                logger.info(f"生成的WHERE子句: {where_clause}")
                logger.info(f"SQL参数: {params}")
                
                # 获取总数
                count_sql = f"SELECT COUNT(*) FROM equipments {where_clause}"
                total = cursor.execute(count_sql, params).fetchone()[0]
                logger.info(f"查询到的总数: {total}")
                
                total_pages = (total + page_size - 1) // page_size
                
                # 排序
                order_by_clause = ""
                if sort_by and sort_order:
                    allowed_sort_by = [
                        'price', 'level', 'equip_level', 'all_damage', 'init_damage', 'init_wakan', 'init_defense',
                        'init_hp', 'init_dex', 'create_time_equip', 'selling_time', 'gem_level',
                        'special_effect', 'special_skill', 'suit_effect', 'server_name', 'equip_name',
                        'seller_nickname', 'zongshang'
                    ]
                    if sort_by in allowed_sort_by and sort_order.lower() in ['asc', 'desc']:
                        order_by_clause = f"ORDER BY {sort_by} {sort_order.upper()}"

                # 分页查询
                offset = (page - 1) * page_size
                query_sql = f"SELECT * FROM equipments {where_clause} {order_by_clause} LIMIT ? OFFSET ?"
                
                logger.info(f"完整查询SQL: {query_sql}")
                logger.info(f"查询参数: {params + [page_size, offset]}")
                
                equipments = cursor.execute(query_sql, params + [page_size, offset]).fetchall()
                
                logger.info(f"查询到的装备数量: {len(equipments)}")
                
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
            logger.error(f"获取装备列表时出错: {e}")
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
            logger.error(f"获取装备详情时出错: {e}")
            return None

    def _get_equipment_by_eid(self, eid: str) -> Optional[Dict]:
        """通过eid查询完整的装备信息"""
        try:
            current_time = datetime.now()
            
            # 尝试当前月份和前几个月份的数据库
            for month_offset in range(3):
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
            logger.error(f"通过eid获取装备信息时出错: {e}")
            return None

    def _get_equipment_by_equip_sn(self, equip_sn: str) -> Optional[Dict]:
        """通过equip_sn查询完整的装备信息"""
        try:
            current_time = datetime.now()
            
            # 尝试当前月份和前几个月份的数据库
            for month_offset in range(3):
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
                    
                    sql = "SELECT * FROM equipments WHERE equip_sn = ?"
                    equipment = cursor.execute(sql, (equip_sn,)).fetchone()
                    
                    if equipment:
                        return dict(equipment)
            
            return None
            
        except Exception as e:
            logger.error(f"通过equip_sn获取装备信息时出错: {e}")
            return None

    def find_equipment_anchors(self, equipment_data: Dict, 
                              similarity_threshold: float = 0.7,
                              max_anchors: int = 30) -> Dict:
        """寻找装备市场锚点"""
        try:
            if not self.evaluator:
                return {
                    "error": "装备锚点估价器未初始化",
                    "anchors": [],
                    "anchor_count": 0
                }
            
            # 根据kindid获取对应的特征提取器
            kindid = equipment_data.get('kindid', 0)
            feature_extractor = self._get_feature_extractor(kindid)
            
            if not feature_extractor:
                extractor_type = "灵饰" if kindid in [61, 62, 63, 64] else "装备"
                return {
                    "error": f"{extractor_type}特征提取器未初始化",
                    "anchors": [],
                    "anchor_count": 0
                }
            
            # 使用特征提取器提取特征
            try:
                equipment_features = feature_extractor.extract_features(equipment_data)
            except Exception as e:
                return {
                    "error": f"特征提取失败: {str(e)}",
                    "anchors": [],
                    "anchor_count": 0
                }
            
            # 确保特征中包含equip_sn信息，用于排除自身
            if 'equip_sn' in equipment_data:
                equipment_features['equip_sn'] = equipment_data['equip_sn']
            
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
            
            # 处理锚点数据
            for anchor in anchors:
                anchor_equip_sn = anchor.get("equip_sn")
                
                # 通过equip_sn查询完整的装备信息
                full_equipment_info = None
                if anchor_equip_sn:
                    full_equipment_info = self._get_equipment_by_equip_sn(anchor_equip_sn)
                
                # 组合锚点信息和完整装备信息
                if full_equipment_info:
                    anchor_info = {
                        **full_equipment_info,
                        "equip_sn": anchor_equip_sn,
                        "similarity": round(float(anchor.get("similarity", 0)), 3),
                    }
                else:
                    # 如果无法获取完整信息，使用基础信息
                    anchor_info = {
                        "equip_sn": anchor_equip_sn,
                        "similarity": round(float(anchor.get("similarity", 0)), 3),
                        "price": float(anchor.get("price", 0)),
                        "equip_name": "未知装备",
                        "server_name": "未知服务器",
                        "equip_level": 0,
                        "special_skill": 0,
                        "suit_effect": 0,
                    }
                result["anchors"].append(anchor_info)
            
            # 添加统计信息
            if anchors:
                prices = [float(anchor["price"]) for anchor in anchors]
                similarities = [float(anchor["similarity"]) for anchor in anchors]
                
                result["statistics"] = {
                    "price_range": {
                        "min": float(min(prices)),
                        "max": float(max(prices))
                    },
                    "similarity_range": {
                        "min": round(float(min(similarities)), 3),
                        "max": round(float(max(similarities)), 3),
                        "avg": round(float(sum(similarities) / len(similarities)), 3)
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
            logger.error(f"查找锚点时发生错误: {e}")
            return {
                "error": f"查找锚点时发生错误: {str(e)}",
                "anchors": [],
                "anchor_count": 0
            }

    def get_equipment_valuation(self, equipment_data: Dict,
                               strategy: str = 'fair_value',
                               similarity_threshold: float = 0.7,
                               max_anchors: int = 30) -> Dict:
        """获取装备估价"""
        try:
            if not self.evaluator:
                return {
                    "error": "装备锚点估价器未初始化",
                    "estimated_price": 0,
                    "estimated_price_yuan": 0
                }
            
            # 根据kindid获取对应的特征提取器
            kindid = equipment_data.get('kindid', 0)
            feature_extractor = self._get_feature_extractor(kindid)
            
            if not feature_extractor:
                extractor_type = "灵饰" if kindid in [61, 62, 63, 64] else "装备"
                return {
                    "error": f"{extractor_type}特征提取器未初始化",
                    "estimated_price": 0,
                    "estimated_price_yuan": 0
                }
            
            # 使用特征提取器提取特征
            try:
                equipment_features = feature_extractor.extract_features(equipment_data)
            except Exception as e:
                return {
                    "error": f"特征提取失败: {str(e)}",
                    "estimated_price": 0,
                    "estimated_price_yuan": 0
                }
            
            # 确保特征中包含equip_sn信息，用于排除自身
            if 'equip_sn' in equipment_data:
                equipment_features['equip_sn'] = equipment_data['equip_sn']
            
            # 验证策略参数
            valid_strategies = ['fair_value', 'competitive', 'premium']
            if strategy not in valid_strategies:
                return {
                    "error": f"无效的估价策略: {strategy}，有效策略: {', '.join(valid_strategies)}",
                    "estimated_price": 0,
                    "estimated_price_yuan": 0
                }
            
            # 验证相似度阈值和最大锚点数量
            if not 0.0 <= similarity_threshold <= 1.0:
                return {
                    "error": "相似度阈值必须在0.0-1.0之间",
                    "estimated_price": 0,
                    "estimated_price_yuan": 0
                }
            
            if not 1 <= max_anchors <= 100:
                return {
                    "error": "最大锚点数量必须在1-100之间",
                    "estimated_price": 0,
                    "estimated_price_yuan": 0
                }
            
            # 调用估价方法
            result = self.evaluator.calculate_value(
                target_features=equipment_features,
                strategy=strategy,
                similarity_threshold=similarity_threshold,
                max_anchors=max_anchors
            )
            
            # 格式化返回结果
            if "error" in result:
                return {
                    "error": result["error"],
                    "estimated_price": 0,
                    "estimated_price_yuan": 0
                }
            
            estimated_price = result.get("estimated_price", 0)
            
            # 获取完整的锚点信息（使用用户指定的参数）
            anchors_result = self.find_equipment_anchors(
                equipment_data=equipment_data,
                similarity_threshold=similarity_threshold,
                max_anchors=max_anchors
            )
            
            # 处理锚点信息
            anchors = anchors_result.get("anchors", [])
            anchor_count = anchors_result.get("anchor_count", 0)
            
            return {
                "estimated_price": estimated_price,
                "estimated_price_yuan": round(estimated_price / 100, 2),
                "strategy": strategy,
                "anchor_count": anchor_count,
                "confidence": result.get("confidence", 0),
                "similarity_threshold": similarity_threshold,
                "max_anchors": max_anchors,
                "anchors": anchors,  # 返回完整的锚点信息
                "price_range": result.get("price_range", {}),
                "fallback_used": result.get("fallback_used", False)
            }
            
        except Exception as e:
            logger.error(f"估价时发生错误: {e}")
            return {
                "error": f"估价时发生错误: {str(e)}",
                "estimated_price": 0,
                "estimated_price_yuan": 0
            } 