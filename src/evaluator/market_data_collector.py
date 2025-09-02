import sys
import os

# 添加项目根目录到Python路径，解决模块导入问题
from src.utils.project_path import get_project_root
project_root = get_project_root()
sys.path.insert(0, project_root)

import sqlite3
import pandas as pd
import numpy as np
import json
import logging
from typing import Dict, Any, List, Optional, Union
from datetime import datetime

try:
    from .feature_extractor.feature_extractor import FeatureExtractor
except ImportError:
    from src.evaluator.feature_extractor.feature_extractor import FeatureExtractor


class MarketDataCollector:
    """市场数据采集器 - 从数据库中获取和处理角色市场数据"""
    
    def __init__(self, db_path: Optional[str] = None, db_type: str = 'normal'):
        """
        初始化市场数据采集器
        
        Args:
            db_path: 数据库文件路径，如果为None则自动查找
            db_type: 数据库类型，'normal' 或 'empty'
        """
        self.logger = logging.getLogger(__name__)
        self.feature_extractor = FeatureExtractor()
        self.market_data = pd.DataFrame()
        self.db_type = db_type
        
        # 自动查找数据库文件
        if db_path is None:
            found_dbs = self._find_recent_dbs()
            # 使用第一个找到的数据库文件
            self.db_path = found_dbs[0] if found_dbs else None
        else:
            self.db_path = db_path
            

        
        print(f"空号市场数据采集器初始化完成，数据库路径: {self.db_path}")
    
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

        # 优先查找当月和上月的数据库
        target_months = [current_month, last_month]
        print(f"优先查找数据库文件，目标月份: {target_months}")

        # 数据库文件固定存放在根目录的data文件夹中
        from src.utils.project_path import get_data_path
        data_path = get_data_path()
        found_dbs = []

        # 首先查找指定月份的数据库文件
        for month in target_months:
            db_file = os.path.join(data_path, month, f"cbg_empty_roles_{month}.db")
            if os.path.exists(db_file):
                found_dbs.append(db_file)
                print(f"找到指定月份数据库文件: {db_file}")

        # 如果没找到指定月份的，则查找所有可用的装备数据库文件
        if not found_dbs:
            print("未找到指定月份的数据库文件，查找所有可用的装备数据库文件")
            # 查找所有年月文件夹下的数据库文件
            pattern = os.path.join(data_path, "*", "cbg_empty_roles_*.db")
            all_dbs = glob.glob(pattern)

            # 按文件名排序，最新的在前
            all_dbs.sort(reverse=True)

            # 取最新的2个数据库文件
            found_dbs = all_dbs[:2]
            print(f"找到所有数据库文件: {all_dbs}")
            print(f"使用最新的数据库文件: {found_dbs}")
        return found_dbs
    
    def refresh_market_data(self, 
                           filters: Optional[Dict[str, Any]] = None,
                           max_records: int = 1000) -> pd.DataFrame:
        """
        刷新市场数据
        
        Args:
            filters: 筛选条件字典，例如 {'level_min': 109, 'price_max': 10000}
            max_records: 最大记录数
            
        Returns:
            pd.DataFrame: 处理后的市场数据
        """
        try:
            print(f"开始刷新市场数据，最大记录数: {max_records}")
            
            # 检查数据库路径
            if not self.db_path:
                raise ValueError("数据库路径未设置或未找到有效的数据库文件")
            
            if not os.path.exists(self.db_path):
                raise FileNotFoundError(f"数据库文件不存在: {self.db_path}")
            
            print(f"使用数据库文件: {self.db_path}")
            
            # 连接数据库
            conn = sqlite3.connect(self.db_path)
            
            # 构建SQL查询 - 修复列名：roles表和large_equip_desc_data表都使用eid
            base_query = """
                SELECT c.*, l.*
                FROM roles c
                LEFT JOIN large_equip_desc_data l ON c.eid = l.eid
                WHERE c.price > 0
            """
            
            # 添加筛选条件
            conditions = []
            if filters:
                if 'level_min' in filters:
                    conditions.append(f"c.level >= {filters['level_min']}")
                if 'level_max' in filters:
                    conditions.append(f"c.level <= {filters['level_max']}")
                if 'price_min' in filters:
                    conditions.append(f"c.price >= {filters['price_min']}")
                if 'price_max' in filters:
                    conditions.append(f"c.price <= {filters['price_max']}")
                if 'server_name' in filters:
                    conditions.append(f"c.server_name = '{filters['server_name']}'")
                if 'school' in filters:
                    conditions.append(f"c.school = '{filters['school']}'")
            
            if conditions:
                base_query += " AND " + " AND ".join(conditions)
            
            base_query += f" ORDER BY c.price DESC LIMIT {max_records}"
            
            print(f"执行SQL查询...")
            
            # 执行查询
            cursor = conn.cursor()
            cursor.execute(base_query)
            columns = [description[0] for description in cursor.description]
            rows = cursor.fetchall()
            
            print(f"查询完成，获取到 {len(rows)} 条原始数据")
            
            # 处理数据
            market_data = []
            for i, row in enumerate(rows):
                try:
                    role_data = dict(zip(columns, row))
                    
                    # 提取特征
                    features = self.feature_extractor.extract_features(role_data)
                    
                    # 添加基本信息 - 使用eid而不是eid
                    features.update({
                        'eid': role_data.get('eid', ''),  # 修复：使用eid
                        'price': role_data.get('price', 0)
                    })
                    
                    # 计算派生特征
                    # features = self._calculate_derived_features(features)
                    
                    market_data.append(features)
                    
                    if (i + 1) % 100 == 0 or i == len(rows) - 1:
                        print(f"已处理 {i + 1}/{len(rows)} 条数据")
                        
                except Exception as e:
                    self.logger.warning(f"处理第 {i+1} 条数据时出错: {e}")
                    continue
            
            # 转换为DataFrame
            self.market_data = pd.DataFrame(market_data)
            
            if not self.market_data.empty:
                self.market_data.set_index('eid', inplace=True)
                print(f"市场数据刷新完成，共 {len(self.market_data)} 条有效数据")
                print(f"数据特征维度: {len(self.market_data.columns)}")
                print(f"价格范围: {self.market_data['price'].min():.1f} - {self.market_data['price'].max():.1f}")
            else:
                print("警告：未获取到有效的市场数据")
            
            conn.close()
            return self.market_data
            
        except Exception as e:
            self.logger.error(f"刷新市场数据失败: {e}")
            raise
    

    
    def get_market_data(self) -> pd.DataFrame:
        """
        获取当前的市场数据
        
        Returns:
            pd.DataFrame: 市场数据
        """
        if self.market_data.empty:
            print("市场数据为空，正在刷新...")
            self.refresh_market_data()
        
        return self.market_data
    
    
    def filter_market_data(self, 
                          level_range: Optional[tuple] = None,
                          price_range: Optional[tuple] = None,
                          school: Optional[str] = None,
                          server: Optional[str] = None) -> pd.DataFrame:
        """
        筛选市场数据
        
        Args:
            level_range: 等级范围 (min, max)
            price_range: 价格范围 (min, max)  
            school: 门派
            server: 服务器
            
        Returns:
            pd.DataFrame: 筛选后的数据
        """
        df = self.get_market_data().copy()
        
        if level_range:
            df = df[(df['level'] >= level_range[0]) & (df['level'] <= level_range[1])]
        
        if price_range:
            df = df[(df['price'] >= price_range[0]) & (df['price'] <= price_range[1])]
        
        if school:
            df = df[df['school_desc'] == school]
        
        if server:
            df = df[df['server_name'] == server]
        
        return df
    
    def get_market_data_for_similarity(self, 
                                      filters: Optional[Dict[str, Any]] = None) -> pd.DataFrame:
        """
        获取用于相似度计算的市场数据
        
        Args:
            filters: 预过滤条件，用于减少计算量
            
        Returns:
            pd.DataFrame: 市场数据
        """
        self.logger.info(f"[GET_SIMILARITY_DATA] 开始获取相似度计算数据，filters: {filters}")
        
        market_data = self.get_market_data()
        
        self.logger.info(f"[GET_SIMILARITY_DATA] 原始市场数据大小: {len(market_data)}")
        
        if market_data.empty:
            self.logger.warning("[GET_SIMILARITY_DATA] 市场数据为空")
            return market_data
        
        # 应用预过滤条件以提高效率
        if filters:
            self.logger.info(f"[GET_SIMILARITY_DATA] 应用预过滤条件: {filters}")
            filtered_data = market_data.copy()
            
            # 等级过滤
            if 'level_range' in filters and filters['level_range'] is not None:
                level_range = filters['level_range']
                self.logger.debug(f"[GET_SIMILARITY_DATA] 等级过滤：level_range={level_range}, 类型={type(level_range)}")
                if isinstance(level_range, (tuple, list)) and len(level_range) == 2:
                    self.logger.debug(f"[GET_SIMILARITY_DATA] 开始解包等级范围...")
                    level_min, level_max = level_range
                    self.logger.debug(f"[GET_SIMILARITY_DATA] 等级范围解包成功: {level_min} - {level_max}")
                    filtered_data = filtered_data[
                        (filtered_data['level'] >= level_min) & 
                        (filtered_data['level'] <= level_max)
                    ]
            
            # 总修炼等级过滤
            if 'total_cultivation_range' in filters and filters['total_cultivation_range'] is not None:
                cultivation_range = filters['total_cultivation_range']
                self.logger.debug(f"[GET_SIMILARITY_DATA] 修炼过滤：cultivation_range={cultivation_range}, 类型={type(cultivation_range)}")
                if isinstance(cultivation_range, (tuple, list)) and len(cultivation_range) == 2:
                    self.logger.debug(f"[GET_SIMILARITY_DATA] 开始解包修炼范围...")
                    cult_min, cult_max = cultivation_range
                    self.logger.debug(f"[GET_SIMILARITY_DATA] 修炼范围解包成功: {cult_min} - {cult_max}")
                    filtered_data = filtered_data[
                        (filtered_data['total_cultivation'] >= cult_min) & 
                        (filtered_data['total_cultivation'] <= cult_max)
                    ]
            
            # 召唤兽控制力总和过滤
            if 'total_beast_cultivation_range' in filters and filters['total_beast_cultivation_range'] is not None:
                beast_range = filters['total_beast_cultivation_range']
                if isinstance(beast_range, (tuple, list)) and len(beast_range) == 2:
                    beast_min, beast_max = beast_range
                    filtered_data = filtered_data[
                        (filtered_data['total_beast_cultivation'] >= beast_min) & 
                        (filtered_data['total_beast_cultivation'] <= beast_max)
                    ]
            
            # 师门技能平均值过滤
            if 'avg_school_skills_range' in filters and filters['avg_school_skills_range'] is not None:
                skills_range = filters['avg_school_skills_range']
                if isinstance(skills_range, (tuple, list)) and len(skills_range) == 2:
                    skills_min, skills_max = skills_range
                    filtered_data = filtered_data[
                        (filtered_data['avg_school_skills'] >= skills_min) & 
                        (filtered_data['avg_school_skills'] <= skills_max)
                    ]
            
            # 价格过滤
            if 'price_range' in filters and filters['price_range'] is not None:
                price_range = filters['price_range']
                if isinstance(price_range, (tuple, list)) and len(price_range) == 2:
                    price_min, price_max = price_range
                    filtered_data = filtered_data[
                        (filtered_data['price'] >= price_min) & 
                        (filtered_data['price'] <= price_max)
                    ]
            
            # 其他范围过滤条件（通用处理）
            range_keys = ['total_cultivation_range', 'total_beast_cultivation_range', 
                         'avg_school_skills_range', 'level_range', 'price_range']
            for key, value in filters.items():
                if key not in range_keys and key in filtered_data.columns:
                    if isinstance(value, (list, tuple)) and len(value) == 2:
                        # 范围过滤
                        filtered_data = filtered_data[
                            (filtered_data[key] >= value[0]) & 
                            (filtered_data[key] <= value[1])
                        ]
                    else:
                        # 精确匹配
                        filtered_data = filtered_data[filtered_data[key] == value]
            
            return filtered_data
        
        return market_data