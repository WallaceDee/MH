import os
import sys
import json
import logging
from typing import Dict, List, Any

# 添加项目根目录到Python路径，解决模块导入问题
current_dir = os.path.dirname(os.path.abspath(__file__))
project_root = os.path.dirname(os.path.dirname(current_dir))  # 向上两级到项目根目录
sys.path.insert(0, project_root)

try:
    from src.evaluator.hybrid_valuation_engine import HybridValuationEngine, ValuationResult
    from src.evaluator.market_anchor_evaluator import MarketAnchorEvaluator
    from src.evaluator.rule_evaluator import RuleEvaluator
except ImportError as e:
    print(f"导入错误: {e}")
    print("请确保所有必需的模块都存在")
    sys.exit(1)


def create_sample_roles() -> List[Dict[str, Any]]:
    """创建示例角色数据"""
    roles = [
        {
            'name': '高修炼普陀山',
            'description': '高修炼、高乾元丹的普陀山角色',
            'data': {
                'level': 129,
                'expt_ski1': 0,        # 攻击修炼（物理门派不主修）
                'expt_ski2': 21,       # 防御修炼
                'expt_ski3': 21,       # 法术修炼（法系门派主修）
                'expt_ski4': 21,       # 抗法修炼
                'expt_ski5': 0,        # 猎术修炼
                'beast_ski1': 20,      # 召唤兽攻击修炼
                'beast_ski2': 20,      # 召唤兽防御修炼
                'beast_ski3': 20,      # 召唤兽法术修炼
                'beast_ski4': 20,      # 召唤兽抗法修炼
                'all_new_point': 4,    # 乾元丹
                'school_history_count': 3,  # 历史门派数
                'life_skills': {
                    '烹饪': 140,
                    '练金': 130, 
                    '打造': 120,
                    '裁缝': 110,
                    '巧匠': 100,
                    '强壮': 10,    # 强壮技能
                    '神速': 20     # 神速技能
                },
                'school_skills': {
                    '普陀山技能1': 150,
                    '普陀山技能2': 150,
                    '普陀山技能3': 150,
                    '普陀山技能4': 150,
                    '普陀山技能5': 150,
                    '普陀山技能6': 150,
                    '普陀山技能7': 150
                },
                'learn_cash': 500000,  # 储备金（50万）
                'packet_page': 8,      # 行囊页数
                'premium_fabao_count': 0,    # 有价值法宝数量
                'hight_grow_rider_count': 2, # 高成长坐骑数量
                'lingyou_count': 0,         # 灵佑次数
                'jiyuan_amount': 20,        # 机缘值
            }
        }
    ]
    
    return roles


def demonstrate_single_valuation(engine: HybridValuationEngine, role: Dict[str, Any]):
    """演示单个角色估价"""
    print(f"\n{'='*60}")
    print(f"角色: {role['name']}")
    print(f"描述: {role['description']}")
    print(f"{'='*60}")
    
    # 执行估价
    result = engine.evaluate(role['data'])
    
    # 显示基本结果
    print(f"\n📊 基本估价结果:")
    print(f"   最终估价: {result.final_value:.1f}")
    print(f"   市场估价: {result.market_value:.1f}")
    print(f"   规则估价: {result.rule_value:.1f}")
    print(f"   整体置信度: {result.confidence:.2%}")
    print(f"   整合策略: {result.integration_strategy}")
    
    # 显示详细信息
    print(f"\n🔍 详细分析:")
    print(f"   市场置信度: {result.market_confidence:.2%}")
    print(f"   规则置信度: {result.rule_confidence:.2%}")
    print(f"   异常分数: {result.anomaly_score:.2f}")
    print(f"   市场锚点数: {result.anchor_count}")
    print(f"   特征校准: {'已应用' if result.calibration_applied else '未应用'}")
    
    # 显示警告信息
    if result.warnings:
        print(f"\n⚠️  警告信息:")
        for warning in result.warnings:
            print(f"   - {warning}")
    
    # 显示价值分解
    if result.value_breakdown:
        print(f"\n💰 价值分解:")
        market_info = result.value_breakdown.get('market_analysis', {})
        rule_info = result.value_breakdown.get('rule_analysis', {})
        
        if market_info:
            print(f"   市场分析:")
            print(f"     估价: {market_info.get('estimated_price', 0):.1f}")
            print(f"     锚点数: {market_info.get('anchor_count', 0)}")
            print(f"     置信度: {market_info.get('confidence', 0):.2%}")
            
            price_range = market_info.get('price_range', {})
            if price_range:
                print(f"     价格范围: {price_range.get('min', 0):.1f} - {price_range.get('max', 0):.1f}")
        
        if rule_info:
            print(f"   规则分析:")
            print(f"     原始价值: {rule_info.get('total_value', 0):.1f}")
            print(f"     最终价值: {rule_info.get('final_value', 0):.1f}")
            
            breakdown = rule_info.get('value_breakdown', {})
            if breakdown:
                print(f"     主要价值项:")
                sorted_items = sorted(breakdown.items(), key=lambda x: x[1], reverse=True)
                for item, value in sorted_items[:5]:  # 显示前5项
                    if value > 0:
                        print(f"       {item}: {value:.1f}")
    
    return result


