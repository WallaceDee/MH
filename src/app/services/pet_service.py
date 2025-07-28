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

from src.utils.project_path import get_project_root, get_data_path

logger = logging.getLogger(__name__)

# 动态导入评估器，避免循环导入
try:
    from evaluator.mark_anchor.pet.index import PetMarketAnchorEvaluator
    from evaluator.feature_extractor.pet_feature_extractor import PetFeatureExtractor
    from evaluator.constants.equipment_types import PET_EQUIP_KINDID
except ImportError:
    PetMarketAnchorEvaluator = None
    PetFeatureExtractor = None
    logger.warning("无法导入宠物锚点估价器或特征提取器")


class PetService:
    def __init__(self):
        # 获取项目根目录
        self.project_root = get_project_root()
        self.data_dir = get_data_path()
        
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
        if PetMarketAnchorEvaluator:
            try:
                self.evaluator = PetMarketAnchorEvaluator()
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
        return os.path.join(self.data_dir, f'{year}{month:02d}',f'cbg_pets_{year}{month:02d}.db')
    
    def get_pets(self, page: int = 1, page_size: int = 10, year: Optional[int] = None, month: Optional[int] = None,
                 level_min: Optional[int] = None, level_max: Optional[int] = None,
                 price_min: Optional[int] = None, price_max: Optional[int] = None,
                 pet_skills: Optional[List[str]] = None,
                 pet_growth: Optional[str] = None,
                 pet_skill_count: Optional[int] = None,
                 pet_lx: Optional[int] = None,
                 pet_texing: Optional[List[str]] = None,
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
                
                # 宠物技能筛选（多选）
                if pet_skills and len(pet_skills) > 0:
                    skill_conditions = []
                    for skill in pet_skills:
                        # 使用all_skill字段进行搜索，处理管道符分隔格式 "305|316|304|301"
                        skill_conditions.append("""
                            (all_skill = ? OR all_skill LIKE ? OR all_skill LIKE ? OR all_skill LIKE ?)
                        """)
                        params.extend([
                            skill,              # 只有这一个技能："305"
                            f'{skill}|%',       # 在开头："305|x|..."
                            f'%|{skill}|%',     # 在中间："|x|305|y|"
                            f'%|{skill}'        # 在结尾："|x|y|305"
                        ])
                    conditions.append(f"({' AND '.join(skill_conditions)})")
                    logger.info(f"添加宠物技能筛选: {pet_skills}")
                
                # 其他筛选条件
                if pet_growth:
                    conditions.append("growth >= ?")
                    params.append(pet_growth)
                    logger.info(f"添加成长筛选: growth >= {pet_growth}")
                # 灵性值
                if pet_lx:
                    conditions.append("lx >= ?")
                    params.append(pet_lx)
                    logger.info(f"添加灵性筛选: lx >= {pet_lx}")
                
                # 特性筛选（多选）
                if pet_texing and len(pet_texing) > 0:
                    texing_conditions = []
                    for texing_id in pet_texing:
                        # 使用texing字段进行搜索，处理JSON格式 {"id": 723, "name": "洞察", ...}
                        texing_conditions.append("texing LIKE ?")
                        params.append(f'%"id": {texing_id}%')
                    conditions.append(f"({' OR '.join(texing_conditions)})")
                    logger.info(f"添加特性筛选: {pet_texing}")
                
                if pet_skill_count is not None:
                    # 根据all_skills字段的长度过滤，计算管道符分隔的技能数量
                    conditions.append("(LENGTH(all_skill) - LENGTH(REPLACE(all_skill, '|', '')) + 1) >= ?")
                    params.append(pet_skill_count)
                    logger.info(f"添加技能数量筛选: 技能数量 >= {pet_skill_count}")
                
                # 构建WHERE子句
                where_clause = ""
                if conditions:
                    where_clause = "WHERE " + " AND ".join(conditions)
                
                # 构建ORDER BY子句
                if sort_by == 'skill_count':
                    # 按技能数量排序：计算all_skill字段中管道符的数量+1，处理空字符串情况
                    order_clause = f"ORDER BY CASE WHEN all_skill = '' OR all_skill IS NULL THEN 0 ELSE (LENGTH(all_skill) - LENGTH(REPLACE(all_skill, '|', '')) + 1) END {sort_order.upper()}"
                else:
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
                pets_rows = cursor.fetchall()
                
                # 先将sqlite3.Row对象转换为可修改的字典
                pets = [dict(row) for row in pets_rows]
                
                # 宠物装备批量估价逻辑，只估价前3个非null装备
                all_equips = []
                equip_index_map = []  # (pet_idx, equip_idx) -> all_equips index
                for pet_idx, pet in enumerate(pets):
                    equip_list_raw = pet.get('equip_list', '[]')
                    try:
                        equip_list = json.loads(equip_list_raw)
                    except Exception:
                        equip_list = []
                    for equip_idx in range(3):
                        equip = equip_list[equip_idx] if equip_idx < len(equip_list) else None
                        if equip:
                            all_equips.append({
                                'kindid': PET_EQUIP_KINDID,
                                'large_equip_desc':equip.get('desc', ''),
                            })
                            equip_index_map.append((pet_idx, equip_idx))

                equip_valuations = []
                if all_equips:
                    from src.app.services.equipment_service import equipment_service
                    try:
                        # 批量估价写死参数 TODO:
                        result = equipment_service.batch_equipment_valuation(all_equips,'fair_value',0.8,30)
                        if isinstance(result, dict):
                            equip_valuations = result.get('results', [])
                        else:
                            equip_valuations = result
                        logger.info(f"批量装备估价完成，成功估价 {len(equip_valuations)} 个装备")
                    except Exception as e:
                        import traceback
                        logger.warning(f"批量装备估价时部分装备失败: {e} (type={type(e)})\n{traceback.format_exc()}")
                        equip_valuations = [{} for _ in all_equips]

                for pet_idx, pet in enumerate(pets):
                    equip_list_raw = pet.get('equip_list', '[]')
                    try:
                        equip_list = json.loads(equip_list_raw)
                    except Exception:
                        equip_list = []
                    equip_list_price = []
                    for equip_idx in range(3):
                        equip = equip_list[equip_idx] if equip_idx < len(equip_list) else None
                        if equip:
                            try:
                                idx = equip_index_map.index((pet_idx, equip_idx))
                                if 0 <= idx < len(equip_valuations):
                                    price_info = equip_valuations[idx]
                                else:
                                    logger.warning(f"装备估价索引超界: idx={idx}, len(equip_valuations)={len(equip_valuations)}")
                                    price_info = {}
                            except Exception as e:
                                logger.warning(f"装备估价回填异常: {e}")
                                price_info = {}
                            equip_list_price.append(price_info)
                        else:
                            equip_list_price.append(None)
                    pet['equip_list_price'] = equip_list_price
                
                return {
                    "total": total,
                    "page": page,
                    "page_size": page_size,
                    "total_pages": total_pages,
                    "data": pets,  # 已经转换为字典列表，包含equip_list_price
                    "year": year,
                    "month": month
                }
                
        except Exception as e:
            import traceback
            logger.error(f"获取宠物列表时出错: {e} (type={type(e)})\n{traceback.format_exc()}")
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
                    return pet_dict
                
                return None
                
        except Exception as e:
            logger.error(f"获取宠物详情时出错: {e}")
            return None
    
    def _get_pet_by_equip_sn(self, equip_sn: str, year: Optional[int] = None, month: Optional[int] = None) -> Optional[Dict]:
        """根据equip_sn获取宠物信息"""
        try:
            year, month = self._validate_year_month(year, month)
            db_file = self._get_db_file(year, month)
            
            if not os.path.exists(db_file):
                return None
            
            with sqlite3.connect(db_file) as conn:
                conn.row_factory = sqlite3.Row
                cursor = conn.cursor()
                
                # 查询宠物信息
                sql = "SELECT * FROM pets WHERE equip_sn = ?"
                cursor.execute(sql, [equip_sn])
                row = cursor.fetchone()
                
                if row:
                    pet_dict = dict(row)
                    return pet_dict
                
                return None
                
        except Exception as e:
            logger.error(f"根据equip_sn获取宠物信息时出错: {e}")
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
              # 确保特征中包含equip_sn信息，用于排除自身
            if 'equip_sn' in pet_data:
                pet_features['equip_sn'] = pet_data['equip_sn']
            # 查找锚点
            anchors = self.evaluator.find_market_anchors(
                pet_features, 
                similarity_threshold=similarity_threshold,
                max_anchors=max_anchors
            )
            
            # 处理锚点数据
            processed_anchors = []
            for anchor in anchors:
                anchor_equip_sn = anchor.get("equip_sn")
                
                # 通过equip_sn查询完整的宠物信息
                full_pet_info = None
                if anchor_equip_sn:
                    full_pet_info = self._get_pet_by_equip_sn(anchor_equip_sn)
                
                # 组合锚点信息和完整宠物信息
                if full_pet_info:
                    anchor_info = {
                        **full_pet_info,
                        "equip_sn": anchor_equip_sn,
                        "similarity": round(float(anchor.get("similarity", 0)), 3),
                    }
                else:
                    # 如果无法获取完整信息，使用基础信息
                    anchor_info = {
                        "equip_sn": anchor_equip_sn,
                        "similarity": round(float(anchor.get("similarity", 0)), 3),
                        "price": float(anchor.get("price", 0)),
                        "equip_name": "未知宠物",
                        "server_name": "未知服务器",
                        "level": 0,
                        "growth": 0,
                        "all_skill": "",
                        "sp_skill": "0",
                        "is_baobao": "否",
                    }
                processed_anchors.append(anchor_info)
            
            return {
                "anchors": processed_anchors,
                "similarity_threshold": similarity_threshold,
                "max_anchors": max_anchors,
                "found_count": len(processed_anchors)
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

            # 策略校验
            valid_strategies = ['fair_value', 'market_price', 'weighted_average']
            if strategy not in valid_strategies:
                return {
                    "error": f"无效的估价策略: {strategy}，有效策略: {', '.join(valid_strategies)}"
                }
            if not 0.0 <= similarity_threshold <= 1.0:
                return {"error": "相似度阈值必须在0.0-1.0之间"}
            if not 1 <= max_anchors <= 100:
                return {"error": "最大锚点数量必须在1-100之间"}

            # 特征提取
            pet_features = self.pet_feature_extractor.extract_features(pet_data)

            # 确保特征中包含equip_sn信息，用于排除自身
            if 'equip_sn' in pet_data:
                pet_features['equip_sn'] = pet_data['equip_sn']

            # 估价
            result = self.evaluator.calculate_value(
                pet_features,
                strategy=strategy,
                similarity_threshold=similarity_threshold,
                max_anchors=max_anchors
            )
            if "error" in result:
                return {
                    "error": result["error"],
                    "estimated_price": 0,
                    "estimated_price_yuan": 0
                }
            estimated_price = result.get("estimated_price", 0)

            # 直接使用calculate_value返回的锚点信息，避免重复查找
            anchors = result.get("anchors", [])
            anchor_count = result.get("anchor_count", 0)

            return {
                "estimated_price": estimated_price,
                "estimated_price_yuan": round(estimated_price / 100, 2),
                "strategy": strategy,
                "anchor_count": anchor_count,
                "confidence": result.get("confidence", 0),
                "similarity_threshold": similarity_threshold,
                "max_anchors": max_anchors,
                "anchors": anchors,
                "price_range": result.get("price_range", {}),
                "fallback_used": result.get("fallback_used", False)
            }
        except Exception as e:
            logger.error(f"获取宠物估价时出错: {e}")
            return {"error": f"获取宠物估价时出错: {str(e)}"} 