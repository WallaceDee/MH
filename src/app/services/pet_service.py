#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
宠物服务
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
    from evaluator.mark_anchor.pet.index import PetAnchorEvaluator
    from evaluator.feature_extractor.pet_feature_extractor import PetFeatureExtractor
except ImportError:
    PetAnchorEvaluator = None
    PetFeatureExtractor = None
    logger.warning("无法导入宠物锚点估价器或特征提取器")


class PetService:
    def __init__(self):
        # 获取项目根目录
        self.project_root = os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
        self.data_dir = os.path.join(self.project_root, 'data')
        
        # 初始化特征提取器
        self.pet_feature_extractor = None
        
        if PetFeatureExtractor:
            try:
                self.pet_feature_extractor = PetFeatureExtractor()
                logger.info("宠物特征提取器初始化成功")
            except Exception as e:
                logger.error(f"宠物特征提取器初始化失败: {e}")

        # 初始化宠物锚点估价器
        self.evaluator = None
        if PetAnchorEvaluator:
            try:
                self.evaluator = PetAnchorEvaluator()
                logger.info("宠物锚点估价器初始化成功")
            except Exception as e:
                logger.error(f"宠物锚点估价器初始化失败: {e}")
    
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
        """获取指定年月的宠物数据库文件路径"""
        year, month = self._validate_year_month(year, month)
        return os.path.join(self.data_dir, f'cbg_pets_{year}{month:02d}.db')
    
    def get_pets(self, page: int = 1, page_size: int = 10, year: Optional[int] = None, month: Optional[int] = None,
                 level_min: Optional[int] = None, level_max: Optional[int] = None,
                 price_min: Optional[int] = None, price_max: Optional[int] = None,
                 pet_type: Optional[List[str]] = None,
                 pet_skills: Optional[List[str]] = None,
                 pet_special_effect: Optional[List[str]] = None,
                 pet_quality: Optional[List[str]] = None,
                 pet_growth: Optional[str] = None,
                 pet_aptitude: Optional[str] = None,
                 pet_skill_count: Optional[int] = None,
                 sort_by: Optional[str] = 'price', sort_order: Optional[str] = 'asc') -> Dict:
        """获取分页的宠物列表"""
        try:
            year, month = self._validate_year_month(year, month)
            db_file = self._get_db_file(year, month)
            
            if not os.path.exists(db_file):
                return {
                    "total": 0, "page": page, "page_size": page_size, "total_pages": 0, "data": [],
                    "year": year, "month": month, "message": f"未找到 {year}年{month}月 的宠物数据文件"
                }
            
            with sqlite3.connect(db_file) as conn:
                conn.row_factory = sqlite3.Row
                cursor = conn.cursor()
                
                # 添加调试日志
                logger.info(f"开始处理筛选条件，参数: level_min={level_min}, level_max={level_max}, price_min={price_min}, price_max={price_max}")
                logger.info(f"多选参数: pet_type={pet_type}, pet_skills={pet_skills}, pet_special_effect={pet_special_effect}")
                
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
                
                # 宠物类型筛选（多选）
                if pet_type and len(pet_type) > 0:
                    type_placeholders = ','.join(['?' for _ in pet_type])
                    conditions.append(f"pet_type IN ({type_placeholders})")
                    params.extend(pet_type)
                    logger.info(f"添加宠物类型筛选: pet_type IN ({type_placeholders}), 值: {pet_type}")
                
                # 宠物技能筛选（多选）
                if pet_skills and len(pet_skills) > 0:
                    skill_conditions = []
                    for skill in pet_skills:
                        skill_conditions.append("(skills LIKE ? OR skills LIKE ? OR skills LIKE ? OR skills LIKE ?)")
                        params.extend([
                            f'[{skill}]',        # 只有这一个技能：[技能名]
                            f'[{skill},%',       # 在开头：[技能名,x,...]
                            f'%,{skill},%',      # 在中间：[x,技能名,y,...]  
                            f'%,{skill}]'        # 在结尾：[x,y,技能名]
                        ])
                    conditions.append(f"({' OR '.join(skill_conditions)})")
                    logger.info(f"添加宠物技能筛选: {pet_skills}")
                
                # 宠物特效筛选（多选）
                if pet_special_effect and len(pet_special_effect) > 0:
                    effect_conditions = []
                    for effect in pet_special_effect:
                        effect_conditions.append("(special_effect LIKE ? OR special_effect LIKE ? OR special_effect LIKE ? OR special_effect LIKE ?)")
                        params.extend([
                            f'[{effect}]',        # 只有这一个特效：[特效名]
                            f'[{effect},%',       # 在开头：[特效名,x,...]
                            f'%,{effect},%',      # 在中间：[x,特效名,y,...]  
                            f'%,{effect}]'        # 在结尾：[x,y,特效名]
                        ])
                    conditions.append(f"({' OR '.join(effect_conditions)})")
                    logger.info(f"添加宠物特效筛选: {pet_special_effect}")
                
                # 宠物品质筛选（多选）
                if pet_quality and len(pet_quality) > 0:
                    quality_placeholders = ','.join(['?' for _ in pet_quality])
                    conditions.append(f"quality IN ({quality_placeholders})")
                    params.extend(pet_quality)
                    logger.info(f"添加宠物品质筛选: quality IN ({quality_placeholders}), 值: {pet_quality}")
                
                # 其他筛选条件
                if pet_growth:
                    conditions.append("growth = ?")
                    params.append(pet_growth)
                    logger.info(f"添加成长筛选: growth = {pet_growth}")
                    
                if pet_aptitude:
                    conditions.append("aptitude = ?")
                    params.append(pet_aptitude)
                    logger.info(f"添加资质筛选: aptitude = {pet_aptitude}")
                
                if pet_skill_count is not None:
                    conditions.append("skill_count = ?")
                    params.append(pet_skill_count)
                    logger.info(f"添加技能数量筛选: skill_count = {pet_skill_count}")
                
                # 构建WHERE子句
                where_clause = ""
                if conditions:
                    where_clause = "WHERE " + " AND ".join(conditions)
                
                # 构建ORDER BY子句
                order_clause = f"ORDER BY {sort_by} {sort_order.upper()}"
                
                # 计算总数
                count_sql = f"SELECT COUNT(*) FROM pets {where_clause}"
                cursor.execute(count_sql, params)
                total = cursor.fetchone()[0]
                
                # 计算分页
                total_pages = (total + page_size - 1) // page_size
                offset = (page - 1) * page_size
                
                # 查询数据
                sql = f"""
                    SELECT * FROM pets 
                    {where_clause}
                    {order_clause}
                    LIMIT ? OFFSET ?
                """
                cursor.execute(sql, params + [page_size, offset])
                rows = cursor.fetchall()
                
                # 转换数据格式
                pets = []
                for row in rows:
                    pet_dict = dict(row)
                    # 转换价格从分到元
                    if 'price' in pet_dict:
                        pet_dict['price'] = pet_dict['price'] / 100
                    pets.append(pet_dict)
                
                return {
                    "total": total,
                    "page": page,
                    "page_size": page_size,
                    "total_pages": total_pages,
                    "data": pets,
                    "year": year,
                    "month": month
                }
                
        except Exception as e:
            logger.error(f"获取宠物列表时出错: {e}")
            return {"error": f"获取宠物列表时出错: {str(e)}"}
    
    def get_pet_details(self, pet_sn: str, year: Optional[int] = None, month: Optional[int] = None) -> Optional[Dict]:
        """获取宠物详情"""
        try:
            year, month = self._validate_year_month(year, month)
            db_file = self._get_db_file(year, month)
            
            if not os.path.exists(db_file):
                return None
            
            with sqlite3.connect(db_file) as conn:
                conn.row_factory = sqlite3.Row
                cursor = conn.cursor()
                
                # 查询宠物详情
                sql = "SELECT * FROM pets WHERE pet_sn = ?"
                cursor.execute(sql, [pet_sn])
                row = cursor.fetchone()
                
                if row:
                    pet_dict = dict(row)
                    # 转换价格从分到元
                    if 'price' in pet_dict:
                        pet_dict['price'] = pet_dict['price'] / 100
                    return pet_dict
                
                return None
                
        except Exception as e:
            logger.error(f"获取宠物详情时出错: {e}")
            return None
    
    def find_pet_anchors(self, pet_data: Dict, similarity_threshold: float = 0.7, max_anchors: int = 30) -> Dict:
        """寻找宠物市场锚点"""
        try:
            if not self.evaluator:
                return {"error": "宠物锚点估价器未初始化"}
            
            if not self.pet_feature_extractor:
                return {"error": "宠物特征提取器未初始化"}
            
            # 提取宠物特征
            pet_features = self.pet_feature_extractor.extract_features(pet_data)
            
            # 查找锚点
            anchors = self.evaluator.find_anchors(
                pet_features, 
                similarity_threshold=similarity_threshold,
                max_anchors=max_anchors
            )
            
            return {
                "anchors": anchors,
                "similarity_threshold": similarity_threshold,
                "max_anchors": max_anchors,
                "found_count": len(anchors)
            }
            
        except Exception as e:
            logger.error(f"查找宠物锚点时出错: {e}")
            return {"error": f"查找宠物锚点时出错: {str(e)}"}
    
    def get_pet_valuation(self, pet_data: Dict, strategy: str = 'fair_value',
                         similarity_threshold: float = 0.7, max_anchors: int = 30) -> Dict:
        """获取宠物估价"""
        try:
            if not self.evaluator:
                return {"error": "宠物锚点估价器未初始化"}
            
            if not self.pet_feature_extractor:
                return {"error": "宠物特征提取器未初始化"}
            
            # 提取宠物特征
            pet_features = self.pet_feature_extractor.extract_features(pet_data)
            
            # 获取估价
            valuation_result = self.evaluator.evaluate(
                pet_features,
                strategy=strategy,
                similarity_threshold=similarity_threshold,
                max_anchors=max_anchors
            )
            
            return {
                "valuation": valuation_result,
                "strategy": strategy,
                "similarity_threshold": similarity_threshold,
                "max_anchors": max_anchors
            }
            
        except Exception as e:
            logger.error(f"获取宠物估价时出错: {e}")
            return {"error": f"获取宠物估价时出错: {str(e)}"} 