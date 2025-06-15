import sqlite3
import pandas as pd
import numpy as np
import json
import logging
from typing import Dict, Any, List, Optional, Union
from datetime import datetime
import os

try:
    from .feature_extractor import FeatureExtractor
except ImportError:
    from feature_extractor import FeatureExtractor


class MarketDataCollector:
    """市场数据采集器 - 从数据库中获取和处理角色市场数据"""
    
    def __init__(self, db_path: Optional[str] = None):
        """
        初始化市场数据采集器
        
        Args:
            db_path: 数据库文件路径，如果为None则自动查找
        """
        self.logger = logging.getLogger(__name__)
        self.feature_extractor = FeatureExtractor()
        self.market_data = pd.DataFrame()
        
        # 自动查找数据库文件
        if db_path is None:
            self.db_path = self._find_database()
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
        
        print(f"市场数据采集器初始化完成，数据库路径: {self.db_path}")
    
    def _find_database(self) -> str:
        """自动查找数据库文件"""
        # 可能的数据库路径
        possible_paths = [
            'data/cbg_data_202412.db',
            'data/cbg_data_202506.db',
            '../data/cbg_data_202412.db', 
            '../data/cbg_data_202506.db',
            '../../data/cbg_data_202412.db',
            '../../data/cbg_data_202506.db',
            './data/cbg_data_202412.db',
            './data/cbg_data_202506.db'
        ]
        
        for path in possible_paths:
            if os.path.exists(path):
                return path
                
        # 查找data目录下的所有.db文件
        data_dirs = ['data', '../data', '../../data', './data']
        for data_dir in data_dirs:
            if os.path.exists(data_dir):
                db_files = [f for f in os.listdir(data_dir) if f.endswith('.db')]
                if db_files:
                    return os.path.join(data_dir, db_files[0])
        
        raise FileNotFoundError("未找到数据库文件，请确保数据库文件存在")
    
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
                FROM characters c
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
                    character_data = dict(zip(columns, row))
                    
                    # 提取特征
                    features = self.feature_extractor.extract_features(character_data)
                    
                    # 添加基本信息
                    features.update({
                        'equip_id': character_data.get('equip_id', ''),
                        'price': character_data.get('price', 0),
                        'server_name': character_data.get('server_name', ''),
                        'school_desc': character_data.get('school_desc', ''),
                        'collect_num': character_data.get('collect_num', 0),
                        'create_time': character_data.get('create_time', ''),
                        'seller_nickname': character_data.get('seller_nickname', '')
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
        # 总修炼等级
        cultivation_keys = ['expt_ski1', 'expt_ski2', 'expt_ski3', 'expt_ski4']
        features['total_cultivation'] = sum(features.get(key, 0) for key in cultivation_keys)
        
        # 总召唤兽修炼等级
        beast_cultivation_keys = ['beast_ski1', 'beast_ski2', 'beast_ski3', 'beast_ski4']
        features['total_beast_cultivation'] = sum(features.get(key, 0) for key in beast_cultivation_keys)
        
        # 总技能等级
        school_skills = features.get('school_skills', [])
        features['total_school_skills'] = sum(school_skills) if school_skills else 0
        features['avg_school_skills'] = (features['total_school_skills'] / len(school_skills)) if school_skills else 0
        
        # 生活技能统计
        life_skills = features.get('life_skills', [])
        features['total_life_skills'] = sum(life_skills) if life_skills else 0
        features['high_life_skills_count'] = sum(1 for skill in life_skills if skill >= 140) if life_skills else 0
        
        # 强壮神速统计
        qiangzhuang_shensu = features.get('qiangzhuang&shensu', [])
        features['total_qiangzhuang_shensu'] = sum(qiangzhuang_shensu) if qiangzhuang_shensu else 0
        
        # 综合评分（用于快速筛选）
        features['comprehensive_score'] = (
            features.get('level', 0) * 0.1 +
            features.get('total_cultivation', 0) * 0.2 +
            features.get('total_beast_cultivation', 0) * 0.1 +
            features.get('all_new_point', 0) * 100 +
            features.get('sum_exp', 0) * 0.01 +
            features.get('total_gem_level', 0) * 0.5 +
            features.get('premium_skill_count', 0) * 200
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
    
    def get_similar_characters(self, 
                              target_features: Dict[str, Any],
                              similarity_threshold: float = 0.6,
                              max_results: int = 50) -> pd.DataFrame:
        """
        根据特征相似度获取相似角色（全特征版本，用于MarketAnchorValuator调用）
        
        Args:
            target_features: 目标角色特征
            similarity_threshold: 相似度阈值
            max_results: 最大结果数
            
        Returns:
            pd.DataFrame: 相似角色数据
        """
        market_data = self.get_market_data()
        
        if market_data.empty:
            return pd.DataFrame()
        
        # 定义所有特征及其容忍度（参考MarketAnchorValuator的配置）
        feature_tolerances = {
            # 核心特征 - 较严格
            'level': 0.05,           # 等级容忍度5%
            'all_new_point': 0.0,    # 乾元丹必须完全一致
            'school_history_count': 0.5,  # 历史门派数必须一致
            'packet_page':1.0,      # 行囊页数必须一致
            'allow_pet_count': 1.0,  # 召唤兽上限必须一致
    
            # 修炼系统特征 - 中等容忍度
            'total_cultivation': 0.15,  # 修炼容忍度15%
            'total_beast_cultivation': 0.20,  # 召唤兽修炼容忍度20%
            'expt_ski1': 0.15,       # 攻击修炼
            'expt_ski2': 0.15,       # 防御修炼
            'expt_ski3': 0.15,       # 法术修炼
            'expt_ski4': 0.15,       # 抗法修炼
            'expt_ski5': 0.15,       # 猎术修炼
            'beast_ski1': 0.20,      # 召唤兽攻击修炼
            'beast_ski2': 0.20,      # 召唤兽防御修炼
            'beast_ski3': 0.20,      # 召唤兽法术修炼
            'beast_ski4': 0.20,      # 召唤兽抗法修炼
            
            
            # 经验和成长系统 - 较宽松
            'sum_exp': 0.30,         # 总经验容忍度30%
            'three_fly_lv': 0.0,    # 化圣等级容忍20%
            'yushoushu_skill': 1.0, # 育兽术等级容忍度100%
            
            # 其他增值系统
            'lingyou_count': 0.50,   # 灵佑次数容忍度20%
            'jiyuan_amount': 0.50,   # 机缘值容忍度30%
            'xianyu_amount': 0.80,   # 仙玉容忍度40%
            'learn_cash': 0.80,      # 储备金容忍度40%
            # 宠物和法宝系统
            'premium_fabao_count': 0.30,  # 法宝容忍度30%
            'hight_grow_rider_count': 0.20,  # 高成长坐骑容忍度20%
            
            # 技能系统 - 组合特征
            'total_school_skills': 0.15,    # 师门技能总和
            'avg_school_skills': 0.10,      # 师门技能平均值
            'total_life_skills': 0.5,      # 生活技能总和
            'high_life_skills_count': 0.30, # 高等级生活技能数量
            'total_qiangzhuang_shensu': 0.20, # 强壮神速总和
            
            # 特殊状态
            'qianyuandan_breakthrough': 0.0,  # 乾元丹突破必须一致

            # 由于目前只计算空号，所以装备系统和宠物特征暂时不计算
            # # 装备系统特征
            # 'total_gem_level': 0.25,  # 宝石容忍度25%
            # 'premium_skill_count': 0.0,  # 特技数量必须完全一致
            # 'limited_skin_value': 0.30,  # 限量锦衣容忍度30%
            # 'collect_num': 0.50,     # 收藏数量容忍度50%

        }
        
        # 定义特征权重（重要性排序）
        feature_weights = {
            # 最重要特征 - 核心影响价值
            'qianyuandan_breakthrough': 1.0,
            'beast_ski1': 1, 'beast_ski2': 1, 'beast_ski3': 1, 'beast_ski4': 1,
            'expt_ski1': 0.9, 'expt_ski2': 0.9, 'expt_ski3': 0.9, 'expt_ski4': 0.9, 'expt_ski5': 0.9,
            'all_new_point': 0.8,
            'total_beast_cultivation': 0.8,
            # 很重要特征 - 显著影响价值
            'total_cultivation': 0.8,
            'school_history_count': 0.8,
            
            # 重要特征 - 中等影响
            'avg_school_skills': 0.6,
            'three_fly_lv': 0.6,
            'total_qiangzhuang_shensu': 0.6,
            
            # 修炼细节特征 - 中等权重
            'total_school_skills': 0.4,
            'level': 0.5,
            
            # 辅助特征 - 较低权重
            'sum_exp': 0.4,
            'lingyou_count': 0.4,
            'yushoushu_skill': 0.4,
            'hight_grow_rider_count': 0.4,
            
            # 次要特征 - 低权重
            'jiyuan_amount': 0.3,
            'total_life_skills': 0.3,
            'high_life_skills_count': 0.3,
            
            # 可选特征 - 最低权重
            'xianyu_amount': 0.2,
            'learn_cash': 0.2,
            'premium_fabao_count': 0.2,
            'allow_pet_count': 0.1,
            'packet_page': 0.1,


        }
        
        print(f"开始计算相似度，使用 {len(feature_tolerances)} 个特征维度")
        
        similarities = []
        for idx, row in market_data.iterrows():
            total_weight = 0
            weighted_similarity = 0
            matched_features = 0
            
            for feature_name, tolerance in feature_tolerances.items():
                if feature_name not in target_features and feature_name not in row:
                    continue
                    
                target_val = target_features.get(feature_name, 0)
                market_val = row.get(feature_name, 0)
                weight = feature_weights.get(feature_name, 0.1)  # 默认权重0.1
                
                # 计算特征相似度
                if target_val == 0 and market_val == 0:
                    # 两者都为0，完全匹配
                    feature_similarity = 1.0
                elif target_val == 0 or market_val == 0:
                    # 一个为0一个不为0，根据特征类型决定相似度
                    if feature_name in ['all_new_point', 'qianyuandan_breakthrough', 'three_fly_lv']:
                        # 关键特征必须一致
                        feature_similarity = 0.0
                    else:
                        # 非关键特征给予部分相似度
                        feature_similarity = 0.3
                else:
                    # 计算相对差异
                    denominator = max(abs(target_val), 1e-8)  # 防止除零
                    diff_ratio = abs(target_val - market_val) / denominator
                    
                    if diff_ratio <= tolerance:
                        # 在容忍度内，相似度为1
                        feature_similarity = 1.0
                    elif diff_ratio <= tolerance * 2:
                        # 超出容忍度但在2倍范围内，线性递减
                        feature_similarity = max(0, 1.0 - (diff_ratio - tolerance) / tolerance)
                    else:
                        # 差异太大，相似度为0
                        feature_similarity = 0.0
                
                weighted_similarity += feature_similarity * weight
                total_weight += weight
                matched_features += 1
            
            # 计算最终相似度
            if total_weight > 0 and matched_features >= 5:  # 至少匹配5个特征
                final_similarity = weighted_similarity / total_weight
                
                # 根据匹配特征数量调整相似度
                feature_coverage = matched_features / len(feature_tolerances)
                coverage_bonus = min(feature_coverage * 0.1, 0.05)  # 最多5%的覆盖加成
                final_similarity = min(final_similarity + coverage_bonus, 1.0)
                
                if final_similarity >= similarity_threshold:
                    similarities.append((idx, final_similarity, matched_features))
        
        print(f"计算完成，找到 {len(similarities)} 个相似角色")
        
        # 排序并返回前N个
        similarities.sort(key=lambda x: x[1], reverse=True)  # 按相似度排序
        selected_indices = [idx for idx, _, _ in similarities[:max_results]]
        
        if similarities:
            best_similarity = similarities[0][1]
            worst_similarity = similarities[-1][1] if len(similarities) > 1 else best_similarity
            avg_features = sum(matched for _, _, matched in similarities) / len(similarities)
            print(f"相似度范围: {worst_similarity:.3f} - {best_similarity:.3f}")
            print(f"平均匹配特征数: {avg_features:.1f}")
        
        return market_data.loc[selected_indices]


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