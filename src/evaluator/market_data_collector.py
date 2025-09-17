import sys
import os
import threading

# 添加项目根目录到Python路径，解决模块导入问题
from src.utils.project_path import get_project_root
project_root = get_project_root()
sys.path.insert(0, project_root)

import pandas as pd
import numpy as np
import json
import logging
from typing import Dict, Any, List, Optional, Union
from datetime import datetime, timedelta

try:
    from .feature_extractor.feature_extractor import FeatureExtractor
except ImportError:
    from src.evaluator.feature_extractor.feature_extractor import FeatureExtractor


class MarketDataCollector:
    """市场数据采集器 - 从MySQL数据库获取空角色数据作为锚点，支持单例模式的数据缓存共享"""
    
    _instance = None  # 单例实例
    _lock = threading.Lock()  # 线程锁，确保线程安全
    
    def __new__(cls):
        """单例模式实现"""
        with cls._lock:
            if cls._instance is None:
                instance = super(MarketDataCollector, cls).__new__(cls)
                cls._instance = instance
                # 标记实例是否已初始化，避免重复初始化
                instance._initialized = False
                print("创建新的 MarketDataCollector 单例实例")
            else:
                print("使用现有的 MarketDataCollector 单例实例")
            
            return cls._instance
    
    def __init__(self):
        """初始化市场数据采集器（单例模式下只初始化一次）"""
        # 避免重复初始化
        if hasattr(self, '_initialized') and self._initialized:
            return
        
        self.logger = logging.getLogger(__name__)
        self.feature_extractor = FeatureExtractor()
        self.market_data = pd.DataFrame()
        
        # 数据缓存相关属性
        self._data_loaded = False
        self._last_refresh_time = None
        self._cache_expiry_hours = 2  # 缓存过期时间（小时）
        
        self._initialized = True
        print("市场数据采集器单例初始化完成，默认获取空角色数据作为锚点")
    
    
    def refresh_market_data(self, 
                       filters: Optional[Dict[str, Any]] = None,
                       max_records: int = 9999) -> pd.DataFrame:
        """
        刷新市场数据 - 从MySQL获取role_type为'empty'的数据
        
        Args:
            filters: 筛选条件字典，例如 {'level_min': 109, 'price_max': 10000}
            max_records: 最大记录数
            
        Returns:
            pd.DataFrame: 处理后的市场数据
        """
        try:
            print(f"开始刷新市场数据，最大记录数: {max_records}")
            
            # 导入MySQL连接相关模块
            from sqlalchemy import create_engine, text
            from app import create_app
            
            # 创建Flask应用上下文获取数据库配置
            app = create_app()
            
            with app.app_context():
                # 获取数据库配置
                db_config = app.config.get('SQLALCHEMY_DATABASE_URI')
                if not db_config:
                    raise ValueError("未找到数据库配置")
                
                print(f"连接MySQL数据库: {db_config}")
                
                # 创建数据库连接
                engine = create_engine(db_config)
                
                # 构建SQL查询 - 获取空角色数据作为锚点
                base_query = """
                    SELECT 
                        c.eid, c.serverid, c.level, c.school,
                        c.price, c.collect_num, c.role_type,
                        c.yushoushu_skill, c.school_skills, c.life_skills, c.expire_time,
                        l.sum_exp, l.three_fly_lv, l.all_new_point,
                        l.jiyuan_amount, l.packet_page, l.xianyu_amount, l.learn_cash,
                        l.sum_amount, l.role_icon,
                        l.expt_ski1, l.expt_ski2, l.expt_ski3, l.expt_ski4, l.expt_ski5,
                        l.beast_ski1, l.beast_ski2, l.beast_ski3, l.beast_ski4,
                        l.changesch_json, l.ex_avt_json, l.huge_horse_json, l.shenqi_json,
                        l.all_equip_json, l.all_summon_json, l.all_rider_json
                    FROM roles c
                    LEFT JOIN large_equip_desc_data l ON c.eid = l.eid
                    WHERE c.role_type = 'empty' AND c.price > 0
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
                        conditions.append(f"c.school = {filters['school']}")
                    if 'serverid' in filters:
                        conditions.append(f"c.serverid = {filters['serverid']}")
                
                if conditions:
                    base_query += " AND " + " AND ".join(conditions)
                
                base_query += f" ORDER BY c.price ASC LIMIT {max_records}"
                
                print(f"执行SQL查询...")
                print(f"查询语句: {base_query}")
                
                # 执行查询
                with engine.connect() as conn:
                    result = conn.execute(text(base_query))
                    columns = result.keys()
                    rows = result.fetchall()
                
                print(f"查询完成，获取到 {len(rows)} 条原始数据")
                
                # 处理数据
                market_data = []
                for i, row in enumerate(rows):
                    try:
                        role_data = dict(zip(columns, row))
                        
                        # 提取特征
                        features = self.feature_extractor.extract_features(role_data)
                        
                        # 添加基本信息
                        features.update({
                            'eid': role_data.get('eid', ''),
                            'price': role_data.get('price', 0),
                            'role_type': role_data.get('role_type', 'empty')
                        })
                        
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
                    print(f"角色类型: {self.market_data['role_type'].unique()}")
                else:
                    print("警告：未获取到有效的市场数据")
                
                return self.market_data
                
        except Exception as e:
            self.logger.error(f"刷新市场数据失败: {e}")
            raise
    

    
    def get_market_data(self, force_refresh: bool = False) -> pd.DataFrame:
        """
        获取当前的市场数据，支持智能缓存和过期检查
        
        Args:
            force_refresh: 是否强制刷新数据
            
        Returns:
            pd.DataFrame: 市场数据
        """
        # 检查是否需要刷新数据
        need_refresh = (
            force_refresh or 
            not self._data_loaded or 
            self.market_data.empty or 
            self._is_cache_expired()
        )
        
        if need_refresh:
            if force_refresh:
                print("强制刷新市场数据...")
            elif not self._data_loaded:
                print("首次加载市场数据...")
            elif self.market_data.empty:
                print("市场数据为空，正在刷新...")
            elif self._is_cache_expired():
                print(f"缓存已过期（超过{self._cache_expiry_hours}小时），正在刷新...")
            
            self.refresh_market_data()
            self._data_loaded = True
            self._last_refresh_time = datetime.now()
        else:
            print(f"使用缓存的市场数据，上次刷新时间: {self._last_refresh_time}, "
                  f"数据量: {len(self.market_data)}")
        
        return self.market_data
    
    def _is_cache_expired(self) -> bool:
        """检查缓存是否过期"""
        if not self._last_refresh_time:
            return True
        
        elapsed_time = datetime.now() - self._last_refresh_time
        return elapsed_time > timedelta(hours=self._cache_expiry_hours)
    
    
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
    
    @classmethod
    def clear_cache(cls):
        """清空单例实例的缓存"""
        with cls._lock:
            if cls._instance and hasattr(cls._instance, 'market_data'):
                cls._instance.market_data = pd.DataFrame()
                cls._instance._data_loaded = False
                cls._instance._last_refresh_time = None
                print("已清空市场数据缓存")
    
    @classmethod
    def get_cache_status(cls) -> Dict[str, Any]:
        """获取单例实例的缓存状态"""
        with cls._lock:
            if cls._instance:
                return {
                    'data_loaded': getattr(cls._instance, '_data_loaded', False),
                    'last_refresh_time': getattr(cls._instance, '_last_refresh_time', None),
                    'cache_expired': cls._instance._is_cache_expired() if hasattr(cls._instance, '_is_cache_expired') else True,
                    'data_size': len(cls._instance.market_data) if hasattr(cls._instance, 'market_data') and not cls._instance.market_data.empty else 0,
                    'data_source': 'MySQL (empty roles)'
                }
            else:
                return {
                    'data_loaded': False,
                    'last_refresh_time': None,
                    'cache_expired': True,
                    'data_size': 0,
                    'data_source': 'MySQL (empty roles)'
                }
    
    def clear_instance_cache(self):
        """清空当前实例的缓存"""
        self.market_data = pd.DataFrame()
        self._data_loaded = False
        self._last_refresh_time = None
        print("已清空市场数据缓存")
    
    def set_cache_expiry(self, hours: float):
        """设置缓存过期时间"""
        self._cache_expiry_hours = hours
        print(f"缓存过期时间已设置为 {hours} 小时")
    
    def get_cache_info(self) -> Dict[str, Any]:
        """获取当前实例的缓存信息"""
        return {
            'data_loaded': self._data_loaded,
            'last_refresh_time': self._last_refresh_time,
            'cache_expired': self._is_cache_expired(),
            'data_size': len(self.market_data) if not self.market_data.empty else 0,
            'cache_expiry_hours': self._cache_expiry_hours,
            'data_source': 'MySQL (empty roles)'
        }