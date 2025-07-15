import sys
import os

# 添加项目根目录到Python路径，解决模块导入问题
current_dir = os.path.dirname(os.path.abspath(__file__))
project_root = os.path.dirname(os.path.dirname(current_dir))  # 向上两级到项目根目录
sys.path.insert(0, project_root)

import numpy as np
import pandas as pd
from typing import Dict, Any, List, Optional, Union, Tuple
import logging
import json
from datetime import datetime
import warnings
from dataclasses import dataclass

try:
    from .market_anchor_evaluator import MarketAnchorEvaluator
    from .rule_evaluator import RuleEvaluator
    from .feature_extractor.feature_extractor import FeatureExtractor
except ImportError:
    from market_anchor_evaluator import MarketAnchorEvaluator
    from rule_evaluator import RuleEvaluator
    from src.evaluator.feature_extractor.feature_extractor import FeatureExtractor

warnings.filterwarnings('ignore')


@dataclass
class ValuationResult:
    """估价结果数据类"""
    market_value: float          # 市场锚定价值
    rule_value: float           # 规则引擎价值
    final_value: float          # 最终估价
    confidence: float           # 整体置信度
    market_confidence: float    # 市场估价置信度
    rule_confidence: float      # 规则估价置信度
    integration_strategy: str   # 价值整合策略
    anomaly_score: float        # 异常分数
    calibration_applied: bool   # 是否应用了特征校准
    anchor_count: int           # 市场锚点数量
    value_breakdown: Dict[str, Any]  # 价值分解
    warnings: List[str]         # 警告信息


