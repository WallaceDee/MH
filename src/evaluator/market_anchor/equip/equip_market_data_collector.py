from datetime import datetime
from typing import Dict, Any, List, Optional, Union, Tuple
import logging
import pandas as pd
import os

# 从配置文件加载常量
from .constant import (
    get_agility_suits, get_magic_suits, get_high_value_suits,
    get_precise_filter_suits, get_high_value_effects, get_important_effects,
    get_high_value_simple_levels, get_simple_effect_id,
    get_low_value_special_skills, get_low_value_effects
)

# 套装效果ID常量定义
# 高价值套装
AGILITY_SUITS = get_agility_suits()  # 敏捷套装
MAGIC_SUITS = get_magic_suits()  # 魔力套装
HIGH_VALUE_SUITS = get_high_value_suits()  # 合并高价值套装

# 精确筛选套装（允许精确筛选的套装效果）
PRECISE_FILTER_SUITS = get_precise_filter_suits()  # 定心术、变身、碎星诀、天神护体、满天花雨、浪涌

# 高价值特效
HIGH_VALUE_EFFECTS = get_high_value_effects()  # 无级别，愤怒，永不磨损 高价值特效
IMPORTANT_EFFECTS = get_important_effects()  # 相似度计算中重要的特效

# 高价值简易装备等级
HIGH_VALUE_EQUIP_LEVELS = get_high_value_simple_levels()  # 高价值简易装备等级
SIMPLE_EFFECT_ID = get_simple_effect_id()  # 简易装备特效编号

# 低价值特技
LOW_VALUE_SPECIAL_SKILLS = get_low_value_special_skills()
# 低价值特效
LOW_VALUE_EFFECTS = get_low_value_effects()

# 添加项目根目录到Python路径，解决模块导入问题
current_dir = os.path.dirname(os.path.abspath(__file__))

try:
    from ...feature_extractor.equip_feature_extractor import EquipFeatureExtractor
    from src.database import db
    from src.models.equipment import Equipment
    from sqlalchemy import and_, or_, func, text
except ImportError:
    try:
        from src.evaluator.feature_extractor.equip_feature_extractor import EquipFeatureExtractor
        from src.database import db
        from src.models.equipment import Equipment
        from sqlalchemy import and_, or_, func, text
    except ImportError:
        # 如果都导入失败，创建一个简单的占位符
        class EquipFeatureExtractor:
            def __init__(self):
                pass

            def extract_features(self, equip_data):
                return {}


