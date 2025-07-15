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

        print(f"召唤兽市场数据采集器初始化，加载数据库: {self.db_paths}")
    
    def _find_recent_dbs(self) -> List[str]:
        """查找当月和上月的灵饰数据库文件"""
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
                db_file = os.path.join(base_path, f"cbg_pets_{month}.db")
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
            return [f"cbg_pets_{current_month}.db", f"cbg_pets_{last_month}.db"]

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
                        limit: int = 1000) -> pd.DataFrame:
        """
        获取市场召唤兽数据，从多个数据库中合并数据

        Args:
            level_range: 等级范围 (min_level, max_level)
            price_range: 价格范围 (min_price, max_price)
            server: 服务器筛选
            limit: 返回数据条数限制
        Returns:
            召唤兽市场数据DataFrame
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
                    query = f"SELECT * FROM pets WHERE 1=1"
                    params = []

                    if level_range is not None:
                        min_level, max_level = level_range
                        query += " AND equip_level BETWEEN ? AND ?"
                        params.extend([min_level, max_level])

                    if role_grade_limit_range is not None:
                        min_role_grade_limit, max_role_grade_limit = role_grade_limit_range
                        query += " AND role_grade_limit BETWEEN ? AND ?"
                        params.extend([min_role_grade_limit, max_role_grade_limit])

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
                        all_data.append(df)
                print(f"查询数据库成功all_dataall_dataall_data ({all_data})")
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
        
        # 获取市场数据
        market_data = self.get_market_data(
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
                features['equip_sn'] = row.get('equip_sn', row.get('eid', row.get('id', None)))
                features['equip_name'] = row.get('equip_name', '未知宠物')
                features['server_name'] = row.get('server_name', '未知服务器')
                features['price'] = row.get('price', 0)
                features['level'] = row.get('level', row.get('equip_level', 0))
                features['growth'] = row.get('growth', 0)
                features['all_skill'] = row.get('all_skill', '')
                features['sp_skill'] = row.get('sp_skill', '0')
                features['is_baobao'] = row.get('is_baobao', '否')
                
                # 保留原有的id和server字段（兼容性）
                features['id'] = row.get('id', features['equip_sn'])
                features['server'] = row.get('server_name', features['server_name'])
                
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
            price = row.get('price', 0)
            if price <= 0 or price > 1000000:  # 价格范围检查
                continue
                
            filtered_data.append(row)
            
        if filtered_data:
            return pd.DataFrame(filtered_data)
        else:
            return pd.DataFrame()