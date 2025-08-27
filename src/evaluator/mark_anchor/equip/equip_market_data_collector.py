from datetime import datetime
from typing import Dict, Any, List, Optional, Union, Tuple
import logging
import numpy as np
import pandas as pd
import sqlite3
import sys
import os

# 套装效果ID常量定义
# 高价值套装
AGILITY_SUITS = [1040, 1047, 1049, 1053, 1056, 1065, 1067, 1070, 1077]  # 敏捷套装
MAGIC_SUITS = [1041, 1042, 1043, 1046, 1050, 1052, 1057, 1059, 1069, 1073, 1074, 1081]  # 魔力套装
HIGH_VALUE_SUITS = AGILITY_SUITS + MAGIC_SUITS  # 合并高价值套装

# 精确筛选套装（允许精确筛选的套装效果）
PRECISE_FILTER_SUITS = [4002, 4011, 4017, 4019, 3011, 3050]  # 定心术、变身、碎星诀、天神护体、满天花雨、浪涌

# 高价值特效
HIGH_VALUE_EFFECTS = [1, 3, 5]  # 无级别，愤怒，永不磨损 高价值特效
IMPORTANT_EFFECTS = [1, 2, 3, 4, 5, 7, 11, 12, 16]  # 相似度计算中重要的特效

# 高价值简易装备等级
HIGH_VALUE_EQUIP_LEVELS = [70, 90, 110, 130]  # 高价值简易装备等级
SIMPLE_EFFECT_ID = 2  # 简易装备特效编号

# 低价值特技
LOW_VALUE_SPECIAL_SKILLS = [1001,1002,1003,1004,1005,1006,1007,1050,2001,2004,1041,2041]
# 低价值特效
LOW_VALUE_EFFECTS = [9, 10, 13, 14, 15, 17, 18]

# 添加项目根目录到Python路径，解决模块导入问题
current_dir = os.path.dirname(os.path.abspath(__file__))

try:
    from ...feature_extractor.equip_feature_extractor import EquipFeatureExtractor
except ImportError:
    try:
        from src.evaluator.feature_extractor.equip_feature_extractor import EquipFeatureExtractor
    except ImportError:
        # 如果都导入失败，创建一个简单的占位符
        class EquipFeatureExtractor:
            def __init__(self):
                pass

            def extract_features(self, equip_data):
                return {}


