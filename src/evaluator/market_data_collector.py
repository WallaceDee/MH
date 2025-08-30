import sys
import os

# 添加项目根目录到Python路径，解决模块导入问题
from src.utils.project_path import get_project_root
project_root = get_project_root()
sys.path.insert(0, project_root)

import sqlite3
import pandas as pd
import numpy as np
import json
import logging
from typing import Dict, Any, List, Optional, Union
from datetime import datetime

try:
    from .feature_extractor.feature_extractor import FeatureExtractor
except ImportError:
    from src.evaluator.feature_extractor.feature_extractor import FeatureExtractor


class MarketDataCollector:
    """市场数据采集器 - 从数据库中获取和处理角色市场数据"""
    
    def __init__(self, db_path: Optional[str] = None, db_type: str = 'normal'):
        """
        初始化市场数据采集器
        
        Args:
            db_path: 数据库文件路径，如果为None则自动查找
            db_type: 数据库类型，'normal' 或 'empty'
        """
        self.logger = logging.getLogger(__name__)
        self.feature_extractor = FeatureExtractor()
        self.market_data = pd.DataFrame()
        self.db_type = db_type
        
        # 自动查找数据库文件
        if db_path is None:
            self.db_path = self._find_recent_dbs()
        else:
            self.db_path = db_path
            
        # 定义特征名映射（中文 -> 英文）
        self.feature_name_mapping = {
            '等级': 'level',
            '门派': 'school',
            '总经验': 'sum_exp',
            '服务器': 'server_name',
            '价格': 'price',
            '修炼': 'cultivation',
            '宝石': 'gems',
            '特技': 'special_skills',
            '召唤兽': 'pets',
            '装备': 'equipment'
        }
        
        print(f"空号市场数据采集器初始化完成，数据库路径: {self.db_path}")
    
    def _find_recent_dbs(self) -> List[str]:
        """查找所有可用的空号角色数据库文件"""
        import glob
        from datetime import datetime, timedelta

        # 获取当前月份和上个月份
        now = datetime.now()
        current_month = now.strftime("%Y%m")

        # 计算上个月
        last_month_date = now.replace(day=1) - timedelta(days=1)
        last_month = last_month_date.strftime("%Y%m")

        # 优先查找当月和上月的数据库
        target_months = [current_month, last_month]
        print(f"优先查找数据库文件，目标月份: {target_months}")

        # 数据库文件固定存放在根目录的data文件夹中
        data_path = "data"
        found_dbs = []

        # 首先查找指定月份的数据库文件
        for month in target_months:
            db_file = os.path.join(data_path, month, f"empty_roles_{month}.db")
            if os.path.exists(db_file):
                found_dbs.append(db_file)
                print(f"找到指定月份数据库文件: {db_file}")

        # 如果没找到指定月份的，则查找所有可用的空号角色数据库文件
        if not found_dbs:
            print("未找到指定月份的数据库文件，查找所有可用的空号角色数据库文件")
            # 查找所有年月文件夹下的数据库文件
            pattern = os.path.join(data_path, "*", "empty_roles_*.db")
            all_dbs = glob.glob(pattern)
            
            # 按文件名排序，最新的在前
            all_dbs.sort(reverse=True)
            
            # 取最新的2个数据库文件
            found_dbs = all_dbs[:2]
            print(f"找到所有数据库文件: {all_dbs}")
            print(f"使用最新的数据库文件: {found_dbs}")

        return found_dbs
    
    def refresh_market_data(self, 
                           filters: Optional[Dict[str, Any]] = None,
                           max_records: int = 10000) -> pd.DataFrame:
        """
        刷新市场数据
        
        Args:
            filters: 筛选条件字典，例如 {'level_min': 109, 'price_max': 10000}
            max_records: 最大记录数
            
        Returns:
            pd.DataFrame: 处理后的市场数据
        """
        try:
            print(f"开始刷新市场数据，最大记录数: {max_records}")
            
            # 连接数据库
            conn = sqlite3.connect(self.db_path)
            
            # 构建SQL查询
            base_query = """
                SELECT 
                    c.id, c.equip_id, c.server_name, c.seller_nickname, c.level, c.price,
                    c.price_desc, c.school AS school_desc, c.area_name, c.icon_index,
                    c.kindid, c.game_ordersn, c.pass_fair_show, c.fair_show_end_time,
                    c.accept_bargain, c.status_desc, c.onsale_expire_time_desc, c.expire_time,
                    c.race, c.fly_status, c.collect_num, c.life_skills, c.school_skills,
                    c.ju_qing_skills, c.yushoushu_skill, c.all_pets_json, c.all_equip_json,
                    c.all_shenqi_json, c.all_rider_json, c.all_fabao_json,
                    c.ex_avt_json, c.create_time, c.update_time,
                    l.*
                FROM roles c
                LEFT JOIN large_equip_desc_data l ON c.equip_id = l.equip_id
                WHERE c.price > 0
            """
            
            # 添加筛选条件
            conditions = []
            if filters:
                if 'level_min' in filters:
                    conditions.append(f"c.level >= {filters['level_min']}")
                if 'level_max' in filters:
                    conditions.append(f"c.level <= {filters['level_max']}")
                if 'price_min' in filters:
                    conditions.append(f"c.price >= {filters['price_min']}")
                if 'price_max' in filters:
                    conditions.append(f"c.price <= {filters['price_max']}")
                if 'server_name' in filters:
                    conditions.append(f"c.server_name = '{filters['server_name']}'")
                if 'school' in filters:
                    conditions.append(f"c.school = '{filters['school']}'")
            
            if conditions:
                base_query += " AND " + " AND ".join(conditions)
            
            base_query += f" ORDER BY c.price DESC LIMIT {max_records}"
            
            print(f"执行SQL查询...")
            
            # 执行查询
            cursor = conn.cursor()
            cursor.execute(base_query)
            columns = [description[0] for description in cursor.description]
            rows = cursor.fetchall()
            
            print(f"查询完成，获取到 {len(rows)} 条原始数据")
            
            # 处理数据
            market_data = []
            for i, row in enumerate(rows):
                try:
                    role_data = dict(zip(columns, row))
                    
                    # 提取特征
                    features = self.feature_extractor.extract_features(role_data)
                    
                    # 添加基本信息
                    features.update({
                        'equip_id': role_data.get('equip_id', ''),
                        'price': role_data.get('price', 0),
                        'server_name': role_data.get('server_name', ''),
                        'school_desc': role_data.get('school_desc', ''),
                        'collect_num': role_data.get('collect_num', 0),
                        'create_time': role_data.get('create_time', ''),
                        'seller_nickname': role_data.get('seller_nickname', '')
                    })
                    
                    # 计算派生特征
                    features = self._calculate_derived_features(features)
                    
                    market_data.append(features)
                    
                    if (i + 1) % 100 == 0 or i == len(rows) - 1:
                        print(f"已处理 {i + 1}/{len(rows)} 条数据")
                        
                except Exception as e:
                    self.logger.warning(f"处理第 {i+1} 条数据时出错: {e}")
                    continue
            
            # 转换为DataFrame
            self.market_data = pd.DataFrame(market_data)
            
            if not self.market_data.empty:
                self.market_data.set_index('equip_id', inplace=True)
                print(f"市场数据刷新完成，共 {len(self.market_data)} 条有效数据")
                print(f"数据特征维度: {len(self.market_data.columns)}")
                print(f"价格范围: {self.market_data['price'].min():.1f} - {self.market_data['price'].max():.1f}")
            else:
                print("警告：未获取到有效的市场数据")
            
            conn.close()
            return self.market_data
            
        except Exception as e:
            self.logger.error(f"刷新市场数据失败: {e}")
            raise
    
    def _calculate_derived_features(self, features: Dict[str, Any]) -> Dict[str, Any]:
        """
        计算派生特征
        
        Args:
            features: 原始特征字典
            
        Returns:
            Dict[str, Any]: 包含派生特征的字典
        """
        # 总修炼等级 - 安全处理None值
        cultivation_keys = ['expt_ski1', 'expt_ski2', 'expt_ski3', 'expt_ski4']
        cultivation_values = []
        for key in cultivation_keys:
            value = features.get(key, 0)
            # 如果值是None，转换为0
            cultivation_values.append(0 if value is None else value)
        features['total_cultivation'] = sum(cultivation_values)
        
        # 总召唤兽修炼等级 - 安全处理None值
        beast_cultivation_keys = ['beast_ski1', 'beast_ski2', 'beast_ski3', 'beast_ski4']
        beast_cultivation_values = []
        for key in beast_cultivation_keys:
            value = features.get(key, 0)
            # 如果值是None，转换为0
            beast_cultivation_values.append(0 if value is None else value)
        features['total_beast_cultivation'] = sum(beast_cultivation_values)
        
        # 总技能等级 - 只保留平均值特征
        school_skills = features.get('school_skills', [])
        features['avg_school_skills'] = (sum(school_skills) / len(school_skills)) if school_skills else 0
        
        # 生活技能统计 - 只保留高等级技能数量
        life_skills = features.get('life_skills', [])
        features['high_life_skills_count'] = sum(1 for skill in life_skills if skill >= 140) if life_skills else 0
        
        # 强壮神速统计
        qiangzhuang_shensu = features.get('qiangzhuang&shensu', [])
        features['total_qiangzhuang_shensu'] = sum(qiangzhuang_shensu) if qiangzhuang_shensu else 0
        
        # 综合评分（用于快速筛选） - 更新公式，移除冗余特征
        features['comprehensive_score'] = (
            features.get('total_cultivation', 0) * 0.5 +
            features.get('total_beast_cultivation', 0) * 0.5 +
            features.get('high_life_skills_count', 0) * 0.3 +
            features.get('total_qiangzhuang_shensu', 0) * 0.1 +
            features.get('avg_school_skills', 0) * 0.2 
        )
        
        return features
    
    def get_market_data(self) -> pd.DataFrame:
        """
        获取当前的市场数据
        
        Returns:
            pd.DataFrame: 市场数据
        """
        if self.market_data.empty:
            print("市场数据为空，正在刷新...")
            self.refresh_market_data()
        
        return self.market_data
    
    def get_market_summary(self) -> Dict[str, Any]:
        """
        获取市场数据摘要
        
        Returns:
            Dict[str, Any]: 市场摘要信息
        """
        if self.market_data.empty:
            return {'error': '市场数据为空'}
        
        df = self.market_data
        
        summary = {
            'total_count': len(df),
            'price_stats': {
                'min': df['price'].min(),
                'max': df['price'].max(),
                'mean': df['price'].mean(),
                'median': df['price'].median(),
                'std': df['price'].std()
            },
            'level_distribution': df['level'].value_counts().to_dict(),
            'school_distribution': df.get('school_desc', pd.Series()).value_counts().to_dict(),
            'server_distribution': df.get('server_name', pd.Series()).value_counts().to_dict(),
            'feature_stats': {
                'avg_cultivation': df.get('total_cultivation', pd.Series()).mean(),
                'avg_gems': df.get('total_gem_level', pd.Series()).mean(),
                'premium_skill_rate': (df.get('premium_skill_count', 0) > 0).mean() if 'premium_skill_count' in df.columns else 0
            }
        }
        
        return summary
    
    def filter_market_data(self, 
                          level_range: Optional[tuple] = None,
                          price_range: Optional[tuple] = None,
                          school: Optional[str] = None,
                          server: Optional[str] = None) -> pd.DataFrame:
        """
        筛选市场数据
        
        Args:
            level_range: 等级范围 (min, max)
            price_range: 价格范围 (min, max)  
            school: 门派
            server: 服务器
            
        Returns:
            pd.DataFrame: 筛选后的数据
        """
        df = self.get_market_data().copy()
        
        if level_range:
            df = df[(df['level'] >= level_range[0]) & (df['level'] <= level_range[1])]
        
        if price_range:
            df = df[(df['price'] >= price_range[0]) & (df['price'] <= price_range[1])]
        
        if school:
            df = df[df['school_desc'] == school]
        
        if server:
            df = df[df['server_name'] == server]
        
        return df
    
    def get_market_data_for_similarity(self, 
                                      filters: Optional[Dict[str, Any]] = None) -> pd.DataFrame:
        """
        获取用于相似度计算的市场数据
        
        Args:
            filters: 预过滤条件，用于减少计算量
            
        Returns:
            pd.DataFrame: 市场数据
        """
        market_data = self.get_market_data()
        
        if market_data.empty:
            return market_data
        
        # 应用预过滤条件以提高效率
        if filters:
            filtered_data = market_data.copy()
            
            # 等级过滤
            if 'level_range' in filters:
                level_min, level_max = filters['level_range']
                filtered_data = filtered_data[
                    (filtered_data['level'] >= level_min) & 
                    (filtered_data['level'] <= level_max)
                ]
            
            # 总修炼等级过滤
            if 'total_cultivation_range' in filters:
                cult_min, cult_max = filters['total_cultivation_range']
                filtered_data = filtered_data[
                    (filtered_data['total_cultivation'] >= cult_min) & 
                    (filtered_data['total_cultivation'] <= cult_max)
                ]
            
            # 召唤兽控制力总和过滤
            if 'total_beast_cultivation_range' in filters:
                beast_min, beast_max = filters['total_beast_cultivation_range']
                filtered_data = filtered_data[
                    (filtered_data['total_beast_cultivation'] >= beast_min) & 
                    (filtered_data['total_beast_cultivation'] <= beast_max)
                ]
            
            # 师门技能平均值过滤
            if 'avg_school_skills_range' in filters:
                skills_min, skills_max = filters['avg_school_skills_range']
                filtered_data = filtered_data[
                    (filtered_data['avg_school_skills'] >= skills_min) & 
                    (filtered_data['avg_school_skills'] <= skills_max)
                ]
            
            # 价格过滤
            if 'price_range' in filters:
                price_min, price_max = filters['price_range']
                filtered_data = filtered_data[
                    (filtered_data['price'] >= price_min) & 
                    (filtered_data['price'] <= price_max)
                ]
            
            # 其他范围过滤条件（通用处理）
            range_keys = ['total_cultivation_range', 'total_beast_cultivation_range', 
                         'avg_school_skills_range', 'level_range', 'price_range']
            for key, value in filters.items():
                if key not in range_keys and key in filtered_data.columns:
                    if isinstance(value, (list, tuple)) and len(value) == 2:
                        # 范围过滤
                        filtered_data = filtered_data[
                            (filtered_data[key] >= value[0]) & 
                            (filtered_data[key] <= value[1])
                        ]
                    else:
                        # 精确匹配
                        filtered_data = filtered_data[filtered_data[key] == value]
            
            return filtered_data
        
        return market_data


if __name__ == "__main__":
    # 测试代码
    try:
        collector = MarketDataCollector()
        
        # 刷新市场数据
        market_data = collector.refresh_market_data(max_records=1000)
        
        # 获取市场摘要
        summary = collector.get_market_summary()
        print("\n=== 市场数据摘要 ===")
        print(f"总数据量: {summary['total_count']}")
        print(f"价格范围: {summary['price_stats']['min']:.1f} - {summary['price_stats']['max']:.1f}")
        print(f"平均价格: {summary['price_stats']['mean']:.1f}")
        print(f"中位价格: {summary['price_stats']['median']:.1f}")
        
        # 测试筛选功能
        filtered_data = collector.filter_market_data(
            level_range=(109, 175),
            price_range=(1000, 50000)
        )
        print(f"\n筛选后数据量: {len(filtered_data)}")
        
    except Exception as e:
        print(f"测试失败: {e}")
        import traceback
        traceback.print_exc() 