import os
import sys
import sqlite3
import json
import logging
import numpy as np
from datetime import datetime
import glob
import pandas as pd
import joblib

# 添加src目录到Python路径
current_dir = os.path.dirname(os.path.abspath(__file__))
src_dir = os.path.dirname(current_dir)
if src_dir not in sys.path:
    sys.path.insert(0, src_dir)

from feature_extractor import FeatureExtractor

class CharacterEvaluator:
    def __init__(self, model_dir='models'):
        """
        model_dir: str, 模型保存目录
        """
        self.logger = logging.getLogger(__name__)
        self.model_dir = model_dir
        self.feature_extractor = FeatureExtractor()
        self.df = None
        
        # 初始化规则引擎参数
        try:
            from evaluate_model.level_config import LevelConfig
        except ImportError:
            from level_config import LevelConfig
        self.level_config = LevelConfig
        
        # 装备评分系数
        self.EQUIP_COEFFS = {
            'total_gem_level': 80,       # 每级宝石价值
            'premium_skill_count': 500,  # 每个特技价值
            'set_bonus_count': 300       # 每件套装价值
        }
        
        # 宝宝评分系数
        self.PET_COEFFS = {
            'premium_pet_count': 1500,   # 每只特殊宝宝
            'total_pet_score': 0.8,      # 宝宝总分系数
            'max_pet_score': 1.2         # 最高宝宝分系数
        }
        
        # 确保模型目录存在
        if not os.path.exists(model_dir):
            os.makedirs(model_dir)
        
    def _connect_db(self):
        """连接数据库"""
        return sqlite3.connect(self.db_path)
        
    def _extract_features(self, character_data, conn=None):
        """提取角色特征
        
        使用 FeatureExtractor 提取特征
        """
        try:
            # 使用 FeatureExtractor 提取特征
            features = self.feature_extractor.extract_features(character_data)
            return features
            
        except Exception as e:
            self.logger.error(f"特征提取失败: {e}")
            raise

    def get_base_price(self, level):
        """获取基础空号价格，返回最接近的等级基准价"""
        config = self.level_config.get_nearest_level_config(level)
        return config['base_price']

    def calc_base_attributes_value(self, base_price, features):
        """计算基础属性价值"""
        try:
            # 获取等级配置
            level = features.get('level', 0)
            config = self.level_config.get_nearest_level_config(level)
            max_cult = config['max_cultivation']
            max_school_skill = config['max_school_skill']
            # 根据等级动态计算修炼完成度（0-1范围）
            total_cultivation = features.get('total_cultivation', 0)
            cult_completion = min(total_cultivation / (max_cult * 3), 1.0)
            
            # 根据等级动态计算控制力完成度
            total_beast_ski = features.get('total_beast_ski', 0)
            beast_completion = min(total_beast_ski / (max_cult * 4), 1.0)
            
            # 经验修正系数（指数增长）
            exp_factor = 1.0
            sum_exp = features.get('sum_exp', 0)
            if sum_exp > 0:
                # 1000亿经验作为基准
                base_exp = 100000000000  # 1000亿
                # 使用sigmoid函数，让经验值接近1000亿时才有明显价值，超过1000亿不再增加
                exp_ratio = min(sum_exp / base_exp, 1.0)  # 限制最大值为1.0
                exp_factor = 1.0 + 0.5 * (1 / (1 + np.exp(-10 * (exp_ratio - 0.8))))
            
            # 技能修正（均值越高价值越高，标准差越低价值越高）
            avg_skill_level = features.get('avg_skill_level', 0)
            skill_std = features.get('skill_std', 0)
            # 技能等级超过180时给予额外加成
            skill_factor = 1.0
            if avg_skill_level > 0:
                skill_factor = avg_skill_level / max_school_skill
                # skill_factor -= skill_std * 0.05
            # print(f"技能修正（均值越高价值越高，标准差越低价值越高）: {avg_skill_level}-{max_school_skill}-{skill_std * 0.05}")
            # 强壮和神速技能修正
            strong_level = features.get('强壮', 0)
            speed_level = features.get('神速', 0)
            strong_factor = 1.0 + min(strong_level / 40, 1) * 0.15
            speed_factor = 1.0 + min(speed_level / 40, 1) * 0.1
            
            # 生活技能修正
            top_life_skills = features.get('top_life_skills', 0)
            # life_skill_factor = 1.0 + min(top_life_skills / 1000, 0.3)
            life_skill_factor = 1.0
            
            # 应用所有修正
            adjusted_value = base_price * cult_completion * beast_completion
            adjusted_value *= exp_factor * skill_factor
            adjusted_value *= strong_factor * speed_factor
            adjusted_value *= life_skill_factor
            
            # 化圣等级特殊修正
            three_fly_lv = features.get('three_fly_lv', 0)
            if three_fly_lv > 0:
                saint_bonus = three_fly_lv * 800
                adjusted_value += saint_bonus
            
            print(f"基础价值计算过程:")
            print(f"基准价: {base_price}")
            print(f"修炼完成度: {cult_completion}")
            print(f"控制力完成度: {beast_completion}")
            print(f"经验系数: {exp_factor}")
            print(f"技能系数: {skill_factor}")
            print(f"强壮系数: {strong_factor}")
            print(f"神速系数: {speed_factor}")
            print(f"生活技能系数: {life_skill_factor}")
            print(f"最终价值: {adjusted_value}")
            
            return adjusted_value
            
        except Exception as e:
            self.logger.error(f"计算基础属性价值失败: {e}")
            return base_price  # 如果计算出错，至少返回基准价

    def calc_equipment_value(self, features):
        """计算装备系统价值"""
        value = 0
        
        # 宝石价值
        value += features.get('total_gem_level', 0) * self.EQUIP_COEFFS['total_gem_level']
        
        # 特技价值
        value += features.get('premium_skill_count', 0) * self.EQUIP_COEFFS['premium_skill_count']
        
        # 套装价值
        value += features.get('set_bonus_count', 0) * self.EQUIP_COEFFS['set_bonus_count']
        
        # 装备总分价值（非线性增长）
        if 'total_equip_score' in features:
            score = features['total_equip_score']
            # 指数增长：总分越高，单位分价值越高
            value += score * (1 + score / 5000)
        
        return value

    def calc_pets_value(self, features):
        """计算召唤兽价值"""
        value = 0
        
        # 特殊宝宝价值
        value += features.get('premium_pet_count', 0) * self.PET_COEFFS['premium_pet_count']
        
        # 宝宝总分价值
        if 'total_pet_score' in features:
            value += features['total_pet_score'] * self.PET_COEFFS['total_pet_score']
        
        # 最高宝宝价值（优质宝宝溢价）
        if 'max_pet_score' in features:
            value += features['max_pet_score'] * self.PET_COEFFS['max_pet_score']
        
        return value

    def calc_appearance_value(self, features):
        """计算外观系统价值"""
        value = 0
        
        # 限量锦衣价值
        if 'limited_skin_value' in features:
            # 指数衰减模型：前几件价值高，后面边际递减
            skin_value = features['limited_skin_value']
            value += 1000 * (1 - np.exp(-skin_value / 500))
        
        return value

    def apply_market_factors(self, value, features):
        """应用市场因子调整"""
        # 服务器热度系数（示例）
        server_hot = {
            '万里长城': 1.15,
            '生日快乐': 1.20,
            '2008': 1.18,
            '其他': 1.0
        }
        server = features.get('server', '其他')
        server_factor = server_hot.get(server, 1.0)
        
        # 等级段供需系数（高等级角色溢价）
        level = features.get('level', 109)
        level_factor = 1.0 + (level - 109) * 0.02  # 109级基准
        
        return value * server_factor * level_factor
            
    def evaluate(self, character_data):
        """评估角色价值"""
        try:
            # 提取特征
            features = self._extract_features(character_data)
            
            # 1. 获取空号基准价
            base_price = self.get_base_price(features['level'])
            
            # 2. 基础属性修正
            base_value = self.calc_base_attributes_value(base_price, features)
            
            # 3. 装备系统修正
            equip_value = self.calc_equipment_value(features)
            
            # 4. 召唤兽修正
            pets_value = self.calc_pets_value(features)
            
            # 5. 外观修正
            appearance_value = self.calc_appearance_value(features)
            
            # 6. 汇总价值
            total_value = base_value + equip_value + pets_value + appearance_value
            
            # 7. 市场因子调整
            final_value = self.apply_market_factors(total_value, features)
            
            # 构建评估结果
            evaluation_result = {
                'features': features,
                'base_value': base_value,
                'equip_value': equip_value,
                'pets_value': pets_value,
                'appearance_value': appearance_value,
                'total_value': total_value,
                'final_value': final_value,
                'value_breakdown': {
                    'base_attributes': base_value,
                    'equipment': equip_value,
                    'pets': pets_value,
                    'appearance': appearance_value
                }
            }
            
            return evaluation_result
            
        except Exception as e:
            self.logger.error(f"角色评估失败: {e}")
            raise

    def print_evaluation_details(self, evaluation_result):
        """打印评估详情"""
        print("\n=== 角色评估详情 ===")
        print(f"\n基础属性价值: {evaluation_result['base_value']:.2f}")
        print(f"装备系统价值: {evaluation_result['equip_value']:.2f}")
        print(f"召唤兽价值: {evaluation_result['pets_value']:.2f}")
        print(f"外观系统价值: {evaluation_result['appearance_value']:.2f}")
        print(f"总价值: {evaluation_result['total_value']:.2f}")
        print(f"最终估价: {evaluation_result['final_value']:.2f}")
        
        print("\n=== 价值构成 ===")
        for category, value in evaluation_result['value_breakdown'].items():
            print(f"{category}: {value:.2f}")

    def fit(self, db_path):
        """加载数据"""
        try:
            print(f"正在连接数据库: {db_path}")
            conn = sqlite3.connect(db_path)
            cursor = conn.cursor()
            
            # 获取所有角色数据
            print("正在查询数据库...")
            cursor.execute("""
                SELECT 
                    c.id, c.equip_id, c.server_name, c.seller_nickname, c.level, c.price,
                    c.price_desc, c.school AS school_desc, c.area_name, c.icon_index,
                    c.kindid, c.game_ordersn, c.pass_fair_show, c.fair_show_end_time,
                    c.accept_bargain, c.status_desc, c.onsale_expire_time_desc, c.expire_time,
                    c.race, c.fly_status, c.collect_num, c.life_skills, c.school_skills,
                    c.ju_qing_skills, c.all_pets_json, c.all_equip_json AS all_equip_json_desc,
                    c.all_shenqi_json, c.all_rider_json AS all_rider_json_desc,
                    c.ex_avt_json AS ex_avt_json_desc, c.create_time, c.update_time,
                    l.*
                FROM characters c
                LEFT JOIN large_equip_desc_data l ON c.equip_id = l.equip_id
                WHERE c.price > 0
            """)
            
            # 获取列名
            columns = [description[0] for description in cursor.description]
            print(f"查询完成，开始获取数据...")
            rows = cursor.fetchall()
            print(f"获取到 {len(rows)} 条数据")
            # 准备训练数据
            print("开始提取特征...")
            data = []
            for i, row in enumerate(rows):
                character_data = dict(zip(columns, row))
                features = self._extract_features(character_data, conn)
                features['price'] = character_data.get('price', 0)
                features['equip_id'] = character_data.get('equip_id', '')
                data.append(features)
                if (i + 1) % 10 == 0:
                    print(f"已处理 {i + 1}/{len(rows)} 条数据")
            
            print("特征提取完成，转换为DataFrame...")
            # 转换为DataFrame
            self.df = pd.DataFrame(data)
            print(f"DataFrame 形状: {self.df.shape}")
            self.df.set_index('equip_id', inplace=True)
            
            print("数据加载和预处理完成")
            
        except Exception as e:
            print(f"数据加载失败: {str(e)}")
            import traceback
            print(traceback.format_exc())
            raise
        finally:
            if 'conn' in locals():
                conn.close()

    def update_base_prices(self, new_prices):
        """更新空号基准价"""
        self.BASE_PRICES.update(new_prices)
    
    def update_coefficients(self, new_coeffs):
        """更新系数配置"""
        if 'equip' in new_coeffs:
            self.EQUIP_COEFFS.update(new_coeffs['equip'])
        if 'pets' in new_coeffs:
            self.PET_COEFFS.update(new_coeffs['pets'])

    def save_model(self, model_name='latest'):
        """保存模型和相关信息"""
        try:
            # 准备保存的数据
            model_data = {
                'LEVEL_CONFIGS': self.level_config.LEVEL_CONFIGS,
                'EQUIP_COEFFS': self.EQUIP_COEFFS,
                'PET_COEFFS': self.PET_COEFFS,
                'train_time': datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            }
            
            # 保存模型文件
            model_path = os.path.join(self.model_dir, f'{model_name}.joblib')
            joblib.dump(model_data, model_path)
            
            # 保存模型信息
            info_path = os.path.join(self.model_dir, f'{model_name}_info.json')
            model_info = {
                'LEVEL_CONFIGS': self.level_config.LEVEL_CONFIGS,
                'EQUIP_COEFFS': self.EQUIP_COEFFS,
                'PET_COEFFS': self.PET_COEFFS,
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
            self.level_config.LEVEL_CONFIGS = model_data['LEVEL_CONFIGS']
            self.EQUIP_COEFFS = model_data['EQUIP_COEFFS']
            self.PET_COEFFS = model_data['PET_COEFFS']
            
            self.logger.info(f"模型已加载: {model_path}")
            self.logger.info(f"训练时间: {model_data['train_time']}")
            
            return {
                'train_time': model_data['train_time'],
                'LEVEL_CONFIGS': self.level_config.LEVEL_CONFIGS,
                'EQUIP_COEFFS': self.EQUIP_COEFFS,
                'PET_COEFFS': self.PET_COEFFS
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
                        'LEVEL_CONFIGS': info.get('LEVEL_CONFIGS', {}),
                        'EQUIP_COEFFS': info['EQUIP_COEFFS'],
                        'PET_COEFFS': info['PET_COEFFS']
                    })
            return models
        except Exception as e:
            self.logger.error(f"列出模型失败: {e}")
            raise

    def generate_cbg_link(self, eid):
        """生成CBG角色分享链接"""
        if not eid:
            return None
        
        # 从eid中提取服务器ID
        # eid格式通常是：服务器ID-角色ID，比如 "201808081404129-230011021108"
        try:
            if '-' in str(eid):
                server_id = str(eid).split('-')[1]
            
            # 构建基础CBG链接
            base_url = "https://xyq.cbg.163.com/equip"
            params = f"s={server_id}&eid={eid}"
            link = f"{base_url}?{params}"
            
            return link
        except Exception:
            return None

    def export_to_excel(self, output_path='results.xlsx'):
        """将评估结果导出到Excel文件"""
        try:
            if self.df is None:
                print("警告：没有数据可导出")
                return None
                
            # 创建一个ExcelWriter对象，启用超链接支持
            with pd.ExcelWriter(output_path, engine='openpyxl') as writer:
                # 导出基础配置
                config_df = pd.DataFrame([{
                    'LEVEL_CONFIGS': json.dumps(self.level_config.LEVEL_CONFIGS, ensure_ascii=False),
                    'EQUIP_COEFFS': json.dumps(self.EQUIP_COEFFS, ensure_ascii=False),
                    'PET_COEFFS': json.dumps(self.PET_COEFFS, ensure_ascii=False)
                }])
                config_df.to_excel(writer, sheet_name='配置信息', index=False)
                
                # 导出所有角色的评估结果
                all_chars_df = self.df.copy()
                
                # 计算每个角色的价值和修正系数
                results = []
                for idx, row in all_chars_df.iterrows():
                    # 直接使用已有的特征数据
                    features = row.to_dict()
                    level = features.get('level', 0)
                    price = features.get('price', 0)
                    
                    # 计算价值
                    base_price = self.get_base_price(level)
                    base_value = self.calc_base_attributes_value(base_price, features)
                    equip_value = self.calc_equipment_value(features)
                    pets_value = self.calc_pets_value(features)
                    appearance_value = self.calc_appearance_value(features)
                    total_value = base_value + equip_value + pets_value + appearance_value
                    
                    # 计算差价和比率
                    price_diff = total_value - price if price > 0 else 0
                    price_ratio = total_value / price if price > 0 else 0
                    
                    # 计算各种修正系数
                    config = self.level_config.get_nearest_level_config(level)
                    max_cult = config['max_cultivation']
                    max_school_skill = config['max_school_skill']
                    
                    total_cultivation = features.get('total_cultivation', 0)
                    cult_completion = min(total_cultivation / (max_cult * 3), 1.0)
                    
                    total_beast_ski = features.get('total_beast_ski', 0)
                    beast_completion = min(total_beast_ski / (max_cult * 4), 1.0)
                    
                    # 经验修正系数
                    sum_exp = features.get('sum_exp', 0)
                    base_exp = 100000000000  # 1000亿
                    exp_ratio = min(sum_exp / base_exp, 1.0)
                    exp_factor = 1.0 + 0.5 * (1 / (1 + np.exp(-10 * (exp_ratio - 0.8))))
                    
                    # 技能修正
                    avg_skill_level = features.get('avg_skill_level', 0)
                    skill_factor = avg_skill_level / max_school_skill if avg_skill_level > 0 else 1.0
                    
                    # 强壮和神速技能修正
                    strong_level = features.get('强壮', 0)
                    speed_level = features.get('神速', 0)
                    strong_factor = 1.0 + min(strong_level / 40, 1) * 0.15
                    speed_factor = 1.0 + min(speed_level / 40, 1) * 0.1
                    
                    # 生活技能修正
                    top_life_skills = features.get('top_life_skills', 0)
                    life_skill_factor = 1.0 
                    
                    # 生成CBG链接
                    cbg_link = self.generate_cbg_link(idx)
                    
                    results.append({
                        'equip_id': idx,
                        'cbg_link': cbg_link,  # 保留用于生成超链接，但不显示
                        'estimated_value': total_value,
                        'price_diff': price_diff,
                        'price_ratio': price_ratio,
                        'base_value': base_value,
                        'equip_value': equip_value,
                        'pets_value': pets_value,
                        'appearance_value': appearance_value,
                        'total_value': total_value,
                        # 修正系数
                        'base_price': base_price,
                        'cult_completion': cult_completion,
                        'beast_completion': beast_completion,
                        'exp_factor': exp_factor,
                        'skill_factor': skill_factor,
                        'strong_factor': strong_factor,
                        'speed_factor': speed_factor,
                        'life_skill_factor': life_skill_factor
                    })
                
                results_df = pd.DataFrame(results)
                results_df.set_index('equip_id', inplace=True)
                
                # 合并原始特征和评估结果
                final_df = pd.concat([results_df, all_chars_df], axis=1)
                
                # 重新排序列：优先信息 -> 修正系数 -> 价值分解 -> 特征数据
                # 先检查哪些列实际存在
                available_priority_cols = ['price', 'estimated_value', 'price_diff', 'price_ratio', 'level']
                optional_cols = ['server', 'school', 'server_name', 'school_desc']
                for col in optional_cols:
                    if col in final_df.columns:
                        available_priority_cols.append(col)
                
                priority_cols = available_priority_cols
                
                factor_cols = [
                    'base_price', 'cult_completion', 'beast_completion', 'exp_factor',
                    'skill_factor', 'strong_factor', 'speed_factor', 'life_skill_factor'
                ]
                
                value_cols = [
                    'base_value', 'equip_value', 'pets_value', 'appearance_value', 'total_value'
                ]
                
                # 特征数据列（排除已经使用的列，包括cbg_link）
                used_cols = set(priority_cols + factor_cols + value_cols + ['cbg_link'])
                feature_cols = [col for col in final_df.columns if col not in used_cols]
                
                # 最终列顺序（不包含cbg_link）
                final_cols = priority_cols + factor_cols + value_cols + feature_cols
                final_df = final_df[final_cols]
                
                # 导出到Excel
                final_df.to_excel(writer, sheet_name='评估结果')
                
                # 获取工作表对象以添加超链接
                worksheet = writer.sheets['评估结果']
                
                # 导入openpyxl的超链接类
                from openpyxl.worksheet.hyperlink import Hyperlink
                
                # 为equip_id添加CBG超链接（在索引列）
                print("正在添加CBG超链接...")
                hyperlink_count = 0
                
                # 因为合并后cbg_link列可能在results_df中，我们直接从results_df获取
                for row_idx, (index, row) in enumerate(final_df.iterrows(), start=2):  # 从第2行开始（第1行是标题）
                    # 尝试从合并的DataFrame中获取cbg_link
                    cbg_link = None
                    if 'cbg_link' in row:
                        cbg_link = row['cbg_link']
                    
                    # 如果还是没有，直接生成链接
                    if not cbg_link:
                        cbg_link = self.generate_cbg_link(index)
                    
                    if cbg_link and cbg_link.strip() and cbg_link != 'None':
                        try:
                            # equip_id在索引列（第1列，列索引为1）
                            cell = worksheet.cell(row=row_idx, column=1)
                            cell.hyperlink = cbg_link  # 直接使用字符串URL
                            cell.value = str(index)  # 显示equip_id
                            
                            # 设置超链接样式
                            from openpyxl.styles import Font
                            cell.font = Font(color="0000FF", underline="single")
                            hyperlink_count += 1
                        except Exception as e:
                            print(f"添加超链接失败 {index}: {e}")
                            continue
                
                print(f"已添加 {hyperlink_count} 个超链接")
                
                # 导出价值统计
                stats_df = pd.DataFrame([{
                    'total_count': len(final_df),
                    'avg_price': final_df['price'].mean(),
                    'avg_estimated_value': final_df['estimated_value'].mean(),
                    'avg_price_diff': final_df['price_diff'].mean(),
                    'avg_price_ratio': final_df['price_ratio'].mean(),
                    'undervalued_count': (final_df['price_ratio'] > 1.2).sum(),
                    'overvalued_count': (final_df['price_ratio'] < 0.8).sum(),
                    'reasonable_count': ((final_df['price_ratio'] >= 0.8) & (final_df['price_ratio'] <= 1.2)).sum(),
                    'base_value_mean': final_df['base_value'].mean(),
                    'equip_value_mean': final_df['equip_value'].mean(),
                    'pets_value_mean': final_df['pets_value'].mean(),
                    'appearance_value_mean': final_df['appearance_value'].mean(),
                    'total_value_mean': final_df['total_value'].mean(),
                    'base_value_median': final_df['base_value'].median(),
                    'equip_value_median': final_df['equip_value'].median(),
                    'pets_value_median': final_df['pets_value'].median(),
                    'appearance_value_median': final_df['appearance_value'].median(),
                    'total_value_median': final_df['total_value'].median()
                }])
                stats_df.to_excel(writer, sheet_name='价值统计', index=False)
            
            print(f"\n导出完成，文件保存在：{output_path}")
            print(f"共导出 {len(self.df)} 个角色的评估结果")
            print("列顺序：优先信息 -> 修正系数 -> 价值分解 -> 特征数据")
            print("已为equip_id添加CBG超链接，点击equip_id可直接跳转")
            
            return output_path
        except Exception as e:
            print(f"导出Excel时发生错误: {str(e)}")
            import traceback
            print(traceback.format_exc())
            return None

if __name__ == "__main__":
    try:
        # 自动查找/data/文件夹下的所有.db文件
        db_files = glob.glob("data/*.db")
        if not db_files:
            print("未找到数据库文件，请确保/data/文件夹下有.db文件")
            exit(1)
        # 选择第一个.db文件
        db_path = db_files[0]
        print(f"使用数据库文件: {db_path}")
        
        evaluator = CharacterEvaluator()
        print("开始加载数据...")
        # 加载数据
        evaluator.fit(db_path)
        print("数据加载完成")
        
        print("\n开始导出结果到Excel...")
        # 导出结果到Excel
        output_path = evaluator.export_to_excel('results_with_links.xlsx')
        if output_path:
            print(f"结果已成功导出到: {output_path}")
        else:
            print("导出Excel失败")
            
    except Exception as e:
        print(f"程序运行出错: {str(e)}")
        import traceback
        print(traceback.format_exc()) 