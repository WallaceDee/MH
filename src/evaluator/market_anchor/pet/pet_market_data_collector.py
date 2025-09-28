import pandas as pd
import logging
from typing import Dict, Any, List, Optional, Tuple, Union
from datetime import datetime

from src.evaluator.feature_extractor.pet_feature_extractor import PetFeatureExtractor
from src.database import db
from src.models.pet import Pet
from sqlalchemy import and_, or_, func, text


class PetMarketDataCollector:
    """宠物市场数据采集器 - 从数据库中获取和处理宠物市场数据"""

    _instance = None  # 单例实例
    _lock = None  # 线程锁，确保线程安全
    
    def __new__(cls):
        """单例模式实现"""
        import threading
        if cls._lock is None:
            cls._lock = threading.Lock()
            
        with cls._lock:
            if cls._instance is None:
                instance = super(PetMarketDataCollector, cls).__new__(cls)
                cls._instance = instance
                # 标记实例是否已初始化，避免重复初始化
                instance._initialized = False
                print("创建新的 PetMarketDataCollector 单例实例")
            else:
                print("使用现有的 PetMarketDataCollector 单例实例")
            
            return cls._instance

    def __init__(self):
        """
        初始化宠物市场数据采集器 - 支持Redis全量缓存（单例模式下只初始化一次）
        """
        # 避免重复初始化
        if hasattr(self, '_initialized') and self._initialized:
            return
            
        self.feature_extractor = PetFeatureExtractor()
        self.logger = logging.getLogger(__name__)

        # 初始化Redis缓存
        try:
            from src.utils.redis_cache import get_redis_cache
            self.redis_cache = get_redis_cache()
            if self.redis_cache and self.redis_cache.is_available():
                self.logger.info("Redis缓存初始化成功，将使用Redis全量缓存模式")
                print("宠物数据采集器初始化，使用Redis全量缓存模式")
            else:
                self.redis_cache = None
                print("宠物数据采集器初始化，Redis不可用，使用MySQL数据库")
        except Exception as e:
            self.logger.warning(f"Redis缓存初始化失败: {e}")
            self.redis_cache = None
            print("宠物数据采集器初始化，Redis初始化失败，使用MySQL数据库")
        
        # 全量缓存相关属性
        self._full_cache_key = "pet_market_data_full"
        self._cache_ttl_hours = -1  # 永不过期，只能手动刷新
        self._full_data_cache = None  # 内存中的全量数据缓存
        
        # 进度跟踪相关属性
        self._refresh_status = "idle"  # idle, running, completed, error
        self._refresh_progress = 0  # 0-100
        self._refresh_message = ""
        self._refresh_start_time = None
        self._refresh_total_records = 0
        self._refresh_processed_records = 0
        self._refresh_current_batch = 0
        self._refresh_total_batches = 0
        
        # MySQL数据统计
        self.mysql_data_count = 0  # MySQL中pets表的总记录数
        
        self._initialized = True
        cache_mode = "永不过期模式" if self._cache_ttl_hours == -1 else f"{self._cache_ttl_hours}小时过期"
        print(f"宠物市场数据采集器单例初始化完成，支持Redis全量缓存（{cache_mode}）")
    
    
    def get_market_data(self,
                        level_range: Optional[Tuple[int, int]] = None,
                        role_grade_limit_range: Optional[Tuple[int, int]] = None,
                        price_range: Optional[Tuple[float, float]] = None,
                        server: Optional[str] = None,
                        all_skill: Optional[Union[str, List[str]]] = None,
                        limit: int = 1000,
                        use_redis_cache: bool = True) -> pd.DataFrame:
        """
        获取市场宠物数据 - 优先从Redis全量缓存获取并筛选

        Args:
            level_range: 等级范围 (min_level, max_level)
            role_grade_limit_range: 携带等级 (min_role_grade_limit, max_role_grade_limit)
            price_range: 价格范围 (min_price, max_price)
            server: 服务器筛选
            all_skill: 技能 使用了管道符拼接的技能字符串以"|"
            limit: 返回数据条数限制
            use_redis_cache: 是否使用Redis缓存

        Returns:
            宠物市场数据DataFrame
        """
        try:
            import time
            start_time = time.time()
            
            # 优先从Redis全量缓存获取数据
            if use_redis_cache and self.redis_cache:
                full_data = self._get_full_data_from_redis()
                
                if full_data is None or full_data.empty:
                    # 缓存未命中，尝试加载全量数据到Redis
                    print("Redis缓存未命中，开始加载全量数据...")
                    if self._load_full_data_to_redis():
                        full_data = self._get_full_data_from_redis()
                
                if full_data is not None and not full_data.empty:
                    # 从Redis全量数据中进行筛选
                    filtered_data = self._filter_data_from_full_cache(
                        full_data=full_data,
                        level_range=level_range,
                        role_grade_limit_range=role_grade_limit_range,
                        price_range=price_range,
                        server=server,
                        all_skill=all_skill,
                        limit=limit
                    )
                    
                    elapsed_time = time.time() - start_time
                    print(f"从Redis全量缓存筛选完成，耗时: {elapsed_time:.3f}秒，返回: {len(filtered_data)} 条数据")
                    return filtered_data
            
            # 降级到MySQL查询
            print("使用MySQL数据库查询（降级模式）...")
            return self._get_market_data_from_mysql(
                level_range=level_range,
                role_grade_limit_range=role_grade_limit_range,
                price_range=price_range,
                server=server,
                all_skill=all_skill,
                limit=limit
            )

        except Exception as e:
            self.logger.error(f"获取市场数据失败: {e}")
            print(f"查询异常: {e}")
            return pd.DataFrame()

    def _get_market_data_from_mysql(self,
                                   level_range: Optional[Tuple[int, int]] = None,
                                   role_grade_limit_range: Optional[Tuple[int, int]] = None,
                                   price_range: Optional[Tuple[float, float]] = None,
                                   server: Optional[str] = None,
                                   all_skill: Optional[Union[str, List[str]]] = None,
                                   limit: int = 1000) -> pd.DataFrame:
        """
        从MySQL数据库获取宠物数据（原始查询逻辑）
        """
        try:
            # 构建SQLAlchemy查询 - 只查询需要的13个字段
            query = db.session.query(
                Pet.role_grade_limit,
                Pet.equip_level,
                Pet.growth,
                Pet.is_baobao,
                Pet.all_skill,
                Pet.evol_skill_list,
                Pet.texing,
                Pet.lx,
                Pet.equip_list,
                Pet.equip_list_amount,
                Pet.neidan,
                Pet.equip_sn,
                Pet.price,
                Pet.update_time  # 用于排序
            )

            # 处理all_skill参数，支持字符串或列表
            target_skills = []
            if all_skill:
                if isinstance(all_skill, str):
                    target_skills = [s for s in all_skill.split('|') if s]
                elif isinstance(all_skill, list):
                    target_skills = [str(s) for s in all_skill if s]

            # 基础筛选条件
            if level_range is not None:
                min_level, max_level = level_range
                query = query.filter(Pet.equip_level.between(min_level, max_level))

            if role_grade_limit_range is not None:
                min_role_grade_limit, max_role_grade_limit = role_grade_limit_range
                query = query.filter(Pet.role_grade_limit.between(min_role_grade_limit, max_role_grade_limit))

            if price_range is not None:
                min_price, max_price = price_range
                query = query.filter(Pet.price.between(min_price, max_price))

            # 注意：server字段不在查询的13个字段中，如果需要服务器筛选，需要添加Pet.server_name到查询中
            # if server is not None:
            #     query = query.filter(Pet.server_name == server)

            # 技能筛选
            if target_skills:
                # 技能SQL初步过滤
                for skill in target_skills:
                    query = query.filter(Pet.all_skill.like(f"%{skill}%"))
                
                # 技能数量过滤 过滤出技能数量 <= len(target_skills)+2 的数据
                skill_count_limit = len(target_skills) + 1
                query = query.filter(
                    func.length(Pet.all_skill) - func.length(func.replace(Pet.all_skill, '|', '')) + 1 <= skill_count_limit
                )

            # 排序和限制
            query = query.order_by(Pet.update_time.desc()).limit(limit)

            # 执行查询
            pets = query.all()
            
            if pets:
                # 转换为字典列表 - 查询结果已经是元组，需要按顺序映射字段
                data_list = []
                for pet_tuple in pets:
                    pet_dict = {
                        'role_grade_limit': pet_tuple[0],
                        'equip_level': pet_tuple[1],
                        'growth': pet_tuple[2],
                        'is_baobao': pet_tuple[3],
                        'all_skill': pet_tuple[4],
                        'evol_skill_list': pet_tuple[5],
                        'texing': pet_tuple[6],
                        'lx': pet_tuple[7],
                        'equip_list': pet_tuple[8],
                        'equip_list_amount': pet_tuple[9],
                        'neidan': pet_tuple[10],
                        'equip_sn': pet_tuple[11],
                        'price': pet_tuple[12],
                        'update_time': pet_tuple[13]  # 用于排序的字段
                    }
                    data_list.append(pet_dict)
                
                result_df = pd.DataFrame(data_list)
                
                # Python集合精确过滤技能
                if target_skills:
                    target_set = set(target_skills)
                    def match(row):
                        all_skill_val = row.get('all_skill', '')
                        skill_set = set(all_skill_val.split('|')) if all_skill_val else set()
                        return target_set.issubset(skill_set)
                    result_df = result_df[result_df.apply(match, axis=1)]
                
                # 去重
                result_df = result_df.drop_duplicates(subset=['equip_sn'], keep='first')
                
                print(f"从MySQL数据库加载了 {len(result_df)} 条宠物市场数据")
                return result_df
            else:
                print(f"从MySQL数据库查询到0条宠物市场数据")
                return pd.DataFrame()

        except Exception as e:
            self.logger.error(f"查询宠物市场数据失败: {e}")
            print(f"SQL执行异常: {e}")
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
        # 优先使用内存缓存
        if self._full_data_cache is not None and not self._full_data_cache.empty:
            print("使用内存缓存进行相似度计算...")
            # 基础过滤条件
            role_grade_limit = target_features.get('role_grade_limit', 0)
            
            # 等级范围：目标等级±20级
            role_grade_limit_range = (max(0, role_grade_limit - 20), role_grade_limit + 20)

            all_skill = target_features.get('all_skill', '')
            
            # 从内存缓存中筛选数据
            market_data = self._filter_data_from_full_cache(
                full_data=self._full_data_cache,
                role_grade_limit_range=role_grade_limit_range,
                all_skill=all_skill,
                limit=5000
            )
        else:
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
            target_features: 目标召唤兽特征
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

    def _get_mysql_pets_count(self) -> int:
        """
        获取MySQL中pets表的总记录数
        
        Returns:
            int: pets表总记录数
        """
        try:
            from src.database import db
            from src.models.pet import Pet
            from flask import current_app
            from src.app import create_app
            
            # 确保在Flask应用上下文中
            if not current_app:
                # 创建应用上下文
                app = create_app()
                with app.app_context():
                    return self._get_mysql_pets_count()
            
            # 查询pets表总数
            count = db.session.query(Pet).count()
            self.mysql_data_count = count
            self.logger.info(f"MySQL pets表总记录数: {count:,}")
            return count
            
        except Exception as e:
            self.logger.error(f"获取MySQL宠物数据总数失败: {e}")
            return 0

    def _load_full_data_to_redis(self, force_refresh: bool = False) -> bool:
        """
        加载全量宠物数据到Redis - 参考装备模块的批次处理和进度跟踪
        
        Args:
            force_refresh: 是否强制刷新
            
        Returns:
            bool: 是否加载成功
        """
        if not self.redis_cache:
            return False
            
        try:
            import time
            from datetime import datetime
            
            # 初始化进度跟踪
            self._refresh_status = "running"
            self._refresh_progress = 0
            self._refresh_message = "开始加载宠物数据..."
            self._refresh_start_time = datetime.now()
            self._refresh_processed_records = 0
            self._refresh_current_batch = 0
            
            start_time = time.time()
            
            # 检查是否已有缓存且不需要强制刷新
            if not force_refresh:
                self._refresh_message = "检查Redis全量缓存..."
                self._refresh_progress = 5
                
                try:
                    print("🔍 开始检查Redis缓存...")
                    hash_key = f"{self._full_cache_key}:hash"
                    cached_data = self.redis_cache.get_hash_data(hash_key)
                    print(f"🔍 Redis缓存检查完成，结果: {cached_data is not None}")
                    
                    if cached_data is not None and not cached_data.empty:
                        print(f"Redis全量缓存已存在，数据量: {len(cached_data)} 条")
                        # 正确设置状态信息
                        self._refresh_status = "completed"
                        self._refresh_progress = 100
                        self._refresh_message = "使用现有缓存"
                        self._refresh_total_records = len(cached_data)
                        self._refresh_processed_records = len(cached_data)
                        self._refresh_total_batches = 1
                        self._refresh_current_batch = 1
                        # 将数据加载到内存缓存
                        self._full_data_cache = cached_data
                        return True
                    else:
                        print("Redis缓存不存在或为空，将重新加载数据")
                except Exception as e:
                    print(f"检查Redis缓存时出错: {e}")
                    self._refresh_message = f"检查缓存失败: {str(e)}"
                    # 继续执行重新加载
            
            print(" 开始从MySQL加载宠物数据到Redis...")
            
            # 从数据库加载全量数据
            from src.database import db
            from src.models.pet import Pet
            from flask import current_app
            from src.app import create_app
            
            # 确保在Flask应用上下文中
            if not current_app:
                # 创建应用上下文
                app = create_app()
                with app.app_context():
                    return self._load_full_data_to_redis(force_refresh)
            
            # 获取总记录数
            self._refresh_message = "统计数据总量..."
            self._refresh_progress = 10
            
            # 获取MySQL宠物数据总数
            full_count = db.session.query(Pet).count()
            self.mysql_data_count = full_count
            total_count = full_count  # 加载全部数据

            print(f"宠物总记录数: {full_count}，本次加载: {total_count} 条")
            
            # 动态调整批次大小
            if total_count > 50000:
                batch_size = 300   # 大数据集：小批次
            elif total_count > 20000:
                batch_size = 500   # 中等数据集
            elif total_count > 5000:
                batch_size = 800   # 中小数据集
            else:
                batch_size = 300   # 小数据集
            
            total_batches = (total_count + batch_size - 1) // batch_size
            self._refresh_total_records = total_count
            self._refresh_total_batches = total_batches
            
            print(f"将分 {total_batches} 批处理，每批 {batch_size} 条")
            
            # 分批加载数据
            all_data = []
            offset = 0
            
            for batch_num in range(total_batches):
                # 更新进度
                self._refresh_current_batch = batch_num + 1
                batch_progress = 10 + int(((batch_num + 1) / total_batches) * 80)  # 10-90%的进度范围
                self._refresh_progress = min(batch_progress, 90)
                self._refresh_message = f"处理第 {batch_num + 1}/{total_batches} 批宠物数据..."
                
                print(f"处理第 {batch_num + 1}/{total_batches} 批，偏移量: {offset}")
                
                try:
                    # 构建批次查询，确保不超过总限制
                    remaining = total_count - offset
                    actual_limit = min(batch_size, remaining)
                    if actual_limit <= 0:
                        break
                        
                    # 查询宠物数据 - 只查询需要的13个字段
                    query = db.session.query(
                        Pet.role_grade_limit,
                        Pet.equip_level,
                        Pet.growth,
                        Pet.is_baobao,
                        Pet.all_skill,
                        Pet.evol_skill_list,
                        Pet.texing,
                        Pet.lx,
                        Pet.equip_list,
                        Pet.equip_list_amount,
                        Pet.neidan,
                        Pet.equip_sn,
                        Pet.price,
                        Pet.update_time  # 用于排序
                    ).offset(offset).limit(actual_limit)
                    pets = query.all()
                    
                    if not pets:
                        print(f"第 {batch_num + 1} 批无数据，跳过")
                        continue
                    
                    # 转换为字典格式 - 查询结果已经是元组，需要按顺序映射字段
                    batch_data = []
                    for pet_tuple in pets:
                        pet_dict = {
                            'role_grade_limit': pet_tuple[0],
                            'equip_level': pet_tuple[1],
                            'growth': pet_tuple[2],
                            'is_baobao': pet_tuple[3],
                            'all_skill': pet_tuple[4],
                            'evol_skill_list': pet_tuple[5],
                            'texing': pet_tuple[6],
                            'lx': pet_tuple[7],
                            'equip_list': pet_tuple[8],
                            'equip_list_amount': pet_tuple[9],
                            'neidan': pet_tuple[10],
                            'equip_sn': pet_tuple[11],
                            'price': pet_tuple[12],
                            'update_time': pet_tuple[13]  # 用于排序的字段
                        }
                        batch_data.append(pet_dict)
                    
                    all_data.extend(batch_data)
                    self._refresh_processed_records += len(batch_data)
                    
                    progress_percentage = (self._refresh_processed_records / total_count) * 100
                    print(f"已处理 {self._refresh_processed_records}/{total_count} 条数据 ({progress_percentage:.1f}%)")
                    
                    offset += batch_size
                    
                    # 每处理几批就强制垃圾回收，释放内存
                    if batch_num % 5 == 0:
                        import gc
                        gc.collect()
                        
                except Exception as e:
                    self.logger.error(f"处理第 {batch_num + 1} 批数据失败: {e}")
                    continue
            
            if not all_data:
                print("未找到宠物数据")
                self._refresh_status = "error"
                self._refresh_message = "未找到宠物数据"
                return False
            
            # 转换为DataFrame
            self._refresh_message = "构建数据结构..."
            self._refresh_progress = 92
            
            df = pd.DataFrame(all_data)
            print(f"总共加载 {len(df)} 条宠物数据")
            
            # 存储到Redis分块缓存
            self._refresh_message = "保存到Redis缓存..."
            self._refresh_progress = 95
            
            chunk_size = 500  # 减小块大小，避免超时
            ttl_seconds = None if self._cache_ttl_hours == -1 else self._cache_ttl_hours * 3600
            
            print(f"准备存储到Redis，数据量: {len(df)} 条，块大小: {chunk_size}")
            
            # 无缝更新策略：先存储新数据，再清理旧数据
            # 使用临时键名存储新数据，避免覆盖现有数据
            temp_cache_key = f"{self._full_cache_key}_temp_{int(time.time())}"
            print(f"使用临时键名存储新数据: {temp_cache_key}")
            
            # 重试机制 - 先存储到临时键
            success = False
            max_retries = 3
            for attempt in range(max_retries):
                try:
                    print(f"第 {attempt + 1} 次尝试存储新数据到临时键...")
                    temp_hash_key = f"{temp_cache_key}:hash"
                    success = self.redis_cache.set_hash_data(
                        hash_key=temp_hash_key,
                        data=df,
                        ttl=ttl_seconds
                    )
                    if success:
                        print("新数据存储到临时键成功！")
                        break
                    else:
                        print(f"第 {attempt + 1} 次存储失败，准备重试...")
                except Exception as e:
                    print(f"第 {attempt + 1} 次存储异常: {e}")
                    if attempt < max_retries - 1:
                        import time
                        time.sleep(2)  # 等待2秒后重试
                    else:
                        print("所有重试都失败了")
            
            if success:
                # 新数据存储成功，开始无缝切换
                print(" 开始无缝切换：将临时数据切换为正式数据...")
                
                # 1. 先清理旧的正式缓存数据
                print("清理旧的正式缓存数据...")
                old_cleared_count = self.redis_cache.clear_pattern(f"{self._full_cache_key}:*")
                if old_cleared_count > 0:
                    print(f"已清理 {old_cleared_count} 个旧正式缓存键")
                else:
                    print("没有找到旧的正式缓存数据")
                
                # 2. 直接重新存储到正式键（更简单可靠的方式）
                print("将临时数据复制到正式键...")
                copy_success = self._copy_temp_cache_to_official(temp_cache_key, self._full_cache_key, df, chunk_size, ttl_seconds)
                
                if copy_success:
                    print(" 无缝切换完成！新数据已生效")
                    elapsed_time = time.time() - start_time
                    cache_info = "永不过期（仅手动刷新）" if self._cache_ttl_hours == -1 else f"{self._cache_ttl_hours}小时"
                    print(f"全量宠物数据已缓存到Redis，缓存策略: {cache_info}，总耗时: {elapsed_time:.2f}秒")
                    self._full_data_cache = df  # 同时缓存到内存
                    
                    # 完成进度跟踪
                    self._refresh_status = "completed"
                    self._refresh_progress = 100
                    self._refresh_message = "宠物数据加载完成！"
                    
                    # 清理临时数据
                    print("清理临时数据...")
                    self.redis_cache.clear_pattern(f"{temp_cache_key}:*")
                    
                    return True
                else:
                    print(" 无缝切换失败，清理临时数据...")
                    self.redis_cache.clear_pattern(f"{temp_cache_key}:*")
                    self._refresh_status = "error"
                    self._refresh_message = "无缝切换失败"
                    return False
            else:
                print(" 新数据存储失败，清理临时数据...")
                self.redis_cache.clear_pattern(f"{temp_cache_key}:*")
                self._refresh_status = "error"
                self._refresh_message = "新数据存储失败"
                return False
                
        except Exception as e:
            self.logger.error(f"加载全量数据到Redis失败: {e}")
            print(f"加载全量数据失败: {e}")
            self._refresh_status = "error"
            self._refresh_message = f"加载失败: {str(e)}"
            return False

    def _get_full_data_from_redis(self) -> Optional[pd.DataFrame]:
        """从Redis获取全量宠物数据"""
        if not self.redis_cache:
            return None
            
        try:
            # 先检查内存缓存
            if self._full_data_cache is not None and not self._full_data_cache.empty:
                print(f"从内存缓存获取全量数据: {len(self._full_data_cache)} 条")
                return self._full_data_cache
            
            # 从Redis获取Hash数据
            hash_key = f"{self._full_cache_key}:hash"
            cached_data = self.redis_cache.get_hash_data(hash_key)
            
            if cached_data is not None and not cached_data.empty:
                print(f"从Redis Hash缓存获取全量数据: {len(cached_data)} 条")
                self._full_data_cache = cached_data  # 缓存到内存
                return cached_data
            else:
                print("Redis全量缓存未命中")
                return None
                
        except Exception as e:
            self.logger.warning(f"从Redis获取全量数据失败: {e}")
            return None

    def _filter_data_from_full_cache(self, full_data: pd.DataFrame, **filters) -> pd.DataFrame:
        """
        从Redis全量数据中进行筛选 - 使用pandas高效筛选
        
        Args:
            full_data: 全量宠物数据
            **filters: 筛选条件
            
        Returns:
            筛选后的DataFrame
        """
        try:
            filtered_df = full_data.copy()
            
            # 基础筛选条件
            level_range = filters.get('level_range')
            role_grade_limit_range = filters.get('role_grade_limit_range')
            price_range = filters.get('price_range')
            server = filters.get('server')
            all_skill = filters.get('all_skill')
            limit = filters.get('limit', 1000)
            
            print(f"开始从 {len(filtered_df)} 条全量数据中筛选...")
            
            # 1. 等级范围筛选
            if level_range:
                min_level, max_level = level_range
                filtered_df = filtered_df[
                    (filtered_df['equip_level'] >= min_level) & 
                    (filtered_df['equip_level'] <= max_level)
                ]
                print(f"按等级范围({min_level}-{max_level})筛选后: {len(filtered_df)} 条")
            
            # 2. 携带等级范围筛选
            if role_grade_limit_range:
                min_role_grade_limit, max_role_grade_limit = role_grade_limit_range
                filtered_df = filtered_df[
                    (filtered_df['role_grade_limit'] >= min_role_grade_limit) & 
                    (filtered_df['role_grade_limit'] <= max_role_grade_limit)
                ]
                print(f"按携带等级范围({min_role_grade_limit}-{max_role_grade_limit})筛选后: {len(filtered_df)} 条")
            
            # 3. 价格范围筛选
            if price_range:
                min_price, max_price = price_range
                filtered_df = filtered_df[
                    (filtered_df['price'] >= min_price) & 
                    (filtered_df['price'] <= max_price)
                ]
                print(f"按价格范围({min_price}-{max_price})筛选后: {len(filtered_df)} 条")
            
            # 4. 服务器筛选
            if server:
                filtered_df = filtered_df[filtered_df['server_name'] == server]
                print(f"按服务器({server})筛选后: {len(filtered_df)} 条")
            
            # 5. 技能筛选
            if all_skill:
                target_skills = []
                if isinstance(all_skill, str):
                    target_skills = [s for s in all_skill.split('|') if s]
                elif isinstance(all_skill, list):
                    target_skills = [str(s) for s in all_skill if s]
                
                if target_skills:
                    target_set = set(target_skills)
                    def match(row):
                        all_skill_val = row.get('all_skill', '')
                        skill_set = set(all_skill_val.split('|')) if all_skill_val else set()
                        return target_set.issubset(skill_set)
                    filtered_df = filtered_df[filtered_df.apply(match, axis=1)]
                    print(f"按技能筛选后: {len(filtered_df)} 条")
            
            # 6. 按更新时间排序并限制数量
            if 'update_time' in filtered_df.columns:
                # 确保update_time是datetime类型
                if filtered_df['update_time'].dtype == 'object':
                    filtered_df['update_time'] = pd.to_datetime(filtered_df['update_time'])
                
                filtered_df = filtered_df.sort_values('update_time', ascending=False)
            
            # 7. 限制返回数量
            if len(filtered_df) > limit:
                filtered_df = filtered_df.head(limit)
                print(f"限制返回数量到: {limit} 条")
            
            return filtered_df
            
        except Exception as e:
            self.logger.error(f"从Redis全量数据筛选失败: {e}")
            print(f"Redis筛选异常: {e}")
            return pd.DataFrame()

    def _copy_temp_cache_to_official(self, temp_key: str, official_key: str, df: pd.DataFrame, chunk_size: int, ttl_seconds: Optional[int]) -> bool:
        """
        将临时缓存复制到正式缓存（无缝切换）
        
        Args:
            temp_key: 临时缓存键名
            official_key: 正式缓存键名
            df: 数据DataFrame
            chunk_size: 块大小
            ttl_seconds: TTL秒数
            
        Returns:
            bool: 是否复制成功
        """
        try:
            print(f"开始复制临时缓存 {temp_key} 到正式缓存 {official_key}...")
            
            # 直接使用set_hash_data重新存储到正式Hash键
            official_hash_key = f"{official_key}:hash"
            success = self.redis_cache.set_hash_data(
                hash_key=official_hash_key,
                data=df,
                ttl=ttl_seconds
            )
            
            if success:
                print(" 临时缓存复制到正式缓存成功")
                return True
            else:
                print(" 临时缓存复制到正式缓存失败")
                return False
                
        except Exception as e:
            print(f" 复制临时缓存失败: {e}")
            return False

    def refresh_full_cache(self) -> bool:
        """手动刷新全量缓存"""
        print(" 手动刷新宠物全量缓存...")
        self._full_data_cache = None  # 清空内存缓存
        return self._load_full_data_to_redis(force_refresh=True)
    
    def set_cache_expiry(self, hours: int):
        """
        设置缓存过期时间
        
        Args:
            hours: 缓存过期时间（小时），-1表示永不过期
        """
        self._cache_ttl_hours = hours
        if hours == -1:
            print("宠物缓存设置为永不过期模式（仅手动刷新）")
        else:
            print(f"宠物缓存设置为 {hours} 小时自动过期")
    
    def manual_refresh(self) -> bool:
        """
        手动刷新缓存（显式调用）
        """
        print(" 用户手动刷新宠物缓存")
        return self.refresh_full_cache()

    def get_cache_status(self) -> Dict[str, Any]:
        """获取缓存状态信息"""
        try:
            # 获取MySQL宠物数据总数
            mysql_count = self._get_mysql_pets_count()
            
            status = {
                'redis_available': False,
                'full_cache_exists': False,
                'full_cache_size': 0,
                'memory_cache_size': 0,
                'cache_key': self._full_cache_key,
                'cache_ttl_hours': self._cache_ttl_hours,
                'cache_never_expires': self._cache_ttl_hours == -1,
                'refresh_mode': 'manual_only' if self._cache_ttl_hours == -1 else 'auto_expire',
                'mysql_data_count': mysql_count
            }
            
            if self.redis_cache and self.redis_cache.is_available():
                status['redis_available'] = True
                
                # 检查Redis中的全量缓存
                try:
                    metadata = self.redis_cache.get(f"{self._full_cache_key}:meta")
                    if metadata:
                        status['full_cache_exists'] = True
                        status['full_cache_size'] = metadata.get('total_rows', 0)
                        status['cache_created_at'] = metadata.get('created_at')
                        status['chunk_info'] = {
                            'total_chunks': metadata.get('total_chunks', 0),
                            'chunk_size': metadata.get('chunk_size', 0)
                        }
                except Exception as e:
                    self.logger.debug(f"检查Redis缓存状态失败: {e}")
            
            # 检查内存缓存
            if self._full_data_cache is not None:
                status['memory_cache_size'] = len(self._full_data_cache)
            
            return status
            
        except Exception as e:
            self.logger.error(f"获取缓存状态失败: {e}")
            return {'error': str(e)}

    def get_refresh_status(self) -> Dict[str, Any]:
        """
        获取刷新进度状态
        
        Returns:
            Dict: 包含进度信息的字典
        """
        # 添加调试信息
        print(f"🔍 获取刷新状态 - 实例ID: {id(self)}")
        print(f"🔍 当前状态: {self._refresh_status}, 进度: {self._refresh_progress}%")
        print(f"🔍 内存缓存状态: {self._full_data_cache is not None and not self._full_data_cache.empty if self._full_data_cache is not None else False}")
        
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

    @classmethod
    def clear_cache(cls):
        """清空单例实例的缓存"""
        with cls._lock:
            if cls._instance and hasattr(cls._instance, '_full_data_cache'):
                cls._instance._full_data_cache = None
                cls._instance._refresh_status = "idle"
                cls._instance._refresh_progress = 0
                cls._instance._refresh_message = ""
                print("已清空宠物数据缓存")

    @classmethod
    def get_cache_status_static(cls) -> Dict[str, Any]:
        """获取单例实例的缓存状态"""
        with cls._lock:
            if cls._instance:
                return cls._instance.get_cache_status()
            else:
                return {
                    'redis_available': False,
                    'full_cache_exists': False,
                    'full_cache_size': 0,
                    'memory_cache_size': 0
                }

    @classmethod
    def get_refresh_status_static(cls) -> Dict[str, Any]:
        """获取单例实例的刷新状态"""
        with cls._lock:
            if cls._instance:
                return cls._instance.get_refresh_status()
            else:
                return {
                    "status": "idle",
                    "progress": 0,
                    "message": "",
                    "processed_records": 0,
                    "total_records": 0,
                    "current_batch": 0,
                    "total_batches": 0,
                    "start_time": None,
                    "elapsed_seconds": 0
                }