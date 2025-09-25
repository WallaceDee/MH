import os
import sys
import pandas as pd
import logging
from typing import Dict, Any, List, Optional, Tuple
from datetime import datetime
import re

# 添加项目根目录到Python路径
from src.utils.project_path import get_project_root
project_root = get_project_root()
sys.path.insert(0, project_root)

# 导入装备类型常量
from src.evaluator.constants.equipment_types import PET_EQUIP_KINDID

# 导入特征提取器
try:
    from src.evaluator.feature_extractor.pet_equip_feature_extractor import PetEquipFeatureExtractor
    from src.database import db
    from src.models.equipment import Equipment
    from sqlalchemy import and_, or_, func, text
except ImportError:
    try:
        from src.evaluator.feature_extractor.pet_equip_feature_extractor import PetEquipFeatureExtractor
        from src.database import db
        from src.models.equipment import Equipment
        from sqlalchemy import and_, or_, func, text
    except ImportError:
        # 如果都导入失败，创建一个简单的占位符类
        class PetEquipFeatureExtractor:
            def __init__(self):
                pass
            
            def extract_features(self, pet_equip_data):
                return {}


class PetEquipMarketDataCollector:
    """召唤兽装备市场数据采集器 - 从数据库中获取和处理召唤兽装备市场数据"""

    def __init__(self):
        """
        初始化召唤兽装备市场数据采集器
        """
        self.feature_extractor = PetEquipFeatureExtractor()
        self.logger = logging.getLogger(__name__)
        
        # 获取装备数据采集器实例，共享缓存
        self.equip_collector = None
        self._init_equip_collector()
        
        # 缓存过滤后的宠物装备数据，避免重复读取和过滤
        self._cached_pet_equip_data = None
        self._cache_timestamp = None

        print(f"召唤兽装备数据采集器初始化，使用MySQL数据库")

    def _init_equip_collector(self):
        """初始化装备数据采集器实例"""
        try:
            from src.evaluator.market_anchor.equip.equip_market_data_collector import EquipMarketDataCollector
            self.equip_collector = EquipMarketDataCollector()
            print("✅ 成功获取装备数据采集器实例，可共享缓存")
        except Exception as e:
            self.logger.warning(f"获取装备数据采集器实例失败: {e}")
            print(f"⚠️ 无法共享装备数据采集器缓存: {e}")

    def _get_shared_cache_data(self, fangyu: int = 0, speed: int = 0, shanghai: int = 0) -> Optional[pd.DataFrame]:
        """
        从装备数据采集器获取共享缓存数据，优先使用实例缓存
        
        Args:
            fangyu: 防御值筛选 >0 即铠甲
            speed: 速度值筛选 >0 即项圈
            shanghai: 伤害值筛选，==0 则只能匹配shanghai小于20的
            
        Returns:
            过滤后的宠物装备数据DataFrame，如果缓存不可用则返回None
        """
        if not self.equip_collector:
            return None
            
        try:
            # 检查实例缓存是否有效
            if self._cached_pet_equip_data is not None:
                print(f"✅ 使用实例缓存的宠物装备数据，共 {len(self._cached_pet_equip_data)} 条")
                
                # 根据属性值进一步过滤
                filtered_data = self._filter_cached_data_by_attrs(
                    self._cached_pet_equip_data, fangyu, speed, shanghai
                )
                if not filtered_data.empty:
                    print(f"✅ 按属性过滤后得到 {len(filtered_data)} 条宠物装备数据")
                    return filtered_data
                else:
                    print(f"实例缓存中没有找到符合条件的宠物装备数据")
                    return None
            
            # 实例缓存为空，从装备数据采集器获取全量缓存
            full_data = self.equip_collector._get_full_data_from_redis()
            
            if full_data is None or full_data.empty:
                print("装备数据采集器缓存为空，无法共享")
                return None
            
            # 过滤出宠物装备数据 (kindid: PET_EQUIP_KINDID) 并保存到实例缓存
            self._cached_pet_equip_data = full_data[full_data['kindid'] == PET_EQUIP_KINDID].copy()
            self._cache_timestamp = datetime.now()
            
            if not self._cached_pet_equip_data.empty:
                print(f"✅ 从装备数据采集器获取并缓存 {len(self._cached_pet_equip_data)} 条宠物装备数据")
                
                # 根据属性值进一步过滤
                filtered_data = self._filter_cached_data_by_attrs(
                    self._cached_pet_equip_data, fangyu, speed, shanghai
                )
                if not filtered_data.empty:
                    print(f"✅ 按属性过滤后得到 {len(filtered_data)} 条宠物装备数据")
                    return filtered_data
                else:
                    print(f"缓存中没有找到符合条件的宠物装备数据")
                    return None
            else:
                print("装备数据采集器缓存中没有找到宠物装备数据")
                return None
                
        except Exception as e:
            self.logger.warning(f"获取共享缓存数据失败: {e}")
            print(f"⚠️ 共享缓存获取失败: {e}")
            return None

    def _filter_cached_data_by_attrs(self, cached_data: pd.DataFrame, 
                                   fangyu: int = 0, speed: int = 0, shanghai: int = 0) -> pd.DataFrame:
        """
        根据属性值过滤缓存数据
        
        Args:
            cached_data: 缓存的数据
            fangyu: 防御值筛选 >0 即铠甲
            speed: 速度值筛选 >0 即项圈
            shanghai: 伤害值筛选，==0 则只能匹配shanghai小于20的
            
        Returns:
            筛选后的DataFrame
        """
        filtered_data = cached_data.copy()
        
        # 伤害值筛选
        if shanghai == 0:
            filtered_data = filtered_data[filtered_data['shanghai'] < 20]
        
        # 根据属性值区分装备类型后进行过滤
        if fangyu > 0:
            # 铠甲类型：要求有防御值
            filtered_data = filtered_data[filtered_data['fangyu'] > 0]
        elif speed > 0:
            # 项圈类型：要求有速度值
            filtered_data = filtered_data[filtered_data['speed'] > 0]
        else:
            # 护腕类型：既没有防御也没有速度
            filtered_data = filtered_data[
                (filtered_data['fangyu'] == 0) & 
                (filtered_data['speed'] == 0)
            ]
        
        return filtered_data

    def clear_cache(self):
        """清除实例缓存，强制下次重新从装备数据采集器获取数据"""
        self._cached_pet_equip_data = None
        self._cache_timestamp = None
        print("✅ 已清除宠物装备数据实例缓存")

    def get_market_data(self,
                        kindid: Optional[int] = None,
                        level_range: Optional[Tuple[int, int]] = None,
                        price_range: Optional[Tuple[float, float]] = None,
                        server: Optional[str] = None,
                        fangyu: Optional[int] = 0,
                        speed: Optional[int] = 0,
                        shanghai: Optional[int] = 0,
                        limit: int = 1000,
                        use_shared_cache: bool = True) -> pd.DataFrame:
        """
        获取市场召唤兽装备数据，优先从装备数据采集器的共享缓存获取数据

        Args:
            kindid: 装备类型ID，默认为宠物装备类型
            level_range: 等级范围 (min_level, max_level)
            price_range: 价格范围 (min_price, max_price)
            server: 服务器筛选
            -- 判断装备类型
                fangyu: 防御值筛选 >0 即铠甲
                speed: 速度值筛选 >0 即项圈
                以上都不是则是护腕
            -- 属性过滤
                shanghai==0 则 只能匹配shanghai小于20的    
            limit: 返回数据条数限制
            use_shared_cache: 是否使用共享缓存

        Returns:
            召唤兽装备市场数据DataFrame
        """
        try:
            import time
            start_time = time.time()
            
            # 优先从共享缓存获取数据
            if use_shared_cache:
                cached_data = self._get_shared_cache_data(fangyu, speed, shanghai)
                
                if cached_data is not None and not cached_data.empty:
                    # 对缓存数据进行进一步筛选
                    filtered_data = self._filter_cached_data(
                        cached_data,
                        level_range=level_range,
                        price_range=price_range,
                        server=server,
                        limit=limit
                    )
                    
                    elapsed_time = time.time() - start_time
                    print(f"✅ 从共享缓存获取宠物装备数据完成，耗时: {elapsed_time:.3f}秒，返回: {len(filtered_data)} 条数据")
                    return filtered_data
            
            # 降级到MySQL查询
            print("使用MySQL数据库查询宠物装备数据（降级模式）...")
            return self._get_market_data_from_mysql(
                kindid=kindid,
                level_range=level_range,
                price_range=price_range,
                server=server,
                fangyu=fangyu,
                speed=speed,
                shanghai=shanghai,
                limit=limit
            )
            
        except Exception as e:
            self.logger.error(f"获取宠物装备市场数据失败: {e}")
            print(f"获取宠物装备市场数据异常: {e}")
            return pd.DataFrame()

    def _filter_cached_data(self, cached_data: pd.DataFrame, 
                           level_range: Optional[Tuple[int, int]] = None,
                           price_range: Optional[Tuple[float, float]] = None,
                           server: Optional[str] = None,
                           limit: int = 1000) -> pd.DataFrame:
        """
        对缓存数据进行筛选
        
        Args:
            cached_data: 缓存的数据
            level_range: 等级范围筛选
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
        
        # 按更新时间排序并限制条数
        filtered_data = filtered_data.sort_values('update_time', ascending=False).head(limit)
        
        return filtered_data

    def _get_market_data_from_mysql(self,
                                   kindid: Optional[int] = None,
                                   level_range: Optional[Tuple[int, int]] = None,
                                   price_range: Optional[Tuple[float, float]] = None,
                                   server: Optional[str] = None,
                                   fangyu: Optional[int] = 0,
                                   speed: Optional[int] = 0,
                                   shanghai: Optional[int] = 0,
                                   limit: int = 1000) -> pd.DataFrame:
        """
        从MySQL数据库获取市场宠物装备数据
        
        Args:
            参数同get_market_data方法
            
        Returns:
            宠物装备市场数据DataFrame
        """
        try:
            # 构建SQLAlchemy查询，筛选宠物装备
            query = db.session.query(Equipment).filter(Equipment.kindid == PET_EQUIP_KINDID)

            # 基础筛选条件
            if level_range is not None:
                min_level, max_level = level_range
                query = query.filter(Equipment.equip_level.between(min_level, max_level))

            if price_range is not None:
                min_price, max_price = price_range
                query = query.filter(Equipment.price.between(min_price, max_price))

            if server is not None:
                query = query.filter(Equipment.server_name == server)

            if shanghai == 0:
                query = query.filter(Equipment.shanghai < 20)

            # 根据属性值区分装备类型后进行过滤
            if fangyu > 0:
                # 铠甲类型：要求有防御值
                query = query.filter(Equipment.fangyu > 0)
            elif speed > 0:
                # 项圈类型：要求有速度值
                query = query.filter(Equipment.speed > 0)
            else:
                # 护腕类型：既没有防御也没有速度
                query = query.filter(
                    and_(
                        Equipment.fangyu == 0,
                        Equipment.speed == 0
                    )
                )

            # 排序和限制
            query = query.order_by(Equipment.update_time.desc()).limit(limit)

            # 执行查询
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
                
                print(f"从MySQL数据库加载了 {len(result_df)} 条召唤兽装备市场数据")
                return result_df
            else:
                print(f"从MySQL数据库查询到0条召唤兽装备市场数据")
                return pd.DataFrame()

        except Exception as e:
            self.logger.error(f"查询召唤兽装备市场数据失败: {e}")
            print(f"SQL执行异常: {e}")
            return pd.DataFrame()

    def get_market_data_for_similarity(self, target_features: Dict[str, Any]) -> pd.DataFrame:
        """
        根据目标特征获取用于相似度计算的市场数据（先类型分类）
        """
    
        print(f"目标特征equip_level_range: {target_features.get('equip_level_range')}")
        market_data = self.get_market_data_with_business_rules(target_features)
   
        if market_data.empty:
            return market_data
        # 特征提取
        features_list = []
        for _, row in market_data.iterrows():
            try:
                features = self.feature_extractor.extract_features(row.to_dict())
                
                # 保留原始关键字段，确保接口返回时有完整信息
                features['equip_sn'] = row.get('equip_sn', row.get('eid', row.get('id', None)))
                features['price'] = row.get('price', 0)

                features_list.append(features)
            except Exception as e:
                self.logger.warning(f"提取特征失败: {e}")
                continue
        if features_list:
            return pd.DataFrame(features_list)
        else:
            return pd.DataFrame()

    def get_market_data_with_addon_classification(self, target_features: Dict[str, Any]) -> pd.DataFrame:
        """
        先类型分类，再做附加属性分类过滤
        """
        try:
            # 先类型分类
            market_data = self.get_market_data_for_similarity(target_features)
            if market_data.empty:
                return market_data
            
            # 再物理、法术分类
            # shanghai>20忽略lingli、addon_fali 
            target_shanghai = target_features.get('shanghai', 0)
            
            # 创建用于属性分类的目标特征副本
            classification_features = target_features.copy()
            
            if target_shanghai > 20:
                # 物理系装备：伤害>20，忽略法力和灵力属性 TODO: 派生得分还是会有其他干扰
                print(f"物理系装备: shanghai={target_shanghai} > 20，忽略法力和灵力属性")
                classification_features['addon_fali'] = 0
                classification_features['addon_lingli'] = 0
            else:
                print(f"法术系装备: shanghai={target_shanghai} <= 20，保留法力和灵力属性")

            # 再做附加属性分类过滤（原有逻辑）
            target_classification = self._get_target_addon_classification(classification_features)
            print(f"目标召唤兽装备属性分类: {target_classification}")
            print(f"classification_features: {classification_features}")
            market_data['addon_classification'] = market_data.apply(
                lambda row: self._classify_addon_attributes(
                    row.get('addon_fali', 0),
                    row.get('addon_lingli', 0),
                    row.get('addon_liliang', 0),
                    row.get('addon_minjie', 0),
                    row.get('addon_naili', 0),
                    row.get('addon_tizhi', 0)
                ), axis=1
            )
            if target_classification != "无属性":
                # 定义同类属性分组（原有逻辑）
                classification_groups = {
                    "法力系": ["法力", "法灵", "法敏", "法耐", "法体", "力法","灵力", "灵敏", "灵耐", "灵体", "力灵"],
                    "力量系": ["力量", "力敏", "力耐", "力体" ],
                    "敏捷系": ["敏捷", "敏耐", "敏体"],
                    "耐力系": ["耐力", "耐体"],
                    "体质系": ["体质"]
                }
                target_group = None
                for group_name, classifications in classification_groups.items():
                    if target_classification in classifications:
                        target_group = classifications
                        break
                if target_group:
                    before_filter_count = len(market_data)
                    market_data = market_data[
                        (market_data['addon_classification'].isin(target_group)) |
                        (market_data['addon_classification'] == "无属性")
                    ]
                    after_filter_count = len(market_data)
                    print(f"召唤兽装备属性分类过滤: {target_classification} -> 同类属性 {target_group}")
                    print(f"过滤结果: {before_filter_count} -> {after_filter_count} 条数据")
                else:
                    print(f"未找到属性分类 {target_classification} 对应的分组，不进行过滤")
            else:
                print(f"目标召唤兽装备无属性，不进行属性分类过滤")
            return market_data
        except Exception as e:
            self.logger.error(f"按属性分类获取召唤兽装备市场数据失败: {e}")
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
        kindid = target_features.get('kindid')
        # 属性过滤
        shanghai = target_features.get('shanghai', 0) 
        # 类型分类参数
        fangyu = target_features.get('fangyu', 0)
        speed = target_features.get('speed', 0)
        level_range = target_features.get('equip_level_range')
        # 先类型分类
        # 获取基础市场数据
        market_data = self.get_market_data(
            kindid=kindid,
            level_range = level_range,
            fangyu=fangyu,
            speed=speed,
            shanghai=shanghai,
            limit=2000
        )
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

    def _classify_addon_attributes(self, addon_fali: int = 0, addon_lingli: int = 0, 
                                  addon_liliang: int = 0, addon_minjie: int = 0, 
                                  addon_naili: int = 0, addon_tizhi: int = 0) -> str:
        """
        根据召唤兽装备的附加属性分类
        
        召唤兽装备属性点加成分类规则：
        1. "法力" - 纯法力加成
        2. "灵力" - 纯灵力加成  
        3. "力量" - 纯力量加成
        4. "敏捷" - 纯敏捷加成
        5. "耐力" - 纯耐力加成
        6. "法灵" - 法力+灵力组合
        7. "力敏" - 力量+敏捷组合
        8. "力耐" - 力量+耐力组合
        9. "敏耐" - 敏捷+耐力组合
         "法敏","法耐","法体","灵敏","灵耐","灵体","力法","力灵", "力体", "敏体","耐体"
        10. "无属性" - 无任何属性加成
        
        Args:
            addon_fali: 法力加成
            addon_lingli: 灵力加成
            addon_liliang: 力量加成
            addon_minjie: 敏捷加成
            addon_naili: 耐力加成
            addon_tizhi: 体质加成
            
        Returns:
            str: 属性分类类型
        """
        # 统计正数属性
        positive_attrs = {}
        if addon_fali > 0:
            positive_attrs['法力'] = addon_fali
        if addon_lingli > 0:
            positive_attrs['灵力'] = addon_lingli
        if addon_liliang > 0:
            positive_attrs['力量'] = addon_liliang
        if addon_minjie > 0:
            positive_attrs['敏捷'] = addon_minjie
        if addon_naili > 0:
            positive_attrs['耐力'] = addon_naili
        if addon_tizhi > 0:
            positive_attrs['体质'] = addon_tizhi
        
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
            
            # 法力相关组合
            if '法力' in attr_names and '灵力' in attr_names:
                return "法灵"
            elif '法力' in attr_names and '敏捷' in attr_names:
                return "法敏"
            elif '法力' in attr_names and '耐力' in attr_names:
                return "法耐"
            elif '法力' in attr_names and '体质' in attr_names:
                return "法体"
            
            # 灵力相关组合
            elif '灵力' in attr_names and '敏捷' in attr_names:
                return "灵敏"
            elif '灵力' in attr_names and '耐力' in attr_names:
                return "灵耐"
            elif '灵力' in attr_names and '体质' in attr_names:
                return "灵体"
            
            # 力量相关组合
            elif '力量' in attr_names and '敏捷' in attr_names:
                return "力敏"
            elif '力量' in attr_names and '耐力' in attr_names:
                return "力耐"
            elif '力量' in attr_names and '体质' in attr_names:
                return "力体"
            elif '力量' in attr_names and '法力' in attr_names:
                return "力法"
            elif '力量' in attr_names and '灵力' in attr_names:
                return "力灵"
            
            # 敏捷相关组合
            elif '敏捷' in attr_names and '耐力' in attr_names:
                return "敏耐"
            elif '敏捷' in attr_names and '体质' in attr_names:
                return "敏体"
            
            # 耐力体质组合
            elif '耐力' in attr_names and '体质' in attr_names:
                return "耐体"
        
        # 多于两个属性或其他情况，返回主属性（数值最大的）
        if positive_attrs:
            main_attr = max(positive_attrs.items(), key=lambda x: x[1])[0]
            return main_attr
        
        return "无属性"

    def _get_target_addon_classification(self, target_features: Dict[str, Any]) -> str:
        """
        获取目标召唤兽装备的属性分类
        
        Args:
            target_features: 目标召唤兽装备特征
            
        Returns:
            str: 属性分类类型
        """
        addon_fali = target_features.get('addon_fali', 0)
        addon_lingli = target_features.get('addon_lingli', 0)
        addon_liliang = target_features.get('addon_liliang', 0)
        addon_minjie = target_features.get('addon_minjie', 0)
        addon_naili = target_features.get('addon_naili', 0)
        addon_tizhi = target_features.get('addon_tizhi', 0)
        return self._classify_addon_attributes(
            addon_fali, addon_lingli, addon_liliang, addon_minjie, addon_naili, addon_tizhi
        )