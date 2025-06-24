import json
import re
import numpy as np
from datetime import datetime
import logging
from typing import Dict, Any, Union, List
import os
from src.utils.jsonc_loader import load_jsonc_relative_to_file

# 配置日志
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class EquipFeatureExtractor:
    """梦幻西游装备特征提取器"""

    def __init__(self):
        """初始化特征提取器"""
        print("初始化特征提取器...")
        self.logger = logging.getLogger(__name__)



    def extract_features(self, equip_data: Dict[str, Any]) -> Dict[str, Union[int, float, str]]:
        """
        提取所有特征
        Returns:
            Dict[str, Union[int, float, str]]: 提取的特征字典，包含以下字段:
                -- 基础属性
                - equip_level (int): 等级
                - kindid (int): 类型
                - init_damage (int): 初伤（包含命中）
                - all_damage (int): 总伤
                - init_wakan (int): 初灵
                - init_defense (int): 初防
                - init_hp (int): 初血
                - init_dex (int): 初敏
                -- 附加属性
                - agg_added_attrs (list): 聚合附加属性
                -- 宝石
                - gem_value (int): 宝石类型
                - gem_level (int): 宝石等级
                -- 特技、特效、套装
                - special_skill (int): 特技
                - special_effect (list): 特效
                - suit_effect (int): 套装效果
                -- 其他
                - hole_num (int): 开运次数 需要在large_equip_desc提取 
                - repair_fail_num (int): 修理失败次数 需要在large_equip_desc提取 
        """
        try:
            features = {}
            
            # 一、基础属性特征
            features.update(self._extract_basic_features(equip_data))

            # 二、附加属性
            features.update(self._extract_added_attrs_features(equip_data))

            # 三、宝石
            features.update(self._extract_gem_features(equip_data))

            # 四、特技
            features.update(self._extract_special_skill_features(equip_data))

            # 五、特效
            features.update(self._extract_special_effect_features(equip_data))

            #  六、套装
            features.update(self._extract_suit_effect_features(equip_data))
            return features

        except Exception as e:
            print(f"特征提取失败: {str(e)}")
            import traceback
            print(traceback.format_exc())
            raise

   