def demonstrate_comprehensive_report(engine: HybridValuationEngine, role: Dict[str, Any]):
    """演示综合报告生成"""
    print(f"\n📋 生成综合报告...")
    
    report = engine.generate_comprehensive_report(role['data'])
    
    if 'error' in report:
        print(f"❌ 报告生成失败: {report['error']}")
        return None
    
    print(f"\n📈 综合评估报告:")
    
    # 估价摘要
    summary = report.get('evaluation_summary', {})
    print(f"   最终估价: {summary.get('final_valuation', 0):.1f}")
    print(f"   置信分数: {summary.get('confidence_score', 0):.2%}")
    print(f"   整合策略: {summary.get('integration_strategy', 'N/A')}")
    print(f"   异常分数: {summary.get('anomaly_score', 0):.2f}")
    
    # 风险评估
    risk = report.get('risk_assessment', {})
    if risk:
        print(f"\n🔍 风险评估:")
        print(f"   异常检测: {'是' if risk.get('anomaly_detected', False) else '否'}")
        print(f"   数据充足性: {'是' if risk.get('data_sufficiency', False) else '否'}")
        print(f"   特征校准: {'是' if risk.get('feature_calibration', False) else '否'}")
    
    # 建议
    recommendations = report.get('recommendations', [])
    if recommendations:
        print(f"\n💡 建议:")
        for i, rec in enumerate(recommendations, 1):
            print(f"   {i}. {rec}")
    
    return report


def demonstrate_batch_valuation(engine: HybridValuationEngine, roles: List[Dict[str, Any]]):
    """演示批量估价"""
    print(f"\n🔄 批量估价演示:")
    print(f"   准备估价 {len(roles)} 个角色...")
    
    # 提取角色数据
    role_data_list = [char['data'] for char in roles]
    
    # 执行批量估价
    results = engine.batch_evaluate(role_data_list)
    
    # 汇总结果
    print(f"\n📊 批量估价结果汇总:")
    print(f"{'角色名称':<15} {'最终估价':<10} {'置信度':<8} {'策略':<15} {'异常':<6}")
    print(f"{'-'*60}")
    
    for i, result in enumerate(results):
        char_name = roles[i]['name'][:14]
        final_value = result.final_value
        confidence = result.confidence
        strategy = result.integration_strategy[:14]
        anomaly = "是" if result.anomaly_score > 0.5 else "否"
        
        print(f"{char_name:<15} {final_value:<10.1f} {confidence:<8.2%} {strategy:<15} {anomaly:<6}")
    
    # 统计分析
    total_value = sum(r.final_value for r in results)
    avg_confidence = sum(r.confidence for r in results) / len(results)
    strategies = [r.integration_strategy for r in results]
    strategy_counts = {s: strategies.count(s) for s in set(strategies)}
    
    print(f"\n📈 统计分析:")
    print(f"   总估价: {total_value:.1f}")
    print(f"   平均置信度: {avg_confidence:.2%}")
    print(f"   策略分布: {strategy_counts}")
    
    return results


def main():
    """主演示函数"""
    print("🎮 混合估价引擎演示程序")
    print("=" * 50)
    
    
    try:
        # 初始化引擎
        print("🔧 初始化混合估价引擎...")
        engine = HybridValuationEngine()
        print("✅ 引擎初始化成功")
        
        # 准备示例数据
        roles = create_sample_roles()
        print(f"📝 已准备 {len(roles)} 个示例角色")
        
        # 演示1：单个角色详细估价
        print(f"\n{'🔍 单个角色详细估价演示'}")
        for role in roles[:2]:  # 演示前两个角色
            result = demonstrate_single_valuation(engine, role)
        
        # 演示2：综合报告生成
        print(f"\n{'📋 综合报告生成演示'}")
        demonstrate_comprehensive_report(engine, roles[0])
        
        # 演示3：批量估价
        print(f"\n{'🔄 批量估价演示'}")
        batch_results = demonstrate_batch_valuation(engine, roles)
        
        # 演示4：策略对比
        print(f"\n{'⚖️  不同策略对比演示'}")
        test_role = roles[0]['data']
        
        # 使用不同的市场策略
        print("不同定价策略对比:")
        
        # 模拟不同的市场条件
        original_config = engine.integration_config.copy()
        
        # 高置信度市场主导
        engine.integration_config['market_weight'] = 0.9
        engine.integration_config['rule_weight'] = 0.1
        result1 = engine.evaluate(test_role)
        print(f"  市场主导策略: {result1.final_value:.1f} (策略: {result1.integration_strategy})")
        
        # 规则主导
        engine.integration_config['market_weight'] = 0.2
        engine.integration_config['rule_weight'] = 0.8
        result2 = engine.evaluate(test_role)
        print(f"  规则主导策略: {result2.final_value:.1f} (策略: {result2.integration_strategy})")
        
        # 恢复原始配置
        engine.integration_config = original_config
        result3 = engine.evaluate(test_role)
        print(f"  平衡策略: {result3.final_value:.1f} (策略: {result3.integration_strategy})")
        
        print(f"\n✅ 演示完成！")
        print(f"📝 详细日志已保存到 hybrid_valuation.log")
        
    except Exception as e:
        print(f"❌ 演示过程中出现错误: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    main() 