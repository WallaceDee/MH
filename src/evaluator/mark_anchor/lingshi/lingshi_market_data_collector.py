from datetime import datetime
from typing import Dict, Any, List, Optional, Union, Tuple
import logging
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
    from ...feature_extractor.lingshi_feature_extractor import LingshiFeatureExtractor
except ImportError:
    try:
        from src.evaluator.feature_extractor.lingshi_feature_extractor import LingshiFeatureExtractor
    except ImportError:
        # 如果都导入失败，创建一个简单的占位符
        class LingshiFeatureExtractor:
            def __init__(self):
                pass

            def extract_features(self, lingshi_data):
                return {}


class LingshiMarketDataCollector:
    """灵饰市场数据采集器 - 从数据库中获取和处理灵饰市场数据"""

    def __init__(self, db_paths: Optional[List[str]] = None):
        """
        初始化灵饰市场数据采集器

        Args:
            db_paths: 数据库文件路径列表，如果为None则自动查找当月和上月的数据库
        """
        self.db_paths = db_paths or self._find_recent_dbs()
        self.feature_extractor = LingshiFeatureExtractor()
        self.logger = logging.getLogger(__name__)

        print(f"灵饰数据采集器初始化，加载数据库: {self.db_paths}")

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
        """查找最新的灵饰数据库文件"""
        dbs = self._find_recent_dbs()
        return dbs[0] if dbs else "cbg_equip_202412.db"

    def connect_database(self, db_path: str) -> sqlite3.Connection:
        """连接到指定的灵饰数据库"""
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
                        main_attr: Optional[str] = None,
                        attrs: Optional[List[Dict[str, Any]]] = None,
                        server: Optional[str] = None,
                        is_super_simple: Optional[bool] = None,
                        limit: int = 1000) -> pd.DataFrame:
        """
        获取市场灵饰数据，从多个数据库中合并数据

        Args:
            kindid: 灵饰类型ID筛选 (61:戒指, 62:耳饰, 63:手镯, 64:佩饰)
            main_attr: 主属性(damage、deface、magic_damage、magic_deface、fengyin、anti_fengyin、speed)
            attrs: 附加属性 List[Dict] - 附加属性对象列表，最多3个
                每个对象包含:
                - attr_type: str - 属性类型，如"伤害"、"法术伤害"
                - attr_value: int - 属性数值
            level_range: 等级范围 (min_level, max_level)
            price_range: 价格范围 (min_price, max_price)
            server: 服务器筛选
            is_super_simple: 是否超级简易筛选 (基于special_effect=="[1]"判断)
            limit: 返回数据条数限制

        Returns:
            灵饰市场数据DataFrame
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
                        query += " AND kindid = ?"
                        params.append(kindid)

                    if level_range is not None:
                        min_level, max_level = level_range
                        query += " AND equip_level BETWEEN ? AND ?"
                        params.extend([min_level, max_level])

                    if price_range is not None:
                        min_price, max_price = price_range
                        query += " AND price BETWEEN ? AND ?"
                        params.extend([min_price, max_price])

                    if server is not None:
                        query += " AND server = ?"
                        params.append(server)

                    if is_super_simple is not None:
                        if is_super_simple:
                            query += " AND special_effect = ?"
                            params.append("[1]")
                        else:
                            query += " AND (special_effect != ? OR special_effect IS NULL)"
                            params.append("[1]")

                    # 主属性筛选：当传入main_attr时，筛选该属性值大于0的装备
                    if main_attr is not None:
                        # 验证主属性字段名是否有效
                        valid_main_attrs = ['damage', 'defense', 'magic_damage', 'magic_defense', 'fengyin', 'anti_fengyin', 'speed']
                        if main_attr in valid_main_attrs:
                            query += f" AND {main_attr} > 0"
                        else:
                            self.logger.warning(f"无效的主属性字段: {main_attr}, 支持的字段: {valid_main_attrs}")

                    # 添加限制
                    query += f" LIMIT {limit}"

                    # 执行查询
                    df = pd.read_sql_query(query, conn, params=params)
                    if not df.empty:
                        all_data.append(df)

            except Exception as e:
                self.logger.error(f"查询数据库失败 ({db_path}): {e}")
                continue

        # 合并所有数据
        if all_data:
            result_df = pd.concat(all_data, ignore_index=True)
            # 去重
            result_df = result_df.drop_duplicates(subset=['id'], keep='first')
            
            # 附加属性筛选：根据attr_type进行筛选
            if attrs is not None and len(attrs) > 0:
                result_df = self._filter_by_attrs(result_df, attrs)
            
            return result_df
        else:
            return pd.DataFrame()

    def _filter_by_attrs(self, data_df: pd.DataFrame, target_attrs: List[Dict[str, Any]]) -> pd.DataFrame:
        """
        根据附加属性类型筛选数据
        TODO:找出更有价值的两条组合去筛选（物理、法术、辅助）
        Args:
            data_df: 市场数据DataFrame
            target_attrs: 目标附加属性列表，每个元素包含attr_type和attr_value
        
        Returns:
            筛选后的DataFrame
        """
        if data_df.empty or not target_attrs:
            return data_df
        
        # 提取目标附加属性的类型
        target_attr_types = set()
        for attr in target_attrs:
            attr_type = attr.get('attr_type', '')
            if attr_type:
                target_attr_types.add(attr_type)
        
        if not target_attr_types:
            return data_df
        
        print(f"[附加属性筛选] 目标属性类型: {list(target_attr_types)}")
        
        # 筛选符合条件的装备
        filtered_rows = []
        
        for _, row in data_df.iterrows():
            try:
                # 提取当前装备的特征（包含附加属性）
                market_features = self.feature_extractor.extract_features(row.to_dict())
                market_attrs = market_features.get('attrs', [])
                
                if not market_attrs:
                    continue
                
                # 统计市场装备的附加属性类型
                market_attr_types = set()
                for attr in market_attrs:
                    attr_type = attr.get('attr_type', '')
                    if attr_type:
                        market_attr_types.add(attr_type)
                
                # 检查是否有任意两条属性类型相同
                # 计算目标属性和市场属性的交集
                common_attr_types = target_attr_types.intersection(market_attr_types)
                
                # 如果交集数量大于等于2，则认为匹配
                if len(common_attr_types) >= 2:
                    filtered_rows.append(row)
                    
            except Exception as e:
                self.logger.warning(f"处理装备 {row.get('id', 'unknown')} 的附加属性时出错: {e}")
                continue
        
        if filtered_rows:
            result_df = pd.DataFrame(filtered_rows)
            print(f"[附加属性筛选] 筛选前: {len(data_df)} 条，筛选后: {len(result_df)} 条")
            return result_df
        else:
            print(f"[附加属性筛选] 未找到符合条件的装备")
            return pd.DataFrame()

    def get_market_data_for_similarity(self,
                                       target_features: Dict[str, Any]) -> pd.DataFrame:
        """
        根据目标特征获取用于相似度计算的市场数据

        Args:
            target_features: 目标灵饰特征

        Returns:
            过滤后的市场数据DataFrame
        """
        # 基础过滤条件
        kindid = target_features.get('kindid')
        equip_level = target_features.get('equip_level', 0)
        
        # 等级范围：目标等级±20级
        level_range = (max(0, equip_level - 20), equip_level + 20)
        
        # 超级简易过滤
        is_super_simple = target_features.get('is_super_simple', False)
        
        # 获取市场数据
        market_data = self.get_market_data(
            kindid=kindid,
            level_range=level_range,
            is_super_simple=is_super_simple,
            limit=5000
        )
        
        if market_data.empty:
            return market_data
            
        # 提取特征
        features_list = []
        for _, row in market_data.iterrows():
            try:
                features = self.feature_extractor.extract_features(row.to_dict())
                features['id'] = row['id']
                features['price'] = row['price']
                features['server'] = row.get('server', '')
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
