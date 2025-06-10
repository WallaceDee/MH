#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
物品解析器模块
负责处理梦幻西游CBG中所有与物品相关的数据解析
"""

import os
import re
import json
import logging
from typing import Dict, Any, Optional, List

# 导入统一配置加载器
try:
    from .config_loader import get_config_loader
except ImportError:
    # 如果相对导入失败，尝试绝对导入
    try:
        from config_loader import get_config_loader
    except ImportError:
        # 如果都失败，创建一个简单的替代函数
        def get_config_loader():
            return None


class EquipmentParser:
    """
    游戏物品描述文本解析器
    
    用于解析游戏中物品的文本描述，提取各种属性和效果。
    支持解析的内容包括：基础属性、特殊效果、符石、星位、熔炼效果等。
    
    示例用法：
        parser = EquipmentParser()
        result = parser.parse(equipment_text)
    """
    
    def __init__(self, logger=None):
        """初始化物品解析器"""
        self.logger = logger or logging.getLogger(__name__)
        self.config_loader = get_config_loader()
        if not self.config_loader:
            self.logger.warning("配置加载器不可用，将影响物品配置加载")
        
        # 配置缓存
        self._equip_config = None

        # 基础属性正则表达式
        self.level_pattern = r"等级\s+(\d+)"  # 等级
        self.element_pattern = r"五行\s+([木火水土金])"  # 五行属性
        self.durability_pattern = r"耐久度\s+(\d+)"  # 耐久度
        self.repair_fail_pattern = r"修理失败\s+(\d+)次"  # 修理失败次数
        self.forge_level_pattern = r"锻炼等级\s+(\d+)"  # 锻炼等级
        self.gem_pattern = r"镶嵌宝石\s+([^\s#]+)"  # 镶嵌宝石
        self.slot_pattern = r"开运孔数：(\d+)孔/(\d+)孔"  # 开运孔数
        
        # 基础属性映射
        self.basic_stats_pattern = {
            "气血": r"气血\s+\+(\d+)",
            "魔法": r"魔法\s+\+(\d+)",
            "命中": r"命中\s+\+(\d+)",
            "伤害": r"伤害\s+\+(\d+)",
            "防御": r"防御\s+\+(\d+)",
            "速度": r"速度\s+\+(\d+)",
            "灵力": r"灵力\s+\+(\d+)",
            "体质": r"体质\s+([+-]\d+)",
            "魔力": r"魔力\s+([+-]\d+)",
            "敏捷": r"敏捷\s+\+(\d+)",
            "躲避": r"法术防御\s+\+(\d+)",
            "法术伤害": r"法术伤害\s+\+(\d+)",
            "法术防御": r"法术防御\s+\+(\d+)",
            "固定伤害": r"法术防御\s+\+(\d+)"
        }
        
        # 特殊效果正则表达式
        self.special_effects_pattern = r"#c4DBAF4特效：#c4DBAF4([^#]+)"  # 特效
        self.special_skills_pattern = r"#c4DBAF4特技：#c4DBAF4([^#]+)"  # 特技
        self.suit_effect_pattern = r"套装效果：([^#]+)"  # 套装效果
        
        # 符石和星位正则表达式
        self.sigil_pattern = r"符石:\s+([^#]+)"  # 符石效果
        self.star_position_pattern = r"星位：([^#]+)"  # 星位效果
        self.sigil_combo_pattern = r"符石组合:\s+([^#\n]+)"  # 符石组合
        
        # 其他属性正则表达式
        self.creator_pattern = r"制造者：([^#]+)"  # 制造者
        self.melt_effect_pattern = r"熔炼效果：#r#Y#r([^#]+)"  # 熔炼效果
        self.active_lock_pattern = r"<active>(.*?)</active>"  # 活跃锁

    def process_character_equipment(self, parsed_data, character_name=None):
        """
        处理角色物品信息的主要入口方法
        包含解析、输出显示、数据处理等完整逻辑
        
        Args:
            parsed_data: 解析后的角色数据
            character_name: 角色名称，用于显示
            
        Returns:
            dict: 处理后的物品信息，可以直接保存到数据库
        """
        if not parsed_data or 'AllEquip' not in parsed_data:
            return {"物品总数": 0, "物品列表": [], "拆分销售装备": []}
        
        # 解析物品信息
        equip_info = self.parse_all_equip(parsed_data)
        
        # 计算并记录JSON长度
        json_length = len(json.dumps(equip_info, ensure_ascii=False))
        self.logger.debug(f"角色 {character_name or '未知'} 物品信息处理完成: {json_length} 字符")
        
        return equip_info
    
    def parse_all_equip(self, parsed_data):
        """
        解析所有物品数据
        """
        try:
            all_equip = parsed_data.get('AllEquip', {})
            equip_info = {
                "物品总数": 0,
                "人物装备": [],  # 人物装备列表
                "召唤兽装备": [],  # 召唤兽装备列表
                "其他物品": [],  # 其他物品列表
                "拆分销售装备": []
            }
            
            # 获取物品配置
            equip_config = self.load_equip_config()
            
            # 位置名称映射
            position_names = {
                1: "武器",
                2: "头盔",
                3: "项链",
                4: "衣服",
                5: "腰带",
                6: "鞋子",
                187: "戒指",
                188: "耳饰",
                189: "配饰",
                190: "手镯"
            }
            
            for pos_key, equip_data in all_equip.items():
                if isinstance(equip_data, dict):
                    # pos_key就是物品位置
                    try:
                        pos = int(pos_key)
                    except:
                        continue
                        
                    # 获取物品基本信息
                    equip_type = equip_data.get('iType', 0)
                    equip_sn = equip_data.get('equip_sn', '')
                    desc = equip_data.get('cDesc', '')
                    
                    equip_info["物品总数"] += 1
                    
                    # 解析物品属性
                    parsed_attrs = self.parse(desc)
                    
                    # 合并所有物品到一个列表
                    equip_summary = {
                        # 中文转换字段
                        "位置": pos,
                        "位置名称": position_names.get(pos, f"位置{pos}"),
                        "物品ID": equip_type,
                        "物品名称": equip_config.get(str(equip_type), f"物品_{equip_type}"),
                        "锁定状态": self.get_lock_status(equip_data),
                        "序列号": equip_sn,
                        "描述": desc,  # 添加cDesc到描述字段
                        "属性": parsed_attrs  # 属性
                    }
                    
                    # 根据装备等级判断类型
                    level = parsed_attrs.get('等级', 0)
                    if level % 10 == 0:  # 人物装备等级是10的倍数
                        equip_info["人物装备"].append(equip_summary)
                    elif level % 10 == 5:  # 召唤兽装备等级是5结尾
                        equip_info["召唤兽装备"].append(equip_summary)
                    else:
                        equip_info["其他物品"].append(equip_summary)
            
            return equip_info
            
        except Exception as e:
            self.logger.error(f"解析AllEquip失败: {e}")
            return {"物品总数": 0, "人物装备": [], "召唤兽装备": [], "其他物品": [], "拆分销售装备": []}

    def get_equip_name(self, equip_type):
        """
        根据物品类型ID获取物品名称
        """
        config = self.load_equip_config()
        equip_id_str = str(equip_type)
        return config.get(equip_id_str, f"物品_{equip_id_str}")
    
    def get_lock_status(self, equip_data):
        """
        获取物品锁定状态 (参考parse_role.js的get_lock_types实现)
        """
        locks = []
        
        # 参考parse_role.js的逻辑
        if equip_data.get('iLockActive'):
            locks.append("活跃锁定")
        if equip_data.get('iLockGreen'):
            locks.append("保护锁定")  
        if equip_data.get('iLock'):
            lock_val = equip_data.get('iLock')
            if lock_val == 1:
                locks.append("普通锁定")
            else:
                locks.append(f"锁定{lock_val}")
        if equip_data.get('iLockNew'):
            lock_val = equip_data.get('iLockNew')
            if lock_val == 1:
                locks.append("新锁定")
            else:
                locks.append(f"新锁定{lock_val}")
                
        return locks if locks else []

    def load_equip_config(self):
        """
        从ConfigLoader加载物品配置信息
        """
        if hasattr(self, '_equip_config') and self._equip_config:
            return self._equip_config
            
        if not self.config_loader:
            raise RuntimeError("ConfigLoader不可用")
            
        try:
            self._equip_config = self.config_loader.get_equipment_config()
            self.logger.debug(f"加载物品配置: {len(self._equip_config)}个物品")
        except Exception as e:
            self.logger.error(f"加载物品配置失败: {e}")
            raise e
            
        return self._equip_config 

    def _clean_color_tags(self, text: str) -> str:
        """
        清理文本中的颜色标记和多余的空白字符
        
        Args:
            text: 原始文本
            
        Returns:
            清理后的文本
        """
        # 移除颜色标记
        text = re.sub(r'#[rGYWcB][^#]*?(?=#|$)', '', text)
        text = re.sub(r'#c[0-9A-F]{6}', '', text)
        # 清理多余空白
        text = re.sub(r'\s+', ' ', text)
        return text.strip()

    def _extract_single_value(self, pattern: str, text: str) -> Optional[str]:
        """
        从文本中提取单个值
        
        Args:
            pattern: 正则表达式模式
            text: 原始文本
            
        Returns:
            匹配到的值，如果没有匹配则返回None
        """
        match = re.search(pattern, text)
        if match:
            value = match.group(1)
            return self._clean_color_tags(value)
        return None

    def _extract_basic_stats(self, text: str) -> Dict[str, Any]:
        """
        提取基础属性值
        
        Args:
            text: 原始文本
            
        Returns:
            包含基础属性及其值的字典
        """
        stats = {}
        # 保存原始文本作为详细信息
        stats["详细"] = self._clean_color_tags(text)
        
        # 找到开运孔数的位置作为基础属性的边界
        slot_match = re.search(self.slot_pattern, text)
        if slot_match:
            # 只处理开运孔数之前的内容
            text = text[:slot_match.start()]
        
        # 基础属性通常在文本开头的几个#r标记之间
        # 使用更严格的匹配规则
        basic_blocks = []
        current_block = []
        
        for line in text.split('#'):
            line = line.strip()
            if not line:
                continue
                
            # 基础属性块的特征：
            # 1. 以'r'开头
            # 2. 包含基础属性名称和加号
            # 3. 不包含特殊标记（如符石、星位等）
            if line.startswith('r'):
                # 检查是否包含基础属性
                has_basic_stat = any(stat in line for stat in self.basic_stats_pattern.keys() if stat != "详细")
                # 检查是否不包含特殊内容
                has_special_content = any(keyword in line for keyword in ['符石:', '星位：', '特效：', '特技：', '熔炼效果：'])
                
                if has_basic_stat and not has_special_content:
                    current_block.append(line)
                else:
                    if current_block:
                        basic_blocks.append(' '.join(current_block))
                        current_block = []
            else:
                if current_block:
                    basic_blocks.append(' '.join(current_block))
                    current_block = []
        
        if current_block:
            basic_blocks.append(' '.join(current_block))
        
        # 将所有基础属性块合并
        basic_stats_text = ' '.join(basic_blocks)
        
        # 在基础属性文本中提取属性
        for stat_name, pattern in self.basic_stats_pattern.items():
            if stat_name == "详细" or not pattern:
                continue
            if match := re.search(pattern, basic_stats_text):
                stats[stat_name] = int(match.group(1))
        
        return stats

    def _parse_special_effects(self, text: str) -> List[str]:
        """
        解析特殊效果
        
        Args:
            text: 原始文本
            
        Returns:
            特殊效果列表
        """
        effects = []
        if special_effects := self._extract_single_value(self.special_effects_pattern, text):
            # 分割并清理每个效果
            effects = [effect.strip() for effect in special_effects.split() if effect.strip()]
            # 移除重复
            effects = list(dict.fromkeys(effects))
        return effects

    def _parse_sigils(self, text: str) -> tuple[List[Dict[str, Any]], str]:
        """
        解析符石效果并返回清理后的文本
        
        Args:
            text: 原始文本
            
        Returns:
            tuple: (符石效果列表, 清理后的文本)
        """
        sigils = []
        cleaned_text = text
        
        # 查找所有符石
        matches = re.finditer(self.sigil_pattern, text)
        for match in matches:
            sigil_text = match.group(0)  # 获取完整的符石文本
            effect_text = match.group(1)
            effects = {}
            parts = effect_text.split()
            
            # 保存原始文本作为详细信息
            effects["详细"] = self._clean_color_tags(effect_text)
            
            current_stat = None
            for part in parts:
                if '+' in part:
                    if current_stat and current_stat != "详细":
                        try:
                            value = float(part.replace('+', '')) if '.' in part else int(part.replace('+', ''))
                            effects[current_stat] = value
                        except ValueError:
                            continue
                else:
                    current_stat = part.strip()
            
            if effects:
                sigils.append(effects)
                
            # 从文本中移除这个符石的完整文本
            cleaned_text = cleaned_text.replace(sigil_text, '')
            
        return sigils, cleaned_text

    def _parse_star_position(self, text: str) -> tuple[Dict[str, Any], str]:
        """
        解析星位效果并返回清理后的文本
        
        Args:
            text: 原始文本
            
        Returns:
            tuple: (星位效果字典, 清理后的文本)
        """
        star_effects = {}
        cleaned_text = text
        
        # 查找星位文本
        match = re.search(r'星位：[^#\n]+', text)
        if match:
            star_text = match.group(0)
            if star_position := self._extract_single_value(self.star_position_pattern, text):
                # 保存原始文本作为详细信息
                star_effects["详细"] = self._clean_color_tags(star_position)
                
                parts = star_position.split()
                current_stat = None
                for part in parts:
                    if '+' in part:
                        if current_stat and current_stat != "详细":
                            try:
                                value = float(part.replace('+', '')) if '.' in part else int(part.replace('+', ''))
                                star_effects[current_stat] = value
                            except ValueError:
                                continue
                    else:
                        current_stat = part.strip()
                        
            # 从文本中移除星位的完整文本
            cleaned_text = cleaned_text.replace(star_text, '')
                    
        return star_effects, cleaned_text

    def _parse_melt_effects(self, text: str) -> Dict[str, Any]:
        """
        解析熔炼效果
        
        Args:
            text: 原始文本
            
        Returns:
            熔炼效果字典
        """
        effects = {}
        if melt_text := self._extract_single_value(self.melt_effect_pattern, text):
            # 保存原始文本作为详细信息
            effects["详细"] = self._clean_color_tags(melt_text)
            
            # 使用正则表达式匹配属性名和数值
            pattern = r'([+\-]?\d+)([^+\-\d]+)'
            matches = re.finditer(pattern, melt_text)
            
            for match in matches:
                value = int(match.group(1))  # 数值部分
                attr = match.group(2).strip()  # 属性名部分
                if attr:
                    effects[attr] = value
                    
        return effects

    def _clean_active_lock(self, text: str) -> Optional[Dict[str, Any]]:
        """
        清理并格式化活跃锁信息
        
        Args:
            text: 原始文本
            
        Returns:
            活跃锁信息字典，如果没有则返回None
        """
        if not text or "活跃锁" not in text:
            return None
            
        result = {
            "详细": self._clean_color_tags(text)
        }
        
        # 提取关键信息
        match = re.search(r'解锁需在三界修行积累(\d+)活跃值，现已获得(\d+)活跃值', text)
        if match:
            total = int(match.group(1))
            current = int(match.group(2))
            result.update({
                "需要活跃值": total,
                "当前活跃值": current,
                "剩余活跃值": total - current
            })
        return result

    def _calculate_total_attributes(self, result: Dict[str, Any]) -> Dict[str, float]:
        """
        计算物品的总属性值（基础属性 + 符石属性 + 星位属性 + 熔炼效果）
        
        Args:
            result: 解析后的物品属性字典
            
        Returns:
            总属性值字典
        """
        total_attrs = {}
        
        # 添加基础属性
        if "基础属性" in result:
            for attr, value in result["基础属性"].items():
                if attr != "详细":
                    total_attrs[attr] = float(value)
        
        # 添加符石属性
        if "符石" in result:
            for sigil in result["符石"]:
                for attr, value in sigil.items():
                    if attr != "详细" and isinstance(value, (int, float)):
                        if attr in total_attrs:
                            total_attrs[attr] += float(value)
                        else:
                            total_attrs[attr] = float(value)
        
        # 添加星位属性
        if "星位" in result:
            for attr, value in result["星位"].items():
                if attr != "详细" and isinstance(value, (int, float)):
                    if attr in total_attrs:
                        total_attrs[attr] += float(value)
                    else:
                        total_attrs[attr] = float(value)
        
        # 添加熔炼效果
        if "熔炼效果" in result:
            for attr, value in result["熔炼效果"].items():
                if attr != "详细" and isinstance(value, (int, float)):
                    if attr in total_attrs:
                        total_attrs[attr] += float(value)
                    else:
                        total_attrs[attr] = float(value)
        
        return total_attrs

    def parse(self, text: str) -> Dict[str, Any]:
        """
        解析物品描述文本
        
        Args:
            text: 物品描述文本
            
        Returns:
            解析后的物品属性字典
        """
        result = {
            "详细": self._clean_color_tags(text)  # 保存完整的原始文本
        }
        
        # 用于提取基础属性的清理文本
        cleaned_text = text
        
        # 基础信息
        if level := self._extract_single_value(self.level_pattern, text):
            result["等级"] = int(level)
        if element := self._extract_single_value(self.element_pattern, text):
            result["五行"] = element
        if durability := self._extract_single_value(self.durability_pattern, text):
            result["耐久度"] = int(durability)
        if repair_fail := self._extract_single_value(self.repair_fail_pattern, text):
            result["修理失败"] = int(repair_fail)
        if forge_level := self._extract_single_value(self.forge_level_pattern, text):
            result["锻炼等级"] = int(forge_level)
        if gem := self._extract_single_value(self.gem_pattern, text):
            result["镶嵌宝石"] = gem
            
        # 先提取符石和星位相关的内容，同时获取清理后的文本
        sigils, cleaned_text = self._parse_sigils(cleaned_text)
        if sigils:
            result["符石"] = sigils
            
        star_effects, cleaned_text = self._parse_star_position(cleaned_text)
        if star_effects:
            result["星位"] = star_effects
            
        # 提取并移除符石组合信息
        if match := re.search(r'符石组合:[^#\n]+', cleaned_text):
            combo_text = match.group(0)
            if sigil_combo := self._extract_single_value(self.sigil_combo_pattern, combo_text):
                result["符石组合"] = sigil_combo.strip()
            cleaned_text = cleaned_text.replace(combo_text, '')
            
        # 基础属性（在移除符石相关内容后提取）
        basic_stats = self._extract_basic_stats(cleaned_text)
        if basic_stats:
            result["基础属性"] = basic_stats
        
        # 特殊效果
        effects = self._parse_special_effects(text)
        if effects:
            result["特效"] = effects
        if special_skills := self._extract_single_value(self.special_skills_pattern, text):
            result["特技"] = special_skills.strip()
        if suit_effect := self._extract_single_value(self.suit_effect_pattern, text):
            result["套装效果"] = suit_effect.strip()
            
        # 开运孔数
        if slot_match := re.search(self.slot_pattern, text):
            result["开运孔数"] = f"{slot_match.group(1)}/{slot_match.group(2)}"
            
        # 制造者
        if creator := self._extract_single_value(self.creator_pattern, text):
            result["制造者"] = creator.strip()
            
        # 熔炼效果
        melt_effects = self._parse_melt_effects(text)
        if melt_effects:
            result["熔炼效果"] = melt_effects
            
        # 活跃锁
        if active_lock := self._extract_single_value(self.active_lock_pattern, text):
            if clean_lock := self._clean_active_lock(active_lock):
                result["活跃锁"] = clean_lock
        
        # 计算总属性
        total_attrs = self._calculate_total_attributes(result)
        if total_attrs:
            result["总属性"] = total_attrs
            
        return result

def parse_equipment(text: str) -> Dict[str, Any]:
    """
    解析物品描述文本的便捷函数
    
    Args:
        text: 物品描述文本
        
    Returns:
        解析后的物品属性字典
    """
    parser = EquipmentParser()
    return parser.parse(text)

if __name__ == "__main__":
    # 测试用例
    test_cases = [
        """#r等级 100  五行 水#r防御 +57 气血 +639#r耐久度 396#r锻炼等级 10  镶嵌宝石 光芒石#Y#r#c4DBAF4套装效果：变身术之灵鹤#Y#Y#r#G开运孔数：4孔/4孔#G#r符石: 魔力 +1 气血 +10#n#G#r符石: 敏捷 +1#n#G#r符石: 敏捷 +1 灵力 +1.5#n#G#r符石: 伤害 +1.5#n#r#cEE82EE符石组合: 隔山打牛#r门派条件：无#r部位条件：无#r法术攻击时有25%的几率临时提升自身50点灵力#Y#r#W制造者：乳神用胸为你强化打造#Y#r#Y熔炼效果：#r#Y#r+1防御 +28气血 #r#Y  """
    ]
    
    print("\n物品解析测试")
    print("=" * 50)
    
    for i, test_text in enumerate(test_cases, 1):
        print(f"\n测试用例 {i}:")
        print("-" * 30)
        
        try:
            result = parse_equipment(test_text)
            formatted_json = json.dumps(result, ensure_ascii=False, indent=2)
            print(formatted_json)
        except Exception as e:
            print(f"解析错误: {e}")
            
        print("-" * 30) 