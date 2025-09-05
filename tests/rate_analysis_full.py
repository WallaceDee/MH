import sqlite3
import json
import sys
import os
import numpy as np
from typing import Dict, List, Any

# 添加项目根目录到路径
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.evaluator.feature_extractor.feature_extractor import FeatureExtractor
from src.evaluator.rule_evaluator import RuleEvaluator
from src.utils.jsonc_loader import load_jsonc_from_config_dir

class RateAnalyzer:
    def __init__(self, db_path: str):
        """初始化分析器
        
        Args:
            db_path: 数据库路径
        """
        self.db_path = db_path
        self.feature_extractor = FeatureExtractor()
        self.rule_evaluator = RuleEvaluator()
        
        # 加载当前rate.jsonc配置
        self.rate_config = load_jsonc_from_config_dir('rate.jsonc', 'src/evaluator/rule_evaluator.py')
        
        print("初始化完成...")
        
    def connect_db(self):
        """连接数据库"""
        try:
            conn = sqlite3.connect(self.db_path)
            conn.row_factory = sqlite3.Row  # 使用Row对象便于按列名访问
            return conn
        except Exception as e:
            print(f"数据库连接失败: {e}")
            return None
    
    def get_role_sample(self, limit: int = 1000):
        """获取角色样本数据
        
        Args:
            limit: 获取的样本数量
            
        Returns:
            List[Dict]: 角色数据列表
        """
        conn = self.connect_db()
        if not conn:
            print("数据库连接失败")
            return []
            
        try:
            # 先检查表结构
            cursor = conn.execute("SELECT COUNT(*) FROM roles WHERE price > 0;")
            count = cursor.fetchone()[0]
            print(f"数据库中有价格的角色数量: {count}")
            
            # 查询角色数据，从large_equip_desc_data表获取详细数据
            # 关联roles表获取价格信息
            query = """
            SELECT c.eid, c.serverid, c.level, c.school,
                    c.price,c.collect_num,
                    c.other_info,
                    c.large_equip_desc,
                    c.yushoushu_skill, c.school_skills, c.life_skills, c.expire_time,
                    l.sum_exp, l.three_fly_lv, l.all_new_point,
                    l.jiyuan_amount, l.packet_page, l.xianyu_amount, l.learn_cash,
                    l.sum_amount, l.role_icon,
                    l.expt_ski1, l.expt_ski2, l.expt_ski3, l.expt_ski4, l.expt_ski5,
                    l.beast_ski1, l.beast_ski2, l.beast_ski3, l.beast_ski4,
                    l.changesch_json, l.ex_avt_json, l.huge_horse_json, l.shenqi_json,
                    l.all_equip_json, l.all_summon_json, l.all_rider_json
                FROM roles c
                LEFT JOIN large_equip_desc_data l ON c.eid = l.eid
            WHERE c.level = 109
            ORDER BY RANDOM() 
            LIMIT ?
            """
            
            print(f"执行查询，获取 {limit} 个样本...")
            cursor = conn.execute(query, (limit,))
            roles = []
            
            for row in cursor:
                # 将Row对象转换为字典
                role_dict = dict(row)
                roles.append(role_dict)
                
            print(f"成功获取 {len(roles)} 个角色样本")
            if len(roles) > 0:
                print(f"第一个角色样例 eid: {roles[0].get('eid', 'N/A')}, price: {roles[0].get('price', 'N/A')}")
            return roles
            
        except Exception as e:
            print(f"获取角色数据失败: {e}")
            import traceback
            print(traceback.format_exc())
            return []
        finally:
            conn.close()
    
    def analyze_role_features(self, roles: List[Dict]) -> List[Dict]:
        """分析角色特征并计算规则估价
        
        Args:
            roles: 角色数据列表
            
        Returns:
            List[Dict]: 包含特征和估价结果的数据列表
        """
        results = []
        
        print("开始提取特征和计算规则估价...")
        
        for i, role in enumerate(roles):
            try:
                if i % 100 == 0:
                    print(f"处理进度: {i}/{len(roles)}")
                
                # 提取特征
                features = self.feature_extractor.extract_features(role)
                
                # 计算规则估价
                rule_evaluation = self.rule_evaluator.calc_rule_evaluation_from_features(features)
                
                # 准备结果数据
                result = {
                    'eid': role.get('eid', ''),
                    'price': role.get('price', 0),
                    'level': role.get('role_level', features.get('level', 0)),  # 优先使用数据库的role_level字段
                    'rule_value': rule_evaluation.get('rule_value', 0),
                }
                
                # 添加各项价值明细
                value_breakdown = rule_evaluation.get('value_breakdown', {})
                for component, value in value_breakdown.items():
                    result[f'{component}_value'] = value
                
                # 添加主要特征
                key_features = [
                    'school_history_count', 'all_new_point', 'qianyuandan_breakthrough',
                    'jiyuan_amount', 'sum_exp', 'school_skills', 'packet_page',
                    'learn_cash', 'xianyu_amount', 'hight_grow_rider_count',
                    'lingyou_count', 'expt_ski1', 'expt_ski2', 'expt_ski3', 'expt_ski4',
                    'beast_ski1', 'beast_ski2', 'beast_ski3', 'beast_ski4',
                    'life_skills', 'qiangzhuang&shensu', 'shenqi',
                    'limited_skin_value', 'limited_huge_horse_value'
                ]
                
                for feature in key_features:
                    if feature == 'school_skills':
                        # 师门技能取平均值
                        skills = features.get(feature, [])
                        result[feature] = np.mean(skills) if skills else 0
                    elif feature == 'life_skills':
                        # 生活技能取数量
                        skills = features.get(feature, [])
                        result[f'{feature}_count'] = len(skills)
                        result[f'{feature}_avg'] = np.mean(skills) if skills else 0
                    elif feature == 'qiangzhuang&shensu':
                        # 强壮神速取总和
                        skills = features.get(feature, [])
                        result['qiangzhuang_shensu_sum'] = sum(skills) if skills else 0
                    elif feature == 'shenqi':
                        # 神器取总分
                        shenqi = features.get(feature, [0,0,0,0,0,0,0,0])
                        result['shenqi_score'] = sum(shenqi)
                    else:
                        result[feature] = features.get(feature, 0)
                
                results.append(result)
                
            except Exception as e:
                print(f"处理角色 {role.get('eid', 'unknown')} 时发生错误: {e}")
                continue
        
        print(f"特征提取完成，共处理 {len(results)} 个角色")
        return results
    
    def analyze_component_performance(self, data: List[Dict]) -> Dict[str, Dict]:
        """分析各个价值组件的表现
        
        Args:
            data: 包含特征和估价的数据列表
            
        Returns:
            Dict: 各组件的分析结果
        """
        print("分析各组件表现...")
        
        # 价值组件列表（与rate.jsonc对应）
        components = [
            'school_history', 'qianyuandan', 'jiyuan', 'exp', 'school_skills',
            'packet', 'learn_cash', 'xianyu', 'cultivation_level', 'cultivation_limit',
            'beast_cultivation', 'life_skills', 'qiangzhuang_shensu', 'lingyou',
            'rider', 'pet_count', 'shenqi', 'limited_skin', 'limited_huge_horse'
        ]
        
        analysis_results = {}
        
        for component in components:
            value_col = f'{component}_value'
            
            # 筛选有此组件价值的角色
            component_data = [d for d in data if d.get(value_col, 0) > 0]
            
            if len(component_data) == 0:
                continue
            
            # 提取价值和价格数据
            values = [d[value_col] for d in component_data]
            prices = [d['price'] for d in component_data]
            rule_values = [d['rule_value'] for d in component_data]
            
            # 计算组件价值与实际价格的相关性
            correlation = np.corrcoef(values, prices)[0, 1] if len(values) > 1 else 0
            
            # 计算组件价值占规则总价值的比例
            value_ratios = [v/rv if rv > 0 else 0 for v, rv in zip(values, rule_values)]
            avg_ratio = np.mean(value_ratios) if value_ratios else 0
            
            # 计算价值分布
            value_stats = {
                'mean': np.mean(values),
                'std': np.std(values),
                'min': np.min(values),
                'max': np.max(values),
                '25%': np.percentile(values, 25),
                '50%': np.percentile(values, 50),
                '75%': np.percentile(values, 75)
            }
            
            # 计算建议的调整系数
            # 基于相关性调整：相关性高的组件应该有更高的系数
            current_rate = self.rate_config.get(component, 1.0)
            
            # 相关性调整建议
            if correlation > 0.7:
                suggested_rate = min(current_rate * 1.2, 1.0)  # 高相关性，增加系数
            elif correlation > 0.3:
                suggested_rate = current_rate  # 中等相关性，保持不变
            elif correlation > 0:
                suggested_rate = max(current_rate * 0.8, 0.1)  # 低相关性，减少系数
            else:
                suggested_rate = max(current_rate * 0.5, 0.0)  # 负相关，大幅减少
            
            analysis_results[component] = {
                'count': len(component_data),
                'correlation': correlation if not np.isnan(correlation) else 0,
                'avg_ratio': avg_ratio,
                'value_stats': value_stats,
                'current_rate': current_rate,
                'suggested_rate': suggested_rate,
                'rate_change': suggested_rate - current_rate
            }
        
        return analysis_results
    
    def generate_rate_suggestions(self, analysis_results: Dict) -> Dict:
        """生成rate.jsonc的调整建议
        
        Args:
            analysis_results: 组件分析结果
            
        Returns:
            Dict: 新的rate配置建议
        """
        print("生成rate.jsonc调整建议...")
        
        new_rates = self.rate_config.copy()
        
        # 根据分析结果调整rate
        for component, analysis in analysis_results.items():
            if analysis['count'] >= 10:  # 只调整有足够样本的组件
                new_rates[component] = round(analysis['suggested_rate'], 2)
        
        return new_rates
    
    def print_price_comparison(self, data: List[Dict]):
        """打印价格对比分析
        
        Args:
            data: 特征数据列表
        """
        print("\n" + "="*100)
        print("真实价格 vs 规则估价对比分析")
        print("="*100)
        
        # 计算统计信息
        prices = [d['price'] for d in data]
        rule_values = [d['rule_value'] for d in data]
        
        price_stats = {
            'min': min(prices),
            'max': max(prices),
            'mean': np.mean(prices),
            'median': np.median(prices)
        }
        
        rule_stats = {
            'min': min(rule_values),
            'max': max(rule_values),
            'mean': np.mean(rule_values),
            'median': np.median(rule_values)
        }
        
        print(f"\n整体统计:")
        print(f"{'指标':<12} {'真实价格':<12} {'规则估价':<12} {'差异':<12}")
        print("-"*50)
        print(f"{'最小值':<12} {price_stats['min']:<12.0f} {rule_stats['min']:<12.0f} {rule_stats['min']-price_stats['min']:<12.0f}")
        print(f"{'最大值':<12} {price_stats['max']:<12.0f} {rule_stats['max']:<12.0f} {rule_stats['max']-price_stats['max']:<12.0f}")
        print(f"{'平均值':<12} {price_stats['mean']:<12.0f} {rule_stats['mean']:<12.0f} {rule_stats['mean']-price_stats['mean']:<12.0f}")
        print(f"{'中位数':<12} {price_stats['median']:<12.0f} {rule_stats['median']:<12.0f} {rule_stats['median']-price_stats['median']:<12.0f}")
        
        # 计算估价准确性
        differences = [abs(d['rule_value'] - d['price']) for d in data]
        relative_errors = [abs(d['rule_value'] - d['price']) / d['price'] * 100 for d in data if d['price'] > 0]
        
        print(f"\n估价准确性:")
        print(f"平均绝对误差: {np.mean(differences):.0f} 元")
        print(f"平均相对误差: {np.mean(relative_errors):.1f}%")
        print(f"相关系数: {np.corrcoef(prices, rule_values)[0,1]:.3f}")
        
        # 显示价格区间分析
        print(f"\n价格区间分析:")
        price_ranges = [
            (0, 1000, "低价区"),
            (1000, 5000, "中价区"),
            (5000, 15000, "高价区"),
            (15000, float('inf'), "超高价区")
        ]
        
        print(f"{'价格区间':<12} {'数量':<8} {'平均真实价格':<12} {'平均规则估价':<12} {'平均误差%':<10}")
        print("-"*60)
        
        for min_price, max_price, name in price_ranges:
            range_data = [d for d in data if min_price <= d['price'] < max_price]
            if range_data:
                avg_price = np.mean([d['price'] for d in range_data])
                avg_rule = np.mean([d['rule_value'] for d in range_data])
                avg_error = np.mean([abs(d['rule_value'] - d['price']) / d['price'] * 100 for d in range_data])
                print(f"{name:<12} {len(range_data):<8} {avg_price:<12.0f} {avg_rule:<12.0f} {avg_error:<10.1f}")
        
        # 显示详细的个案对比（前20个和后20个）
        print(f"\n详细对比样例 (前20个角色):")
        print(f"{'序号':<4} {'角色ID':<20} {'等级':<4} {'真实价格':<8} {'规则估价':<8} {'误差':<8} {'误差%':<8}")
        print("-"*70)
        
        # 按价格排序显示
        sorted_data = sorted(data, key=lambda x: x['price'], reverse=True)
        
        for i, d in enumerate(sorted_data[:20]):
            error = d['rule_value'] - d['price']
            error_pct = abs(error) / d['price'] * 100 if d['price'] > 0 else 0
            print(f"{i+1:<4} {str(d['eid'])[:18]:<20} {d['level']:<4} {d['price']:<8.0f} {d['rule_value']:<8.0f} {error:<8.0f} {error_pct:<8.1f}")
        
        print(f"\n最低价格20个角色:")
        print(f"{'序号':<4} {'角色ID':<20} {'等级':<4} {'真实价格':<8} {'规则估价':<8} {'误差':<8} {'误差%':<8}")
        print("-"*70)
        
        lowest_data = sorted(data, key=lambda x: x['price'])
        for i, d in enumerate(lowest_data[:20]):
            error = d['rule_value'] - d['price']
            error_pct = abs(error) / d['price'] * 100 if d['price'] > 0 else 0
            print(f"{i+1:<4} {str(d['eid'])[:18]:<20} {d['level']:<4} {d['price']:<8.0f} {d['rule_value']:<8.0f} {error:<8.0f} {error_pct:<8.1f}")

    def print_analysis_report(self, analysis_results: Dict, new_rates: Dict):
        """打印分析报告
        
        Args:
            analysis_results: 组件分析结果
            new_rates: 新的rate配置
        """
        print("\n" + "="*80)
        print("CBG角色估价系统 - Rate参数调整分析报告")
        print("="*80)
        
        print(f"\n数据库路径: {self.db_path}")
        print(f"分析组件数量: {len(analysis_results)}")
        
        print("\n组件分析结果:")
        print("-"*80)
        print(f"{'组件名称':<20} {'样本数':<8} {'相关性':<8} {'当前系数':<10} {'建议系数':<10} {'变化':<8}")
        print("-"*80)
        
        for component, analysis in analysis_results.items():
            if analysis['count'] >= 10:
                print(f"{component:<20} {analysis['count']:<8} "
                      f"{analysis['correlation']:<8.3f} {analysis['current_rate']:<10.2f} "
                      f"{analysis['suggested_rate']:<10.2f} {analysis['rate_change']:<8.3f}")
        
        print("\n调整建议说明:")
        print("- 相关性 > 0.7: 高相关，建议增加系数")
        print("- 相关性 0.3-0.7: 中等相关，保持当前系数")
        print("- 相关性 0-0.3: 低相关，建议减少系数")
        print("- 相关性 < 0: 负相关，建议大幅减少系数")
        
        print("\n新的rate.jsonc配置:")
        print("-"*40)
        print(json.dumps(new_rates, indent=4, ensure_ascii=False))
    
    def save_results(self, data: List[Dict], analysis_results: Dict, new_rates: Dict):
        """保存分析结果
        
        Args:
            data: 特征数据列表
            analysis_results: 组件分析结果
            new_rates: 新的rate配置
        """
        # 创建输出目录
        output_dir = "tests/rate_analysis_output"
        os.makedirs(output_dir, exist_ok=True)
        
        # 保存价格对比数据
        import csv
        if data:
            # 创建简化的价格对比数据
            comparison_data = []
            for d in data:
                comparison_data.append({
                    'eid': d['eid'],
                    'level': d['level'],
                    'real_price': d['price'],
                    'rule_value': d['rule_value'],
                    'difference': d['rule_value'] - d['price'],
                    'error_percent': abs(d['rule_value'] - d['price']) / d['price'] * 100 if d['price'] > 0 else 0
                })
            
            # 按价格排序保存
            comparison_data.sort(key=lambda x: x['real_price'], reverse=True)
            
            with open(f"{output_dir}/price_comparison.csv", 'w', newline='', encoding='utf-8-sig') as f:
                writer = csv.DictWriter(f, fieldnames=['eid', 'level', 'real_price', 'rule_value', 'difference', 'error_percent'])
                writer.writeheader()
                writer.writerows(comparison_data)
            
            # 保存完整特征数据（选择关键字段）
            key_fields = ['eid', 'level', 'price', 'rule_value', 'school_history_count', 'all_new_point', 
                         'jiyuan_amount', 'sum_exp', 'packet_page', 'learn_cash', 
                         'hight_grow_rider_count', 'lingyou_count', 'limited_skin_value', 'limited_huge_horse_value']
            
            filtered_data = []
            for d in data:
                filtered_item = {}
                for field in key_fields:
                    if field == 'school_skills' and field in d:
                        # 师门技能取平均值
                        skills = d.get(field, [])
                        filtered_item[field] = np.mean(skills) if skills else 0
                    elif field == 'shenqi_score' and 'shenqi_score' in d:
                        filtered_item['shenqi_score'] = d.get('shenqi_score', 0)
                    else:
                        filtered_item[field] = d.get(field, 0)
                filtered_data.append(filtered_item)
            
            # 添加shenqi_score到字段列表中（如果数据中有的话）
            if filtered_data and 'shenqi_score' in filtered_data[0]:
                key_fields.append('shenqi_score')
            
            with open(f"{output_dir}/role_features_summary.csv", 'w', newline='', encoding='utf-8-sig') as f:
                writer = csv.DictWriter(f, fieldnames=key_fields)
                writer.writeheader()
                writer.writerows(filtered_data)
        
        # 保存分析结果
        with open(f"{output_dir}/analysis_results.json", 'w', encoding='utf-8') as f:
            json.dump(analysis_results, f, indent=4, ensure_ascii=False, default=str)
        
        # 保存新的rate配置
        with open(f"{output_dir}/new_rate_config.json", 'w', encoding='utf-8') as f:
            json.dump(new_rates, f, indent=4, ensure_ascii=False)
        
        print(f"\n结果已保存到: {output_dir}/")
        print(f"- price_comparison.csv: 价格对比详细数据")
        print(f"- role_features_summary.csv: 角色特征摘要数据")
        print(f"- analysis_results.json: 组件分析结果")
        print(f"- new_rate_config.json: 新的rate配置")
    
    def run_analysis(self, sample_size: int = 1000):
        """运行完整分析流程
        
        Args:
            sample_size: 样本数量
        """
        print("开始CBG角色估价系统Rate参数分析...")
        
        # 1. 获取角色样本
        roles = self.get_role_sample(sample_size)
        if not roles:
            print("未获取到角色数据，分析结束")
            return
        
        # 2. 提取特征并计算规则估价
        data = self.analyze_role_features(roles)
        if not data:
            print("特征提取失败，分析结束")
            return
        
        # 3. 打印价格对比分析
        self.print_price_comparison(data)
        
        # 4. 分析各组件表现
        analysis_results = self.analyze_component_performance(data)
        
        # 5. 生成rate调整建议
        new_rates = self.generate_rate_suggestions(analysis_results)
        
        # 6. 打印分析报告
        self.print_analysis_report(analysis_results, new_rates)
        
        # 7. 保存结果
        self.save_results(data, analysis_results, new_rates)
        
        print("\n分析完成！")

def main():
    """主函数"""
    db_path = r"C:\Users\Administrator\Desktop\mh\data\202509\cbg_empty_roles_202509.db"
    
    # 检查数据库文件是否存在
    if not os.path.exists(db_path):
        print(f"数据库文件不存在: {db_path}")
        return
    
    # 创建分析器并运行分析
    analyzer = RateAnalyzer(db_path)
    analyzer.run_analysis(sample_size=99999)  # 分析500个样本

if __name__ == "__main__":
    main() 