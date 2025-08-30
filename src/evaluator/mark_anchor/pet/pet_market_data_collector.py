import sys
import os

# 添加项目根目录到Python路径，解决模块导入问题
current_dir = os.path.dirname(os.path.abspath(__file__))
project_root = os.path.dirname(os.path.dirname(current_dir))  # 向上两级到项目根目录
sys.path.insert(0, project_root)

import sqlite3
import pandas as pd
import logging
from typing import Dict, Any, List, Optional, Tuple, Union
from datetime import datetime

try:
    from ...feature_extractor.pet_feature_extractor import PetFeatureExtractor
except ImportError:
    from src.evaluator.feature_extractor.pet_feature_extractor import PetFeatureExtractor


class PetMarketDataCollector:
    """市场数据采集器 - 从数据库中获取和处理召唤兽市场数据"""

    def __init__(self, db_paths: Optional[List[str]] = None):
        """
        初始化召唤兽市场数据采集器

        Args:
            db_paths: 数据库文件路径列表，如果为None则自动查找当月和上月的数据库
        """
        self.db_paths = db_paths or self._find_recent_dbs()
        self.feature_extractor = PetFeatureExtractor()
        self.logger = logging.getLogger(__name__)
    
    def _find_recent_dbs(self) -> List[str]:
        """查找所有可用的召唤兽数据库文件"""
        import glob
        from datetime import datetime, timedelta

        # 获取当前月份和上个月份
        now = datetime.now()
        current_month = now.strftime("%Y%m")

        # 计算上个月
        last_month_date = now.replace(day=1) - timedelta(days=1)
        last_month = last_month_date.strftime("%Y%m")

        # 优先查找当月和上月的数据库
        target_months = [current_month, last_month]

            # 数据库文件固定存放在根目录的data文件夹中
        from src.utils.project_path import get_data_path
        data_path = get_data_path()
        found_dbs = []

        # 首先查找指定月份的数据库文件
        for month in target_months:
            db_file = os.path.join(data_path, month, f"cbg_pets_{month}.db")
            if os.path.exists(db_file):
                found_dbs.append(db_file)

        # 如果没找到指定月份的，则查找所有可用的召唤兽数据库文件
        if not found_dbs:
            # 查找所有年月文件夹下的数据库文件
            pattern = os.path.join(data_path, "*", "cbg_pets_*.db")
            all_dbs = glob.glob(pattern)
            
            # 按文件名排序，最新的在前
            all_dbs.sort(reverse=True)
            
            # 取最新的2个数据库文件
            found_dbs = all_dbs[:2]

        return found_dbs

    def connect_database(self, db_path: str) -> sqlite3.Connection:
        """连接到指定的召唤兽数据库"""
        try:
            conn = sqlite3.connect(db_path)
            return conn
        except Exception as e:
            self.logger.error(f"数据库连接失败 ({db_path}): {e}")
            raise
    
    def get_market_data(self,
                        level_range: Optional[Tuple[int, int]] = None,
                        role_grade_limit_range: Optional[Tuple[int, int]] = None,
                        price_range: Optional[Tuple[float, float]] = None,
                        server: Optional[str] = None,
                        all_skill: Optional[Union[str, List[str]]] = None,
                        limit: int = 1000) -> pd.DataFrame:
        """
        获取市场召唤兽数据，从多个数据库中合并数据

        Args:
            level_range: 等级范围 (min_level, max_level)
            price_range: 价格范围 (min_price, max_price)
            server: 服务器筛选
            limit: 返回数据条数限制

            role_grade_limit_range: 携带等级 (min_role_grade_limit, max_role_grade_limit)
            all_skill: 技能 使用了管道符拼接的技能字符串以"|"
        Returns:
            召唤兽市场数据DataFrame
        """
        all_data = []

        # 处理all_skill参数，支持字符串或列表
        target_skills = []
        if all_skill:
            if isinstance(all_skill, str):
                target_skills = [s for s in all_skill.split('|') if s]
            elif isinstance(all_skill, list):
                target_skills = [str(s) for s in all_skill if s]

        for db_path in self.db_paths:
            try:
                # 检查数据库文件是否存在
                if not os.path.exists(db_path):
                    print(f"数据库文件不存在: {db_path}")
                    continue

                with self.connect_database(db_path) as conn:
                    # `role_grade_limit` - 角色等级限制

                    # `equip_level` - 装备等级

                    # `growth` - 成长值

                    # `is_baobao` - 是否宝宝

                    # `all_skill` - 所有技能（字符串）

                    # `evol_skill_list` - 进化技能列表（JSON数组）

                    # `texing` - 特性信息（JSON对象）

                    # `lx` - 灵性值

                    # `equip_list` - 装备列表（JSON数组）

                    # `equip_list_amount` - 装备列表金额

                    # `neidan` - 内丹信息（JSON数组）

                    # `equip_sn` - 装备序列号
                    
                    # `price` - 价格
                    # 构建SQL查询
                    query = f"SELECT pets.role_grade_limit, pets.equip_level, pets.growth, pets.is_baobao, pets.all_skill, pets.evol_skill_list, pets.texing, pets.lx, pets.equip_list, pets.equip_list_amount, pets.neidan, pets.equip_sn, pets.price FROM pets WHERE 1=1"
                    params = []

                    if level_range is not None:
                        min_level, max_level = level_range
                        query += " AND equip_level BETWEEN ? AND ?"
                        params.extend([min_level, max_level])

                    if role_grade_limit_range is not None:
                        min_role_grade_limit, max_role_grade_limit = role_grade_limit_range
                        query += " AND role_grade_limit BETWEEN ? AND ?"
                        params.extend([min_role_grade_limit, max_role_grade_limit])

                    # 技能SQL初步过滤
                    if target_skills:
                        for skill in target_skills:
                            # 用|分隔，LIKE能初步过滤，防止全表扫描
                            query += " AND all_skill LIKE ?"
                            params.append(f"%{skill}%")
                        # 技能数量过滤 过滤出技能数量 <= len(target_skills)+2 的数据
                        skill_count_limit = len(target_skills) + 1
                        query += " AND (LENGTH(all_skill) - LENGTH(REPLACE(all_skill, '|', '')) + 1) <= ?"
                        params.append(skill_count_limit)

                    if price_range is not None:
                        min_price, max_price = price_range
                        query += " AND price BETWEEN ? AND ?"
                        params.extend([min_price, max_price])

                    if server is not None:
                        query += " AND server = ?"
                        params.append(server)

                    query += f" LIMIT {limit}"
                    # 执行查询
                    df = pd.read_sql_query(query, conn, params=params)
                    if not df.empty:
                        # Python集合精确过滤
                        if target_skills:
                            target_set = set(target_skills)
                            def match(row):
                                all_skill_val = row.get('all_skill', '')
                                skill_set = set(all_skill_val.split('|')) if all_skill_val else set()
                                return target_set.issubset(skill_set)
                            df = df[df.apply(match, axis=1)]
                        all_data.append(df)
            except Exception as e:
                self.logger.error(f"查询数据库失败 ({db_path}): {e}")
                continue

        # 合并所有数据
        if all_data:
            result_df = pd.concat(all_data, ignore_index=True)
            # 去重
            result_df = result_df.drop_duplicates(subset=['equip_sn'], keep='first')
            return result_df
        else:
            return pd.DataFrame()
        
    def get_market_data_for_similarity(self,
                                       target_features: Dict[str, Any]) -> pd.DataFrame:
        """
        根据目标特征获取用于相似度计算的市场数据

        Args:
            target_features: 目标召唤兽特征

        Returns:
            过滤后的市场数据DataFrame
        """
        # 基础过滤条件
        role_grade_limit = target_features.get('role_grade_limit', 0)
        
        # 等级范围：目标等级±20级
        role_grade_limit_range = (max(0, role_grade_limit - 20), role_grade_limit + 20)

        all_skill = target_features.get('all_skill', '')
        
        # 获取市场数据
        market_data = self.get_market_data(
            role_grade_limit_range=role_grade_limit_range,
            all_skill=all_skill,
            limit=5000
        )
        
        if market_data.empty:
            return market_data
            
        # 提取特征
        features_list = []
        for _, row in market_data.iterrows():
            try:
                features = self.feature_extractor.extract_features(row.to_dict())
                
                # 保留原始关键字段，确保接口返回时有完整信息
                features['equip_sn'] = row.get('equip_sn', row.get('eid',None))
                features['price'] = row.get('price', 0)
                
                features_list.append(features)
            except Exception as e:
                self.logger.warning(f"提取特征失败: {e}")
                continue
                
        if features_list:
            return pd.DataFrame(features_list)
        else:
            return pd.DataFrame()
        
    def get_market_data_with_business_rules(self,
                                           target_features: Dict[str, Any],
                                           **kwargs) -> pd.DataFrame:
        """
        根据业务规则获取市场数据

        Args:
            target_features: 目标灵饰特征
            **kwargs: 其他过滤参数

        Returns: 
            过滤后的市场数据DataFrame
        """
        # 获取基础市场数据
        market_data = self.get_market_data_for_similarity(target_features)
        
        if market_data.empty:
            return market_data
            
        # 应用业务规则过滤
        filtered_data = []
        
        for _, row in market_data.iterrows():
            # 这里可以添加更多的业务规则过滤逻辑
            # 例如：价格异常值过滤、属性组合过滤等
            
            # 示例：过滤价格异常值（价格过高或过低的装备）
            # price = row.get('price', 0)
            # if price <= 0 or price > 1000000:  # 价格范围检查
            #     continue
                
            filtered_data.append(row)
            
        if filtered_data:
            return pd.DataFrame(filtered_data)
        else:
            return pd.DataFrame()