class EquipMarketDataCollector:
    """装备市场数据采集器 - 从数据库中获取和处理装备市场数据"""

    _instance = None  # 单例实例
    _lock = None  # 线程锁，确保线程安全
    
    def __new__(cls):
        """单例模式实现"""
        import threading
        if cls._lock is None:
            cls._lock = threading.Lock()
            
        with cls._lock:
            if cls._instance is None:
                instance = super(EquipMarketDataCollector, cls).__new__(cls)
                cls._instance = instance
                # 标记实例是否已初始化，避免重复初始化
                instance._initialized = False
                print("创建新的 EquipMarketDataCollector 单例实例")
            else:
                print("使用现有的 EquipMarketDataCollector 单例实例")
            
            return cls._instance

    def __init__(self):
        """
        初始化装备市场数据采集器 - 支持Redis全量缓存（单例模式下只初始化一次）
        """
        # 避免重复初始化
        if hasattr(self, '_initialized') and self._initialized:
            return
            
        self.feature_extractor = EquipFeatureExtractor()
        self.logger = logging.getLogger(__name__)

        # 初始化Redis缓存
        try:
            from src.utils.redis_cache import get_redis_cache
            self.redis_cache = get_redis_cache()
            if self.redis_cache and self.redis_cache.is_available():
                self.logger.info("Redis缓存初始化成功，将使用Redis全量缓存模式")
                print("装备数据采集器初始化，使用Redis全量缓存模式")
            else:
                self.redis_cache = None
                print("装备数据采集器初始化，Redis不可用，使用MySQL数据库")
        except Exception as e:
            self.logger.warning(f"Redis缓存初始化失败: {e}")
            self.redis_cache = None
            print("装备数据采集器初始化，Redis初始化失败，使用MySQL数据库")
        
        # 全量缓存相关属性
        self._full_cache_key = "equipment_market_data_full"
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
        self.mysql_data_count = 0  # MySQL中equipments表的总记录数
        
        self._initialized = True
        cache_mode = "永不过期模式" if self._cache_ttl_hours == -1 else f"{self._cache_ttl_hours}小时过期"
        print(f"装备市场数据采集器单例初始化完成，支持Redis全量缓存（{cache_mode}）")

    def _get_mysql_equipments_count(self) -> int:
        """
        获取MySQL中equipments表的总记录数
        
        Returns:
            int: equipments表总记录数
        """
        try:
            from src.database import db
            from src.models.equipment import Equipment
            from flask import current_app
            from src.app import create_app
            
            # 确保在Flask应用上下文中
            if not current_app:
                # 创建应用上下文
                app = create_app()
                with app.app_context():
                    return self._get_mysql_equipments_count()
            
            # 查询equipments表总数
            count = db.session.query(Equipment).count()
            self.mysql_data_count = count
            self.logger.info(f"MySQL equipments表总记录数: {count:,}")
            return count
            
        except Exception as e:
            self.logger.error(f"获取MySQL装备数据总数失败: {e}")
            return 0

    def _load_full_data_to_redis(self, force_refresh: bool = False) -> bool:
        """
        加载全量装备数据到Redis - 参考角色模块的批次处理和进度跟踪
        
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
            self._refresh_message = "开始加载装备数据..."
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
                    cached_data = self.redis_cache.get_chunked_data(self._full_cache_key)
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
            
            print("🧪 [临时测试模式] 开始从MySQL加载装备数据到Redis...")
            
            # 从数据库加载全量数据
            from src.database import db
            from src.models.equipment import Equipment
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
            
            # 获取MySQL装备数据总数
            full_count = db.session.query(Equipment).count()
            self.mysql_data_count = full_count
            total_count = full_count  # 加载全部数据
            # total_count = 1500  # 临时测试：加载500条数据

            print(f"装备总记录数: {full_count}，本次加载: {total_count} 条")
            
            # 动态调整批次大小（参考角色模块）
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
                self._refresh_message = f"处理第 {batch_num + 1}/{total_batches} 批装备数据..."
                
                print(f"处理第 {batch_num + 1}/{total_batches} 批，偏移量: {offset}")
                
                try:
                    # 构建批次查询，确保不超过总限制
                    remaining = total_count - offset
                    actual_limit = min(batch_size, remaining)
                    if actual_limit <= 0:
                        break
                        
                    # 只查询特征提取器需要的字段（排除iType和cDesc）
                    # 增加灵饰特征提取器需要的字段：'damage', 'defense', 'magic_damage', 'magic_defense', 'fengyin', 'anti_fengyin', 'speed'
                    required_fields = [
                        Equipment.equip_level, Equipment.kindid, Equipment.init_damage, Equipment.init_damage_raw,
                        Equipment.all_damage, Equipment.init_wakan, Equipment.init_defense, Equipment.init_hp,
                        Equipment.init_dex, Equipment.mingzhong, Equipment.shanghai, Equipment.addon_tizhi,
                        Equipment.addon_liliang, Equipment.addon_naili, Equipment.addon_minjie, Equipment.addon_lingli,
                        Equipment.addon_moli, Equipment.agg_added_attrs, Equipment.gem_value, Equipment.gem_level,
                        Equipment.special_skill, Equipment.special_effect, Equipment.suit_effect, Equipment.large_equip_desc,
                        # 灵饰特征提取器需要的字段
                        Equipment.damage, Equipment.defense, Equipment.magic_damage, Equipment.magic_defense,
                        Equipment.fengyin, Equipment.anti_fengyin, Equipment.speed,
                        # 召唤兽装备特征提取器需要的字段
                        Equipment.fangyu, Equipment.qixue, Equipment.addon_fali, Equipment.xiang_qian_level, Equipment.addon_status,
                        # 基础字段
                        Equipment.equip_sn, Equipment.price, Equipment.server_name, Equipment.update_time
                    ]
                    query = db.session.query(*required_fields).offset(offset).limit(actual_limit)
                    equipments = query.all()
                    
                    if not equipments:
                        print(f"第 {batch_num + 1} 批无数据，跳过")
                        continue
                    
                    # 转换为字典格式 - 现在查询返回的是元组
                    batch_data = []
                    field_names = [
                        'equip_level', 'kindid', 'init_damage', 'init_damage_raw', 'all_damage',
                        'init_wakan', 'init_defense', 'init_hp', 'init_dex', 'mingzhong', 'shanghai',
                        'addon_tizhi', 'addon_liliang', 'addon_naili', 'addon_minjie', 'addon_lingli', 'addon_moli',
                        'agg_added_attrs', 'gem_value', 'gem_level', 'special_skill', 'special_effect', 'suit_effect',
                        'large_equip_desc',
                        # 灵饰特征提取器需要的字段
                        'damage', 'defense', 'magic_damage', 'magic_defense', 'fengyin', 'anti_fengyin', 'speed',
                        # 召唤兽装备特征提取器需要的字段
                        'fangyu', 'qixue', 'addon_fali', 'xiang_qian_level', 'addon_status',
                        # 基础字段
                        'equip_sn', 'price', 'server_name', 'update_time'
                    ]
                    
                    for equipment_tuple in equipments:
                        equipment_dict = {}
                        for i, value in enumerate(equipment_tuple):
                            field_name = field_names[i]
                            if hasattr(value, 'isoformat'):  # datetime对象
                                equipment_dict[field_name] = value.isoformat()
                            else:
                                equipment_dict[field_name] = value
                        batch_data.append(equipment_dict)
                    
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
                print("未找到装备数据")
                self._refresh_status = "error"
                self._refresh_message = "未找到装备数据"
                return False
            
            # 转换为DataFrame
            self._refresh_message = "构建数据结构..."
            self._refresh_progress = 92
            
            df = pd.DataFrame(all_data)
            print(f"总共加载 {len(df)} 条装备数据")
            
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
                    success = self.redis_cache.set_chunked_data(
                        base_key=temp_cache_key,
                        data=df,
                        chunk_size=chunk_size,
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
                print("🔄 开始无缝切换：将临时数据切换为正式数据...")
                
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
                    print(f"全量装备数据已缓存到Redis，缓存策略: {cache_info}，总耗时: {elapsed_time:.2f}秒")
                    self._full_data_cache = df  # 同时缓存到内存
                    
                    # 完成进度跟踪
                    self._refresh_status = "completed"
                    self._refresh_progress = 100
                    self._refresh_message = "装备数据加载完成！"
                    
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
        """从Redis获取全量装备数据"""
        if not self.redis_cache:
            return None
            
        try:
            # 先检查内存缓存
            if self._full_data_cache is not None and not self._full_data_cache.empty:
                print(f"从内存缓存获取全量数据: {len(self._full_data_cache)} 条")
                return self._full_data_cache
            
            # 从Redis获取分块数据
            cached_data = self.redis_cache.get_chunked_data(self._full_cache_key)
            
            if cached_data is not None and not cached_data.empty:
                print(f"从Redis分块缓存获取全量数据: {len(cached_data)} 条")
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
            full_data: 全量装备数据
            **filters: 筛选条件
            
        Returns:
            筛选后的DataFrame
        """
        try:
            # 定义安全的字符串包含检查函数，避免正则表达式错误
            def safe_contains(series, pattern):
                """安全的字符串包含检查，避免正则表达式错误"""
                try:
                    return series.str.contains(pattern, na=False, regex=False)
                except Exception:
                    # 如果str.contains失败，使用纯字符串匹配
                    return series.astype(str).str.find(pattern) >= 0
            
            filtered_df = full_data.copy()
            
            # 基础筛选条件
            kindid = filters.get('kindid')
            level_range = filters.get('level_range')
            price_range = filters.get('price_range')
            server = filters.get('server')
            special_skill = filters.get('special_skill')
            suit_effect = filters.get('suit_effect')
            special_effect = filters.get('special_effect')
            exclude_special_effect = filters.get('exclude_special_effect')
            exclude_suit_effect = filters.get('exclude_suit_effect')
            exclude_high_value_simple_equips = filters.get('exclude_high_value_simple_equips', False)
            require_high_value_suits = filters.get('require_high_value_suits', False)
            exclude_high_value_special_skills = filters.get('exclude_high_value_special_skills', False)
            limit = filters.get('limit', 1000)
            
            print(f"开始从 {len(filtered_df)} 条全量数据中筛选...")
            
            # 1. 装备类型筛选
            if kindid is not None:
                filtered_df = filtered_df[filtered_df['kindid'] == kindid]
                print(f"按装备类型({kindid})筛选后: {len(filtered_df)} 条")
            
            # 2. 等级范围筛选
            if level_range:
                min_level, max_level = level_range
                filtered_df = filtered_df[
                    (filtered_df['equip_level'] >= min_level) & 
                    (filtered_df['equip_level'] <= max_level)
                ]
                print(f"按等级范围({min_level}-{max_level})筛选后: {len(filtered_df)} 条")
            
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
            
            # 5. 特技筛选
            if special_skill is not None:
                if not exclude_high_value_special_skills:
                    filtered_df = filtered_df[filtered_df['special_skill'] == special_skill]
                    print(f"按特技({special_skill})筛选后: {len(filtered_df)} 条")
            
            # 6. 排除高价值特技装备
            if exclude_high_value_special_skills:
                low_value_condition = (
                    (filtered_df['special_skill'] == 0) |
                    (filtered_df['special_skill'].isna()) |
                    (filtered_df['special_skill'].isin(LOW_VALUE_SPECIAL_SKILLS))
                )
                filtered_df = filtered_df[low_value_condition]
                print(f"排除高价值特技后: {len(filtered_df)} 条")
            
            # 7. 套装效果筛选
            if suit_effect is not None:
                try:
                    suit_effect_num = int(suit_effect) if suit_effect is not None else 0
                    if suit_effect_num > 0:
                        filtered_df = filtered_df[filtered_df['suit_effect'] == suit_effect_num]
                        print(f"按套装效果({suit_effect_num})筛选后: {len(filtered_df)} 条")
                except (ValueError, TypeError):
                    if suit_effect and str(suit_effect).strip():
                        filtered_df = filtered_df[filtered_df['suit_effect'] == suit_effect]
                        print(f"按套装效果({suit_effect})筛选后: {len(filtered_df)} 条")
            
            # 8. 强制包含高价值套装
            if require_high_value_suits:
                high_value_suits = HIGH_VALUE_SUITS
                if high_value_suits:
                    filtered_df = filtered_df[filtered_df['suit_effect'].isin(high_value_suits)]
                    print(f"强制包含高价值套装后: {len(filtered_df)} 条")
            
            # 9. 特效筛选（JSON数组格式）
            if special_effect is not None and special_effect and len(special_effect) > 0:
                effect_mask = pd.Series([False] * len(filtered_df))
                for effect in special_effect:
                    if effect not in LOW_VALUE_EFFECTS:
                        # 使用精确的JSON数组匹配，避免数字包含关系的误匹配
                        # 比如effect为6，匹配模式：[6], [6,x], [x,6], [x,6,y] 等，但不匹配16, 26等包含6的数字
                        effect_condition = (
                            safe_contains(filtered_df['special_effect'], f'[{effect}]') |
                            safe_contains(filtered_df['special_effect'], f'[{effect},') |
                            safe_contains(filtered_df['special_effect'], f',{effect},') |
                            safe_contains(filtered_df['special_effect'], f',{effect}]')
                        )
                        effect_mask = effect_mask | effect_condition
                
                filtered_df = filtered_df[effect_mask]
                print(f"按特效筛选后: {len(filtered_df)} 条")
            
            # 10. 排除特效筛选
            if exclude_special_effect is not None and exclude_special_effect and len(exclude_special_effect) > 0:
                # 使用与SQLite版本完全相同的逻辑
                # SQLite版本：对每个特效创建排除条件，然后用AND连接
                exclude_conditions = []
                for effect in exclude_special_effect:
                    # 对每个特效，创建排除条件（不包含该特效的装备）
                    effect_exclude_condition = ~(
                        safe_contains(filtered_df['special_effect'], f'[{effect}]') |  # 只有这一个特效：[1]
                        safe_contains(filtered_df['special_effect'], f'[{effect},') |  # 在开头：[1,x,...]
                        safe_contains(filtered_df['special_effect'], f',{effect},') |  # 在中间：[x,1,y,...]
                        safe_contains(filtered_df['special_effect'], f',{effect}]')    # 在结尾：[x,y,1]
                    )
                    exclude_conditions.append(effect_exclude_condition)
                
                # 使用AND连接所有排除条件（与SQLite的and_(*exclude_conditions)相同）
                if exclude_conditions:
                    final_exclude_mask = exclude_conditions[0]
                    for condition in exclude_conditions[1:]:
                        final_exclude_mask = final_exclude_mask & condition
                    filtered_df = filtered_df[final_exclude_mask]
                
                print(f"排除特效后: {len(filtered_df)} 条")
            
            # 11. 排除套装效果
            if exclude_suit_effect is not None and exclude_suit_effect and len(exclude_suit_effect) > 0:
                filtered_df = filtered_df[~filtered_df['suit_effect'].isin(exclude_suit_effect)]
                print(f"排除套装效果后: {len(filtered_df)} 条")
            
            # 12. 排除高价值简易装备
            if exclude_high_value_simple_equips:
                high_value_levels = HIGH_VALUE_EQUIP_LEVELS
                simple_effect_id = SIMPLE_EFFECT_ID
                
                # 排除指定等级且有简易特效的装备
                exclude_condition = pd.Series([False] * len(filtered_df))
                for level in high_value_levels:
                    level_condition = (filtered_df['equip_level'] == level)
                    simple_condition = (
                        safe_contains(filtered_df['special_effect'], f'[{simple_effect_id}]') |
                        safe_contains(filtered_df['special_effect'], f'[{simple_effect_id},') |
                        safe_contains(filtered_df['special_effect'], f',{simple_effect_id},') |
                        safe_contains(filtered_df['special_effect'], f',{simple_effect_id}]')
                    )
                    exclude_condition = exclude_condition | (level_condition & simple_condition)
                
                filtered_df = filtered_df[~exclude_condition]
                print(f"排除高价值简易装备后: {len(filtered_df)} 条")
            
            # 13. 按更新时间排序并限制数量
            if 'update_time' in filtered_df.columns:
                # 确保update_time是datetime类型
                if filtered_df['update_time'].dtype == 'object':
                    filtered_df['update_time'] = pd.to_datetime(filtered_df['update_time'])
                
                filtered_df = filtered_df.sort_values('update_time', ascending=False)
            
            # 14. 限制返回数量
            if len(filtered_df) > limit:
                filtered_df = filtered_df.head(limit)
                print(f"限制返回数量到: {limit} 条")
            
            return filtered_df
            
        except Exception as e:
            self.logger.error(f"从Redis全量数据筛选失败: {e}")
            print(f"Redis筛选异常: {e}")
            return pd.DataFrame()

    def get_market_data(self,
                        kindid: Optional[int] = None,
                        level_range: Optional[Tuple[int, int]] = None,
                        price_range: Optional[Tuple[float, float]] = None,
                        server: Optional[str] = None,
                        special_skill: Optional[int] = None,
                        suit_effect: Optional[int] = None,
                        special_effect: Optional[List[str]] = None,
                        exclude_special_effect: Optional[List[int]] = None,
                        exclude_suit_effect: Optional[List[int]] = None,
                        exclude_high_value_simple_equips: bool = False,
                        require_high_value_suits: bool = False,
                        exclude_high_value_special_skills: bool = False,
                        limit: int = 1000,
                        use_redis_cache: bool = True) -> pd.DataFrame:
        """
        获取市场装备数据 - 优先从Redis全量缓存获取并筛选

        Args:
            kindid: 装备类型ID筛选
            level_range: 等级范围 (min_level, max_level)
            price_range: 价格范围 (min_price, max_price)
            server: 服务器筛选
            special_effect: 特效筛选（高价值必须包含）
            require_high_value_suits: 强制包含高价值套装装备（魔力套和敏捷套）
            special_skill: 特技筛选（必须完全一致）
            exclude_special_effect: 排除特效筛选（排除具有这些特效的装备）
            exclude_suit_effect: 排除套装效果筛选（排除具有这些套装效果的装备）
            exclude_high_value_simple_equips: 排除高价值简易装备（70/90/110/130级的简易装备）
            exclude_high_value_special_skills: 排除高价值特技装备（只搜索无特技或低价值特技装备）
            suit_effect: 套装效果有三种，如果是"附加状态"/"追加法术"，则传入过滤，"变身术"/"变化咒"，则不传入过滤，在锚定的时候做聚类
            limit: 返回数据条数限制
            use_redis_cache: 是否使用Redis缓存

        Returns:
            装备市场数据DataFrame
            
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
                        kindid=kindid,
                        level_range=level_range,
                        price_range=price_range,
                        server=server,
                        special_skill=special_skill,
                        suit_effect=suit_effect,
                        special_effect=special_effect,
                        exclude_special_effect=exclude_special_effect,
                        exclude_suit_effect=exclude_suit_effect,
                        exclude_high_value_simple_equips=exclude_high_value_simple_equips,
                        require_high_value_suits=require_high_value_suits,
                        exclude_high_value_special_skills=exclude_high_value_special_skills,
                        limit=limit
                    )
                    
                    elapsed_time = time.time() - start_time
                    print(f"从Redis全量缓存筛选完成，耗时: {elapsed_time:.3f}秒，返回: {len(filtered_data)} 条数据")
                    return filtered_data
            
            # 降级到MySQL查询
            print("使用MySQL数据库查询（降级模式）...")
            return self._get_market_data_from_mysql(
                kindid=kindid,
                level_range=level_range,
                price_range=price_range,
                server=server,
                special_skill=special_skill,
                suit_effect=suit_effect,
                special_effect=special_effect,
                exclude_special_effect=exclude_special_effect,
                exclude_suit_effect=exclude_suit_effect,
                exclude_high_value_simple_equips=exclude_high_value_simple_equips,
                require_high_value_suits=require_high_value_suits,
                exclude_high_value_special_skills=exclude_high_value_special_skills,
                limit=limit
            )

        except Exception as e:
            self.logger.error(f"获取市场数据失败: {e}")
            print(f"查询异常: {e}")
            return pd.DataFrame()

    def _get_market_data_from_mysql(self,
                                   kindid: Optional[int] = None,
                                   level_range: Optional[Tuple[int, int]] = None,
                                   price_range: Optional[Tuple[float, float]] = None,
                                   server: Optional[str] = None,
                                   special_skill: Optional[int] = None,
                                   suit_effect: Optional[int] = None,
                                   special_effect: Optional[List[str]] = None,
                                   exclude_special_effect: Optional[List[int]] = None,
                                   exclude_suit_effect: Optional[List[int]] = None,
                                   exclude_high_value_simple_equips: bool = False,
                                   require_high_value_suits: bool = False,
                                   exclude_high_value_special_skills: bool = False,
                                   limit: int = 1000) -> pd.DataFrame:
        """
        从MySQL数据库获取装备数据（原始查询逻辑）
        """
        try:
            from src.database import db
            from src.models.equipment import Equipment
            from flask import current_app
            from src.app import create_app
            
            # 确保在Flask应用上下文中
            if not current_app:
                # 创建应用上下文
                app = create_app()
                with app.app_context():
                    return self._get_market_data_from_mysql(
                        kindid=kindid,
                        level_range=level_range,
                        price_range=price_range,
                        server=server,
                        special_skill=special_skill,
                        suit_effect=suit_effect,
                        special_effect=special_effect,
                        exclude_special_effect=exclude_special_effect,
                        exclude_suit_effect=exclude_suit_effect,
                        exclude_high_value_simple_equips=exclude_high_value_simple_equips,
                        require_high_value_suits=require_high_value_suits,
                        exclude_high_value_special_skills=exclude_high_value_special_skills,
                        limit=limit
                    )
            
            # 构建SQLAlchemy查询 - 只查询特征提取器需要的字段
            # 根据特征提取器统计，需要以下字段（排除iType和cDesc）：
            # 增加灵饰特征提取器需要的字段：'damage', 'defense', 'magic_damage', 'magic_defense', 'fengyin', 'anti_fengyin', 'speed'
            required_fields = [
                Equipment.equip_level,
                Equipment.kindid,
                Equipment.init_damage,
                Equipment.init_damage_raw,
                Equipment.all_damage,
                Equipment.init_wakan,
                Equipment.init_defense,
                Equipment.init_hp,
                Equipment.init_dex,
                Equipment.mingzhong,
                Equipment.shanghai,
                Equipment.addon_tizhi,
                Equipment.addon_liliang,
                Equipment.addon_naili,
                Equipment.addon_minjie,
                Equipment.addon_lingli,
                Equipment.addon_moli,
                Equipment.agg_added_attrs,
                Equipment.gem_value,
                Equipment.gem_level,
                Equipment.special_skill,
                Equipment.special_effect,
                Equipment.suit_effect,
                Equipment.large_equip_desc,
                # 灵饰特征提取器需要的字段
                Equipment.damage,
                Equipment.defense,
                Equipment.magic_damage,
                Equipment.magic_defense,
                Equipment.fengyin,
                Equipment.anti_fengyin,
                Equipment.speed,
                # 保留一些必要的元数据字段
                Equipment.equip_sn,
                Equipment.price,
                Equipment.server_name,
                Equipment.update_time
            ]
            query = db.session.query(*required_fields)

            if kindid is not None:
                query = query.filter(Equipment.kindid == kindid)

            if special_skill is not None:
                # 只有当不需要排除高价值特技时，才添加具体的特技筛选条件
                if not (exclude_high_value_special_skills or not require_high_value_suits):
                    query = query.filter(Equipment.special_skill == special_skill)
                else:
                    print(f"跳过具体特技筛选，因为需要排除高价值特技")

            # 特技筛选逻辑：如果目标装备是低价值特技，则排除高价值特技装备
            if exclude_high_value_special_skills:
                # 只能搜索无特技或低价值特技的装备
                query = query.filter(
                    or_(
                        Equipment.special_skill == 0,
                        Equipment.special_skill.is_(None),
                        Equipment.special_skill.in_(LOW_VALUE_SPECIAL_SKILLS)
                    )
                )
                print(f"特技筛选：只搜索无特技或低价值特技装备")

            if suit_effect is not None:
                # 将字符串转换为数字后再比较（pet_equip除外，其他都是数字字符串）
                try:
                    suit_effect_num = int(suit_effect) if suit_effect is not None else 0
                    if suit_effect_num > 0:
                        query = query.filter(Equipment.suit_effect == suit_effect_num)
                except (ValueError, TypeError):
                    # 如果转换失败（可能是pet_equip的字符串套装），直接使用原值
                    if suit_effect and str(suit_effect).strip():
                        query = query.filter(Equipment.suit_effect == suit_effect)

            if require_high_value_suits:
                # 强制包含高价值套装：只搜索魔力套和敏捷套装备
                high_value_suits = HIGH_VALUE_SUITS
                if high_value_suits:
                    query = query.filter(Equipment.suit_effect.in_(high_value_suits))
                    print(f"强制包含高价值套装：只搜索魔力套和敏捷套装备")

            if special_effect is not None:
                # 特效筛选（多选，JSON数组格式）
                if special_effect and len(special_effect) > 0:
                    effect_conditions = []
                    for effect in special_effect:
                        effect_conditions.append(
                            or_(
                                Equipment.special_effect.like(f'[{effect}]'),
                                Equipment.special_effect.like(f'[{effect},%'),
                                Equipment.special_effect.like(f'%,{effect},%'),
                                Equipment.special_effect.like(f'%,{effect}]')
                            )
                        )
                    
                    if effect_conditions:
                        query = query.filter(or_(*effect_conditions))

            if exclude_special_effect is not None:
                # 排除特效筛选：排除具有指定特效的装备
                if exclude_special_effect and len(exclude_special_effect) > 0:
                    exclude_conditions = []
                    for effect in exclude_special_effect:
                        exclude_conditions.append(
                            ~or_(
                                Equipment.special_effect.like(f'[{effect}]'),
                                Equipment.special_effect.like(f'[{effect},%'),
                                Equipment.special_effect.like(f'%,{effect},%'),
                                Equipment.special_effect.like(f'%,{effect}]')
                            )
                        )
                    
                    if exclude_conditions:
                        query = query.filter(and_(*exclude_conditions))

            if exclude_suit_effect is not None:
                # 排除套装效果筛选：排除具有指定套装效果的装备
                if exclude_suit_effect and len(exclude_suit_effect) > 0:
                    query = query.filter(~Equipment.suit_effect.in_(exclude_suit_effect))

            if exclude_high_value_simple_equips:
                # 排除高价值简易装备：排除70级/90级/110级/130级且有简易特效(2)的装备
                high_value_levels = HIGH_VALUE_EQUIP_LEVELS
                simple_effect_conditions = []
                
                for level in high_value_levels:
                    # 对于每个高价值等级，排除该等级且有简易特效的装备
                    simple_conditions = or_(
                        Equipment.special_effect.like(f'[{SIMPLE_EFFECT_ID}]'),
                        Equipment.special_effect.like(f'[{SIMPLE_EFFECT_ID},%'),
                        Equipment.special_effect.like(f'%,{SIMPLE_EFFECT_ID},%'),
                        Equipment.special_effect.like(f'%,{SIMPLE_EFFECT_ID}]')
                    )
                    simple_effect_conditions.append(
                        ~(Equipment.equip_level == level) | ~simple_conditions
                    )
                
                if simple_effect_conditions:
                    query = query.filter(and_(*simple_effect_conditions))
                    print(f"排除高价值简易装备：70级/90级/110级/130级且有简易特效的装备")

            if level_range:
                query = query.filter(Equipment.equip_level.between(level_range[0], level_range[1]))

            if price_range:
                query = query.filter(Equipment.price.between(price_range[0], price_range[1]))

            if server:
                query = query.filter(Equipment.server_name == server)

            # 排序和限制
            query = query.order_by(Equipment.update_time.desc()).limit(limit)

            # 执行查询并转换为DataFrame
            equipments = query.all()
            
            if equipments:
                # 转换为字典列表 - 现在查询返回的是元组
                data_list = []
                field_names = [
                    'equip_level', 'kindid', 'init_damage', 'init_damage_raw', 'all_damage',
                    'init_wakan', 'init_defense', 'init_hp', 'init_dex', 'mingzhong', 'shanghai',
                    'addon_tizhi', 'addon_liliang', 'addon_naili', 'addon_minjie', 'addon_lingli', 'addon_moli',
                    'agg_added_attrs', 'gem_value', 'gem_level', 'special_skill', 'special_effect', 'suit_effect',
                    'large_equip_desc',
                    # 灵饰特征提取器需要的字段
                    'damage', 'defense', 'magic_damage', 'magic_defense', 'fengyin', 'anti_fengyin', 'speed',
                    # 基础字段
                    'equip_sn', 'price', 'server_name', 'update_time'
                ]
                
                for equipment_tuple in equipments:
                    equipment_dict = {}
                    for i, value in enumerate(equipment_tuple):
                        field_name = field_names[i]
                        if hasattr(value, 'isoformat'):  # datetime对象
                            equipment_dict[field_name] = value.isoformat()
                        else:
                            equipment_dict[field_name] = value
                    data_list.append(equipment_dict)
                
                df = pd.DataFrame(data_list)
                print(f"从MySQL数据库加载了 {len(df)} 条装备数据")
                return df
            else:
                print(f"从MySQL数据库查询到0条数据")
                return pd.DataFrame()

        except Exception as e:
            self.logger.error(f"查询装备数据失败: {e}")
            print(f"SQL执行异常: {e}")
            return pd.DataFrame()

    def get_market_data_for_similarity(self,
                                       target_features: Dict[str, Any]) -> pd.DataFrame:
        """
        获取用于相似度计算的市场数据

        专门为相似度计算优化的数据获取方法，包含以下特殊逻辑：
        1. 高价值特效的公平性筛选
        2. 高价值套装的公平性筛选
        3. 相似度计算相关的特效筛选
        4. 适当的数据量控制

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
            exclude_high_value_simple_equips = False

            # 使用预定义的特效和等级常量
            high_value_effects = HIGH_VALUE_EFFECTS
            important_effects = IMPORTANT_EFFECTS

            # 简易装备特殊逻辑处理
            target_equip_level = target_features.get('equip_level', 0)
            simple_effect_id = SIMPLE_EFFECT_ID
            high_value_equip_levels = HIGH_VALUE_EQUIP_LEVELS

            # 检查目标装备是否包含高价值特效
            target_has_high_value_effects = False
            target_has_simple_effect = False
            
            if special_effect and len(special_effect) > 0:
                # 筛选出重要特效用于相似度计算
                filtered_effects = []
                for effect in special_effect:
                    if effect in important_effects:
                        # 如果特效是 SIMPLE_EFFECT_ID，则等级要符合 HIGH_VALUE_EQUIP_LEVELS
                        if effect != simple_effect_id or (effect == simple_effect_id and target_equip_level in high_value_equip_levels):
                            filtered_effects.append(effect)
                    # 检查是否包含基础高价值特效（无级别、愤怒、永不磨损）
                    if effect in high_value_effects:
                        target_has_high_value_effects = True
                    # 检查是否包含简易特效
                    if effect == simple_effect_id:
                        target_has_simple_effect = True

                if filtered_effects:
                    filtered_special_effect = filtered_effects

            # 判断目标装备是否有高价值简易特效
            if target_has_simple_effect and target_equip_level in high_value_equip_levels:
                target_has_high_value_effects = True
                print(f"目标装备{target_equip_level}级简易装备视为高价值特效")

            # 公平性筛选：如果目标装备不包含高价值特效，则排除具有这些特效的装备
            if not target_has_high_value_effects:
                # 排除基础高价值特效
                exclude_special_effect = high_value_effects
                # 排除高价值简易装备（70/90/130级的简易装备）
                exclude_high_value_simple_equips = True
                print(
                    f"目标装备不包含高价值特效，将排除基础高价值特效 {high_value_effects} 和70级/90级/130级简易装备")

            # 处理套装效果筛选逻辑
            exclude_suit_effect = []
            require_high_value_suits = False

            # 使用预定义的高价值套装和精确筛选套装
            high_value_suits = HIGH_VALUE_SUITS
            precise_filter_suits = PRECISE_FILTER_SUITS

            # 检查目标装备的套装类型
            target_has_high_value_suits = False
            target_has_precise_filter_suits = False

            # 处理suit_effect：尝试转换为数字，如果失败则保持原值
            suit_effect_value = None
            if suit_effect:
                try:
                    suit_effect_value = int(suit_effect)
                except (ValueError, TypeError):
                    # 转换失败（可能是pet_equip的字符串套装），保持原值
                    suit_effect_value = suit_effect

            if suit_effect_value:
                # 检查是否包含高价值套装（只对数字套装有效）
                if isinstance(suit_effect_value, int) and suit_effect_value in high_value_suits:
                    target_has_high_value_suits = True
                # 检查是否包含精确筛选套装（只对数字套装有效）TODO: 需要优化需要优化需要优化需要优化需要优化需要优化需要优化
                elif isinstance(suit_effect_value, int) and suit_effect_value in precise_filter_suits:
                    target_has_precise_filter_suits = True

            # 套装筛选逻辑
            if target_has_high_value_suits:
                # 情况1：目标装备有高价值套装 → 强制只搜索高价值套装装备
                require_high_value_suits = True
                print(f"目标装备包含高价值套装 {suit_effect}，强制只搜索高价值套装装备")
            elif target_has_precise_filter_suits:
                # 情况2：目标装备有精确筛选套装 → 精确筛选该套装装备，排除其他高价值套装
                exclude_suit_effect = high_value_suits + \
                    [s for s in precise_filter_suits if s != suit_effect_value]
                print(f"目标装备包含精确筛选套装 {suit_effect}，将精确筛选该套装，排除其他精确筛选套装和高价值套装")
            else:
                # 情况3：目标装备没有套装或有其他套装 → 排除高价值套装和精确筛选套装
                exclude_suit_effect = high_value_suits + precise_filter_suits
                print(f"目标装备不包含高价值套装和精确筛选套装，将排除这些套装的装备")

            # 特技筛选逻辑
            exclude_high_value_special_skills = False
            if require_high_value_suits or (special_effect and len(special_effect) > 0 and not target_has_high_value_effects):
                # 如果强制高价值套装，或者有特效但不是高价值特效，则检查特技
                if special_skill and special_skill in LOW_VALUE_SPECIAL_SKILLS:
                    # 如果目标装备是低价值特技，则只能搜索无特技或低价值特技的装备
                    exclude_high_value_special_skills = True
                    print(f"目标装备是低价值特技 {special_skill}，将排除高价值特技装备")

            print(
                f"相似度筛选 - 重要特效: {filtered_special_effect}, 排除特效: {exclude_special_effect}")
            print(
                f"相似度筛选 - 排除套装: {exclude_suit_effect}, 强制高价值套装: {require_high_value_suits}")

            # 属性点加成分类，属性点加成类型一般成对出现；有三种情况:1、空白，即没有属性点；2、一个属性加成（正/负）；3、一对属性加成（两个正数，或者一正一负）；
            # 如果两个都是正数则是组合双加，如体质+10和耐力+10都是正数则是体耐；
            # 如果单种属性正数，如体质+10，则是体质；
            # 如果一个正数一个负数，如体质+15，敏捷-2，则是体质；
            # 分四个聚类
            # 1."体质", "体耐",
            # 2."魔力", "魔体","魔耐","魔敏",
            # 3."耐力",
            # 4."敏捷","敏体","敏耐",
            # 5."力量", "力体","力魔","力耐","力敏"

            # 调用基础数据获取方法（应用业务规则）
            market_data = self.get_market_data_with_business_rules(
                target_features=target_features,
                special_effect=filtered_special_effect,
                exclude_special_effect=exclude_special_effect,
                exclude_suit_effect=exclude_suit_effect if exclude_suit_effect else None,
                exclude_high_value_simple_equips=exclude_high_value_simple_equips,
                require_high_value_suits=require_high_value_suits,
                exclude_high_value_special_skills=exclude_high_value_special_skills,
                limit=2000  # 相似度计算需要更多数据
            )

            return market_data

        except Exception as e:
            self.logger.error(f"获取相似度计算市场数据失败: {e}")
            return pd.DataFrame()

    def refresh_full_cache(self) -> bool:
        """手动刷新全量缓存"""
        print("🔄 手动刷新装备全量缓存...")
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
            print("装备缓存设置为永不过期模式（仅手动刷新）")
        else:
            print(f"装备缓存设置为 {hours} 小时自动过期")
    
    def manual_refresh(self) -> bool:
        """
        手动刷新缓存（显式调用）
        """
        print(" 用户手动刷新装备缓存")
        return self.refresh_full_cache()
    
    def incremental_update(self, last_update_time: Optional[datetime] = None) -> bool:
        """
        增量更新缓存数据 - 先操作内存缓存，再同步到Redis
        
        Args:
            last_update_time: 上次更新时间，如果为None则从缓存元数据获取
            
        Returns:
            bool: 是否更新成功
        """
        try:
            print("🔄 开始增量更新装备缓存...")
            
            if not self.redis_cache:
                print(" Redis不可用，无法进行增量更新")
                return False
            
            # 获取上次更新时间
            if last_update_time is None:
                last_update_time = self._get_last_cache_update_time()
                if last_update_time is None:
                    print(" 无法获取上次更新时间，将进行全量刷新")
                    return self.refresh_full_cache()
            
            print(f"📅 上次更新时间: {last_update_time}")
            
            # 查询新增或更新的数据
            new_data = self._get_incremental_data_from_mysql(last_update_time)
            
            if new_data.empty:
                print(" 没有新数据需要更新")
                return True
            
            print(f" 发现 {len(new_data)} 条新数据")
            
            # 优先从内存缓存获取现有数据
            existing_data = self._get_existing_data_from_memory()
            if existing_data is None or existing_data.empty:
                print(" 内存缓存为空，尝试从Redis获取")
                existing_data = self._get_full_data_from_redis()
                if existing_data is None or existing_data.empty:
                    print(" Redis缓存也为空，将进行全量刷新")
                    return self.refresh_full_cache()
                # 将Redis数据加载到内存缓存
                self._full_data_cache = existing_data
                print(" 已将Redis数据加载到内存缓存")
            
            print(f" 现有内存缓存数据: {len(existing_data)} 条")
            
            # 合并数据到内存缓存
            merged_data = self._merge_incremental_data(existing_data, new_data)
            
            # 更新内存缓存
            self._full_data_cache = merged_data
            print(f" 内存缓存更新完成，总数据量: {len(merged_data)} 条")
            
            # 同步到Redis缓存
            success = self._sync_memory_cache_to_redis(merged_data)
            
            if success:
                print(f" 增量更新完成，数据已同步到Redis")
                # 更新缓存元数据中的最后更新时间
                self._update_cache_metadata(merged_data)
                return True
            else:
                print(" Redis同步失败，但内存缓存已更新")
                return False
                
        except Exception as e:
            self.logger.error(f"增量更新失败: {e}")
            print(f" 增量更新异常: {e}")
            return False
    
    def _get_last_cache_update_time(self) -> Optional[datetime]:
        """
        获取缓存中记录的最后更新时间 - 优先从内存缓存获取
        
        Returns:
            Optional[datetime]: 最后更新时间，如果不存在则返回None
        """
        try:
            # 优先从内存缓存获取最后更新时间
            memory_data = self._get_existing_data_from_memory()
            if memory_data is not None and not memory_data.empty and 'update_time' in memory_data.columns:
                # 确保update_time是datetime类型
                if memory_data['update_time'].dtype == 'object':
                    memory_data['update_time'] = pd.to_datetime(memory_data['update_time'])
                
                max_time = memory_data['update_time'].max()
                if pd.notna(max_time):
                    print(f"📅 从内存缓存获取最后更新时间: {max_time}")
                    return max_time.to_pydatetime()
            
            # 如果内存缓存中没有数据，尝试从Redis获取
            if not self.redis_cache:
                return None
            
            print("📅 内存缓存为空，尝试从Redis获取最后更新时间...")
            
            # 从缓存元数据获取最后更新时间
            metadata = self.redis_cache.get(f"{self._full_cache_key}:meta")
            if metadata and 'last_update_time' in metadata:
                last_time = datetime.fromisoformat(metadata['last_update_time'])
                print(f"📅 从Redis元数据获取最后更新时间: {last_time}")
                return last_time
            
            # 如果元数据中没有，尝试从数据中获取最新的update_time
            cached_data = self.redis_cache.get_chunked_data(self._full_cache_key)
            if cached_data is not None and not cached_data.empty and 'update_time' in cached_data.columns:
                # 确保update_time是datetime类型
                if cached_data['update_time'].dtype == 'object':
                    cached_data['update_time'] = pd.to_datetime(cached_data['update_time'])
                
                max_time = cached_data['update_time'].max()
                if pd.notna(max_time):
                    print(f"📅 从Redis数据获取最后更新时间: {max_time}")
                    return max_time.to_pydatetime()
            
            print("📅 未找到最后更新时间")
            return None
            
        except Exception as e:
            self.logger.warning(f"获取最后更新时间失败: {e}")
            return None
    
    def _get_incremental_data_from_mysql(self, last_update_time: datetime) -> pd.DataFrame:
        """
        从MySQL获取增量数据
        
        Args:
            last_update_time: 上次更新时间
            
        Returns:
            pd.DataFrame: 增量数据
        """
        try:
            from src.database import db
            from src.models.equipment import Equipment
            from flask import current_app
            from src.app import create_app
            
            # 确保在Flask应用上下文中
            if not current_app:
                app = create_app()
                with app.app_context():
                    return self._get_incremental_data_from_mysql(last_update_time)
            
            # 查询自上次更新以来的新数据
            required_fields = [
                Equipment.equip_level, Equipment.kindid, Equipment.init_damage, Equipment.init_damage_raw,
                Equipment.all_damage, Equipment.init_wakan, Equipment.init_defense, Equipment.init_hp,
                Equipment.init_dex, Equipment.mingzhong, Equipment.shanghai, Equipment.addon_tizhi,
                Equipment.addon_liliang, Equipment.addon_naili, Equipment.addon_minjie, Equipment.addon_lingli,
                Equipment.addon_moli, Equipment.agg_added_attrs, Equipment.gem_value, Equipment.gem_level,
                Equipment.special_skill, Equipment.special_effect, Equipment.suit_effect, Equipment.large_equip_desc,
                # 灵饰特征提取器需要的字段
                Equipment.damage, Equipment.defense, Equipment.magic_damage, Equipment.magic_defense,
                Equipment.fengyin, Equipment.anti_fengyin, Equipment.speed,
                # 召唤兽装备特征提取器需要的字段
                Equipment.fangyu, Equipment.qixue, Equipment.addon_fali, Equipment.xiang_qian_level, Equipment.addon_status,
                # 基础字段
                Equipment.equip_sn, Equipment.price, Equipment.server_name, Equipment.update_time
            ]
            
            query = db.session.query(*required_fields).filter(
                Equipment.update_time > last_update_time
            ).order_by(Equipment.update_time.desc())
            
            equipments = query.all()
            
            if not equipments:
                return pd.DataFrame()
            
            # 转换为DataFrame
            field_names = [
                'equip_level', 'kindid', 'init_damage', 'init_damage_raw', 'all_damage',
                'init_wakan', 'init_defense', 'init_hp', 'init_dex', 'mingzhong', 'shanghai',
                'addon_tizhi', 'addon_liliang', 'addon_naili', 'addon_minjie', 'addon_lingli', 'addon_moli',
                'agg_added_attrs', 'gem_value', 'gem_level', 'special_skill', 'special_effect', 'suit_effect',
                'large_equip_desc',
                # 灵饰特征提取器需要的字段
                'damage', 'defense', 'magic_damage', 'magic_defense', 'fengyin', 'anti_fengyin', 'speed',
                # 召唤兽装备特征提取器需要的字段
                'fangyu', 'qixue', 'addon_fali', 'xiang_qian_level', 'addon_status',
                # 基础字段
                'equip_sn', 'price', 'server_name', 'update_time'
            ]
            
            data_list = []
            for equipment_tuple in equipments:
                equipment_dict = {}
                for i, value in enumerate(equipment_tuple):
                    field_name = field_names[i]
                    if hasattr(value, 'isoformat'):  # datetime对象
                        equipment_dict[field_name] = value.isoformat()
                    else:
                        equipment_dict[field_name] = value
                data_list.append(equipment_dict)
            
            df = pd.DataFrame(data_list)
            print(f"从MySQL获取增量数据: {len(df)} 条")
            return df
            
        except Exception as e:
            self.logger.error(f"获取增量数据失败: {e}")
            return pd.DataFrame()
    
    def _merge_incremental_data(self, existing_data: pd.DataFrame, new_data: pd.DataFrame) -> pd.DataFrame:
        """
        合并现有数据和增量数据
        
        Args:
            existing_data: 现有缓存数据
            new_data: 新增数据
            
        Returns:
            pd.DataFrame: 合并后的数据
        """
        try:
            # 确保两个DataFrame的列顺序一致
            if not existing_data.empty and not new_data.empty:
                # 确保列顺序一致
                new_data = new_data.reindex(columns=existing_data.columns, fill_value=None)
            
            # 合并数据，新数据会覆盖相同equip_sn的旧数据
            if existing_data.empty:
                merged_data = new_data
            elif new_data.empty:
                merged_data = existing_data
            else:
                # 使用equip_sn作为主键进行合并
                # 先删除现有数据中与新数据重复的记录
                existing_data = existing_data[~existing_data['equip_sn'].isin(new_data['equip_sn'])]
                # 然后合并
                merged_data = pd.concat([existing_data, new_data], ignore_index=True)
            
            print(f"数据合并完成: 现有 {len(existing_data)} 条 + 新增 {len(new_data)} 条 = 总计 {len(merged_data)} 条")
            return merged_data
            
        except Exception as e:
            self.logger.error(f"合并数据失败: {e}")
            return existing_data
    
    def _get_existing_data_from_memory(self) -> Optional[pd.DataFrame]:
        """
        从内存缓存获取现有数据
        
        Returns:
            Optional[pd.DataFrame]: 内存缓存中的数据，如果不存在则返回None
        """
        try:
            if self._full_data_cache is not None and not self._full_data_cache.empty:
                return self._full_data_cache
            return None
        except Exception as e:
            self.logger.warning(f"获取内存缓存数据失败: {e}")
            return None
    
    def _sync_memory_cache_to_redis(self, data: pd.DataFrame) -> bool:
        """
        将内存缓存数据同步到Redis
        
        Args:
            data: 要同步的数据
            
        Returns:
            bool: 是否同步成功
        """
        try:
            if not self.redis_cache or data.empty:
                print(" Redis不可用或数据为空，跳过同步")
                return True
            
            # 更新Redis缓存
            chunk_size = 500
            ttl_seconds = None if self._cache_ttl_hours == -1 else self._cache_ttl_hours * 3600
            
            success = self.redis_cache.set_chunked_data(
                base_key=self._full_cache_key,
                data=data,
                chunk_size=chunk_size,
                ttl=ttl_seconds
            )
            
            if success:
                print(" 内存缓存已同步到Redis")
                return True
            else:
                print(" 同步到Redis失败")
                return False
                
        except Exception as e:
            self.logger.error(f"同步到Redis失败: {e}")
            return False

    def _update_cache_with_merged_data(self, merged_data: pd.DataFrame) -> bool:
        """
        使用合并后的数据更新缓存（兼容旧方法）
        
        Args:
            merged_data: 合并后的数据
            
        Returns:
            bool: 是否更新成功
        """
        try:
            if merged_data.empty:
                print(" 合并后数据为空，跳过缓存更新")
                return True
            
            # 更新内存缓存
            self._full_data_cache = merged_data
            
            # 同步到Redis缓存
            return self._sync_memory_cache_to_redis(merged_data)
                
        except Exception as e:
            self.logger.error(f"更新缓存失败: {e}")
            return False
    
    def _update_cache_metadata(self, merged_data: pd.DataFrame):
        """
        更新缓存元数据
        
        Args:
            merged_data: 合并后的数据
        """
        try:
            if not self.redis_cache or merged_data.empty:
                return
            
            # 更新元数据
            metadata = {
                'total_rows': len(merged_data),
                'created_at': datetime.now().isoformat(),
                'last_update_time': datetime.now().isoformat(),
                'total_chunks': (len(merged_data) + 499) // 500,  # 假设chunk_size=500
                'chunk_size': 500
            }
            
            self.redis_cache.set(f"{self._full_cache_key}:meta", metadata)
            print(" 缓存元数据更新成功")
            
        except Exception as e:
            self.logger.warning(f"更新缓存元数据失败: {e}")
    
    def get_incremental_update_status(self) -> Dict[str, Any]:
        """
        获取增量更新状态信息 - 优先从内存缓存获取
        
        Returns:
            Dict: 增量更新状态信息
        """
        try:
            status = {
                'last_update_time': None,
                'mysql_latest_time': None,
                'has_new_data': False,
                'new_data_count': 0,
                'memory_cache_size': 0,
                'data_source': 'unknown'
            }
            
            # 优先从内存缓存获取状态信息
            memory_data = self._get_existing_data_from_memory()
            if memory_data is not None and not memory_data.empty:
                status['memory_cache_size'] = len(memory_data)
                status['data_source'] = 'memory'
                print(f" 从内存缓存获取状态信息，数据量: {len(memory_data)} 条")
            else:
                status['data_source'] = 'redis'
                print(" 内存缓存为空，从Redis获取状态信息")
            
            # 获取缓存中的最后更新时间（现在会优先从内存缓存获取）
            last_update_time = self._get_last_cache_update_time()
            if last_update_time:
                status['last_update_time'] = last_update_time.isoformat()
            
            # 获取MySQL中的最新时间
            mysql_latest_time = self._get_mysql_latest_update_time()
            if mysql_latest_time:
                status['mysql_latest_time'] = mysql_latest_time.isoformat()
                
                # 检查是否有新数据
                if last_update_time and mysql_latest_time > last_update_time:
                    status['has_new_data'] = True
                    # 获取新数据数量（这里只是估算，实际数量需要查询）
                    status['new_data_count'] = self._estimate_new_data_count(last_update_time)
                    print(f" 检测到新数据: {status['new_data_count']} 条")
                else:
                    print(" 没有新数据需要更新")
            
            return status
            
        except Exception as e:
            self.logger.error(f"获取增量更新状态失败: {e}")
            return {'error': str(e)}
    
    def _get_mysql_latest_update_time(self) -> Optional[datetime]:
        """
        获取MySQL中的最新更新时间
        
        Returns:
            Optional[datetime]: 最新更新时间
        """
        try:
            from src.database import db
            from src.models.equipment import Equipment
            from flask import current_app
            from src.app import create_app
            
            # 确保在Flask应用上下文中
            if not current_app:
                app = create_app()
                with app.app_context():
                    return self._get_mysql_latest_update_time()
            
            # 查询最新的update_time
            latest_time = db.session.query(func.max(Equipment.update_time)).scalar()
            return latest_time
            
        except Exception as e:
            self.logger.error(f"获取MySQL最新时间失败: {e}")
            return None
    
    def _estimate_new_data_count(self, last_update_time: datetime) -> int:
        """
        估算新数据数量
        
        Args:
            last_update_time: 上次更新时间
            
        Returns:
            int: 估算的新数据数量
        """
        try:
            from src.database import db
            from src.models.equipment import Equipment
            from flask import current_app
            from src.app import create_app
            
            # 确保在Flask应用上下文中
            if not current_app:
                app = create_app()
                with app.app_context():
                    return self._estimate_new_data_count(last_update_time)
            
            # 查询新数据数量
            count = db.session.query(Equipment).filter(
                Equipment.update_time > last_update_time
            ).count()
            
            return count
            
        except Exception as e:
            self.logger.error(f"估算新数据数量失败: {e}")
            return 0
    
    
    def auto_incremental_update(self) -> bool:
        """
        自动检测并执行增量更新
        
        Returns:
            bool: 是否更新成功
        """
        try:
            print("🤖 开始自动增量更新检测...")
            
            # 获取增量更新状态
            status = self.get_incremental_update_status()
            
            if 'error' in status:
                print(f" 获取增量更新状态失败: {status['error']}")
                return False
            
            if not status.get('has_new_data', False):
                print(" 没有新数据需要更新")
                return True
            
            new_data_count = status.get('new_data_count', 0)
            print(f" 检测到 {new_data_count} 条新数据，开始增量更新...")
            
            # 执行增量更新
            return self.incremental_update()
            
        except Exception as e:
            self.logger.error(f"自动增量更新失败: {e}")
            print(f" 自动增量更新异常: {e}")
            return False
    
    def force_incremental_update(self) -> bool:
        """
        强制增量更新（忽略缓存状态检查）
        
        Returns:
            bool: 是否更新成功
        """
        try:
            print("💪 开始强制增量更新...")
            
            # 获取MySQL中的最新时间
            mysql_latest_time = self._get_mysql_latest_update_time()
            if mysql_latest_time is None:
                print(" 无法获取MySQL最新时间")
                return False
            
            # 获取缓存中的最后更新时间
            last_update_time = self._get_last_cache_update_time()
            if last_update_time is None:
                print(" 无法获取缓存最后更新时间，将进行全量刷新")
                return self.refresh_full_cache()
            
            # 如果MySQL时间早于缓存时间，说明没有新数据
            if mysql_latest_time <= last_update_time:
                print(" MySQL数据没有更新，无需增量更新")
                return True
            
            # 执行增量更新
            return self.incremental_update(last_update_time)
            
        except Exception as e:
            self.logger.error(f"强制增量更新失败: {e}")
            print(f" 强制增量更新异常: {e}")
            return False

    def get_cache_status(self) -> Dict[str, Any]:
        """获取缓存状态信息"""
        try:
            # 获取MySQL装备数据总数
            mysql_count = self._get_mysql_equipments_count()
            
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
                print("已清空装备数据缓存")

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

    def _should_filter_suit_effect(self, suit_effect: Union[int, str]) -> bool:
        """
        判断套装效果是否应该被用于筛选

        业务规则：只有特定的高价值套装效果才用于精确筛选，
        其他套装效果在相似度计算时进行聚类处理

        Args:
            suit_effect: 套装效果ID（数字或数字字符串，pet_equip可能是纯字符串）

        Returns:
            bool: 是否应该筛选此套装效果
        """
        # 允许精确筛选的套装效果：定心术、变身术、碎星诀、天神护体、满天花雨、浪涌
        allowed_suit_effects = PRECISE_FILTER_SUITS

        # 尝试转换为数字进行比较
        try:
            suit_effect_num = int(suit_effect)
            return suit_effect_num in allowed_suit_effects
        except (ValueError, TypeError):
            # 转换失败（可能是pet_equip的字符串套装），不进行精确筛选
            return False

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

    def _classify_addon_attributes(self, addon_minjie: int = 0, addon_liliang: int = 0,
                                   addon_naili: int = 0, addon_tizhi: int = 0,
                                   addon_moli: int = 0) -> str:
        """
        根据装备的附加属性分类
        #属性点加成分类，属性点加成类型一般成对出现；
        # 如果两个都是正数则是组合双加，如体质+10和耐力+10都是正数则是体耐；
        # 如果单种属性正数，如体质+10，则是体质；
        # 如果一个正数一个负数，如体质+15，敏捷-2，则是体质；
        # 分四个聚类
        # 1."体质", "体耐",
        # 2."魔力", "魔体","魔耐","魔敏",
        # 3."耐力",
        # 4."敏捷","敏体","敏耐",
        # 5."力量", "力体","力魔","力耐","力敏"

        Args:
            addon_minjie: 敏捷加成
            addon_liliang: 力量加成
            addon_naili: 耐力加成
            addon_tizhi: 体质加成
            addon_moli: 魔力加成

        Returns:
            str: 属性分类类型
        """
        # 统计正数属性
        positive_attrs = {}
        if addon_minjie > 0:
            positive_attrs['敏捷'] = addon_minjie
        if addon_liliang > 0:
            positive_attrs['力量'] = addon_liliang
        if addon_naili > 0:
            positive_attrs['耐力'] = addon_naili
        if addon_tizhi > 0:
            positive_attrs['体质'] = addon_tizhi
        if addon_moli > 0:
            positive_attrs['魔力'] = addon_moli

        # 如果没有正数属性
        if not positive_attrs:
            return "无属性"

        # 如果只有一个正数属性
        if len(positive_attrs) == 1:
            attr_name = list(positive_attrs.keys())[0]
            return attr_name

        # 如果有两个正数属性，按组合规则分类
        if len(positive_attrs) == 2:
            attr_names = sorted(positive_attrs.keys())

            # 体质相关组合
            if '体质' in attr_names and '耐力' in attr_names:
                return "体耐"
            elif '体质' in attr_names and '敏捷' in attr_names:
                return "敏体"
            elif '体质' in attr_names and '力量' in attr_names:
                return "力体"
            elif '体质' in attr_names and '魔力' in attr_names:
                return "魔体"

            # 魔力相关组合
            elif '魔力' in attr_names and '耐力' in attr_names:
                return "魔耐"
            elif '魔力' in attr_names and '敏捷' in attr_names:
                return "魔敏"
            elif '魔力' in attr_names and '力量' in attr_names:
                return "力魔"

            # 敏捷相关组合
            elif '敏捷' in attr_names and '耐力' in attr_names:
                return "敏耐"
            elif '敏捷' in attr_names and '力量' in attr_names:
                return "力敏"

            # 力量耐力组合
            elif '力量' in attr_names and '耐力' in attr_names:
                return "力耐"

        # 多于两个属性或其他情况，返回主属性（数值最大的）
        if positive_attrs:
            main_attr = max(positive_attrs.items(), key=lambda x: x[1])[0]
            return main_attr

        return "无属性"

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
            
            # 直接使用set_chunked_data重新存储到正式键
            success = self.redis_cache.set_chunked_data(
                base_key=official_key,
                data=df,
                chunk_size=chunk_size,
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

    def _rename_temp_cache_to_official(self, temp_key: str, official_key: str) -> bool:
        """
        将临时缓存重命名为正式缓存（无缝切换）
        
        Args:
            temp_key: 临时缓存键名
            official_key: 正式缓存键名
            
        Returns:
            bool: 是否重命名成功
        """
        try:
            # 获取临时缓存的所有键
            temp_keys = self.redis_cache.client.keys(f"{temp_key}:*")
            if not temp_keys:
                print(f" 临时缓存键不存在: {temp_key}")
                return False
            
            print(f"找到 {len(temp_keys)} 个临时缓存键，开始重命名...")
            
            # 使用Redis管道批量重命名
            pipe = self.redis_cache.client.pipeline()
            
            for temp_key_full in temp_keys:
                # 将临时键名替换为正式键名
                official_key_full = temp_key_full.decode('utf-8').replace(temp_key, official_key)
                
                # 获取临时键的值
                value = self.redis_cache.client.get(temp_key_full)
                if value is not None:
                    # 设置到正式键
                    pipe.set(official_key_full, value)
                    # 删除临时键
                    pipe.delete(temp_key_full)
                    print(f"重命名: {temp_key_full.decode('utf-8')} -> {official_key_full}")
            
            # 执行管道操作
            results = pipe.execute()
            
            # 检查结果
            success_count = sum(1 for result in results if result is True)
            total_operations = len(results) // 2  # 每个键有set和delete两个操作
            
            print(f"重命名完成: {success_count}/{total_operations} 个键操作成功")
            
            if success_count == total_operations:
                print(" 所有临时缓存键重命名成功")
                return True
            else:
                print(f" 部分重命名失败: {success_count}/{total_operations}")
                return False
                
        except Exception as e:
            print(f" 重命名临时缓存失败: {e}")
            return False

    def _get_target_addon_classification(self, target_features: Dict[str, Any]) -> str:
        """
        获取目标装备的属性分类

        Args:
            target_features: 目标装备特征

        Returns:
            str: 属性分类类型
        """
        addon_minjie = target_features.get('addon_minjie', 0)
        addon_liliang = target_features.get('addon_liliang', 0)
        addon_naili = target_features.get('addon_naili', 0)
        addon_tizhi = target_features.get('addon_tizhi', 0)
        addon_moli = target_features.get('addon_moli', 0)

        return self._classify_addon_attributes(
            addon_minjie, addon_liliang, addon_naili, addon_tizhi, addon_moli
        )

    def get_market_data_with_addon_classification(self,
                                                  target_features: Dict[str, Any],
                                                  **kwargs) -> pd.DataFrame:
        """
        根据属性加成分类获取市场数据

        自动按照装备属性分类过滤市场数据，只保留同类属性装备

        Args:
            target_features: 目标装备特征
            **kwargs: 其他查询参数

        Returns:
            市场数据DataFrame，包含属性分类信息，已按同类属性过滤
        """
        try:
            # 获取基础市场数据
            market_data = self.get_market_data_for_similarity(target_features)
            if market_data.empty:
                return market_data

            # 获取目标装备的属性分类
            target_classification = self._get_target_addon_classification(
                target_features)
            print(f"目标装备属性分类: {target_classification}")

            # 为市场数据添加属性分类
            market_data['addon_classification'] = market_data.apply(
                lambda row: self._classify_addon_attributes(
                    row.get('addon_minjie', 0),
                    row.get('addon_liliang', 0),
                    row.get('addon_naili', 0),
                    row.get('addon_tizhi', 0),
                    row.get('addon_moli', 0)
                ), axis=1
            )

            # 始终按属性分类过滤（除非目标装备是无属性）
            if target_classification != "无属性":
                # 定义同类属性分组
                classification_groups = {
                    "体质系": ["体质", "体耐"],
                    "魔力系": ["魔力", "魔体", "魔耐", "魔敏"],
                    "耐力系": ["耐力"],
                    "敏捷系": ["敏捷", "敏体", "敏耐"],
                    "力量系": ["力量", "力体", "力魔", "力耐", "力敏"]
                }

                # 找到目标装备所属的分组
                target_group = None
                for group_name, classifications in classification_groups.items():
                    if target_classification in classifications:
                        target_group = classifications
                        break

                if target_group:
                    # 过滤同类属性装备（保留无属性装备作为参考）
                    before_filter_count = len(market_data)
                    market_data = market_data[
                        (market_data['addon_classification'].isin(target_group)) |
                        (market_data['addon_classification'] == "无属性")
                    ]
                    after_filter_count = len(market_data)

                    print(
                        f"属性分类过滤: {target_classification} -> 同类属性 {target_group}")
                    print(
                        f"过滤结果: {before_filter_count} -> {after_filter_count} 条数据")
                else:
                    print(f"未找到属性分类 {target_classification} 对应的分组，不进行过滤")
            else:
                print(f"目标装备无属性，不进行属性分类过滤")

            return market_data

        except Exception as e:
            self.logger.error(f"按属性分类获取市场数据失败: {e}")
            return pd.DataFrame()