class HybridValuationEngine:
    """混合估价引擎 - 整合市场锚定和规则引擎"""
    
    def __init__(self, 
                 market_evaluator: Optional[MarketAnchorEvaluator] = None,
                 rule_evaluator: Optional[RuleEvaluator] = None):
        """
        初始化混合估价引擎
        
        Args:
            market_evaluator: 市场锚定估价器实例
            rule_evaluator: 规则估价器实例
        """
        self.logger = logging.getLogger(__name__)
        
        # 初始化子引擎
        self.market_evaluator = market_evaluator or MarketAnchorEvaluator()
        self.rule_evaluator = rule_evaluator or RuleEvaluator()
        self.feature_extractor = FeatureExtractor()
        
        # 整合策略配置
        self.integration_config = {
            # 基础权重配置
            'market_weight': 0.7,      # 市场锚定权重
            'rule_weight': 0.3,        # 规则引擎权重
            
            # 动态权重调整阈值
            'high_confidence_threshold': 0.8,  # 高置信度阈值
            'low_confidence_threshold': 0.3,   # 低置信度阈值
            'anchor_sufficient_count': 10,     # 充足锚点数量
            
            # 异常检测阈值
            'anomaly_threshold': 0.7,          # 异常检测阈值
            'extreme_ratio_threshold': 3.0,    # 极端比值阈值
            
            # 校准参数
            'calibration_enabled': True,       # 是否启用特征校准
            'calibration_threshold': 0.5,      # 校准应用阈值
        }
        
        print("混合估价引擎初始化完成")
    
    def evaluate(self, character_data: Dict[str, Any]) -> ValuationResult:
        """
        执行混合估价
        
        Args:
            character_data: 角色数据
            
        Returns:
            ValuationResult: 估价结果
        """
        try:
            print("\n=== 开始混合估价 ===")
            
            # 1. 特征提取和校准
            features = self._extract_and_calibrate_features(character_data)
            
            # 2. 执行双引擎估价
            market_result, rule_result = self._dual_engine_valuation(features)
            
            # 3. 异常检测
            anomaly_score = self._detect_anomalies(market_result, rule_result, features)
            
            # 4. 价值整合
            final_result = self._integrate_values(market_result, rule_result, anomaly_score)
            
            # 5. 生成置信度报告
            confidence_metrics = self._calculate_confidence_metrics(
                market_result, rule_result, final_result, anomaly_score
            )
            
            # 6. 构建最终结果
            result = ValuationResult(
                market_value=market_result.get('estimated_price', 0),
                rule_value=rule_result.get('final_value', 0),
                final_value=final_result['final_value'],
                confidence=confidence_metrics['overall_confidence'],
                market_confidence=market_result.get('confidence', 0),
                rule_confidence=confidence_metrics['rule_confidence'],
                integration_strategy=final_result['strategy'],
                anomaly_score=anomaly_score,
                calibration_applied=features.get('_calibration_applied', False),
                anchor_count=market_result.get('anchor_count', 0),
                value_breakdown=self._create_value_breakdown(market_result, rule_result),
                warnings=final_result.get('warnings', [])
            )
            
            print(f"混合估价完成: {result.final_value:.1f}")
            print(f"整体置信度: {result.confidence:.2f}")
            print(f"整合策略: {result.integration_strategy}")
            
            return result
            
        except Exception as e:
            self.logger.error(f"混合估价失败: {e}")
            return self._create_fallback_result()
    
    def _extract_and_calibrate_features(self, character_data: Dict[str, Any]) -> Dict[str, Any]:
        """提取并校准特征"""
        try:
            # 使用 FeatureExtractor 提取特征
            features = self.feature_extractor.extract_features(character_data)
            
            # 特征校准
            if self.integration_config['calibration_enabled']:
                features = self._apply_feature_calibration(features)
                features['_calibration_applied'] = True
            else:
                features['_calibration_applied'] = False
            
            return features
            
        except Exception as e:
            self.logger.error(f"特征提取和校准失败: {e}")
            return {}
    
    def _dual_engine_valuation(self, features: Dict[str, Any]) -> Tuple[Dict[str, Any], Dict[str, Any]]:
        """执行双引擎估价"""
        try:
            print("执行市场锚定估价...")
            # 市场锚定估价
            market_result = self.market_evaluator.calculate_value(features, 'fair_value')
            
            print("执行规则引擎估价...")
            # 规则引擎估价
            rule_result = self.rule_evaluator.calc_base_attributes_value_improved(features)
            
            return market_result, rule_result
            
        except Exception as e:
            self.logger.error(f"双引擎估价失败: {e}")
            return {}, {}
    
    def _detect_anomalies(self, 
                         market_result: Dict[str, Any], 
                         rule_result: Dict[str, Any],
                         features: Dict[str, Any]) -> float:
        """异常检测"""
        try:
            anomaly_indicators = []
            
            market_value = market_result.get('estimated_price', 0)
            rule_value = rule_result.get('final_value', 0)
            
            if market_value > 0 and rule_value > 0:
                # 1. 价值差异异常
                ratio = max(market_value, rule_value) / min(market_value, rule_value)
                if ratio > self.integration_config['extreme_ratio_threshold']:
                    anomaly_indicators.append(0.8)  # 高异常分数
                elif ratio > 2.0:
                    anomaly_indicators.append(0.4)  # 中等异常分数
                
                # 2. 市场置信度异常
                market_confidence = market_result.get('confidence', 0)
                if market_confidence < self.integration_config['low_confidence_threshold']:
                    anomaly_indicators.append(0.6)
                
                # 3. 锚点数量异常
                anchor_count = market_result.get('anchor_count', 0)
                if anchor_count < 3:
                    anomaly_indicators.append(0.7)
                
                # 4. 特征完整性检测
                key_features = ['level', 'total_cultivation', 'total_beast_cultivation']
                missing_features = sum(1 for f in key_features if features.get(f, 0) == 0)
                if missing_features > 1:
                    anomaly_indicators.append(0.5)
            
            # 计算综合异常分数
            if anomaly_indicators:
                anomaly_score = max(anomaly_indicators)  # 取最高异常分数
            else:
                anomaly_score = 0.0
            
            return anomaly_score
            
        except Exception as e:
            self.logger.error(f"异常检测失败: {e}")
            return 0.0
    
    def _integrate_values(self, 
                         market_result: Dict[str, Any], 
                         rule_result: Dict[str, Any],
                         anomaly_score: float) -> Dict[str, Any]:
        """价值整合"""
        try:
            market_value = market_result.get('estimated_price', 0)
            rule_value = rule_result.get('final_value', 0)
            market_confidence = market_result.get('confidence', 0)
            anchor_count = market_result.get('anchor_count', 0)
            
            warnings = []
            
            # 选择整合策略
            if anomaly_score > self.integration_config['anomaly_threshold']:
                # 高异常分数：保守策略
                if market_confidence > 0.5 and anchor_count >= 5:
                    strategy = "anomaly_market_priority"
                    final_value = market_value * 0.9  # 市场价值打折
                    warnings.append("检测到异常，使用保守市场估价")
                else:
                    strategy = "anomaly_rule_priority"  
                    final_value = rule_value * 0.8   # 规则价值打折
                    warnings.append("检测到异常，使用保守规则估价")
                    
            elif (market_confidence > self.integration_config['high_confidence_threshold'] and 
                  anchor_count >= self.integration_config['anchor_sufficient_count']):
                # 高置信度市场数据：市场主导
                strategy = "market_dominant"
                weight_market = 0.85
                weight_rule = 0.15
                final_value = market_value * weight_market + rule_value * weight_rule
                
            elif market_confidence < self.integration_config['low_confidence_threshold'] or anchor_count < 3:
                # 低置信度市场数据：规则主导
                strategy = "rule_dominant"
                weight_market = 0.2
                weight_rule = 0.8
                final_value = market_value * weight_market + rule_value * weight_rule
                warnings.append("市场数据不足，主要依据规则估价")
                
            else:
                # 标准平衡策略
                strategy = "balanced"
                weight_market = self.integration_config['market_weight']
                weight_rule = self.integration_config['rule_weight']
                final_value = market_value * weight_market + rule_value * weight_rule
            
            return {
                'final_value': final_value,
                'strategy': strategy,
                'market_weight': weight_market if 'weight_market' in locals() else None,
                'rule_weight': weight_rule if 'weight_rule' in locals() else None,
                'warnings': warnings
            }
            
        except Exception as e:
            self.logger.error(f"价值整合失败: {e}")
            return {'final_value': 0, 'strategy': 'error', 'warnings': ['价值整合失败']}
    
    def _apply_feature_calibration(self, features: Dict[str, Any]) -> Dict[str, Any]:
        """应用特征校准"""
        try:
            calibrated_features = features.copy()
            
            # 1. 修炼值校准 - 确保合理性
            cultivation_fields = ['expt_ski1', 'expt_ski2', 'expt_ski3', 'expt_ski4', 'expt_ski5']
            for field in cultivation_fields:
                value = calibrated_features.get(field, 0)
                if value > 100:  # 修炼等级不应超过100
                    calibrated_features[field] = min(value, 100)
            
            # 2. 等级与修炼一致性校准
            level = calibrated_features.get('level', 0)
            if level > 0:
                max_possible_cultivation = min(level, 100)
                for field in cultivation_fields:
                    value = calibrated_features.get(field, 0)
                    if value > max_possible_cultivation:
                        calibrated_features[field] = max_possible_cultivation
            
            # 3. 总修炼重新计算（确保一致性）
            total_cultivation = sum(calibrated_features.get(f'expt_ski{i}', 0) for i in range(1, 5))
            calibrated_features['total_cultivation'] = total_cultivation
            
            total_beast_cultivation = sum(calibrated_features.get(f'beast_ski{i}', 0) for i in range(1, 5))
            calibrated_features['total_beast_cultivation'] = total_beast_cultivation
            
            return calibrated_features
            
        except Exception as e:
            self.logger.error(f"特征校准失败: {e}")
            return features
    
    def _calculate_confidence_metrics(self, 
                                    market_result: Dict[str, Any],
                                    rule_result: Dict[str, Any],
                                    final_result: Dict[str, Any],
                                    anomaly_score: float) -> Dict[str, float]:
        """计算置信度指标"""
        try:
            market_confidence = market_result.get('confidence', 0)
            anchor_count = market_result.get('anchor_count', 0)
            
            # 规则引擎置信度（基于价值分解完整性）
            value_breakdown = rule_result.get('value_breakdown', {})
            rule_confidence = min(len(value_breakdown) / 10.0, 1.0)  # 基于价值分解项数
            
            # 整体置信度
            base_confidence = (market_confidence + rule_confidence) / 2
            
            # 异常分数惩罚
            anomaly_penalty = anomaly_score * 0.3
            overall_confidence = max(0, base_confidence - anomaly_penalty)
            
            # 锚点数量加成
            if anchor_count >= 10:
                overall_confidence = min(1.0, overall_confidence + 0.1)
            
            return {
                'overall_confidence': overall_confidence,
                'market_confidence': market_confidence,
                'rule_confidence': rule_confidence,
                'anomaly_penalty': anomaly_penalty
            }
            
        except Exception as e:
            self.logger.error(f"置信度计算失败: {e}")
            return {
                'overall_confidence': 0.0,
                'market_confidence': 0.0,
                'rule_confidence': 0.0,
                'anomaly_penalty': 1.0
            }
    
    def _create_value_breakdown(self, 
                              market_result: Dict[str, Any],
                              rule_result: Dict[str, Any]) -> Dict[str, Any]:
        """创建价值分解"""
        try:
            breakdown = {
                'market_analysis': {
                    'estimated_price': market_result.get('estimated_price', 0),
                    'anchor_count': market_result.get('anchor_count', 0),
                    'price_range': market_result.get('price_range', {}),
                    'confidence': market_result.get('confidence', 0)
                },
                'rule_analysis': {
                    'total_value': rule_result.get('total_raw_value', 0),
                    'final_value': rule_result.get('final_value', 0),
                    'value_breakdown': rule_result.get('value_breakdown', {})
                }
            }
            
            return breakdown
            
        except Exception as e:
            self.logger.error(f"创建价值分解失败: {e}")
            return {}
    
    def _create_fallback_result(self) -> ValuationResult:
        """创建备用结果"""
        return ValuationResult(
            market_value=0,
            rule_value=0,
            final_value=0,
            confidence=0,
            market_confidence=0,
            rule_confidence=0,
            integration_strategy='error',
            anomaly_score=1.0,
            calibration_applied=False,
            anchor_count=0,
            value_breakdown={},
            warnings=['估价引擎执行失败']
        )
    
    def batch_evaluate(self, character_list: List[Dict[str, Any]]) -> List[ValuationResult]:
        """批量混合估价"""
        results = []
        print(f"开始批量混合估价，共 {len(character_list)} 个角色")
        
        for i, character_data in enumerate(character_list):
            try:
                result = self.evaluate(character_data)
                results.append(result)
                
                if (i + 1) % 5 == 0:
                    print(f"已完成 {i + 1}/{len(character_list)} 个角色的混合估价")
                    
            except Exception as e:
                self.logger.error(f"批量估价第 {i+1} 个角色失败: {e}")
                results.append(self._create_fallback_result())
        
        print(f"批量混合估价完成")
        return results
    
    def generate_comprehensive_report(self, character_data: Dict[str, Any]) -> Dict[str, Any]:
        """生成综合估价报告"""
        try:
            # 执行混合估价
            result = self.evaluate(character_data)
            
            # 获取详细的市场分析
            features = self._extract_and_calibrate_features(character_data)
            market_distribution = self.market_evaluator.value_distribution_report(features)
            
            # 构建综合报告
            report = {
                'evaluation_summary': {
                    'final_valuation': result.final_value,
                    'confidence_score': result.confidence,
                    'integration_strategy': result.integration_strategy,
                    'anomaly_score': result.anomaly_score
                },
                'dual_engine_analysis': {
                    'market_valuation': result.market_value,
                    'rule_valuation': result.rule_value,
                    'market_confidence': result.market_confidence,
                    'rule_confidence': result.rule_confidence,
                    'anchor_count': result.anchor_count
                },
                'market_distribution': market_distribution,
                'value_breakdown': result.value_breakdown,
                'risk_assessment': {
                    'anomaly_detected': result.anomaly_score > 0.5,
                    'data_sufficiency': result.anchor_count >= 10,
                    'feature_calibration': result.calibration_applied,
                    'warnings': result.warnings
                },
                'recommendations': self._generate_recommendations(result)
            }
            
            return report
            
        except Exception as e:
            self.logger.error(f"生成综合报告失败: {e}")
            return {'error': str(e)}
    
    def _generate_recommendations(self, result: ValuationResult) -> List[str]:
        """生成估价建议"""
        recommendations = []
        
        if result.confidence < 0.5:
            recommendations.append("置信度较低，建议谨慎参考估价结果")
        
        if result.anomaly_score > 0.7:
            recommendations.append("检测到异常，建议进一步核实角色特征")
        
        if result.anchor_count < 5:
            recommendations.append("市场参考数据不足，建议结合其他信息源")
        
        if result.integration_strategy == "rule_dominant":
            recommendations.append("主要基于规则估价，可能存在市场差异")
        
        if not result.calibration_applied:
            recommendations.append("特征校准未启用，估价可能存在偏差")
        
        return recommendations


