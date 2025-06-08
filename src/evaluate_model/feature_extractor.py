import json
import re
import numpy as np
from datetime import datetime
import logging

class FeatureExtractor:
    """梦幻西游账号特征提取器"""
    
    def __init__(self):
        self.logger = logging.getLogger(__name__)
        
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

    def extract_features(self, character_data):
        """提取所有特征"""
        try:
            features = {}
            
            # 一、基础属性特征
            features.update(self._extract_basic_features(character_data))
            
            # 二、修炼与控制力特征
            features.update(self._extract_cultivation_features(character_data))
            
            # 三、技能体系特征
            features.update(self._extract_skill_features(character_data))
            
            # 四、装备特征体系
            features.update(self._extract_equipment_features(character_data))
            
            # 五、召唤兽特征
            features.update(self._extract_pet_features(character_data))
            
            # 六、外观与增值特征
            features.update(self._extract_appearance_features(character_data))
            
            # 七、市场行为特征
            features.update(self._extract_market_features(character_data))
            
            return features
            
        except Exception as e:
            self.logger.error(f"特征提取失败: {e}")
            raise

    def _extract_basic_features(self, data):
        """提取基础属性特征"""
        features = {
            'level': data.get('level', 0), # 等级
            'sum_exp': data.get('sum_exp', 0),  # 总经验(亿)
            'three_fly_lv': data.get('three_fly_lv', 0),  # 化圣等级
            # 'nine_fight_level': data.get('nine_fight_level', 0),  # 生死劫等级
            'cash': data.get('cash', 0),  # 现金
            # 'learn_cash': data.get('learn_cash', 0),  # 储备金
            # 'nuts_num': data.get('nuts_num', 0),  # 潜能果数量
            # 'dup_score':data.get('dup_score', 0) , # 副本评分
            # 'shenqi_score':data.get('shenqi_score', 0) # 神器评分
        }
        return features

    def _extract_cultivation_features(self, data):
        """提取修炼与控制力特征"""
        features = {}
        
        # 人物修炼
        total_cultivation = 0
        
        total_cultivation = data.get('expt_ski1', 0) +data.get('expt_ski2', 0) +data.get('expt_ski3', 0) +data.get('expt_ski4', 0)
        features['expt_ski5'] = data.get('expt_ski5', 0)
        features['total_cultivation'] = total_cultivation
        features['cultivation_completion'] = total_cultivation / (25 * 4)  # 修炼完成度
        
        total_beast_ski = data.get('beast_ski1', 0) +data.get('beast_ski2', 0) +data.get('beast_ski3', 0) +data.get('beast_ski4', 0)
        features['total_beast_ski'] = total_beast_ski
        features['beast_ski_completion'] = total_beast_ski / (25 * 4)  # 控制力完成度
        
        return features

    def _extract_skill_features(self, data):
        """提取技能体系特征"""
        features = {}
        
        # 师门技能
        skills = data.get('school_skills', {})
        if isinstance(skills, str):
            try:
                skills = json.loads(skills)
            except Exception:
                skills = {}
        if skills:
            skill_levels = [int(level) for level in skills.values()]
            features['avg_skill_level'] = np.mean(skill_levels)
            # 计算标准差前判断数据量
            if len(skill_levels) > 1:
                features['skill_std'] = np.std(skill_levels)  # 技能均衡度
            else:
                features['skill_std'] = 0.0  # 只有一个值时，标准差为0
        
        # 生活技能
        life_skills = data.get('life_skills', {})
        if isinstance(life_skills, str):
            try:
                life_skills = json.loads(life_skills)
            except Exception:
                life_skills = {}
        if life_skills:
            features['神速'] = life_skills.get('神速', 0)
            features['强壮'] = life_skills.get('强壮', 0)
            # 排除神速和强壮后再进行计算
            life_skills.pop('神速', None)
            life_skills.pop('强壮', None)
            top_skills = sorted(life_skills.items(), key=lambda x: x[1], reverse=True)[:5]
            features['top_life_skills'] = sum(level for _, level in top_skills)

        return features

    def _extract_equipment_features(self, data):
        """提取装备特征体系"""
        features = {
            'total_gem_level': 0,
            'premium_skill_count': 0,
            'set_bonus_count': 0,
            'total_equip_score': 0
        }
        # TODO: 装备特征提取
        try:
            equips_raw = data.get('all_equip_json_desc', '[]')
            if not equips_raw:
                equips = {}
            else:
                equips = json.loads(equips_raw)
                equips = equips['人物装备']
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
                features['avg_gem_level'] = features['total_gem_level'] / len(equips)
        except (json.JSONDecodeError, TypeError) as e:
            self.logger.warning(f"装备特征提取失败: {e}")
        return features

    def _extract_pet_features(self, data):
        """提取召唤兽特征"""
        features = {
            'premium_pet_count': 0,
            'total_pet_score': 0,
            'max_pet_score': 0
        }
        try:
            pets_raw = data.get('pets_json', '[]')
            if not pets_raw:
                pets = []
            else:
                pets = json.loads(pets_raw)
            if not isinstance(pets, list):
                return features
            for pet in pets:
                if not isinstance(pet, dict):
                    continue
                # 特殊技能统计
                if any(skill in pet.get('skills', []) for skill in self.premium_pet_skills):
                    features['premium_pet_count'] += 1
                # 宝宝评分
                pet_score = self._calculate_pet_score(pet)
                features['total_pet_score'] += pet_score
                features['max_pet_score'] = max(features['max_pet_score'], pet_score)
            # 计算平均值
            if pets:
                features['avg_pet_score'] = features['total_pet_score'] / len(pets)
        except (json.JSONDecodeError, TypeError) as e:
            self.logger.warning(f"召唤兽特征提取失败: {e}")
        return features

    def _extract_appearance_features(self, data):
        """提取外观与增值特征"""
        features = {
            'limited_skin_value': 0,
            'achievement_points': data.get('achievement_points', 0),
            'jade_points': data.get('jade_points', 0)
        }
        try:
            skins_raw = data.get('skins_json', '[]')
            if not skins_raw:
                skins = []
            else:
                skins = json.loads(skins_raw)
            if isinstance(skins, list):
                for skin in skins:
                    if isinstance(skin, dict) and skin.get('name') in self.limited_skin_values:
                        features['limited_skin_value'] += self.limited_skin_values[skin['name']]
            # 成就点价值 (0.5元/点)
            features['achievement_value'] = features['achievement_points'] * 0.5
            # 仙玉积分价值 (0.3元/分)
            features['jade_value'] = features['jade_points'] * 0.3
        except (json.JSONDecodeError, TypeError) as e:
            self.logger.warning(f"外观特征提取失败: {e}")
        return features

    def _extract_market_features(self, data):
        """提取市场行为特征"""
        features = {
            'days_listed': 0,
            'collect_rate': 0,
            'server_heat': 1.0
        }
        
        # 上架天数
        if 'list_time' in data:
            list_time = datetime.strptime(data['list_time'], '%Y-%m-%d %H:%M:%S')
            features['days_listed'] = (datetime.now() - list_time).days
        
        # 收藏转化率
        views = data.get('views', 0)
        collects = data.get('collects', 0)
        if views > 0:
            features['collect_rate'] = collects / views
        
        # 服务器热度
        server = data.get('server', '')
        features['server_heat'] = self.school_heat.get(server, 1.0)
        
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
            pet.get('attack_aptitude', 0) +
            pet.get('defense_aptitude', 0) +
            pet.get('speed_aptitude', 0)
        ) / 3
        
        # 成长系数
        growth = pet.get('growth', 1.0)
        
        # 技能数量
        skill_count = len(pet.get('skills', []))
        
        # 特殊技能加成
        special_skill_bonus = sum(
            2 for skill in pet.get('skills', [])
            if skill in self.premium_pet_skills
        )
        
        return base_score * growth * (1 + 0.1 * skill_count) * (1 + 0.2 * special_skill_bonus)
