# 装备估价系统常量配置

## 文件结构

```
constant/
├── __init__.py          # 配置加载器主模块
├── config.jsonc         # 主配置文件（套装、特效、装备常量）
├── weapon.jsonc         # 武器配置（伤害标准、附加属性标准）
├── lingshi.jsonc        # 灵石配置（各等级属性范围）
├── jade.jsonc           # 玉佩配置（各类型属性范围）
├── pet_equip.jsonc      # 召唤兽装备配置（各等级属性标准）
├── test_config.py       # 配置测试文件
└── README.md            # 说明文档
```

## 配置文件格式

使用JSONC格式（JSON with Comments），支持`//`开头的注释行。

## 使用方法

### 1. 直接导入函数

```python
from .constant import get_high_value_suits, get_important_effects

# 获取高价值套装ID列表
high_value_suits = get_high_value_suits()

# 获取重要特效ID列表
important_effects = get_important_effects()
```

### 2. 导入完整配置

```python
from .constant import get_config, get_weapon_config, get_lingshi_config

# 获取主配置
config = get_config()

# 获取武器配置
weapon_config = get_weapon_config()

# 获取灵石配置
lingshi_config = get_lingshi_config()
```

## 配置结构

### 主配置 (config.jsonc)
```json
{
  "suits": {
    "agility": [...],           // 敏捷套装ID列表
    "magic": [...],             // 魔力套装ID列表
    "high_value": [...],        // 高价值套装ID列表
    "precise_filter": [...],    // 精确筛选套装ID列表
    "agility_detailed": {       // 敏捷套详细分类
      "B": [...],               // B级敏捷套：凤凰, 幽灵, 吸血鬼
      "A": [...]                // A级敏捷套：画魂, 雾中仙, 机关鸟, 巴蛇, 猫灵（人型）, 修罗傀儡妖
    },
    "magic_detailed": {         // 魔力套详细分类
      "B": [...],               // B级魔力套：蛟龙, 雨师, 如意仙子, 星灵仙子, 净瓶女娲, 灵符女娲
      "A": [...]                // A级魔力套：灵鹤, 炎魔神, 葫芦宝贝, 混沌兽, 长眉灵猴, 蜃气妖
    }
  },
  "effects": {
    "high_value": [...],        // 高价值特效ID列表
    "important": [...],         // 重要特效ID列表
    "low_value": [...],         // 低价值特效ID列表
    "simple": 2                 // 简易装备特效编号
  },
  "equipment": {
    "high_value_simple_levels": [...],    // 高价值简易装备等级列表
    "low_value_special_skills": [...]     // 低价值特技ID列表
  }
}
```

### 武器配置 (weapon.jsonc)
- **init_damage_raw_standards**: 各等级初始伤害标准
- **all_damage_standards**: 各等级总伤害标准
- **addon_total_standards**: 各等级附加属性总和标准

### 灵石配置 (lingshi.jsonc)
- 按等级分类（60、80、100、120、140级）
- 每个等级包含主属性和附加属性的范围配置

### 玉佩配置 (jade.jsonc)
- 按类型分类（0、1类型）
- 每个类型包含主属性和附加属性的范围配置

### 召唤兽装备配置 (pet_equip.jsonc)
- 按等级分类（65-145级）
- 每个等级包含各属性的最大值标准

## 可用函数

### 主配置相关
- `get_agility_suits()` - 获取敏捷套装ID列表
- `get_magic_suits()` - 获取魔力套装ID列表
- `get_high_value_suits()` - 获取高价值套装ID列表
- `get_precise_filter_suits()` - 获取精确筛选套装ID列表
- `get_agility_suits_detailed()` - 获取敏捷套装详细分类
- `get_magic_suits_detailed()` - 获取魔力套装详细分类
- `get_agility_suits_b()` - 获取B级敏捷套装ID列表
- `get_agility_suits_a()` - 获取A级敏捷套装ID列表
- `get_magic_suits_b()` - 获取B级魔力套装ID列表
- `get_magic_suits_a()` - 获取A级魔力套装ID列表
- `get_high_value_effects()` - 获取高价值特效ID列表
- `get_important_effects()` - 获取重要特效ID列表
- `get_low_value_effects()` - 获取低价值特效ID列表
- `get_high_value_simple_levels()` - 获取高价值简易装备等级列表
- `get_low_value_special_skills()` - 获取低价值特技ID列表
- `get_simple_effect_id()` - 获取简易装备特效编号

### 装备配置相关
- `get_weapon_config()` - 获取武器配置
- `get_lingshi_config()` - 获取灵石配置
- `get_jade_config()` - 获取玉佩配置
- `get_pet_equip_config()` - 获取召唤兽装备配置

## 套装分类说明

### 敏捷套装分类
- **B级敏捷套**: 凤凰(1040)、幽灵(1047)、吸血鬼(1049)
- **A级敏捷套**: 画魂(1053)、雾中仙(1056)、机关鸟(1065)、巴蛇(1067)、猫灵人型(1070)、修罗傀儡妖(1077)

### 魔力套装分类
- **B级魔力套**: 蛟龙(1041)、雨师(1042)、如意仙子(1043)、星灵仙子(1046)、净瓶女娲(1050)、灵符女娲(1052)
- **A级魔力套**: 灵鹤(1057)、炎魔神(1059)、葫芦宝贝(1069)、混沌兽(1073)、长眉灵猴(1074)、蜃气妖(1081)

## 测试配置

运行测试文件验证配置是否正确加载：

```bash
cd src/evaluator/mark_anchor/equip/constant
python test_config.py
```

## 迁移说明

所有配置文件已从`plugins/`文件夹迁移到`constant/`文件夹，相关引用已更新为使用统一的配置加载接口。 