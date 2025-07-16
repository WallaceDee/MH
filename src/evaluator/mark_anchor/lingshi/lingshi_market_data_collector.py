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

        # 优先查找当月和上月的数据库
        target_months = [current_month, last_month]
        print(f"优先查找数据库文件，目标月份: {target_months}")

        # 数据库文件固定存放在根目录的data文件夹中
        data_path = "data"
        found_dbs = []

        # 首先查找指定月份的数据库文件
        for month in target_months:
            db_file = os.path.join(data_path, month, f"cbg_equip_{month}.db")
            if os.path.exists(db_file):
                found_dbs.append(db_file)
                print(f"找到指定月份数据库文件: {db_file}")

        # 如果没找到指定月份的，则查找所有可用的灵饰数据库文件
        if not found_dbs:
            print("未找到指定月份的数据库文件，查找所有可用的灵饰数据库文件")
            # 查找所有年月文件夹下的数据库文件
            pattern = os.path.join(data_path, "*", "cbg_equip_*.db")
            all_dbs = glob.glob(pattern)
            
            # 按文件名排序，最新的在前
            all_dbs.sort(reverse=True)
            
            # 取最新的2个数据库文件
            found_dbs = all_dbs[:2]
            print(f"找到所有数据库文件: {all_dbs}")
            print(f"使用最新的数据库文件: {found_dbs}")

        return found_dbs

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
                        main_attr: Optional[str] = None,
                        attrs: Optional[List[Dict[str, Any]]] = None,
                        is_super_simple: Optional[bool] = None,
                        price_range: Optional[Tuple[float, float]] = None,
                        server: Optional[str] = None,
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
                    print(query)
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
            result_df = result_df.drop_duplicates(subset=['equip_sn'], keep='first')
            
            # 附加属性筛选：根据attr_type进行筛选
            if attrs is not None and len(attrs) > 0:
                result_df = self._filter_by_attrs(result_df, attrs)
            
            return result_df
        else:
            return pd.DataFrame()

    def _filter_by_attrs(self, data_df: pd.DataFrame, target_attrs: List[Dict[str, Any]]) -> pd.DataFrame:
        """
        根据附加属性类型筛选数据
       
        Args:
            data_df: 市场数据DataFrame
            target_attrs: 目标附加属性列表，每个元素包含attr_type和attr_value
        
        Returns:
            筛选后的DataFrame
        """
        if data_df.empty or not target_attrs:
            return data_df
        
        # 提取目标附加属性的类型
        target_attr_types = []
        for attr in target_attrs:
            attr_type = attr.get('attr_type', '')
            if attr_type:
                target_attr_types.append(attr_type)
        
        if not target_attr_types:
            return data_df
        
        print(f"[附加属性筛选] 目标属性类型: {target_attr_types}")
        
        # 定义属性优先级映射
        # 戒指/耳饰属性优先级：
        # 物理系：伤害(S)、物理暴击等级(A)、穿刺等级(B)、狂暴等级(C)
        # 法术系：法术伤害(S)、法术暴击等级(A)、法术伤害结果(B)
        # 辅助系：固定伤害(S)、治疗能力(A)、封印命中等级(B)、速度(C)
        # 手镯/佩饰属性优先级：
        # 气血(S)、防御(S)、抵抗封印等级(A)、抗物理暴击(A)、格挡值(B)、法术防御(B)、抗法术暴击(C)、气血回复效果(C)
        
        ring_earring_priority = {
            # 物理系 - S级
            '伤害': 1,
            # 物理系 - A级
            '物理暴击等级': 2,
            # 物理系 - B级
            '穿刺等级': 3,
            # 物理系 - C级
            '狂暴等级': 4,
            
            # 法术系 - S级
            '法术伤害': 1,
            # 法术系 - A级
            '法术暴击等级': 2,
            # 法术系 - B级
            '法术伤害结果': 3,
            
            # 辅助系 - S级
            '固定伤害': 1,
            # 辅助系 - A级
            '治疗能力': 2,
            # 辅助系 - B级
            '封印命中等级': 3,
            # 辅助系 - C级
            '速度': 4,
        }
        
        bracelet_accessory_priority = {
            # S级
            '气血': 1,
            '防御': 1,
            # A级
            '抵抗封印等级': 2,
            '抗物理暴击': 2,
            # B级
            '格挡值': 3,
            '法术防御': 3,
            # C级
            '抗法术暴击': 4,
            '气血回复效果': 4,
        }
        
        # 根据目标属性数量确定匹配策略
        target_attr_count = len(target_attr_types)
        
        # 获取目标属性的优先级排序
        def get_priority_sorted_attrs(attr_types, equipment_type):
            """根据装备类型获取优先级排序的属性列表"""
            if equipment_type in [61, 62]:  # 戒指/耳饰
                priority_map = ring_earring_priority
            elif equipment_type in [63, 64]:  # 手镯/佩饰
                priority_map = bracelet_accessory_priority
            else:
                # 未知类型，按原顺序返回
                return attr_types
            
            # 按优先级排序，优先级相同的保持原顺序
            sorted_attrs = sorted(attr_types, key=lambda x: priority_map.get(x, 999))
            return sorted_attrs
        
        # 根据目标属性数量确定匹配所需的属性
        def get_match_attrs(target_attrs, equipment_type):
            """根据目标属性数量和装备类型确定匹配所需的属性"""
            if target_attr_count == 2:
                # 2条属性时，需要2条属性类型相同
                return set(target_attrs)
            elif target_attr_count == 3:
                # 3条属性时，检查是否都相同
                unique_attrs = set(target_attrs)
                if len(unique_attrs) == 1:
                    # 3条属性都一样，必须3条匹配
                    return set(target_attrs)
                else:
                    # 3条属性不全相同，按优先级取2条
                    sorted_attrs = get_priority_sorted_attrs(target_attrs, equipment_type)
                    return set(sorted_attrs[:2])
            else:
                # 其他情况，使用所有属性
                return set(target_attrs)
        
        filtered_rows = []
        
        for _, row in data_df.iterrows():
            try:
                # 直接使用数据库中已经存在的agg_added_attrs字段，避免重复特征提取
                market_attrs = row.get('agg_added_attrs', [])
                
                # 如果agg_added_attrs是字符串（JSON），需要解析
                if isinstance(market_attrs, str):
                    import json
                    try:
                        market_attrs = json.loads(market_attrs)
                    except json.JSONDecodeError:
                        market_attrs = []

                if not market_attrs:
                    continue
                
                # 获取装备类型
                equipment_type = row.get('kindid', 0)
                
                # 统计市场装备的附加属性类型
                market_attr_types = []
                for attr in market_attrs:
                    attr_type = attr.get('attr_type', '')
                    if attr_type:
                        market_attr_types.append(attr_type)
                print(f"market_attr_types {market_attr_types}")
                
                # 确定目标匹配属性
                target_match_attrs = get_match_attrs(target_attr_types, equipment_type)
                
                # 检查匹配条件
                if target_attr_count == 2:
                    # 2条属性时，需要2条属性类型相同
                    # 检查目标属性是否都相同
                    unique_target_attrs = set(target_attr_types)
                    if len(unique_target_attrs) == 1:
                        # 2条属性都一样，需要市场装备至少有2条该类型属性
                        target_attr_type = list(unique_target_attrs)[0]
                        market_attr_counter = {}
                        for attr_type in market_attr_types:
                            market_attr_counter[attr_type] = market_attr_counter.get(attr_type, 0) + 1
                        
                        if market_attr_counter.get(target_attr_type, 0) >= 2:
                            filtered_rows.append(row)
                    else:
                        # 2条属性不同，需要市场装备包含这2种属性
                        market_attr_set = set(market_attr_types)
                        if len(target_match_attrs.intersection(market_attr_set)) >= 2:
                            filtered_rows.append(row)
                elif target_attr_count == 3:
                    # 3条属性时的特殊处理
                    unique_target_attrs = set(target_attr_types)
                    if len(unique_target_attrs) == 1:
                        # 3条属性都一样，必须3条匹配
                        market_attr_counter = {}
                        for attr_type in market_attr_types:
                            market_attr_counter[attr_type] = market_attr_counter.get(attr_type, 0) + 1
                        
                        target_attr_type = list(unique_target_attrs)[0]
                        if market_attr_counter.get(target_attr_type, 0) >= 3:
                            filtered_rows.append(row)
                    else:
                        # 3条属性不全相同，按优先级取2条匹配
                        market_attr_set = set(market_attr_types)
                        if len(target_match_attrs.intersection(market_attr_set)) >= 2:
                            filtered_rows.append(row)
                else:
                    # 其他情况，使用交集匹配
                    market_attr_set = set(market_attr_types)
                    common_attr_types = target_match_attrs.intersection(market_attr_set)
                    if len(common_attr_types) >= min(2, len(target_match_attrs)):
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
        
        # 超级简易过滤
        is_super_simple = target_features.get('is_super_simple', False)
        level_range = target_features.get('equip_level_range',(0,160))
        main_attr = target_features.get('main_attr', None)
        attrs = target_features.get('attrs', None)
        print(f"get_market_data_for_similarity_target_features: {target_features}")
        # 获取市场数据
        market_data = self.get_market_data(
            kindid=kindid,
            level_range=level_range,
            is_super_simple=is_super_simple,
            main_attr=main_attr,
            attrs=attrs,
            limit=5000
        )
        
        if market_data.empty:
            return market_data
            
        # 提取特征
        features_list = []
        for _, row in market_data.iterrows():
            try:
                features = self.feature_extractor.extract_features(row.to_dict())
                features['equip_sn'] = row.get('equip_sn', row.get('eid', row.get('id', None)))
                features['price'] = row['price']
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
            过滤后的市场数据DataFrame (已提取特征)
        """
        # 获取基础市场数据 (已包含提取的特征)
        market_data = self.get_market_data_for_similarity(target_features)
        
        if market_data.empty:
            return market_data
            
        # 应用业务规则过滤 (保持特征数据格式)
        filtered_mask = []
        
        for _, row in market_data.iterrows():
            # 这里可以添加更多的业务规则过滤逻辑
            # 例如：价格异常值过滤、属性组合过滤等
            
            # 示例：过滤价格异常值（价格过高或过低的装备）
            price = row.get('price', 0)
            if price <= 0 or price > 1000000:  # 价格范围检查
                filtered_mask.append(False)
                continue
            
            filtered_mask.append(True)
            
        # 使用布尔掩码过滤，保持DataFrame结构和特征数据
        if any(filtered_mask):
            filtered_data = market_data[filtered_mask].copy()
            print(f"[业务规则过滤] 筛选前: {len(market_data)} 条，筛选后: {len(filtered_data)} 条")
            return filtered_data
        else:
            print(f"[业务规则过滤] 所有数据都被过滤掉了")
            return pd.DataFrame()
