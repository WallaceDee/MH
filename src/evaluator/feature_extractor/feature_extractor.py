import json
import re
import numpy as np
from datetime import datetime
import logging
from typing import Dict, Any, Union, List
import os
from src.utils.jsonc_loader import load_jsonc_from_config_dir, load_jsonc_relative_to_file
from utils.project_path import get_project_root

# 配置日志
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class FeatureExtractor:
    """梦幻西游账号特征提取器"""

    def __init__(self):
        """初始化特征提取器"""
        print("初始化特征提取器...")
        self.logger = logging.getLogger(__name__)

        # 加载规则配置
        self.config = load_jsonc_relative_to_file(
            __file__, '../config/rule_setting.jsonc')

        # 加载hot_server_list配置
        self.hot_server_list = load_jsonc_relative_to_file(
            __file__, '../../constant/hot_server_list.json')

    def extract_features(self, role_data: Dict[str, Any]) -> Dict[str, Union[int, float, str]]:
        """
        提取所有特征
        Returns:
            Dict[str, Union[int, float, str]]: 提取的特征字典，包含以下字段:
                - level (int): 等级
                - sum_exp (int): 总经验
                - three_fly_lv (int): 化圣等级
                - school_history_count (int): 历史门派个数
                - all_new_point (int): 乾元丹
                - qianyuandan_breakthrough (bool): 129/5 159/7
                - jiyuan_amount (int): 机缘值
                - packet_page (int): 行囊拓展
                - xianyu_amount (int): 仙玉
                - learn_cash (int): 储备金
                - hight_grow_rider_count (int): 高成长坐骑数量
                - expt_ski1 (int): 攻击修炼
                - expt_ski2 (int): 防御修炼
                - expt_ski3 (int): 法术修炼
                - expt_ski4 (int): 抗法修炼
                - expt_ski5 (int): 猎术修炼
                - beast_ski1 (int): 召唤兽攻击修炼
                - beast_ski2 (int): 召唤兽防御修炼
                - beast_ski3 (int): 召唤兽法术修炼
                - beast_ski4 (int): 召唤兽抗法修炼
                - yushoushu_skill (int): 育兽术等级
                - school_skills (List[int]): 师门技能等级列表
                - qiangzhuang&shensu (List[int]): 强壮神速技能等级
                - life_skills (List[int]): 生活技能等级列表(≥80级)
                - lingyou_count (int): 灵佑数量
                - hours_listed (int): 上架时间(小时)
                - server_heat (int): 服务器热度
                - collect_num (int): 收藏数量
                - sum_amount (int): 最大召唤兽携带数量
                -- 规则引擎使用
                - limited_skin_value (int): 限量锦衣价值（规则引擎使用）
                - limited_huge_horse_value (int): 限量祥瑞价值（规则引擎使用）
                - limited_other_value (int): 限量其他价值（规则引擎使用）
                --市场锚定法使用
                - limited_skin_score (int): 限量锦衣得分（市场锚定法使用）
                - limited_other_score (int): 限量其他得分（市场锚定法使用）
                - limited_skin_score (int): 限量祥瑞得分（市场锚定法使用）
                - shenqi_score (float): 神器得分（归一化0-100）
                -- 派生特征
                - total_cultivation (int): 总修炼等级（攻击+防御+法术+抗法修炼）
                - total_beast_cultivation (int): 总召唤兽修炼等级（召唤兽攻击+防御+法术+抗法修炼）
                - avg_school_skills (float): 平均师门技能等级
                - high_life_skills_count (int): 高等级生活技能数量（≥140级）
                - total_qiangzhuang_shensu (int): 强壮神速技能总和

        """
        try:
            features = {}

            # 一、基础属性特征
            features.update(self._extract_basic_features(role_data))

            # 二、修炼与控制力特征
            features.update(self._extract_cultivation_features(role_data))

            # 三、技能体系特征
            features.update(self._extract_skill_features(role_data))

            # 四、外观与增值特征
            features.update(self._extract_appearance_features(role_data))

            # 五、市场行为特征
            features.update(self._extract_market_features(role_data))

            # 六、神器得分（归一化0-100）
            value_map = self.config.get('ShenqiAttr2Value', {})
            shenqi = features.get('shenqi', [0,0,0,0,0,0,0,0])
            keys = [
                "allTheSameCount", "same9Count", "3attr", "3", "2attr", "2", "1attr", "1"
            ]
            raw_score = sum(shenqi[i] * value_map.get(keys[i], 0) for i in range(8))
            max_score = 50000
            shenqi_score = min(raw_score / max_score * 100, 100) if max_score > 0 else 0
            features['shenqi_score'] = round(shenqi_score, 2)

            # 七、计算派生特征
            features.update(self._calculate_derived_features(features))

            return features

        except Exception as e:
            print(f"特征提取失败: {str(e)}")
            import traceback
            print(traceback.format_exc())
            raise

    def _extract_basic_features(self, data):
        """提取基础属性特征"""
        qianyuandanBreakthrough = (data.get('level', 0) == 129 and data.get('all_new_point', 0) == 5) or (
            data.get('level', 0) == 159 and data.get('all_new_point', 0) == 7)
        # 历史门派个数 [1,2,1,2,3]计数为3，如果data.get('role_school')不在列表中再+1
        try:
            changesch_json = data.get('changesch_json', '[]')
            if changesch_json and changesch_json != '':
                changesch_data = json.loads(changesch_json)
                schoolHistoryCount = len(set(changesch_data)) + (
                    0 if data.get('role_school') in changesch_data else 0)
            else:
                schoolHistoryCount = 0  # 如果没有转职记录，默认为0个门派
        except (json.JSONDecodeError, TypeError):
            schoolHistoryCount = 0

        # 高成长坐骑 字段data.get('all_rider_json') 格式{"1": {"all_skills": {}, "iType": 505, "exgrow": 12635, "ExtraGrow": 0, "iGrade": 96, "mattrib": "魔力"}, "2": {"all_skills": {"600": 3}, "iType": 504, "exgrow": 13069, "ExtraGrow": 0, "iGrade": 150, "mattrib": "敏捷"}}
        # 统计exgrow>=2.3数量
        try:
            rider_json = data.get('all_rider_json', '{}')
            if rider_json and rider_json != '':
                rider_data = json.loads(rider_json)
                hightGrowRiderCount = sum(1 for rider in rider_data.values()
                                          if float(rider.get('exgrow', 0)) / 10000 >= 2.3)
            else:
                hightGrowRiderCount = 0
        except (json.JSONDecodeError, TypeError, ValueError):
            hightGrowRiderCount = 0
            

        # 神器解析 数据在 shenqi_json 字段（格式：{"full": 0, "power": 1200, "suit": [{"max_use_count": 125, "curr_illusion": 0, "my_use_count": 0, "components": [{"unlock": 1, "wuxing": [{"status": 0, "new_id": 0, "attr": "固定伤害 +3", "wuxingshi_affix": 0, "affix_disable": 0, "new_attr": "", "id": 16, "wuxingshi_level": 1}, {"status": 0, "new_id": 0, "attr": "气血 +21", "wuxingshi_affix": 0, "affix_disable": 0, "new_attr": "", "id": 2, "wuxingshi_level": 1}, {"status": 0, "new_id": 0, "attr": "抵抗封印 +6", "wuxingshi_affix": 0, "affix_disable": 0, "new_attr": "", "id": 4, "wuxingshi_level": 1}, {"status": 0, "new_id": 0, "attr": "气血 +21", "wuxingshi_affix": 0, "affix_disable": 0, "new_attr": "", "id": 2, "wuxingshi_level": 1}], "level": 1}, {"unlock": 0, "wuxing": [{"status": 0, "new_id": 0, "attr": "封印命中 +0", "wuxingshi_affix": 0, "affix_disable": 0, "new_attr": "", "id": 8, "wuxingshi_level": 0}, {"status": 0, "new_id": 0, "attr": "气血 +0", "wuxingshi_affix": 0, "affix_disable": 0, "new_attr": "", "id": 2, "wuxingshi_level": 0}, {"status": 0, "new_id": 0, "attr": "封印命中 +0", "wuxingshi_affix": 0, "affix_disable": 0, "new_attr": "", "id": 8, "wuxingshi_level": 0}, {"status": 0, "new_id": 0, "attr": "气血 +0", "wuxingshi_affix": 0, "affix_disable": 0, "new_attr": "", "id": 2, "wuxingshi_level": 0}], "level": 0}, {"unlock": 0, "wuxing": [{"status": 0, "new_id": 0, "attr": "固定伤害 +0", "wuxingshi_affix": 0, "affix_disable": 0, "new_attr": "", "id": 16, "wuxingshi_level": 0}, {"status": 0, "new_id": 0, "attr": "抵抗封印 +0", "wuxingshi_affix": 0, "affix_disable": 0, "new_attr": "", "id": 4, "wuxingshi_level": 0}, {"status": 0, "new_id": 0, "attr": "抵抗封印 +0", "wuxingshi_affix": 0, "affix_disable": 0, "new_attr": "", "id": 4, "wuxingshi_level": 0}, {"status": 0, "new_id": 0, "attr": "速度 +0", "wuxingshi_affix": 0, "affix_disable": 0, "new_attr": "", "id": 1, "wuxingshi_level": 0}], "level": 0}], "actived": 1, "attributes": [{"new_id": 1, "disable": 1, "new_attr": "速度 +0", "attr": "速度 +0", "id": 1}, {"new_id": 2, "disable": 0, "new_attr": "气血 +0", "attr": "气血 +42", "id": 2}, {"new_id": 8, "disable": 1, "new_attr": "封印命中 +0", "attr": "封印命中 +0", "id": 8}, {"new_id": 16, "disable": 0, "new_attr": "固定伤害 +0", "attr": "固定伤害 +3", "id": 16}, {"new_id": 4, "disable": 0, "new_attr": "抵抗封印 +0", "attr": "抵抗封印 +6", "id": 4}], "illusion": 0}], "active": 0, "my_fu_count": 0, "skill": 0, "skill_level": 1, "illusion": 0, "skill_desc": "", "id": 6205}）
        # 遍历 json 的 suit 字段
        # 在 suit 中的 components 数组中，统计子字段item.wuxing 的id，如果相同的id数目等于 12 个，则 allTheSameCount+=1，否则相同的id数大于等于9，则same9Count+=1。注意遍历components时，如果item.unlock==0则跳过。每个suit互为独立
        # 新增逻辑：same9Count和allTheSameCount的计数还有加一个条件，大于9或者等于12的所统计的id不能一样，若id与之前统计的一样则跳过，即suit第一个统计了12个id为1的，allTheSameCount统计了12个id为1的，则allTheSameCount+=1，当第二个统计也是12个id为1的则跳过，若时12个id为2的才allTheSameCount+=1
        # 统计所有suit下components下的item
        # wuxingshi_level==1 且 wuxingshi_affix>0 则 1attrCount+=1，否则wuxingshi_level==1,1Count+=1
        # wuxingshi_level==2 且 wuxingshi_affix>0 则 2attrCount+=1，否则wuxingshi_level==2,2Count+=1
        # wuxingshi_level==3 且 wuxingshi_affix>0 则 3attrCount+=1，否则wuxingshi_level==3,3Count+=1
        # allTheSameCount,same9Count,3attrCount,3Count,2attrCount,2Count,1attrCount,1Count
        shenqi = [0, 0, 0, 0, 0, 0, 0, 0]

        try:
            shenqi_json = data.get('shenqi_json', '{}')
            if shenqi_json is None or shenqi_json == '':
                shenqi_json = '{}'
            shenqi_data = json.loads(shenqi_json)
            # 记录已经统计过的id
            counted_ids = set()

            for suit in shenqi_data.get('suit', []):
                # 统计相同id的数量
                id_counts = {}
                for component in suit.get('components', []):
                    if component.get('unlock') == 0:
                        continue
                    for wuxing in component.get('wuxing', []):
                        wuxing_id = wuxing.get('id')
                        if wuxing_id:
                            id_counts[wuxing_id] = id_counts.get(
                                wuxing_id, 0) + 1

                # 检查是否有12个相同的id
                for wuxing_id, count in id_counts.items():
                    if count >= 12 and wuxing_id not in counted_ids:
                        shenqi[0] += 1  # allTheSameCount
                        counted_ids.add(wuxing_id)
                        break  # 找到一个12个的就跳出循环
                    elif count >= 9 and wuxing_id not in counted_ids:
                        shenqi[1] += 1  # same9Count
                        counted_ids.add(wuxing_id)
                        break  # 找到一个9个的就跳出循环

                # 统计五行等级和属性
                for component in suit.get('components', []):
                    for wuxing in component.get('wuxing', []):
                        level = wuxing.get('wuxingshi_level', 0)
                        affix = wuxing.get('wuxingshi_affix', 0)

                        if level == 1:
                            if affix > 0:
                                shenqi[6] += 1  # 1attrCount
                            else:
                                shenqi[7] += 1  # 1Count
                        elif level == 2:
                            if affix > 0:
                                shenqi[4] += 1  # 2attrCount
                            else:
                                shenqi[5] += 1  # 2Count
                        elif level == 3:
                            if affix > 0:
                                shenqi[2] += 1  # 3attrCount
                            else:
                                shenqi[3] += 1  # 3Count

        except Exception as e:
            self.logger.error(f"神器统计失败: {e}")
            print(f"错误详情: {str(e)}")
            
        # 特殊召唤兽 灵佑
        try:
            special_pets_raw = data.get('pet', '[]')
            if not special_pets_raw or special_pets_raw == '':
                pets = []
            else:
                try:
                    pets = json.loads(special_pets_raw)
                except (json.JSONDecodeError, TypeError):
                    pets = []
            if not isinstance(pets, list):
                pets = []
            lingyou_count = 0
            for pet in pets:
                skills = pet.get('all_skills', [])
                for skill in skills:
                    if skill['name'] == '灵佑':
                        lingyou_count += skill.get('value', 0)

        except Exception as e:
            self.logger.error(f"灵佑统计失败: {e}")
            print(f"错误详情: {str(e)}")
            lingyou_count = 0

        # 将浮点数转换为整数
        def safe_float_to_int(value, default=0):
            if value is None:
                return default
            try:
                return int(float(value))
            except (ValueError, TypeError):
                return default

        all_new_point = safe_float_to_int(data.get('all_new_point'))

        # 性别 "1":男, "0":女
        icon_id = data.get('role_icon')
        gender = self.get_gender(icon_id)

        features = {
            'level': safe_float_to_int(data.get('level')),  # 等级
            'sum_exp': safe_float_to_int(data.get('sum_exp')),  # 总经验(亿)
            # 化圣等级
            'three_fly_lv': safe_float_to_int(data.get('three_fly_lv')),
            'school_history_count': schoolHistoryCount,  # 历史门派个数
            'all_new_point': all_new_point,  # 乾元丹
            'qianyuandan_breakthrough': qianyuandanBreakthrough,  # 乾元丹突破
            # 月饼粽子机缘
            'jiyuan_amount': safe_float_to_int(data.get('jiyuan_amount')) + safe_float_to_int(data.get('add_point')),
            'packet_page': safe_float_to_int(data.get('packet_page')),  # 行囊拓展
            # 仙玉
            'xianyu_amount': safe_float_to_int(data.get('xianyu_amount')),
            'learn_cash': safe_float_to_int(data.get('learn_cash')),  # 储备金
            'hight_grow_rider_count': hightGrowRiderCount,
            # 最大召唤兽携带数量
            'sum_amount': safe_float_to_int(data.get('sum_amount')),

            'shenqi': shenqi,
            'gender': gender,
            'lingyou_count': lingyou_count  # 灵佑数量
        }

        return features

    def _extract_cultivation_features(self, data):
        """提取修炼与控制力特征"""
        features = {}

        try:
            # 人物修炼
            expt_ski1 = data.get('expt_ski1', 0)
            expt_ski2 = data.get('expt_ski2', 0)
            expt_ski3 = data.get('expt_ski3', 0)
            expt_ski4 = data.get('expt_ski4', 0)
            expt_ski5 = data.get('expt_ski5', 0)
            features['expt_ski1'] = expt_ski1
            features['expt_ski2'] = expt_ski2
            features['expt_ski3'] = expt_ski3
            features['expt_ski4'] = expt_ski4
            features['expt_ski5'] = expt_ski5

            max_expt1 = data.get('max_expt1', 0)
            max_expt2 = data.get('max_expt2', 0)
            max_expt3 = data.get('max_expt3', 0)
            max_expt4 = data.get('max_expt4', 0)

            features['max_expt1'] = max_expt1
            features['max_expt2'] = max_expt2
            features['max_expt3'] = max_expt3
            features['max_expt4'] = max_expt4
            # 控制力
            beast_ski1 = data.get('beast_ski1', 0)
            beast_ski2 = data.get('beast_ski2', 0)
            beast_ski3 = data.get('beast_ski3', 0)
            beast_ski4 = data.get('beast_ski4', 0)
            features['beast_ski1'] = beast_ski1
            features['beast_ski2'] = beast_ski2
            features['beast_ski3'] = beast_ski3
            features['beast_ski4'] = beast_ski4

            features['yushoushu_skill'] = data.get('yushoushu_skill', 0)

        except Exception as e:
            self.logger.error(f"提取修炼特征失败: {e}")
            print(f"错误详情: {str(e)}")
            features['expt_ski1'] = 0
            features['expt_ski2'] = 0
            features['expt_ski3'] = 0
            features['expt_ski4'] = 0
            features['expt_ski5'] = 0
            features['max_expt1'] = 0
            features['max_expt2'] = 0
            features['max_expt3'] = 0
            features['max_expt4'] = 0
            features['beast_ski1'] = 0
            features['beast_ski2'] = 0
            features['beast_ski3'] = 0
            features['beast_ski4'] = 0
            features['yushoushu_skill'] = 0
        return features

    def _extract_skill_features(self, data):
        """提取技能体系特征"""
        features = {
            'school_skills': [0, 0, 0, 0, 0, 0, 0],  # 师门技能
            'qiangzhuang&shensu': [0, 0],  # 强壮神速
            'life_skills': []  # 等级高于80的技能
        }

        try:
            # 师门技能
            skills = data.get('school_skills', {})
            if isinstance(skills, str):
                try:
                    skills = json.loads(skills)
                except Exception:
                    skills = {}

            if isinstance(skills, dict) and skills:
                skill_levels = []
                for skill_name, level in skills.items():
                    try:
                        level = int(level)
                        skill_levels.append(level)
                    except (ValueError, TypeError):
                        continue
                # 确保skill_levels不为None且是列表
                if skill_levels and isinstance(skill_levels, list):
                    features['school_skills'] = skill_levels
                else:
                    features['school_skills'] = [0, 0, 0, 0, 0, 0, 0]
            else:
                # 确保默认值
                features['school_skills'] = [0, 0, 0, 0, 0, 0, 0]
                
            # 生活技能
            life_skills = data.get('life_skills', {})
            if isinstance(life_skills, str):
                try:
                    life_skills = json.loads(life_skills)
                except Exception:
                    life_skills = {}

            if isinstance(life_skills, dict) and life_skills:
                life_skill_levels = []
                for skill_name, level in life_skills.items():
                    try:
                        level = int(level)
                        if skill_name == '强壮':
                            features['qiangzhuang&shensu'][0] = level
                        elif skill_name == '神速':
                            features['qiangzhuang&shensu'][1] = level
                        elif level >= 80:  # 只保留等级大于等于80的技能
                            life_skill_levels.append(level)
                    except (ValueError, TypeError):
                        continue

                if life_skill_levels and isinstance(life_skill_levels, list):
                    features['life_skills'] = life_skill_levels
                else:
                    features['life_skills'] = []
            else:
                # 确保默认值
                features['life_skills'] = []

        except Exception as e:
            self.logger.error(f"提取技能特征失败: {e}")
            # 确保异常情况下也有默认值
            features['school_skills'] = [0, 0, 0, 0, 0, 0, 0]
            features['qiangzhuang&shensu'] = [0, 0]
            features['life_skills'] = []

        return features

    def _extract_appearance_features(self, role_data):
        """提取外观特征，基于价值配置转化为0-100标准化得分"""
        features = {
            'limited_skin_value': 0,      # 限量锦衣价值得分
            'limited_huge_horse_value': 0,     # 限量祥瑞价值得分
            'limited_other_value': 0,        # 限量其他价值得分
            'limited_skin_score': 0,        # 限量锦衣得分
            'limited_huge_horse_score': 0,  # 限量祥瑞得分
            'limited_other_score': 0,       # 限量其他得分
        }

        try:
            # 获取角色性别用于价值计算
            icon_id = role_data.get('role_icon')
            gender = self.get_gender(icon_id)  # "0":女, "1":男

            # 处理锦衣数据
            skins_str = role_data.get('ex_avt_json', '{}')
            if skins_str and skins_str.strip():
                try:
                    skins = json.loads(skins_str)
                    if isinstance(skins, dict):
                        skin_total_value = 0
                        config = self._load_appearance_config()
                        limited_avt_widget = config.get(
                            'limited_avt_widget', {})

                        # 使用新的变体组合计算逻辑
                        skin_total_value = self._calculate_skin_variant_value(
                            skins, gender, config)

                        # 处理特殊挂件（恶魔猪猪等）
                        for skin_id, skin_item in skins.items():
                            if isinstance(skin_item, dict):
                                skin_name = skin_item.get('cName', '未知锦衣')
                                if skin_name in limited_avt_widget:
                                    skin_total_value += limited_avt_widget.get(
                                        skin_name, 0)
                        # 锦衣总价值 规则引擎使用
                        features['limited_skin_value'] = skin_total_value
                        # 转化为标准化得分 市场锚定法使用
                        features['limited_skin_score'] = self._calculate_appearance_score(
                            skin_total_value)

                except (json.JSONDecodeError, TypeError) as e:
                    self.logger.warning(f"解析锦衣数据失败: {e}")

            # 处理祥瑞数据
            huge_horse_str = role_data.get('huge_horse_json', '{}')
            if huge_horse_str and huge_horse_str.strip():
                try:
                    huge_horses = json.loads(huge_horse_str)
                    huge_horses_value = 0

                    if isinstance(huge_horses, dict):
                        # 字典格式处理（实际数据格式）
                        for horse_id, horse_data in huge_horses.items():
                            if isinstance(horse_data, dict):
                                huge_horse_name = horse_data.get(
                                    'cName', '未知祥瑞')
                                huge_horse_value = self._get_appearance_item_value(
                                    huge_horse_name, gender, 'limited_huge_horses', '祥瑞')
                                huge_horses_value += huge_horse_value

                    # 祥瑞总价值 规则引擎使用
                    features['limited_huge_horse_value'] = huge_horses_value
                    # 转化为标准化得分 市场锚定法使用
                    features['limited_huge_horse_score'] = self._calculate_appearance_score(
                        huge_horses_value)
                except (json.JSONDecodeError, TypeError) as e:
                    self.logger.warning(f"解析祥瑞数据失败: {e}")

        except Exception as e:
            self.logger.error(f"提取外观特征失败: {e}")
            # 保持默认值

        return features

    def _get_appearance_item_value(self, item_name, gender, config_key, item_type="外观"):
        """
        获取外观物品价值（元）- 通用方法

        Args:
            item_name (str): 物品名称
            gender (str): 角色性别 "0":女, "1":男
            config_key (str): 配置文件中的键名 (如 'limited_skins', 'limited_huge_horses')
            item_type (str): 物品类型，用于错误日志 (如 '锦衣', '祥瑞')

        Returns:
            int: 物品价值（元）
        """
        try:
            # 加载配置文件
            config = self._load_appearance_config()
            items_config = config.get(config_key, {})

            # 首先尝试直接匹配
            if item_name in items_config:
                item_config = items_config[item_name]
                return self._calculate_item_price(item_config, item_name, gender)

            # 如果没有直接匹配，尝试去掉染色后缀匹配基础名称
            if '·' in item_name:
                base_name = item_name.split('·')[0]  # 取"·"前面的部分作为基础名称
                if base_name in items_config:
                    item_config = items_config[base_name]
                    # 传入原始名称用于判断是否染色
                    return self._calculate_item_price(item_config, item_name, gender)

            return 0

        except Exception as e:
            self.logger.error(f"获取{item_type}价值失败: {e}")
            return 0

    def _calculate_skin_variant_value(self, skins, gender, config):
        """
        计算锦衣变体组合价值

        优化规则：
        - 如果只有基础版本：统计基础价格
        - 如果有基础版本 + 1种变体：统计变体价格
        - 如果有基础版本 + n种变体：统计 变体价格*n - 基础价格

        Args:
            skins: 锦衣数据字典
            gender: 性别
            config: 配置文件

        Returns:
            int: 总价值（元）
        """
        limited_skins = config.get('limited_skins', {})
        skin_groups = {}  # 按基础名称分组

        # 按基础名称分组锦衣
        for skin_id, skin_item in skins.items():
            if isinstance(skin_item, dict):
                skin_name = skin_item.get('cName', '未知锦衣')

                # 跳过非限量锦衣
                base_name = skin_name.split(
                    '·')[0] if '·' in skin_name else skin_name
                if base_name not in limited_skins:
                    continue

                if base_name not in skin_groups:
                    skin_groups[base_name] = {
                        'base': False,  # 是否有基础版本
                        'variants': [],  # 变体列表
                        'config': limited_skins[base_name]
                    }

                if '·' in skin_name:
                    # 变体版本
                    skin_groups[base_name]['variants'].append(skin_name)
                else:
                    # 基础版本
                    skin_groups[base_name]['base'] = True

        total_value = 0

        # 计算每个基础锦衣组的价值
        for base_name, group_info in skin_groups.items():
            has_base = group_info['base']
            variant_count = len(group_info['variants'])
            config_item = group_info['config']

            if variant_count == 0:
                # 只有基础版本
                if has_base:
                    value = self._calculate_item_price(
                        config_item, base_name, gender)
                    total_value += value
            elif variant_count == 1:
                # 有基础版本 + 1种变体：统计变体价格
                variant_name = group_info['variants'][0]
                value = self._calculate_item_price(
                    config_item, variant_name, gender)
                total_value += value
            else:
                # 有基础版本 + n种变体：统计 变体价格*n - 基础价格
                variant_price = self._calculate_item_price(
                    config_item, group_info['variants'][0], gender)  # 变体价格
                base_price = self._calculate_item_price(
                    config_item, base_name, gender)  # 基础价格
                total_value += variant_price * variant_count - base_price

        # 处理非变体锦衣（不支持变体的锦衣直接累加）
        for skin_id, skin_item in skins.items():
            if isinstance(skin_item, dict):
                skin_name = skin_item.get('cName', '未知锦衣')
                base_name = skin_name.split(
                    '·')[0] if '·' in skin_name else skin_name

                # 如果配置中不支持变体（非数组格式），直接按原逻辑计算
                if base_name in limited_skins:
                    config_item = limited_skins[base_name]
                    if not isinstance(config_item, list):  # 非数组格式，不支持变体
                        # 确保不重复计算已处理的变体锦衣
                        if base_name not in skin_groups:
                            value = self._calculate_item_price(
                                config_item, skin_name, gender)
                            total_value += value

        return total_value

    def _calculate_item_price(self, item_config, item_name, gender):
        """
        根据配置计算物品价格

        Args:
            item_config: 配置项（dict/list/int/float）
            item_name: 物品名称（用于判断是否染色版本）
            gender: 性别

        Returns:
            int: 价格
        """
        if isinstance(item_config, dict):
            # 男女价格不同的情况
            return item_config.get(gender, 0)
        elif isinstance(item_config, list):
            # 数组格式：[基础价格, 染色/特殊价格]
            if '·' in item_name:  # 染色/特殊版本
                return item_config[1] if len(item_config) > 1 else item_config[0]
            else:  # 基础版本
                return item_config[0]
        elif isinstance(item_config, (int, float)):
            # 统一价格
            return item_config
        else:
            return 0

    def _calculate_appearance_score(self, value_yuan):
        """
        将外观价值（元）转化为标准化得分
        参考calculate_skin_score逻辑
        - 100元以下：10-20分
        - 100-1000元：20-40分  
        - 1000-10000元：40-70分
        - 10000元以上：70-100分
        """
        if value_yuan <= 0:
            return 0
        elif value_yuan < 100:
            return 10 + (value_yuan / 100) * 10
        elif value_yuan < 1000:
            return 20 + ((value_yuan - 100) / 900) * 20
        elif value_yuan < 10000:
            return 40 + ((value_yuan - 1000) / 9000) * 30
        else:
            return 70 + min(((value_yuan - 10000) / 50000) * 30, 30)

    def _load_appearance_config(self):
        """加载外观价值配置文件"""
        try:
            # 构建相对路径：从evaluator目录到config/ex_avt_value.jsonc
            relative_path = os.path.join('..','config', 'ex_avt_value.jsonc')
            return load_jsonc_relative_to_file(__file__, relative_path)

        except Exception as e:
            self.logger.error(f"加载外观配置文件失败: {e}")
            return {}

    def _extract_market_features(self, data):
        """提取市场行为特征"""
        features = {
            'hours_listed': 0,
            'collect_num': 0,
            'server_heat': 0,
        }
        # self.hot_server_list 加载了服务器热度配置，根据serverid获取热度
        # 根据serverid获取热度
        server_id = data.get('serverid', 0)
        features['server_heat'] = self._get_server_heat(server_id)

        # 上架时间（小时）
        # expire_time是上架过期的时间 "2025-06-13 21:28:50" 上架时间固定是14天正的
        # 已上架时间（小时） = 14天*24 - (上架过期时间 - 现在时间).总小时数
        if 'expire_time' in data:
            expire_time = datetime.strptime(
                data['expire_time'], '%Y-%m-%d %H:%M:%S')
            now = datetime.now()
            time_until_expire = expire_time - now
            hours_until_expire = time_until_expire.total_seconds() / 3600
            features['hours_listed'] = (14 * 24) - hours_until_expire

        # 收藏
            features['collect_num'] = data.get('collect_num', 0)

        return features
         
    def _get_server_heat(self, server_id):
        """
        根据服务器ID获取服务器热度
        
        Args:
            server_id: 服务器ID
            
        Returns:
            int: 服务器热度值，默认为0
        """
        try:
            # 遍历所有热度分组
            for heat_group in self.hot_server_list:
                server_heat = heat_group.get('server_heat', 0)
                
                # 检查该组中的所有服务器
                for server in heat_group.get('children', []):
                    if server.get('server_id') == server_id:
                        return server_heat
                        
            # 如果没有找到匹配的服务器，返回默认热度0
            return 0
            
        except Exception as e:
            logging.error(f"获取服务器热度失败: {e}")
            return 0
        
    def get_gender(self, icon_id):
        """
        根据图标ID获取角色性别
        完全参考JavaScript逻辑实现，将所有逻辑整合在一个函数内

        Args:
            icon_id (int): 角色图标ID

        Returns:
            str: "0"(女性) 或 "1"(男性)
        """
        try:
            # 输入验证
            if icon_id is None:
                return "0"

            type_id = int(icon_id)

            # 角色图标ID范围修正逻辑（对应JavaScript的get_role_iconid函数）
            need_fix_range = [
                [13, 24],   # 第一个门派范围
                [37, 48],   # 第二个门派范围
                [61, 72],   # 第三个门派范围
                [213, 224],  # 第四个门派范围
                [237, 248],  # 第五个门派范围
                [261, 272]  # 第六个门派范围
            ]

            # 检查type_id是否在需要修正的范围内，如果是则减12
            for range_start, range_end in need_fix_range:
                if range_start <= type_id <= range_end:
                    type_id = type_id - 12
                    break

            # 性别信息映射，与JavaScript保持一致
            gender_info = {
                "0": ["1", "2", "5", "6", "9", "10", "201", "205", "209"],      # 女性
                "1": ["3", "4", "7", "8", "11", "12", "203", "207", "208", "211"]  # 男性
            }

            # 转换为字符串进行查找
            type_id_str = str(type_id)

            # 在gender_info中查找对应的性别
            for gender_key, id_list in gender_info.items():
                if type_id_str in id_list:
                    return gender_key

            # 默认返回"0"(女性)
            return "0"

        except (ValueError, TypeError) as e:
            self.logger.error(f"获取角色性别失败: {e}")
            return "0"

    def _calculate_derived_features(self, features: Dict[str, Any]) -> Dict[str, Any]:
        """
        计算派生特征
        
        Args:
            features: 原始特征字典
            
        Returns:
            Dict[str, Any]: 包含派生特征的字典
        """
        derived_features = {}
        
        # 总修炼等级 - 安全处理None值
        cultivation_keys = ['expt_ski1', 'expt_ski2', 'expt_ski3', 'expt_ski4']
        cultivation_values = []
        for key in cultivation_keys:
            value = features.get(key, 0)
            # 如果值是None，转换为0
            cultivation_values.append(0 if value is None else value)
        derived_features['total_cultivation'] = sum(cultivation_values)
        
        # 总召唤兽修炼等级 - 安全处理None值
        beast_cultivation_keys = ['beast_ski1', 'beast_ski2', 'beast_ski3', 'beast_ski4']
        beast_cultivation_values = []
        for key in beast_cultivation_keys:
            value = features.get(key, 0)
            # 如果值是None，转换为0
            beast_cultivation_values.append(0 if value is None else value)
        derived_features['total_beast_cultivation'] = sum(beast_cultivation_values)
        
        # 总技能等级 - 安全处理None值和空列表
        school_skills = features.get('school_skills', [])
        if school_skills is None or not isinstance(school_skills, list):
            school_skills = []
        derived_features['avg_school_skills'] = (sum(school_skills) / len(school_skills)) if school_skills else 0
        
        # 生活技能统计 - 安全处理None值和空列表
        life_skills = features.get('life_skills', [])
        if life_skills is None or not isinstance(life_skills, list):
            life_skills = []
        derived_features['high_life_skills_count'] = sum(1 for skill in life_skills if skill >= 140) if life_skills else 0
        
        # 强壮神速统计 - 安全处理None值和空列表
        qiangzhuang_shensu = features.get('qiangzhuang&shensu', [])
        if qiangzhuang_shensu is None or not isinstance(qiangzhuang_shensu, list):
            qiangzhuang_shensu = []
        derived_features['total_qiangzhuang_shensu'] = sum(qiangzhuang_shensu) if qiangzhuang_shensu else 0

        return derived_features
