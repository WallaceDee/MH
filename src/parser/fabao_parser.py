# -*- coding: utf-8 -*-
"""
法宝数据解析器
用于处理已经解析好的法宝JSON数据，生成中文可读的法宝信息
"""

import json
import logging
from typing import Dict, Any, Optional
from functools import lru_cache

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

class FabaoParser:
    """法宝数据解析器"""
    
    def __init__(self, logger: Optional[logging.Logger] = None):
        self.logger = logger if logger else self._setup_logger()
        self.config_loader = get_config_loader()
        if not self.config_loader:
            self.logger.warning("配置加载器不可用，将影响坐骑配置加载")
        self._fabao_config: Optional[Dict[str, Any]] = None

    def _setup_logger(self) -> logging.Logger:
        """设置日志器"""
        logger = logging.getLogger('FabaoParser')
        if not logger.handlers:
            handler = logging.StreamHandler()
            formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
            handler.setFormatter(formatter)
            logger.addHandler(handler)
            logger.setLevel(logging.INFO)
        return logger
    
    def process_character_fabao(self, parsed_data: Dict[str, Any], character_name: Optional[str] = None) -> Dict[str, Any]:
        """
        处理角色法宝数据
        
        Args:
            parsed_data: 解析后的角色数据
            character_name: 角色名称（可选）
            
        Returns:
            处理后的法宝数据
        """
        try:
            # 获取法宝数据
            fabao_data = parsed_data.get('fabao', {})
            self.logger.warning(f"解析后的法宝数据: {fabao_data}")
            
            if not fabao_data:
                self.logger.warning(f"角色 {character_name or '未知'} 没有法宝数据")
                return []
            
            # 处理法宝列表
            fabao_list = []
            for fabao_index, fabao_info in fabao_data.items():
                fabao_name = self._get_fabao_name(fabao_info.get('iType'))
                self.logger.warning(f"处理法宝: {fabao_name}")
                if fabao_name:
                    fabao_list.append({
                        'name': fabao_name,
                        'cDesc': fabao_info.get('cDesc', '')
                    })
            
            return fabao_list
            
        except Exception as e:
            self.logger.error(f"处理法宝数据时出错: {str(e)}")
            return []
    
    def _get_fabao_name(self, fabao_id: str) -> str:
        """
        根据法宝ID获取法宝名称
        
        Args:
            fabao_id: 法宝ID
            
        Returns:
            法宝名称
        """
        try:
            # 从配置中获取法宝信息
            fabao_config = self.load_fabao_config()
            # 获取法宝名称，如果不存在则返回"未知法宝"
            return fabao_config.get(str(fabao_id), {}).get('name', '未知法宝')
        except Exception as e:
            self.logger.error(f"获取法宝名称失败: {e}")
            return '未知法宝'

    @lru_cache(maxsize=1)
    def load_fabao_config(self) -> Dict[str, Any]:
        """从ConfigLoader加载法宝配置信息"""
        if self._fabao_config:
            return self._fabao_config
            
        if not self.config_loader:
            raise RuntimeError("ConfigLoader不可用")
            
        try:
            self._fabao_config = self.config_loader.get_fabao_config()
            self.logger.debug(f"加载法宝配置: {len(self._fabao_config)}个配置块")
        except Exception as e:
            self.logger.error(f"加载法宝配置失败: {e}")
            raise e
            
        return self._fabao_config