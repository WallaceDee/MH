from datetime import datetime
from typing import Dict, Any, List, Optional, Union, Tuple
import logging
import numpy as np
import pandas as pd

# 导入灵饰优先级配置
from src.evaluator.constants.lingshi_priorities import (
    RING_EARRING_PRIORITY, BRACELET_ACCESSORY_PRIORITY,
    get_priority_by_attr_name
)

from src.evaluator.feature_extractor.lingshi_feature_extractor import LingshiFeatureExtractor
from src.database import db
from src.models.equipment import Equipment
from sqlalchemy import and_, or_, func, text



class LingshiMarketDataCollector:
    """灵饰市场数据采集器 - 从数据库中获取和处理灵饰市场数据"""

    def __init__(self):
        """
        初始化灵饰市场数据采集器
        """
        self.feature_extractor = LingshiFeatureExtractor()
        self.logger = logging.getLogger(__name__)
        self.target_features = None  # 保存目标特征，用于传递target_match_attrs
        
        # 获取装备数据采集器实例，共享缓存
        self.equip_collector = None
        self._init_equip_collector()
        
        # 缓存过滤后的灵饰数据，避免重复读取和过滤
        self._cached_lingshi_data = None
        self._cache_timestamp = None

        print(f"灵饰数据采集器初始化，使用MySQL数据库")
    
    def _init_equip_collector(self):
        """初始化装备数据采集器实例"""
        try:
            from src.evaluator.mark_anchor.equip.equip_market_data_collector import EquipMarketDataCollector
            self.equip_collector = EquipMarketDataCollector()
            print("✅ 成功获取装备数据采集器实例，可共享缓存")
        except Exception as e:
            self.logger.warning(f"获取装备数据采集器实例失败: {e}")
            print(f"⚠️ 无法共享装备数据采集器缓存: {e}")
    
    def _get_shared_cache_data(self, kindid: Optional[int] = None) -> Optional[pd.DataFrame]:
        """
        从装备数据采集器获取共享缓存数据，优先使用实例缓存
        
        Args:
            kindid: 灵饰类型ID筛选 (61:戒指, 62:耳饰, 63:手镯, 64:佩饰)
            
        Returns:
            过滤后的灵饰数据DataFrame，如果缓存不可用则返回None
        """
        if not self.equip_collector:
            return None
            
        try:
            # 检查实例缓存是否有效
            if self._cached_lingshi_data is not None:
                print(f"✅ 使用实例缓存的灵饰数据，共 {len(self._cached_lingshi_data)} 条")
                
                # 如果指定了kindid，进一步过滤
                if kindid is not None:
                    filtered_data = self._cached_lingshi_data[self._cached_lingshi_data['kindid'] == kindid]
                    if not filtered_data.empty:
                        print(f"✅ 按kindid={kindid}过滤后得到 {len(filtered_data)} 条灵饰数据")
                        return filtered_data
                    else:
                        print(f"实例缓存中没有找到kindid={kindid}的灵饰数据")
                        return None
                else:
                    return self._cached_lingshi_data
            
            # 实例缓存为空，从装备数据采集器获取全量缓存
            full_data = self.equip_collector._get_full_data_from_redis()
            
            if full_data is None or full_data.empty:
                print("装备数据采集器缓存为空，无法共享")
                return None
            
            # 过滤出灵饰数据 (kindid: 61-64) 并保存到实例缓存
            self._cached_lingshi_data = full_data[full_data['kindid'].isin([61, 62, 63, 64])].copy()
            self._cache_timestamp = datetime.now()
            
            if not self._cached_lingshi_data.empty:
                print(f"✅ 从装备数据采集器获取并缓存 {len(self._cached_lingshi_data)} 条灵饰数据")
                
                # 如果指定了kindid，进一步过滤
                if kindid is not None:
                    filtered_data = self._cached_lingshi_data[self._cached_lingshi_data['kindid'] == kindid]
                    if not filtered_data.empty:
                        print(f"✅ 按kindid={kindid}过滤后得到 {len(filtered_data)} 条灵饰数据")
                        return filtered_data
                    else:
                        print(f"缓存中没有找到kindid={kindid}的灵饰数据")
                        return None
                else:
                    return self._cached_lingshi_data
            else:
                print("装备数据采集器缓存中没有找到灵饰数据")
                return None
                
        except Exception as e:
            self.logger.warning(f"获取共享缓存数据失败: {e}")
            print(f"⚠️ 共享缓存获取失败: {e}")
            return None

    def clear_cache(self):
        """清除实例缓存，强制下次重新从装备数据采集器获取数据"""
        self._cached_lingshi_data = None
        self._cache_timestamp = None
        print("✅ 已清除灵饰数据实例缓存")

    def get_market_data(self,
                        kindid: Optional[int] = None,
                        level_range: Optional[Tuple[int, int]] = None,
                        main_attr: Optional[str] = None,
                        attrs: Optional[List[Dict[str, Any]]] = None,
                        is_super_simple: Optional[bool] = None,
                        price_range: Optional[Tuple[float, float]] = None,
                        server: Optional[str] = None,
                        limit: int = 1000,
                        use_shared_cache: bool = True) -> pd.DataFrame:
        """
        获取市场灵饰数据，优先从装备数据采集器的共享缓存获取数据

        Args:
            kindid: 灵饰类型ID筛选 (61:戒指, 62:耳饰, 63:手镯, 64:佩饰)
            main_attr: 主属性(damage、defense、magic_damage、magic_defense、fengyin、anti_fengyin、speed)
            attrs: 附加属性 List[Dict] - 附加属性对象列表，最多3个
                每个对象包含:
                - attr_type: str - 属性类型，如"伤害"、"法术伤害"
                - attr_value: int - 属性数值
            level_range: 等级范围 (min_level, max_level)
            price_range: 价格范围 (min_price, max_price)
            server: 服务器筛选
            is_super_simple: 是否超级简易筛选 (基于special_effect=="[1]"判断)
            limit: 返回数据条数限制
            use_shared_cache: 是否使用共享缓存

        Returns:
            灵饰市场数据DataFrame
        """
        try:
            import time
            start_time = time.time()
            
            # 优先从共享缓存获取数据
            if use_shared_cache:
                cached_data = self._get_shared_cache_data(kindid)
                
                if cached_data is not None and not cached_data.empty:
                    # 对缓存数据进行进一步筛选
                    filtered_data = self._filter_cached_data(
                        cached_data,
                        level_range=level_range,
                        main_attr=main_attr,
                        is_super_simple=is_super_simple,
                        price_range=price_range,
                        server=server,
                        limit=limit
                    )
                    
                    # 附加属性筛选：根据attr_type进行筛选
                    if attrs is not None and len(attrs) > 0:
                        filtered_data = self._filter_by_attrs(filtered_data, attrs)
                    
                    elapsed_time = time.time() - start_time
                    print(f"✅ 从共享缓存获取灵饰数据完成，耗时: {elapsed_time:.3f}秒，返回: {len(filtered_data)} 条数据")
                    return filtered_data
            
            # 降级到MySQL查询
            print("使用MySQL数据库查询灵饰数据（降级模式）...")
            return self._get_market_data_from_mysql(
                kindid=kindid,
                level_range=level_range,
                main_attr=main_attr,
                is_super_simple=is_super_simple,
                price_range=price_range,
                server=server,
                limit=limit,
                attrs=attrs
            )
            
        except Exception as e:
            self.logger.error(f"获取灵饰市场数据失败: {e}")
            print(f"获取灵饰市场数据异常: {e}")
            return pd.DataFrame()
    
    def _filter_cached_data(self, cached_data: pd.DataFrame, 
                           level_range: Optional[Tuple[int, int]] = None,
                           main_attr: Optional[str] = None,
                           is_super_simple: Optional[bool] = None,
                           price_range: Optional[Tuple[float, float]] = None,
                           server: Optional[str] = None,
                           limit: int = 1000) -> pd.DataFrame:
        """
        对缓存数据进行筛选
        
        Args:
            cached_data: 缓存的数据
            level_range: 等级范围筛选
            main_attr: 主属性筛选
            is_super_simple: 超级简易筛选
            price_range: 价格范围筛选
            server: 服务器筛选
            limit: 数据条数限制
            
        Returns:
            筛选后的DataFrame
        """
        filtered_data = cached_data.copy()
        
        # 等级范围筛选
        if level_range is not None:
            min_level, max_level = level_range
            filtered_data = filtered_data[
                (filtered_data['equip_level'] >= min_level) & 
                (filtered_data['equip_level'] <= max_level)
            ]
        
        # 价格范围筛选
        if price_range is not None:
            min_price, max_price = price_range
            filtered_data = filtered_data[
                (filtered_data['price'] >= min_price) & 
                (filtered_data['price'] <= max_price)
            ]
        
        # 服务器筛选
        if server is not None:
            filtered_data = filtered_data[filtered_data['server_name'] == server]
        
        # 超级简易筛选
        if is_super_simple is not None:
            if is_super_simple:
                filtered_data = filtered_data[filtered_data['special_effect'] == "[1]"]
            else:
                filtered_data = filtered_data[
                    (filtered_data['special_effect'] != "[1]") | 
                    (filtered_data['special_effect'].isna())
                ]
        
        # 主属性筛选
        if main_attr is not None:
            valid_main_attrs = ['damage', 'defense', 'magic_damage', 'magic_defense', 'fengyin', 'anti_fengyin', 'speed']
            if main_attr in valid_main_attrs:
                filtered_data = filtered_data[filtered_data[main_attr] > 0]
            else:
                self.logger.warning(f"无效的主属性字段: {main_attr}, 支持的字段: {valid_main_attrs}")
        
        # 按更新时间排序并限制条数
        filtered_data = filtered_data.sort_values('update_time', ascending=False).head(limit)
        
        return filtered_data
    
    def _get_market_data_from_mysql(self,
                                   kindid: Optional[int] = None,
                                   level_range: Optional[Tuple[int, int]] = None,
                                   main_attr: Optional[str] = None,
                                   is_super_simple: Optional[bool] = None,
                                   price_range: Optional[Tuple[float, float]] = None,
                                   server: Optional[str] = None,
                                   limit: int = 1000,
                                   attrs: Optional[List[Dict[str, Any]]] = None) -> pd.DataFrame:
        """
        从MySQL数据库获取市场灵饰数据
        
        Args:
            参数同get_market_data方法
            
        Returns:
            灵饰市场数据DataFrame
        """
        try:
            # 构建SQLAlchemy查询
            query = db.session.query(Equipment)

            if kindid is not None:
                query = query.filter(Equipment.kindid == kindid)

            if level_range is not None:
                min_level, max_level = level_range
                query = query.filter(Equipment.equip_level.between(min_level, max_level))

            if price_range is not None:
                min_price, max_price = price_range
                query = query.filter(Equipment.price.between(min_price, max_price))

            if server is not None:
                query = query.filter(Equipment.server_name == server)

            if is_super_simple is not None:
                if is_super_simple:
                    query = query.filter(Equipment.special_effect == "[1]")
                else:
                    query = query.filter(
                        or_(
                            Equipment.special_effect != "[1]",
                            Equipment.special_effect.is_(None)
                        )
                    )

            # 主属性筛选：当传入main_attr时，筛选该属性值大于0的装备
            if main_attr is not None:
                # 验证主属性字段名是否有效
                valid_main_attrs = ['damage', 'defense', 'magic_damage', 'magic_defense', 'fengyin', 'anti_fengyin', 'speed']
                if main_attr in valid_main_attrs:
                    query = query.filter(getattr(Equipment, main_attr) > 0)
                else:
                    self.logger.warning(f"无效的主属性字段: {main_attr}, 支持的字段: {valid_main_attrs}")

            # 排序和限制
            query = query.order_by(Equipment.update_time.desc()).limit(limit)

            # 执行查询并转换为DataFrame
            equipments = query.all()
            
            if equipments:
                # 转换为字典列表
                data_list = []
                for equipment in equipments:
                    equipment_dict = {}
                    for column in equipment.__table__.columns:
                        value = getattr(equipment, column.name)
                        if hasattr(value, 'isoformat'):  # datetime对象
                            equipment_dict[column.name] = value.isoformat()
                        else:
                            equipment_dict[column.name] = value
                    data_list.append(equipment_dict)
                
                result_df = pd.DataFrame(data_list)
                
                # 去重
                result_df = result_df.drop_duplicates(subset=['equip_sn'], keep='first')
                
                # 附加属性筛选：根据attr_type进行筛选
                if attrs is not None and len(attrs) > 0:
                    result_df = self._filter_by_attrs(result_df, attrs)
                
                print(f"从MySQL数据库加载了 {len(result_df)} 条灵饰数据")
                return result_df
            else:
                print(f"从MySQL数据库查询到0条灵饰数据")
                return pd.DataFrame()

        except Exception as e:
            self.logger.error(f"查询灵饰数据失败: {e}")
            print(f"SQL执行异常: {e}")
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
        
        # 保存目标特征，供后续特征计算使用
        self.target_features = {'attrs': target_attrs}
        
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
        # 辅助系：固定伤害(S)、治疗能力(A)、速度(B)、封印命中等级(C)
        # 使用统一的灵饰属性优先级配置
        # 戒指/耳饰属性优先级：伤害(1)、物理暴击等级(2)、穿刺等级(3)、狂暴等级(4)、法术伤害(1)、法术暴击等级(2)、法术伤害结果(3)、固定伤害(1)、治疗能力(2)、封印命中等级(3)、速度(4)
        # 手镯/佩饰属性优先级：气血(1)、防御(1)、抵抗封印等级(2)、抗物理暴击(2)、格挡值(3)、法术防御(3)、抗法术暴击(4)、气血回复效果(4)
        
        # 根据目标属性数量确定匹配策略
        target_attr_count = len(target_attr_types)
        
        # 获取目标属性的优先级排序
        def get_priority_sorted_attrs(attr_types, equipment_type):
            """根据装备类型获取优先级排序的属性列表"""
            # 使用统一的优先级配置
            # 按优先级排序，优先级相同的保持原顺序
            sorted_attrs = sorted(attr_types, key=lambda x: get_priority_by_attr_name(x, equipment_type))
            return sorted_attrs
        
        # 根据目标属性数量确定匹配所需的属性
        def get_match_attrs(target_attrs, equipment_type):
            """根据目标属性数量和装备类型确定匹配所需的属性，返回(匹配属性列表, 未选中属性)"""
            if target_attr_count == 2:
                # 2条属性时，需要2条属性类型相同
                return list(target_attrs), None
            elif target_attr_count == 3:
                # 3条属性时，检查是否都相同
                unique_attrs = set(target_attrs)
                if len(unique_attrs) == 1:
                    # 3条属性都一样，必须3条匹配
                    return list(target_attrs), None
                else:
                    # 3条属性不全相同，优先选择重复的属性
                    from collections import Counter
                    attr_counter = Counter(target_attrs)
                    
                    # 如果有重复属性，优先选择重复最多的属性
                    if len(attr_counter) < len(target_attrs):
                        # 有重复属性，选择重复最多的属性
                        most_common_attr = attr_counter.most_common(1)[0][0]
                        # 如果重复属性有2个或以上，选择2个重复属性
                        if attr_counter[most_common_attr] >= 2:
                            # 选择2个重复属性，未选中的是其他属性
                            unmatched_attrs = [attr for attr in target_attrs if attr != most_common_attr]
                            return [most_common_attr, most_common_attr], unmatched_attrs[0] if unmatched_attrs else None
                        else:
                            # 重复属性只有1个，选择1个重复属性 + 1个其他属性
                            other_attrs = [attr for attr in target_attrs if attr != most_common_attr]
                            # 未选中的是其他属性中除了已选择的那一个
                            unmatched_attr = other_attrs[1] if len(other_attrs) > 1 else None
                            return [most_common_attr, other_attrs[0]], unmatched_attr
                    else:
                        # 没有重复属性，按优先级取2条
                        sorted_attrs = get_priority_sorted_attrs(target_attrs, equipment_type)
                        # 未选中的是排序后第3个属性
                        unmatched_attr = sorted_attrs[2] if len(sorted_attrs) > 2 else None
                        return sorted_attrs[:2], unmatched_attr
            else:
                # 灵饰最多只有3条属性，这里不应该到达
                raise ValueError(f"灵饰属性数量异常: {target_attr_count}，最多只能有3条属性")
        
        # 预先计算目标匹配属性，避免在循环中重复计算
        # 由于equipment_type在同类装备中是固定的，可以预先计算
        # 从第一行数据获取equipment_type，因为同类装备的equipment_type是固定的
        first_equipment_type = data_df.iloc[0].get('kindid', 0) if not data_df.empty else 0
        target_match_attrs, unmatched_attr = get_match_attrs(target_attr_types, first_equipment_type)
        print(f"预先计算目标匹配属性target_match_attrs {target_match_attrs}")
        print(f"预先计算未选中属性unmatched_attr {unmatched_attr}")
        
        # 将target_match_attrs信息添加到目标特征中，供后续特征计算使用
        if hasattr(self, 'target_features') and self.target_features:
            self.target_features['target_match_attrs'] = target_match_attrs
            self.target_features['attr_3_type'] = unmatched_attr
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
                        target_match_set = set(target_match_attrs)
                        if len(target_match_set.intersection(market_attr_set)) >= 2:
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
                        # 3条属性不全相同，优先选择重复的属性
                        # 使用计数方式，因为target_match_attrs可能包含重复属性
                        market_attr_counter = {}
                        for attr_type in market_attr_types:
                            market_attr_counter[attr_type] = market_attr_counter.get(attr_type, 0) + 1
                        
                        # 检查target_match_attrs中的每个属性是否在市场装备中存在
                        match_count = 0
                        for target_attr in target_match_attrs:
                            if market_attr_counter.get(target_attr, 0) > 0:
                                match_count += 1
                                # 减少计数，避免重复计算
                                market_attr_counter[target_attr] -= 1
                        
                        if match_count >= 2:
                            filtered_rows.append(row)
                else:
                    # 其他情况，使用交集匹配
                    market_attr_set = set(market_attr_types)
                    target_match_set = set(target_match_attrs)
                    common_attr_types = target_match_set.intersection(market_attr_set)
                    if len(common_attr_types) >= min(2, len(target_match_set)):
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
