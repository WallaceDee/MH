"""
等级配置管理
"""

class LevelConfig:
    # 等级配置表
    LEVEL_CONFIGS = {
        89: {
            'base_price': 800,     # 空号基准价
            'max_cultivation': 13,  # 修炼上限
            'max_school_skill': 99  # 门派技能上限
        },
        109: {
            'base_price': 1800,
            'max_cultivation': 17,
            'max_school_skill': 119
        },
        129: {
            'base_price': 5500,
            'max_cultivation': 21,
            'max_school_skill': 150
        },
        159: {
            'base_price': 8000,
            'max_cultivation': 25,
            'max_school_skill': 164
        },
        175: {
            'base_price': 11000,
            'max_cultivation': 25,
            'max_school_skill': 180
        }
    }
    
    @classmethod
    def get_nearest_level_config(cls, level):
        """
        获取最接近的等级配置
        
        Args:
            level (int): 角色等级
            
        Returns:
            dict: 包含该等级对应的所有配置项
        """
        # 获取所有配置等级
        config_levels = sorted(cls.LEVEL_CONFIGS.keys())
        
        # 如果等级小于最小配置等级，返回最小等级的配置
        if level <= config_levels[0]:
            return cls.LEVEL_CONFIGS[config_levels[0]]
            
        # 如果等级大于最大配置等级，返回最大等级的配置
        if level >= config_levels[-1]:
            return cls.LEVEL_CONFIGS[config_levels[-1]]
            
        # 找到最接近的配置等级
        for i in range(len(config_levels) - 1):
            if config_levels[i] <= level < config_levels[i + 1]:
                # 如果等级正好等于配置等级，直接返回
                if level == config_levels[i]:
                    return cls.LEVEL_CONFIGS[config_levels[i]]
                    
                # 否则返回较低等级的配置
                return cls.LEVEL_CONFIGS[config_levels[i]]
                
        # 兜底返回最高等级配置
        return cls.LEVEL_CONFIGS[config_levels[-1]] 