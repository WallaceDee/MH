import json
import re
import numpy as np
from datetime import datetime
import logging
from typing import Dict, Any, Union, List
import os


class FeatureExtractor:
    """梦幻西游账号特征提取器"""

    def __init__(self):
        """初始化特征提取器"""
        print("初始化特征提取器...")
        self.logger = logging.getLogger(__name__)
        
        # 加载规则配置
        config_path = os.path.join(os.path.dirname(__file__), 'rule_setting.json')
        with open(config_path, 'r', encoding='utf-8') as f:
            self.config = json.load(f)
        
        # 定义高价值特技
        self.premium_skills = ['罗汉金钟', '晶清诀', '四海升平', '慈航普度', '笑里藏刀']

        # 定义特殊宝宝技能
        self.premium_pet_skills = ['净台妙谛', '死亡召唤', '力劈华山', '善恶有报', '须弥真言']

        # 定义限量锦衣价值
        self.limited_skin_values = {
            '青花瓷': 500,
            '浪淘沙': 400,
            '云龙梦': 300,
            '绯雪织': 300,
            '冰寒绡': 200
        }

        # 定义门派热度系数
        self.school_heat = {
            '大唐官府': 1.2,
            '方寸山': 1.1,
            '化生寺': 1.0,
            '女儿村': 1.1,
            '天宫': 1.0,
            '龙宫': 1.3,
            '五庄观': 0.9,
            '普陀山': 1.0,
            '阴曹地府': 1.1,
            '魔王寨': 1.2,
            '狮驼岭': 1.0,
            '盘丝洞': 0.9,
            '神木林': 1.1,
            '凌波城': 1.2,
            '无底洞': 1.0,
            '女魃墓': 1.1,
            '天机城': 0.9,
            '花果山': 1.2
        }

        # 从配置文件加载高价值法宝
        self.premium_fabao = self.config.get('PremiumFabao', [])

    def extract_features(self, character_data: Dict[str, Any]) -> Dict[str, Union[int, float, str]]:
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
                - total_gem_level (int): 宝石总等级
                - premium_skill_count (int): 特技数量
                - set_bonus_count (int): 套装数量
                - total_equip_score (int): 装备总分
                - avg_gem_level (float): 平均宝石等级(当有装备时)
                - premium_pet_count (int): 极品宠物数量
                - total_pet_score (float): 宠物总分
                - max_pet_score (float): 最高宠物分数
                - lingyou_count (int): 灵佑数量
                - avg_pet_score (float): 平均宠物分数(当有宠物时)
                - limited_skin_value (int): 限量锦衣数量
                - hours_listed (int): 上架时间(小时)
                - collect_num (int): 收藏数量
                - allow_pet_count (int): 最大召唤兽携带数量
                - premium_fabao_count (int): 高价值法宝数量
        """
        try:
            features = {}

            # 一、基础属性特征
            features.update(self._extract_basic_features(character_data))

            # 二、修炼与控制力特征
            features.update(self._extract_cultivation_features(character_data))

            # 三、技能体系特征
            features.update(self._extract_skill_features(character_data))

            # # 四、装备特征体系
            # features.update(self._extract_equipment_features(character_data))

            # # 五、召唤兽特征
            # features.update(self._extract_pet_features(character_data))

            # # 六、外观与增值特征
            # features.update(self._extract_appearance_features(character_data))

            # # 七、市场行为特征
            # features.update(self._extract_market_features(character_data))

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
        # 历史门派个数 [1,2,1,2,3]计数为3，如果data.get('character_school')不在列表中再+1
        try:
            changesch_json = data.get('changesch_json', '[]')
            if changesch_json and changesch_json != '':
                changesch_data = json.loads(changesch_json)
                schoolHistoryCount = len(set(changesch_data)) + (
                    0 if data.get('character_school') in changesch_data else 0)
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
        # 有价值的法宝数量 在 all_fabao_json（格式[{"name": "附灵玉", "cDesc": "0#Y灵气：#G50 #Y 五行：#G水#Y#r修炼境界：第#G4#Y层 #c13E1EC预知福祸#Y"}, {"name": "重明战鼓", "cDesc": "0#Y灵气：#G500#Y 五行：#G水#Y#r修炼境界：第#G14#Y层 #cFF6F28返璞归真#Y#r#n#Y最佳五行属性奖励：额外增加召唤兽等级*3％的物攻和法攻#G（已生效）#Y"}, {"name": "拭剑石", "cDesc": "0#Y灵气：#G192#Y 五行：#G水#Y#r修炼境界：第#G9#Y层 #cFF6F28不堕轮回#Y"}, {"name": "仓颉神木", "cDesc": "0【专用】修炼境界：第#G4#Y层"}]）在找出名字在 self.premium_fabao 列表中的格式 ，
        fabao_json = data.get('all_fabao_json')
        if fabao_json is None or fabao_json == '':
            premiumFabaoCount = 0
        else:
            try:
                fabao_data = json.loads(fabao_json)
                premiumFabaoCount = sum(1 for fabao in fabao_data
                                        if fabao.get('name') in self.premium_fabao)
            except (json.JSONDecodeError, TypeError):
                premiumFabaoCount = 0
        # 神器解析 数据在 shenqi_json 字段（格式：{"full": 0, "power": 1200, "suit": [{"max_use_count": 125, "curr_illusion": 0, "my_use_count": 0, "components": [{"unlock": 1, "wuxing": [{"status": 0, "new_id": 0, "attr": "固定伤害 +3", "wuxingshi_affix": 0, "affix_disable": 0, "new_attr": "", "id": 16, "wuxingshi_level": 1}, {"status": 0, "new_id": 0, "attr": "气血 +21", "wuxingshi_affix": 0, "affix_disable": 0, "new_attr": "", "id": 2, "wuxingshi_level": 1}, {"status": 0, "new_id": 0, "attr": "抵抗封印 +6", "wuxingshi_affix": 0, "affix_disable": 0, "new_attr": "", "id": 4, "wuxingshi_level": 1}, {"status": 0, "new_id": 0, "attr": "气血 +21", "wuxingshi_affix": 0, "affix_disable": 0, "new_attr": "", "id": 2, "wuxingshi_level": 1}], "level": 1}, {"unlock": 0, "wuxing": [{"status": 0, "new_id": 0, "attr": "封印命中 +0", "wuxingshi_affix": 0, "affix_disable": 0, "new_attr": "", "id": 8, "wuxingshi_level": 0}, {"status": 0, "new_id": 0, "attr": "气血 +0", "wuxingshi_affix": 0, "affix_disable": 0, "new_attr": "", "id": 2, "wuxingshi_level": 0}, {"status": 0, "new_id": 0, "attr": "封印命中 +0", "wuxingshi_affix": 0, "affix_disable": 0, "new_attr": "", "id": 8, "wuxingshi_level": 0}, {"status": 0, "new_id": 0, "attr": "气血 +0", "wuxingshi_affix": 0, "affix_disable": 0, "new_attr": "", "id": 2, "wuxingshi_level": 0}], "level": 0}, {"unlock": 0, "wuxing": [{"status": 0, "new_id": 0, "attr": "固定伤害 +0", "wuxingshi_affix": 0, "affix_disable": 0, "new_attr": "", "id": 16, "wuxingshi_level": 0}, {"status": 0, "new_id": 0, "attr": "抵抗封印 +0", "wuxingshi_affix": 0, "affix_disable": 0, "new_attr": "", "id": 4, "wuxingshi_level": 0}, {"status": 0, "new_id": 0, "attr": "抵抗封印 +0", "wuxingshi_affix": 0, "affix_disable": 0, "new_attr": "", "id": 4, "wuxingshi_level": 0}, {"status": 0, "new_id": 0, "attr": "速度 +0", "wuxingshi_affix": 0, "affix_disable": 0, "new_attr": "", "id": 1, "wuxingshi_level": 0}], "level": 0}], "actived": 1, "attributes": [{"new_id": 1, "disable": 1, "new_attr": "速度 +0", "attr": "速度 +0", "id": 1}, {"new_id": 2, "disable": 0, "new_attr": "气血 +0", "attr": "气血 +42", "id": 2}, {"new_id": 8, "disable": 1, "new_attr": "封印命中 +0", "attr": "封印命中 +0", "id": 8}, {"new_id": 16, "disable": 0, "new_attr": "固定伤害 +0", "attr": "固定伤害 +3", "id": 16}, {"new_id": 4, "disable": 0, "new_attr": "抵抗封印 +0", "attr": "抵抗封印 +6", "id": 4}], "illusion": 0}], "active": 0, "my_fu_count": 0, "skill": 0, "skill_level": 1, "illusion": 0, "skill_desc": "", "id": 6205}）
        # 遍历 json 的 suit 字段
        # 在 suit 中的 components 数组中，统计子字段item.wuxing 的id，如果相同的id数目等于 12 个，则 allTheSameCount+=1，否则相同的id数大于等于9，则same9Count+=1。注意遍历components时，如果item.unlock==0则跳过。每个suit互为独立
        # 新增逻辑：same9Count和allTheSameCount的计数还有加一个条件，大于9或者等于12的所统计的id不能一样，若id与之前统计的一样则跳过，即suit第一个统计了12个id为1的，allTheSameCount统计了12个id为1的，则allTheSameCount+=1，当第二个统计也是12个id为1的则跳过，若时12个id为2的才allTheSameCount+=1
        # 统计所有suit下components下的item
        # wuxingshi_level==1 且 wuxingshi_affix>0 则 1attrCount+=1，否则wuxingshi_level==1,1Count+=1
        # wuxingshi_level==2 且 wuxingshi_affix>0 则 2attrCount+=1，否则wuxingshi_level==2,2Count+=1
        # wuxingshi_level==3 且 wuxingshi_affix>0 则 3attrCount+=1，否则wuxingshi_level==3,3Count+=1
        shenqi = {
            "same9Count": 0,
            "allTheSameCount":0,
            "1Count": 0,
            "1attrCount": 0,
            "2Count": 0,
            "2attrCount": 0,
            "3Count": 0,
            "3attrCount": 0
        }

        try:
            shenqi_data = json.loads(data.get('shenqi_json', '{}'))
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
                            id_counts[wuxing_id] = id_counts.get(wuxing_id, 0) + 1
                
                # 检查是否有12个相同的id
                for wuxing_id, count in id_counts.items():
                    if count >= 12 and wuxing_id not in counted_ids:
                        shenqi['allTheSameCount'] += 1
                        counted_ids.add(wuxing_id)
                        break  # 找到一个12个的就跳出循环
                    elif count >= 9 and wuxing_id not in counted_ids:
                        shenqi['same9Count'] += 1
                        counted_ids.add(wuxing_id)
                        break  # 找到一个9个的就跳出循环

                # 统计五行等级和属性
                for component in suit.get('components', []):
                    for wuxing in component.get('wuxing', []):
                        level = wuxing.get('wuxingshi_level', 0)
                        affix = wuxing.get('wuxingshi_affix', 0)
                        
                        if level == 1:
                            if affix > 0:
                                shenqi['1attrCount'] += 1
                            else:
                                shenqi['1Count'] += 1
                        elif level == 2:
                            if affix > 0:
                                shenqi['2attrCount'] += 1
                            else:
                                shenqi['2Count'] += 1
                        elif level == 3:
                            if affix > 0:
                                shenqi['3attrCount'] += 1
                            else:
                                shenqi['3Count'] += 1

        except Exception as e:
            self.logger.error(f"神器统计失败: {e}")
            print(f"错误详情: {str(e)}")

        # 将浮点数转换为整数
        def safe_float_to_int(value, default=0):
            if value is None:
                return default
            try:
                return int(float(value))
            except (ValueError, TypeError):
                return default

        all_new_point = safe_float_to_int(data.get('all_new_point'))
        features = {
            'level': safe_float_to_int(data.get('level')),  # 等级
            'sum_exp': safe_float_to_int(data.get('sum_exp')),  # 总经验(亿)
            'three_fly_lv': safe_float_to_int(data.get('three_fly_lv')),  # 化圣等级
            'school_history_count': schoolHistoryCount,  # 历史门派个数
            'all_new_point': all_new_point,  # 乾元丹
            'qianyuandan_breakthrough': qianyuandanBreakthrough,  # 乾元丹突破
            'jiyuan_amount': safe_float_to_int(data.get('jiyuan_amount')) + safe_float_to_int(data.get('add_point')),   # 月饼粽子机缘
            'packet_page': safe_float_to_int(data.get('packet_page')),  # 行囊拓展
            'xianyu_amount': safe_float_to_int(data.get('xianyu_amount')),  # 仙玉
            'learn_cash': safe_float_to_int(data.get('learn_cash')),  # 储备金
            'hight_grow_rider_count': hightGrowRiderCount,
            'allow_pet_count': safe_float_to_int(data.get('allow_pet_count')),  # 最大召唤兽携带数量
            'premium_fabao_count': premiumFabaoCount,  # 高价值法宝数量
            'shenqi': shenqi
        }
        features.update(shenqi)
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
            max_expt5 = data.get('max_expt5', 0)
            
            features['max_expt1'] = max_expt1
            features['max_expt2'] = max_expt2
            features['max_expt3'] = max_expt3
            features['max_expt4'] = max_expt4
            features['max_expt5'] = max_expt5
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
            features['max_expt5'] = 0
            features['beast_ski1'] = 0
            features['beast_ski2'] = 0
            features['beast_ski3'] = 0
            features['beast_ski4'] = 0
            features['yushoushu_skill'] = 0
        return features

    def _extract_skill_features(self, data):
        """提取技能体系特征"""
        features = {
            'school_skills': [0, 0, 0, 0, 0, 0, 0],
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
                features['school_skills'] = skill_levels
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

                if life_skill_levels:
                    features['life_skills'] = life_skill_levels

        except Exception as e:
            self.logger.error(f"提取技能特征失败: {e}")

        return features

    def _extract_equipment_features(self, data):
        """提取装备特征体系"""
        features = {
            'total_gem_level': 0,
            'premium_skill_count': 0,
            'set_bonus_count': 0,
            'total_equip_score': 0
        }

        try:
            equips_raw = data.get('all_equip_json_desc', '{}')
            if not equips_raw or equips_raw == '':
                equips = {}
            else:
                try:
                    equips = json.loads(equips_raw)
                    equips = equips.get('人物装备')
                except (json.JSONDecodeError, TypeError):
                    equips = {}
            if not isinstance(equips, list):
                return features
            for equip in equips:
                if not isinstance(equip, dict):
                    continue
                  # 宝石等级
                features['total_gem_level'] += equip['属性'].get('锻炼等级', 0)
                # 特技统计
                if equip['属性'].get('特技') in self.premium_skills:
                    features['premium_skill_count'] += 1
                # 套装统计
                if equip['属性'].get('套装效果'):
                    features['set_bonus_count'] += 1

            # 计算平均值
            if equips:
                features['avg_gem_level'] = features['total_gem_level'] / \
                    len(equips)
        except Exception as e:
            self.logger.warning(f"装备特征提取失败: {e}")
        return features

    def _extract_pet_features(self, data):
        """提取召唤兽特征"""
        features = {
            'premium_pet_count': 0,
            'total_pet_score': 0,
            'max_pet_score': 0,
            'lingyou_count': 0
        }
        try:
            pets_raw = data.get('all_pets_json', '[]')
            if not pets_raw or pets_raw == '':
                pets = []
            else:
                try:
                    pets = json.loads(pets_raw)
                except (json.JSONDecodeError, TypeError):
                    pets = []
            if not isinstance(pets, list):
                return features
            for pet in pets:
                if not isinstance(pet, dict):
                    continue
                # 获取宝宝等级
                pet_level = pet['详细信息'].get('等级', 0)
                if pet_level < 100:  # 跳过100级以下的宝宝
                    continue
                # 特殊技能统计
                if any(skill in pet.get('技能', []) for skill in self.premium_pet_skills):
                    features['premium_pet_count'] += 1
                # 宝宝评分
                pet_score = self._calculate_pet_score(pet)
                features['total_pet_score'] += pet_score
                features['max_pet_score'] = max(
                    features['max_pet_score'], pet_score)
            # 计算平均值
            if pets:
                features['avg_pet_score'] = features['total_pet_score'] / \
                    len(pets)
        except Exception as e:
            self.logger.warning(f"召唤兽特征提取失败: {e}")

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
                return features
            lingyou_count = 0
            for pet in pets:
                skills = pet.get('all_skills', [])
                for skill in skills:
                    if skill['name'] == '灵佑':
                        lingyou_count += skill.get('value', 0)
            features['lingyou_count'] = lingyou_count
        except Exception as e:
            self.logger.warning(f"特殊宠物特征提取失败: {e}")
        return features

    def _extract_appearance_features(self, character_data):
        """提取外观特征"""
        features = {}

        try:
            # 处理锦衣数据
            skins = character_data.get('skins', {})
            if isinstance(skins, dict):
                limited_skins = skins.get('锦衣', {}).get('限量', [])
                if isinstance(limited_skins, list):
                    features['limited_skin_value'] = len(limited_skins)
                else:
                    features['limited_skin_value'] = 0
            else:
                features['limited_skin_value'] = 0

        except Exception as e:
            self.logger.error(f"提取外观特征失败: {e}")
            features['limited_skin_value'] = 0

        return features

    def _extract_market_features(self, data):
        """提取市场行为特征"""
        features = {
            'hours_listed': 0,
            'collect_num': 0,
        }

        # 上架时间（小时）
        # expire_time是上架过期的时间 "2025-06-13 21:28:50" 上架时间固定是14天正的
        # 已上架时间（小时） = 14天*24 - (上架过期时间 - 现在时间).总小时数
        if 'expire_time' in data:
            expire_time = datetime.strptime(
                data['expire_time'], '%Y-%m-%d %H:%M:%S')
            now = datetime.now()
            time_until_expire = expire_time - now
            hours_until_expire = time_until_expire.total_seconds() / 3600
            # features['hours_listed'] = (14 * 24) - hours_until_expire

        # 收藏
            # features['collect_num'] = data.get('collect_num', 0)

        return features

    def _parse_ascension(self, ascension_str):
        """解析化圣等级"""
        if not ascension_str:
            return 0
        match = re.search(r'化圣(\d+)', ascension_str)
        return int(match.group(1)) if match else 0

    def _parse_money(self, money_str):
        """解析金钱字符串为数值"""
        if not money_str:
            return 0
        return int(money_str.replace(',', ''))

    def _parse_cultivation(self, cult_str):
        """解析修炼字符串"""
        if not cult_str:
            return 0
        match = re.search(r'(\d+)/\d+', cult_str)
        return int(match.group(1)) if match else 0

    def _calculate_pet_score(self, pet):
        """计算宝宝评分"""
        if not isinstance(pet, dict):
            return 0

        # 基础资质评分
        base_score = (
            pet['资质'].get('攻击资质', 0) +
            pet['资质'].get('速度资质', 0) +
            pet['资质'].get('防御资质', 0)
        ) / 3

        # 成长系数
        growth = pet['详细信息'].get('成长', 1.0)

        # 技能数量
        skill_count = len(pet.get('技能', []))

        # 特殊技能加成
        special_skill_bonus = sum(
            2 for skill in pet.get('技能', [])
            if skill in self.premium_pet_skills
        )

        return base_score * growth * (1 + 0.1 * skill_count) * (1 + 0.2 * special_skill_bonus)
