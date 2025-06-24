from datetime import datetime
from typing import Dict, Any, List, Optional, Union, Tuple
import logging
import json
import numpy as np
import pandas as pd
import sqlite3
import sys
import os

# 添加项目根目录到Python路径，解决模块导入问题
current_dir = os.path.dirname(os.path.abspath(__file__))
project_root = os.path.dirname(os.path.dirname(
    os.path.dirname(os.path.dirname(current_dir))))  # 向上四级到项目根目录
sys.path.insert(0, project_root)


try:
    from ...feature_extractor.equip_feature_extractor import EquipFeatureExtractor
except ImportError:
    try:
        from src.evaluator.feature_extractor.equip_feature_extractor import EquipFeatureExtractor
    except ImportError:
        # 如果都导入失败，创建一个简单的占位符
        class EquipFeatureExtractor:
            def __init__(self):
                pass

            def extract_features(self, equip_data):
                return {}


class EquipMarketDataCollector:
    """装备市场数据采集器 - 从数据库中获取和处理装备市场数据"""

    def __init__(self, db_paths: Optional[List[str]] = None):
        """
        初始化装备市场数据采集器

        Args:
            db_paths: 数据库文件路径列表，如果为None则自动查找当月和上月的数据库
        """
        self.db_paths = db_paths or self._find_recent_dbs()
        self.feature_extractor = EquipFeatureExtractor()
        self.logger = logging.getLogger(__name__)

        print(f"装备数据采集器初始化，加载数据库: {self.db_paths}")

    def _find_recent_dbs(self) -> List[str]:
        """查找当月和上月的装备数据库文件"""
        import glob
        from datetime import datetime, timedelta

        # 获取当前月份和上个月份
        now = datetime.now()
        current_month = now.strftime("%Y%m")

        # 计算上个月
        last_month_date = now.replace(day=1) - timedelta(days=1)
        last_month = last_month_date.strftime("%Y%m")

        target_months = [current_month, last_month]
        print(f"查找数据库文件，目标月份: {target_months}")

        # 数据库文件只在根目录下的data文件夹中
        # 从当前位置向上查找到项目根目录的data文件夹
        current_path = os.path.abspath(".")

        # 向上查找直到找到data文件夹或到达系统根目录
        possible_base_paths = []
        search_path = current_path
        for _ in range(5):  # 最多向上5级目录
            data_path = os.path.join(search_path, "data")
            if os.path.exists(data_path) and os.path.isdir(data_path):
                possible_base_paths.append(data_path)
                break
            parent = os.path.dirname(search_path)
            if parent == search_path:  # 已经到达根目录
                break
            search_path = parent

        # 如果没找到，使用默认的data路径
        if not possible_base_paths:
            possible_base_paths = ["data"]

        found_dbs = []

        for base_path in possible_base_paths:
            for month in target_months:
                db_file = os.path.join(base_path, f"cbg_equip_{month}.db")
                if os.path.exists(db_file):
                    found_dbs.append(db_file)

        # 去重并排序
        found_dbs = list(set(found_dbs))
        found_dbs.sort(reverse=True)  # 最新的在前

        if found_dbs:
            print(f"找到数据库文件: {found_dbs}")
            return found_dbs
        else:
            print(f"未找到数据库文件，使用默认文件名")
            # 如果找不到，返回默认的当月和上月文件名
            return [f"cbg_equip_{current_month}.db", f"cbg_equip_{last_month}.db"]

    def _find_latest_db(self) -> str:
        """查找最新的装备数据库文件"""
        dbs = self._find_recent_dbs()
        return dbs[0] if dbs else "cbg_equip_202412.db"

    def connect_database(self, db_path: str) -> sqlite3.Connection:
        """连接到指定的装备数据库"""
        try:
            conn = sqlite3.connect(db_path)
            return conn
        except Exception as e:
            self.logger.error(f"数据库连接失败 ({db_path}): {e}")
            raise

    def get_market_data(self,
                        kindid: Optional[int] = None,
                        level_range: Optional[Tuple[int, int]] = None,
                        price_range: Optional[Tuple[float, float]] = None,
                        server: Optional[str] = None,
                        special_skill: Optional[int] = None,
                        suit_effect: Optional[int] = None,
                        special_effect: Optional[List[str]] = None,
                        exclude_special_effect: Optional[List[int]] = None,
                        limit: int = 1000) -> pd.DataFrame:
        """
        获取市场装备数据，从多个数据库中合并数据

        Args:
            kindid: 装备类型ID筛选
            level_range: 等级范围 (min_level, max_level)
            price_range: 价格范围 (min_price, max_price)
            server: 服务器筛选
            special_skill: 特技筛选（必须完全一致）
            special_effect: 特效筛选（高价值必须包含）
            exclude_special_effect: 排除特效筛选（排除具有这些特效的装备）
            suit_effect: 套装效果有三种，如果是"附加状态"/"追加法术"，则传入过滤，"变身术"/"变化咒"，则不传入过滤，在锚定的时候做聚类
            limit: 返回数据条数限制

        Returns:
            装备市场数据DataFrame
        """
        all_data = []

        for db_path in self.db_paths:
            try:
                # 检查数据库文件是否存在
                if not os.path.exists(db_path):
                    print(f"数据库文件不存在: {db_path}")
                    continue

                with self.connect_database(db_path) as conn:
                    # 构建SQL查询
                    query = f"SELECT * FROM equipments WHERE 1=1"
                    params = []

                    if kindid is not None:
                        # 直接使用kindid字段
                        query += " AND kindid = ?"
                        params.append(kindid)

                    if special_skill is not None:
                        query += " AND special_skill = ?"
                        params.append(special_skill)

                    if suit_effect is not None and suit_effect > 0:
                        query += " AND suit_effect = ?"
                        params.append(suit_effect)

                    if special_effect is not None:
                        # 特效筛选（多选，JSON数组格式）
                        if special_effect and len(special_effect) > 0:
                            effect_conditions = []
                            for effect in special_effect:
                                # 使用精确的JSON数组匹配，避免数字包含关系的误匹配
                                # 匹配模式：[6], [6,x], [x,6], [x,6,y] 等，但不匹配16, 26等包含6的数字
                                effect_conditions.append(
                                    "(special_effect LIKE ? OR special_effect LIKE ? OR special_effect LIKE ? OR special_effect LIKE ?)")
                                # 四种匹配模式：单独存在、开头、中间、结尾
                                params.extend([
                                    f'[{effect}]',        # 只有这一个特效：[6]
                                    f'[{effect},%',       # 在开头：[6,x,...]
                                    f'%,{effect},%',      # 在中间：[x,6,y,...]
                                    f'%,{effect}]'        # 在结尾：[x,y,6]
                                ])

                            # 将特效条件添加到查询中
                            if effect_conditions:
                                query += f" AND ({' OR '.join(effect_conditions)})"

                    if exclude_special_effect is not None:
                        # 排除特效筛选：排除具有指定特效的装备
                        if exclude_special_effect and len(exclude_special_effect) > 0:
                            exclude_conditions = []
                            for effect in exclude_special_effect:
                                # 使用NOT操作排除包含指定特效的装备
                                exclude_conditions.append(
                                    "NOT (special_effect LIKE ? OR special_effect LIKE ? OR special_effect LIKE ? OR special_effect LIKE ?)")
                                # 四种匹配模式：单独存在、开头、中间、结尾
                                params.extend([
                                    f'[{effect}]',        # 只有这一个特效：[1]
                                    f'[{effect},%',       # 在开头：[1,x,...]
                                    f'%,{effect},%',      # 在中间：[x,1,y,...]
                                    f'%,{effect}]'        # 在结尾：[x,y,1]
                                ])

                            # 将排除条件添加到查询中
                            if exclude_conditions:
                                query += f" AND ({' AND '.join(exclude_conditions)})"

                    if level_range:
                        # 直接使用equip_level字段
                        query += " AND equip_level BETWEEN ? AND ?"
                        params.extend(level_range)

                    if price_range:
                        query += " AND price BETWEEN ? AND ?"
                        params.extend(price_range)

                    if server:
                        query += " AND server = ?"
                        params.append(server)

                    # 每个数据库限制一定数量，总体控制在limit内
                    db_limit = min(limit // len(self.db_paths) + 100, limit)
                    query += f" ORDER BY update_time DESC LIMIT {db_limit}"

                    try:
                        df = pd.read_sql_query(query, conn, params=params)
                        if not df.empty:
                            df['source_db'] = db_path  # 标记数据来源
                            all_data.append(df)
                            print(f"从 {db_path} 加载了 {len(df)} 条装备数据")
                    except Exception as e:
                        self.logger.error(f"查询装备数据失败 ({db_path}): {e}")
                        continue

            except Exception as e:
                self.logger.error(f"处理数据库失败 ({db_path}): {e}")
                continue

        # 合并所有数据
        if all_data:
            combined_df = pd.concat(all_data, ignore_index=True)

            # 按时间排序并限制总数量
            if 'update_time' in combined_df.columns:
                combined_df = combined_df.sort_values(
                    'update_time', ascending=False)

            combined_df = combined_df.head(limit)

            print(f"总共加载了 {len(combined_df)} 条装备数据")
            return combined_df
        else:
            print("未从任何数据库加载到装备数据")
            return pd.DataFrame()

    def get_market_data_for_similarity(self,
                                       target_features: Dict[str, Any]) -> pd.DataFrame:
        """
        获取用于相似度计算的市场数据
        
        专门为相似度计算优化的数据获取方法，包含以下特殊逻辑：
        1. 高价值特效的公平性筛选
        2. 相似度计算相关的特效筛选
        3. 适当的数据量控制

        Args:
            target_features: 目标装备特征

        Returns:
            市场数据DataFrame
        """
        try:
            # 提取基础筛选条件
            level_range = target_features.get('equip_level_range', None)
            kindid = target_features.get('kindid', None)
            special_skill = target_features.get('special_skill', 0)
            special_effect = target_features.get('special_effect', [])
            suit_effect = target_features.get('suit_effect', 0)
            
            # 处理特效筛选逻辑
            filtered_special_effect = None
            exclude_special_effect = None
            
            # 定义重要特效
            high_value_effects = [1, 3, 5]  # 无级别，愤怒，永不磨损
            important_effects = [1, 2, 3, 4, 5, 7, 11, 12, 16]  # 相似度计算中重要的特效
            
            # 检查目标装备是否包含高价值特效
            target_has_high_value_effects = False
            
            if special_effect and len(special_effect) > 0:
                # 筛选出重要特效用于相似度计算
                filtered_effects = []
                for effect in special_effect:
                    if effect in important_effects:
                        filtered_effects.append(effect)
                    # 检查是否包含高价值特效
                    if effect in high_value_effects:
                        target_has_high_value_effects = True
                
                if filtered_effects:
                    filtered_special_effect = filtered_effects
            
            # 公平性筛选：如果目标装备不包含高价值特效，则排除具有这些特效的装备
            if not target_has_high_value_effects:
                exclude_special_effect = high_value_effects
                print(f"目标装备不包含高价值特效 {high_value_effects}，将排除具有这些特效的装备")
             
            print(f"相似度筛选 - 重要特效: {filtered_special_effect}, 排除特效: {exclude_special_effect}")
            
            # 调用基础数据获取方法（应用业务规则）
            market_data = self.get_market_data_with_business_rules(
                target_features=target_features,
                special_effect=filtered_special_effect,
                exclude_special_effect=exclude_special_effect,
                limit=2000  # 相似度计算需要更多数据
            )

            return market_data

        except Exception as e:
            self.logger.error(f"获取相似度计算市场数据失败: {e}")
            return pd.DataFrame()

    def _should_filter_suit_effect(self, suit_effect: int) -> bool:
        """
        判断套装效果是否应该被用于筛选
        
        业务规则：只有特定的套装效果才用于精确筛选，
        其他套装效果在相似度计算时进行聚类处理
        
        Args:
            suit_effect: 套装效果ID
            
        Returns:
            bool: 是否应该筛选此套装效果
        """
        # 允许精确筛选的套装效果：定心术、变身术、碎星诀、天神护体、满天花雨、浪涌
        allowed_suit_effects = [4002, 4011, 4017, 4019, 3011, 3050]
        return suit_effect in allowed_suit_effects

    def get_market_data_with_business_rules(self,
                                           target_features: Dict[str, Any],
                                           **kwargs) -> pd.DataFrame:
        """
        应用业务规则获取市场数据
        
        这个方法在基础查询的基础上应用特定的业务规则，
        比如套装效果的筛选策略等
        
        Args:
            target_features: 目标装备特征
            **kwargs: 其他查询参数
            
        Returns:
            市场数据DataFrame
        """
        try:
            # 处理套装效果业务规则
            suit_effect = target_features.get('suit_effect', 0)
            filtered_suit_effect = None
            
            if suit_effect and self._should_filter_suit_effect(suit_effect):
                filtered_suit_effect = suit_effect
                print(f"套装效果 {suit_effect} 将用于精确筛选")
            else:
                print(f"套装效果 {suit_effect} 将在相似度计算时处理")
            
            # 合并参数
            query_params = {
                'kindid': target_features.get('kindid'),
                'level_range': target_features.get('equip_level_range'),
                'special_skill': target_features.get('special_skill', 0),
                'suit_effect': filtered_suit_effect,
                **kwargs
            }
            
            return self.get_market_data(**query_params)
            
        except Exception as e:
            self.logger.error(f"应用业务规则获取市场数据失败: {e}")
            return pd.DataFrame()
