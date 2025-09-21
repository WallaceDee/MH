import sys
import os
import threading
import concurrent.futures

# 添加项目根目录到Python路径，解决模块导入问题
from src.utils.project_path import get_project_root
project_root = get_project_root()
sys.path.insert(0, project_root)

import pandas as pd
import numpy as np
import json
import logging
import time
import hashlib
from typing import Dict, Any, List, Optional, Union
from datetime import datetime, timedelta
from flask import current_app

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
        self._cache_expiry_hours = 24  # 缓存过期时间（小时）
        
        # Flask-Caching 缓存实例（延迟初始化）
        self._cache = None
        
        # 进度跟踪相关属性
        self._refresh_status = "idle"  # idle, running, completed, error
        self._refresh_progress = 0  # 0-100
        self._refresh_message = ""
        self._refresh_start_time = None
        self._refresh_total_records = 0
        self._refresh_processed_records = 0
        self._refresh_current_batch = 0
        self._refresh_total_batches = 0
        
        self._initialized = True
        print("市场数据采集器单例初始化完成，默认获取空角色数据作为锚点")
    
    def _get_cache(self):
        """获取Flask-Caching实例"""
        if self._cache is None:
            try:
                # 获取当前应用的缓存实例
                from flask_caching import Cache
                
                # 检查是否在应用上下文中
                if current_app:
                    # 从应用扩展中获取缓存实例
                    extensions = getattr(current_app, 'extensions', {})
                    
                    # 查找Cache实例
                    cache_instance = None
                    for ext_name, ext_instance in extensions.items():
                        if isinstance(ext_instance, Cache):
                            cache_instance = ext_instance
                            self.logger.info("成功获取Flask-Caching实例")
                            break
                    
                    if cache_instance is None:
                        # 如果没有找到，尝试从应用中直接获取
                        if hasattr(current_app, 'cache'):
                            cache_instance = current_app.cache
                            self.logger.info("从应用属性获取Flask-Caching实例")
                        else:
                            # 创建新的实例
                            cache_instance = Cache()
                            cache_instance.init_app(current_app)
                            self.logger.info("创建新的Flask-Caching实例")
                    
                    self._cache = cache_instance
                        
                else:
                    self.logger.warning("未在Flask应用上下文中，无法使用缓存")
                    
            except Exception as e:
                self.logger.warning(f"获取Flask-Caching实例失败: {e}")
                self._cache = None
                
        return self._cache
    
    def _generate_cache_key(self, filters: Optional[Dict[str, Any]] = None, max_records: int = 9999) -> str:
        """
        生成缓存键 - 只基于筛选条件，不包含max_records
        这样可以让不同的max_records值复用同一个缓存
        """
        # 创建唯一的缓存键，只基于筛选条件
        cache_data = {
            'filters': filters or {},
            'version': '1.0'  # 版本号，用于缓存失效
        }
        
        # 生成哈希
        cache_str = json.dumps(cache_data, sort_keys=True, ensure_ascii=False)
        cache_hash = hashlib.md5(cache_str.encode('utf-8')).hexdigest()[:16]
        
        return f"market_data:{cache_hash}"
    
    def _get_cached_data(self, filters: Optional[Dict[str, Any]] = None, max_records: int = 9999) -> Optional[pd.DataFrame]:
        """从Flask-Caching获取市场数据，支持智能截取"""
        cache = self._get_cache()
        if not cache:
            return None
        
        try:
            cache_key = self._generate_cache_key(filters, max_records)
            cached_data = cache.get(cache_key)
            
            if cached_data is not None:
                df = None
                
                # 从JSON格式还原DataFrame
                if isinstance(cached_data, dict) and 'data' in cached_data:
                    df = pd.DataFrame(cached_data['data'])
                    # 如果有索引信息，设置索引
                    if 'index' in cached_data and cached_data['index'] and len(df) > 0:
                        if cached_data['index'] in df.columns:
                            df.set_index(cached_data['index'], inplace=True)
                elif isinstance(cached_data, pd.DataFrame):
                    # 直接是DataFrame（向后兼容）
                    df = cached_data
                else:
                    # 其他格式，尝试转换
                    self.logger.warning(f"从Flask-Caching获取到未知格式数据: {type(cached_data)}")
                    return None
                
                if df is not None:
                    # 智能截取：如果缓存数据量大于请求量，截取前N条
                    original_len = len(df)
                    if original_len > max_records:
                        df = df.head(max_records)
                        self.logger.info(f"从Flask-Caching获取市场数据并截取，原始: {original_len} 条，截取: {len(df)} 条")
                    else:
                        self.logger.info(f"从Flask-Caching获取市场数据，数据量: {len(df)} 条（满足请求量 {max_records}）")
                    
                    return df
                    
        except Exception as e:
            self.logger.warning(f"从Flask-Caching获取数据失败: {e}")
        
        return None
    
    def _set_cached_data(self, filters: Optional[Dict[str, Any]], max_records: int, data: pd.DataFrame) -> bool:
        """
        设置Flask-Caching缓存数据
        智能缓存策略：优先缓存更大的数据集，以便后续不同max_records的请求都能复用
        """
        cache = self._get_cache()
        if not cache:
            self.logger.warning("缓存实例不可用")
            return False
            
        if data.empty:
            self.logger.warning("数据为空，不进行缓存")
            return False
        
        try:
            cache_key = self._generate_cache_key(filters, max_records)
            
            # 检查是否已有缓存
            existing_cached = cache.get(cache_key)
            if existing_cached and isinstance(existing_cached, dict):
                existing_count = existing_cached.get('record_count', 0)
                current_count = len(data)
                
                # 如果当前数据量小于或等于已缓存的数据量，不更新缓存
                if current_count <= existing_count:
                    self.logger.info(f"跳过缓存更新，当前数据量 {current_count} <= 已缓存数据量 {existing_count}")
                    return True
                else:
                    self.logger.info(f"更新缓存，当前数据量 {current_count} > 已缓存数据量 {existing_count}")
            
            # 将DataFrame转换为可序列化的格式
            cache_data = {
                'data': data.reset_index().to_dict(orient='records'),
                'index': data.index.name if hasattr(data.index, 'name') and data.index.name else 'eid',
                'cached_at': datetime.now().isoformat(),
                'record_count': len(data),
                'max_records_used': max_records  # 记录用于生成此缓存的max_records，用于调试
            }
            
            # 设置缓存，使用6小时TTL
            result = cache.set(cache_key, cache_data, timeout=6*3600)
            
            # Flask-Caching 的 set 方法返回 True/False 或 None
            if result is True:
                self.logger.info(f"市场数据已缓存到Flask-Caching，数据量: {len(data)}，支持max_records <= {len(data)}")
                return True
            elif result is False:
                self.logger.warning("Flask-Caching.set() 返回False")
                return False
            elif result is None:
                # 有些缓存后端返回None表示成功
                self.logger.info(f"市场数据已缓存到Flask-Caching（返回None），数据量: {len(data)}，支持max_records <= {len(data)}")
                return True
            else:
                self.logger.warning(f"Flask-Caching.set() 返回未预期值: {result}")
                return False
            
        except Exception as e:
            self.logger.warning(f"设置Flask-Caching失败: {str(e)}")
            return False
    
    
    def refresh_market_data(self, 
                       filters: Optional[Dict[str, Any]] = None,
                       max_records: int = 99999,
                       use_cache: bool = True,
                       force_refresh: bool = False,
                       batch_size: int = 2000) -> pd.DataFrame:
        """
        刷新市场数据 - 优先从Redis全量缓存获取，支持筛选、分页和详细进度跟踪
        
        Args:
            filters: 筛选条件字典，例如 {'level_min': 109, 'price_max': 10000}
            max_records: 最大记录数
            use_cache: 是否使用缓存
            force_refresh: 是否强制刷新全量缓存
            batch_size: 批次大小（仅在从数据库加载时使用）
            
        Returns:
            pd.DataFrame: 处理后的市场数据
        """
        try:
            start_time = time.time()
            
            # 初始化进度状态
            self._refresh_status = "running"
            self._refresh_progress = 0
            self._refresh_message = "准备开始..."
            self._refresh_start_time = datetime.now()
            self._refresh_processed_records = 0
            self._refresh_current_batch = 0
            self._refresh_total_batches = 0
            self._refresh_total_records = 0
            
            # 如果使用缓存且不强制刷新，尝试从Redis全量缓存获取
            if use_cache and not force_refresh:
                self._refresh_message = "检查Redis缓存..."
                self._refresh_progress = 5
                
                cached_data = self._get_full_cached_data()
                if cached_data is not None and not cached_data.empty:
                    self._refresh_message = "从缓存筛选数据..."
                    self._refresh_progress = 30
                    
                    # 应用筛选条件
                    filtered_data = self._apply_filters(cached_data, filters, max_records)
                    
                    self.market_data = filtered_data
                    self._data_loaded = True
                    self._last_refresh_time = datetime.now()
                    
                    # 更新进度状态 - 缓存命中完成
                    self._refresh_status = "completed"
                    self._refresh_progress = 100
                    self._refresh_message = "从缓存获取完成！"
                    self._refresh_processed_records = len(filtered_data)
                    self._refresh_total_records = len(filtered_data)
                    
                    elapsed_time = time.time() - start_time
                    print(f"从Redis全量缓存获取市场数据成功，耗时: {elapsed_time:.2f}秒")
                    print(f"全量缓存数据: {len(cached_data)} 条，筛选后: {len(filtered_data)} 条")
                    print(f"特征维度: {len(filtered_data.columns)}")
                    if not filtered_data.empty:
                        print(f"价格范围: {filtered_data['price'].min():.1f} - {filtered_data['price'].max():.1f}")
                    
                    return self.market_data
                else:
                    print("Redis全量缓存未命中或已过期，将从MySQL重新加载全量数据")
                    self._refresh_message = "缓存未命中，准备从数据库加载..."
                    self._refresh_progress = 10
            
            self._refresh_message = "开始从数据库加载全量数据..."
            print(f"开始从数据库加载全量市场数据到Redis缓存")
            
            # 导入MySQL连接相关模块
            from sqlalchemy import create_engine, text
            from src.app import create_app
            
            # 创建Flask应用上下文获取数据库配置
            app = create_app()
            
            with app.app_context():
                # 获取数据库配置
                db_config = app.config.get('SQLALCHEMY_DATABASE_URI')
                if not db_config:
                    raise ValueError("未找到数据库配置")
                
                self._refresh_message = "连接数据库..."
                self._refresh_progress = 15
                print(f"连接MySQL数据库: {db_config}")
                
                # 创建优化的数据库连接 - 使用连接池
                connection_config = self._get_optimized_connection_config(db_config)
                engine = create_engine(db_config, **connection_config)
                
                # 输出数据库索引优化建议
                self._optimize_database_indexes()
                
                # 优化的分批查询策略 - 避免一次性加载所有数据
                self._refresh_message = "分析数据量..."
                self._refresh_progress = 20
                print(f"开始优化的分批全量查询...")
                
                # 首先获取总记录数
                count_query = """
                    SELECT COUNT(*) as total_count
                    FROM roles c
                    WHERE c.role_type = 'empty' AND c.price > 0
                """
                
                with engine.connect() as conn:
                    count_result = conn.execute(text(count_query))
                    total_count = count_result.fetchone()[0]
                
                print(f"总记录数: {total_count}")
                
                # 动态调整批次大小（如果没有传入batch_size参数）
                if batch_size == 2000:  # 使用默认值时才自动调整
                    if total_count > 50000:
                        batch_size = 5000  # 大数据集使用较大批次
                    elif total_count > 20000:
                        batch_size = 2000  # 中等数据集
                    else:
                        batch_size = 1000  # 小数据集
                
                total_batches = (total_count + batch_size - 1) // batch_size
                
                # 更新进度跟踪信息
                self._refresh_total_records = total_count
                self._refresh_total_batches = total_batches
                self._refresh_message = f"开始分批处理，共 {total_batches} 批..."
                self._refresh_progress = 25
                
                print(f"将分 {total_batches} 批处理，每批 {batch_size} 条")
                
                # 优化的SQL查询 - 只选择必要字段，减少数据传输
                base_query = """
                    SELECT 
                        c.eid, c.serverid, c.level, c.school, c.price, c.collect_num,
                        c.yushoushu_skill, c.school_skills, c.life_skills,
                        l.sum_exp, l.three_fly_lv, l.all_new_point, l.jiyuan_amount, 
                        l.packet_page, l.xianyu_amount, l.sum_amount,
                        l.expt_ski1, l.expt_ski2, l.expt_ski3, l.expt_ski4, l.expt_ski5,
                        l.beast_ski1, l.beast_ski2, l.beast_ski3, l.beast_ski4,
                        l.changesch_json, l.ex_avt_json, l.huge_horse_json, l.shenqi_json,
                        l.all_equip_json, l.all_summon_json, l.all_rider_json
                    FROM roles c
                    LEFT JOIN large_equip_desc_data l ON c.eid = l.eid
                    WHERE c.role_type = 'empty' AND c.price > 0
                    ORDER BY c.price ASC
                    LIMIT {batch_size} OFFSET {offset}
                """
                
                # 分批处理数据
                full_market_data = []
                processed_count = 0
                
                with engine.connect() as conn:
                    for batch_num in range(total_batches):
                        # 更新当前批次
                        self._refresh_current_batch = batch_num + 1
                        offset = batch_num * batch_size
                        current_batch_query = base_query.format(batch_size=batch_size, offset=offset)
                        
                        # 更新进度消息
                        self._refresh_message = f"处理第 {batch_num + 1}/{total_batches} 批数据..."
                        
                        # 计算进度（25% 已用于前期准备，剩余75%用于数据处理）
                        batch_progress = 25 + (batch_num / total_batches) * 70  # 70%用于数据处理，5%留给最后的缓存
                        self._refresh_progress = int(batch_progress)
                        
                        print(f"处理第 {batch_num + 1}/{total_batches} 批，偏移量: {offset}")
                        
                        try:
                            # 执行批次查询
                            batch_result = conn.execute(text(current_batch_query))
                            batch_columns = batch_result.keys()
                            batch_rows = batch_result.fetchall()
                            
                            if not batch_rows:
                                print(f"第 {batch_num + 1} 批无数据，跳过")
                                continue
                            
                            # 使用并行处理当前批次的数据
                            batch_data = self._process_batch_data_parallel(batch_rows, batch_columns, batch_num + 1)
                            full_market_data.extend(batch_data)
                            
                            processed_count += len(batch_data)
                            self._refresh_processed_records = processed_count
                            
                            progress_percent = (processed_count / total_count) * 100
                            print(f"已处理 {processed_count}/{total_count} 条数据 ({progress_percent:.1f}%)")
                            
                            # 每处理几批就强制垃圾回收，释放内存
                            if batch_num % 5 == 0:
                                import gc
                                gc.collect()
                                
                        except Exception as e:
                            self.logger.error(f"处理第 {batch_num + 1} 批数据失败: {e}")
                            continue
                
                # 转换为DataFrame
                self._refresh_message = "处理数据格式..."
                self._refresh_progress = 95
                full_data_df = pd.DataFrame(full_market_data)
                
                if not full_data_df.empty:
                    full_data_df.set_index('eid', inplace=True)
                    
                    elapsed_time = time.time() - start_time
                    print(f"全量市场数据加载完成，共 {len(full_data_df)} 条有效数据，耗时: {elapsed_time:.2f}秒")
                    print(f"数据特征维度: {len(full_data_df.columns)}")
                    print(f"价格范围: {full_data_df['price'].min():.1f} - {full_data_df['price'].max():.1f}")
                    
                    # 缓存全量数据到Redis
                    if use_cache:
                        self._refresh_message = "缓存数据到Redis..."
                        cache_start = time.time()
                        if self._set_full_cached_data(full_data_df):
                            cache_time = time.time() - cache_start
                            print(f"全量数据已缓存到Redis，缓存耗时: {cache_time:.2f}秒")
                        else:
                            print("Redis全量缓存设置失败，但数据获取成功")
                    
                    # 应用筛选条件并返回结果
                    self._refresh_message = "应用筛选条件..."
                    filtered_data = self._apply_filters(full_data_df, filters, max_records)
                    self.market_data = filtered_data
                    
                    # 更新缓存状态
                    self._data_loaded = True
                    self._last_refresh_time = datetime.now()
                    
                    # 完成进度跟踪
                    self._refresh_status = "completed"
                    self._refresh_progress = 100
                    self._refresh_message = "数据加载完成！"
                    self._refresh_processed_records = len(filtered_data)
                    self._refresh_total_records = len(filtered_data)
                    
                    print(f"筛选后数据: {len(filtered_data)} 条")
                    
                else:
                    print("警告：未获取到有效的市场数据")
                    self.market_data = pd.DataFrame()
                    
                    # 设置失败状态
                    self._refresh_status = "error"
                    self._refresh_progress = 0
                    self._refresh_message = "未获取到有效数据"
                
                return self.market_data
                
        except Exception as e:
            # 更新错误状态
            self._refresh_status = "error"
            self._refresh_progress = 0
            self._refresh_message = f"刷新失败: {str(e)}"
            
            self.logger.error(f"刷新市场数据失败: {e}")
            raise
    def get_refresh_status(self) -> Dict[str, Any]:
        """
        获取刷新进度状态
        
        Returns:
            Dict: 包含进度信息的字典
        """
        status_info = {
            "status": self._refresh_status,
            "progress": self._refresh_progress,
            "message": self._refresh_message,
            "processed_records": self._refresh_processed_records,
            "total_records": self._refresh_total_records,
            "current_batch": self._refresh_current_batch,
            "total_batches": self._refresh_total_batches,
            "start_time": self._refresh_start_time.isoformat() if self._refresh_start_time else None,
            "elapsed_seconds": (datetime.now() - self._refresh_start_time).total_seconds() if self._refresh_start_time else 0
        }
        return status_info

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
            print("🔄 数据需要刷新，开始刷新市场数据...")
            self.refresh_market_data()
        else:
            print("✅ 使用现有数据，数据仍在有效期内")
        
        return self.market_data

    def _is_cache_expired(self) -> bool:
        """检查缓存是否过期"""
        if not self._last_refresh_time:
            return True
        
        expiry_time = self._last_refresh_time + timedelta(hours=self._cache_expiry_hours)
        return datetime.now() > expiry_time
                    
                    elapsed_time = time.time() - start_time
                    print(f"从Flask-Caching缓存获取数据成功，耗时: {elapsed_time:.2f}秒")
                    print(f"缓存数据量: {len(cached_data)} 条，特征维度: {len(cached_data.columns)}")
                    print(f"✅ 智能缓存复用成功！max_records={max_records}")
                    
                    # 检查是否进行了智能截取
                    if 'data' in cached_data.columns and len(cached_data) < max_records:
                        print(f"💡 缓存数据({len(cached_data)}条) < 请求量({max_records}条)，已返回全部缓存数据")
                    
                    return self.market_data
            
            # 初始化进度状态
            self._refresh_status = "running"
            self._refresh_progress = 0
            self._refresh_message = "准备开始..."
            self._refresh_start_time = datetime.now()
            self._refresh_processed_records = 0
            self._refresh_current_batch = 0
            
            print(f"开始分批刷新市场数据，最大记录数: {max_records}，批次大小: {batch_size}")
            
            # 导入MySQL连接相关模块
            from sqlalchemy import create_engine, text
            from src.app import create_app
            
            # 创建Flask应用上下文获取数据库配置
            app = create_app()
            
            with app.app_context():
                # 获取数据库配置
                db_config = app.config.get('SQLALCHEMY_DATABASE_URI')
                if not db_config:
                    raise ValueError("未找到数据库配置")
                
                self._refresh_message = "连接数据库..."
                self._refresh_progress = 5
                print(f"连接MySQL数据库: {db_config}")
                
                # 创建数据库连接
                engine = create_engine(db_config)
                
                # 构建基础SQL查询
                base_query = """
                    SELECT 
                        c.eid, c.serverid, c.level, c.school,
                        c.price, c.collect_num,
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
                
                base_query += " ORDER BY c.price ASC"
                
                # 计算总批次数
                self._refresh_total_batches = (max_records + batch_size - 1) // batch_size
                self._refresh_total_records = max_records
                
                self._refresh_message = f"开始分批处理，共 {self._refresh_total_batches} 批..."
                self._refresh_progress = 10
                
                # 分批处理数据
                market_data = []
                
                with engine.connect() as conn:
                    for batch_num in range(self._refresh_total_batches):
                        # 更新当前批次
                        self._refresh_current_batch = batch_num + 1
                        
                        # 计算当前批次的偏移量和大小
                        offset = batch_num * batch_size
                        current_batch_size = min(batch_size, max_records - offset)
                        
                        if current_batch_size <= 0:
                            break
                        
                        # 分批处理不使用批次级缓存，只在最终缓存完整数据
                        # 这样不同批次大小都可以使用同一个缓存
                        
                        # 构建分页查询
                        paginated_query = f"{base_query} LIMIT {current_batch_size} OFFSET {offset}"
                        
                        self._refresh_message = f"处理第 {batch_num + 1}/{self._refresh_total_batches} 批数据..."
                        
                        try:
                            # 执行查询
                            result = conn.execute(text(paginated_query))
                            if batch_num == 0:  # 第一次获取列名
                                columns = result.keys()
                            rows = result.fetchall()
                            
                            if not rows:
                                print(f"第 {batch_num + 1} 批查询无数据，停止处理")
                                break
                            
                            print(f"第 {batch_num + 1} 批获取到 {len(rows)} 条原始数据")
                            
                            # 处理当前批次数据
                            batch_data = []
                            for i, row in enumerate(rows):
                                try:
                                    role_data = dict(zip(columns, row))
                                    
                                    # 提取特征
                                    features = self.feature_extractor.extract_features(role_data)
                                    
                                    # 添加基本信息
                                    features.update({
                                        'eid': role_data.get('eid', ''),
                                        'price': role_data.get('price', 0),
                                        'school': role_data.get('school', 0),
                                        'serverid': role_data.get('serverid', 0)
                                    })
                                    
                                    batch_data.append(features)
                                    self._refresh_processed_records += 1
                                    
                                except Exception as e:
                                    self.logger.warning(f"批次 {batch_num + 1} 第 {i+1} 条数据处理失败: {e}")
                                    continue
                            
                            market_data.extend(batch_data)
                            
                            # 不进行批次级缓存，只在最终缓存完整数据
                            # 这样任何批次大小都可以使用相同的缓存
                            
                            # 更新进度
                            batch_progress = 10 + (batch_num + 1) / self._refresh_total_batches * 80
                            self._refresh_progress = min(90, int(batch_progress))
                            
                            print(f"批次 {batch_num + 1} 处理完成，有效数据: {len(batch_data)} 条，总计: {len(market_data)} 条")
                            
                            # 批次间短暂休息
                            if batch_num < self._refresh_total_batches - 1:
                                time.sleep(0.05)  # 50ms休息，减少等待时间
                                
                        except Exception as e:
                            self.logger.error(f"第 {batch_num + 1} 批处理失败: {e}")
                            break
                
                # 构建最终DataFrame
                self._refresh_message = "构建数据索引..."
                self._refresh_progress = 95
                
                self.market_data = pd.DataFrame(market_data)
                
                if not self.market_data.empty:
                    self.market_data.set_index('eid', inplace=True)
                    
                    # 更新缓存状态
                    self._data_loaded = True
                    self._last_refresh_time = datetime.now()
                    
                    self._refresh_message = "刷新完成！"
                    self._refresh_progress = 100
                    self._refresh_status = "completed"
                    
                    elapsed_time = time.time() - start_time
                    print(f"市场数据分批刷新完成，共 {len(self.market_data)} 条有效数据，总耗时: {elapsed_time:.2f}秒")
                    print(f"数据特征维度: {len(self.market_data.columns)}")
                    print(f"价格范围: {self.market_data['price'].min():.1f} - {self.market_data['price'].max():.1f}")
                    
                    # 缓存完整数据到Flask-Caching（基于筛选条件和记录数）
                    if use_cache:
                        cache_start = time.time()
                        if self._set_cached_data(filters, max_records, self.market_data):
                            cache_time = time.time() - cache_start
                            print(f"完整数据已缓存到Flask-Caching，缓存耗时: {cache_time:.2f}秒")
                            print(f"✅ 此缓存可被任何批次大小复用！")
                        else:
                            print("Flask-Caching设置失败，但数据获取成功")
                    
                else:
                    self._refresh_message = "未获取到有效数据"
                    self._refresh_status = "completed"
                    print("警告：未获取到有效的市场数据")
                
                return self.market_data
                
        except Exception as e:
            self._refresh_status = "error"
            self._refresh_message = f"刷新失败: {str(e)}"
            self._refresh_progress = 0
            self.logger.error(f"分批刷新市场数据失败: {e}")
            raise
    
    def get_refresh_status(self) -> Dict[str, Any]:
        """
        获取刷新进度状态
        
        Returns:
            Dict: 包含进度信息的字典
        """
        status_info = {
            "status": self._refresh_status,
            "progress": self._refresh_progress,
            "message": self._refresh_message,
            "processed_records": self._refresh_processed_records,
            "total_records": self._refresh_total_records,
            "current_batch": self._refresh_current_batch,
            "total_batches": self._refresh_total_batches,
            "start_time": self._refresh_start_time.isoformat() if self._refresh_start_time else None,
            "elapsed_seconds": int((datetime.now() - self._refresh_start_time).total_seconds()) if self._refresh_start_time else 0
        }
        
        return status_info
    
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
        """获取当前实例的缓存信息（包括Flask-Caching信息）"""
        info = {
            'data_loaded': self._data_loaded,
            'last_refresh_time': self._last_refresh_time,
            'cache_expired': self._is_cache_expired(),
            'data_size': len(self.market_data) if not self.market_data.empty else 0,
            'cache_expiry_hours': self._cache_expiry_hours,
            'data_source': 'MySQL (empty roles)',
            'cache_available': False,
            'cache_type': None,
            'cache_config': {}
        }
        
        # 添加Flask-Caching信息
        cache = self._get_cache()
        if cache:
            info['cache_available'] = True
            try:
                # 获取缓存配置信息
                if hasattr(cache, 'config') and cache.config:
                    cache_config = cache.config
                elif hasattr(current_app, 'config'):
                    cache_config = current_app.config
                else:
                    cache_config = {}
                
                info['cache_type'] = cache_config.get('CACHE_TYPE', 'Unknown')
                info['cache_config'] = {
                    'cache_type': cache_config.get('CACHE_TYPE'),
                    'default_timeout': cache_config.get('CACHE_DEFAULT_TIMEOUT'),
                    'key_prefix': cache_config.get('CACHE_KEY_PREFIX'),
                }
                
                # 如果是Redis缓存，添加Redis特定信息
                if info['cache_type'] == 'RedisCache':
                    info['cache_config'].update({
                        'redis_host': cache_config.get('CACHE_REDIS_HOST'),
                        'redis_port': cache_config.get('CACHE_REDIS_PORT'),
                        'redis_db': cache_config.get('CACHE_REDIS_DB')
                    })
                        
            except Exception as e:
                info['cache_error'] = str(e)
        
        return info

    def _get_full_cached_data(self) -> Optional[pd.DataFrame]:
        """从Redis获取全量缓存数据 - 支持分块存储"""
        try:
            from src.utils.redis_cache import get_redis_cache
            redis_cache = get_redis_cache()
            
            if not redis_cache or not redis_cache.is_available():
                print("Redis不可用，尝试备用方案")
                return self._fallback_get_full_cached_data()
            
            # 使用固定的全量缓存键
            full_cache_key = "market_data_full_empty_roles"
            
            print("尝试从Redis分块缓存获取全量数据...")
            
            # 尝试获取分块数据
            cached_data = redis_cache.get_chunked_data(full_cache_key)
            
            if cached_data is not None and not cached_data.empty:
                print(f"从Redis分块缓存获取数据成功: {len(cached_data)} 条")
                return cached_data
            else:
                print("Redis分块缓存未命中，尝试备用方案")
                return self._fallback_get_full_cached_data()
                
        except Exception as e:
            self.logger.warning(f"获取Redis分块缓存失败: {str(e)}")
            print("获取分块缓存失败，尝试备用方案")
            return self._fallback_get_full_cached_data()

    def _fallback_get_full_cached_data(self) -> Optional[pd.DataFrame]:
        """备用获取缓存方案 - 使用SharedCacheManager"""
        try:
            from src.utils.shared_cache_manager import get_shared_cache_manager
            cache_manager = get_shared_cache_manager()
            
            if not cache_manager.is_available():
                return None
            
            # 使用固定的全量缓存键
            full_cache_key = "market_data_full_empty_roles"
            cached_data = cache_manager.get_role_cache(full_cache_key)
            
            if cached_data is not None:
                print(f"从Redis全量缓存获取数据（备用方案）: {len(cached_data)} 条")
                return cached_data
            else:
                print("Redis全量缓存未命中")
                return None
                
        except Exception as e:
            self.logger.warning(f"备用获取缓存方案失败: {str(e)}")
            return None

    def _set_full_cached_data(self, data: pd.DataFrame) -> bool:
        """将全量数据缓存到Redis - 使用分块存储和Pipeline优化"""
        try:
            from src.utils.redis_cache import get_redis_cache
            redis_cache = get_redis_cache()
            
            if not redis_cache or not redis_cache.is_available():
                print("Redis不可用，尝试使用SharedCacheManager")
                return self._fallback_set_full_cached_data(data)
            
            # 使用固定的全量缓存键
            full_cache_key = "market_data_full_empty_roles"
            
            # 设置较长的缓存时间（24小时）
            cache_hours = 24
            ttl_seconds = cache_hours * 3600
            
            print(f"开始使用分块存储全量数据: {len(data)} 条记录")
            
            # 根据数据大小动态调整块大小
            if len(data) > 10000:
                chunk_size = 2000  # 大数据集使用较大的块
            elif len(data) > 5000:
                chunk_size = 1000  # 中等数据集
            else:
                chunk_size = 500   # 小数据集
            
            # 使用分块存储
            success = redis_cache.set_chunked_data(
                base_key=full_cache_key,
                data=data,
                chunk_size=chunk_size,
                ttl=ttl_seconds
            )
            
            if success:
                print(f"全量数据已分块缓存到Redis，缓存时间: {cache_hours}小时，块大小: {chunk_size}")
                return True
            else:
                print("Redis分块缓存设置失败，尝试备用方案")
                return self._fallback_set_full_cached_data(data)
                
        except Exception as e:
            self.logger.warning(f"设置Redis全量缓存失败: {str(e)}")
            print("Redis缓存失败，尝试备用方案")
            return self._fallback_set_full_cached_data(data)

    def _fallback_set_full_cached_data(self, data: pd.DataFrame) -> bool:
        """备用缓存方案 - 使用SharedCacheManager"""
        try:
            from src.utils.shared_cache_manager import get_shared_cache_manager
            cache_manager = get_shared_cache_manager()
            
            if not cache_manager.is_available():
                return False
            
            # 使用固定的全量缓存键
            full_cache_key = "market_data_full_empty_roles"
            
            # 设置较长的缓存时间（24小时）
            cache_hours = 24
            success = cache_manager.set_role_cache(
                cache_key=full_cache_key,
                data=data,
                cache_type='market_analysis',
                ttl_hours=cache_hours
            )
            
            if success:
                print(f"全量数据已缓存到Redis（备用方案），缓存时间: {cache_hours}小时")
                return True
            else:
                print("备用Redis缓存设置也失败")
                return False
                
        except Exception as e:
            self.logger.warning(f"备用缓存方案也失败: {str(e)}")
            return False

    def _apply_filters(self, data: pd.DataFrame, filters: Optional[Dict[str, Any]], max_records: int) -> pd.DataFrame:
        """对数据应用筛选条件"""
        if data.empty:
            return data
        
        try:
            filtered_data = data.copy()
            
            # 应用筛选条件
            if filters:
                if 'level_min' in filters and 'level' in filtered_data.columns:
                    filtered_data = filtered_data[filtered_data['level'] >= filters['level_min']]
                
                if 'level_max' in filters and 'level' in filtered_data.columns:
                    filtered_data = filtered_data[filtered_data['level'] <= filters['level_max']]
                
                if 'price_min' in filters and 'price' in filtered_data.columns:
                    filtered_data = filtered_data[filtered_data['price'] >= filters['price_min']]
                
                if 'price_max' in filters and 'price' in filtered_data.columns:
                    filtered_data = filtered_data[filtered_data['price'] <= filters['price_max']]
                
                if 'school' in filters and 'school' in filtered_data.columns:
                    filtered_data = filtered_data[filtered_data['school'] == filters['school']]
                
                if 'serverid' in filters and 'serverid' in filtered_data.columns:
                    filtered_data = filtered_data[filtered_data['serverid'] == filters['serverid']]
            
            # 应用记录数限制
            if len(filtered_data) > max_records:
                # 按价格排序后取前N条
                if 'price' in filtered_data.columns:
                    filtered_data = filtered_data.sort_values('price').head(max_records)
                else:
                    filtered_data = filtered_data.head(max_records)
            
            return filtered_data
            
        except Exception as e:
            self.logger.warning(f"应用筛选条件失败: {str(e)}")
            return data.head(max_records) if len(data) > max_records else data

    def refresh_full_cache(self) -> bool:
        """
        手动刷新全量缓存 - 从MySQL重新加载所有empty角色数据到Redis
        
        Returns:
            bool: 是否成功刷新缓存
        """
        try:
            print("开始手动刷新全量缓存...")
            
            # 强制从数据库刷新，不使用现有缓存
            self.refresh_market_data(
                filters=None, 
                max_records=999999,  # 设置很大的值以获取全部数据
                use_cache=True,
                force_refresh=True
            )
            
            print("全量缓存刷新完成")
            return True
            
        except Exception as e:
            self.logger.error(f"刷新全量缓存失败: {e}")
            return False

    def get_cache_status(self) -> Dict[str, Any]:
        """
        获取缓存状态信息 - 支持分块缓存
        
        Returns:
            Dict: 缓存状态信息
        """
        try:
            from src.utils.redis_cache import get_redis_cache
            redis_cache = get_redis_cache()
            
            status = {
                'redis_available': False,
                'full_cache_exists': False,
                'full_cache_size': 0,
                'full_cache_last_update': None,
                'cache_type': 'unknown',
                'chunk_info': {}
            }
            
            # 检查Redis连接
            if redis_cache and redis_cache.is_available():
                status['redis_available'] = True
                
                # 检查分块缓存
                full_cache_key = "market_data_full_empty_roles"
                
                # 先检查分块缓存的元数据
                try:
                    metadata = redis_cache.get(f"{full_cache_key}:meta")
                    if metadata:
                        status['full_cache_exists'] = True
                        status['cache_type'] = 'chunked'
                        status['full_cache_size'] = metadata.get('total_rows', 0)
                        status['full_cache_last_update'] = metadata.get('created_at')
                        status['chunk_info'] = {
                            'total_chunks': metadata.get('total_chunks', 0),
                            'chunk_size': metadata.get('chunk_size', 0),
                            'columns_count': len(metadata.get('columns', []))
                        }
                        
                        # 验证所有分块是否完整
                        total_chunks = metadata.get('total_chunks', 0)
                        if total_chunks > 0:
                            chunk_keys = [f"{full_cache_key}:chunk_{i}" for i in range(total_chunks)]
                            existing_chunks = redis_cache.get_batch(chunk_keys)
                            status['chunk_info']['existing_chunks'] = len(existing_chunks)
                            status['chunk_info']['is_complete'] = len(existing_chunks) == total_chunks
                        
                        return status
                except Exception as e:
                    self.logger.debug(f"检查分块缓存元数据失败: {e}")
                
                # 如果分块缓存不存在，检查备用缓存
                try:
                    from src.utils.shared_cache_manager import get_shared_cache_manager
                    cache_manager = get_shared_cache_manager()
                    
                    if cache_manager.is_available():
                        cached_data = cache_manager.get_role_cache(full_cache_key)
                        if cached_data is not None and not cached_data.empty:
                            status['full_cache_exists'] = True
                            status['cache_type'] = 'legacy'
                            status['full_cache_size'] = len(cached_data)
                            
                            # 尝试获取缓存时间信息
                            try:
                                cache_info = cache_manager.redis_cache.client.hgetall(
                                    cache_manager.redis_cache._make_key(f"role_data:{full_cache_key}:meta")
                                )
                                if cache_info and b'timestamp' in cache_info:
                                    status['full_cache_last_update'] = cache_info[b'timestamp'].decode('utf-8')
                            except:
                                pass
                except Exception as e:
                    self.logger.debug(f"检查备用缓存失败: {e}")
            
            return status
            
        except Exception as e:
            self.logger.error(f"获取缓存状态失败: {e}")
            return {
                'redis_available': False,
                'full_cache_exists': False,
                'full_cache_size': 0,
                'full_cache_last_update': None,
                'cache_type': 'error',
                'error': str(e)
            }

    def _process_batch_data(self, batch_rows: List, batch_columns: List, batch_num: int) -> List[Dict]:
        """
        批量处理数据 - 优化特征提取性能
        
        Args:
            batch_rows: 数据库查询结果行
            batch_columns: 列名列表
            batch_num: 批次号
            
        Returns:
            List[Dict]: 处理后的特征数据列表
        """
        try:
            batch_data = []
            
            # 预先转换为字典列表，减少重复操作
            role_data_list = [dict(zip(batch_columns, row)) for row in batch_rows]
            
            # 批量提取特征
            for i, role_data in enumerate(role_data_list):
                try:
                    # 提取特征
                    features = self.feature_extractor.extract_features(role_data)
                    
                    # 添加基本信息
                    features.update({
                        'eid': role_data.get('eid', ''),
                        'price': role_data.get('price', 0),
                        'school': role_data.get('school', 0),
                        'serverid': role_data.get('serverid', 0)
                    })
                    
                    batch_data.append(features)
                    
                except Exception as e:
                    self.logger.warning(f"处理第{batch_num}批第{i+1}条数据时出错: {e}")
                    continue
            
            print(f"第{batch_num}批处理完成: {len(batch_data)}/{len(batch_rows)} 条有效数据")
            return batch_data
            
        except Exception as e:
            self.logger.error(f"批量处理第{batch_num}批数据失败: {e}")
            return []

    def _optimize_database_indexes(self):
        """
        优化数据库索引建议 - 仅输出建议，不执行
        """
        index_suggestions = [
            "CREATE INDEX idx_roles_type_price ON roles(role_type, price);",
            "CREATE INDEX idx_roles_eid ON roles(eid);",
            "CREATE INDEX idx_large_equip_eid ON large_equip_desc_data(eid);",
            "CREATE INDEX idx_roles_level ON roles(level);",
            "CREATE INDEX idx_roles_serverid ON roles(serverid);",
            "CREATE INDEX idx_roles_school ON roles(school);"
        ]
        
        print("🔍 数据库索引优化建议:")
        for suggestion in index_suggestions:
            print(f"  {suggestion}")
        print("📝 请在数据库中手动执行这些索引创建语句以提升查询性能")

    def _get_optimized_connection_config(self, db_config: str) -> Dict:
        """
        获取优化的数据库连接配置
        
        Args:
            db_config: 原始数据库连接字符串
            
        Returns:
            Dict: 优化的连接参数
        """
        return {
            'pool_size': 10,           # 连接池大小
            'max_overflow': 20,        # 最大溢出连接数
            'pool_timeout': 30,        # 获取连接超时时间
            'pool_recycle': 3600,      # 连接回收时间（1小时）
            'pool_pre_ping': True,     # 连接前ping测试
            'echo': False,             # 不打印SQL
            'connect_args': {
                'charset': 'utf8mb4',
                'connect_timeout': 60,
                'read_timeout': 300,
                'write_timeout': 300,
                'autocommit': True
            }
        }

    def _process_batch_data_parallel(self, batch_rows: List, batch_columns: List, batch_num: int, max_workers: int = 4) -> List[Dict]:
        """
        并行批量处理数据 - 使用多线程优化特征提取性能
        
        Args:
            batch_rows: 数据库查询结果行
            batch_columns: 列名列表
            batch_num: 批次号
            max_workers: 最大工作线程数
            
        Returns:
            List[Dict]: 处理后的特征数据列表
        """
        try:
            if len(batch_rows) < 100:
                # 小批次数据直接串行处理，避免线程开销
                return self._process_batch_data(batch_rows, batch_columns, batch_num)
            
            # 预先转换为字典列表
            role_data_list = [dict(zip(batch_columns, row)) for row in batch_rows]
            
            # 分割数据供多线程处理
            chunk_size = max(1, len(role_data_list) // max_workers)
            chunks = [role_data_list[i:i + chunk_size] for i in range(0, len(role_data_list), chunk_size)]
            
            batch_data = []
            
            # 使用线程池并行处理
            with concurrent.futures.ThreadPoolExecutor(max_workers=max_workers) as executor:
                # 提交任务
                future_to_chunk = {
                    executor.submit(self._process_data_chunk, chunk, f"{batch_num}-{i+1}"): i 
                    for i, chunk in enumerate(chunks)
                }
                
                # 收集结果
                for future in concurrent.futures.as_completed(future_to_chunk):
                    chunk_index = future_to_chunk[future]
                    try:
                        chunk_result = future.result()
                        batch_data.extend(chunk_result)
                    except Exception as e:
                        self.logger.error(f"处理第{batch_num}批第{chunk_index+1}块数据失败: {e}")
                        continue
            
            print(f"第{batch_num}批并行处理完成: {len(batch_data)}/{len(batch_rows)} 条有效数据")
            return batch_data
            
        except Exception as e:
            self.logger.error(f"并行处理第{batch_num}批数据失败: {e}")
            # 降级到串行处理
            return self._process_batch_data(batch_rows, batch_columns, batch_num)

    def _process_data_chunk(self, role_data_chunk: List[Dict], chunk_id: str) -> List[Dict]:
        """
        处理数据块 - 线程安全的特征提取
        
        Args:
            role_data_chunk: 角色数据块
            chunk_id: 块标识
            
        Returns:
            List[Dict]: 处理后的特征数据
        """
        try:
            chunk_data = []
            
            for i, role_data in enumerate(role_data_chunk):
                try:
                    # 提取特征
                    features = self.feature_extractor.extract_features(role_data)
                    
                    # 添加基本信息
                    features.update({
                        'eid': role_data.get('eid', ''),
                        'price': role_data.get('price', 0),
                        'school': role_data.get('school', 0),
                        'serverid': role_data.get('serverid', 0)
                    })
                    
                    chunk_data.append(features)
                    
                except Exception as e:
                    self.logger.warning(f"处理块{chunk_id}第{i+1}条数据时出错: {e}")
                    continue
            
            return chunk_data
            
        except Exception as e:
            self.logger.error(f"处理数据块{chunk_id}失败: {e}")
            return []

    def get_performance_stats(self) -> Dict[str, Any]:
        """
        获取性能统计信息
        
        Returns:
            Dict: 性能统计数据
        """
        try:
            stats = {
                'data_loaded': self._data_loaded,
                'last_refresh_time': self._last_refresh_time.isoformat() if self._last_refresh_time else None,
                'data_count': len(self.market_data) if not self.market_data.empty else 0,
                'memory_usage_mb': self.market_data.memory_usage(deep=True).sum() / 1024 / 1024 if not self.market_data.empty else 0,
                'cache_expiry_hours': self._cache_expiry_hours,
                'optimization_suggestions': self._get_optimization_suggestions()
            }
            
            # 添加数据库连接池状态
            try:
                from src.app import create_app
                app = create_app()
                with app.app_context():
                    db_config = app.config.get('SQLALCHEMY_DATABASE_URI')
                    if db_config:
                        stats['database_config'] = {
                            'connection_pool_enabled': True,
                            'suggested_indexes': self._get_index_suggestions()
                        }
            except:
                pass
                
            return stats
            
        except Exception as e:
            self.logger.error(f"获取性能统计失败: {e}")
            return {'error': str(e)}

    def _get_optimization_suggestions(self) -> List[str]:
        """获取优化建议"""
        suggestions = []
        
        if hasattr(self, 'market_data') and not self.market_data.empty:
            data_count = len(self.market_data)
            
            if data_count > 100000:
                suggestions.append("数据量较大，建议使用分块缓存策略")
            
            if data_count > 50000:
                suggestions.append("建议在数据库中创建复合索引以提升查询性能")
                
            memory_mb = self.market_data.memory_usage(deep=True).sum() / 1024 / 1024
            if memory_mb > 500:
                suggestions.append("内存使用较高，建议优化数据类型或使用分批处理")
        
        suggestions.extend([
            "建议在数据库中创建推荐的索引以提升查询性能",
            "使用Redis分块缓存可以显著提升读取速度",
            "并行处理可以加速特征提取过程"
        ])
        
        return suggestions

    def _get_index_suggestions(self) -> List[str]:
        """获取索引建议"""
        return [
            "CREATE INDEX idx_roles_type_price ON roles(role_type, price);",
            "CREATE INDEX idx_roles_eid ON roles(eid);", 
            "CREATE INDEX idx_large_equip_eid ON large_equip_desc_data(eid);",
            "CREATE INDEX idx_roles_level ON roles(level);",
            "CREATE INDEX idx_roles_serverid ON roles(serverid);"
        ]