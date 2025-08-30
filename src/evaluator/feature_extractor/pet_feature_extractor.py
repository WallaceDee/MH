import json
import logging
from typing import Dict, Any, Union, List

# 配置日志
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class PetFeatureExtractor:
    """梦幻西游召唤兽特征提取器"""

    def __init__(self):
        """初始化特征提取器"""
        print("初始化特征提取器...")
        self.logger = logging.getLogger(__name__)

    def extract_features(self, equip_data: Dict[str, Any]) -> Dict[str, Union[int, float, str]]:
        """
        提取所有特征
        共使用了equip_data以下13个字段：
            `role_grade_limit` - 角色等级限制

            `equip_level` - 装备等级

            `growth` - 成长值

            `is_baobao` - 是否宝宝

            `all_skill` - 所有技能（字符串）

            `evol_skill_list` - 进化技能列表（JSON数组）

            `texing` - 特性信息（JSON对象）

            `lx` - 灵性值

            `equip_list` - 装备列表（JSON数组）

            `equip_list_amount` - 装备列表金额

            `neidan` - 内丹信息（JSON数组）

            `equip_sn` - 装备序列号
            
            `price` - 价格

        Returns:
            Dict[str, Union[int, float, str]]: 提取的特征字典，包含以下字段:
            
            基础属性特征:
                - role_grade_limit: int - 角色等级限制
                - equip_level: int - 装备等级
                - growth: float - 成长值
                - is_baobao: bool - 是否宝宝（True/False）
            
            技能特征:
                - all_skill: str - 所有技能字符串
                - skill_count: int - 技能数量
                - evol_skill_list_count: List[int] - 进化技能统计 [A级技能数, B级技能数]
                - evol_skill_list_value: int - 进化技能价值评分（A级×3 + B级×10）
            
            进阶信息特征:
                - lx: int - 灵性值
                - texing: int - 特性等级（1表示S/A级，0表示其他）
            
            装备特征:
                - equip_count: int - 有效装备数量（前3个装备中非null的个数）
                - equip_list_amount: int - 装备列表金额
            
            内丹特征:
                - neidan_count: int - 内丹数量
        """
        try:
            features = {}

            # 一、基础属性特征
            features.update(self._extract_basic_features(equip_data))

            # 二、技能
            features.update(self._extract_skill_features(equip_data))

            # 三、进阶信息
            features.update(self._extract_advanced_features(equip_data))

            # 四、装备
            features.update(self._extract_equip_features(equip_data))

            # 五、内丹
            features.update(self._extract_neidan_features(equip_data))

            return features

        except Exception as e:
            print(f"特征提取失败: {str(e)}")
            import traceback
            print(traceback.format_exc())
            raise

    def _extract_basic_features(self, equip_data: Dict[str, Any]) -> Dict[str, Union[int, float]]:
        """
        基础属性
        """
        features = {}
        
        # 处理role_grade_limit映射
        raw_role_grade_limit = equip_data.get('role_grade_limit', 0)
        features['role_grade_limit'] = self._map_role_grade_limit(raw_role_grade_limit)
        
        features['equip_level'] = equip_data.get('equip_level', 0)
        features['growth'] = equip_data.get('growth', 0)
        features['is_baobao'] = equip_data.get('is_baobao', '否') == '是'
        return features
    
    def _map_role_grade_limit(self, raw_value: int) -> int:
        """
        处理role_grade_limit值：只保留后三位
        65=>65, 105=>105, 10125=>125, 20155=>155, 30175=>175
        """
        # 将数字转换为字符串，然后取后三位
        str_value = str(raw_value)
        if len(str_value) <= 3:
            # 如果数字长度小于等于3位，直接返回
            return raw_value
        else:
            # 取后三位
            last_three = str_value[-3:]
            return int(last_three)

    def _extract_skill_features(self, equip_data: Dict[str, Any]) -> Dict[str, Union[int, float]]:
        """
        技能
        """
        features = {}
        features['all_skill'] = equip_data.get('all_skill', '')
        features['skill_count'] = len(
            equip_data.get('all_skill', '').split('|'))
        # 获取增强技能
        # evol_skill_list:[{"skill_type": "424", "level": 1, "icon": "https://cbg-xyq.res.netease.com/images/skill/0424.gif", "evol_type": "424", "name": "超级魔之心（进化后获得）", "desc": "#G造成的法术伤害提高25%。#r#W——纳浩瀚魔息入心，施天下无双之法。", "cifuIcon": "https://cbg-xyq.res.netease.com/images/skill/55424.gif", "hlightLight": true}, {"skill_type": "426", "level": 1, "icon": "https://cbg-xyq.res.netease.com/images/skill/0426.gif", "evol_type": "426", "name": "超级奔雷咒（进化后获得）", "desc": "#G发动超级雷属性法术攻击多个敌人；#r对主目标造成的伤害提高10%，并有25%几率附弱点雷两回合；#r攻击人数=自身等级/30+1，最多3人；#r#W——九天落雷，万马齐喑。", "cifuIcon": "https://cbg-xyq.res.netease.com/images/skill/55426.gif", "hlightLight": true}, {"skill_type": "431", "level": 1, "icon": "https://cbg-xyq.res.netease.com/images/skill/0431.gif", "evol_type": "431", "name": "超级土属性吸收（进化后获得）", "desc": "#G必定免受土属性法术伤害，并按应受伤害的大小恢复气血；#r#W——土造吾主筋骨。", "cifuIcon": "https://cbg-xyq.res.netease.com/images/skill/55431.gif", "hlightLight": false}, {"skill_type": "629", "level": 1, "icon": "https://cbg-xyq.res.netease.com/images/skill/0629.gif", "evol_type": "629", "name": "超级盾气（进化后获得）", "desc": "#G第2回合及以后进入战斗时，增加等级×2的防御持续5回合，且逐回合减少20%效果；#r在场时主人获得“盾气”，最多持续5回合；#r#R隐身时不触发本效果。#r#W——有正气护体，可力挽狂势。", "cifuIcon": "https://cbg-xyq.res.netease.com/images/skill/55629.gif", "hlightLight": false}]
        # hlightLight为true且heightCifuIcon有值的技能数,hlightLight为true且cifuIcon有值的技能数为A
        # hlightLight为true且cifuIcon有值的技能数,hlightLight为true且cifuIcon有值的技能数为B 
        # features['evol_skill_list_count'] = [A,B]
        evol_skill_list_data = equip_data.get('evol_skill_list', '[]')
        
        # 处理evol_skill_list字段，可能是字符串或列表
        if isinstance(evol_skill_list_data, str):
            try:
                evol_skill_list = json.loads(evol_skill_list_data)
            except (json.JSONDecodeError, TypeError):
                evol_skill_list = []
        elif isinstance(evol_skill_list_data, list):
            evol_skill_list = evol_skill_list_data
        else:
            evol_skill_list = []
        
        # 过滤出hlightLight为true的技能
        evol_skill_list = [skill for skill in evol_skill_list if skill.get('hlightLight', False)]
        
        # features['evol_skill_list'] = evol_skill_list
        features['evol_skill_list_count'] = [len([skill for skill in evol_skill_list if skill.get('heightCifuIcon', '')]), len([skill for skill in evol_skill_list if skill.get('cifuIcon', '')])]
        features['evol_skill_list_value'] = 0
        # 使用索引明确区分A级和B级技能
        for i, count in enumerate(features['evol_skill_list_count']):
            if i == 0:  # 蓝色A级技能
                features['evol_skill_list_value'] += count * 3
            else:  # 红色B级技能
                features['evol_skill_list_value'] += count * 10
        return features

    def _extract_advanced_features(self, equip_data: Dict[str, Any]) -> Dict[str, Union[int, float]]:
        """
        进阶信息
      
        """
        texing2Level =  {
            # ===== S级：顶级战术特性（5种）=====
            "逆境": "S",    # 己方≥4封印时100%解全体
            "力破": "S",    # 最高忽视240防御（点杀核心）
            "灵刃": "S",    # 进场物理伤害+50%
            "灵法": "S",    # 进场法术伤害+50%
            "瞬法": "S",    # 出场自动释放法术（收割神技）

            # ===== A级：高价值特性（7种）=====
            "瞬击": "A",    # 进场必攻气血最低单位
            "争锋": "A",    # 对召唤兽伤害+20%
            "顺势": "A",    # 对气血<70%单位法伤+180
            "护佑": "A",    # 出场30%概率给主人加护盾
            "御风": "A",    # 速度+10%（先手核心）
            "洞察": "A",    # 无视隐身（战术克制）
            "巧劲": "A",    # 物理伤害结果+8%

            # ===== B级：实用功能特性（10种）=====
            "复仇": "B",    # 主人倒地100%反击
            "阳护": "B",    # 减死亡禁锢2回合
            "灵断": "B",    # 无视神佑/鬼魂
            "抗法": "B",    # 法术抵抗+15%
            "抗物": "B",    # 物理抵抗+15%
            "识药": "B",    # 药品效果+20%
            "怒吼": "B",    # 出场提升队友物伤5%
            "鼓舞": "B",    # 出场提升队友法伤5%
            "荆棘": "B",    # 反伤15%所受物理伤害
            "天道": "B",    # 对玩家单位伤害+10%

            # ===== C级：特殊场景特性（6种）=====
            "吮魔": "C",    # 普攻吸蓝（损失气血5%）
            "识物": "C",    # 套装触发率+16%
            "弑神": "C",    # 对神佑过单位法伤+180
            "狠毒": "C",    # 攻击中毒单位伤害+12%
            "易怒": "C",    # 气血<30%时伤害+15%
            "暗劲": "C",    # 属性吸收时限制回血

            # ===== D级：低价值特性（5种）=====
            "自恋": "D",    # 击杀后炫耀（无加成）
            "乖巧": "D",    # 巫医费用-20%
            "预知": "D",    # 战斗喊话（全属性-2%）
            "灵动": "D",    # 战斗交流（全属性-2%）
            "独行": "D"     # 无其他召唤兽时伤害+10%
        }
        features = {}
        texing_data = equip_data.get('texing', '{}')
        
        # 处理texing字段，可能是字符串或字典
        if isinstance(texing_data, str):
            try:
                texing_obj = json.loads(texing_data)
            except (json.JSONDecodeError, TypeError):
                texing_obj = {}
        elif isinstance(texing_data, dict):
            texing_obj = texing_data
        else:
            texing_obj = {}
        
        texing = texing_obj.get('name', '')
        features['lx'] = equip_data.get('lx', 0)
        
        # 获取特性等级，S级和A级记录为1，其他为0
        texing_level = texing2Level.get(texing, 'D')
        features['texing'] = 1 if texing_level in ['S', 'A'] else 0
        return features

    def _extract_equip_features(self, equip_data: Dict[str, Any]) -> Dict[str, Union[int, float]]:
        """
        装备
        """
        features = {}
        # 获取装备列表，前三个是装备（武器、防具、饰品），第四个是饰品
        equip_list = equip_data.get('equip_list', '[]')
        
        # 如果equip_list是字符串，尝试解析为列表
        if isinstance(equip_list, str):
            try:
                equip_list = json.loads(equip_list)
            except (json.JSONDecodeError, TypeError):
                equip_list = []
        
        # 确保equip_list是列表
        if not isinstance(equip_list, list):
            equip_list = []
        
        # 只计算前三个装备中不是null的有效个数
        valid_equip_count = 0
        for i in range(min(3, len(equip_list))):
            if equip_list[i] is not None and equip_list[i] != 'null':
                valid_equip_count += 1
        
        features['equip_count'] = valid_equip_count
        
        # 提取套装效果
        # features.update(self._extract_suit_effect(equip_list))
        # 取消套装提取，equip_list_amount代替
        features['equip_list_amount'] = equip_data.get('equip_list_amount', 0)
        return features
    
    def _extract_suit_effect(self, equip_list: List[Any]) -> Dict[str, Union[int, float]]:
        """
        提取装备套装效果
        """
        features = {}
        # 用于存储套装效果及其出现次数
        suit_effects = {}
        
        # 遍历装备数组，提取套装效果
        for equip in equip_list:
            if equip and isinstance(equip, dict) and 'desc' in equip:
                desc = equip['desc']
                if desc:
                    # 匹配套装效果：套装效果：附加状态 + 技能名称
                    # 使用正则表达式匹配套装效果
                    import re
                    # 匹配格式：#c4DBAF4套装效果：附加状态#c4DBAF4技能名称#Y#Y
                    suit_match = re.search(r'套装效果：附加状态#c4DBAF4([^#]+)', desc)
                    if suit_match:
                        suit_name = suit_match.group(1).strip()
                        suit_effects[suit_name] = suit_effects.get(suit_name, 0) + 1
        
        # 检查是否有达到3件套的效果
        for suit_name, count in suit_effects.items():
            if count >= 3:
                features['suit_effect'] = 1  # 有完整套装效果
                features['suit_name'] = suit_name
                break
        else:
            # 如果没有达到3件套，记录最高件数
            features['suit_effect'] = 0  # 没有完整套装效果
            features['suit_name'] = ''
        
        return features

    def _extract_neidan_features(self, equip_data: Dict[str, Any]) -> Dict[str, Union[int, float]]:
        """
        内丹
        """
        features = {}
        neidan_data = equip_data.get('neidan', '[]')
        
        # 处理neidan字段，可能是字符串或列表
        if isinstance(neidan_data, str):
            try:
                neidan = json.loads(neidan_data)
            except (json.JSONDecodeError, TypeError):
                neidan = []
        elif isinstance(neidan_data, list):
            neidan = neidan_data
        else:
            neidan = []
        
        features['neidan_count'] = len(neidan)
        return features