if __name__ == "__main__":
    # 测试混合估价引擎
    try:
        # 初始化引擎
        engine = HybridValuationEngine()
        
        # 构造测试角色数据
        test_character = {
            'level': 129,
            'expt_ski1': 0,        # 攻击修炼
            'expt_ski2': 21,       # 防御修炼
            'expt_ski3': 21,       # 法术修炼
            'expt_ski4': 21,       # 抗法修炼
            'expt_ski5': 0,        # 猎术修炼
            'beast_ski1': 20,      # 召唤兽攻击修炼
            'beast_ski2': 20,      # 召唤兽防御修炼
            'beast_ski3': 20,      # 召唤兽法术修炼
            'beast_ski4': 20,      # 召唤兽抗法修炼
            'all_new_point': 5,    # 乾元丹
            'school_history_count': 3,  # 历史门派数
            'life_skills': [120, 110, 100, 90],  # 生活技能
            'school_skills': [160, 150, 140],     # 师门技能
        }
        
        print("=== 混合估价引擎测试 ===")
        
        # 执行混合估价
        result = engine.evaluate(test_character)
        
        print(f"\n=== 估价结果 ===")
        print(f"最终估价: {result.final_value:.1f}")
        print(f"市场估价: {result.market_value:.1f}")
        print(f"规则估价: {result.rule_value:.1f}")
        print(f"整体置信度: {result.confidence:.2f}")
        print(f"整合策略: {result.integration_strategy}")
        print(f"异常分数: {result.anomaly_score:.2f}")
        print(f"锚点数量: {result.anchor_count}")
        
        if result.warnings:
            print(f"警告信息: {', '.join(result.warnings)}")
        
        # 生成综合报告
        print(f"\n=== 生成综合报告 ===")
        report = engine.generate_comprehensive_report(test_character)
        
        if 'error' not in report:
            print(f"报告生成成功")
            print(f"建议: {', '.join(report['recommendations'])}")
        else:
            print(f"报告生成失败: {report['error']}")
            
    except Exception as e:
        print(f"测试失败: {e}")
        import traceback
        traceback.print_exc() 