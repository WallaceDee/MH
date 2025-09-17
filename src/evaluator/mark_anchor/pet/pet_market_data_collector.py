import sys
import os

# 添加项目根目录到Python路径，解决模块导入问题
current_dir = os.path.dirname(os.path.abspath(__file__))
project_root = os.path.dirname(os.path.dirname(current_dir))  # 向上两级到项目根目录
sys.path.insert(0, project_root)

import pandas as pd
import logging
from typing import Dict, Any, List, Optional, Tuple, Union
from datetime import datetime

try:
    from ...feature_extractor.pet_feature_extractor import PetFeatureExtractor
    from src.database import db
    from src.models.pet import Pet
    from sqlalchemy import and_, or_, func, text
except ImportError:
    try:
        from src.evaluator.feature_extractor.pet_feature_extractor import PetFeatureExtractor
        from src.database import db
        from src.models.pet import Pet
        from sqlalchemy import and_, or_, func, text
    except ImportError:
        # 如果都导入失败，创建一个简单的占位符
        class PetFeatureExtractor:
            def __init__(self):
                pass

            def extract_features(self, pet_data):
                return {}


class PetMarketDataCollector:
    """市场数据采集器 - 从数据库中获取和处理召唤兽市场数据"""

    def __init__(self):
        """
        初始化召唤兽市场数据采集器
        """
        self.feature_extractor = PetFeatureExtractor()
        self.logger = logging.getLogger(__name__)
        print(f"宠物市场数据采集器初始化，使用MySQL数据库")
    
    
    def get_market_data(self,
                        level_range: Optional[Tuple[int, int]] = None,
                        role_grade_limit_range: Optional[Tuple[int, int]] = None,
                        price_range: Optional[Tuple[float, float]] = None,
                        server: Optional[str] = None,
                        all_skill: Optional[Union[str, List[str]]] = None,
                        limit: int = 1000) -> pd.DataFrame:
        """
        获取市场召唤兽数据，从MySQL数据库中获取数据

        Args:
            level_range: 等级范围 (min_level, max_level)
            price_range: 价格范围 (min_price, max_price)
            server: 服务器筛选
            limit: 返回数据条数限制

            role_grade_limit_range: 携带等级 (min_role_grade_limit, max_role_grade_limit)
            all_skill: 技能 使用了管道符拼接的技能字符串以"|"
        Returns:
            召唤兽市场数据DataFrame
        """
        try:
            # 构建SQLAlchemy查询
            query = db.session.query(Pet)

            # 处理all_skill参数，支持字符串或列表
            target_skills = []
            if all_skill:
                if isinstance(all_skill, str):
                    target_skills = [s for s in all_skill.split('|') if s]
                elif isinstance(all_skill, list):
                    target_skills = [str(s) for s in all_skill if s]

            # 基础筛选条件
            if level_range is not None:
                min_level, max_level = level_range
                query = query.filter(Pet.equip_level.between(min_level, max_level))

            if role_grade_limit_range is not None:
                min_role_grade_limit, max_role_grade_limit = role_grade_limit_range
                query = query.filter(Pet.role_grade_limit.between(min_role_grade_limit, max_role_grade_limit))

            if price_range is not None:
                min_price, max_price = price_range
                query = query.filter(Pet.price.between(min_price, max_price))

            if server is not None:
                query = query.filter(Pet.server_name == server)

            # 技能筛选
            if target_skills:
                # 技能SQL初步过滤
                for skill in target_skills:
                    query = query.filter(Pet.all_skill.like(f"%{skill}%"))
                
                # 技能数量过滤 过滤出技能数量 <= len(target_skills)+2 的数据
                skill_count_limit = len(target_skills) + 1
                query = query.filter(
                    func.length(Pet.all_skill) - func.length(func.replace(Pet.all_skill, '|', '')) + 1 <= skill_count_limit
                )

            # 排序和限制
            query = query.order_by(Pet.update_time.desc()).limit(limit)

            # 执行查询
            pets = query.all()
            
            if pets:
                # 转换为字典列表
                data_list = []
                for pet in pets:
                    pet_dict = {}
                    for column in pet.__table__.columns:
                        value = getattr(pet, column.name)
                        if hasattr(value, 'isoformat'):  # datetime对象
                            pet_dict[column.name] = value.isoformat()
                        else:
                            pet_dict[column.name] = value
                    data_list.append(pet_dict)
                
                result_df = pd.DataFrame(data_list)
                
                # Python集合精确过滤技能
                if target_skills:
                    target_set = set(target_skills)
                    def match(row):
                        all_skill_val = row.get('all_skill', '')
                        skill_set = set(all_skill_val.split('|')) if all_skill_val else set()
                        return target_set.issubset(skill_set)
                    result_df = result_df[result_df.apply(match, axis=1)]
                
                # 去重
                result_df = result_df.drop_duplicates(subset=['equip_sn'], keep='first')
                
                print(f"从MySQL数据库加载了 {len(result_df)} 条宠物市场数据")
                return result_df
            else:
                print(f"从MySQL数据库查询到0条宠物市场数据")
                return pd.DataFrame()

        except Exception as e:
            self.logger.error(f"查询宠物市场数据失败: {e}")
            print(f"SQL执行异常: {e}")
            return pd.DataFrame()
        
    def get_market_data_for_similarity(self,
                                       target_features: Dict[str, Any]) -> pd.DataFrame:
        """
        根据目标特征获取用于相似度计算的市场数据

        Args:
            target_features: 目标召唤兽特征

        Returns:
            过滤后的市场数据DataFrame
        """
        # 基础过滤条件
        role_grade_limit = target_features.get('role_grade_limit', 0)
        
        # 等级范围：目标等级±20级
        role_grade_limit_range = (max(0, role_grade_limit - 20), role_grade_limit + 20)

        all_skill = target_features.get('all_skill', '')
        
        # 获取市场数据
        market_data = self.get_market_data(
            role_grade_limit_range=role_grade_limit_range,
            all_skill=all_skill,
            limit=5000
        )
        
        if market_data.empty:
            return market_data
            
        # 提取特征
        features_list = []
        for _, row in market_data.iterrows():
            try:
                features = self.feature_extractor.extract_features(row.to_dict())
                
                # 保留原始关键字段，确保接口返回时有完整信息
                features['equip_sn'] = row.get('equip_sn', row.get('eid',None))
                features['price'] = row.get('price', 0)
                
                features_list.append(features)
            except Exception as e:
                self.logger.warning(f"提取特征失败: {e}")
                continue
                
        if features_list:
            return pd.DataFrame(features_list)
        else:
            return pd.DataFrame()
        
    def get_market_data_with_business_rules(self,
                                           target_features: Dict[str, Any],
                                           **kwargs) -> pd.DataFrame:
        """
        根据业务规则获取市场数据

        Args:
            target_features: 目标灵饰特征
            **kwargs: 其他过滤参数

        Returns: 
            过滤后的市场数据DataFrame
        """
        # 获取基础市场数据
        market_data = self.get_market_data_for_similarity(target_features)
        
        if market_data.empty:
            return market_data
            
        # 应用业务规则过滤
        filtered_data = []
        
        for _, row in market_data.iterrows():
            # 这里可以添加更多的业务规则过滤逻辑
            # 例如：价格异常值过滤、属性组合过滤等
            
            # 示例：过滤价格异常值（价格过高或过低的装备）
            # price = row.get('price', 0)
            # if price <= 0 or price > 1000000:  # 价格范围检查
            #     continue
                
            filtered_data.append(row)
            
        if filtered_data:
            return pd.DataFrame(filtered_data)
        else:
            return pd.DataFrame()