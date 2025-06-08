import os
import sqlite3
import json
import logging
import numpy as np
from datetime import datetime
from collections import defaultdict
from sklearn.cluster import KMeans
from sklearn.preprocessing import StandardScaler, MinMaxScaler
from lifelines import CoxPHFitter
from sklearn.semi_supervised import LabelSpreading
import glob
import pandas as pd
from sklearn.metrics.pairwise import euclidean_distances
from sklearn.linear_model import LinearRegression
from sklearn.model_selection import train_test_split
from sklearn.metrics import mean_squared_error, r2_score
import joblib

class CharacterEvaluator:
    def __init__(self, feature_weights=None, n_neighbors=5, model_dir='models'):
        """
        feature_weights: dict, 特征权重
        n_neighbors: int, 查找相似角色时参考的邻居数量
        model_dir: str, 模型保存目录
        """
        self.feature_weights = feature_weights or {
            'level': 0.2,                    # 等级
            'equipment_score': 0.3,          # 装备评分
            'expt_total': 0.2,               # 修炼总分
            'limited_avt_count': 0.1,        # 限量锦衣数量
            'school_heat': 0.1,              # 门派热度
            'market_index': 0.1              # 市场指数
        }
        self.n_neighbors = n_neighbors
        self.scaler = MinMaxScaler()
        self.df = None
        self.feature_cols = list(self.feature_weights.keys())
        self.logger = logging.getLogger(__name__)
        self.kmeans = None
        self.cph_model = None
        self.label_model = None
        self.model = None
        self.model_dir = model_dir
        
        # 确保模型目录存在
        if not os.path.exists(model_dir):
            os.makedirs(model_dir)
        
    def _connect_db(self):
        """连接数据库"""
        return sqlite3.connect(self.db_path)
        
    def _get_listing_days(self, character_data):
        """计算上架天数"""
        try:
            create_time = datetime.strptime(character_data['create_time'], '%Y-%m-%d %H:%M:%S')
            now = datetime.now()
            return (now - create_time).days
        except:
            return 0
            
    def _calculate_virtual_price(self, character_data):
        """计算虚拟成交价"""
        price = character_data['price']
        days_listed = self._get_listing_days(character_data)
        
        # 基础衰减系数：每7天降价5%
        decay = 0.95 ** (days_listed / 7)
        # 加入随机波动模拟议价空间
        noise = np.random.uniform(0.97, 1.03)
        
        return price * decay * noise
        
    def _calculate_value_density(self, character_data):
        """计算价值密度"""
        # 修炼总分
        expt_skills = [
            character_data.get('expt_ski1', 0),  # 攻击修炼
            character_data.get('expt_ski2', 0),  # 防御修炼
            character_data.get('expt_ski3', 0),  # 法术修炼
            character_data.get('expt_ski4', 0),  # 抗法修炼
            character_data.get('expt_ski5', 0),  # 猎术修炼
        ]
        expt_total = sum(skill * 2 for skill in expt_skills)  # 每级修炼2分
        
        # 装备评分
        try:
            equips_json = character_data.get('all_equip_json')
            if equips_json is None:
                equips = []
            else:
                equips = json.loads(equips_json)
                # 确保equips是列表
                if not isinstance(equips, list):
                    equips = []
            equip_score = sum(equip.get('score', 0) for equip in equips if isinstance(equip, dict))
        except (json.JSONDecodeError, TypeError):
            equip_score = 0
        
        # 计算价值密度
        price = character_data.get('price', 0)
        if price > 0:
            return (expt_total + equip_score) / price
        return 0
        
    def _calculate_premium_factor(self, character_data):
        """计算溢价因子"""
        # 限量锦衣数量
        try:
            ex_avt_json = character_data.get('ex_avt_json')
            if ex_avt_json is None:
                ex_avt = []
            else:
                ex_avt = json.loads(ex_avt_json)
                # 确保ex_avt是列表
                if not isinstance(ex_avt, list):
                    ex_avt = []
            limited_avt_count = sum(1 for item in ex_avt if isinstance(item, dict) and item.get('is_limited', False))
        except (json.JSONDecodeError, TypeError):
            limited_avt_count = 0
        
        # 等级
        level = character_data.get('level', 1)
        
        return limited_avt_count / (level / 175)
        
    def _calculate_liquidity_risk(self, character_data):
        """计算流动性风险"""
        days_listed = self._get_listing_days(character_data)
        price = character_data['price']
        
        # 获取价格百分位
        try:
            conn = self._connect_db()
            cursor = conn.cursor()
            cursor.execute("""
                SELECT COUNT(*) as count
                FROM characters
                WHERE price <= ?
            """, (price,))
            count = cursor.fetchone()[0]
            
            cursor.execute("SELECT COUNT(*) as total FROM characters")
            total = cursor.fetchone()[0]
            
            price_percentile = count / total if total > 0 else 0.5
            
            return days_listed * price_percentile
            
        except Exception as e:
            self.logger.error(f"计算流动性风险失败: {e}")
            return 0
        finally:
            conn.close()
            
    def _get_school_heat(self, school):
        """获取门派热度系数"""
        # 根据当前版本门派强度赋值
        school_heat = {
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
        return school_heat.get(school, 1.0)
        
    def _calculate_market_index(self, server_name, conn):
        """计算市场供需指数"""
        try:
            cursor = conn.cursor()
            # 获取服务器在售数量
            cursor.execute("""
                SELECT COUNT(*) as supply
                FROM characters
                WHERE server_name = ?
            """, (server_name,))
            supply = cursor.fetchone()[0]
            
            # 获取服务器平均收藏数
            cursor.execute("""
                SELECT AVG(collect_num) as avg_collect
                FROM characters
                WHERE server_name = ?
            """, (server_name,))
            avg_collect = cursor.fetchone()[0] or 0
            
            # 计算供需指数
            demand = avg_collect
            return demand / (supply + 1e-5)
            
        except Exception as e:
            self.logger.error(f"计算市场供需指数失败: {e}")
            return 0.5

    def _calculate_expt_total(self, character_data):
        """计算修炼总分"""
        expt_skills = [
            character_data.get('expt_ski1', 0),  # 攻击修炼
            character_data.get('expt_ski2', 0),  # 防御修炼
            character_data.get('expt_ski3', 0),  # 法术修炼
            character_data.get('expt_ski4', 0),  # 抗法修炼
            character_data.get('expt_ski5', 0),  # 猎术修炼
        ]
        return sum(skill * 2 for skill in expt_skills)  # 每级修炼2分

    def _calculate_equipment_score(self, character_data):
        """计算装备评分"""
        try:
            equips_json = character_data.get('all_equip_json')
            if equips_json is None:
                return 0
            equips = json.loads(equips_json)
            if not isinstance(equips, list):
                return 0
            return sum(equip.get('score', 0) for equip in equips if isinstance(equip, dict))
        except (json.JSONDecodeError, TypeError):
            return 0

    def _calculate_limited_avt_count(self, character_data):
        """计算限量锦衣数量"""
        try:
            ex_avt_json = character_data.get('ex_avt_json')
            if ex_avt_json is None:
                return 0
            ex_avt = json.loads(ex_avt_json)
            if not isinstance(ex_avt, list):
                return 0
            return sum(1 for item in ex_avt if isinstance(item, dict) and item.get('is_limited', False))
        except (json.JSONDecodeError, TypeError):
            return 0

    def _extract_features(self, character_data, conn=None):
        """提取角色特征
        
        六大类特征：
        1. 基础属性特征
        2. 修炼与控制力特征
        3. 技能体系特征
        4. 装备特征体系
        5. 召唤兽特征
        6. 外观与增值特征
        """
        try:
            features = {}
            
            # 1. 基础属性特征
            features.update({
                'level': character_data.get('level', 0),                    # 等级
                'exp_total': float(character_data.get('exp_total', 0)),    # 总经验
                'ascension_level': character_data.get('ascension_level', 0), # 飞升状态
                'life_death_level': character_data.get('life_death_level', 0), # 生死劫等级
                'money_total': character_data.get('money_total', 0),       # 现金+存款+储备金
                'potential_fruit': character_data.get('potential_fruit', 0) # 潜能果数量
            })
            
            # 2. 修炼与控制力特征
            cultivation_scores = {
                'atk_cult': character_data.get('expt_ski1', 0),    # 攻击修炼
                'def_cult': character_data.get('expt_ski2', 0),    # 防御修炼
                'mag_cult': character_data.get('expt_ski3', 0),    # 法术修炼
                'res_cult': character_data.get('expt_ski4', 0),    # 抗法修炼
                'hunt_cult': character_data.get('expt_ski5', 0)    # 猎术修炼
            }
            features.update(cultivation_scores)
            features['cultivation_total'] = sum(cultivation_scores.values())  # 修炼总分
            
            # 3. 技能体系特征
            try:
                skills_json = character_data.get('skills_json')
                if skills_json:
                    skills = json.loads(skills_json)
                    if isinstance(skills, list):
                        # 师门技能
                        school_skills = [s for s in skills if s.get('type') == 'school']
                        features['school_skill_avg'] = np.mean([s.get('level', 0) for s in school_skills])
                        features['school_skill_std'] = np.std([s.get('level', 0) for s in school_skills])
                        
                        # 生活技能
                        life_skills = [s for s in skills if s.get('type') == 'life']
                        life_skill_scores = {s.get('name'): s.get('level', 0) for s in life_skills}
                        top_skills = sorted(life_skill_scores.items(), key=lambda x: x[1], reverse=True)[:5]
                        features['top_life_skills'] = sum(score for _, score in top_skills)
                        
                        # 剧情技能
                        story_skills = [s for s in skills if s.get('type') == 'story']
                        features['story_skill_score'] = sum(s.get('level', 0) for s in story_skills)
            except (json.JSONDecodeError, TypeError):
                features.update({
                    'school_skill_avg': 0,
                    'school_skill_std': 0,
                    'top_life_skills': 0,
                    'story_skill_score': 0
                })
            
            # 4. 装备特征体系
            try:
                equips_json = character_data.get('all_equip_json')
                if equips_json:
                    equips = json.loads(equips_json)
                    if isinstance(equips, list):
                        # 宝石等级
                        gem_levels = []
                        # 特技统计
                        special_skills = defaultdict(int)
                        # 套装统计
                        suit_types = defaultdict(int)
                        
                        for equip in equips:
                            if isinstance(equip, dict):
                                # 宝石等级
                                if 'gem_level' in equip:
                                    gem_levels.append(equip['gem_level'])
                                # 特技
                                if 'special_skill' in equip:
                                    special_skills[equip['special_skill']] += 1
                                # 套装
                                if 'suit_type' in equip:
                                    suit_types[equip['suit_type']] += 1
                        
                        features.update({
                            'avg_gem_level': np.mean(gem_levels) if gem_levels else 0,
                            'total_gem_level': sum(gem_levels),
                            'special_skill_count': len(special_skills),
                            'suit_activation': max(suit_types.values()) if suit_types else 0
                        })
            except (json.JSONDecodeError, TypeError):
                features.update({
                    'avg_gem_level': 0,
                    'total_gem_level': 0,
                    'special_skill_count': 0,
                    'suit_activation': 0
                })
            
            # 5. 召唤兽特征
            try:
                pets_json = character_data.get('pets_json')
                if pets_json:
                    pets = json.loads(pets_json)
                    if isinstance(pets, list):
                        # 特殊技能统计
                        premium_skills = ['净台妙谛', '死亡召唤', '力劈华山']
                        special_skill_count = 0
                        total_pet_score = 0
                        
                        for pet in pets:
                            if isinstance(pet, dict):
                                # 特殊技能
                                if 'skills' in pet and isinstance(pet['skills'], list):
                                    special_skill_count += sum(1 for skill in pet['skills'] 
                                                             if skill in premium_skills)
                                # 资质评分
                                if all(k in pet for k in ['attack', 'defense', 'speed', 'growth']):
                                    pet_score = (pet['attack'] + pet['defense'] + pet['speed']) / 3 * pet['growth']
                                    total_pet_score += pet_score
                        
                        features.update({
                            'premium_pet_skills': special_skill_count,
                            'total_pet_score': total_pet_score,
                            'pet_count': len(pets)
                        })
            except (json.JSONDecodeError, TypeError):
                features.update({
                    'premium_pet_skills': 0,
                    'total_pet_score': 0,
                    'pet_count': 0
                })
            
            # 6. 外观与增值特征
            try:
                # 限量锦衣
                ex_avt_json = character_data.get('ex_avt_json')
                if ex_avt_json:
                    ex_avt = json.loads(ex_avt_json)
                    if isinstance(ex_avt, list):
                        features['limited_avt_count'] = sum(1 for item in ex_avt 
                                                          if isinstance(item, dict) and item.get('is_limited', False))
                
                # 成就点
                features['achievement_points'] = character_data.get('achievement_points', 0)
                
                # 仙玉积分
                features['jade_points'] = character_data.get('jade_points', 0)
                
                # 坐骑装饰
                features['mount_decoration'] = character_data.get('mount_decoration', 0)
                
            except (json.JSONDecodeError, TypeError):
                features.update({
                    'limited_avt_count': 0,
                    'achievement_points': 0,
                    'jade_points': 0,
                    'mount_decoration': 0
                })
            
            # 7. 市场行为特征
            features.update({
                'school_heat': self._get_school_heat(character_data.get('school', '')),
                'market_index': self._calculate_market_index(character_data.get('server_name', ''), conn) if conn else 0.5,
                'list_days': (datetime.now() - datetime.strptime(character_data.get('list_time', '2024-01-01'), '%Y-%m-%d')).days,
                'collect_rate': character_data.get('collect_num', 0) / (character_data.get('view_num', 0) + 1)
            })
            
            return features
            
        except Exception as e:
            self.logger.error(f"特征提取失败: {e}")
            raise

    def train(self):
        """训练模型"""
        try:
            conn = self._connect_db()
            cursor = conn.cursor()
            
            # 获取所有角色数据
            cursor.execute("""
                SELECT c.*, l.* 
                FROM characters c 
                LEFT JOIN large_equip_desc_data l ON c.equip_id = l.equip_id
                WHERE c.price > 0
            """)
            columns = [description[0] for description in cursor.description]
            rows = cursor.fetchall()  # 一次性获取所有数据

            # 准备训练数据
            X = []  # 特征
            y = []  # 虚拟成交价
            days_listed_list = []
            all_features = []  # 存储所有特征

            print("\n开始提取特征...")
            for i, row in enumerate(rows):
                character_data = dict(zip(columns, row))
                features = self._extract_features(character_data, conn)
                all_features.append(features)
                X.append(list(features.values()))
                y.append(features['virtual_price'])
                days_listed_list.append(self._get_listing_days(character_data))
                
                # 每100条数据打印一次进度
                if (i + 1) % 100 == 0:
                    print(f"已处理 {i + 1} 条数据")

            # 计算特征统计信息
            print("\n特征统计信息:")
            feature_names = list(all_features[0].keys())
            for name in feature_names:
                values = [f[name] for f in all_features]
                print(f"\n{name}:")
                print(f"  最小值: {min(values):.2f}")
                print(f"  最大值: {max(values):.2f}")
                print(f"  平均值: {sum(values)/len(values):.2f}")
                print(f"  标准差: {np.std(values):.2f}")
                print(f"  非零值数量: {sum(1 for v in values if v != 0)}")
                print(f"  零值数量: {sum(1 for v in values if v == 0)}")

            # 数据标准化
            X = self.scaler.fit_transform(X)

            # 训练K-means聚类
            self.kmeans = KMeans(n_clusters=3, random_state=42)
            self.kmeans.fit(X)

            # 训练生存分析模型
            df = pd.DataFrame(X, columns=features.keys())
            df['days_listed'] = days_listed_list
            df['sold'] = 0  # 假设所有样本都未成交

            try:
                self.cph_model = CoxPHFitter()
                self.cph_model.fit(df, duration_col='days_listed', event_col='sold')
            except Exception as e:
                self.logger.error(f"生存分析模型训练失败: {e}")
                self.cph_model = None

            # 训练半监督学习模型
            # 使用聚类结果作为伪标签
            pseudo_labels = self.kmeans.labels_
            self.label_model = LabelSpreading(kernel='knn', n_neighbors=5)
            self.label_model.fit(X, pseudo_labels)

            self.logger.info("模型训练完成")

        except Exception as e:
            self.logger.error(f"模型训练失败: {e}")
            raise
        finally:
            conn.close()
            
    def evaluate(self, character_data):
        """评估角色价值"""
        try:
            # 提取特征
            features = self._extract_features(character_data)
            X = self.scaler.transform([list(features.values())])
            
            # 获取聚类结果
            cluster = self.kmeans.predict(X)[0]
            
            # 获取生存分析结果
            survival_prob = self.cph_model.predict_survival_function(X)[0]
            
            # 获取标签传播结果
            label_prob = self.label_model.predict_proba(X)[0]
            
            # 计算最终价值
            base_value = features['virtual_price']
            market_adjustment = 1 + 0.5 * (features['market_index'] - 0.5)
            school_adjustment = features['school_heat']
            
            final_value = base_value * market_adjustment * school_adjustment
            
            return {
                'features': features,
                'cluster': cluster,
                'survival_probability': survival_prob,
                'label_probabilities': label_prob,
                'base_value': base_value,
                'market_adjustment': market_adjustment,
                'school_adjustment': school_adjustment,
                'final_value': final_value
            }
            
        except Exception as e:
            self.logger.error(f"角色评估失败: {e}")
            raise
            
    def find_undervalued_characters(self, min_discount_rate=0.2):
        """查找被低估的角色"""
        try:
            if self.df is None:
                raise ValueError('请先调用fit方法加载在售角色数据')
            if self.model is None:
                raise ValueError('请先调用train_model方法训练模型')
                
            undervalued = []
            for idx, row in self.df.iterrows():
                # 使用模型预测价格
                X = np.array([[row[c] for c in self.feature_cols]])
                predicted_price = self.model.predict(X)[0]
                actual_price = row['price']
                
                # 计算折扣率
                discount_rate = (predicted_price - actual_price) / predicted_price
                
                if discount_rate >= min_discount_rate:
                    undervalued.append({
                        'equip_id': idx,
                        'actual_price': actual_price,
                        'predicted_price': predicted_price,
                        'discount_rate': discount_rate,
                        'features': {c: row[c] for c in self.feature_cols}
                    })
            
            # 按折扣率排序
            undervalued.sort(key=lambda x: x['discount_rate'], reverse=True)
            
            return undervalued
            
        except Exception as e:
            self.logger.error(f"查找被低估角色失败: {e}")
            raise

    def fit(self, db_path):
        """训练模型"""
        try:
            conn = sqlite3.connect(db_path)
            cursor = conn.cursor()
            
            # 获取所有角色数据
            cursor.execute("""
                SELECT c.*, l.* 
                FROM characters c 
                LEFT JOIN large_equip_desc_data l ON c.equip_id = l.equip_id
                WHERE c.price > 0
            """)
            
            # 获取列名
            columns = [description[0] for description in cursor.description]
            
            # 准备训练数据
            data = []
            for row in cursor.fetchall():
                character_data = dict(zip(columns, row))
                features = self._extract_features(character_data, conn)
                features['price'] = character_data.get('price', 0)
                features['equip_id'] = character_data.get('equip_id', '')
                data.append(features)
            
            # 转换为DataFrame
            self.df = pd.DataFrame(data)
            self.df.set_index('equip_id', inplace=True)
            
            # 计算加权分数
            self.df['score'] = self.df[self.feature_cols].mul(
                [self.feature_weights[c] for c in self.feature_cols], axis=1
            ).sum(axis=1)
            
            # 标准化特征
            self.df_scaled = self.scaler.fit_transform(self.df[self.feature_cols])
            
            self.logger.info("模型训练完成")
            
        except Exception as e:
            self.logger.error(f"模型训练失败: {e}")
            raise
        finally:
            if 'conn' in locals():
                conn.close()

    def evaluate_recommendation(self, character_data):
        """评估推荐角色价值"""
        try:
            if self.df is None:
                raise ValueError('请先调用fit方法加载在售角色数据')
                
            # 提取特征
            features = self._extract_features(character_data)
            query_vec = np.array([[features[c] for c in self.feature_cols]])
            query_vec_scaled = self.scaler.transform(query_vec)
            
            # 计算与所有角色的距离
            dists = euclidean_distances(query_vec_scaled, self.df_scaled)[0]
            
            # 获取最相似的n个角色
            idx = np.argsort(dists)[:self.n_neighbors]
            neighbors = self.df.iloc[idx]
            
            # 计算推荐价格
            mean_price = neighbors['price'].mean()
            median_price = neighbors['price'].median()
            
            # 计算加权分数
            score = sum(features[c] * w for c, w in self.feature_weights.items())
            
            return {
                'features': features,
                'score': score,
                'recommend_price': mean_price,
                'median_price': median_price,
                'neighbor_ids': neighbors.index.tolist(),
                'neighbor_prices': neighbors['price'].tolist(),
                'neighbor_scores': neighbors['score'].tolist()
            }
            
        except Exception as e:
            self.logger.error(f"角色推荐评估失败: {e}")
            raise

    def train_model(self, test_size=0.2, random_state=42):
        """训练价格预测模型"""
        try:
            if self.df is None:
                raise ValueError('请先调用fit方法加载在售角色数据')
            
            # 准备训练数据
            X = self.df[self.feature_cols]
            y = self.df['price']
            
            # 划分训练集和测试集
            X_train, X_test, y_train, y_test = train_test_split(
                X, y, test_size=test_size, random_state=random_state
            )
            
            # 训练线性回归模型
            self.model = LinearRegression()
            self.model.fit(X_train, y_train)
            
            # 评估模型
            y_pred = self.model.predict(X_test)
            mse = mean_squared_error(y_test, y_pred)
            r2 = r2_score(y_test, y_pred)
            
            # 更新特征权重
            feature_importance = np.abs(self.model.coef_)
            total_importance = np.sum(feature_importance)
            self.feature_weights = dict(zip(
                self.feature_cols,
                feature_importance / total_importance
            ))
            
            # 输出模型评估结果
            self.logger.info(f"模型训练完成:")
            self.logger.info(f"均方误差 (MSE): {mse:.2f}")
            self.logger.info(f"决定系数 (R²): {r2:.2f}")
            self.logger.info("特征权重:")
            for feature, weight in self.feature_weights.items():
                self.logger.info(f"{feature}: {weight:.3f}")
            
            return {
                'mse': mse,
                'r2': r2,
                'feature_weights': self.feature_weights
            }
            
        except Exception as e:
            self.logger.error(f"模型训练失败: {e}")
            raise

    def predict_price(self, character_data):
        """使用训练好的模型预测价格"""
        try:
            if self.model is None:
                raise ValueError('请先调用train_model方法训练模型')
            
            # 提取特征
            features = self._extract_features(character_data)
            X = np.array([[features[c] for c in self.feature_cols]])
            
            # 预测价格
            predicted_price = self.model.predict(X)[0]
            
            return {
                'features': features,
                'predicted_price': predicted_price,
                'feature_weights': self.feature_weights
            }
            
        except Exception as e:
            self.logger.error(f"价格预测失败: {e}")
            raise

    def save_model(self, model_name='latest'):
        """保存模型和相关信息"""
        try:
            if self.model is None:
                raise ValueError('没有可保存的模型，请先训练模型')
            
            # 准备保存的数据
            model_data = {
                'model': self.model,
                'scaler': self.scaler,
                'feature_weights': self.feature_weights,
                'feature_cols': self.feature_cols,
                'n_neighbors': self.n_neighbors,
                'train_time': datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            }
            
            # 保存模型文件
            model_path = os.path.join(self.model_dir, f'{model_name}.joblib')
            joblib.dump(model_data, model_path)
            
            # 保存模型信息
            info_path = os.path.join(self.model_dir, f'{model_name}_info.json')
            model_info = {
                'feature_weights': self.feature_weights,
                'feature_cols': self.feature_cols,
                'n_neighbors': self.n_neighbors,
                'train_time': model_data['train_time']
            }
            with open(info_path, 'w', encoding='utf-8') as f:
                json.dump(model_info, f, ensure_ascii=False, indent=2)
            
            self.logger.info(f"模型已保存到: {model_path}")
            self.logger.info(f"模型信息已保存到: {info_path}")
            
            return {
                'model_path': model_path,
                'info_path': info_path
            }
            
        except Exception as e:
            self.logger.error(f"保存模型失败: {e}")
            raise

    def load_model(self, model_name='latest'):
        """加载模型和相关信息"""
        try:
            model_path = os.path.join(self.model_dir, f'{model_name}.joblib')
            if not os.path.exists(model_path):
                raise ValueError(f'模型文件不存在: {model_path}')
            
            # 加载模型数据
            model_data = joblib.load(model_path)
            
            # 恢复模型状态
            self.model = model_data['model']
            self.scaler = model_data['scaler']
            self.feature_weights = model_data['feature_weights']
            self.feature_cols = model_data['feature_cols']
            self.n_neighbors = model_data['n_neighbors']
            
            self.logger.info(f"模型已加载: {model_path}")
            self.logger.info(f"训练时间: {model_data['train_time']}")
            self.logger.info("特征权重:")
            for feature, weight in self.feature_weights.items():
                self.logger.info(f"{feature}: {weight:.3f}")
            
            return {
                'train_time': model_data['train_time'],
                'feature_weights': self.feature_weights
            }
            
        except Exception as e:
            self.logger.error(f"加载模型失败: {e}")
            raise

    def list_models(self):
        """列出所有可用的模型"""
        try:
            models = []
            for file in os.listdir(self.model_dir):
                if file.endswith('_info.json'):
                    model_name = file[:-10]  # 移除 '_info.json' 后缀
                    info_path = os.path.join(self.model_dir, file)
                    with open(info_path, 'r', encoding='utf-8') as f:
                        info = json.load(f)
                    models.append({
                        'name': model_name,
                        'train_time': info['train_time'],
                        'feature_weights': info['feature_weights']
                    })
            return models
        except Exception as e:
            self.logger.error(f"列出模型失败: {e}")
            raise

if __name__ == "__main__":
    # 自动查找/data/文件夹下的所有.db文件
    db_files = glob.glob("data/*.db")
    if not db_files:
        print("未找到数据库文件，请确保/data/文件夹下有.db文件")
        exit(1)
    # 选择第一个.db文件
    db_path = db_files[0]
    print(f"使用数据库文件: {db_path}")
    evaluator = CharacterEvaluator()
    # 训练模型
    evaluator.fit(db_path)
    print("数据加载完成")
    # 训练模型
    model_metrics = evaluator.train_model()
    print("\n模型训练完成")
    print(f"均方误差 (MSE): {model_metrics['mse']:.2f}")
    print(f"决定系数 (R²): {model_metrics['r2']:.2f}")
    print("\n特征权重:")
    for feature, weight in model_metrics['feature_weights'].items():
        print(f"{feature}: {weight:.3f}")
    # 保存模型
    model_paths = evaluator.save_model()
    print(f"\n模型已保存:")
    print(f"模型文件: {model_paths['model_path']}")
    print(f"模型信息: {model_paths['info_path']}")
    # 列出所有模型
    models = evaluator.list_models()
    print("\n可用模型:")
    for model in models:
        print(f"\n模型名称: {model['name']}")
        print(f"训练时间: {model['train_time']}")
        print("特征权重:")
        for feature, weight in model['feature_weights'].items():
            print(f"  {feature}: {weight:.3f}")
    # 查找被低估的角色
    undervalued = evaluator.find_undervalued_characters()
    print("\n被低估的角色：")
    for char in undervalued:
        print(f"ID: {char['equip_id']}")
        print(f"实际价格: {char['actual_price']:.2f}")
        print(f"预测价格: {char['predicted_price']:.2f}")
        print(f"折扣率: {char['discount_rate']:.2%}")
        print("特征值:")
        for feature, value in char['features'].items():
            print(f"  {feature}: {value}")
        print("---") 