class EquipMarketDataCollector:
    """装备市场数据采集器 - 从数据库中获取和处理装备市场数据"""

    def __init__(self, db_paths: Optional[List[str]] = None):
        """
        初始化装备市场数据采集器

        Args:
            db_paths: 数据库文件路径列表，如果为None则自动查找当月和上月的数据库
        """
        self.db_paths = db_paths or self._find_recent_dbs()
        self.feature_extractor = EquipFeatureExtractor()
        self.logger = logging.getLogger(__name__)

        print(f"装备数据采集器初始化，加载数据库: {self.db_paths}")

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
            db_file = os.path.join(data_path, month, f"cbg_equip_{month}.db")
            if os.path.exists(db_file):
                found_dbs.append(db_file)
                print(f"找到指定月份数据库文件: {db_file}")

        # 如果没找到指定月份的，则查找所有可用的装备数据库文件
        if not found_dbs:
            print("未找到指定月份的数据库文件，查找所有可用的装备数据库文件")
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
        """连接到指定的装备数据库"""
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
        获取市场装备数据，从多个数据库中合并数据

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

        Returns:
            装备市场数据DataFrame
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
                        # 直接使用kindid字段
                        query += " AND kindid = ?"
                        params.append(kindid)

                    if special_skill is not None:
                        # 只有当不需要排除高价值特技时，才添加具体的特技筛选条件
                        if not exclude_high_value_special_skills:
                            query += " AND special_skill = ?"
                            params.append(special_skill)
                        else:
                            print(f"跳过具体特技筛选，因为需要排除高价值特技")

                    # 特技筛选逻辑：如果目标装备是低价值特技，则排除高价值特技装备
                    if exclude_high_value_special_skills:
                        # 只能搜索无特技或低价值特技的装备
                        # 无特技：special_skill = 0 或 special_skill IS NULL
                        # 低价值特技：special_skill IN (低价值特技列表)
                        query += " AND (special_skill = 0 OR special_skill IS NULL OR special_skill IN ("
                        placeholders = ','.join(['?' for _ in LOW_VALUE_SPECIAL_SKILLS])
                        query += f"{placeholders}))"
                        params.extend(LOW_VALUE_SPECIAL_SKILLS)
                        print(f"特技筛选：只搜索无特技或低价值特技装备")

                    if suit_effect is not None:
                        # 将字符串转换为数字后再比较（pet_equip除外，其他都是数字字符串）
                        try:
                            suit_effect_num = int(
                                suit_effect) if suit_effect is not None else 0
                            if suit_effect_num > 0:
                                query += " AND suit_effect = ?"
                                params.append(suit_effect_num)
                        except (ValueError, TypeError):
                            # 如果转换失败（可能是pet_equip的字符串套装），直接使用原值
                            if suit_effect and str(suit_effect).strip():
                                query += " AND suit_effect = ?"
                                params.append(suit_effect)

                    if require_high_value_suits:
                        # 强制包含高价值套装：只搜索魔力套和敏捷套装备
                        high_value_suits = HIGH_VALUE_SUITS

                        if high_value_suits:
                            # 创建IN条件：suit_effect IN (1040, 1041, ...)
                            placeholders = ','.join(
                                ['?' for _ in high_value_suits])
                            query += f" AND suit_effect IN ({placeholders})"
                            params.extend(high_value_suits)
                            print(f"强制包含高价值套装：只搜索魔力套和敏捷套装备")

                    if special_effect is not None:
                        # 特效筛选（多选，JSON数组格式）
                        if special_effect and len(special_effect) > 0:
                            effect_conditions = []
                            for effect in special_effect:
                                if effect not in LOW_VALUE_EFFECTS:  # 排除低价值特效
                                    # 使用精确的JSON数组匹配，避免数字包含关系的误匹配
                                    # 匹配模式：[6], [6,x], [x,6], [x,6,y] 等，但不匹配16, 26等包含6的数字
                                    effect_conditions.append(
                                        "(special_effect LIKE ? OR special_effect LIKE ? OR special_effect LIKE ? OR special_effect LIKE ?)")
                                    # 四种匹配模式：单独存在、开头、中间、结尾
                                    params.extend([
                                        f'[{effect}]',        # 只有这一个特效：[6]
                                        f'[{effect},%',       # 在开头：[6,x,...]
                                        f'%,{effect},%',      # 在中间：[x,6,y,...]
                                        f'%,{effect}]'        # 在结尾：[x,y,6]
                                    ])

                            # 将特效条件添加到查询中
                            if effect_conditions:
                                query += f" AND ({' OR '.join(effect_conditions)})"

                    if exclude_special_effect is not None:
                        # 排除特效筛选：排除具有指定特效的装备
                        if exclude_special_effect and len(exclude_special_effect) > 0:
                            exclude_conditions = []
                            for effect in exclude_special_effect:
                                # 使用NOT操作排除包含指定特效的装备
                                exclude_conditions.append(
                                    "NOT (special_effect LIKE ? OR special_effect LIKE ? OR special_effect LIKE ? OR special_effect LIKE ?)")
                                # 四种匹配模式：单独存在、开头、中间、结尾
                                params.extend([
                                    f'[{effect}]',        # 只有这一个特效：[1]
                                    f'[{effect},%',       # 在开头：[1,x,...]
                                    f'%,{effect},%',      # 在中间：[x,1,y,...]
                                    f'%,{effect}]'        # 在结尾：[x,y,1]
                                ])

                            # 将排除条件添加到查询中
                            if exclude_conditions:
                                query += f" AND ({' AND '.join(exclude_conditions)})"

                    if exclude_suit_effect is not None:
                        # 排除套装效果筛选：排除具有指定套装效果的装备
                        if exclude_suit_effect and len(exclude_suit_effect) > 0:
                            exclude_suit_conditions = []
                            for suit_id in exclude_suit_effect:
                                # 排除具有指定套装效果的装备
                                exclude_suit_conditions.append(
                                    "suit_effect != ?")
                                params.append(suit_id)

                            # 将排除套装条件添加到查询中
                            if exclude_suit_conditions:
                                query += f" AND ({' AND '.join(exclude_suit_conditions)})"

                    if exclude_high_value_simple_equips:
                        # 排除高价值简易装备：排除70级/90级/110级/130级且有简易特效(2)的装备
                        high_value_levels = HIGH_VALUE_EQUIP_LEVELS
                        simple_effect_patterns = [
                            f'[{SIMPLE_EFFECT_ID}]', f'[{SIMPLE_EFFECT_ID},%', f'%,{SIMPLE_EFFECT_ID},%', f'%,{SIMPLE_EFFECT_ID}]']  # 简易特效的匹配模式

                        exclude_high_value_simple_conditions = []
                        for level in high_value_levels:
                            # 对于每个高价值等级，排除该等级且有简易特效的装备
                            level_condition_parts = []
                            for pattern in simple_effect_patterns:
                                level_condition_parts.append(
                                    "special_effect LIKE ?")
                                params.append(pattern)

                            # 组合等级和简易特效条件：NOT (equip_level = ? AND (简易特效条件))
                            level_and_simple_condition = f"NOT (equip_level = ? AND ({' OR '.join(level_condition_parts)}))"
                            # 在简易特效参数前插入等级参数
                            params.insert(-len(simple_effect_patterns), level)
                            exclude_high_value_simple_conditions.append(
                                level_and_simple_condition)

                        # 将所有高价值简易装备排除条件添加到查询中
                        if exclude_high_value_simple_conditions:
                            query += f" AND ({' AND '.join(exclude_high_value_simple_conditions)})"
                            print(f"排除高价值简易装备：70级/90级/110级/130级且有简易特效的装备")

                    if level_range:
                        # 直接使用equip_level字段
                        query += " AND equip_level BETWEEN ? AND ?"
                        params.extend(level_range)

                    if price_range:
                        query += " AND price BETWEEN ? AND ?"
                        params.extend(price_range)

                    if server:
                        query += " AND server = ?"
                        params.append(server)

                    # 每个数据库限制一定数量，总体控制在limit内
                    db_limit = min(limit // len(self.db_paths) + 100, limit)
                    query += f" ORDER BY update_time DESC LIMIT {db_limit}"

                    try:
                        df = pd.read_sql_query(query, conn, params=params)
                        if not df.empty:
                            df['source_db'] = db_path  # 标记数据来源
                            all_data.append(df)
                            print(f"从 {db_path} 加载了 {len(df)} 条装备数据")
                        else:
                            print(f"从 {db_path} 查询到0条数据")
                    except Exception as e:
                        self.logger.error(f"查询装备数据失败 ({db_path}): {e}")
                        print(f"SQL执行异常: {e}")
                        continue

            except Exception as e:
                self.logger.error(f"处理数据库失败 ({db_path}): {e}")
                continue

        # 合并所有数据
        if all_data:
            combined_df = pd.concat(all_data, ignore_index=True)

            # 按时间排序并限制总数量
            if 'update_time' in combined_df.columns:
                combined_df = combined_df.sort_values(
                    'update_time', ascending=False)

            combined_df = combined_df.head(limit)

            print(f"总共加载了 {len(combined_df)} 条装备数据")
            return combined_df
        else:
            print(f"未从任何数据库加载到装备数据")
            print(f"请检查数据库文件是否存在，以及筛选条件是否过于严格")
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
            print(f"special_effectspecial_effectspecial_effectspecial_effect: {special_effect}-----------------target_equip_level{target_features}")
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
                # 检查是否包含精确筛选套装（只对数字套装有效）
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
