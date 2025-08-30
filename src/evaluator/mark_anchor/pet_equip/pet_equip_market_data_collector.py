import os
import sys
import sqlite3
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
except ImportError:
    # 如果导入失败，创建一个简单的占位符类
    class PetEquipFeatureExtractor:
        def __init__(self):
            pass
        
        def extract_features(self, lingshi_data):
            return {}


class PetEquipMarketDataCollector:
    """召唤兽装备市场数据采集器 - 从数据库中获取和处理召唤兽装备市场数据"""

    def __init__(self, db_paths: Optional[List[str]] = None):
        """
        初始化灵饰市场数据采集器

        Args:
            db_paths: 数据库文件路径列表，如果为None则自动查找当月和上月的数据库
        """
        self.db_paths = db_paths or self._find_recent_dbs()
        self.feature_extractor = PetEquipFeatureExtractor()
        self.logger = logging.getLogger(__name__)

        print(f"召唤兽装备数据采集器初始化，加载数据库: {self.db_paths}")

    def _find_recent_dbs(self) -> List[str]:
        """查找所有可用的召唤兽装备数据库文件"""
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
            db_file = os.path.join(data_path, month, f"cbg_equip_{month}.db")
            if os.path.exists(db_file):
                found_dbs.append(db_file)
                print(f"找到指定月份数据库文件: {db_file}")

        # 如果没找到指定月份的，则查找所有可用的召唤兽装备数据库文件
        if not found_dbs:
            print("未找到指定月份的数据库文件，查找所有可用的召唤兽装备数据库文件")
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
                        price_range: Optional[Tuple[float, float]] = None,
                        server: Optional[str] = None,
                        fangyu: Optional[int] = 0,
                        speed: Optional[int] = 0,
                        shanghai: Optional[int] = 0,
                        limit: int = 1000) -> pd.DataFrame:
        """
        获取市场灵饰数据，从多个数据库中合并数据
        TODO: 分类，物理、法术、 套装？目前根据shanghai 20 区分

        Args:
            main_attr: 主属性(damage、deface、magic_damage、magic_deface、fengyin、anti_fengyin、speed)
            attrs: 附加属性 List[Dict] - 附加属性对象列表，最多3个
                每个对象包含:
                - attr_type: str - 属性类型，如"伤害"、"法术伤害"
                - attr_value: int - 属性数值
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
                    query = f"SELECT * FROM equipments WHERE 1=1 AND kindid = {PET_EQUIP_KINDID}"
                    params = []

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

                    if shanghai == 0:
                        query += " AND shanghai < 20"

                    # 根据属性值区分装备类型后进行过滤
                    if fangyu > 0:
                        # 铠甲类型：要求有防御值
                        query += " AND fangyu > 0"
                    elif speed > 0:
                        # 项圈类型：要求有速度值
                        query += " AND speed > 0"
                    else:
                        # 护腕类型：既没有防御也没有速度
                        query += " AND fangyu = 0 AND speed = 0"
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
            result_df = result_df.drop_duplicates(subset=['equip_sn'], keep='first')
            
            return result_df
        else:
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